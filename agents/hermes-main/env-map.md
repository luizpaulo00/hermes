# hermes-main env map

> Não colocar valores reais neste arquivo.

## Configuração Hermes

Arquivos sensíveis reais ficam fora do control room:

- `~/.hermes/.env`
- `~/.hermes/config.yaml`
- `~/.hermes/auth.json`
- `~/.hermes/state.db`
- `~/.hermes/logs/`

## Segredos esperados

- Token do bot Telegram: configurado pelo `hermes gateway setup` ou config equivalente.
- Auth OpenAI Codex/OAuth: guardado em `~/.hermes/auth.json`.
- Chaves de provedores opcionais: ficam em `~/.hermes/.env`.
- Credenciais GitHub, se usadas: não salvar neste repo; usar `gh auth`, variável temporária, ou GitHub Secrets quando necessário.

## Regra

Este arquivo só lista nomes/locais esperados. Nunca colocar valores reais de tokens, chaves ou cookies.
