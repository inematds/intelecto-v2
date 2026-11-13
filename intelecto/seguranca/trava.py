"""Trava de comandos: classifica cada comando ANTES de rodar.

Três resultados:
  livre     — só lê (ls, cat, grep…): roda sem perguntar
  aprovar   — qualquer outro: precisa do OK do dono (ver aprovacao.py)
  bloqueado — destrutivo conhecido: nunca roda, nem com OK

Diferente da v1 (lista de palavras proibidas), aqui o padrão é "precisa aprovar":
só o que está na lista de leitura passa direto. A lista de bloqueio é a segunda rede,
não a primeira. A rede de verdade é a caixa (executor="caixa").
"""
import re
import shlex
from dataclasses import dataclass

LIVRE, APROVAR, BLOQUEADO = "livre", "aprovar", "bloqueado"

# Comandos que só leem. Qualquer coisa fora daqui pede aprovação.
SO_LEITURA = {
    "ls", "cat", "head", "tail", "wc", "grep", "pwd", "date", "whoami", "df", "du",
    "echo", "uname", "file", "stat", "sort", "uniq", "cut", "tr", "basename", "dirname",
    "true", "env", "printenv", "uptime", "free", "id", "which", "realpath", "nl", "tree",
}
# Opções que transformam um comando de leitura em escrita/execução.
OPCOES_PERIGOSAS = {"find": {"-delete", "-exec", "-execdir", "-ok", "-fprint"}}

# Padrões destrutivos: bloqueados sempre (texto normalizado, minúsculo).
PADROES_BLOQUEIO = [
    (r"\bmkfs(\.\w+)?\b", "formatar disco"),
    (r"\bdd\b.*\bof=/dev/", "escrever direto no disco"),
    (r">\s*/dev/(sd|nvme|hd|mmcblk)", "escrever direto no disco"),
    (r"\b(shutdown|reboot|halt|poweroff)\b", "desligar a máquina"),
    (r":\(\)\s*\{\s*:\|:&\s*\};:", "fork bomb"),
    (r"\bchmod\b.*-r.*\b777\b\s+/(\s|$)", "abrir permissão do sistema inteiro"),
    (r"\b(curl|wget)\b[^|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b", "baixar e executar script"),
    (r"\bsudo\b", "comando como administrador"),
    (r"shutil\.rmtree\(\s*['\"](/|~)", "apagar a raiz por código"),
    (r"\bos\.system\(.*rm\s+-", "apagar por código"),
]
ALVOS_RAIZ = {"/", "/*", "~", "~/", "~/*", "$home", "${home}", "$home/", "..", "../", "/home", "/etc", "/usr", "/var", "/boot"}


@dataclass
class Veredito:
    classe: str
    motivo: str = ""


def _segmentos(comando: str) -> list:
    """Divide em comandos simples: ; && || | e quebra de linha."""
    partes = re.split(r"\|\||&&|[;|\n]", comando)
    return [p.strip() for p in partes if p.strip()]


def _rm_perigoso(tokens: list) -> bool:
    if not tokens or tokens[0] not in ("rm", "/bin/rm", "/usr/bin/rm"):
        return False
    recursivo = False
    alvos = []
    for t in tokens[1:]:
        if t.startswith("--"):
            recursivo |= t in ("--recursive",)
        elif t.startswith("-") and len(t) > 1:
            recursivo |= ("r" in t[1:].lower())
        else:
            alvos.append(t.lower().rstrip())
    return recursivo and any(a in ALVOS_RAIZ or a.startswith("/") and a.count("/") == 1 for a in alvos)


def classificar(comando: str) -> Veredito:
    texto = " ".join((comando or "").split())
    if not texto:
        return Veredito(BLOQUEADO, "comando vazio")
    baixo = texto.lower()
    for padrao, motivo in PADROES_BLOQUEIO:
        if re.search(padrao, baixo):
            return Veredito(BLOQUEADO, motivo)
    pior = LIVRE
    motivo = ""
    if "$(" in texto or "`" in texto or re.search(r"(^|[^>])>{1,2}[^&]", texto) or "<(" in texto:
        pior, motivo = APROVAR, "substituição de comando ou redirecionamento para arquivo"
    for seg in _segmentos(texto):
        try:
            tokens = shlex.split(seg)
        except ValueError:
            return Veredito(APROVAR, "aspas sem fechar")
        if not tokens:
            continue
        if _rm_perigoso(tokens):
            return Veredito(BLOQUEADO, "apagar pasta do sistema ou a pasta pessoal")
        # interpretador com código na linha: olha o código também
        if tokens[0] in ("bash", "sh", "zsh", "dash") and "-c" in tokens:
            interno = tokens[tokens.index("-c") + 1] if tokens.index("-c") + 1 < len(tokens) else ""
            v = classificar(interno)
            if v.classe == BLOQUEADO:
                return v
            pior, motivo = APROVAR, "shell com código na linha"
            continue
        base = tokens[0].rsplit("/", 1)[-1]
        if base in OPCOES_PERIGOSAS and set(tokens[1:]) & OPCOES_PERIGOSAS[base]:
            pior, motivo = APROVAR, f"{base} com opção que altera arquivos"
        elif base not in SO_LEITURA and base not in OPCOES_PERIGOSAS:
            pior, motivo = APROVAR, f"'{base}' não é só leitura"
    return Veredito(pior, motivo)
