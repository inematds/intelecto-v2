"""Citação conferida em código, não pela opinião de um modelo.

Cada achado de uma pesquisa guarda: a afirmação, a fonte (número) e a FRASE EXATA da página que a
sustenta. Aqui o código confere se essa frase está no texto da página como foi salvo:

  exata    — a frase está lá (ignorando maiúsculas, acentos de digitação e pontuação)
  parcial  — frase longa, emendada ou cortada: a maior parte dos trechos de 6 palavras está lá
  ausente  — não está; o achado não pode entrar no relatório

E no texto final, toda marca [n] que não aponta para uma fonte real vira [?].
"""
import re
import unicodedata

EXATA, PARCIAL, AUSENTE = "exata", "parcial", "ausente"


def normalizar(texto: str) -> str:
    t = unicodedata.normalize("NFKC", str(texto or "")).casefold()
    return " ".join(re.findall(r"\w+", t))


def apoio(frase: str, pagina: str) -> str:
    q, p = normalizar(frase), normalizar(pagina)
    if not q or not p:
        return AUSENTE
    if q in p:
        return EXATA
    palavras = q.split()
    if len(palavras) < 8:
        return AUSENTE
    janelas = [" ".join(palavras[i:i + 6]) for i in range(0, len(palavras) - 5, 3)]
    acertos = sum(1 for j in janelas if j in p) / max(1, len(janelas))
    return PARCIAL if acertos >= 0.6 else AUSENTE


def corrigir_marcas(texto: str, validas) -> str:
    """[3] e [2, 5] ficam só se o número for de uma fonte real; senão viram [?]."""
    validas = {int(v) for v in validas}

    def troca(m):
        nums = [x.strip() for x in m.group(1).split(",")]
        return "[" + ", ".join(x if int(x) in validas else "?" for x in nums) + "]"
    return re.sub(r"\[(\d{1,3}(?:\s*,\s*\d{1,3})*)\]", troca, texto)


def conferir(achados: list, paginas: dict) -> tuple:
    """achados: [{afirmacao, fonte, frase}]; paginas: {fonte: texto salvo}.

    Devolve (aceitos, recusados). Cada um ganha o campo 'apoio'. Achado de página nunca aberta
    é recusado com apoio 'sem página' — abra a página antes de citar."""
    aceitos, recusados = [], []
    for a in achados:
        texto = paginas.get(a.get("fonte"))
        if texto is None:
            recusados.append({**a, "apoio": "sem página"})
            continue
        r = apoio(a.get("frase", ""), texto)
        (aceitos if r != AUSENTE else recusados).append({**a, "apoio": r})
    return aceitos, recusados
