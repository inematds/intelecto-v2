import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def roda(args, home, entrada=None):
    env = {**os.environ, "INTELECTO_HOME": str(home), "PYTHONPATH": RAIZ}
    return subprocess.run([sys.executable, "-m", "intelecto", *args], input=entrada, capture_output=True,
                          text=True, env=env, cwd=RAIZ, timeout=60)


def test_demo_completa(tmp_path):
    r = roda(["demo"], tmp_path)
    assert r.returncode == 0, r.stderr
    for trecho in ("meu nome é Ana", "bloqueado", "fora da pasta de trabalho", "livre     rodou=True  ls"):
        assert trecho in r.stdout


def test_configurar_e_conversar_mock(tmp_path):
    assert roda(["configurar", "--nao-interativo", "--provedor", "mock", "--nome", "Teste"], tmp_path).returncode == 0
    assert (tmp_path / "identidade" / "SOUL.md").exists()
    r = roda(["conversar"], tmp_path, "lembre que meu time é o Grêmio\nqual meu time?\nrode: echo x > y.txt\n")
    assert "Grêmio" in r.stdout and "não é um terminal → recusado" in r.stdout
    assert "Grêmio" in roda(["memoria", "time"], tmp_path).stdout
    assert '"tipo": "comando"' in roda(["auditoria"], tmp_path).stdout


def test_cofre_pela_cli(tmp_path):
    env_ok = roda(["cofre", "listar"], tmp_path)
    assert "(cofre vazio)" in env_ok.stdout
    r = subprocess.run([sys.executable, "-m", "intelecto", "cofre", "guardar", "telegram"], capture_output=True, text=True,
                       env={**os.environ, "INTELECTO_HOME": str(tmp_path), "PYTHONPATH": RAIZ, "INTELECTO_SEGREDO": "123:abc"},
                       cwd=RAIZ, timeout=60)
    assert r.returncode == 0 and "123:abc" not in r.stdout
    assert roda(["cofre", "listar"], tmp_path).stdout.strip() == "telegram"


def test_verificar_aponta_o_que_falta(tmp_path):
    r = roda(["verificar"], tmp_path)
    assert "[OK] Python" in r.stdout and "sem config" in r.stdout and r.returncode == 1
