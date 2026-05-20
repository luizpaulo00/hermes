#!/usr/bin/env bash
set -euo pipefail

SESSION="hermes-gateway"

echo "== Hermes version =="
hermes --version || true

echo
echo "== Gateway status =="
hermes gateway status || true

echo
echo "== Gateway process =="
pgrep -af "hermes gateway run" || echo "Nenhum processo hermes gateway run encontrado."

echo
echo "== tmux =="
if command -v tmux >/dev/null 2>&1; then
  tmux ls 2>/dev/null || echo "Nenhuma sessão tmux."
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Sessão $SESSION existe. Ver tela: tmux attach -t $SESSION"
  fi
else
  echo "tmux não instalado."
fi

echo
echo "== Últimas linhas do gateway.log =="
LOG="$HOME/.hermes/logs/gateway.log"
if [ -f "$LOG" ]; then
  tail -40 "$LOG"
else
  echo "Log não encontrado: $LOG"
fi
