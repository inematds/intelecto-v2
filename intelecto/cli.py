"""Linha de comando: python3 -m intelecto <comando>.

  conversar   conversa no terminal (padrão)
  demo        demonstração completa sem rede (cérebro de mentira)
  telegram    liga o bot do Telegram
  configurar  assistente de configuração (pergunta e grava config.json)
  cofre       guardar | listar | apagar segredos
  memoria     lista ou busca memórias
  auditoria   últimas linhas do registro de auditoria
  verificar   confere tudo o que o assistente precisa
  avancado    demonstração dos recursos avançados (tarefas, rotinas, citações, escada, desfazer)
  avaliar     mede o assistente: tarefas fixas → acerto, tempo, rodadas e tokens (--comparar)
"""
import argparse
import asyncio
import getpass
import json
import os
import shutil
import sqlite3
import sys
import urllib.request

from . import VERSAO
from . import config as cfg


def _config(a) -> cfg.Config:
    c = cfg.carregar()
    for campo in ("provedor", "modelo", "executor", "aprovacao"):
        v = getattr(a, campo, None)
        if v:
            setattr(c, campo, v)
    erros = c.validar()
    if erros:
        sys.exit("config inválida: " + "; ".join(erros))
    return c


def cmd_conversar(a) -> int:
    from .montagem import montar, perguntar_no_terminal
    p = montar(_config(a), perguntar_no_terminal)
    interativo = sys.stdin.isatty()
    if interativo:
        print(f"{p.config.nome} v{VERSAO} · cérebro {p.config.provedor}/{p.config.modelo} · comandos {p.config.executor} · "
              f"aprovação {p.config.aprovacao}\nEscreva e tecle Enter. 'sair' para terminar.\n")

    async def laco():
        while True:
            try:
                linha = input("você> " if interativo else "")
            except EOFError:
                break
            linha = linha.strip()
            if not linha:
                continue
            if linha.lower() in ("sair", "exit", "quit"):
                break
            if not interativo:
                print(f"você> {linha}")
            print(f"{p.config.nome.lower()}> {await p.agente.responder('terminal', linha)}\n", flush=True)
    asyncio.run(laco())
    return 0


DEMO = [
    "lembre que meu nome é Ana e moro em Curitiba",
    "qual meu nome?",
    "rode: ls",
    "rode: echo teste > nota.txt",
    "rode: rm -rf /",
    "leia ../../etc/passwd",
]


def cmd_demo(a) -> int:
    import tempfile
    from .montagem import montar
    os.environ["INTELECTO_HOME"] = tempfile.mkdtemp(prefix="intelecto-demo-")
    c = cfg.Config(provedor="mock", modelo="mock", nome="INTELECTO")
    p = montar(c)
    print(f"Demonstração sem rede (cérebro de mentira) · pasta temporária {c.home}\n")

    async def roda():
        for frase in DEMO:
            print(f"você> {frase}")
            print(f"intelecto> {await p.agente.responder('demo', frase)}\n")
    asyncio.run(roda())
    print("Auditoria desta demonstração:")
    for linha in p.auditoria.ultimas(20):
        if linha["tipo"] == "comando":
            print(f"  {linha['classe']:9} rodou={str(linha['rodou']):5} {linha['comando']}  ({linha['decisao']})")
    shutil.rmtree(c.home, ignore_errors=True)
    return 0


def cmd_telegram(a) -> int:
    from .canais.telegram import Telegram
    from .montagem import montar
    p = montar(_config(a))
    token = p.cofre.ler("telegram")
    if not token:
        sys.exit("sem token: rode `python3 -m intelecto cofre guardar telegram` (token do @BotFather)")
    bot = Telegram(token, p.config.telegram_donos, p.config.telegram_url, p.auditoria)

    async def ao_receber(chat, texto, perguntar):
        p.portao.perguntar = perguntar      # aprovação vai para o celular de quem pediu
        return await p.agente.responder(chat, texto)
    donos = ", ".join(map(str, p.config.telegram_donos)) or "NENHUM (só /id responde)"
    print(f"Bot ligado · donos: {donos} · Ctrl+C para parar")
    try:
        asyncio.run(bot.rodar(ao_receber))
    except KeyboardInterrupt:
        pass
    return 0


def modelos_ollama(url: str) -> list:
    """Modelos já baixados no Ollama (vazio se ele não responder)."""
    try:
        with urllib.request.urlopen(f"{url}/api/tags", timeout=3) as r:
            return [m["name"] for m in json.loads(r.read())["models"]]
    except (OSError, ValueError, KeyError):
        return []


def _pergunta(texto, padrao):
    r = input(f"{texto} [{padrao}]: ").strip()
    return r or padrao


