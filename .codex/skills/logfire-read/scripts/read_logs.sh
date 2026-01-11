#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
venv_python="$repo_root/.venv/bin/python"

if [[ -f "$repo_root/.env" ]]; then
  set -a
  . "$repo_root/.env"
  set +a
fi

if [[ -x "$venv_python" ]]; then
  PYTHONPATH="$repo_root" "$venv_python" "$repo_root/scripts/logfire-read-agent.py" "$@"
else
  PYTHONPATH="$repo_root" python "$repo_root/scripts/logfire-read-agent.py" "$@"
fi
