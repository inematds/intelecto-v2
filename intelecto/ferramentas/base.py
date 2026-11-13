"""Contrato de ferramenta + registro."""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..provedores.base import DefFerramenta


@dataclass
class Resultado:
    ok: bool
    saida: str


class Ferramenta(ABC):
    nome: str = ""
    descricao: str = ""
    parametros: dict = {}

    @abstractmethod
    async def executar(self, **args) -> Resultado:
        ...


class Registro:
    def __init__(self, ferramentas=()):
        self._f = {}
        for f in ferramentas:
            self.adicionar(f)

    def adicionar(self, f: Ferramenta) -> None:
        self._f[f.nome] = f

    def pegar(self, nome: str):
        return self._f.get(nome)

    def todas(self) -> list:
        return list(self._f.values())

    def definicoes(self) -> list:
        return [DefFerramenta(f.nome, f.descricao, f.parametros) for f in self._f.values()]
