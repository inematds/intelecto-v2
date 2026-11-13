import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def home(tmp_path, monkeypatch):
    """Cada teste ganha uma pasta do assistente só dele."""
    monkeypatch.setenv("INTELECTO_HOME", str(tmp_path / "home"))
    return tmp_path / "home"


class ServidorFalso:
    """Servidor HTTP local que responde JSON pronto e guarda o que recebeu (nada sai da máquina)."""

    def __init__(self, responder):
        self.pedidos = []
        dono = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                corpo = json.loads(self.rfile.read(n) or b"{}")
                dono.pedidos.append({"caminho": self.path, "corpo": corpo, "cabecalhos": dict(self.headers)})
                status, resposta = responder(self.path, corpo)
                dados = json.dumps(resposta).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(dados)))
                self.end_headers()
                self.wfile.write(dados)

            def log_message(self, *a):
                pass

        self.srv = HTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.srv.server_address[1]}"
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def fechar(self):
        self.srv.shutdown()


@pytest.fixture
def servidor():
    criados = []

    def fabrica(responder):
        s = ServidorFalso(responder)
        criados.append(s)
        return s
    yield fabrica
    for s in criados:
        s.fechar()
