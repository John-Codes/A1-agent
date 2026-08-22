#!/usr/bin/env bash
set -euo pipefail

image="${HERMES_DOCKER_IMAGE:-hermes}"
port="${HERMES_API_PORT:-8000}"

mkdir -p .lancedb
touch gateway.log

docker build -t "$image" .
exec docker run --rm \
  --env-file .env \
  -e HERMES_API_HOST=0.0.0.0 \
  -e HERMES_API_PORT=8000 \
  -p "${port}:8000" \
  -v "$(pwd)/context:/app/context" \
  -v "$(pwd)/.lancedb:/app/.lancedb" \
  -v "$(pwd)/gateway.log:/app/gateway.log" \
  "$image"
