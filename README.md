# INTELECTO v2

**🇧🇷 Português · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

**O seu próprio Jarvis, que roda no seu computador, lembra de você e não mexe no que não deve.**

Assistente pessoal de IA em Python puro: **nenhum pacote para instalar**, 1.500 linhas que dá para ler numa tarde.
Fala com você no terminal ou no Telegram, pensa com um modelo **local** (Ollama, custo zero) ou na nuvem
(OpenRouter), guarda memórias num SQLite e só roda comando de terminal depois de passar por uma trava e, se
precisar, pela sua aprovação. Com `executor = caixa`, cada comando roda num container descartável sem internet.

📖 Guia completo: **https://inematds.github.io/intelecto-v2/guia/**

## Em 1 minuto

```bash
git clone https://github.com/inematds/intelecto-v2 && cd intelecto-v2
python3 -m intelecto demo          # demonstração completa, sem internet e sem modelo
python3 -m intelecto configurar    # escolhe nome, personalidade, cérebro, onde rodar comandos
python3 -m intelecto               # conversa no terminal
```

## As 8 peças

| # | Peça | Arquivo | O que faz |
|---|---|---|---|
| 1 | Canal | `canais/telegram.py`, `cli.py` | Terminal ou Telegram. No Telegram só responde aos seus ids. |
| 2 | Loop com freio | `agente/loop.py` | Pensa → usa ferramenta → responde. No máximo 5 rodadas. |
| 3 | Identidade | `identidade/*.md` | SOUL, AGENTS, USER e MEMORY: 4 arquivos de texto que você edita. |
| 4 | Cérebro | `provedores/` | Ollama (local), OpenRouter (nuvem) ou mock (testes). |
| 5 | Memória | `memoria/store.py` | SQLite + busca FTS5, sem duplicar, acha sem acento. |
| 6 | Ferramentas | `ferramentas/basicas.py` | Memória, ler/gravar/listar arquivos (só na pasta de trabalho), rodar comando. |
| 7 | Trava, aprovação e cofre | `seguranca/` | Comando que só lê roda; o resto pede OK; o destrutivo é recusado. Segredos cifrados. Tudo vai para a auditoria. |
| 8 | Caixa | `seguranca/executor.py` | Comando num container Docker sem rede, só com a pasta de trabalho. |

## O processo, do início ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Baixar | `git clone https://github.com/inematds/intelecto-v2 && cd intelecto-v2` | você |
| 2 | Ver funcionando sem nada instalado | `python3 -m intelecto demo` | ⚙️ script |
| 3 | Instalar o cérebro local | [ollama.com](https://ollama.com) → `ollama pull qwen3.6:35b-a3b` (ou um modelo menor, ver o guia) | você |
| 4 | Configurar | `python3 -m intelecto configurar` | você |
| 5 | Dar a sua cara | editar `~/.intelecto2/identidade/SOUL.md`, `USER.md`, `MEMORY.md` | você |
| 6 | Conferir | `python3 -m intelecto verificar` → `tudo certo` | ⚙️ script |
| 7 | Conversar | `python3 -m intelecto` | você |
| 8 | Telegram (opcional) | @BotFather → `python3 -m intelecto cofre guardar telegram` → `/id` no bot → seu id no `configurar` → `python3 -m intelecto telegram` | você |
| 9 | Ligar sozinho (opcional) | `servico/intelecto-telegram.service` (Linux) ou `servico/club.inema.intelecto.plist` (macOS) | ⚙️ serviço |
| 10 | Rodar comandos na caixa (opcional) | `configurar` → executor `caixa` (precisa de Docker) | você |
| 11 | Provar que está tudo certo | `python3 -m pytest -q` → `67 passed` | ⚙️ testes |
| 12 | Proteger o projeto com a caixa-do-agente | ver [Como a caixa-do-agente melhora o seu projeto](#como-a-caixa-do-agente-melhora-o-seu-projeto) | você |

## Comandos

```
python3 -m intelecto conversar [--provedor ollama|openrouter|mock] [--modelo M] [--executor local|caixa] [--aprovacao perigosos|sempre|nunca]
python3 -m intelecto demo
python3 -m intelecto telegram
python3 -m intelecto configurar [--nao-interativo --provedor P --modelo M --nome N]
python3 -m intelecto cofre guardar|listar|apagar [nome]
python3 -m intelecto memoria [busca]
python3 -m intelecto auditoria [-n 20]
python3 -m intelecto verificar
```

Tudo do assistente fica em `~/.intelecto2/` (troque com `INTELECTO_HOME`): `config.json`, `memoria.db`,
`identidade/`, `area/` (a única pasta que as ferramentas enxergam), `auditoria.jsonl` e o cofre (`.cofre`).

## O que foi testado, e onde

| Item | Como foi testado (12/11/2026) |
|---|---|
| Loop, memória, ferramentas, trava, aprovação, cofre, auditoria | 67 testes automáticos (`python3 -m pytest -q`) |
| Ollama local | ao vivo com `qwen3.6:35b-a3b`: guardou "meu nome é Nei e moro em Porto Alegre" e lembrou numa execução seguinte. Com `llama3.2` (3B) conversa, mas quase nunca usa as ferramentas. |
| Executor caixa | ao vivo, Docker 28: vê só a pasta de trabalho, não vê as variáveis do seu terminal, sem internet |
| OpenRouter e Telegram | contra servidores falsos locais (formato dos pedidos, chave no cabeçalho, filtro de dono, aprovação por /sim). **Não testados ao vivo**: dependem da sua chave e do seu bot. |
| macOS | não testado (o serviço launchd e o id da máquina pelo `ioreg` estão no código) |

## Como a caixa-do-agente melhora o seu projeto

O INTELECTO protege **o que o assistente faz** (trava, aprovação, caixa por comando). A
[caixa-do-agente](https://inematds.github.io/caixa-do-agente/guia/) protege **o projeto enquanto você ou outro agente
mexe nele** (Claude Code, Codex): roda tudo numa cópia sem senhas e sem internet, e você só aplica o que aprovar.

```bash
# 1. imagem com o pytest (a caixa não tem internet para instalar nada)
docker build -t intelecto-v2-testes caixa/
# 2. os testes do INTELECTO numa cópia sem .env, sem rede, que se apaga no fim
~/caixa-do-agente/caixa.sh ~/intelecto-v2 --imagem intelecto-v2-testes -- python3 -m pytest -q -p no:cacheprovider
# 3. nota da proteção de quem programa no projeto (só lê)
python3 ~/caixa-do-agente/auditar.py ~/intelecto-v2
```

Resultado real nesta máquina: o `.env` ficou fora da cópia, `66 passed, 1 skipped` (o teste que precisa de Docker
dentro da caixa é pulado) e `0 arquivo(s) mudaram`. Os números do auditor estão no guia.

## Versões

- **v2 (este repo)**: código completo e testado, sem dependências, Linux e macOS, caixa por comando.
- **v1**: [inematds/intelecto](https://github.com/inematds/intelecto) (a mercearia de frameworks e o plano) e o curso
  [intelecto-curso](https://inematds.github.io/intelecto-curso/) continuam no ar. O que mudou: [docs/v1-para-v2.md](docs/v1-para-v2.md).

Licença MIT · [inema.club](https://inema.club)
