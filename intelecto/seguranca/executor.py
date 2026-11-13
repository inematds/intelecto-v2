"""Onde o comando roda depois de aprovado.

  local — subprocesso na pasta de trabalho (rápido; a trava e a aprovação são a proteção)
  caixa — container Docker descartável, SEM rede, só com a pasta de trabalho montada,
          teto de memória/CPU/processos e tempo. As senhas (cofre, .env, ~/.ssh) não
          existem lá dentro. É a mesma ideia do kit caixa-do-agente, por comando.
"""
import asyncio
import os
import shutil
import uuid

MAX_SAIDA = 10 * 1024


async def _rodar(argv: list, cwd: str, tempo: int, ao_estourar=None) -> tuple:
    proc = await asyncio.create_subprocess_exec(
        *argv, cwd=cwd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
        stdin=asyncio.subprocess.DEVNULL,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=tempo)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        if ao_estourar:
            await ao_estourar()
        return 124, f"(parou: passou de {tempo} s)"
    texto = out.decode("utf-8", "replace")
    if len(texto) > MAX_SAIDA:
        texto = texto[:MAX_SAIDA] + f"\n(saída cortada em {MAX_SAIDA // 1024} KB)"
    return proc.returncode, texto


class ExecutorLocal:
    nome = "local"

    def __init__(self, area: str, tempo: int = 60):
        self.area = area
        self.tempo = tempo

    async def rodar(self, comando: str) -> tuple:
        os.makedirs(self.area, exist_ok=True)
        return await _rodar(["/bin/sh", "-c", comando], self.area, self.tempo)


class ExecutorCaixa:
    nome = "caixa"

    def __init__(self, area: str, tempo: int = 60, imagem: str = "python:3.12-slim",
                 memoria: str = "512m", cpus: str = "1", docker: str = "docker"):
        self.area = area
        self.tempo = tempo
        self.imagem = imagem
        self.memoria = memoria
        self.cpus = cpus
        self.docker = docker

    @staticmethod
    def disponivel(docker: str = "docker") -> bool:
        return shutil.which(docker) is not None

    def argv(self, comando: str, nome: str) -> list:
        return [
            self.docker, "run", "--rm", "--name", nome,
            "--network", "none",                  # sem internet
            "--memory", self.memoria, "--cpus", self.cpus, "--pids-limit", "128",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
            "--user", f"{os.getuid()}:{os.getgid()}",
            "-e", "HOME=/tmp",                    # nenhuma variável do seu terminal entra
            "-v", f"{self.area}:/trabalho", "-w", "/trabalho",
            self.imagem, "sh", "-c", comando,
        ]

    async def rodar(self, comando: str) -> tuple:
        os.makedirs(self.area, exist_ok=True)
        nome = "intelecto-caixa-" + uuid.uuid4().hex[:8]

        async def matar():
            p = await asyncio.create_subprocess_exec(self.docker, "rm", "-f", nome,
                                                     stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
            await p.wait()
        return await _rodar(self.argv(comando, nome), self.area, self.tempo + 15, ao_estourar=matar)


def criar(config) -> object:
    if config.executor == "caixa":
        return ExecutorCaixa(config.area, config.tempo_comando, config.imagem_caixa)
    return ExecutorLocal(config.area, config.tempo_comando)
