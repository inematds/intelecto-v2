"""Portão de aprovação: quem decide se um comando "aprovar" roda.

Políticas (config.aprovacao):
  perigosos — livre roda; aprovar pergunta ao dono; bloqueado nunca   (padrão)
  sempre    — até o livre pergunta
  nunca     — ninguém pergunta: só o livre roda, o resto é recusado (modo sem dono por perto)

O "perguntar" é uma função async que o canal fornece (terminal: input; Telegram: /sim /nao).
"""
from .trava import APROVAR, BLOQUEADO, LIVRE, classificar


async def recusar_sempre(comando: str, motivo: str) -> bool:
    return False


class Portao:
    def __init__(self, politica: str = "perigosos", perguntar=None, auditoria=None):
        self.politica = politica
        self.perguntar = perguntar or recusar_sempre
        self.auditoria = auditoria

    async def decidir(self, comando: str) -> tuple:
        """Devolve (pode_rodar, explicacao)."""
        v = classificar(comando)
        if v.classe == BLOQUEADO:
            ok, txt = False, f"bloqueado: {v.motivo}"
        elif v.classe == LIVRE and self.politica != "sempre":
            ok, txt = True, "livre (só leitura)"
        elif self.politica == "nunca":
            ok, txt = False, f"recusado: precisa de aprovação ({v.motivo or 'só leitura'}) e a política é 'nunca'"
        else:
            sim = await self.perguntar(comando, v.motivo or "confirmação pedida pela política 'sempre'")
            ok, txt = (True, "aprovado pelo dono") if sim else (False, "o dono não aprovou")
        if self.auditoria:
            self.auditoria.registrar("comando", comando=comando, classe=v.classe, rodou=ok, decisao=txt)
        return ok, txt
