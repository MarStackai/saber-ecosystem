#!/usr/bin/env bash
set -euo pipefail

echo "==> Bringing up local dev stack (API + Frontend)"

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
APP_DIR="$ROOT_DIR/epc-portal-react"
export XDG_CONFIG_HOME="$APP_DIR/.config"
export WRANGLER_HOME="$APP_DIR/.wrangler-home"

API_PORT=${API_PORT:-8787}
WEB_PORT=${WEB_PORT:-4200}

echo "- Seeding D1 schema (local)"
cd "$APP_DIR"
mkdir -p dev-static && echo "<!doctype html><title>EPC Dev</title>" > dev-static/index.html
npx wrangler d1 execute epc-form-data --local --file "$ROOT_DIR/schema.sql" >/dev/null

echo "- Starting Pages Functions on :$API_PORT"
nohup env XDG_CONFIG_HOME="$XDG_CONFIG_HOME" WRANGLER_HOME="$WRANGLER_HOME" \
  npx wrangler pages dev ./dev-static --ip 0.0.0.0 --port "$API_PORT" \
  > "$ROOT_DIR/.api-dev.log" 2>&1 &
API_PID=$!
sleep 2

echo "- Starting Next.js dev on :$WEB_PORT (proxying /api to $API_PORT)"
nohup env NEXT_FORCE_WASM_BINARY=1 XDG_CACHE_HOME=.cache \
  NEXT_PUBLIC_API_URL="http://localhost:$API_PORT" \
  npm run dev --prefix "$APP_DIR" \
  > "$ROOT_DIR/.next-dev.log" 2>&1 &
WEB_PID=$!
sleep 2

echo "==> Dev up: API PID=$API_PID, WEB PID=$WEB_PID"
echo "    Frontend: http://localhost:$WEB_PORT"
echo "    API:      http://localhost:$API_PORT"

