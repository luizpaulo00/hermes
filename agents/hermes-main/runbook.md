# hermes-main runbook

## Status do Hermes

```bash
hermes --version
hermes status --all
```

## Status do gateway

```bash
hermes gateway status
```

Estado observado neste ambiente:

```text
Failed to connect to bus: No medium found
User gateway service is stopped
Gateway process is running for this profile, but the service is not active
```

Interpretação: o gateway está rodando como processo manual/background, não como serviço systemd user.

## Rodar gateway manualmente

```bash
hermes gateway run
```

## Rodar gateway em tmux

```bash
tmux new-session -d -s hermes-gateway 'hermes gateway run'
```

Ver tela:

```bash
tmux attach -t hermes-gateway
```

Sair sem parar:

```text
Ctrl+B, depois D
```

Parar tmux:

```bash
tmux kill-session -t hermes-gateway
```

## Scripts do control room

```bash
/home/luiz/hermes-control-room/scripts/status-gateway.sh
/home/luiz/hermes-control-room/scripts/start-gateway.sh
/home/luiz/hermes-control-room/scripts/stop-gateway.sh
```

## Logs

```bash
tail -f ~/.hermes/logs/gateway.log
```

## Parar processo manual sem tmux

Use com cuidado:

```bash
pkill -f 'hermes gateway run'
```

## Atualizar Hermes

```bash
hermes update
hermes --version
```

## Troubleshooting rápido

1. Bot não responde no Telegram:
   - rodar `hermes gateway status`;
   - verificar se existe processo `hermes gateway run`;
   - olhar `~/.hermes/logs/gateway.log`.
2. Serviço systemd user falha:
   - usar fallback com `tmux`;
   - investigar bus/systemd user depois.
3. Mudanças de config não aplicam:
   - reiniciar gateway/processo Hermes.
