#!/usr/bin/env bash
set -euo pipefail

# One-command local test runner:
# 1) Worker/API tests (no external calls)
# 2) Browser E2E via Puppeteer
# 3) Optional SharePoint verification via PowerShell (if pwsh available)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"

# Config defaults
E2E_VERIFY_URL_DEFAULT="https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access.html"
E2E_EMAIL_DEFAULT="test@example.com"
E2E_INVITE_CODE_DEFAULT="ABCD1234"
E2E_UPLOAD_FILE_DEFAULT="$ROOT_DIR/tests/fixtures/sample.pdf"

E2E_VERIFY_URL="${E2E_VERIFY_URL:-$E2E_VERIFY_URL_DEFAULT}"
E2E_EMAIL="${E2E_EMAIL:-$E2E_EMAIL_DEFAULT}"
E2E_INVITE_CODE="${E2E_INVITE_CODE:-$E2E_INVITE_CODE_DEFAULT}"
E2E_UPLOAD_FILE="${E2E_UPLOAD_FILE:-$E2E_UPLOAD_FILE_DEFAULT}"

echo "===================================================="
echo "🚀 Saber EPC - Local E2E Test Runner"
echo "===================================================="
echo "Verify URL:   $E2E_VERIFY_URL"
echo "Email:        $E2E_EMAIL"
echo "Invite Code:  $E2E_INVITE_CODE"
echo "Upload File:  $E2E_UPLOAD_FILE"
echo

echo "[1/3] Running worker/API tests..."
node "$ROOT_DIR/tests/worker/test_worker.js"
echo

echo "[2/3] Running browser E2E (Puppeteer)..."
E2E_VERIFY_URL="$E2E_VERIFY_URL" \
E2E_EMAIL="$E2E_EMAIL" \
E2E_INVITE_CODE="$E2E_INVITE_CODE" \
E2E_UPLOAD_FILE="$E2E_UPLOAD_FILE" \
node "$ROOT_DIR/tests/e2e/puppeteer_e2e.js"
echo

echo "[3/3] SharePoint verification (if pwsh available)..."
if command -v pwsh >/dev/null 2>&1; then
  set +e
  pwsh -File "$ROOT_DIR/scripts/verify-submission.ps1" \
    -InvitationCode "$E2E_INVITE_CODE" \
    -Email "$E2E_EMAIL" \
    -VerifyInvitation
  status=$?
  set -e
  if [ $status -eq 0 ]; then
    echo "✅ SharePoint verification passed"
  else
    echo "⚠ SharePoint verification did not find a matching submission."
    echo "   You can re-run: pwsh -File $ROOT_DIR/scripts/verify-submission.ps1 -InvitationCode $E2E_INVITE_CODE -Email $E2E_EMAIL -VerifyInvitation"
  fi
else
  echo "pwsh not found. Skipping SharePoint verification."
  echo "Install PowerShell 7 and PnP.PowerShell if you want this step:"
  echo "  sudo snap install powershell --classic"
  echo "  pwsh -c 'Install-Module PnP.PowerShell -Scope CurrentUser'"
fi

echo
echo "Done."

