# Meu assistente — lista de ingredientes (base: INTELECTO v2)

> Para o Claude Code ou o Codex: construa **em cima** do repositório https://github.com/inematds/intelecto-v2 (clonado em `~/intelecto-v2`).
> Ele já roda (terminal e Telegram, Ollama/OpenRouter, memória, trava, aprovação, cofre e caixa) e tem testes automáticos.
> Leia `README.md` e `CLAUDE.md` do repositório antes de começar.

## Como usar este arquivo

1. `cd ~/intelecto-v2` e copie este arquivo para lá.
2. Abra o agente na pasta e peça: "Leia meu-assistente.md e implemente os ingredientes marcados como a acrescentar e parcial, um de cada vez, seguindo as Regras para o agente."
3. Mais seguro: rode o agente dentro da caixa-do-agente (https://inematds.github.io/caixa-do-agente/guia/) e aplique só o patch revisado.

**Total: 12 ingredientes** · ✅ já existem no v2: 2 · 🟡 parciais: 2 · ➕ a acrescentar: 8

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

### 1. Integração com WhatsApp (`WhatsApp Integration`)

**O que faz**: Converse com sua IA pelo WhatsApp. Envie mensagens, imagens, notas de voz. O mais natural para uso empresarial diário.

**No INTELECTO v2**: ➕ a acrescentar — peça 1 · Canal (`intelecto/canais/` + subcomando novo em `cli.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoClaw, NanoBot (https://github.com/HKUDS/nanobot), PicoClaw, ZeroClaw, TinyClaw, ClaudeClaw (https://github.com/earlyaidopters/claudeclaw-os), Hermes (https://github.com/NousResearch/hermes-agent)

---

### 2. E-mail (IMAP/SMTP) (`Email Integration`)

**O que faz**: A IA lê seu e-mail e pode responder. Filtra spam, resume newsletters, rascunha respostas.

**No INTELECTO v2**: ➕ a acrescentar — peça 1 · Canal (`intelecto/canais/` + subcomando novo em `cli.py`)

**Quem já implementa (para estudar)**: NanoBot (https://github.com/HKUDS/nanobot), ZeroClaw

---

## Memória e Conhecimento

Onde encaixa no v2: peça 5 · Memória (`intelecto/memoria/store.py` + ferramentas de memória)

### 1. Base de Conhecimento em Documentos (`Document Knowledge Base`)

**O que faz**: Faça upload de PDFs, planilhas, documentos. A IA pode pesquisar e analisá-los. O conhecimento da sua empresa ao alcance da mão.

**No INTELECTO v2**: ➕ a acrescentar — peça 5 · Memória (`intelecto/memoria/store.py` + ferramentas de memória)

**Quem já implementa (para estudar)**: Agent Zero, OpenClaw (https://github.com/openclaw/openclaw)

---

### 2. Busca Híbrida Vetorial + por Palavras-Chave (`Hybrid Vector+Keyword Search`)

**O que faz**: Combina "entender o que você quer dizer" (semântica) com "encontrar palavras exatas" (palavras-chave). O melhor dos dois mundos para recuperação.

**No INTELECTO v2**: ➕ a acrescentar — peça 5 · Memória (`intelecto/memoria/store.py` + ferramentas de memória)

**Quem já implementa (para estudar)**: IronClaw, ZeroClaw, Agent Zero

---

## Segurança e Proteção

Onde encaixa no v2: peças 7 e 8 · Trava, cofre e caixa (`intelecto/seguranca/`)

### 1. Defesa contra Injeção de Prompt (`Prompt Injection Defense`)

**O que faz**: Detecta e bloqueia tentativas de enganar sua IA com instruções ocultas em páginas web ou mensagens. Detecção de padrões em múltiplas camadas.

**No INTELECTO v2**: 🟡 parcial — regra no AGENTS.md (texto de terceiros é informação, não ordem) + trava e aprovação; não há filtro de entrada

**Quem já implementa (para estudar)**: IronClaw, Hermes (https://github.com/NousResearch/hermes-agent), ClaudeClaw (https://github.com/earlyaidopters/claudeclaw-os)

---

### 2. Detecção de Vazamento de Segredos (`Secret Leak Detection`)

**O que faz**: Verifica as saídas das ferramentas antes de chegarem à IA para garantir que suas chaves de API e senhas não sejam expostas acidentalmente.

**No INTELECTO v2**: ➕ a acrescentar — peças 7 e 8 · Trava, cofre e caixa (`intelecto/seguranca/`)

**Quem já implementa (para estudar)**: IronClaw

---

## Skills Integradas e Ferramentas Prontas

Onde encaixa no v2: peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

### 1. Mensagens Proativas ao Usuário (`Proactive User Messaging`)

**O que faz**: A IA envia mensagens para você sem esperar pelo seu prompt. Alertas, lembretes, atualizações de status enviados ao seu chat.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: TinyClaw, Agent Zero

---

## Automação e Agendamento

Onde encaixa no v2: peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

### 1. Gatilhos via Webhook (`Webhook Triggers`)

**O que faz**: Serviços externos (Zapier, n8n, Shopify) podem acionar sua IA via URL. Conecta-se a qualquer ecossistema de automação.

**No INTELECTO v2**: ➕ a acrescentar — peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), ZeroClaw, IronClaw

---

## Integrações e Protocolos

Onde encaixa no v2: peça 4 · Cérebro (`intelecto/provedores/`) ou peça 6 · Ferramentas (`intelecto/ferramentas/`)

### 1. OpenRouter — 100+ Modelos, 1 Chave (`OpenRouter 100+ Models`)

**O que faz**: Acesse Claude, GPT-4, Gemini, Mistral, DeepSeek, Llama e mais de 100 modelos com uma única chave de API. Troque de modelo sem mudar o código. Ideal como provider principal com Ollama como fallback local.

**No INTELECTO v2**: ✅ já existe — `intelecto/provedores/openrouter.py` (testado contra servidor falso; não ao vivo). Só ajuste se precisar.

**Quem já implementa (para estudar)**: OpenRouter, INTELECTO, NanoBot (https://github.com/HKUDS/nanobot), Hermes (https://github.com/NousResearch/hermes-agent), ClaudeClaw (https://github.com/earlyaidopters/claudeclaw-os)

---

### 2. Failover Multi-Provedor de IA (`Multi-Provider Failover`)

**O que faz**: Se o Claude cair, alterne automaticamente para o GPT. Se o GPT estiver lento, tente o Gemini ou OpenRouter. Com OpenRouter você tem 100+ modelos como fallback automático em uma única chave. Nunca perca o serviço.

**No INTELECTO v2**: ➕ a acrescentar — peça 4 · Cérebro (`intelecto/provedores/`) ou peça 6 · Ferramentas (`intelecto/ferramentas/`)

**Quem já implementa (para estudar)**: IronClaw, OpenClaw (https://github.com/openclaw/openclaw), ZeroClaw, OpenRouter, Hermes (https://github.com/NousResearch/hermes-agent)

---

## Padrões de Arquitetura

Onde encaixa no v2: peça 2 · Loop (`intelecto/agente/loop.py`) e a montagem (`intelecto/montagem.py`)

### 1. Trace de Requisição (6 hops) (`Request Trace (6 hops)`)

**O que faz**: HERMES_TRACE=1 expõe o caminho end-to-end (webhook -> gateway -> memory FTS5 -> LLM -> tool exec -> resposta+write) com latências P50/P95/P99.

**No INTELECTO v2**: 🟡 parcial — `auditoria.jsonl` registra comandos, ferramentas, memórias diretas e erros

**Quem já implementa (para estudar)**: Hermes (https://github.com/NousResearch/hermes-agent)

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
