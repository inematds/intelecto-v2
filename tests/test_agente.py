import asyncio

from intelecto import config as cfg
from intelecto.memoria.store import Memorias
from intelecto.montagem import montar
from intelecto.provedores.base import Provedor, Resposta


def _pecas(home, **k):
    c = cfg.Config(provedor="mock", modelo="mock", **k)
    return montar(c)


def test_memoria_salva_busca_sem_duplicar(tmp_path):
    m = Memorias(str(tmp_path / "m.db"))
    a = m.salvar("Meu nome é Ana")
    assert m.salvar("  meu   NOME é ana ") == a
    m.salvar("Gosto de café sem açúcar")
    assert [x.conteudo for x in m.buscar("qual é o meu nome?")] == ["Meu nome é Ana"]
    assert m.buscar("acucar")[0].conteudo.startswith("Gosto")      # sem acento também acha
    assert m.buscar("???") == []
    assert m.esquecer(a) and m.total() == 1


def test_memoria_semeia_uma_vez(tmp_path):
    md = tmp_path / "MEMORY.md"
    md.write_text("# x\n- fato um\n- fato dois\n- Nome: (preencha)\n")
    m = Memorias(str(tmp_path / "m.db"))
    assert m.semear(str(md)) == 2
    assert m.semear(str(md)) == 0


def test_memoria_persiste_entre_execucoes(home):
    p = _pecas(home)
    asyncio.run(p.agente.responder("t", "lembre que meu cachorro se chama Thor"))
    p2 = _pecas(home)   # nova "execução", mesmo banco
    r = asyncio.run(p2.agente.responder("t", "qual o nome do meu cachorro?"))
    assert "Thor" in r


def test_loop_ferramentas_e_auditoria(home):
    p = _pecas(home)
    r = asyncio.run(p.agente.responder("t", "rode: ls"))
    assert "[local, saída 0]" in r
    r = asyncio.run(p.agente.responder("t", "rode: rm -rf ~"))
    assert "bloqueado" in r
    tipos = [x["tipo"] for x in p.auditoria.ultimas()]
    assert tipos.count("comando") == 2 and tipos.count("ferramenta") == 2


def test_ler_arquivo_nao_sai_da_area(home):
    p = _pecas(home)
    assert "fora da pasta de trabalho" in asyncio.run(p.agente.responder("t", "leia ../config.json"))
    (home / "area" / "nota.txt").write_text("olá")
    assert "olá" in asyncio.run(p.agente.responder("t", "leia nota.txt"))


class Teimoso(Provedor):
    """Cérebro que pede ferramenta para sempre: o freio tem de parar."""
    nome = "teimoso"

    def __init__(self):
        self.n = 0

    async def conversar(self, msgs, ferramentas=None):
        self.n += 1
        if ferramentas is None:
            return Resposta("parei")
        return Resposta("", [{"id": str(self.n), "nome": "listar_arquivos", "args": {}}])


def test_freio_de_rodadas(home):
    p = _pecas(home, max_rodadas=3)
    p.agente.provedor = Teimoso()
    assert asyncio.run(p.agente.responder("t", "oi")) == "parei"
    assert p.agente.provedor.n == 4      # 3 rodadas + 1 resposta final sem ferramentas


def test_identidade_entra_no_contexto(home):
    p = _pecas(home, nome="Sexta-feira", personalidade="Fala como pirata.")
    sistema = p.agente.contexto.montar([], "oi")[0].texto
    assert "Sexta-feira" in sistema and "Fala como pirata." in sistema and "{nome}" not in sistema


def test_historico_limitado(home):
    p = _pecas(home)
    for i in range(15):
        asyncio.run(p.agente.responder("t", f"mensagem {i}"))
    assert len(p.agente.historico["t"]) == 20


def test_config_valida_e_salva(home):
    c = cfg.Config(provedor="nada")
    assert c.validar()
    c = cfg.Config()
    cfg.salvar(c)
    assert cfg.existe() and cfg.carregar().modelo == c.modelo


class Calado(Provedor):
    """Cérebro que nunca chama ferramenta (como um modelo pequeno): só ecoa o que recebeu de contexto."""
    nome = "calado"

    async def conversar(self, msgs, ferramentas=None):
        return Resposta(" | ".join(m.texto for m in msgs if m.papel == "system")[-300:])


def test_lembre_que_guarda_sem_o_modelo_chamar_ferramenta(home):
    p = _pecas(home)
    p.agente.provedor = Calado()
    asyncio.run(p.agente.responder("t", "Lembre que meu cachorro se chama Thor."))
    assert [m.conteudo for m in p.memorias.buscar("cachorro")] == ["Meu cachorro se chama Thor"]
    resposta = asyncio.run(p.agente.responder("t", "qual o nome do meu cachorro?"))
    assert "Thor" in resposta          # a memória chega no contexto da pergunta seguinte
    antes = p.memorias.total()
    asyncio.run(p.agente.responder("t", "lembra quando fomos à praia?"))   # pergunta: não guarda
    assert p.memorias.total() == antes
    assert p.agente.lembrete_direto("guarde: a reunião é às 15h")[1] == "a reunião é às 15h"
    assert p.agente.lembrete_direto("como você lembra das coisas?") is None


def test_mock_entende_en_e_es(home):
    p = _pecas(home)
    assert "[local, saída 0]" in asyncio.run(p.agente.responder("t", "run: ls"))
    assert "[local, saída 0]" in asyncio.run(p.agente.responder("t", "ejecuta: pwd"))
    asyncio.run(p.agente.responder("t", "remember that my dog is Rex"))
    assert "Rex" in asyncio.run(p.agente.responder("t", "what is my dog?"))
    asyncio.run(p.agente.responder("t", "recuerda que mi gato es Tom"))
    assert "Tom" in asyncio.run(p.agente.responder("t", "¿cómo se llama mi gato?"))
