"""OpenRouter: centenas de modelos na nuvem por uma chave só (formato OpenAI).

A chave fica no cofre (`intelecto cofre guardar openrouter`), nunca no config.
Testado contra um servidor falso local (tests/test_provedores.py); a chamada real
depende da sua chave e do seu saldo.
"""
import json

from .base import ErroProvedor, Provedor, Resposta, args_dict, post_json_async


def _para_openai(m) -> dict:
    d = {"role": m.papel, "content": m.texto or ""}
    if m.chamadas:
        d["tool_calls"] = [{"id": c["id"], "type": "function",
                            "function": {"name": c["nome"], "arguments": json.dumps(c.get("args", {}), ensure_ascii=False)}}
                           for c in m.chamadas]
    if m.papel == "tool":
        d["tool_call_id"] = m.id_chamada or ""
    return d


class OpenRouter(Provedor):
    nome = "openrouter"

    def __init__(self, chave: str, modelo: str, url: str = "https://openrouter.ai/api/v1", temperatura: float = 0.4, tempo: int = 120):
        if not chave:
            raise ErroProvedor("sem chave do OpenRouter: rode `python3 -m intelecto cofre guardar openrouter`")
        self.chave = chave
        self.modelo = modelo
        self.url = url.rstrip("/")
        self.temperatura = temperatura
        self.tempo = tempo

    async def conversar(self, mensagens, ferramentas=None) -> Resposta:
        corpo = {"model": self.modelo, "messages": [_para_openai(m) for m in mensagens], "temperature": self.temperatura}
        if ferramentas:
            corpo["tools"] = [{"type": "function", "function": {
                "name": f.nome, "description": f.descricao, "parameters": f.parametros}} for f in ferramentas]
        r = await post_json_async(f"{self.url}/chat/completions", corpo,
                                  {"Authorization": f"Bearer {self.chave}", "X-Title": "INTELECTO v2"}, self.tempo)
        escolhas = r.get("choices") or []
        if not escolhas:
            raise ErroProvedor(f"resposta sem 'choices': {str(r)[:200]}")
        msg = escolhas[0].get("message") or {}
        chamadas = [{"id": c.get("id", ""), "nome": (c.get("function") or {}).get("name", ""),
                     "args": args_dict((c.get("function") or {}).get("arguments"))}
                    for c in msg.get("tool_calls") or []]
        u = r.get("usage") or {}
        return Resposta(texto=msg.get("content") or "", chamadas=chamadas,
                        uso={"entrada": u.get("prompt_tokens", 0), "saida": u.get("completion_tokens", 0)})
