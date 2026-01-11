#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose_file="$repo_root/example_compose/docker-compose.yml"

docker compose --env-file "$repo_root/.env" -f "$compose_file" down
