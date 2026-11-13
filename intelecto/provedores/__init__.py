"""Fábrica: escolhe o cérebro pelo nome do config."""
from .base import ErroProvedor, Provedor


def criar(config, cofre=None) -> Provedor:
    if config.provedor == "mock":
        from .mock import Mock
        return Mock()
    if config.provedor == "ollama":
        from .ollama import Ollama
        return Ollama(config.modelo, config.ollama_url, config.temperatura)
    if config.provedor == "openrouter":
        from .openrouter import OpenRouter
        chave = cofre.ler("openrouter") if cofre else None
        return OpenRouter(chave, config.modelo, config.openrouter_url, config.temperatura)
    raise ErroProvedor(f"provedor desconhecido: {config.provedor}")
