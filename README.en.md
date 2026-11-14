# INTELECTO v2

[![INTELECTO v2 — Your safe Jarvis](guia/assets/banner-en.jpg)](https://inematds.github.io/intelecto-v2/guia/en/)

**🇧🇷 [Português](README.md) · 🇺🇸 English · 🇪🇸 [Español](README.es.md)**

**Your own Jarvis, which remembers you and doesn’t touch what it shouldn’t.**

## What it is

You want a personal AI assistant that remembers your things, but you don’t want to hand over your data or leave an AI running loose on your computer. INTELECTO v2 is a free personal assistant that you install on your computer and talk to through the terminal or Telegram. It thinks with an AI running on your machine (Ollama, at no cost) or in the cloud (OpenRouter), stores memories, works only in a workspace folder, and asks for your approval before any command that isn’t read-only. You need Python 3.10 or newer; nothing else is required.

Pure Python: **no packages to install**, 1,500 lines you can read in an afternoon. With `executor = caixa`, each command runs in a disposable container without internet access.

## 🎓 Free course

**Your safe Jarvis: INTELECTO v2 and caixa-do-agente** (9 lessons, PT/EN/ES): **https://inematds.github.io/intelecto-v2-curso/en/**

## 📖 User guide

Complete guide (landing page + step-by-step): **https://inematds.github.io/intelecto-v2/guia/en/**

## In 1 minute

```bash
cd ~ && git clone https://github.com/inematds/intelecto-v2 && cd intelecto-v2
python3 -m intelecto demo          # full demo, no internet or model needed
python3 -m intelecto configurar    # choose a name, personality, brain, and where to run commands
python3 -m intelecto               # chat in the terminal
```

## The 8 parts

| # | Part | File | What it does |
|---|---|---|---|
| 1 | Channel | `canais/telegram.py`, `cli.py` | Terminal or Telegram. On Telegram, it only replies to your IDs. |
| 2 | Loop with brakes | `agente/loop.py` | Thinks → uses a tool → replies. At most 5 rounds. |
| 3 | Identity | `identidade/*.md` | SOUL, AGENTS, USER, and MEMORY: 4 text files you can edit. |
| 4 | Brain | `provedores/` | Ollama (local), OpenRouter (cloud), or mock (tests). |
| 5 | Memory | `memoria/store.py` | SQLite + FTS5 search, no duplicates, finds words without accents. |
| 6 | Tools | `ferramentas/basicas.py` | Memory, read/write/list files (only in the workspace folder), run commands. |
| 7 | Lock, approval, and vault | `seguranca/` | Read-only commands run; everything else requires approval; destructive commands are refused. Secrets are encrypted. Everything is logged for auditing. |
| 8 | Box | `seguranca/executor.py` | Runs commands in a Docker container without network access, with only the workspace folder. |

## Build your own: the grocery store and 5 ready-made examples

INTELECTO v2 is the foundation that already works. To go further, the **grocery store** (https://inematds.github.io/intelecto-v2/guia/mercearia/en/)
has 144 ingredients from 12 agent projects. You choose, it generates **`meu-assistente.md`**, and Claude Code or
Codex builds on top of INTELECTO. Each item is marked: ✅ already exists in v2 (with the file), 🟡 partial, ➕ to add
(with the part it fits into), and the file ends with the rules for the agent (one item at a time, with a test).

| Ready-made example | Diagram | File |
|---|---|---|
| Personal Jarvis on Telegram | [view](exemplos/01-jarvis-telegram.jpg) | [exemplos/01-jarvis-telegram.md](exemplos/01-jarvis-telegram.md) |
| Small business assistant | [view](exemplos/02-atendente-negocio.jpg) | [exemplos/02-atendente-negocio.md](exemplos/02-atendente-negocio.md) |
| Secure programmer | [view](exemplos/03-programador-seguro.jpg) | [exemplos/03-programador-seguro.md](exemplos/03-programador-seguro.md) |
| 100% local and private | [view](exemplos/04-local-privado.jpg) | [exemplos/04-local-privado.md](exemplos/04-local-privado.md) |
| Voice-controlled smart home | [view](exemplos/05-casa-voz.jpg) | [exemplos/05-casa-voz.md](exemplos/05-casa-voz.md) |

```bash
cd ~/intelecto-v2 && cp exemplos/01-jarvis-telegram.md meu-assistente.md
# in Claude Code or Codex, open in this folder:
# "Read meu-assistente.md and implement the items to add and the partial ones, one at a time, following the Rules for the agent."
```

## Advanced features (v2.1)

Six additional components in `intelecto/avancado/`, tested and dependency-free: **agents in .md**, **web and memory never in
the same agent**, **citations checked in code** (invented phrases are excluded; `[n]` without a source becomes `[?]`), **long-running tasks**
that resume from the last step and deliver what they have when time runs out, **routines** with delays by type and quiet hours,
a **brain ladder** with cooldowns by error type, and **undo**. See everything in action: `python3 -m intelecto avancado`.
They are not yet connected to the conversation or Telegram; instructions for connecting them are in
[docs/RECURSOS-AVANCADOS.md](docs/RECURSOS-AVANCADOS.md).

## Measure: Is it getting things right? (v2.2)

You switch models or change the identity and don’t know whether the assistant got better or worse. `avaliar` gives you a
number: it runs 8 fixed tasks (save and recall, read and write a file, a read command, both safeguards, and a calculation),
each in a clean folder, and tells you how many it got right, how long it took, how many rounds it used, and how many tokens it spent.

```bash
python3 -m intelecto avaliar                                   # the brain in your config
python3 -m intelecto avaliar --provedor ollama --modelo llama3.2  # another brain, same test
python3 -m intelecto avaliar --comparar                        # all measurements side by side
```

Each measurement is saved in `~/.intelecto2/avaliacoes/`. Nothing is approved during the measurement: only read commands run.
To measure what matters to you, write your tasks in a JSON file (`--tarefas minhas.json`); the format is at the
top of `intelecto/avaliacao.py`. The fake brain (`--provedor mock`) gets 7 out of 8 right: it can’t do calculations,
and the measurement shows that.

Measured here on 14/11/2026, on the same machine and with the same 8 tasks:

| Cérebro | Acerto | Tempo por tarefa | Observação |
|---|---|---|---|
| `mock` | 7 de 8 | 0,1 s | errou só a conta (de propósito) |
| `ollama/llama3.2` (3B) | 7 de 8 | 1,1 s | leu o `notas.txt` mas respondeu que não achou a hora |
| `ollama/qwen3.6:35b-a3b` | 6 de 8 e 5 de 8 | 7,7–8,1 s | as falhas foram do cérebro caindo (erro de CUDA com a GPU dividida), marcadas como "caiu" e não como resposta errada |

Moral: the number only counts when the machine is free, and the small model did well on a short task. Measure yours before choosing.

## The process, from start to finish

| # | Step | Command | Who |
|---|---|---|---|
| 1 | Download | `cd ~ && git clone https://github.com/inematds/intelecto-v2 && cd intelecto-v2` | you |
| 2 | See it working with nothing installed | `python3 -m intelecto demo` | ⚙️ script |
| 3 | Install the local brain | [ollama.com](https://ollama.com) → `ollama pull qwen3.6:35b-a3b` (or a smaller model; see the guide) | you |
| 4 | Configure | `python3 -m intelecto configurar` | you |
| 5 | Make it your own | edit `~/.intelecto2/identidade/SOUL.md`, `USER.md`, `MEMORY.md` | you |
| 6 | Verify | `python3 -m intelecto verificar` → `tudo certo` | ⚙️ script |
| 7 | Chat | `python3 -m intelecto` | you |
| 8 | Telegram (optional) | @BotFather → `python3 -m intelecto cofre guardar telegram` → `/id` in the bot → your ID in `configurar` → `python3 -m intelecto telegram` | you |
| 9 | Run automatically (optional) | `servico/intelecto-telegram.service` (Linux) or `servico/club.inema.intelecto.plist` (macOS) | ⚙️ service |
| 10 | Run commands in the box (optional) | `configurar` → executor `caixa` (requires Docker) | you |
| 11 | Make sure everything is working | `python3 -m pytest -q` → `113 passed` | ⚙️ tests |
| 12 | Protect the project with caixa-do-agente | see [How caixa-do-agente improves your project](#how-caixa-do-agente-improves-your-project) | you |
| 13 | See the advanced features | `python3 -m intelecto avancado` | ⚙️ script |
| 13b | Measure your assistant (and compare brains) | `python3 -m intelecto avaliar` → `--comparar` | ⚙️ script |

## Commands

```
python3 -m intelecto conversar [--provedor ollama|openrouter|mock] [--modelo M] [--executor local|caixa] [--aprovacao perigosos|sempre|nunca]
python3 -m intelecto demo
python3 -m intelecto telegram
python3 -m intelecto configurar [--nao-interativo --provedor P --modelo M --nome N]
python3 -m intelecto cofre guardar|listar|apagar [nome]
python3 -m intelecto memoria [busca]
python3 -m intelecto auditoria [-n 20]
python3 -m intelecto verificar
python3 -m intelecto avancado
python3 -m intelecto avaliar [--provedor P --modelo M] [--tarefas minhas.json] [--tempo 180] [--comparar] [--nao-gravar]
```

All assistant data is stored in `~/.intelecto2/` (change it with `INTELECTO_HOME`): `config.json`, `memoria.db`,
`identidade/`, `area/` (the only folder the tools can see), `auditoria.jsonl`, and the vault (`.cofre`).

## What was tested, and where

| Item | How it was tested (12/11/2026) |
|---|---|
| Loop, memory, tools, lock, approval, vault, audit | 68 automated tests (`python3 -m pytest -q`) |
| Local Ollama | live with `qwen3.6:35b-a3b`: stored “my name is Nei and I live in Porto Alegre” and recalled it in a later run. `llama3.2` (3B) rarely uses the tools on its own; since v2.0.1, "lembre que …" (remember that…) is saved directly by the assistant, and llama3.2 remembered too (13/11/2026). |
| Box executor | live, Docker 28: sees only the workspace folder, can’t see your terminal’s environment variables, no internet |
| OpenRouter and Telegram | against local fake servers (request format, key in header, owner filter, approval via /sim). **Not tested live**: they depend on your key and bot. |
| macOS | not tested (the launchd service and machine ID via `ioreg` are in the code) |

## How caixa-do-agente improves your project

INTELECTO protects **what the assistant does** (lock, approval, per-command box). The
[caixa-do-agente](https://inematds.github.io/caixa-do-agente/guia/) protects **the project while you or another agent
works on it** (Claude Code, Codex): it runs everything in a copy without passwords or internet access, and you only apply what you approve.

```bash
# 1. image with pytest (the box has no internet access to install anything)
docker build -t intelecto-v2-testes caixa/
# 2. INTELECTO tests in a copy without .env or network, deleted at the end
~/caixa-do-agente/caixa.sh ~/intelecto-v2 --imagem intelecto-v2-testes -- python3 -m pytest -q -p no:cacheprovider
# 3. protection report for the person programming on the project (read-only)
python3 ~/caixa-do-agente/auditar.py ~/intelecto-v2
```

Actual result on this machine: `.env` stayed out of the copy, `67 passed, 1 skipped` (the test that needs Docker inside the box is skipped), and `0 arquivo(s) mudaram`. The auditor’s numbers are in the guide.

## Versions

- **v2.2**: measurement (`python3 -m intelecto avaliar`): accuracy, time, rounds, and tokens per brain, with `--comparar`.
- **v2.1**: advanced features in `intelecto/avancado/` ([docs/RECURSOS-AVANCADOS.md](docs/RECURSOS-AVANCADOS.md), in Portuguese).
- **v2 (this repo)**: complete and tested code, no dependencies, Linux and macOS, per-command box.
- **v1**: [inematds/intelecto](https://github.com/inematds/intelecto) (the framework supermarket and the plan) and the
  [intelecto-curso](https://inematds.github.io/intelecto-curso/) course are still online. What changed: [docs/v1-para-v2.md](docs/v1-para-v2.md) (in Portuguese).

MIT License · [inema.club](https://inema.club)