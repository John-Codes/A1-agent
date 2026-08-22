#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi

stamp=".venv/.requirements.stamp"
if [ ! -f "$stamp" ] || [ requirements.txt -nt "$stamp" ]; then
  .venv/bin/python -m pip install -r requirements.txt
  touch "$stamp"
fi

exec .venv/bin/python main.py "$@"
