"""O loop com freio: pensa → (ferramenta → resultado)* → responde. No máximo N rodadas.

Contexto de cada mensagem = SOUL + AGENTS + USER (identidade) + memórias que casam
com a pergunta + as últimas conversas do mesmo chat.
"""
import os

from ..provedores.base import ErroProvedor, Mensagem


class Contexto:
    def __init__(self, config, memorias):
        self.config = config
        self.memorias = memorias

    def identidade(self) -> str:
        partes = []
        for nome in ("SOUL.md", "AGENTS.md", "USER.md"):
            p = os.path.join(self.config.identidade, nome)
            if os.path.isfile(p):
                with open(p, encoding="utf-8") as f:
                    partes.append(f.read().strip())
        texto = "\n\n".join(partes)
        return texto.replace("{nome}", self.config.nome).replace("{personalidade}", self.config.personalidade)

    def montar(self, historico: list, pergunta: str) -> list:
        msgs = [Mensagem("system", self.identidade())]
        achadas = self.memorias.buscar(pergunta, limite=5)
        if achadas:
            msgs.append(Mensagem("system", "Memórias que podem ajudar:\n" + "\n".join(f"- {m.conteudo}" for m in achadas)))
        msgs.extend(historico)
        msgs.append(Mensagem("user", pergunta))
        return msgs


class Agente:
    def __init__(self, config, provedor, memorias, registro, auditoria=None):
        self.config = config
        self.provedor = provedor
        self.contexto = Contexto(config, memorias)
        self.registro = registro
        self.auditoria = auditoria
        self.historico = {}

    async def responder(self, chat: str, pergunta: str) -> str:
        hist = self.historico.setdefault(chat, [])
        msgs = self.contexto.montar(hist, pergunta)
        defs = self.registro.definicoes() if self.registro else None
        final = ""
        try:
            for _ in range(int(self.config.max_rodadas)):
                r = await self.provedor.conversar(msgs, defs)
                if not r.chamadas:
                    final = r.texto
                    break
                msgs.append(Mensagem("assistant", r.texto, chamadas=r.chamadas))
                for c in r.chamadas:
                    f = self.registro.pegar(c["nome"])
                    if f is None:
                        saida, ok = f"ferramenta desconhecida: {c['nome']}", False
                    else:
                        res = await f.executar(**(c.get("args") or {}))
                        saida, ok = res.saida, res.ok
                    if self.auditoria:
                        self.auditoria.registrar("ferramenta", chat=chat, nome=c["nome"], ok=ok, args=c.get("args"))
                    msgs.append(Mensagem("tool", saida, id_chamada=c.get("id"), nome=c["nome"]))
            else:
                # freio: acabaram as rodadas → resposta final sem ferramentas
                msgs.append(Mensagem("system", "Limite de rodadas atingido. Responda agora com o que você já tem."))
                final = (await self.provedor.conversar(msgs, None)).texto
        except ErroProvedor as e:
            if self.auditoria:
                self.auditoria.registrar("erro", chat=chat, erro=str(e))
            return f"Não consegui falar com o cérebro ({self.provedor.nome}): {e}"
        final = final.strip() or "(sem resposta)"
        hist += [Mensagem("user", pergunta), Mensagem("assistant", final)]
        del hist[:-20]   # guarda as últimas 10 trocas
        return final
