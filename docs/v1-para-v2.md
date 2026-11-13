# Da v1 para a v2

| | v1 (`inematds/intelecto`) | v2 (este repo) |
|---|---|---|
| Código | README descrevia o assistente, mas o pacote não existia; havia um `exemplo-jarvis` mínimo (~970 linhas, provedor só de mentira) | assistente completo, ~1.500 linhas, 67 testes |
| Dependências | prometia 7 pacotes pip | nenhuma (biblioteca padrão); `cryptography` opcional para o Fernet |
| Cérebro | OpenRouter (prometido) | Ollama local testado ao vivo, OpenRouter, mock |
| Comandos | lista de palavras proibidas (`rm -rf /` por substring; `rm -r -f /` passava) | trava em 3 classes: só leitura roda, o resto pede OK, destrutivo nunca roda; `rm -r -f /`, `bash -c '…'` e `curl … \| sh` pegos |
| Aprovação | prometida no curso | `perigosos` / `sempre` / `nunca`, no terminal e pelo Telegram (/sim /nao) |
| Telegram | estrutural, não rodava | long polling real, só responde aos donos, `/id` para descobrir o seu |
| Cofre | substituto do Fernet chamado de Fernet | Fernet quando o pacote existe; senão cifra da stdlib, e o `verificar` diz qual está em uso |
| Isolamento | WASM sandbox no curso, nada no código | executor `caixa`: Docker sem rede, só a pasta de trabalho, sem as variáveis do terminal |
| Plataforma | só macOS | Linux testado; macOS no código (launchd, id da máquina) |
| Repositório | 85 MB de `reference-repos/` | só o projeto |

O método da v1, escolher os ingredientes na **mercearia** e entregar o briefing para o Claude Code ou o Codex
construir, continua válido e está no guia ("Monte o seu do seu jeito").
