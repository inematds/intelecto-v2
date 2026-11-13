"""Ollama, OpenRouter e Telegram contra servidores falsos locais: o formato dos pedidos e das respostas."""
import asyncio
import shutil
import subprocess

import pytest

from intelecto.canais.telegram import Telegram, dividir
from intelecto.provedores.base import DefFerramenta, ErroProvedor, Mensagem
from intelecto.provedores.ollama import Ollama
from intelecto.provedores.openrouter import OpenRouter
from intelecto.seguranca.executor import ExecutorCaixa, ExecutorLocal

FERR = [DefFerramenta("salvar_memoria", "guarda", {"type": "object", "properties": {}})]


def test_ollama_formato(servidor):
    s = servidor(lambda p, c: (200, {"message": {"content": "", "tool_calls": [
        {"function": {"name": "salvar_memoria", "arguments": {"conteudo": "x"}}}]}, "prompt_eval_count": 5, "eval_count": 2}))
    r = asyncio.run(Ollama("m", s.url).conversar([Mensagem("user", "oi")], FERR))
    assert r.chamadas[0]["nome"] == "salvar_memoria" and r.chamadas[0]["args"] == {"conteudo": "x"}
    pedido = s.pedidos[0]
    assert pedido["caminho"] == "/api/chat" and pedido["corpo"]["stream"] is False
    assert pedido["corpo"]["tools"][0]["function"]["name"] == "salvar_memoria"


def test_openrouter_formato_e_chave(servidor):
    s = servidor(lambda p, c: (200, {"choices": [{"message": {"content": "", "tool_calls": [
        {"id": "a1", "type": "function", "function": {"name": "salvar_memoria", "arguments": "{\"conteudo\": \"y\"}"}}]}}],
        "usage": {"prompt_tokens": 9, "completion_tokens": 1}}))
    msgs = [Mensagem("user", "oi"), Mensagem("assistant", "", chamadas=[{"id": "a0", "nome": "x", "args": {"k": 1}}]),
            Mensagem("tool", "ok", id_chamada="a0", nome="x")]
    r = asyncio.run(OpenRouter("chave-falsa", "m", s.url).conversar(msgs, FERR))
    assert r.chamadas == [{"id": "a1", "nome": "salvar_memoria", "args": {"conteudo": "y"}}] and r.uso["entrada"] == 9
    p = s.pedidos[0]
    assert p["caminho"] == "/chat/completions" and p["cabecalhos"]["Authorization"] == "Bearer chave-falsa"
    assert p["corpo"]["messages"][2] == {"role": "tool", "content": "ok", "tool_call_id": "a0"}
    assert p["corpo"]["messages"][1]["tool_calls"][0]["function"]["arguments"] == '{"k": 1}'


def test_provedor_erro_vira_mensagem(servidor):
    s = servidor(lambda p, c: (500, {"error": "CUDA"}))
    with pytest.raises(ErroProvedor):
        asyncio.run(Ollama("m", s.url).conversar([Mensagem("user", "oi")]))
    with pytest.raises(ErroProvedor):
        OpenRouter("", "m")


def test_telegram_dividir():
    partes = dividir(("a" * 3000 + "\n\n") * 3)
    assert all(len(x) <= 4096 for x in partes) and len(partes) == 3
    assert dividir("x" * 9000) == ["x" * 4096, "x" * 4096, "x" * 808]


def test_telegram_so_dono_e_aprovacao(servidor):
    fila = [[
        {"update_id": 1, "message": {"text": "/id", "chat": {"id": 7}, "from": {"id": 99}}},
        {"update_id": 2, "message": {"text": "oi de estranho", "chat": {"id": 7}, "from": {"id": 99}}},
        {"update_id": 3, "message": {"text": "oi do dono", "chat": {"id": 5}, "from": {"id": 42}}},
    ], [
        {"update_id": 4, "message": {"text": "/sim", "chat": {"id": 5}, "from": {"id": 42}}},
    ]]

    def responder(caminho, corpo):
        if caminho.endswith("/getUpdates"):
            return 200, {"ok": True, "result": fila.pop(0) if fila else []}
        return 200, {"ok": True, "result": {}}
    s = servidor(responder)
    recebidas, aprov = [], []

    async def ao_receber(chat, texto, perguntar):
        recebidas.append(texto)
        aprov.append(await perguntar("echo a > b", "teste"))
        return "resposta"

    async def roda():
        bot = Telegram("TOKEN", donos=[42], url=s.url, espera=0)
        await bot.uma_rodada(ao_receber)
        await asyncio.sleep(0.3)               # a pergunta de aprovação sai
        await bot.uma_rodada(ao_receber)       # chega o /sim
        await asyncio.sleep(0.3)
    asyncio.run(roda())
    assert recebidas == ["oi do dono"] and aprov == [True]
    enviados = [p["corpo"]["text"] for p in s.pedidos if p["caminho"].endswith("/sendMessage")]
    assert enviados[0] == "Seu id é 99. Coloque em telegram_donos no config.json."
    assert any("Posso rodar" in t for t in enviados) and enviados[-1] == "resposta"
    assert all("/botTOKEN/" in p["caminho"] for p in s.pedidos)


def test_executor_local_tempo(tmp_path):
    e = ExecutorLocal(str(tmp_path), tempo=1)
    assert asyncio.run(e.rodar("echo ok")) == (0, "ok\n")
    rc, txt = asyncio.run(e.rodar("sleep 5"))
    assert rc == 124 and "passou de 1 s" in txt


def test_executor_caixa_argv(tmp_path):
    a = ExecutorCaixa(str(tmp_path)).argv("ls", "n1")
    for trecho in (["--network", "none"], ["--cap-drop", "ALL"], ["-e", "HOME=/tmp"], ["-v", f"{tmp_path}:/trabalho"]):
        i = a.index(trecho[0])
        assert a[i:i + 2] == trecho


def _docker_ok():
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "image", "inspect", "python:3.12-slim"], capture_output=True).returncode == 0


@pytest.mark.skipif(not _docker_ok(), reason="sem Docker ou sem a imagem python:3.12-slim")
def test_executor_caixa_de_verdade(tmp_path, monkeypatch):
    monkeypatch.setenv("SEGREDO_DO_TERMINAL", "nao-pode-aparecer")
    (tmp_path / "dentro.txt").write_text("visivel")
    e = ExecutorCaixa(str(tmp_path), tempo=60)
    rc, txt = asyncio.run(e.rodar(
        "cat dentro.txt; echo; env | grep -c SEGREDO_DO_TERMINAL; ls /root ~/.ssh 2>&1 | head -1; "
        "python3 -c \"import urllib.request as u;u.urlopen('https://example.com',timeout=5)\" 2>&1 | tail -1; echo criado > novo.txt"))
    assert "visivel" in txt and "\n0\n" in txt                 # vê a área, não vê a variável
    assert "rror" in txt                                       # sem rede: a chamada falha
    assert (tmp_path / "novo.txt").read_text() == "criado\n"   # escreve só na área
