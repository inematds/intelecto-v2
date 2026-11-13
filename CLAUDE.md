# CLAUDE.md — intelecto-v2

Assistente pessoal de IA em Python puro (stdlib). Repo público `inematds/intelecto-v2`, autor dos commits `inematds <inematds@gmail.com>`.
A v1 (`~/projetos/intelecto`, `~/projetos/intelecto-curso`) NÃO se mexe.

- Rodar: `python3 -m intelecto demo` (sem rede) · `python3 -m intelecto` (terminal) · `python3 -m intelecto telegram`.
- Testes: `python3 -m pytest -q` → todos passam antes de qualquer commit. Teste novo para toda regra de trava.
- Sem dependências obrigatórias: nada de `pip install` no código principal (só `cryptography` opcional no cofre).
- Testes NUNCA chamam API de verdade: OpenRouter e Telegram só contra o `ServidorFalso` do `tests/conftest.py`.
- Estado do usuário fica em `INTELECTO_HOME` (padrão `~/.intelecto2`), nunca dentro do repo.
- Trava (`seguranca/trava.py`): o padrão é APROVAR; só a lista de leitura passa direto. Bloqueio novo = padrão + caso em `BLOQUEADOS` do teste.
- Guia em `guia/` (PT) + `guia/en/` + `guia/es/`; README em 3 idiomas. Mudou o PT, retraduza os dois (`inema-traduz`), `<pre>` byte a byte iguais.
- Processo do início ao fim: tabela no README. Mudou o fluxo, atualize a tabela no mesmo commit.

## Self-learning

Quando eu for corrigido ou perceber um erro: antes de seguir, acrescente a lição como regra de uma linha no TOPO de `## Lessons`.

## Lessons
- `llama3.2` (3B) conversa mas quase não chama ferramentas; o padrão testado é `qwen3.6:35b-a3b`. Teste ao vivo com a GPU livre (`fila-vaga gpu`): com outra carga deu CUDA illegal memory access. (12/11/2026)
- A caixa-do-agente não tem internet: dependência de teste vai numa imagem (`caixa/Dockerfile`), nunca `pip install` dentro dela. (12/11/2026)
