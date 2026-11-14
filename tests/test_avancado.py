"""Recursos avançados (v2.1): cada regra tem teste. Nada aqui usa rede nem modelo."""
import asyncio
import os
from datetime import datetime

import pytest

from intelecto.avancado import citacoes, perfis
from intelecto.avancado.desfazer import LIMITE, Desfazer
from intelecto.avancado.escada import DESCANSO, Escada, tipo_erro
from intelecto.avancado.rotinas import Rotinas, dentro, proxima
from intelecto.avancado.tarefas import MAX_ABERTURAS, PAUSA_SEM_COTA, Tarefas
from intelecto.provedores.base import ErroProvedor, Provedor, Resposta

AGENTES = os.path.join(os.path.dirname(__file__), "..", "intelecto", "avancado", "agentes")


# ---------------- perfis ----------------
def test_web_tira_memoria():
    nomes, fora = perfis.permitidas(["buscar_web", "buscar_memoria", "salvar_memoria", "anotar"])
    assert "buscar_memoria" not in nomes and "salvar_memoria" not in nomes
    assert "buscar_web" in nomes and "anotar" in nomes
    assert {n for n, _ in fora} == {"buscar_memoria", "salvar_memoria"}


def test_sem_web_mantem_memoria():
    nomes, _ = perfis.permitidas(["buscar_memoria", "ler_arquivo"])
    assert nomes == ["buscar_memoria", "ler_arquivo"]


def test_fundo_nao_recebe_ferramenta_que_age():
    nomes, fora = perfis.permitidas(["rodar_comando", "escrever_arquivo", "enviar_mensagem", "anotar"])
    assert nomes == ["anotar"]
    assert len(fora) == 3
    nomes, _ = perfis.permitidas(["rodar_comando"], fundo=False)
    assert nomes == ["rodar_comando"]


def test_desconhecida_sai():
    nomes, fora = perfis.permitidas(["apagar_tudo"])
    assert nomes == [] and fora[0][1] == "ferramenta desconhecida"


def test_perfil_md_e_agentes_de_exemplo():
    p = perfis.ler_perfil("---\nnome: x\nferramentas: anotar, ler_arquivo\nminutos: 999\n---\nfaça", "x.md")
    assert p.nome == "x" and p.ferramentas == ["anotar", "ler_arquivo"] and p.minutos == 240
    assert p.instrucao == "faça"
    todos = perfis.carregar(AGENTES)
    assert {"geral", "pesquisador"} <= set(todos)
    nomes, _ = perfis.permitidas(todos["pesquisador"].ferramentas)
    assert "buscar_memoria" not in nomes


def test_perfil_quebrado_nao_derruba_os_outros(tmp_path):
    (tmp_path / "bom.md").write_text("---\nnome: bom\n---\nok")
    (tmp_path / "ruim.md").write_text("---\nnome: ruim\nsem fechamento")
    avisos = []
    assert list(perfis.carregar(str(tmp_path), log=avisos.append)) == ["bom"]
    assert avisos


# ---------------- citações ----------------
PAGINA = "Segundo o instituto, o Brasil registrou 1.200 mm de chuva em março de 2026, recorde da série."


def test_citacao_exata_ignora_caixa_e_pontuacao():
    assert citacoes.apoio("REGISTROU 1.200 mm de chuva, em março", PAGINA) == citacoes.EXATA


def test_citacao_inventada_e_ausente():
    assert citacoes.apoio("registrou 3.000 mm de chuva", PAGINA) == citacoes.AUSENTE


def test_citacao_longa_emendada_e_parcial():
    frase = ("o Brasil registrou 1.200 mm de chuva em março de 2026 recorde da série "
             "e o governo decretou emergência em vários estados")
    assert citacoes.apoio(frase, PAGINA) == citacoes.PARCIAL      # a maior parte está na página
    inventada = "o Brasil registrou 1.200 mm de chuva e o governo decretou emergência em vários estados do sul ontem"
    assert citacoes.apoio(inventada, PAGINA) == citacoes.AUSENTE   # metade inventada não passa
    pagina = PAGINA + " Depois disso o governo decretou emergência em vários estados do sul."
    assert citacoes.apoio(frase.replace(" e o governo", " o governo"), pagina) == citacoes.PARCIAL


def test_marca_orfa_vira_interrogacao():
    assert citacoes.corrigir_marcas("a [1] b [2, 9] c [9]", {1, 2}) == "a [1] b [2, ?] c [?]"


def test_achado_sem_pagina_aberta_e_recusado():
    ok, nao = citacoes.conferir([{"afirmacao": "x", "fonte": 7, "frase": "y"}], {1: PAGINA})
    assert ok == [] and nao[0]["apoio"] == "sem página"


# ---------------- tarefas ----------------
def _escrever(t):
    return "\n".join(t["passos"])


