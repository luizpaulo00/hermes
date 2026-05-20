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
