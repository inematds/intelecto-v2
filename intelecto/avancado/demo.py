"""python3 -m intelecto avancado — mostra os 6 recursos avançados funcionando, sem rede e sem modelo."""
import asyncio
import os
import shutil
import tempfile
from datetime import datetime, timedelta

from ..provedores.base import ErroProvedor, Provedor, Resposta
from . import citacoes, perfis
from .desfazer import Desfazer
from .escada import Escada
from .rotinas import Rotinas
from .tarefas import Tarefas

AGENTES = os.path.join(os.path.dirname(__file__), "agentes")


class _Falha(Provedor):
    def __init__(self, nome, erro):
        self.nome, self.erro, self.chamadas = nome, erro, 0

    async def conversar(self, mensagens, ferramentas=None):
        self.chamadas += 1
        raise ErroProvedor(self.erro)


class _Ok(Provedor):
    nome = "local"

    async def conversar(self, mensagens, ferramentas=None):
        return Resposta(texto="ok")


def _titulo(n, t):
    print(f"\n{n}. {t}\n" + "-" * (len(t) + 3))


def rodar() -> int:
    pasta = tempfile.mkdtemp(prefix="intelecto-avancado-")
    try:
        _titulo(1, "Agentes em .md + web × memória")
        for p in perfis.carregar(AGENTES).values():
            nomes, fora = perfis.permitidas(p.ferramentas)
            print(f"  {p.nome}: recebe {', '.join(nomes)}")
            for n, motivo in fora:
                print(f"     fora: {n} — {motivo}")

        _titulo(2, "Citação conferida em código")
        pagina = "O Brasil registrou 1.200 mm de chuva em março, segundo o instituto."
        achados = [{"afirmacao": "choveu 1.200 mm", "fonte": 1, "frase": "registrou 1.200 mm de chuva em março"},
                   {"afirmacao": "choveu 3.000 mm", "fonte": 1, "frase": "registrou 3.000 mm de chuva"},
                   {"afirmacao": "dado sem página", "fonte": 2, "frase": "qualquer coisa"}]
        aceitos, recusados = citacoes.conferir(achados, {1: pagina})
        for a in aceitos + recusados:
            print(f"  {a['apoio']:10} {a['afirmacao']}")
        print("  texto: " + citacoes.corrigir_marcas("Choveu muito [1], mais que em 2020 [4].", {1}))

        _titulo(3, "Tarefa longa: cai no meio e retoma do último passo")
        relogio = [1000.0]
        tarefas = Tarefas(os.path.join(pasta, "tarefas"), relogio=lambda: relogio[0])
        tid = tarefas.criar("comparar 3 impressoras 3D", minutos=10, rodadas=4)

        def passo_que_cai(t):
            relogio[0] += 30
            if t["rodadas_feitas"] == 2:
                raise KeyboardInterrupt("simulação: o computador desligou")
            return {"nota": f"achado {t['rodadas_feitas'] + 1}"}

        def escrever(t):
            return "# Relatório\n" + "\n".join(f"- {n}" for n in t["passos"])
        try:
            asyncio.run(tarefas.rodar(tid, passo_que_cai, escrever))
        except KeyboardInterrupt as e:
            print(f"  {e} (passos salvos: {tarefas.pegar(tid)['rodadas_feitas']})")
        t = asyncio.run(tarefas.rodar(tid, lambda t: {"nota": f"achado {t['rodadas_feitas'] + 1}"}, escrever))
        print(f"  reabriu: status={t['status']} aberturas={t['aberturas']} passos={t['rodadas_feitas']}")
        print("  " + t["relatorio"].replace("\n", "\n  "))

        _titulo(4, "Rotinas: atraso por tipo e horário de silêncio")
        r = Rotinas(os.path.join(pasta, "rotinas.json"))
        base = datetime(2026, 11, 14, 6, 0)
        r.definir_silencio("23:00-07:00")
        r.adicionar("bom dia", "instrucao", {"tipo": "uma_vez", "em": "2026-11-14T08:00"}, "resumo do dia", base)
        r.adicionar("remédio", "lembrete", {"tipo": "uma_vez", "em": "2026-11-14T09:00"}, "tomar o remédio", base)
        r.adicionar("check-in", "instrucao", {"tipo": "intervalo", "minutos": 60}, "puxa conversa", base,
                    silenciavel=True)
        for ev in r.checar(datetime(2026, 11, 14, 10, 30)):
            print(f"  10:30 {ev['rotina']['nome']:9} {ev['acao']:9} {ev['motivo']}")
        r2 = Rotinas(os.path.join(pasta, "rotinas2.json"))
        r2.definir_silencio("23:00-07:00")
        r2.adicionar("check-in", "instrucao", {"tipo": "intervalo", "minutos": 60}, "puxa conversa",
                     datetime(2026, 11, 14, 22, 30), silenciavel=True)
        for ev in r2.checar(datetime(2026, 11, 14, 23, 30)):
            print(f"  23:30 {ev['rotina']['nome']:9} {ev['acao']:9} {ev['motivo']}")

        _titulo(5, "Escada de cérebros com descanso")
        tempo = [0.0]
        fora = _Falha("nuvem", "HTTP 503 em https://exemplo: indisponível")
        escada = Escada([fora, _Ok()], relogio=lambda: tempo[0])
        for _ in range(3):
            asyncio.run(escada.conversar([]))
        print(f"  3 perguntas: o cérebro fora do ar foi tentado {fora.chamadas} vez(es); descansando: {escada.descansando()}")

        _titulo(6, "Desfazer")
        d = Desfazer(os.path.join(pasta, "lixeira"))
        arq = os.path.join(pasta, "notas.txt")
        print("  " + d.gravar(arq, "versão 1"))
        print("  " + d.gravar(arq, "versão 2"))
        print("  " + d.desfazer() + f" → conteúdo: {open(arq, encoding='utf-8').read()!r}")
        print("  " + d.apagar(arq))
        print("  " + d.desfazer() + f" → existe de novo: {os.path.exists(arq)}")
        print("\nTudo acima rodou nesta máquina, sem rede e sem modelo.")
        return 0
    finally:
        shutil.rmtree(pasta, ignore_errors=True)
