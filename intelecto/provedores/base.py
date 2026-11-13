"""Contrato do cérebro: recebe mensagens (+ ferramentas) e devolve texto ou pedidos de ferramenta."""
import asyncio
import json
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Mensagem:
    papel: str                      # system | user | assistant | tool
    texto: str
    chamadas: list | None = None    # [{id, nome, args}] quando o assistant pede ferramenta
    id_chamada: str | None = None   # na resposta de uma ferramenta (papel tool)
    nome: str | None = None         # nome da ferramenta (papel tool)


@dataclass
class DefFerramenta:
    nome: str
    descricao: str
    parametros: dict                # JSON Schema


@dataclass
class Resposta:
    texto: str
    chamadas: list = field(default_factory=list)   # [{id, nome, args(dict)}]
    uso: dict = field(default_factory=dict)


class ErroProvedor(RuntimeError):
    pass


class Provedor(ABC):
    nome = "base"

    @abstractmethod
    async def conversar(self, mensagens: list, ferramentas: list | None = None) -> Resposta:
        ...


def post_json(url: str, corpo: dict, cabecalhos: dict | None = None, tempo: int = 120) -> dict:
    dados = json.dumps(corpo).encode()
    req = urllib.request.Request(url, data=dados, method="POST",
                                 headers={"Content-Type": "application/json", **(cabecalhos or {})})
    try:
        with urllib.request.urlopen(req, timeout=tempo) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", "replace")[:300]
        raise ErroProvedor(f"HTTP {e.code} em {url}: {detalhe}") from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise ErroProvedor(f"sem resposta de {url}: {e}") from e


async def post_json_async(*a, **k) -> dict:
    return await asyncio.to_thread(post_json, *a, **k)


def args_dict(args) -> dict:
    if isinstance(args, dict):
        return args
    try:
        v = json.loads(args or "{}")
        return v if isinstance(v, dict) else {}
    except (TypeError, json.JSONDecodeError):
        return {}
