#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SESSION="${A1_TMUX_SESSION:-a1}"
PYTHON="${A1_PYTHON:-$ROOT_DIR/.venv/bin/python}"

cd "$ROOT_DIR"
if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is required: install it with your system package manager" >&2
  exit 1
fi
if tmux has-session -t "$SESSION" 2>/dev/null; then
  :
else
  tmux new-session -d -s "$SESSION" -n console \
    "cd '$ROOT_DIR' && exec '$PYTHON' main.py"
fi

if [[ "${1:-}" == "--watch" ]]; then
  trap 'tmux kill-session -t "$SESSION" 2>/dev/null || true' TERM INT EXIT
  while tmux has-session -t "$SESSION" 2>/dev/null; do
    sleep 5
  done
  exit 1
fi
