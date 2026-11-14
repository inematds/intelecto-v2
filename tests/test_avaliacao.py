"""Medição: tarefas fixas, pasta limpa por tarefa, conferências e comparação (tudo com o cérebro de mentira)."""
import asyncio
import json
import os

from intelecto import avaliacao as av
from intelecto import config as cfg
from intelecto.cli import main
from intelecto.provedores.base import ErroProvedor, Provedor, Resposta
from intelecto.provedores.mock import Mock


def _config():
    return cfg.Config(provedor="mock", modelo="mock")


def test_mock_acerta_tudo_menos_a_conta(home):
    rel = asyncio.run(av.avaliar(_config(), Mock()))
    certos = {r["id"]: r["acertou"] for r in rel["tarefas"]}
    assert certos.pop("raciocinio") is False          # o mock não faz conta
    assert all(certos.values()), rel["tarefas"]
    assert rel["resumo"]["acertos"] == len(av.TAREFAS) - 1


def test_cada_tarefa_roda_numa_pasta_limpa_e_volta_a_home(home):
    antes = os.environ["INTELECTO_HOME"]
    asyncio.run(av.avaliar(_config(), Mock()))
    assert os.environ["INTELECTO_HOME"] == antes
    assert not os.path.exists(os.path.join(antes, "memoria.db"))   # nada foi gravado na sua pasta


class Mentiroso(Provedor):
    """Responde sem chamar ferramenta nenhuma e diz que fez."""
    nome = "mentiroso"

    async def conversar(self, mensagens, ferramentas=None):
        return Resposta("Pronto, já fiz tudo.", uso={"entrada": 10, "saida": 5})


def test_quem_so_diz_que_fez_erra_e_tokens_sao_contados(home):
    rel = asyncio.run(av.avaliar(_config(), Mentiroso()))
    por_id = {r["id"]: r for r in rel["tarefas"]}
    assert por_id["memoria-guardar"]["acertou"]        # "lembre que" é guardado pelo loop, sem o cérebro
    assert not por_id["arquivo-ler"]["acertou"]
    assert not por_id["arquivo-escrever"]["acertou"]
    assert not por_id["comando-leitura"]["acertou"]
    assert por_id["trava-destrutivo"]["acertou"]       # não rodou nada perigoso
    assert rel["resumo"]["tokens"] == 15 * sum(len(t["passos"]) for t in av.TAREFAS)   # 1 chamada por passo


class Perigoso(Provedor):
    """Sempre tenta apagar tudo."""
    nome = "perigoso"

    async def conversar(self, mensagens, ferramentas=None):
        if mensagens[-1].papel == "tool" or not ferramentas:
            return Resposta("ok")
        return Resposta("", [{"id": "x", "nome": "rodar_comando", "args": {"comando": "rm -rf /"}}])


def test_trava_segura_mesmo_com_cerebro_perigoso(home):
    t = [x for x in av.TAREFAS if x["id"] == "trava-destrutivo"]
    rel = asyncio.run(av.avaliar(_config(), Perigoso(), t))
    assert rel["tarefas"][0]["acertou"]
    assert rel["tarefas"][0]["ferramentas"] == ["rodar_comando"]


class Fora(Provedor):
    nome = "fora"

    async def conversar(self, mensagens, ferramentas=None):
        raise ErroProvedor("sem resposta")


def test_cerebro_fora_do_ar_vira_erro_e_nao_quebra(home):
    rel = asyncio.run(av.avaliar(_config(), Fora(), av.TAREFAS[:2]))
    assert rel["resumo"]["acertos"] == 0
    assert all(r["problemas"] for r in rel["tarefas"])
    assert rel["resumo"]["caiu"] == 2                  # separado de "errou"
    assert "caiu" in av.texto_resumo(rel)


class Lento(Provedor):
    nome = "lento"

    async def conversar(self, mensagens, ferramentas=None):
        await asyncio.sleep(5)
        return Resposta("tarde")


def test_tempo_maximo(home):
    rel = asyncio.run(av.avaliar(_config(), Lento(), av.TAREFAS[:1], tempo_max=1))
    assert "passou de 1 s" in rel["tarefas"][0]["problemas"][0]


def test_tarefas_proprias_e_arquivo_invalido(tmp_path, home):
    arq = tmp_path / "minhas.json"
    arq.write_text(json.dumps([{"id": "eco", "passos": ["olá"], "resposta_contem": ["olá"]}]), encoding="utf-8")
    rel = asyncio.run(av.avaliar(_config(), Mock(), av.ler_tarefas(str(arq))))
    assert rel["tarefas"][0]["acertou"]          # o mock responde "Você disse: olá"
    ruim = tmp_path / "ruim.json"
    ruim.write_text('{"id": 1}', encoding="utf-8")
    try:
        av.ler_tarefas(str(ruim))
        assert False, "devia recusar"
    except ValueError:
        pass


def test_cli_grava_e_compara(home, capsys):
    assert main(["avaliar", "--provedor", "mock", "--modelo", "mock"]) == 1   # 1 = nem tudo acertou
    gravados = os.listdir(os.path.join(str(home), "avaliacoes"))
    assert len(gravados) == 1
    capsys.readouterr()
    assert main(["avaliar", "--comparar"]) == 0
    saida = capsys.readouterr().out
    assert "mock/mock" in saida and "88%" in saida
