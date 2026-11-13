# Meu assistente — lista de ingredientes (base: INTELECTO v2)

> Para o Claude Code ou o Codex: construa **em cima** do repositório https://github.com/inematds/intelecto-v2 (clonado em `~/intelecto-v2`).
> Ele já roda (terminal e Telegram, Ollama/OpenRouter, memória, trava, aprovação, cofre e caixa) e tem testes automáticos.
> Leia `README.md` e `CLAUDE.md` do repositório antes de começar.

## Como usar este arquivo

1. `cd ~/intelecto-v2` e copie este arquivo para lá.
2. Abra o agente na pasta e peça: "Leia meu-assistente.md e implemente os ingredientes marcados como a acrescentar e parcial, um de cada vez, seguindo as Regras para o agente."
3. Mais seguro: rode o agente dentro da caixa-do-agente (https://inematds.github.io/caixa-do-agente/guia/) e aplique só o patch revisado.

**Total: 10 ingredientes** · ✅ já existem no v2: 5 · 🟡 parciais: 1 · ➕ a acrescentar: 4

---

## Integrações e Protocolos

Onde encaixa no v2: peça 4 · Cérebro (`intelecto/provedores/`) ou peça 6 · Ferramentas (`intelecto/ferramentas/`)

### 1. Suporte a LLM Local (Ollama) (`Local LLM Support`)

**O que faz**: Execute modelos de IA no seu próprio computador. Zero custo de API. Privacidade total. Sem necessidade de internet. Use junto com OpenRouter: nuvem quando precisa de potência, local quando precisa de privacidade.

**No INTELECTO v2**: ✅ já existe — `intelecto/provedores/ollama.py` (testado ao vivo com qwen3.6 e llama3.2). Só ajuste se precisar.

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), ZeroClaw, PicoClaw, Agent Zero, NanoBot (https://github.com/HKUDS/nanobot), INTELECTO, Hermes (https://github.com/NousResearch/hermes-agent), AIOS (https://github.com/agiresearch/AIOS)

---

## Segurança e Proteção

Onde encaixa no v2: peças 7 e 8 · Trava, cofre e caixa (`intelecto/seguranca/`)

### 1. Mapa de Dados Local-First (`Local-First Data Map`)

**O que faz**: Mapa explícito do que fica no seu hardware (config, SQLite, skills, secrets em env) vs o que sai (prompts ao provider, memória opt para Honcho cloud).

**No INTELECTO v2**: 🟡 parcial — tudo do assistente em `~/.intelecto2` (config, memória, cofre, auditoria)

**Quem já implementa (para estudar)**: Hermes (https://github.com/NousResearch/hermes-agent)

---

### 2. Armazenamento Criptografado de Segredos (`Encrypted Secret Store`)

**O que faz**: Chaves de API armazenadas com criptografia de nível militar (ChaCha20). Mesmo que alguém roube o arquivo, não conseguirá lê-lo.

**No INTELECTO v2**: ✅ já existe — `intelecto/seguranca/cofre.py` (Fernet se houver o pacote cryptography; senão cifra da biblioteca padrão). Só ajuste se precisar.

**Quem já implementa (para estudar)**: ZeroClaw, IronClaw

---

### 3. Isolamento por Container VM (`Container VM Isolation`)

**O que faz**: Cada conversa roda em sua própria máquina virtual. Isolamento completo em nível de SO. A barreira mais forte entre a IA e seu sistema.

**No INTELECTO v2**: ✅ já existe — `intelecto/seguranca/executor.py`: executor `caixa` (Docker sem rede, só a pasta de trabalho). Só ajuste se precisar.

**Quem já implementa (para estudar)**: NanoClaw

---

### 4. Lista de Bloqueio de Comandos Perigosos (`Command Blocklist`)

**O que faz**: Bloqueia automaticamente comandos que podem danificar seu sistema (deletar tudo, formatar discos, reiniciar, etc.)

**No INTELECTO v2**: ✅ já existe — `intelecto/seguranca/trava.py`: roda / pergunta / recusa (o padrão é perguntar). Só ajuste se precisar.

**Quem já implementa (para estudar)**: PicoClaw, NanoBot (https://github.com/HKUDS/nanobot), ZeroClaw

---

## Memória e Conhecimento

Onde encaixa no v2: peça 5 · Memória (`intelecto/memoria/store.py` + ferramentas de memória)

### 1. Recall SQLite FTS5 / BM25 (sem embeddings) (`SQLite FTS5 / BM25 Recall`)

**O que faz**: Memória persistente local em 3 camadas (conversas com TTL, fatos sem TTL, skills) com busca full-text BM25 — sem embeddings, offline, recall em milissegundos.

**No INTELECTO v2**: ✅ já existe — `intelecto/memoria/store.py`. Só ajuste se precisar.

**Quem já implementa (para estudar)**: Hermes (https://github.com/NousResearch/hermes-agent), INTELECTO

---

## Skills Integradas e Ferramentas Prontas

Onde encaixa no v2: peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

### 1. Whisper Speech-to-Text (`Whisper Speech-to-Text`)

**O que faz**: Converta gravações de voz em texto. Funciona localmente (sem chave de API) ou via OpenAI Whisper API.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoClaw

---

### 2. Busca Web Privada SearXNG (`SearXNG Private Search`)

**O que faz**: Motor de busca web auto-hospedado. Sem rastreamento, sem chaves de API. Privacidade total na busca.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: Agent Zero

---

### 3. Automação do Vault do Obsidian (`Obsidian Vault Integration`)

**O que faz**: Trabalhe com vaults do Obsidian e automatize o gerenciamento de notas em markdown simples.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

### 4. Perguntas e Respostas sobre Documentos (PDF, Planilha, HTML) (`Document Query Tool`)

**O que faz**: Faça upload de documentos e faça perguntas sobre eles. A IA extrai respostas dos seus arquivos.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: Agent Zero

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
