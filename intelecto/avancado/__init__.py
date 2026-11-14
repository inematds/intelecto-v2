"""Recursos avançados do INTELECTO v2 (v2.1): peças prontas e testadas, Python puro.

  perfis     agentes em .md + separação web × memória + agente de fundo sem ferramenta que age
  citacoes   confere em código se a frase citada está na página; citação órfã vira [?]
  tarefas    tarefa longa com passo salvo, retomada, orçamento e "escreve o que tem"
  rotinas    lembretes e rotinas com janela de atraso por tipo e horário de silêncio
  escada     vários cérebros em fila, com descanso por tipo de erro (429, 503, 404)
  desfazer   desfaz a última ação reversível (gravar, mover, apagar arquivo)

Estado: biblioteca + testes + demonstração (`python3 -m intelecto avancado`).
Ainda NÃO estão ligadas ao loop de conversa nem ao Telegram: cada uma se liga quando você quiser,
uma por vez, com teste (ver docs/RECURSOS-AVANCADOS.md).
"""
