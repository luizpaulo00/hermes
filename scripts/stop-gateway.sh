#!/usr/bin/env bash
set -euo pipefail

SESSION="hermes-gateway"

if command -v tmux >/dev/null 2>&1 && tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux kill-session -t "$SESSION"
  echo "Sessão tmux $SESSION parada."
fi

if pgrep -af "hermes gateway run" >/dev/null; then
  echo "Processos gateway ainda encontrados:"
  pgrep -af "hermes gateway run"
  echo
  echo "Para parar processo manual, rode com confirmação:"
  echo "pkill -f 'hermes gateway run'"
else
  echo "Nenhum processo 'hermes gateway run' encontrado."
fi
