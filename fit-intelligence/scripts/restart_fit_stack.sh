#!/usr/bin/env bash
set -euo pipefail

SERVICES=("fit-api.service" "fit-cloudflared.service")

echo "Reloading user-level systemd units..."
systemctl --user daemon-reload

for svc in "${SERVICES[@]}"; do
  echo "Restarting ${svc}"
  systemctl --user restart "$svc"
done

echo "Checking status"
systemctl --user --no-pager status "${SERVICES[@]}"

echo "Done"
