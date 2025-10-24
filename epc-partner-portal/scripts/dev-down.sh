#!/usr/bin/env bash
set -euo pipefail

API_PORT=${API_PORT:-8787}
WEB_PORT=${WEB_PORT:-4200}

echo "==> Bringing down local dev stack"

kill_by_port() {
  local port=$1
  local pids
  pids=$(lsof -ti tcp:"$port" || true)
  if [ -n "$pids" ]; then
    echo "- Killing processes on :$port -> $pids"
    kill $pids || true
  else
    echo "- No processes on :$port"
  fi
}

kill_by_port "$API_PORT"
kill_by_port "$WEB_PORT"

echo "==> Done"

