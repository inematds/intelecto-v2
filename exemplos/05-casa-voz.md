# Meu assistente — lista de ingredientes (base: INTELECTO v2)

> Para o Claude Code ou o Codex: construa **em cima** do repositório https://github.com/inematds/intelecto-v2 (clonado em `~/intelecto-v2`).
> Ele já roda (terminal e Telegram, Ollama/OpenRouter, memória, trava, aprovação, cofre e caixa) e tem testes automáticos.
> Leia `README.md` e `CLAUDE.md` do repositório antes de começar.

## Como usar este arquivo

1. `cd ~/intelecto-v2` e copie este arquivo para lá.
2. Abra o agente na pasta e peça: "Leia meu-assistente.md e implemente os ingredientes marcados como a acrescentar e parcial, um de cada vez, seguindo as Regras para o agente."
3. Mais seguro: rode o agente dentro da caixa-do-agente (https://inematds.github.io/caixa-do-agente/guia/) e aplique só o patch revisado.

**Total: 12 ingredientes** · ✅ já existem no v2: 2 · 🟡 parciais: 0 · ➕ a acrescentar: 10

---

## Canais de Comunicação

Onde encaixa no v2: peça 1 · Canal (`intelecto/canais/` + subcomando novo em `cli.py`)

### 1. Palavra de Ativação por Voz (`Voice Wake Word`)

**O que faz**: Diga "hey claude" e sua IA escuta. Controle de voz sempre ativo como um alto-falante inteligente, mas privado.

**No INTELECTO v2**: ➕ a acrescentar — peça 1 · Canal (`intelecto/canais/` + subcomando novo em `cli.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

## Skills Integradas e Ferramentas Prontas

Onde encaixa no v2: peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

### 1. Whisper Speech-to-Text (`Whisper Speech-to-Text`)

**O que faz**: Converta gravações de voz em texto. Funciona localmente (sem chave de API) ou via OpenAI Whisper API.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoClaw

---

### 2. Texto para Fala (ElevenLabs + Local) (`ElevenLabs Text-to-Speech`)

**O que faz**: Converta texto em fala natural. Na nuvem via ElevenLabs ou offline via sherpa-onnx. Sua IA fala de volta.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

### 3. Controle de Luzes Philips Hue (`Philips Hue Lights`)

**O que faz**: Controle suas luzes e cenas Philips Hue via comandos de IA. "Diminua a sala de estar para 30%."

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

### 4. Controle de Caixas Sonos (`Sonos Speaker Control`)

**O que faz**: Controle caixas Sonos: reprodução, volume, agrupamento e descoberta.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

### 5. Capturas de Câmeras de Segurança (`Security Camera Snapshots`)

**O que faz**: Capture frames e clipes de vídeo de câmeras RTSP/ONVIF. A IA monitora seus feeds de segurança.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

### 6. Controle do Player Spotify (`Spotify Player Control`)

**O que faz**: Controle a reprodução do Spotify e pesquise músicas pelo seu assistente de IA.

**No INTELECTO v2**: ➕ a acrescentar — peça 6 · Ferramentas (`intelecto/ferramentas/`, registrada em `padrao()` de `ferramentas/basicas.py`)

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw)

---

## Automação e Agendamento

Onde encaixa no v2: peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

### 1. Agendamento Cron (`Cron Scheduling`)

**O que faz**: Execute tarefas em um cronograma: "toda segunda-feira às 9h, me envie um briefing." Funciona como um despertador confiável para sua IA.

**No INTELECTO v2**: ➕ a acrescentar — peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), NanoClaw, NanoBot (https://github.com/HKUDS/nanobot), PicoClaw, ZeroClaw, TinyClaw, IronClaw

---

### 2. Heartbeat (Verificações Periódicas) (`Heartbeat System`)

**O que faz**: A IA acorda a cada 30 minutos para verificar se algo precisa de atenção. Proativa, não apenas reativa.

**No INTELECTO v2**: ➕ a acrescentar — peça nova de agenda (`intelecto/agenda/`), ligada ao loop e com subcomando em `cli.py`

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), PicoClaw, NanoBot (https://github.com/HKUDS/nanobot), IronClaw, ZeroClaw, Hermes (https://github.com/NousResearch/hermes-agent)

---

## Integrações e Protocolos

Onde encaixa no v2: peça 4 · Cérebro (`intelecto/provedores/`) ou peça 6 · Ferramentas (`intelecto/ferramentas/`)

### 1. Controle de Hardware / IoT (`Hardware IoT Control`)

**O que faz**: Controle dispositivos físicos: luzes, sensores, motores. A IA pode interagir com o mundo real através de pinos GPIO.

**No INTELECTO v2**: ➕ a acrescentar — peça 4 · Cérebro (`intelecto/provedores/`) ou peça 6 · Ferramentas (`intelecto/ferramentas/`)

**Quem já implementa (para estudar)**: PicoClaw

---

### 2. Suporte a LLM Local (Ollama) (`Local LLM Support`)

**O que faz**: Execute modelos de IA no seu próprio computador. Zero custo de API. Privacidade total. Sem necessidade de internet. Use junto com OpenRouter: nuvem quando precisa de potência, local quando precisa de privacidade.

**No INTELECTO v2**: ✅ já existe — `intelecto/provedores/ollama.py` (testado ao vivo com qwen3.6 e llama3.2). Só ajuste se precisar.

**Quem já implementa (para estudar)**: OpenClaw (https://github.com/openclaw/openclaw), ZeroClaw, PicoClaw, Agent Zero, NanoBot (https://github.com/HKUDS/nanobot), INTELECTO, Hermes (https://github.com/NousResearch/hermes-agent), AIOS (https://github.com/agiresearch/AIOS)

---

## Segurança e Proteção

Onde encaixa no v2: peças 7 e 8 · Trava, cofre e caixa (`intelecto/seguranca/`)

### 1. Gates de Aprovação de Execução (`Execution Approval Gates`)

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
