"""Ollama: modelo rodando no seu computador (custo zero, nada sai da máquina).

Usa a API local /api/chat com ferramentas (modelos com tool calling: llama3.2, qwen3…).
"""
import uuid

from .base import Provedor, Resposta, args_dict, post_json_async


def _para_ollama(m) -> dict:
    d = {"role": m.papel, "content": m.texto or ""}
    if m.chamadas:
        d["tool_calls"] = [{"function": {"name": c["nome"], "arguments": c.get("args", {})}} for c in m.chamadas]
    if m.papel == "tool" and m.nome:
        d["tool_name"] = m.nome
    return d


class Ollama(Provedor):
    nome = "ollama"

    def __init__(self, modelo: str = "llama3.2", url: str = "http://localhost:11434", temperatura: float = 0.4, tempo: int = 300):
        self.modelo = modelo
        self.url = url.rstrip("/")
        self.temperatura = temperatura
        self.tempo = tempo

    async def conversar(self, mensagens, ferramentas=None) -> Resposta:
        corpo = {
            "model": self.modelo,
            "messages": [_para_ollama(m) for m in mensagens],
            "stream": False,
            "options": {"temperature": self.temperatura},
        }
        if ferramentas:
            corpo["tools"] = [{"type": "function", "function": {
                "name": f.nome, "description": f.descricao, "parameters": f.parametros}} for f in ferramentas]
        r = await post_json_async(f"{self.url}/api/chat", corpo, tempo=self.tempo)
        msg = r.get("message") or {}
        chamadas = []
        for c in msg.get("tool_calls") or []:
            fn = c.get("function") or {}
            chamadas.append({"id": c.get("id") or uuid.uuid4().hex[:8], "nome": fn.get("name", ""), "args": args_dict(fn.get("arguments"))})
        uso = {"entrada": r.get("prompt_eval_count", 0), "saida": r.get("eval_count", 0)}
        return Resposta(texto=msg.get("content") or "", chamadas=chamadas, uso=uso)
