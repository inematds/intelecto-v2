"""Liga as 8 peças: config → cofre → cérebro → memória → trava/aprovação → executor → ferramentas → agente."""
import os
import sys

from . import config as cfg
from .agente.loop import Agente
from .ferramentas.base import Registro
from .ferramentas.basicas import padrao
from .memoria.store import Memorias
from .provedores import criar as criar_provedor
from .seguranca import executor as ex
from .seguranca.aprovacao import Portao
from .seguranca.auditoria import Auditoria
from .seguranca.cofre import Cofre


class Pecas:
    pass


def montar(config=None, perguntar=None) -> Pecas:
    c = config or cfg.carregar()
    cfg.preparar_pastas(c)
    p = Pecas()
    p.config = c
    p.auditoria = Auditoria(c.log_auditoria)
    p.cofre = Cofre(c.home)
    p.memorias = Memorias(c.banco)
    p.memorias.semear(os.path.join(c.identidade, "MEMORY.md"))
    p.portao = Portao(c.aprovacao, perguntar, p.auditoria)
    p.executor = ex.criar(c)
    p.registro = Registro(padrao(p.memorias, c.area, p.portao, p.executor))
    p.provedor = criar_provedor(c, p.cofre)
    p.agente = Agente(c, p.provedor, p.memorias, p.registro, p.auditoria)
    return p


async def perguntar_no_terminal(comando: str, motivo: str) -> bool:
    """Aprovação pelo terminal. Sem terminal interativo (entrada por pipe) = não aprova."""
    if not sys.stdin.isatty():
        print(f"  [aprovação] '{comando}' precisa de OK ({motivo}); entrada não é um terminal → recusado")
        return False
    r = input(f"  [aprovação] rodar '{comando}'? ({motivo}) [s/N] ").strip().lower()
    return r in ("s", "sim", "y", "yes")
