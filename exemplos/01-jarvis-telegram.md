# Meu assistente — lista de ingredientes (base: INTELECTO v2)

> Para o Claude Code ou o Codex: construa **em cima** do repositório https://github.com/inematds/intelecto-v2 (clonado em `~/intelecto-v2`).
> Ele já roda (terminal e Telegram, Ollama/OpenRouter, memória, trava, aprovação, cofre e caixa) e tem testes automáticos.
> Leia `README.md` e `CLAUDE.md` do repositório antes de começar.

## Como usar este arquivo

1. `cd ~/intelecto-v2` e copie este arquivo para lá.
2. Abra o agente na pasta e peça: "Leia meu-assistente.md e implemente os ingredientes marcados como a acrescentar e parcial, um de cada vez, seguindo as Regras para o agente."
3. Mais seguro: rode o agente dentro da caixa-do-agente (https://inematds.github.io/caixa-do-agente/guia/) e aplique só o patch revisado.

**Total: 12 ingredientes** · ✅ já existem no v2: 5 · 🟡 parciais: 3 · ➕ a acrescentar: 4

---

## Identidade e Personalidade

Onde encaixa no v2: peça 3 · Identidade (`intelecto/identidade/` e `Contexto` em `agente/loop.py`)

### 1. Arquivo de Personalidade Soul.md (`Soul.md Personality File`)

**O que faz**: Defina a personalidade, os valores e o estilo de comunicação da sua IA em um arquivo de texto simples. Como escrever uma ficha de personagem.

**No INTELECTO v2**: ✅ já existe — `intelecto/identidade/SOUL.md` (+ AGENTS.md, USER.md e MEMORY.md), lidos em `agente/loop.py` (Contexto). Só ajuste se precisar.

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoBot (https://github.com/HKUDS/nanobot), ZeroClaw, PicoClaw

---

## Canais de Comunicação

Onde encaixa no v2: peça 1 · Canal (`intelecto/canais/` + subcomando novo em `cli.py`)

### 1. Bot do Telegram (`Telegram Bot`)

**O que faz**: Configuração mais fácil — apenas um token. Suporte a mídia rica, botões inline, compartilhamento de arquivos. Ótimo para equipes.

**No INTELECTO v2**: ✅ já existe — `intelecto/canais/telegram.py` (long polling, só responde aos ids em telegram_donos). Só ajuste se precisar.

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoBot (https://github.com/HKUDS/nanobot), PicoClaw, ZeroClaw, IronClaw, TinyClaw, ClaudeClaw (https://github.com/earlyaidopters/claudeclaw-os), Hermes (https://github.com/NousResearch/hermes-agent)

---

## Memória e Conhecimento

Onde encaixa no v2: peça 5 · Memória (`intelecto/memoria/store.py` + ferramentas de memória)

### 1. Sistema de Memória em Duas Camadas (`Two-Layer Memory`)

**O que faz**: Camada 1: Fatos rápidos (MEMORY.md). Camada 2: Log de histórico pesquisável. Simples, mas eficaz.

**No INTELECTO v2**: 🟡 parcial — MEMORY.md (semente, lida uma vez) + memoria.db; falta a camada de histórico de conversas pesquisável

**Quem já implementa (para estudar)**: NanoBot (https://github.com/HKUDS/nanobot), PicoClaw

---

### 2. Recall SQLite FTS5 / BM25 (sem embeddings) (`SQLite FTS5 / BM25 Recall`)

**O que faz**: Memória persistente local em 3 camadas (conversas com TTL, fatos sem TTL, skills) com busca full-text BM25 — sem embeddings, offline, recall em milissegundos.

**No INTELECTO v2**: ✅ já existe — `intelecto/memoria/store.py`. Só ajuste se precisar.

**Quem já implementa (para estudar)**: Hermes (https://github.com/NousResearch/hermes-agent), INTELECTO

---

## Skills Integradas e Ferramentas Prontas

Onde encaixa no v2: peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

### 1. Armazenar / Recuperar / Esquecer Memória (`Memory Store/Recall/Forget`)

**O que faz**: Ferramentas dedicadas para salvar, pesquisar e excluir memórias. A IA gerencia sua própria base de conhecimento.

**No INTELECTO v2**: 🟡 parcial — salvar_memoria e buscar_memoria em `ferramentas/basicas.py` e "lembre que…" direto no loop; esquecer existe (`Memorias.esquecer`) mas não é ferramenta

**Quem já implementa (para estudar)**: ZeroClaw, IronClaw, Agent Zero

---

### 2. Previsão do Tempo (Sem Chave de API) (`Weather Skill`)

**O que faz**: Obtenha o clima atual e previsões usando serviços gratuitos. Sem chave de API necessária.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoBot (https://github.com/HKUDS/nanobot), PicoClaw

---

### 3. Suite Google Workspace (Gmail, Calendar, Drive, Sheets, Docs, Slides) (`Google Workspace Suite`)

**O que faz**: Integração completa com o Google Workspace: envie e-mails, gerencie calendário, leia/escreva documentos, crie planilhas, construa apresentações.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), IronClaw

---

## Automação e Agendamento

Onde encaixa no v2: peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

### 1. Agendamento Cron (`Cron Scheduling`)

**O que faz**: Execute tarefas em um cronograma: "toda segunda-feira às 9h, me envie um briefing." Funciona como um despertador confiável para sua IA.

**No INTELECTO v2**: ➕ a acrescentar — peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoClaw, NanoBot (https://github.com/HKUDS/nanobot), PicoClaw, ZeroClaw, TinyClaw, IronClaw

---

### 2. Agente Proativo por Heartbeat (`Heartbeat Proactive Agent`)

**O que faz**: Scheduler embutido (APScheduler) com zombie detection, reclaim e retries: briefings, lembretes e check-ins proativos que fazem o agente parecer vivo 24/7.

**No INTELECTO v2**: ➕ a acrescentar — peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

**Quem já implementa (para estudar)**: Hermes (https://github.com/NousResearch/hermes-agent)

---

## Segurança e Proteção

Onde encaixa no v2: peças 7 e 8 · Trava, cofre e caixa (`intelecto/seguranca/`)

### 1. Armazenamento Criptografado de Segredos (`Encrypted Secret Store`)

**O que faz**: Chaves de API armazenadas com criptografia de nível militar (ChaCha20). Mesmo que alguém roube o arquivo, não conseguirá lê-lo.

**No INTELECTO v2**: ✅ já existe — `intelecto/seguranca/cofre.py` (Fernet se houver o pacote cryptography; senão cifra da biblioteca padrão). Só ajuste se precisar.

**Quem já implementa (para estudar)**: ZeroClaw, IronClaw

---

### 2. Controle de Acesso por Código de Pareamento (`Pairing Code Access`)

**O que faz**: Novos usuários devem inserir um código de 6 dígitos que você fornece antes de conversar com sua IA. Impede acesso não autorizado.

**No INTELECTO v2**: 🟡 parcial — lista de ids donos (`telegram_donos`) + comando /id; não há código de pareamento

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), ZeroClaw, TinyClaw

---

### 3. Gates de Aprovação de Execução (`Execution Approval Gates`)

**O que faz**: A IA deve pedir sua permissão antes de executar certos comandos. Três níveis: somente leitura, supervisionado, autonomia total.

**No INTELECTO v2**: ✅ já existe — `intelecto/seguranca/aprovacao.py`: políticas perigosos / sempre / nunca; no terminal e por /sim /nao no Telegram. Só ajuste se precisar.

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), ZeroClaw

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