def test_tarefa_cai_e_retoma_do_ultimo_passo(tmp_path):
    rel = [0.0]
    tf = Tarefas(str(tmp_path), relogio=lambda: rel[0])
    tid = tf.criar("x", rodadas=4)

    def cai(t):
        if t["rodadas_feitas"] == 2:
            raise RuntimeError("desligou")
        return {"nota": f"p{t['rodadas_feitas']}"}
    with pytest.raises(RuntimeError):
        asyncio.run(tf.rodar(tid, cai, _escrever))
    assert tf.pegar(tid)["rodadas_feitas"] == 2
    t = asyncio.run(tf.rodar(tid, lambda t: {"nota": f"p{t['rodadas_feitas']}"}, _escrever))
    assert t["status"] == "concluida" and t["passos"] == ["p0", "p1", "p2", "p3"]
    assert (tmp_path / f"{tid}.md").read_text() == "p0\np1\np2\np3"


def test_tarefa_interrompida_3_vezes_falha(tmp_path):
    tf = Tarefas(str(tmp_path))
    tid = tf.criar("x")

    def sempre_cai(t):
        raise RuntimeError("caiu")
    for _ in range(MAX_ABERTURAS):
        with pytest.raises(RuntimeError):
            asyncio.run(tf.rodar(tid, sempre_cai, _escrever))
    t = asyncio.run(tf.rodar(tid, sempre_cai, _escrever))
    assert t["status"] == "falhou"


def test_orcamento_de_tempo_acaba_e_escreve_o_que_tem(tmp_path):
    rel = [0.0]
    tf = Tarefas(str(tmp_path), relogio=lambda: rel[0])
    tid = tf.criar("x", minutos=1, rodadas=999)

    def passo(t):
        rel[0] += 25
        return {"nota": "achado"}
    t = asyncio.run(tf.rodar(tid, passo, _escrever))
    assert t["status"] == "concluida" and t["rodadas_feitas"] == 3 and t["relatorio"]


def test_sem_cota_pausa_e_volta_depois(tmp_path):
    rel = [0.0]
    tf = Tarefas(str(tmp_path), relogio=lambda: rel[0])
    tid = tf.criar("x", rodadas=2)
    t = asyncio.run(tf.rodar(tid, lambda t: {"sem_cota": True}, _escrever))
    assert t["status"] == "pausada" and tid not in tf.prontas()
    rel[0] += PAUSA_SEM_COTA + 1
    assert tid in tf.prontas()
    t = asyncio.run(tf.rodar(tid, lambda t: {"nota": "ok"}, _escrever))
    assert t["status"] == "concluida"


def test_encerrar_recado_e_cancelar(tmp_path):
    tf = Tarefas(str(tmp_path))
    tid = tf.criar("x", rodadas=10)
    vistos = []

    def passo(t):
        vistos.append(list(t["recados_lidos"]))
        if t["rodadas_feitas"] == 0:
            tf.recado(tid, "em euro também")
        if t["rodadas_feitas"] == 2:
            tf.encerrar(tid)
        return {"nota": "n"}
    t = asyncio.run(tf.rodar(tid, passo, _escrever))
    assert t["status"] == "concluida" and t["rodadas_feitas"] == 3
    assert vistos[1] == ["em euro também"]
    tid2 = tf.criar("y")
    tf.cancelar(tid2)
    assert asyncio.run(tf.rodar(tid2, passo, _escrever))["status"] == "cancelada"


def test_tarefa_agendada_espera(tmp_path):
    rel = [100.0]
    tf = Tarefas(str(tmp_path), relogio=lambda: rel[0])
    tid = tf.criar("x", comecar_em=200.0)
    assert tid not in tf.prontas()
    rel[0] = 201.0
    assert tid in tf.prontas()


# ---------------- rotinas ----------------
D = datetime(2026, 11, 14, 6, 0)      # sábado


def test_lembrete_atrasado_ainda_toca_ate_2h(tmp_path):
    r = Rotinas(str(tmp_path / "r.json"))
    r.adicionar("remédio", "lembrete", {"tipo": "uma_vez", "em": "2026-11-14T09:00"}, "t", D)
    ev = r.checar(datetime(2026, 11, 14, 10, 30))
    assert ev[0]["acao"] == "rodar"
    assert r.listar()[0]["ativa"] is False


def test_instrucao_com_3h_de_atraso_e_pulada_e_registrada(tmp_path):
    r = Rotinas(str(tmp_path / "r.json"))
    r.adicionar("bom dia", "instrucao", {"tipo": "uma_vez", "em": "2026-11-14T08:00"}, "t", D)
    ev = r.checar(datetime(2026, 11, 14, 11, 0))
    assert ev[0]["acao"] == "pulada" and r.historico()[-1]["acao"] == "pulada"


def test_silencio_segura_so_o_silenciavel(tmp_path):
    r = Rotinas(str(tmp_path / "r.json"))
    r.definir_silencio("23:00-07:00")
    r.adicionar("check-in", "instrucao", {"tipo": "intervalo", "minutos": 30}, "t",
                datetime(2026, 11, 14, 23, 0), silenciavel=True)
    r.adicionar("acordar", "lembrete", {"tipo": "uma_vez", "em": "2026-11-15T06:30"}, "t", D)
    assert r.checar(datetime(2026, 11, 14, 23, 30))[0]["acao"] == "segurada"
    ev = {e["rotina"]["nome"]: e["acao"] for e in r.checar(datetime(2026, 11, 15, 6, 30))}
    assert ev["acordar"] == "rodar"


