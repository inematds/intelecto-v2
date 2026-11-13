"""Registro de auditoria: uma linha JSON por evento (comando, ferramenta, erro)."""
import datetime
import json
import os


class Auditoria:
    def __init__(self, caminho: str):
        self.caminho = caminho

    def registrar(self, tipo: str, **dados) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.caminho)), exist_ok=True)
        linha = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "tipo": tipo, **dados}
        with open(self.caminho, "a", encoding="utf-8") as f:
            f.write(json.dumps(linha, ensure_ascii=False) + "\n")

    def ultimas(self, n: int = 20) -> list:
        if not os.path.isfile(self.caminho):
            return []
        with open(self.caminho, encoding="utf-8") as f:
            linhas = f.readlines()[-n:]
        return [json.loads(x) for x in linhas if x.strip()]
