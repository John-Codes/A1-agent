#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$UNIT_DIR"
sed "s#%h/A1-agent#$ROOT_DIR#g" "$ROOT_DIR/deploy/a1-console.service" > "$UNIT_DIR/a1-console.service"
systemctl --user daemon-reload
systemctl --user enable --now a1-console.service
echo "A1 is running in tmux session 'a1'. Attach with: tmux attach -t a1"
