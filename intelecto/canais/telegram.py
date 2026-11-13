"""Canal Telegram pela Bot API (long polling), só com a biblioteca padrão.

Segurança: só responde aos ids em config.telegram_donos. Mensagem de qualquer outro
id é ignorada (e anotada na auditoria). Sem dono configurado, o bot responde só
"/id" (para você descobrir o seu id) e nada mais.

Aprovação de comando pelo celular: o bot manda "Posso rodar …? responda /sim ou /nao"
e espera até 120 s.
"""
import asyncio
import json
import urllib.error
import urllib.request

LIMITE = 4096


def dividir(texto: str, limite: int = LIMITE) -> list:
    if len(texto) <= limite:
        return [texto]
    partes, buf = [], ""
    for par in texto.split("\n\n"):
        cand = f"{buf}\n\n{par}" if buf else par
        if len(cand) <= limite:
            buf = cand
            continue
        if buf:
            partes.append(buf)
        while len(par) > limite:
            partes.append(par[:limite])
            par = par[limite:]
        buf = par
    if buf:
        partes.append(buf)
    return partes


class Telegram:
    def __init__(self, token: str, donos=(), url: str = "https://api.telegram.org", auditoria=None, espera: int = 30):
        if not token:
            raise ValueError("sem token do Telegram: rode `python3 -m intelecto cofre guardar telegram`")
        self.base = f"{url.rstrip('/')}/bot{token}"
        self.donos = {str(d) for d in donos}
        self.auditoria = auditoria
        self.espera = espera
        self.offset = 0
        self._pendente = {}   # chat -> Future da aprovação

    def _api(self, metodo: str, **params) -> dict:
        req = urllib.request.Request(f"{self.base}/{metodo}", data=json.dumps(params).encode(),
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.espera + 15) as r:
                d = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Telegram {metodo}: HTTP {e.code}") from None   # sem o token na mensagem
        if not d.get("ok"):
            raise RuntimeError(f"Telegram {metodo}: {d.get('description', 'erro')}")
        return d

    async def api(self, metodo: str, **params) -> dict:
        return await asyncio.to_thread(self._api, metodo, **params)

    async def enviar(self, chat, texto: str) -> None:
        for parte in dividir(texto or "(vazio)"):
            await self.api("sendMessage", chat_id=chat, text=parte)

    def autorizado(self, remetente) -> bool:
        return str(remetente) in self.donos

    def perguntador(self, chat):
        async def perguntar(comando: str, motivo: str) -> bool:
            fut = asyncio.get_running_loop().create_future()
            self._pendente[str(chat)] = fut
            await self.enviar(chat, f"Posso rodar este comando?\n\n{comando}\n\nMotivo da pergunta: {motivo}\nResponda /sim ou /nao (120 s).")
            try:
                return await asyncio.wait_for(fut, timeout=120)
            except asyncio.TimeoutError:
                await self.enviar(chat, "Sem resposta em 120 s: não rodei.")
                return False
            finally:
                self._pendente.pop(str(chat), None)
        return perguntar

    async def uma_rodada(self, ao_receber) -> int:
        """Busca as mensagens novas uma vez e trata cada uma. Devolve quantas chegaram."""
        d = await self.api("getUpdates", offset=self.offset, timeout=self.espera, allowed_updates=["message"])
        n = 0
        for u in d.get("result", []):
            self.offset = max(self.offset, int(u["update_id"]) + 1)
            msg = u.get("message") or {}
            texto = (msg.get("text") or "").strip()
            chat = (msg.get("chat") or {}).get("id")
            rem = (msg.get("from") or {}).get("id")
            if not texto or chat is None:
                continue
            n += 1
            if texto == "/id":
                await self.enviar(chat, f"Seu id é {rem}. Coloque em telegram_donos no config.json.")
                continue
            if not self.autorizado(rem):
                if self.auditoria:
                    self.auditoria.registrar("telegram_ignorado", remetente=rem)
                continue
            fut = self._pendente.get(str(chat))
            if fut and not fut.done() and texto.lower() in ("/sim", "/nao", "/não", "sim", "nao", "não"):
                fut.set_result(texto.lower().lstrip("/") == "sim")
                continue
            asyncio.ensure_future(self._tratar(chat, texto, ao_receber))
        return n

    async def _tratar(self, chat, texto, ao_receber):
        try:
            await self.api("sendChatAction", chat_id=chat, action="typing")
            resposta = await ao_receber(str(chat), texto, self.perguntador(chat))
        except Exception as e:  # nunca derruba o bot por uma mensagem
            resposta = f"Erro: {e}"
        await self.enviar(chat, resposta)

    async def rodar(self, ao_receber) -> None:
        while True:
            try:
                await self.uma_rodada(ao_receber)
            except (RuntimeError, OSError) as e:
                if self.auditoria:
                    self.auditoria.registrar("telegram_erro", erro=str(e)[:200])
                await asyncio.sleep(5)
