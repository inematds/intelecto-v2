# INTELECTO v2

[![INTELECTO v2 — Seu Jarvis seguro](guia/assets/banner.jpg)](https://inematds.github.io/intelecto-v2/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

**Seu próprio Jarvis, que lembra de você e não mexe no que não deve.**

## O que é

Você quer um assistente de IA só seu, que lembre das suas coisas, mas não quer entregar seus dados nem deixar uma
IA solta no computador. O INTELECTO v2 é um assistente pessoal gratuito que você instala no seu computador e
conversa com ele pelo terminal ou pelo Telegram. Ele pensa com uma IA que roda na sua máquina (Ollama, sem custo)
ou na nuvem (OpenRouter), guarda memórias, mexe só numa pasta de trabalho e pede a sua aprovação antes de qualquer
comando que não seja só de leitura. Você precisa de Python 3.10 ou mais novo; nada mais é obrigatório.

Python puro: **nenhum pacote para instalar**, 1.500 linhas que dá para ler numa tarde. Com `executor = caixa`,
cada comando roda num container descartável sem internet.

## 🎓 Curso grátis

**Seu Jarvis seguro: INTELECTO v2 e caixa-do-agente** (9 aulas, PT/EN/ES): **https://inematds.github.io/intelecto-v2-curso/**

## 📖 Guia de uso

Guia completo (landing + passo a passo): **https://inematds.github.io/intelecto-v2/guia/**

## Em 1 minuto

```bash
cd ~ && git clone https://github.com/inematds/intelecto-v2 && cd intelecto-v2
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

## Monte o seu: a mercearia e 5 exemplos prontos

O INTELECTO v2 é a base que já funciona. Para ir além, a **mercearia** (https://inematds.github.io/intelecto-v2/guia/mercearia/)
tem 144 ingredientes de 12 projetos de agentes. Você escolhe, ela gera o **`meu-assistente.md`**, e o Claude Code ou o
Codex constrói em cima do INTELECTO. Cada item vem marcado: ✅ já existe no v2 (com o arquivo), 🟡 parcial, ➕ a acrescentar
(com a peça onde encaixa), e o arquivo termina com as regras para o agente (um item por vez, com teste).

| Exemplo pronto | Diagrama | Arquivo |
|---|---|---|
| Jarvis pessoal no Telegram | [ver](exemplos/01-jarvis-telegram.jpg) | [exemplos/01-jarvis-telegram.md](exemplos/01-jarvis-telegram.md) |
| Atendente do pequeno negócio | [ver](exemplos/02-atendente-negocio.jpg) | [exemplos/02-atendente-negocio.md](exemplos/02-atendente-negocio.md) |
| Programador seguro | [ver](exemplos/03-programador-seguro.jpg) | [exemplos/03-programador-seguro.md](exemplos/03-programador-seguro.md) |
| 100% local e privado | [ver](exemplos/04-local-privado.jpg) | [exemplos/04-local-privado.md](exemplos/04-local-privado.md) |
| Casa inteligente com voz | [ver](exemplos/05-casa-voz.jpg) | [exemplos/05-casa-voz.md](exemplos/05-casa-voz.md) |

```bash
cd ~/intelecto-v2 && cp exemplos/01-jarvis-telegram.md meu-assistente.md
# no Claude Code ou no Codex, aberto nesta pasta:
# "Leia meu-assistente.md e implemente os itens a acrescentar e parciais, um de cada vez, seguindo as Regras para o agente."
```

## Recursos avançados (v2.1)

Seis peças a mais em `intelecto/avancado/`, testadas e sem dependência: **agentes em .md**, **web e memória nunca no
mesmo agente**, **citação conferida em código** (frase inventada não entra; `[n]` sem fonte vira `[?]`), **tarefa longa**
que retoma do último passo e entrega o que tem quando o tempo acaba, **rotinas** com atraso por tipo e horário de silêncio,
**escada de cérebros** com descanso por tipo de erro e **desfazer**. Veja tudo rodando: `python3 -m intelecto avancado`.
Ainda não estão ligadas à conversa nem ao Telegram; o passo a passo para ligar está em
[docs/RECURSOS-AVANCADOS.md](docs/RECURSOS-AVANCADOS.md).

## Medir: ele está acertando? (v2.2)

Você troca de modelo ou mexe na identidade e não sabe se o assistente ficou melhor ou pior. O `avaliar` responde com
número: roda 8 tarefas fixas (guardar e lembrar, ler e gravar arquivo, comando de leitura, as duas travas e uma conta),
cada uma numa pasta limpa, e diz quantas acertou, quanto tempo levou, quantas rodadas usou e quantos tokens gastou.

```bash
python3 -m intelecto avaliar                                   # o cérebro do seu config
python3 -m intelecto avaliar --provedor ollama --modelo llama3.2  # outro cérebro, mesmo teste
python3 -m intelecto avaliar --comparar                        # todas as medições lado a lado
```

Cada medição fica gravada em `~/.intelecto2/avaliacoes/`. Na medição ninguém aprova nada: só comando de leitura roda.
Para medir o que importa para você, escreva as suas tarefas num JSON (`--tarefas minhas.json`); o formato está no
topo de `intelecto/avaliacao.py`. O cérebro de mentira (`--provedor mock`) acerta 7 de 8: ele não sabe fazer conta,
e a medição mostra isso.

Medido aqui em 14/11/2026, na mesma máquina e com as mesmas 8 tarefas:

| Cérebro | Acerto | Tempo por tarefa | Observação |
|---|---|---|---|
| `mock` | 7 de 8 | 0,1 s | errou só a conta (de propósito) |
| `ollama/llama3.2` (3B) | 7 de 8 | 1,1 s | leu o `notas.txt` mas respondeu que não achou a hora |
| `ollama/qwen3.6:35b-a3b` | 6 de 8 e 5 de 8 | 7,7–8,1 s | as falhas foram do cérebro caindo (erro de CUDA com a GPU dividida), marcadas como "caiu" e não como resposta errada |

Moral: o número só vale com a máquina livre, e o modelo pequeno foi bem em tarefa curta. Meça o seu antes de escolher.

## O processo, do início ao fim

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Baixar | `cd ~ && git clone https://github.com/inematds/intelecto-v2 && cd intelecto-v2` | você |
| 2 | Ver funcionando sem nada instalado | `python3 -m intelecto demo` | ⚙️ script |
| 3 | Instalar o cérebro local | [ollama.com](https://ollama.com) → `ollama pull qwen3.6:35b-a3b` (ou um modelo menor, ver o guia) | você |
| 4 | Configurar | `python3 -m intelecto configurar` | você |
| 5 | Dar a sua cara | editar `~/.intelecto2/identidade/SOUL.md`, `USER.md`, `MEMORY.md` | você |
| 6 | Conferir | `python3 -m intelecto verificar` → `tudo certo` | ⚙️ script |
| 7 | Conversar | `python3 -m intelecto` | você |
| 8 | Telegram (opcional) | @BotFather → `python3 -m intelecto cofre guardar telegram` → `/id` no bot → seu id no `configurar` → `python3 -m intelecto telegram` | você |
| 9 | Ligar sozinho (opcional) | `servico/intelecto-telegram.service` (Linux) ou `servico/club.inema.intelecto.plist` (macOS) | ⚙️ serviço |
| 10 | Rodar comandos na caixa (opcional) | `configurar` → executor `caixa` (precisa de Docker) | você |
| 11 | Provar que está tudo certo | `python3 -m pytest -q` → `113 passed` | ⚙️ testes |
| 12 | Proteger o projeto com a caixa-do-agente | ver [Como a caixa-do-agente melhora o seu projeto](#como-a-caixa-do-agente-melhora-o-seu-projeto) | você |
| 13 | Ver os recursos avançados | `python3 -m intelecto avancado` | ⚙️ script |
| 13b | Medir o seu assistente (e comparar cérebros) | `python3 -m intelecto avaliar` → `--comparar` | ⚙️ script |
| 14 | Ir além: escolher ingredientes e gerar o `meu-assistente.md` | [mercearia](https://inematds.github.io/intelecto-v2/guia/mercearia/) ou `exemplos/*.md` → entregar ao Claude Code/Codex na pasta | você + 🤖 agente |

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
python3 -m intelecto avancado
python3 -m intelecto avaliar [--provedor P --modelo M] [--tarefas minhas.json] [--tempo 180] [--comparar] [--nao-gravar]
```

Tudo do assistente fica em `~/.intelecto2/` (troque com `INTELECTO_HOME`): `config.json`, `memoria.db`,
`identidade/`, `area/` (a única pasta que as ferramentas enxergam), `auditoria.jsonl` e o cofre (`.cofre`).

## O que foi testado, e onde

| Item | Como foi testado (12/11/2026) |
|---|---|
| Loop, memória, ferramentas, trava, aprovação, cofre, auditoria | 68 testes automáticos (`python3 -m pytest -q`) |
| Ollama local | ao vivo com `qwen3.6:35b-a3b`: guardou "meu nome é Nei e moro em Porto Alegre" e lembrou numa execução seguinte. Com `llama3.2` (3B) quase não usa as ferramentas sozinho; desde a v2.0.1, "lembre que …" é guardado direto pelo assistente, e o llama3.2 também lembrou (13/11/2026). |
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

Resultado real nesta máquina: o `.env` ficou fora da cópia, `67 passed, 1 skipped` (o teste que precisa de Docker
dentro da caixa é pulado) e `0 arquivo(s) mudaram`. Os números do auditor estão no guia.

## Versões

- **v2.2**: medição (`python3 -m intelecto avaliar`): acerto, tempo, rodadas e tokens por cérebro, com `--comparar`.
- **v2.1**: recursos avançados em `intelecto/avancado/` ([docs/RECURSOS-AVANCADOS.md](docs/RECURSOS-AVANCADOS.md)).
- **v2 (este repo)**: código completo e testado, sem dependências, Linux e macOS, caixa por comando.
- **v1**: [inematds/intelecto](https://github.com/inematds/intelecto) (a mercearia de frameworks e o plano) e o curso
  [intelecto-curso](https://inematds.github.io/intelecto-curso/) continuam no ar. O que mudou: [docs/v1-para-v2.md](docs/v1-para-v2.md).

Licença MIT · [inema.club](https://inema.club)
