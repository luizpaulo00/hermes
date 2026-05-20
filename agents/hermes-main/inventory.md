# hermes-main inventory

## Identidade

- Nome: `hermes-main`
- Profile Hermes: `default`
- Função: assistente Hermes principal do Luiz
- Level atual: Level 1

## Onde roda

- Host: VPS Linux
- Home: `/home/luiz`
- Hermes project: `/home/luiz/.hermes/hermes-agent`
- Control room: `/home/luiz/hermes-control-room`

## Canais

- CLI: `hermes`
- Telegram: bot configurado no gateway
- Telegram home chat: `958140131`

## Responsabilidades

- Assistente geral.
- Operação inicial do Level 1.
- Administração assistida de VPS, GitHub e documentação.
- Manter o control room organizado.

## Limites

- Não publicar segredos no GitHub.
- Não executar ações destrutivas sem confirmação.
- Não commitar `.env`, `auth.json`, `state.db`, logs brutos ou config com tokens.

## Estado observado

- Hermes está up to date.
- Gateway está rodando como processo manual/background.
- Serviço systemd user não está ativo neste ambiente por erro de bus.