def cmd_configurar(a) -> int:
    c = cfg.carregar()
    if a.nao_interativo:
        for campo in ("provedor", "modelo", "nome", "executor", "aprovacao"):
            v = getattr(a, campo, None)
            if v:
                setattr(c, campo, v)
    else:
        print("Configuração do INTELECTO (Enter mantém o valor entre colchetes)\n")
        c.nome = _pergunta("Nome do assistente", c.nome)
        c.personalidade = _pergunta("Personalidade em uma frase", c.personalidade)
        c.provedor = _pergunta("Cérebro: ollama (local, grátis) | openrouter (nuvem) | mock", c.provedor)
        if c.provedor == "ollama":
            instalados = modelos_ollama(c.ollama_url)
            if instalados:
                print(f"  modelos instalados no seu Ollama: {', '.join(instalados)}")
                if c.modelo.split(':')[0] not in {m.split(':')[0] for m in instalados}:
                    c.modelo = instalados[0]
            else:
                print(f"  Ollama não respondeu em {c.ollama_url}: instale em https://ollama.com e baixe um modelo (ollama pull ...)")
        c.modelo = _pergunta("Modelo", c.modelo)
        c.executor = _pergunta("Onde rodar comandos: local | caixa (Docker sem rede)", c.executor)
        c.aprovacao = _pergunta("Aprovação: perigosos | sempre | nunca", c.aprovacao)
        donos = _pergunta("Seus ids do Telegram (vírgula; vazio = sem Telegram)", ",".join(map(str, c.telegram_donos)))
        c.telegram_donos = [d.strip() for d in donos.split(",") if d.strip()]
    print(f"gravado: {cfg.salvar(c)}")
    cfg.preparar_pastas(c)
    print(f"identidade: {c.identidade} (edite SOUL.md, AGENTS.md, USER.md, MEMORY.md)")
    return 0


def cmd_cofre(a) -> int:
    from .seguranca.cofre import Cofre
    cf = Cofre(cfg.pasta_home())
    if a.acao == "listar":
        print("\n".join(cf.listar()) or "(cofre vazio)")
    elif a.acao == "guardar":
        valor = os.environ.get("INTELECTO_SEGREDO") or getpass.getpass(f"valor de '{a.nome}' (não aparece na tela): ")
        cf.guardar(a.nome, valor.strip())
        print(f"guardado '{a.nome}' ({cf.motor})")
    elif a.acao == "apagar":
        print("apagado" if cf.apagar(a.nome) else "não existe")
    return 0


def cmd_memoria(a) -> int:
    from .memoria.store import Memorias
    m = Memorias(cfg.carregar().banco)
    itens = m.buscar(" ".join(a.busca)) if a.busca else m.recentes(30)
    for x in itens:
        print(f"#{x.id:<4} {x.criada}  {x.conteudo}")
    print(f"({m.total()} memórias no total)")
    return 0


def cmd_auditoria(a) -> int:
    from .seguranca.auditoria import Auditoria
    for linha in Auditoria(cfg.carregar().log_auditoria).ultimas(a.n):
        print(json.dumps(linha, ensure_ascii=False))
    return 0


def cmd_verificar(a) -> int:
    from .seguranca.cofre import Cofre
    c = cfg.carregar()
    falhas = 0

    def linha(ok, texto):
        nonlocal falhas
        falhas += 0 if ok else 1
        print(f"[{'OK' if ok else 'FALTA'}] {texto}")
    linha(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]} (precisa 3.10+)")
    try:
        sqlite3.connect(":memory:").execute("create virtual table t using fts5(x)")
        linha(True, "SQLite com FTS5 (memória)")
    except sqlite3.OperationalError:
        linha(False, "SQLite sem FTS5")
    linha(cfg.existe(), f"config em {c.arquivo}" if cfg.existe() else "sem config: rode `python3 -m intelecto configurar`")
    cf = Cofre(c.home)
    print(f"[INFO] cofre: {cf.motor} ({'Fernet' if cf.motor == 'fernet' else 'biblioteca padrão; para Fernet: pip install cryptography'})")
    if c.provedor == "ollama":
        nomes = modelos_ollama(c.ollama_url)
        if not nomes:
            linha(False, f"Ollama não responde em {c.ollama_url} ou não tem modelo (instale: https://ollama.com)")
        else:
            ok = any(n.split(":")[0] == c.modelo.split(":")[0] for n in nomes)
            linha(ok, f"Ollama no ar com o modelo {c.modelo}" if ok else
                  f"o modelo {c.modelo} não está no seu Ollama (tem: {', '.join(nomes)}); rode `configurar` e escolha um deles")
    if c.provedor == "openrouter":
        linha("openrouter" in cf.listar(), "chave do OpenRouter no cofre")
    if c.executor == "caixa":
        linha(shutil.which("docker") is not None, "Docker instalado (executor caixa)")
    if c.telegram_donos:
        linha("telegram" in cf.listar(), "token do Telegram no cofre")
    print("tudo certo" if not falhas else f"{falhas} item(ns) faltando")
    return 1 if falhas else 0


