"""Escada de cérebros: vários provedores em ordem, com descanso por tipo de erro.

Sem isso, um cérebro fora do ar custa a espera inteira (o timeout) em TODA chamada. Com a escada,
o erro é pago uma vez e o degrau descansa:

  sem cota (HTTP 429)                     5 min   — cota volta logo
  fora do ar (502/503/504, sem resposta)  30 min  — queda dura mais que uma nova tentativa
  não existe para você (404/403)          6 h     — o modelo não está na sua conta e não vai estar daqui a 1 min
  outro erro                              1 min

Se todos estão descansando, tenta o que acorda primeiro (melhor que não responder).
A própria Escada é um Provedor: entra no lugar de qualquer cérebro sem mudar o resto.
"""
import time

from ..provedores.base import ErroProvedor, Provedor

DESCANSO = {"cota": 300, "fora": 1800, "inexistente": 6 * 3600, "outro": 60}


def tipo_erro(msg: str) -> str:
    m = str(msg).lower()
    if "http 429" in m or "quota" in m or "rate limit" in m or "resource_exhausted" in m:
        return "cota"
    if "http 404" in m or "http 403" in m or "not found" in m:
        return "inexistente"
    if any(s in m for s in ("http 502", "http 503", "http 504", "sem resposta", "timed out", "timeout")):
        return "fora"
    return "outro"


class Escada(Provedor):
    nome = "escada"

    def __init__(self, provedores: list, relogio=time.monotonic, log=None):
        if not provedores:
            raise ValueError("a escada precisa de pelo menos um provedor")
        self.provedores = list(provedores)
        self.relogio = relogio
        self.log = log or (lambda s: None)
        self._ate = {}          # índice do degrau -> até quando descansa

    def descansando(self) -> dict:
        agora = self.relogio()
        return {self._rotulo(i): round(fim - agora) for i, fim in self._ate.items() if fim > agora}

    def _rotulo(self, i: int) -> str:
        p = self.provedores[i]
        return f"{i}:{p.nome}:{getattr(p, 'modelo', '')}"

    async def conversar(self, mensagens: list, ferramentas: list | None = None):
        agora = self.relogio()
        ordem = [i for i in range(len(self.provedores)) if self._ate.get(i, 0) <= agora]
        if not ordem:
            ordem = [min(self._ate, key=self._ate.get)]
        erros = []
        for i in ordem:
            try:
                r = await self.provedores[i].conversar(mensagens, ferramentas)
                self._ate.pop(i, None)
                return r
            except ErroProvedor as e:
                t = tipo_erro(e)
                self._ate[i] = self.relogio() + DESCANSO[t]
                self.log(f"[escada] {self._rotulo(i)} {t}: descansa {DESCANSO[t] // 60} min")
                erros.append(f"{self._rotulo(i)} ({t}): {e}")
        raise ErroProvedor("nenhum cérebro respondeu: " + " | ".join(erros))
