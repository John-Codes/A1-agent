#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
bind_ip="${AONE_BIND_IP:-100.91.34.26}"
port="${AONE_PORT:-8001}"
mkdir -p .lancedb .browser-use .browseruse
touch gateway.log
docker stop aone-hermes >/dev/null 2>&1 || true
docker rm aone-hermes >/dev/null 2>&1 || true
docker run -d --name aone-hermes --restart unless-stopped \
  --env-file .env -e HERMES_API_HOST=0.0.0.0 -e HERMES_API_PORT=8000 \
  -p "${bind_ip}:${port}:8000" \
  -v "$PWD/.env:/app/.env" \
  -v "$PWD/context:/app/context" -v "$PWD/.lancedb:/app/.lancedb" \
  -v "$PWD/.browser-use:/app/.browser-use" \
  -v "$PWD/.browseruse:/app/.browseruse" \
  -v "$PWD/gateway.log:/app/gateway.log" aone-hermes:local