def test_rotinas_persistem(tmp_path):
    arq = str(tmp_path / "r.json")
    Rotinas(arq).adicionar("x", "lembrete", {"tipo": "semanal", "dias": [4], "hora": "17:00"}, "t", D)
    assert Rotinas(arq).listar()[0]["proxima"] == "2026-11-20T17:00"     # próxima sexta


def test_proxima_e_janela():
    assert dentro("23:00-07:00", datetime(2026, 1, 1, 2, 0))
    assert not dentro("23:00-07:00", datetime(2026, 1, 1, 12, 0))
    q = {"tipo": "intervalo", "minutos": 60, "entre": "08:00-18:00"}
    assert proxima(q, datetime(2026, 11, 14, 18, 30)) == datetime(2026, 11, 15, 8, 0)
    with pytest.raises(ValueError):
        proxima({"tipo": "nada"}, D)


def test_data_no_passado_recusada(tmp_path):
    with pytest.raises(ValueError):
        Rotinas(str(tmp_path / "r.json")).adicionar("x", "lembrete", {"tipo": "uma_vez", "em": "2020-01-01T00:00"},
                                                    "t", D)


# ---------------- escada ----------------
class _Falha(Provedor):
    def __init__(self, erro):
        self.nome, self.erro, self.n = "f", erro, 0

    async def conversar(self, m, f=None):
        self.n += 1
        raise ErroProvedor(self.erro)


class _Ok(Provedor):
    nome = "ok"

    async def conversar(self, m, f=None):
        return Resposta(texto="ok")


@pytest.mark.parametrize("msg,tipo", [("HTTP 429 em x: quota", "cota"), ("HTTP 503 em x", "fora"),
                                      ("sem resposta de x: timed out", "fora"), ("HTTP 404 em x", "inexistente"),
                                      ("HTTP 500 em x", "outro")])
def test_tipo_de_erro(msg, tipo):
    assert tipo_erro(msg) == tipo


def test_degrau_fora_do_ar_e_pago_uma_vez_so():
    t = [0.0]
    fora = _Falha("HTTP 503 em x")
    e = Escada([fora, _Ok()], relogio=lambda: t[0])
    for _ in range(5):
        assert asyncio.run(e.conversar([])).texto == "ok"
    assert fora.n == 1
    t[0] += DESCANSO["fora"] + 1
    asyncio.run(e.conversar([]))
    assert fora.n == 2


def test_todos_descansando_tenta_o_que_acorda_primeiro():
    t = [0.0]
    a, b = _Falha("HTTP 404 em x"), _Falha("HTTP 429 em x")
    e = Escada([a, b], relogio=lambda: t[0])
    with pytest.raises(ErroProvedor):
        asyncio.run(e.conversar([]))
    with pytest.raises(ErroProvedor):
        asyncio.run(e.conversar([]))
    assert (a.n, b.n) == (1, 2)       # b (cota, 5 min) acorda antes de a (404, 6 h)


# ---------------- desfazer ----------------
def test_desfaz_gravar_criar_mover_apagar(tmp_path):
    d = Desfazer(str(tmp_path / "lixo"))
    f = str(tmp_path / "a.txt")
    d.gravar(f, "1")
    d.gravar(f, "2")
    d.desfazer()
    assert open(f).read() == "1"
    g = str(tmp_path / "b.txt")
    d.mover(f, g)
    d.desfazer()
    assert os.path.exists(f) and not os.path.exists(g)
    d.apagar(f)
    assert not os.path.exists(f)
    d.desfazer()
    assert open(f).read() == "1"
    d.desfazer()                         # desfaz o "criar"
    assert not os.path.exists(f)
    assert d.desfazer() == "não há nada para desfazer"


def test_nao_apaga_criado_que_mudou(tmp_path):
    d = Desfazer(str(tmp_path / "lixo"))
    f = tmp_path / "a.txt"
    d.gravar(str(f), "meu")
    f.write_text("mexido por você")
    assert "não consegui" in d.desfazer() and f.exists()


def test_arquivo_grande_nao_registra_desfazer(tmp_path):
    d = Desfazer(str(tmp_path / "lixo"))
    f = tmp_path / "grande.txt"
    f.write_text("x" * (LIMITE + 1))
    assert "sem desfazer" in d.gravar(str(f), "novo") and not d.pode()


def test_mover_nunca_por_cima(tmp_path):
    d = Desfazer(str(tmp_path / "lixo"))
    (tmp_path / "a").write_text("a")
    (tmp_path / "b").write_text("b")
    with pytest.raises(FileExistsError):
        d.mover(str(tmp_path / "a"), str(tmp_path / "b"))


def test_demo_roda(capsys):
    from intelecto.avancado.demo import rodar
    assert rodar() == 0
    saida = capsys.readouterr().out
    assert "quem acessa a web não acessa a sua memória" in saida and "[?]" in saida
