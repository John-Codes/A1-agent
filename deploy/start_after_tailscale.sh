#!/usr/bin/env bash
set -euo pipefail

tailscale_ip="${TAILSCALE_IP:-100.91.34.26}"
for _ in $(seq 1 60); do
  if ip -4 address show | grep -Fq "$tailscale_ip"; then
    docker start aone-whisper >/dev/null 2>&1 || true
    docker start aone-voice-api >/dev/null 2>&1 || true
    docker start aone-hermes >/dev/null 2>&1 || true
    docker start aone-mongodb-api >/dev/null 2>&1 || true
    docker start aone-trello-api >/dev/null 2>&1 || true
    docker start aone-chat-history-api >/dev/null 2>&1 || true
    exit 0
  fi
  sleep 2
done
echo "Tailscale IP did not appear: $tailscale_ip" >&2
exit 1
