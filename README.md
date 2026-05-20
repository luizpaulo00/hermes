# Hermes Control Room

Control room da operação Hermes do Luiz.

Este diretório documenta como o Hermes roda na VPS, como acessar pelo Telegram, como reiniciar, como evoluir de um agente pessoal para uma frota de agentes especialistas e quais regras de segurança seguir.

## Estado atual

- Level atual: **Level 1**
- VPS: Linux em `/home/luiz`
- Hermes: instalado e atualizado
- Telegram: configurado e respondendo neste chat
- Gateway: rodando como processo manual/background, não como serviço systemd user
- Plano principal: `plans/hermes-levels-roadmap.md`

## Estrutura

- `plans/`: planos e roadmap por level.
- `agents/hermes-main/`: inventário, runbook e mapa de ambiente do agente principal.
- `shared/`: regras de segurança e comandos úteis.
- `scripts/`: scripts operacionais seguros.

## Regras importantes

Não guardar segredos aqui.

Segredos proibidos neste diretório/repo:

- tokens do Telegram;
- GitHub PATs;
- arquivos `.env`;
- `auth.json`;
- logs brutos;
- `state.db`;
- `config.yaml` com chaves.

## Próximo marco

Completar Level 1:

1. manter o gateway estável;
2. documentar operação;
3. salvar control room no GitHub quando o repositório estiver definido;
4. só depois iniciar Level 2 com profiles especialistas.
