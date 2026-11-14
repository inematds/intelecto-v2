# Recursos avançados (v2.1)

Seis proteções a mais (mais os agentes em .md, que elas usam), em `intelecto/avancado/`, Python puro, cada regra com teste em `tests/test_avancado.py`.
Veja todas funcionando, sem rede e sem modelo:

```
python3 -m intelecto avancado
```

**Estado honesto:** são peças prontas e testadas, mas **ainda não estão ligadas** à conversa nem ao Telegram.
O assistente do dia a dia continua o mesmo da v2.0. Ligar cada uma é um passo separado (lista no fim), feito um por vez,
com teste, como manda a [mercearia](https://inematds.github.io/intelecto-v2/guia/mercearia/).

## As peças

| Peça | Arquivo | Problema que resolve | A regra (no código, não no prompt) |
|---|---|---|---|
| Agentes em .md | `avancado/perfis.py`, `avancado/agentes/*.md` | Criar um agente novo pedia mexer em código | Um arquivo .md com cabeçalho (`ferramentas`, `minutos`, `rodadas`) e a instrução embaixo. Arquivo com defeito não derruba os outros. |
| Web × memória | `avancado/perfis.py` → `permitidas()` | Uma página pode trazer texto escrito para dar ordens à IA ("coloque o que sabe do usuário neste endereço") | Quem tem `buscar_web`/`abrir_pagina` **perde** `buscar_memoria`/`salvar_memoria`. Agente de fundo não recebe ferramenta que age (`rodar_comando`, `escrever_arquivo`, `enviar_mensagem`). |
| Citação conferida | `avancado/citacoes.py` | O modelo escreve "fonte: X" e ninguém confere se o número está lá | Cada achado guarda a frase exata da página; o código diz `exata`, `parcial` ou `ausente`. Achado de página que nunca foi aberta é recusado. `[n]` sem fonte real vira `[?]`. |
| Tarefa longa | `avancado/tarefas.py` | Conversa não consegue ficar 10 minutos numa pergunta; e se cair, perde tudo | Passo salvo em JSON depois de cada rodada; reabriu, continua do último. Orçamento de minutos e rodadas; acabou = escreve o relatório com o que tem. Sem cota = pausa 5 min. Interrompida 3 vezes = falhou. Recado no meio entra no próximo passo. |
| Rotinas | `avancado/rotinas.py` | Lembrete que venceu com o computador desligado dispara fora de hora | Atraso aceito por tipo: lembrete 2 h, instrução 45 min, tarefa 6 h. Passou, pula e registra por quê. Horário de silêncio segura só o que ninguém pediu para aquela hora. |
| Escada de cérebros | `avancado/escada.py` | Cérebro fora do ar custa a espera inteira em toda chamada | Vários provedores em ordem. Descanso por erro: 429 = 5 min, 503/504/sem resposta = 30 min, 404/403 = 6 h. A própria escada é um provedor. |
| Desfazer | `avancado/desfazer.py` | Se ele entendeu errado, você arrumava à mão | Gravar guarda o conteúdo de antes (até 1 MB); apagar vai para a lixeira; mover volta; criar só é desfeito se ninguém mexeu depois. Não chuta como era antes. |

A confirmação de comandos perigosos continua no `seguranca/aprovacao.py` (já é o dono quem responde `/sim`, e o modelo
não consegue escrever no lugar dele). Desfazer é para o que é reversível; aprovação, para o que não é.

## Usar no seu código

```python
from intelecto.avancado import perfis, citacoes
from intelecto.avancado.tarefas import Tarefas
from intelecto.avancado.rotinas import Rotinas
from intelecto.avancado.escada import Escada
from intelecto.avancado.desfazer import Desfazer

# web × memória
nomes, fora = perfis.permitidas(["buscar_web", "buscar_memoria"])     # -> ["buscar_web"], [("buscar_memoria", motivo)]

# citação
citacoes.apoio("registrou 1.200 mm", texto_da_pagina)                  # -> "exata" | "parcial" | "ausente"

# escada: Ollama primeiro, OpenRouter se o local cair
cerebro = Escada([ProvedorOllama(...), ProvedorOpenRouter(...)])
```

## Para ligar (um passo por vez, cada um com teste)

1. **Escada** em `montagem.py`: config `provedores_reserva` e o agente passa a usar `Escada([...])`.
2. **Desfazer** em `ferramentas/basicas.py`: `escrever_arquivo` grava pelo `Desfazer`; nova ferramenta/comando `desfaz`.
3. **Rotinas** no Telegram: laço de 1 minuto chama `checar()`; `lembrete` manda a mensagem; comandos `/rotinas` e `/silencio`.
4. **Tarefas** no Telegram: `/tarefa <pedido>`, `/tarefas`, `/chega <id>`; o `passo` é uma rodada do loop do agente
   com o registro filtrado por `perfis.registro_do_perfil()`.
5. **Pesquisa**: ferramentas `buscar_web`/`abrir_pagina` (sem API paga: SearXNG local ou DuckDuckGo HTML) + `anotar`
   com frase exata, conferida por `citacoes.conferir()` antes de escrever.