def cmd_avancado(a) -> int:
    from .avancado.demo import rodar
    return rodar()


def cmd_avaliar(a) -> int:
    from . import avaliacao as av
    from .provedores import criar as criar_provedor
    from .seguranca.cofre import Cofre
    home = cfg.pasta_home()
    if a.comparar:
        print(av.tabela_comparar(av.anteriores(home)))
        return 0
    c = _config(a)
    try:
        tarefas = av.ler_tarefas(a.tarefas) if a.tarefas else av.TAREFAS
    except (OSError, ValueError) as e:
        sys.exit(f"tarefas: {e}")
    cerebro = criar_provedor(c, Cofre(home))      # a chave vem da sua pasta; as tarefas rodam em pastas limpas
    print(f"Medindo {c.provedor}/{c.modelo} em {len(tarefas)} tarefas (cada uma numa pasta limpa; ninguém aprova nada)\n")
    rel = asyncio.run(av.avaliar(c, cerebro, tarefas, a.tempo, ao_terminar=lambda r: print(av.linha_tarefa(r), flush=True)))
    print("\n" + av.texto_resumo(rel))
    if not a.nao_gravar:
        print(f"gravado: {av.salvar(rel, home)}  (compare com `python3 -m intelecto avaliar --comparar`)")
    return 0 if rel["resumo"]["acertos"] == rel["resumo"]["tarefas"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="intelecto", description=f"INTELECTO v{VERSAO} — assistente pessoal de IA")
    ap.add_argument("--versao", action="version", version=VERSAO)
    sub = ap.add_subparsers(dest="cmd")

    def opcoes(s):
        s.add_argument("--provedor", choices=cfg.PROVEDORES)
        s.add_argument("--modelo")
        s.add_argument("--executor", choices=cfg.EXECUTORES)
        s.add_argument("--aprovacao", choices=cfg.APROVACAO)
        return s
    opcoes(sub.add_parser("conversar", help="conversar no terminal")).set_defaults(f=cmd_conversar)
    sub.add_parser("demo", help="demonstração sem rede").set_defaults(f=cmd_demo)
    opcoes(sub.add_parser("telegram", help="ligar o bot do Telegram")).set_defaults(f=cmd_telegram)
    s = opcoes(sub.add_parser("configurar", help="configurar"))
    s.add_argument("--nome")
    s.add_argument("--nao-interativo", action="store_true")
    s.set_defaults(f=cmd_configurar)
    s = sub.add_parser("cofre", help="segredos cifrados")
    s.add_argument("acao", choices=("guardar", "listar", "apagar"))
    s.add_argument("nome", nargs="?", default="")
    s.set_defaults(f=cmd_cofre)
    s = sub.add_parser("memoria", help="listar/buscar memórias")
    s.add_argument("busca", nargs="*")
    s.set_defaults(f=cmd_memoria)
    s = sub.add_parser("auditoria", help="registro de auditoria")
    s.add_argument("-n", type=int, default=20)
    s.set_defaults(f=cmd_auditoria)
    sub.add_parser("verificar", help="conferir instalação").set_defaults(f=cmd_verificar)
    sub.add_parser("avancado", help="demonstração dos recursos avançados").set_defaults(f=cmd_avancado)
    s = opcoes(sub.add_parser("avaliar", help="medir acerto, tempo, rodadas e tokens"))
    s.add_argument("--tarefas", help="arquivo JSON com as suas tarefas (padrão: as 8 do intelecto)")
    s.add_argument("--tempo", type=int, default=180, help="segundos no máximo por tarefa")
    s.add_argument("--comparar", action="store_true", help="mostra as medições gravadas lado a lado")
    s.add_argument("--nao-gravar", action="store_true", help="não grava o resultado")
    s.set_defaults(f=cmd_avaliar)
    a = ap.parse_args(argv)
    if not a.cmd:
        if not cfg.existe() and sys.stdin.isatty():
            print("Primeira vez: vamos configurar.\n")
            a = ap.parse_args(["configurar"])
        else:
            a = ap.parse_args(["conversar"])
    if a.cmd == "cofre" and a.acao in ("guardar", "apagar") and not a.nome:
        ap.error("diga o nome do segredo (ex.: telegram, openrouter)")
    return a.f(a) or 0
