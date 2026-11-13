"""As ferramentas que vêm de fábrica: memória, arquivos (só na pasta de trabalho) e comando."""
import os

from .base import Ferramenta, Resultado

MAX_LEITURA = 100 * 1024


class SalvarMemoria(Ferramenta):
    nome = "salvar_memoria"
    descricao = "Guarda um fato ou preferência do dono para lembrar depois."
    parametros = {"type": "object", "properties": {"conteudo": {"type": "string", "description": "o fato, numa frase"}},
                  "required": ["conteudo"]}

    def __init__(self, memorias):
        self.memorias = memorias

    async def executar(self, **args) -> Resultado:
        conteudo = str(args.get("conteudo", "")).strip()
        if not conteudo:
            return Resultado(False, "nada para guardar")
        return Resultado(True, f"guardado (#{self.memorias.salvar(conteudo)}): {conteudo}")


class BuscarMemoria(Ferramenta):
    nome = "buscar_memoria"
    descricao = "Procura nas memórias guardadas por palavras."
    parametros = {"type": "object", "properties": {"busca": {"type": "string"}}, "required": ["busca"]}

    def __init__(self, memorias):
        self.memorias = memorias

    async def executar(self, **args) -> Resultado:
        achados = self.memorias.buscar(str(args.get("busca", "")))
        return Resultado(True, "; ".join(m.conteudo for m in achados) if achados else "(nada encontrado)")


def _dentro(area: str, caminho: str) -> str:
    area = os.path.realpath(area)
    alvo = os.path.realpath(os.path.join(area, os.path.expanduser(caminho)))
    if alvo != area and not alvo.startswith(area + os.sep):
        raise ValueError("fora da pasta de trabalho")
    return alvo


class LerArquivo(Ferramenta):
    nome = "ler_arquivo"
    descricao = "Lê um arquivo de texto da pasta de trabalho (até 100 KB)."
    parametros = {"type": "object", "properties": {"caminho": {"type": "string"}}, "required": ["caminho"]}

    def __init__(self, area):
        self.area = area

    async def executar(self, **args) -> Resultado:
        try:
            alvo = _dentro(self.area, str(args.get("caminho", "")))
        except ValueError as e:
            return Resultado(False, str(e))
        if not os.path.isfile(alvo):
            return Resultado(False, "arquivo não existe")
        with open(alvo, encoding="utf-8", errors="replace") as f:
            return Resultado(True, f.read(MAX_LEITURA))


class EscreverArquivo(Ferramenta):
    nome = "escrever_arquivo"
    descricao = "Grava um arquivo de texto na pasta de trabalho (cria ou substitui)."
    parametros = {"type": "object", "properties": {"caminho": {"type": "string"}, "texto": {"type": "string"}},
                  "required": ["caminho", "texto"]}

    def __init__(self, area):
        self.area = area

    async def executar(self, **args) -> Resultado:
        try:
            alvo = _dentro(self.area, str(args.get("caminho", "")))
        except ValueError as e:
            return Resultado(False, str(e))
        os.makedirs(os.path.dirname(alvo), exist_ok=True)
        with open(alvo, "w", encoding="utf-8") as f:
            f.write(str(args.get("texto", "")))
        return Resultado(True, f"gravado: {os.path.relpath(alvo, os.path.realpath(self.area))}")


class ListarArquivos(Ferramenta):
    nome = "listar_arquivos"
    descricao = "Lista os arquivos de uma pasta dentro da pasta de trabalho."
    parametros = {"type": "object", "properties": {"pasta": {"type": "string", "default": "."}}}

    def __init__(self, area):
        self.area = area

    async def executar(self, **args) -> Resultado:
        try:
            alvo = _dentro(self.area, str(args.get("pasta", ".") or "."))
        except ValueError as e:
            return Resultado(False, str(e))
        if not os.path.isdir(alvo):
            return Resultado(False, "pasta não existe")
        itens = sorted(os.listdir(alvo))[:200]
        return Resultado(True, "\n".join(itens) or "(vazia)")


class RodarComando(Ferramenta):
    nome = "rodar_comando"
    descricao = ("Roda um comando de terminal na pasta de trabalho. Comandos que só leem rodam direto; "
                 "os outros precisam do OK do dono; os destrutivos são recusados.")
    parametros = {"type": "object", "properties": {"comando": {"type": "string"}}, "required": ["comando"]}

    def __init__(self, portao, executor):
        self.portao = portao
        self.executor = executor

    async def executar(self, **args) -> Resultado:
        comando = str(args.get("comando", ""))
        pode, porque = await self.portao.decidir(comando)
        if not pode:
            return Resultado(False, f"não rodei: {porque}")
        rc, saida = await self.executor.rodar(comando)
        onde = "na caixa" if self.executor.nome == "caixa" else "local"
        return Resultado(rc == 0, f"[{onde}, saída {rc}] {saida}".strip())


def padrao(memorias, area, portao, executor) -> list:
    return [SalvarMemoria(memorias), BuscarMemoria(memorias), LerArquivo(area), EscreverArquivo(area),
            ListarArquivos(area), RodarComando(portao, executor)]
