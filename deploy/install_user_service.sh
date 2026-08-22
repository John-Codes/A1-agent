#!/usr/bin/env bash
set -euo pipefail

service_dir="$HOME/.config/systemd/user"
repo="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$service_dir"
ln -sfn "$repo/deploy/aone-services.service" "$service_dir/aone-services.service"
systemctl --user daemon-reload
systemctl --user enable aone-services.service
