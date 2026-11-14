"""Tarefa longa em segundo plano: "pesquisa isso por 10 minutos" e a conversa continua.

Cada tarefa é um arquivo JSON em <pasta>/<id>.json, gravado depois de CADA passo (gravação atômica).
  - Caiu, reiniciou, desligou: reabre e continua do último passo salvo, nunca do zero.
  - Orçamento de minutos e de rodadas. Acabou o orçamento (ou você disse "chega, escreve"):
    o último passo é escrever o relatório com o que já tem. Parar nunca é perder o trabalho.
  - Sem cota no cérebro: a tarefa pausa 5 minutos e continua de onde parou.
  - Interrompida 3 vezes no meio de um passo: falhou (não tenta para sempre).
  - Você manda recado no meio ("olha os preços em euro também"): o próximo passo recebe.

Quem faz o trabalho de verdade são duas funções que você entrega (podem ser async):
  passo(tarefa)    -> {"nota": "..."} | {"fim": True, "nota": ...} | {"sem_cota": True}
  escrever(tarefa) -> texto do relatório (Markdown)
"""
import inspect
import json
import os
import secrets
import threading
import time

MAX_ABERTURAS = 3
PAUSA_SEM_COTA = 300
FINAIS = ("concluida", "cancelada", "falhou")


async def _chamar(f, *a):
    r = f(*a)
    return await r if inspect.isawaitable(r) else r


class Tarefas:
    def __init__(self, pasta: str, relogio=time.time):
        self.pasta = pasta
        self.relogio = relogio
        self._trava = threading.Lock()
        os.makedirs(pasta, exist_ok=True)

    # ---------- armazenamento ----------
    def _caminho(self, tid: str) -> str:
        if not tid.replace("-", "").isalnum():
            raise ValueError("id de tarefa inválido")
        return os.path.join(self.pasta, f"{tid}.json")

    def pegar(self, tid: str) -> dict | None:
        try:
            with open(self._caminho(tid), encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def _gravar(self, t: dict) -> None:
        caminho = self._caminho(t["id"])
        tmp = caminho + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(t, f, ensure_ascii=False, indent=1)
        os.replace(tmp, caminho)

    def _mudar(self, tid: str, **campos) -> dict:
        with self._trava:
            t = self.pegar(tid)
            if t is None:
                raise KeyError(tid)
            t.update(campos)
            self._gravar(t)
            return t

    # ---------- o que a conversa usa ----------
    def criar(self, pedido: str, perfil: str = "geral", minutos: int = 10, rodadas: int = 50,
              comecar_em: float | None = None) -> str:
        tid = f"{int(self.relogio())}-{secrets.token_hex(3)}"
        t = {"id": tid, "pedido": pedido, "perfil": perfil, "minutos": int(minutos), "rodadas": int(rodadas),
             "comecar_em": comecar_em, "status": "nova", "aberturas": 0, "gasto_s": 0.0, "rodadas_feitas": 0,
             "passos": [], "recados": [], "recados_lidos": [], "encerrar": False, "cancelar": False,
             "retoma_em": None, "relatorio": None, "motivo": ""}
        with self._trava:
            self._gravar(t)
        return tid

    def listar(self) -> list:
        ids = sorted(n[:-5] for n in os.listdir(self.pasta) if n.endswith(".json"))
        return [t for t in (self.pegar(i) for i in ids) if t]

    def recado(self, tid: str, texto: str) -> None:
        with self._trava:
            t = self.pegar(tid)
            t["recados"].append(texto)
            self._gravar(t)

    def encerrar(self, tid: str) -> None:
        """'Chega, escreve o que tem.'"""
        self._mudar(tid, encerrar=True)

    def cancelar(self, tid: str) -> None:
        self._mudar(tid, cancelar=True)

    def prontas(self) -> list:
        """Ids que podem rodar agora (inclui as que caíram no meio e as pausadas cuja pausa acabou)."""
        agora = self.relogio()
        saida = []
        for t in self.listar():
            if t["status"] in FINAIS:
                continue
            if t["comecar_em"] and agora < t["comecar_em"]:
                continue
            if t["status"] == "pausada" and t["retoma_em"] and agora < t["retoma_em"]:
                continue
            saida.append(t["id"])
        return saida

    # ---------- o motor ----------
    async def rodar(self, tid: str, passo, escrever) -> dict:
        t = self.pegar(tid)
        if t is None:
            raise KeyError(tid)
        if t["status"] in FINAIS or tid not in self.prontas():
            return t
        if t["status"] == "rodando":           # a última execução morreu no meio de um passo
            t["aberturas"] += 1
            if t["aberturas"] >= MAX_ABERTURAS:
                return self._mudar(tid, status="falhou", aberturas=t["aberturas"],
                                   motivo=f"interrompida {t['aberturas']} vezes")
        t = self._mudar(tid, status="rodando", aberturas=t["aberturas"], retoma_em=None)
        while True:
            t = self.pegar(tid)
            if t["cancelar"]:
                return self._mudar(tid, status="cancelada", motivo="cancelada pelo dono")
            acabou = (t["encerrar"] or t["rodadas_feitas"] >= t["rodadas"]
                      or t["gasto_s"] >= t["minutos"] * 60)
            if acabou:
                texto = await _chamar(escrever, t)
                with open(os.path.join(self.pasta, f"{tid}.md"), "w", encoding="utf-8") as f:
                    f.write(texto)
                return self._mudar(tid, status="concluida", relatorio=texto, aberturas=0,
                                   motivo="orçamento acabou" if not t["encerrar"] else "pronta")
            if t["recados"]:
                t = self._mudar(tid, recados_lidos=t["recados_lidos"] + t["recados"], recados=[])
            inicio = self.relogio()
            r = await _chamar(passo, t) or {}
            dur = max(0.0, self.relogio() - inicio)
            if r.get("sem_cota"):
                return self._mudar(tid, status="pausada", retoma_em=self.relogio() + PAUSA_SEM_COTA,
                                   gasto_s=t["gasto_s"] + dur, motivo="sem cota no cérebro: pausa de 5 min")
            with self._trava:
                atual = self.pegar(tid)                 # pega recado/cancelar que chegou durante o passo
                atual["passos"].append(str(r.get("nota", "")))
                atual["rodadas_feitas"] += 1
                atual["gasto_s"] += dur
                if r.get("fim"):
                    atual["encerrar"] = True
                self._gravar(atual)
