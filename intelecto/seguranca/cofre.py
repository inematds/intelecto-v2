"""Cofre de segredos (token do Telegram, chave do OpenRouter) cifrado em disco.

- Com o pacote `cryptography` instalado: Fernet (AES-128-CBC + HMAC-SHA256).
- Sem ele: cifra da biblioteca padrão (PBKDF2 + fluxo HMAC-SHA256 + etiqueta HMAC).
  Protege contra leitura casual e cópia do arquivo para outra máquina; NÃO é auditada
  como o Fernet. `intelecto verificar` mostra qual está em uso.
A chave sai do id da máquina (/etc/machine-id ou IOPlatformUUID no macOS) + um sal local:
o arquivo copiado para outro computador não abre.
"""
import base64
import hashlib
import hmac
import json
import os
import subprocess

try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
    MOTOR = "fernet"
except ImportError:  # pragma: no cover - depende da máquina
    Fernet = None
    InvalidToken = ValueError
    MOTOR = "stdlib"

_ITER = 200_000


def id_da_maquina() -> str:
    for p in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
        try:
            with open(p) as f:
                v = f.read().strip()
                if v:
                    return v
        except OSError:
            pass
    try:  # macOS
        out = subprocess.run(["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], capture_output=True, text=True, timeout=5).stdout
        for linha in out.splitlines():
            if "IOPlatformUUID" in linha:
                return linha.split('"')[-2]
    except (OSError, subprocess.SubprocessError):
        pass
    return "sem-id-de-maquina"


class Cofre:
    def __init__(self, pasta: str, motor: str | None = None, maquina: str | None = None):
        self.arquivo = os.path.join(pasta, ".cofre")
        self.arquivo_sal = os.path.join(pasta, ".cofre.sal")
        self.motor = motor or MOTOR
        if self.motor == "fernet" and Fernet is None:
            self.motor = "stdlib"
        self.maquina = maquina or id_da_maquina()
        os.makedirs(pasta, mode=0o700, exist_ok=True)

    def _sal(self) -> bytes:
        if not os.path.exists(self.arquivo_sal):
            with open(self.arquivo_sal, "wb") as f:
                f.write(os.urandom(16))
            os.chmod(self.arquivo_sal, 0o600)
        with open(self.arquivo_sal, "rb") as f:
            return f.read()

    def _chave(self) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", self.maquina.encode(), self._sal(), _ITER)

    # --- cifra ---
    def _cifrar(self, texto: str) -> str:
        chave = self._chave()
        if self.motor == "fernet":
            return Fernet(base64.urlsafe_b64encode(chave)).encrypt(texto.encode()).decode()
        nonce = os.urandom(16)
        dados = texto.encode()
        fluxo = b""
        i = 0
        while len(fluxo) < len(dados):
            fluxo += hmac.new(chave, nonce + i.to_bytes(4, "big"), hashlib.sha256).digest()
            i += 1
        cifrado = bytes(a ^ b for a, b in zip(dados, fluxo))
        etiqueta = hmac.new(chave, nonce + cifrado, hashlib.sha256).digest()
        return "s1:" + base64.urlsafe_b64encode(nonce + etiqueta + cifrado).decode()

    def _decifrar(self, token: str) -> str:
        chave = self._chave()
        if not token.startswith("s1:"):
            if Fernet is None:
                raise ValueError("segredo gravado com Fernet; instale o pacote cryptography")
            try:
                return Fernet(base64.urlsafe_b64encode(chave)).decrypt(token.encode()).decode()
            except InvalidToken as e:
                raise ValueError("segredo não abre nesta máquina (ou foi alterado)") from e
        bruto = base64.urlsafe_b64decode(token[3:])
        nonce, etiqueta, cifrado = bruto[:16], bruto[16:48], bruto[48:]
        if not hmac.compare_digest(etiqueta, hmac.new(chave, nonce + cifrado, hashlib.sha256).digest()):
            raise ValueError("segredo não abre nesta máquina (ou foi alterado)")
        fluxo = b""
        i = 0
        while len(fluxo) < len(cifrado):
            fluxo += hmac.new(chave, nonce + i.to_bytes(4, "big"), hashlib.sha256).digest()
            i += 1
        return bytes(a ^ b for a, b in zip(cifrado, fluxo)).decode()

    # --- API ---
    def _todos(self) -> dict:
        if not os.path.exists(self.arquivo):
            return {}
        with open(self.arquivo, encoding="utf-8") as f:
            return json.load(f)

    def _gravar(self, d: dict) -> None:
        tmp = self.arquivo + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f)
        os.chmod(tmp, 0o600)
        os.replace(tmp, self.arquivo)

    def guardar(self, nome: str, valor: str) -> None:
        d = self._todos()
        d[nome] = self._cifrar(valor)
        self._gravar(d)

    def ler(self, nome: str) -> str | None:
        token = self._todos().get(nome)
        return None if token is None else self._decifrar(token)

    def listar(self) -> list:
        return sorted(self._todos())

    def apagar(self, nome: str) -> bool:
        d = self._todos()
        if nome not in d:
            return False
        del d[nome]
        self._gravar(d)
        return True
