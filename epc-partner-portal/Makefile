SHELL := /bin/bash

.PHONY: test test-worker test-e2e verify setup

test: test-worker test-e2e verify
	@echo "All tests completed"

test-worker:
	node tests/worker/test_worker.js

test-e2e:
	E2E_VERIFY_URL?=https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access.html
	E2E_EMAIL?=test@example.com
	E2E_INVITE_CODE?=ABCD1234
	E2E_UPLOAD_FILE?=$(PWD)/tests/fixtures/sample.pdf
	E2E_VERIFY_URL=$$E2E_VERIFY_URL E2E_EMAIL=$$E2E_EMAIL E2E_INVITE_CODE=$$E2E_INVITE_CODE E2E_UPLOAD_FILE=$$E2E_UPLOAD_FILE \
		node tests/e2e/puppeteer_e2e.js

verify:
	@if command -v pwsh >/dev/null 2>&1; then \
	  pwsh -File scripts/verify-submission.ps1 -InvitationCode $${E2E_INVITE_CODE:-ABCD1234} -Email $${E2E_EMAIL:-test@example.com} -VerifyInvitation || true; \
	else \
	  echo "pwsh not found; skipping SharePoint verification"; \
	fi

