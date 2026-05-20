#!/usr/bin/env bash
set -euo pipefail

SESSION="hermes-gateway"
CMD="hermes gateway run"

if pgrep -af "hermes gateway run" >/dev/null; then
  echo "Gateway já está rodando:"
  pgrep -af "hermes gateway run"
  exit 0
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "ERRO: tmux não encontrado. Rode manualmente: $CMD" >&2
  exit 1
fi

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Sessão tmux $SESSION já existe. Status:"
  tmux ls | grep "$SESSION" || true
  exit 0
fi

tmux new-session -d -s "$SESSION" "$CMD"
echo "Gateway iniciado em tmux: $SESSION"
echo "Ver tela: tmux attach -t $SESSION"
