"""Cérebro de mentira, sem rede: serve para a demonstração e os testes.

Segue um roteiro simples e previsível que exercita o loop inteiro:
  "lembre que X"      → pede salvar_memoria(X)
  "… meu/minha …?"    → pede buscar_memoria
  "rode: CMD"         → pede rodar_comando(CMD)
  "leia ARQ"          → pede ler_arquivo(ARQ)
Depois que a ferramenta responde, devolve um texto com o resultado.
"""
import re

from .base import Provedor, Resposta


class Mock(Provedor):
    nome = "mock"

    def __init__(self):
        self.chamadas = 0

    async def conversar(self, mensagens, ferramentas=None) -> Resposta:
        self.chamadas += 1
        ultimo = next((m for m in reversed(mensagens) if m.papel in ("user", "tool")), None)
        if ultimo is None:
            return Resposta("Olá!")
        if ultimo.papel == "tool":
            return Resposta(f"Feito. Resultado de {ultimo.nome}: {ultimo.texto}")
        texto = ultimo.texto.strip()
        baixo = texto.lower()
        if not ferramentas:
            return Resposta(f"Você disse: {texto}")
        m = re.match(r"(lembre|lembra|guarde)( que)?\s+(.+)", baixo)
        if m:
            fato = texto[len(texto) - len(m.group(3)):].strip()
            return Resposta("", [{"id": "c1", "nome": "salvar_memoria", "args": {"conteudo": fato}}])
        if baixo.endswith("?") and re.search(r"\b(meu|minha|meus|minhas)\b", baixo):
            termo = re.sub(r"[^\w ]", " ", baixo).split()[-1]
            return Resposta("", [{"id": "c2", "nome": "buscar_memoria", "args": {"busca": termo}}])
        m = re.match(r"(rode|execute|roda)\s*:?\s*(.+)", texto, re.I)
        if m:
            return Resposta("", [{"id": "c3", "nome": "rodar_comando", "args": {"comando": m.group(2)}}])
        m = re.match(r"(leia|abra)\s+(.+)", texto, re.I)
        if m:
            return Resposta("", [{"id": "c4", "nome": "ler_arquivo", "args": {"caminho": m.group(2).strip()}}])
        return Resposta(f"Você disse: {texto}")
