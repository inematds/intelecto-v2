"""Agentes em .md e a regra de quais ferramentas cada um recebe.

Um agente é um arquivo .md: cabeçalho entre linhas '---' (nome, titulo, ferramentas, minutos, rodadas)
e, embaixo, a instrução. Agente novo = arquivo novo, sem mexer em código.

AS REGRAS (decididas aqui, no código, e não no prompt — o agente lê páginas de estranhos, e nada
do que ele lê pode aumentar o que ele pode fazer):
  1. Web e memória nunca no mesmo agente. Um agente que abre endereços poderia ser levado por uma
     página a colocar o que sabe de você dentro de um endereço. Quem tem web perde a memória.
  2. Agente de fundo (trabalha sem você olhando) não recebe ferramenta que age: rodar comando,
     escrever arquivo fora da pasta da tarefa, mandar mensagem.
  3. Ferramenta que ninguém conhece é descartada, e o motivo fica registrado.
"""
import os
from dataclasses import dataclass, field

from ..ferramentas.base import Registro

WEB = {"buscar_web", "abrir_pagina"}
MEMORIA = {"salvar_memoria", "buscar_memoria"}
AGEM = {"rodar_comando", "escrever_arquivo", "enviar_mensagem"}
CONHECIDAS = WEB | MEMORIA | AGEM | {"ler_arquivo", "listar_arquivos", "anotar", "gravar_relatorio"}


@dataclass
class Perfil:
    nome: str
    titulo: str = ""
    ferramentas: list = field(default_factory=list)
    minutos: int = 10
    rodadas: int = 50
    instrucao: str = ""
    arquivo: str = ""


def _inteiro(valor, padrao, minimo, maximo) -> int:
    try:
        return max(minimo, min(maximo, int(str(valor).strip())))
    except (TypeError, ValueError):
        return padrao


def ler_perfil(texto: str, arquivo: str = "") -> Perfil:
    cab, corpo = {}, texto
    linhas = texto.splitlines()
    if linhas and linhas[0].strip() == "---":
        try:
            fim = next(i for i in range(1, len(linhas)) if linhas[i].strip() == "---")
        except StopIteration:
            raise ValueError(f"{arquivo or 'perfil'}: cabeçalho sem o '---' de fechamento")
        for ln in linhas[1:fim]:
            if ":" in ln:
                k, v = ln.split(":", 1)
                cab[k.strip().lower()] = v.strip()
        corpo = "\n".join(linhas[fim + 1:])
    nome = cab.get("nome") or os.path.splitext(os.path.basename(arquivo))[0]
    if not nome:
        raise ValueError("perfil sem nome")
    ferr = [f.strip() for f in cab.get("ferramentas", "").split(",") if f.strip()]
    return Perfil(nome=nome, titulo=cab.get("titulo", nome), ferramentas=ferr,
                  minutos=_inteiro(cab.get("minutos"), 10, 1, 240),
                  rodadas=_inteiro(cab.get("rodadas"), 50, 1, 1000),
                  instrucao=corpo.strip(), arquivo=arquivo)


def carregar(pasta: str, log=print) -> dict:
    """Todos os .md da pasta. Um arquivo com defeito não impede os outros de carregar."""
    perfis = {}
    if not os.path.isdir(pasta):
        return perfis
    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith(".md"):
            continue
        caminho = os.path.join(pasta, nome)
        try:
            with open(caminho, encoding="utf-8") as f:
                p = ler_perfil(f.read(), caminho)
            perfis[p.nome] = p
        except (OSError, ValueError) as e:
            log(f"[perfis] ignorado {nome}: {e}")
    return perfis


def permitidas(pedidas, fundo: bool = True) -> tuple:
    """(ferramentas que o agente recebe, [(ferramenta, motivo) das que ficaram de fora])."""
    fora, nomes = [], []
    for n in dict.fromkeys(pedidas):
        if n not in CONHECIDAS:
            fora.append((n, "ferramenta desconhecida"))
        elif fundo and n in AGEM:
            fora.append((n, "agente de fundo não recebe ferramenta que age"))
        else:
            nomes.append(n)
    if WEB & set(nomes):
        for n in [x for x in nomes if x in MEMORIA]:
            nomes.remove(n)
            fora.append((n, "quem acessa a web não acessa a sua memória"))
    return nomes, fora


def registro_do_perfil(registro: Registro, perfil: Perfil, fundo: bool = True) -> tuple:
    """Um Registro novo só com o que o perfil pode usar (e que existe no registro)."""
    nomes, fora = permitidas(perfil.ferramentas, fundo)
    novo = Registro()
    for n in nomes:
        f = registro.pegar(n)
        if f is not None:
            novo.adicionar(f)
    return novo, fora
