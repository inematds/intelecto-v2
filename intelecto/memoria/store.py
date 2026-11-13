"""Memória de longo prazo: SQLite com busca de texto FTS5 (ranking BM25), sem servidor.

- `salvar` não duplica: o mesmo fato (ignorando maiúsculas e espaços) devolve o id que já existe.
- `buscar` aceita texto livre; cada palavra vira um termo OU.
- `semear` lê as linhas "- " do MEMORY.md na 1ª vez.
"""
import os
import sqlite3
from dataclasses import dataclass

ESQUEMA = """
CREATE TABLE IF NOT EXISTS memorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conteudo TEXT NOT NULL,
    chave TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL DEFAULT 'fato',
    criada TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE VIRTUAL TABLE IF NOT EXISTS memorias_fts USING fts5(conteudo, content='memorias', content_rowid='id', tokenize='unicode61 remove_diacritics 2');
CREATE TRIGGER IF NOT EXISTS m_ai AFTER INSERT ON memorias BEGIN
  INSERT INTO memorias_fts(rowid, conteudo) VALUES (new.id, new.conteudo); END;
CREATE TRIGGER IF NOT EXISTS m_ad AFTER DELETE ON memorias BEGIN
  INSERT INTO memorias_fts(memorias_fts, rowid, conteudo) VALUES ('delete', old.id, old.conteudo); END;
CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
"""
PALAVRAS_VAZIAS = {"o", "a", "os", "as", "de", "do", "da", "dos", "das", "e", "é", "que", "qual", "quais", "meu", "minha",
                   "um", "uma", "em", "no", "na", "para", "por", "com", "se", "me", "eu", "você", "the", "is", "my", "what"}


@dataclass
class Memoria:
    id: int
    conteudo: str
    categoria: str
    criada: str


def _chave(texto: str) -> str:
    return " ".join(texto.lower().split())


def _consulta(texto: str) -> str:
    termos = ["".join(c for c in t if c.isalnum()) for t in texto.lower().split()]
    termos = [t for t in termos if t and t not in PALAVRAS_VAZIAS]
    return " OR ".join(f'"{t}"' for t in termos)


class Memorias:
    def __init__(self, caminho: str):
        self.caminho = caminho
        if caminho != ":memory:":
            os.makedirs(os.path.dirname(os.path.abspath(caminho)), exist_ok=True)
        self.db = sqlite3.connect(caminho)
        self.db.row_factory = sqlite3.Row
        self.db.executescript(ESQUEMA)
        self.db.commit()

    def salvar(self, conteudo: str, categoria: str = "fato") -> int:
        conteudo = conteudo.strip()
        if not conteudo:
            raise ValueError("memória vazia")
        k = _chave(conteudo)
        achou = self.db.execute("SELECT id FROM memorias WHERE chave=?", (k,)).fetchone()
        if achou:
            return int(achou["id"])
        cur = self.db.execute("INSERT INTO memorias (conteudo, chave, categoria) VALUES (?,?,?)", (conteudo, k, categoria))
        self.db.commit()
        return int(cur.lastrowid)

    def buscar(self, texto: str, limite: int = 5) -> list:
        q = _consulta(texto)
        if not q:
            return []
        linhas = self.db.execute(
            "SELECT m.id, m.conteudo, m.categoria, m.criada FROM memorias_fts f JOIN memorias m ON m.id=f.rowid "
            "WHERE memorias_fts MATCH ? ORDER BY bm25(memorias_fts) LIMIT ?", (q, limite)).fetchall()
        return [Memoria(r["id"], r["conteudo"], r["categoria"], r["criada"]) for r in linhas]

    def recentes(self, limite: int = 10) -> list:
        linhas = self.db.execute("SELECT id, conteudo, categoria, criada FROM memorias ORDER BY id DESC LIMIT ?", (limite,)).fetchall()
        return [Memoria(r["id"], r["conteudo"], r["categoria"], r["criada"]) for r in linhas]

    def esquecer(self, id_: int) -> bool:
        cur = self.db.execute("DELETE FROM memorias WHERE id=?", (int(id_),))
        self.db.commit()
        return cur.rowcount > 0

    def total(self) -> int:
        return int(self.db.execute("SELECT count(*) FROM memorias").fetchone()[0])

    def semear(self, arquivo_md: str) -> int:
        """Carrega as linhas '- ' do MEMORY.md uma única vez."""
        if self.db.execute("SELECT 1 FROM meta WHERE k='semeado'").fetchone() or not os.path.isfile(arquivo_md):
            return 0
        n = 0
        with open(arquivo_md, encoding="utf-8") as f:
            for linha in f:
                if linha.startswith("- ") and "(preencha)" not in linha:
                    self.salvar(linha[2:].strip(), "inicial")
                    n += 1
        self.db.execute("INSERT OR REPLACE INTO meta VALUES ('semeado', datetime('now'))")
        self.db.commit()
        return n

    def fechar(self) -> None:
        self.db.close()
