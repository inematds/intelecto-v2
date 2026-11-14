"""Desfazer: "desfaz" volta a última ação reversível.

A regra é sobre ser reversível, não sobre parecer perigoso: o que dá para voltar é feito na hora e
entra na pilha; só o irreversível pede aprovação (isso continua no seguranca/aprovacao.py).

  gravar  — guarda o conteúdo de antes (arquivo > 1 MB: grava, mas avisa que não dá para desfazer)
  criar   — desfazer apaga o arquivo criado, só se ninguém mexeu nele depois
  mover   — desfazer move de volta (nunca por cima de algo que apareceu no lugar)
  apagar  — o arquivo vai para a lixeira do assistente; desfazer traz de volta

Não chuta: se não sabe como era antes, não registra desfazer.
"""
import hashlib
import os
import shutil
import time

LIMITE = 1_000_000


def _hash(caminho: str) -> str:
    with open(caminho, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class Desfazer:
    def __init__(self, lixeira: str, maximo: int = 20):
        self.lixeira = lixeira
        self.maximo = maximo
        self._pilha = []

    def registrar(self, rotulo: str, volta) -> None:
        self._pilha.append((rotulo, volta))
        del self._pilha[:-self.maximo]

    def pode(self) -> bool:
        return bool(self._pilha)

    def historico(self) -> list:
        return [r for r, _ in reversed(self._pilha)]

    def desfazer(self) -> str:
        if not self._pilha:
            return "não há nada para desfazer"
        rotulo, volta = self._pilha.pop()
        try:
            volta()
            return f"desfeito: {rotulo}"
        except Exception as e:      # noqa: BLE001 — o motivo vai para quem pediu
            return f"não consegui desfazer ({rotulo}): {e}"

    # ---------- ações com desfazer ----------
    def gravar(self, caminho: str, texto: str) -> str:
        if os.path.exists(caminho):
            if os.path.getsize(caminho) > LIMITE:
                with open(caminho, "w", encoding="utf-8") as f:
                    f.write(texto)
                return f"gravado {caminho} (sem desfazer: o arquivo de antes passava de 1 MB)"
            with open(caminho, encoding="utf-8", errors="surrogateescape") as f:
                antes = f.read()

            def volta():
                with open(caminho, "w", encoding="utf-8", errors="surrogateescape") as f:
                    f.write(antes)
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(texto)
            self.registrar(f"gravar {caminho}", volta)
            return f"gravado {caminho}"
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)
        marca = _hash(caminho)

        def apaga_criado():
            if os.path.exists(caminho) and _hash(caminho) != marca:
                raise RuntimeError("o arquivo mudou depois de criado; não apago")
            if os.path.exists(caminho):
                os.remove(caminho)
        self.registrar(f"criar {caminho}", apaga_criado)
        return f"criado {caminho}"

    def mover(self, origem: str, destino: str) -> str:
        if os.path.exists(destino):
            raise FileExistsError(f"já existe {destino}; não movo por cima")
        shutil.move(origem, destino)

        def volta():
            if os.path.exists(origem):
                raise RuntimeError(f"já existe algo em {origem}")
            shutil.move(destino, origem)
        self.registrar(f"mover {origem} → {destino}", volta)
        return f"movido para {destino}"

    def apagar(self, caminho: str) -> str:
        os.makedirs(self.lixeira, exist_ok=True)
        guardado = os.path.join(self.lixeira, f"{time.time_ns()}-{os.path.basename(caminho)}")
        shutil.move(caminho, guardado)

        def volta():
            if os.path.exists(caminho):
                raise RuntimeError(f"já existe algo em {caminho}")
            shutil.move(guardado, caminho)
        self.registrar(f"apagar {caminho}", volta)
        return f"apagado {caminho} (está na lixeira; diga 'desfaz' para voltar)"
