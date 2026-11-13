"""Configuração: um arquivo JSON na pasta do assistente (INTELECTO_HOME, padrão ~/.intelecto2).

Nada de segredo aqui: chaves e tokens ficam no cofre (seguranca/cofre.py).
"""
import json
import os
import shutil
from dataclasses import asdict, dataclass, field, fields

PROVEDORES = ("ollama", "openrouter", "mock")
APROVACAO = ("perigosos", "sempre", "nunca")
EXECUTORES = ("local", "caixa")


def pasta_home() -> str:
    return os.path.abspath(os.path.expanduser(os.environ.get("INTELECTO_HOME", "~/.intelecto2")))


@dataclass
class Config:
    nome: str = "INTELECTO"
    personalidade: str = "Direto, honesto, sem enrolação."
    provedor: str = "ollama"
    modelo: str = "qwen3.6:35b-a3b"
    ollama_url: str = "http://localhost:11434"
    openrouter_url: str = "https://openrouter.ai/api/v1"
    telegram_url: str = "https://api.telegram.org"
    telegram_donos: list = field(default_factory=list)  # ids que podem falar com o bot
    aprovacao: str = "perigosos"   # perigosos | sempre | nunca
    executor: str = "local"        # local | caixa (container sem rede)
    imagem_caixa: str = "python:3.12-slim"
    max_rodadas: int = 5
    tempo_comando: int = 60
    temperatura: float = 0.4

    def validar(self) -> list:
        erros = []
        if self.provedor not in PROVEDORES:
            erros.append(f"provedor deve ser um de {PROVEDORES}")
        if self.aprovacao not in APROVACAO:
            erros.append(f"aprovacao deve ser um de {APROVACAO}")
        if self.executor not in EXECUTORES:
            erros.append(f"executor deve ser um de {EXECUTORES}")
        if not 1 <= int(self.max_rodadas) <= 20:
            erros.append("max_rodadas entre 1 e 20")
        if not 1 <= int(self.tempo_comando) <= 3600:
            erros.append("tempo_comando entre 1 e 3600 segundos")
        return erros

    # caminhos derivados
    @property
    def home(self) -> str:
        return pasta_home()

    @property
    def arquivo(self) -> str:
        return os.path.join(self.home, "config.json")

    @property
    def banco(self) -> str:
        return os.path.join(self.home, "memoria.db")

    @property
    def area(self) -> str:
        """Pasta de trabalho: a única que as ferramentas de arquivo e shell enxergam."""
        return os.path.join(self.home, "area")

    @property
    def identidade(self) -> str:
        return os.path.join(self.home, "identidade")

    @property
    def log_auditoria(self) -> str:
        return os.path.join(self.home, "auditoria.jsonl")


def existe() -> bool:
    return os.path.isfile(os.path.join(pasta_home(), "config.json"))


def carregar() -> Config:
    c = Config()
    if os.path.isfile(c.arquivo):
        with open(c.arquivo, encoding="utf-8") as f:
            dados = json.load(f)
        nomes = {x.name for x in fields(Config)}
        for k, v in dados.items():
            if k in nomes:
                setattr(c, k, v)
    return c


def salvar(c: Config) -> str:
    erros = c.validar()
    if erros:
        raise ValueError("; ".join(erros))
    os.makedirs(c.home, mode=0o700, exist_ok=True)
    tmp = c.arquivo + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(asdict(c), f, ensure_ascii=False, indent=2)
    os.replace(tmp, c.arquivo)
    return c.arquivo


def preparar_pastas(c: Config) -> None:
    """Cria a pasta do assistente e copia os 4 arquivos de identidade na 1ª vez."""
    os.makedirs(c.home, mode=0o700, exist_ok=True)
    os.makedirs(c.area, exist_ok=True)
    os.makedirs(c.identidade, exist_ok=True)
    modelos = os.path.join(os.path.dirname(__file__), "identidade")
    for nome in ("SOUL.md", "AGENTS.md", "USER.md", "MEMORY.md"):
        destino = os.path.join(c.identidade, nome)
        if not os.path.exists(destino):
            shutil.copy(os.path.join(modelos, nome), destino)
