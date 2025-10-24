MCP Puppeteer Test Guide (Local LLM Friendly)

Overview
- Use the MCP Puppeteer server to drive a real browser for end‑to‑end testing of the EPC onboarding flow.
- Works well with a local LLM (e.g., Ollama --OSS:20B) via an MCP-capable client (e.g., Claude Desktop).

What this covers
- Verify-access page behavior (invalid vs valid invite code)
- Full form completion (multi-step), file upload, and submission
- Screenshot artifacts for each step

Prerequisites
- Node.js 18+ (Node 20+ recommended)
- npm available on PATH
- An MCP client that can connect to local MCP servers (e.g., Claude Desktop)
- A valid test invite code (e.g., ABCD1234)
- Target URLs (SharePoint-hosted or Cloudflare Pages)

Install the Puppeteer MCP Server (one-time)
Option A: Use the included manager (writes Claude Desktop config)
  python mcp-manager/install_manager.py install puppeteer system

Option B: Direct npm
  npm install -g @modelcontextprotocol/server-puppeteer

After install (Claude Desktop)
- The manager writes ~/.config/claude/config.json with an MCP server entry named "puppeteer".
- Restart Claude Desktop so it picks up the new server.

Recommended Test Prompt (copy/paste)
> You have access to the "puppeteer" MCP server. Please run an end‑to‑end EPC portal test:
> 1) Open https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access.html
> 2) Take a screenshot named step-1-verify.png
> 3) Enter email test@example.com and invalid code XXXX0000, submit, assert error is shown (DOM contains "Invalid" or similar), screenshot step-2-invalid.png
> 4) Replace code with ABCD1234 (valid test code), submit, wait for navigation to the main form, screenshot step-3-form.png
> 5) Fill multi-step form with realistic test data:
>    - Company Name: Test EPC Ltd
>    - Trading Name: Test EPC
>    - Company Reg No: 12345678
>    - VAT No: GB123
>    - Years Trading: 7
>    - Primary Contact: Jane Doe, jane@example.com, +44 1234 567890
>    - Coverage Regions: North West, Midlands
>    - ISO Standards: ISO 9001, ISO 14001
>    - Acts as Principal Contractor: Yes; Principal Designer: No; GDPR Policy: Yes
>    - HSEQ incidents: 0; RIDDOR: 0
>    - Notes: E2E automated test
> 6) Upload two small files from the local file system (adjust the paths on your machine):
>    - /home/marstack/saber_business_ops/tests/fixtures/sample.pdf
>    - /home/marstack/saber_business_ops/tests/fixtures/sample.docx (or a .png)
> 7) Submit the form, wait for success UI; assert success text is present, screenshot step-4-success.png
> 8) Return the list of screenshots and any console logs encountered.

Tips
- If DOM selectors differ, use labels/placeholder text and visible text to locate inputs and buttons.
- If running against Cloudflare Pages, update the base URLs in the prompt accordingly.
- For SharePoint latency, include small waits on navigation or specific element presence.

Optional: Backend verification
- If you have SharePoint read access for testing, verify the new item exists in "EPC Onboarding" and capture key fields. Otherwise, rely on success UI and Worker/API logs.
- Script provided: `scripts/verify-submission.ps1`
  - Device login; no secrets stored
  - Examples:
    - `pwsh scripts/verify-submission.ps1 -InvitationCode ABCD1234 -Email test@example.com -VerifyInvitation`
    - `pwsh scripts/verify-submission.ps1 -CompanyName "Test EPC Ltd" -Json`
  - Reads defaults from `config.json` if present; override via params.

Troubleshooting
- If the client cannot see MCP tools, verify ~/.config/claude/config.json includes a "puppeteer" entry and restart the client.
- If the browser fails to launch in a headless environment, set the MCP server to run with --no-sandbox args.
