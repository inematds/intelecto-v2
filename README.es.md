# INTELECTO v2

[![INTELECTO v2 — Tu Jarvis seguro](guia/assets/banner-es.jpg)](https://inematds.github.io/intelecto-v2/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 Español**

**Tu propio Jarvis, que te recuerda y no toca lo que no debe.**

## Qué es

Quieres un asistente de IA solo para ti, que recuerde tus cosas, pero no quieres entregarle tus datos ni dejar una IA suelta en tu computadora. INTELECTO v2 es un asistente personal gratuito que instalas en tu computadora y con el que conversas por la terminal o por Telegram. Piensa con una IA que funciona en tu máquina (Ollama, sin costo) o en la nube (OpenRouter), guarda recuerdos, trabaja solo dentro de una carpeta de trabajo y te pide aprobación antes de cualquier comando que no sea solo de lectura. Necesitas Python 3.10 o una versión más reciente; nada más es obligatorio.

Python puro: **ningún paquete que instalar**, 1.500 líneas que puedes leer en una tarde. Con `executor = caixa`, cada comando se ejecuta en un contenedor descartable sin internet.

## 🎓 Curso gratis

**Tu Jarvis seguro: INTELECTO v2 y caixa-do-agente** (9 clases, PT/EN/ES): **https://inematds.github.io/intelecto-v2-curso/es/**

## 📖 Guía de uso

Guía completa (landing + paso a paso): **https://inematds.github.io/intelecto-v2/guia/es/**

## En 1 minuto

```bash
cd ~ && git clone https://github.com/inematds/intelecto-v2 && cd intelecto-v2
python3 -m intelecto demo          # demostración completa, sin internet y sin modelo
python3 -m intelecto configurar    # elige nombre, personalidad, cerebro y dónde ejecutar comandos
python3 -m intelecto               # conversa en la terminal
```

## Las 8 piezas

| # | Pieza | Archivo | Qué hace |
|---|---|---|---|
| 1 | Canal | `canais/telegram.py`, `cli.py` | Terminal o Telegram. En Telegram solo responde a tus IDs. |
| 2 | Bucle con freno | `agente/loop.py` | Piensa → usa una herramienta → responde. Máximo 5 rondas. |
| 3 | Identidad | `identidade/*.md` | SOUL, AGENTS, USER y MEMORY: 4 archivos de texto que editas. |
| 4 | Cerebro | `provedores/` | Ollama (local), OpenRouter (nube) o mock (pruebas). |
| 5 | Memoria | `memoria/store.py` | SQLite + búsqueda FTS5, sin duplicados, encuentra aunque no uses tildes. |
| 6 | Herramientas | `ferramentas/basicas.py` | Memoria, leer/guardar/listar archivos (solo en la carpeta de trabajo), ejecutar comandos. |
| 7 | Bloqueo, aprobación y bóveda | `seguranca/` | Los comandos de solo lectura se ejecutan; el resto pide aprobación; los destructivos se rechazan. Secretos cifrados. Todo queda registrado en la auditoría. |
| 8 | Caja | `seguranca/executor.py` | Ejecuta comandos en un contenedor Docker sin red y solo con acceso a la carpeta de trabajo. |

## Arma el tuyo: el almacén y 5 ejemplos listos

INTELECTO v2 es la base que ya funciona. Para ir más allá, el **almacén** (https://inematds.github.io/intelecto-v2/guia/mercearia/es/)
tiene 144 ingredientes de 12 proyectos de agentes. Tú eliges, ella genera **`meu-assistente.md`**, y Claude Code o
Codex construye sobre INTELECTO. Cada elemento está marcado: ✅ ya existe en v2 (con el archivo), 🟡 parcial, ➕ por agregar
(con la pieza donde encaja), y el archivo termina con las reglas para el agente (un elemento a la vez, con prueba).

| Ejemplo listo | Diagrama | Archivo |
|---|---|---|
| Jarvis personal en Telegram | [ver](exemplos/01-jarvis-telegram.jpg) | [exemplos/01-jarvis-telegram.md](exemplos/01-jarvis-telegram.md) |
| Asistente del pequeño negocio | [ver](exemplos/02-atendente-negocio.jpg) | [exemplos/02-atendente-negocio.md](exemplos/02-atendente-negocio.md) |
| Programador seguro | [ver](exemplos/03-programador-seguro.jpg) | [exemplos/03-programador-seguro.md](exemplos/03-programador-seguro.md) |
| 100 % local y privado | [ver](exemplos/04-local-privado.jpg) | [exemplos/04-local-privado.md](exemplos/04-local-privado.md) |
| Casa inteligente con voz | [ver](exemplos/05-casa-voz.jpg) | [exemplos/05-casa-voz.md](exemplos/05-casa-voz.md) |

```bash
cd ~/intelecto-v2 && cp exemplos/01-jarvis-telegram.md meu-assistente.md
# en Claude Code o en Codex, abierto en esta carpeta:
# "Lee meu-assistente.md e implementa los elementos por agregar y los parciales, uno a la vez, siguiendo las Reglas para el agente."
```

## Recursos avanzados (v2.1)

Seis piezas adicionales en `intelecto/avancado/`, probadas y sin dependencias: **agentes en .md**, **web y memoria nunca en el
mismo agente**, **cita verificada en código** (las frases inventadas no se incluyen; `[n]` sin fuente se convierte en `[?]`), **tarea larga**
que retoma desde el último paso y entrega lo que tiene cuando se acaba el tiempo, **rutinas** con demora por tipo y horario de silencio,
**escalera de cerebros** con descanso por tipo de error y **deshacer**. Vea todo en funcionamiento: `python3 -m intelecto avancado`.
Todavía no están conectadas a la conversación ni a Telegram; el paso a paso para conectarlas está en
[docs/RECURSOS-AVANCADOS.md](docs/RECURSOS-AVANCADOS.md).

## Medir: ¿está acertando? (v2.2)

Cambias de modelo o modificas la identidad y no sabes si el asistente mejoró o empeoró. `avaliar` responde con
un número: ejecuta 8 tareas fijas (guardar y recordar, leer y guardar un archivo, comando de lectura, los dos bloqueos y una cuenta),
cada una en una carpeta limpia, y dice cuántas acertó, cuánto tiempo tardó, cuántas rondas usó y cuántos tokens gastó.

```bash
python3 -m intelecto avaliar                                   # o cérebro do seu config
python3 -m intelecto avaliar --provedor ollama --modelo llama3.2  # outro cérebro, mesmo teste
python3 -m intelecto avaliar --comparar                        # todas as medições lado a lado
```

Cada medición queda guardada en `~/.intelecto2/avaliacoes/`. Durante la medición nadie aprueba nada: solo se ejecutan comandos de lectura.
Para medir lo que te importa, escribe tus tareas en un JSON (`--tarefas minhas.json`); el formato está al
inicio de `intelecto/avaliacao.py`. El cerebro falso (`--provedor mock`) acierta 7 de 8: no sabe hacer cuentas,
y la medición lo muestra.

Medido aquí el 14/11/2026, en la misma máquina y con las mismas 8 tareas:

| Cérebro | Acerto | Tempo por tarefa | Observação |
|---|---|---|---|
| `mock` | 7 de 8 | 0,1 s | errou só a conta (de propósito) |
| `ollama/llama3.2` (3B) | 7 de 8 | 1,1 s | leu o `notas.txt` mas respondeu que não achou a hora |
| `ollama/qwen3.6:35b-a3b` | 6 de 8 e 5 de 8 | 7,7–8,1 s | as falhas foram do cérebro caindo (erro de CUDA com a GPU dividida), marcadas como "caiu" e não como resposta errada |

Moraleja: el número solo sirve con la máquina libre, y el modelo pequeño rindió bien en tareas cortas. Mide el tuyo antes de elegir.

## El proceso, de principio a fin

| # | Paso | Comando | Quién |
|---|---|---|---|
| 1 | Descargar | `cd ~ && git clone https://github.com/inematds/intelecto-v2 && cd intelecto-v2` | tú |
| 2 | Ver cómo funciona sin instalar nada | `python3 -m intelecto demo` | ⚙️ script |
| 3 | Instalar el cerebro local | [ollama.com](https://ollama.com) → `ollama pull qwen3.6:35b-a3b` (o un modelo más pequeño; consulta la guía) | tú |
| 4 | Configurar | `python3 -m intelecto configurar` | tú |
| 5 | Darle tu estilo | editar `~/.intelecto2/identidade/SOUL.md`, `USER.md`, `MEMORY.md` | tú |
| 6 | Verificar | `python3 -m intelecto verificar` → `tudo certo` | ⚙️ script |
| 7 | Conversar | `python3 -m intelecto` | tú |
| 8 | Telegram (opcional) | @BotFather → `python3 -m intelecto cofre guardar telegram` → `/id` en el bot → tu ID en `configurar` → `python3 -m intelecto telegram` | tú |
| 9 | Iniciarlo automáticamente (opcional) | `servico/intelecto-telegram.service` (Linux) o `servico/club.inema.intelecto.plist` (macOS) | ⚙️ servicio |
| 10 | Ejecutar comandos en la caja (opcional) | `configurar` → ejecutor `caixa` (necesitas Docker) | tú |
| 11 | Comprobar que todo está bien | `python3 -m pytest -q` → `113 passed` | ⚙️ pruebas |
| 12 | Proteger el proyecto con caixa-do-agente | ver [Cómo caixa-do-agente mejora tu proyecto](#cómo-caixa-do-agente-mejora-tu-proyecto) | tú |
| 13 | Ver los recursos avanzados | `python3 -m intelecto avancado` | ⚙️ script |
| 13b | Medir el asistente (y comparar cerebros) | `python3 -m intelecto avaliar` → `--comparar` | ⚙️ script |

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

Todo lo del asistente queda en `~/.intelecto2/` (cámbialo con `INTELECTO_HOME`): `config.json`, `memoria.db`,
`identidade/`, `area/` (la única carpeta que las herramientas pueden ver), `auditoria.jsonl` y la bóveda (`.cofre`).

## Qué se probó y dónde

| Elemento | Cómo se probó (12/11/2026) |
|---|---|
| Bucle, memoria, herramientas, bloqueo, aprobación, bóveda, auditoría | 68 pruebas automáticas (`python3 -m pytest -q`) |
| Ollama local | en vivo con `qwen3.6:35b-a3b`: guardó «mi nombre es Nei y vivo en Porto Alegre» y lo recordó en una ejecución posterior. `llama3.2` (3B) casi no usa las herramientas por sí solo; desde la v2.0.1, "lembre que …" (recuerda que…) lo guarda directamente el asistente, y llama3.2 también recordó (13/11/2026). |
| Ejecutor en caja | en vivo, Docker 28: solo ve la carpeta de trabajo, no ve las variables de tu terminal y no tiene internet |
| OpenRouter y Telegram | contra servidores falsos locales (formato de las solicitudes, clave en el encabezado, filtro de propietario, aprobación mediante /sim). **No se probaron en vivo**: dependen de tu clave y de tu bot. |
| macOS | no probado (el servicio launchd y el ID de la máquina obtenido mediante `ioreg` están en el código) |

## Cómo caixa-do-agente mejora tu proyecto

INTELECTO protege **lo que hace el asistente** (bloqueo, aprobación, caja por comando). La
[caixa-do-agente](https://inematds.github.io/caixa-do-agente/guia/) protege **el proyecto mientras tú u otro agente
trabajan en él** (Claude Code, Codex): ejecuta todo en una copia sin contraseñas y sin internet, y tú solo aplicas lo que apruebas.

```bash
# 1. imagen con pytest (la caja no tiene internet para instalar nada)
docker build -t intelecto-v2-testes caixa/
# 2. las pruebas de INTELECTO en una copia sin .env, sin red, que se borra al terminar
~/caixa-do-agente/caixa.sh ~/intelecto-v2 --imagem intelecto-v2-testes -- python3 -m pytest -q -p no:cacheprovider
# 3. nota de la protección para quien programa en el proyecto (solo lectura)
python3 ~/caixa-do-agente/auditar.py ~/intelecto-v2
```

Resultado real en esta máquina: `.env` quedó fuera de la copia, `67 passed, 1 skipped` (se omite la prueba que necesita Docker dentro de la caja) y `0 arquivo(s) mudaram`. Las cifras del auditor están en la guía.

## Versiones

- **v2.2**: medición (`python3 -m intelecto avaliar`): aciertos, tiempo, rondas y tokens por cerebro, con `--comparar`.
- **v2.1**: recursos avanzados en `intelecto/avancado/` ([docs/RECURSOS-AVANCADOS.md](docs/RECURSOS-AVANCADOS.md), en portugués).
- **v2 (este repo)**: código completo y probado, sin dependencias, Linux y macOS, caja por comando.
- **v1**: [inematds/intelecto](https://github.com/inematds/intelecto) (la tienda de frameworks y el plan) y el curso
  [intelecto-curso](https://inematds.github.io/intelecto-curso/) siguen disponibles. Qué cambió: [docs/v1-para-v2.md](docs/v1-para-v2.md) (en portugués).

Licencia MIT · [inema.club](https://inema.club)