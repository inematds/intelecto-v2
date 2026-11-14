"""Rotinas: lembretes e tarefas com hora, num motor só.

Quando:
  {"tipo": "uma_vez",   "em": "2026-11-14T09:00"}
  {"tipo": "semanal",   "dias": [0, 4], "hora": "17:00"}          (0 = segunda … 6 = domingo)
  {"tipo": "intervalo", "minutos": 30, "entre": "08:00-18:00"}    ("entre" é opcional)

O quê (tipo da rotina): "lembrete" (diz um texto), "instrucao" (o assistente faz algo), "tarefa" (abre
uma tarefa de fundo).

ATRASO TRATADO DE PROPÓSITO. Se a rotina venceu com o assistente desligado ou ocupado, ela ainda roda
enquanto fizer sentido: lembrete até 2 h de atraso, instrução até 45 min, tarefa até 6 h. Passou disso,
é pulada e o histórico diz por quê (nada de um "bom dia" às 15 h).

HORÁRIO DE SILÊNCIO ("23:00-07:00") segura só o que ninguém pediu para aquela hora (rotina marcada
silenciavel=True). Um lembrete que você marcou para 06:30 toca mesmo dentro do silêncio.
"""
import json
import os
import secrets
from datetime import datetime, timedelta

ATRASO = {"lembrete": 2 * 3600, "instrucao": 45 * 60, "tarefa": 6 * 3600}
TIPOS = tuple(ATRASO)


def _hm(texto: str) -> tuple:
    h, m = texto.strip().split(":")
    h, m = int(h), int(m)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError(f"hora inválida: {texto}")
    return h, m


def _janela(entre: str) -> tuple:
    a, b = entre.split("-")
    return _hm(a), _hm(b)


def dentro(entre: str, dt: datetime) -> bool:
    """dt está dentro da faixa 'HH:MM-HH:MM'? Faixa que vira a noite (23:00-07:00) funciona."""
    (h1, m1), (h2, m2) = _janela(entre)
    a, b, x = h1 * 60 + m1, h2 * 60 + m2, dt.hour * 60 + dt.minute
    return a <= x < b if a <= b else (x >= a or x < b)


def proxima(quando: dict, depois: datetime):
    """A próxima vez estritamente depois de `depois` (ou None se não há mais)."""
    tipo = quando.get("tipo")
    if tipo == "uma_vez":
        em = datetime.fromisoformat(quando["em"])
        return em if em > depois else None
    if tipo == "semanal":
        h, m = _hm(quando["hora"])
        dias = set(quando.get("dias") or range(7))
        for d in range(8):
            c = (depois + timedelta(days=d)).replace(hour=h, minute=m, second=0, microsecond=0)
            if c > depois and c.weekday() in dias:
                return c
        return None
    if tipo == "intervalo":
        passo = timedelta(minutes=max(1, int(quando["minutos"])))
        c = depois.replace(second=0, microsecond=0) + passo
        entre = quando.get("entre")
        if not entre or dentro(entre, c):
            return c
        (h1, m1), _ = _janela(entre)
        inicio = c.replace(hour=h1, minute=m1)
        return inicio if inicio > depois else inicio + timedelta(days=1)
    raise ValueError(f"quando desconhecido: {quando}")


class Rotinas:
    def __init__(self, arquivo: str):
        self.arquivo = arquivo
        self._doc = {"rotinas": [], "silencio": "", "historico": []}
        if os.path.exists(arquivo):
            with open(arquivo, encoding="utf-8") as f:
                self._doc.update(json.load(f))

    def _gravar(self) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.arquivo)), exist_ok=True)
        tmp = self.arquivo + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._doc, f, ensure_ascii=False, indent=1)
        os.replace(tmp, self.arquivo)

    def listar(self) -> list:
        return list(self._doc["rotinas"])

    def historico(self, n: int = 20) -> list:
        return self._doc["historico"][-n:]

    def adicionar(self, nome: str, tipo: str, quando: dict, texto: str, agora: datetime,
                  silenciavel: bool = False) -> str:
        if tipo not in TIPOS:
            raise ValueError(f"tipo deve ser um de {TIPOS}")
        nxt = proxima(quando, agora)
        if nxt is None:
            raise ValueError("essa rotina não tem nenhuma próxima vez (data no passado?)")
        rid = secrets.token_hex(3)
        self._doc["rotinas"].append({"id": rid, "nome": nome, "tipo": tipo, "quando": quando, "texto": texto,
                                     "silenciavel": bool(silenciavel), "ativa": True,
                                     "proxima": nxt.isoformat(timespec="minutes")})
        self._gravar()
        return rid

    def remover(self, rid: str) -> bool:
        antes = len(self._doc["rotinas"])
        self._doc["rotinas"] = [r for r in self._doc["rotinas"] if r["id"] != rid]
        self._gravar()
        return len(self._doc["rotinas"]) < antes

    def definir_silencio(self, entre: str) -> None:
        if entre:
            _janela(entre)          # valida
        self._doc["silencio"] = entre
        self._gravar()

    def checar(self, agora: datetime) -> list:
        """O que fazer agora: [{rotina, acao: rodar|pulada|segurada, motivo}]. Chame a cada minuto."""
        eventos = []
        for r in self._doc["rotinas"]:
            if not r["ativa"] or not r["proxima"]:
                continue
            venc = datetime.fromisoformat(r["proxima"])
            if venc > agora:
                continue
            atraso = (agora - venc).total_seconds()
            if atraso > ATRASO[r["tipo"]]:
                acao, motivo = "pulada", f"{int(atraso // 60)} min de atraso (limite {ATRASO[r['tipo']] // 60} min)"
            elif r["silenciavel"] and self._doc["silencio"] and dentro(self._doc["silencio"], agora):
                acao, motivo = "segurada", f"horário de silêncio {self._doc['silencio']}"
            else:
                acao, motivo = "rodar", "na hora" if atraso < 60 else f"{int(atraso // 60)} min de atraso"
            nxt = proxima(r["quando"], agora)
            r["proxima"] = nxt.isoformat(timespec="minutes") if nxt else None
            if nxt is None:
                r["ativa"] = False
            eventos.append({"rotina": dict(r), "acao": acao, "motivo": motivo})
            self._doc["historico"].append({"em": agora.isoformat(timespec="minutes"), "nome": r["nome"],
                                           "acao": acao, "motivo": motivo})
        self._doc["historico"] = self._doc["historico"][-200:]
        if eventos:
            self._gravar()
        return eventos
