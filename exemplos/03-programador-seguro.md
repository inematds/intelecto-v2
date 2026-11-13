# Meu assistente — lista de ingredientes (base: INTELECTO v2)

> Para o Claude Code ou o Codex: construa **em cima** do repositório https://github.com/inematds/intelecto-v2 (clonado em `~/intelecto-v2`).
> Ele já roda (terminal e Telegram, Ollama/OpenRouter, memória, trava, aprovação, cofre e caixa) e tem testes automáticos.
> Leia `README.md` e `CLAUDE.md` do repositório antes de começar.

## Como usar este arquivo

1. `cd ~/intelecto-v2` e copie este arquivo para lá.
2. Abra o agente na pasta e peça: "Leia meu-assistente.md e implemente os ingredientes marcados como a acrescentar e parcial, um de cada vez, seguindo as Regras para o agente."
3. Mais seguro: rode o agente dentro da caixa-do-agente (https://inematds.github.io/caixa-do-agente/guia/) e aplique só o patch revisado.

**Total: 12 ingredientes** · ✅ já existem no v2: 4 · 🟡 parciais: 0 · ➕ a acrescentar: 8

---

## Skills Integradas e Ferramentas Prontas

Onde encaixa no v2: peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

### 1. Orquestração de Agentes de Codificação (`Coding Agent Orchestration`)

**O que faz**: Execute Codex CLI, Claude Code ou outros agentes de codificação programaticamente. A IA gerencia codificadores de IA.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

### 2. Operações Git (Status, Diff, Log, Commit) (`Git Operations Tool`)

**O que faz**: Operações Git estruturadas com saída JSON analisada. A IA gerencia seus repositórios de código.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: ZeroClaw

---

### 3. GitHub (Issues, PRs, CI, API) (`GitHub Integration Skill`)

**O que faz**: Fluxo de trabalho completo do GitHub: gerencie issues, revise pull requests, acione execuções de CI, consulte a API. Gerenciamento de código pelo chat.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoBot (https://github.com/HKUDS/nanobot), PicoClaw, IronClaw, ZeroClaw

---

### 4. Revisão + Preparação + Merge Automatizados de PR (`PR Review/Prepare/Merge Workflow`)

**O que faz**: Fluxo de trabalho de pull request em três etapas: a IA revisa o código, prepara as alterações e faz o merge após validação. Pipeline completo de revisão de código.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

### 5. Controle Remoto de Sessões Tmux (`Tmux Remote Control`)

**O que faz**: Envie teclas para sessões de terminal e extraia saídas. A IA opera ferramentas CLI de forma interativa.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoBot (https://github.com/HKUDS/nanobot), PicoClaw

---

## Segurança e Proteção

Onde encaixa no v2: peças 7 e 8 · Trava, cofre e caixa (`intelecto/seguranca/`)

### 1. Isolamento por Container VM (`Container VM Isolation`)

**O que faz**: Cada conversa roda em sua própria máquina virtual. Isolamento completo em nível de SO. A barreira mais forte entre a IA e seu sistema.

**No INTELECTO v2**: ✅ já existe — `intelecto/seguranca/executor.py`: executor `caixa` (Docker sem rede, só a pasta de trabalho). Só ajuste se precisar.

**Quem já implementa (para estudar)**: NanoClaw

---

### 2. Lista de Bloqueio de Comandos Perigosos (`Command Blocklist`)

**O que faz**: Bloqueia automaticamente comandos que podem danificar seu sistema (deletar tudo, formatar discos, reiniciar, etc.)

**No INTELECTO v2**: ✅ já existe — `intelecto/seguranca/trava.py`: roda / pergunta / recusa (o padrão é perguntar). Só ajuste se precisar.

**Quem já implementa (para estudar)**: PicoClaw, NanoBot (https://github.com/HKUDS/nanobot), ZeroClaw

---

### 3. Gates de Aprovação de Execução (`Execution Approval Gates`)

**O que faz**: A IA deve pedir sua permissão antes de executar certos comandos. Três níveis: somente leitura, supervisionado, autonomia total.

**No INTELECTO v2**: ✅ já existe — `intelecto/seguranca/aprovacao.py`: políticas perigosos / sempre / nunca; no terminal e por /sim /nao no Telegram. Só ajuste se precisar.

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), ZeroClaw

---

### 4. Allowlist de Egress + Sandbox Endurecido (`Egress Allowlist + Sandbox Hardening`)

**O que faz**: Sandbox de execução (firejail/bubblewrap/docker), allowlist de egress e audit log imutável; blacklist de ~/.ssh ~/.aws para conter exfiltration.

**No INTELECTO v2**: ➕ a acrescentar — peças 7 e 8 · Trava, cofre e caixa (`intelecto/seguranca/`)

**Quem já implementa (para estudar)**: Hermes (https://github.com/NousResearch/hermes-agent)

---

## Automação e Agendamento

Onde encaixa no v2: peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

### 1. Acceptance Checks (Sucesso Verificável) (`Acceptance Checks`)

**O que faz**: Tarefa agendada só conta como sucesso se a saída contém um marcador definido — um "turno retornou" deixa de ser confundido com "objetivo cumprido".

**No INTELECTO v2**: ➕ a acrescentar — peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

**Quem já implementa (para estudar)**: ClaudeClaw (https://github.com/earlyaidopters/claudeclaw-os)

---

## Padrões de Arquitetura

Onde encaixa no v2: peça 2 · Loop (`intelecto/agente/loop.py`) e a montagem (`intelecto/montagem.py`)

### 1. Isolamento de Espaço de Trabalho por Projeto (`Project Workspace Isolation`)

**O que faz**: Espaços de trabalho separados por cliente/projeto. Cada um tem sua própria memória, segredos e instruções. Sem mistura de dados.

**No INTELECTO v2**: ✅ já existe — pasta de trabalho `~/.intelecto2/area`: as ferramentas de arquivo não saem dela. Só ajuste se precisar.

**Quem já implementa (para estudar)**: Agent Zero, NanoClaw

---

## Memória e Conhecimento

Onde encaixa no v2: peça 5 · Memória (`intelecto/memoria/store.py` + ferramentas de memória)

### 1. Compactação Automática de Sessão (`Session Auto-Compaction`)

**O que faz**: Quando as conversas ficam muito longas, resume automaticamente as partes antigas para manter a IA rápida enquanto preserva informações essenciais.

**No INTELECTO v2**: ➕ a acrescentar — peça 5 · Memória (`intelecto/memoria/store.py` + ferramentas de memória)

**Quem já implementa (para estudar)**: NanoClaw, IronClaw

---

## Regras para o agente (não pule)

1. Parta do código que existe. Antes de escrever, leia `README.md`, `CLAUDE.md` e a peça indicada no item.
2. Um ingrediente por vez: implemente, escreva o teste em `tests/` e rode `python3 -m pytest -q`. Só siga com tudo verde.
3. Sem dependência obrigatória nova. Se precisar de um pacote, deixe opcional (como o `cryptography` no cofre).
4. Nunca enfraqueça a trava (`intelecto/seguranca/trava.py`) nem a aprovação. Ferramenta nova que executa algo passa pelo `Portao`.
5. Token, chave e senha só no cofre: `python3 -m intelecto cofre guardar <nome>`. Nada de segredo no código nem no config.
6. Testes nunca chamam API de verdade: use o `ServidorFalso` de `tests/conftest.py`.
7. Mudou o jeito de usar? Atualize a tabela "O processo, do início ao fim" do README no mesmo commit.
8. Diga "pronto" só com a saída dos testes na mão; o que não foi testado ao vivo, diga que não foi.

---

*Gerado pela Mercearia do INTELECTO v2 — https://inematds.github.io/intelecto-v2/guia/mercearia/*
