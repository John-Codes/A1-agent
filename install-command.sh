#!/usr/bin/env bash
set -euo pipefail

command_name="${1:-Aone}"
gateway_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bin_dir="${HOME}/.local/bin"
command_path="${bin_dir}/${command_name}"
shell_name="$(basename "${SHELL:-}")"
profile_file="${HOME}/.bashrc"

if [ "$shell_name" = "zsh" ]; then
  profile_file="${HOME}/.zshrc"
fi

case "$command_name" in
  *[!a-zA-Z0-9._-]* | "")
    echo "Command name must contain only letters, numbers, dots, underscores, or dashes." >&2
    exit 2
    ;;
esac

mkdir -p "$bin_dir"

cat > "$command_path" <<EOF
#!/usr/bin/env bash
set -euo pipefail

POCKETFLOW_GATEWAY_DIR="${gateway_dir}"
export POCKETFLOW_GATEWAY_DIR

exec "\${POCKETFLOW_GATEWAY_DIR}/run.sh" "\$@"
EOF

chmod +x "$command_path"

touch "$profile_file"

if ! grep -Fq "POCKETFLOW_GATEWAY_DIR=" "$profile_file"; then
  {
    echo ""
    echo "# PocketFlow personal AI gateway"
    echo "export POCKETFLOW_GATEWAY_DIR=\"${gateway_dir}\""
  } >> "$profile_file"
fi

if ! grep -Fq 'export PATH="$HOME/.local/bin:$PATH"' "$profile_file"; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$profile_file"
fi

echo "Installed ${command_name} at ${command_path}"
echo "Open a new terminal or run: source ${profile_file}"
