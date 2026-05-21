# Useful commands

## Hermes

```bash
hermes
hermes --version
hermes status --all
hermes gateway status
hermes gateway run
hermes profile list
hermes config path
hermes config env-path
```

## Gateway via scripts

```bash
/home/luiz/hermes-control-room/scripts/status-gateway.sh
/home/luiz/hermes-control-room/scripts/start-gateway.sh
/home/luiz/hermes-control-room/scripts/stop-gateway.sh
```

## Gateway tmux

```bash
tmux new-session -d -s hermes-gateway 'hermes gateway run'
tmux attach -t hermes-gateway
tmux kill-session -t hermes-gateway
tmux ls
```

## Logs

```bash
tail -f ~/.hermes/logs/gateway.log
```

## Browse.sh / Browse CLI

```bash
browse --version
browse doctor
browse skills list
browse skills find "zillow"
browse skills add <domain>/<task-slug>
browse open https://example.com --local
browse snapshot --compact
browse get title
browse stop
```

Notas locais:

- wrapper: `~/.local/bin/browse`
- CLI real: `~/.hermes/node/bin/browse`
- Chrome local: `~/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome`
- env persistido em `~/.hermes/.env`: `CHROME_PATH` e `BROWSE_NO_SANDBOX=1`
- skill Hermes criada: `browse-sh`

## Cron / automações recorrentes

```bash
hermes cron list
hermes cron status
hermes cron run c37f7708dda9
hermes cron run 1453330e293a
hermes cron run aa3e257db6b6
hermes cron run 0a9355c19ace
```

Jobs ativos:

- `c37f7708dda9` — `Hermes VPS daily health check`, roda todo dia às `09:00 UTC` e entrega o resumo neste Telegram.
- `1453330e293a` — `Hermes weekly safe backup`, roda segunda às `08:00 UTC`, gera backup seguro em `/home/luiz/backups/hermes-control-room/` e entrega confirmação no Telegram.
- `aa3e257db6b6` — `Hermes weekly operations review`, roda segunda às `10:00 UTC` e entrega uma revisão curta da operação no Telegram.
- `0a9355c19ace` — `Hermes GitHub monitor`, roda a cada 6 horas e só avisa quando houver mudança relevante no repo `luizpaulo00/hermes`.

O health check verifica VPS, disco, memória, processos Hermes, gateway, tmux e erros recentes de log sem expor segredos. O backup usa `git archive` do `HEAD`, roda `scripts/check-no-secrets.py` antes e mantém os 12 backups mais recentes. O monitor GitHub compara estado salvo em `~/.hermes/state/github-monitor-luizpaulo00-hermes.json` e fica silencioso quando nada muda.

## Git

```bash
git status
git add .
git commit -m "docs: update hermes control room"
git push
```

## Segurança

```bash
python3 scripts/check-no-secrets.py
```
