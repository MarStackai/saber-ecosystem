/*
 One-command E2E: drives verify → form → submit using Puppeteer.
 Uses the DOM from epc-form/*.html as deployed to SharePoint.

 Usage:
   node saber_business_ops/tests/e2e/puppeteer_e2e.js

 Env overrides:
   E2E_VERIFY_URL   - Full URL to verify-access.html
   E2E_EMAIL        - Test email (default: test@example.com)
   E2E_INVITE_CODE  - Test invite code (default: ABCD1234)
   E2E_UPLOAD_FILE  - Path to a file to upload
   E2E_HEADFUL      - "1" to run non-headless
   PUPPETEER_MODULE_PATH - Absolute path to puppeteer module dir (optional)
*/

import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));

async function loadPuppeteer() {
  const explicit = process.env.PUPPETEER_MODULE_PATH;
  const candidatePaths = [];
  if (explicit) candidatePaths.push(explicit);
  // Try the MCP server’s dependency path
  candidatePaths.push(path.join(process.env.HOME || '~', '.npm-global/lib/node_modules/@modelcontextprotocol/server-puppeteer/node_modules/puppeteer'));
  // Fallback to normal resolution
  try {
    return (await import('puppeteer')).default;
  } catch {}
  for (const p of candidatePaths) {
    try {
      const mod = await import(url.pathToFileURL(path.join(p, 'lib/esm/puppeteer/puppeteer.js')));
      return mod.default || mod;
    } catch {}
    try {
      const mod = await import(url.pathToFileURL(path.join(p, 'index.js')));
      return mod.default || mod;
    } catch {}
  }
  throw new Error('Unable to load puppeteer. Set PUPPETEER_MODULE_PATH to a valid module directory.');
}

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function ts() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

async function run() {
  const puppeteer = await loadPuppeteer();
  const verifyUrl = process.env.E2E_VERIFY_URL || 'https://saberrenewables.sharepoint.com/sites/SaberEPCPartners/SiteAssets/EPCForm/verify-access.html';
  const email = process.env.E2E_EMAIL || 'test@example.com';
  const inviteCode = (process.env.E2E_INVITE_CODE || 'ABCD1234').toUpperCase();
  const uploadFile = process.env.E2E_UPLOAD_FILE || path.resolve(__dirname, '../fixtures/sample.pdf');
  const headful = process.env.E2E_HEADFUL === '1';

  const screenshotsDir = path.resolve(__dirname, 'screens', ts());
  ensureDir(screenshotsDir);

  const browser = await puppeteer.launch({ headless: !headful, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  const page = await browser.newPage();
  page.setDefaultTimeout(20000);

  try {
    // 1) Verify page
    await page.goto(verifyUrl, { waitUntil: 'domcontentloaded' });
    await page.screenshot({ path: path.join(screenshotsDir, 'step-1-verify.png') });

    // Fill email
    await page.waitForSelector('#email');
    await page.type('#email', email);

    // Enter invalid code first
    const code = 'XXXX0000';
    const digits = await page.$$('.code-input');
    if (digits.length >= 8) {
      for (let i = 0; i < 8; i++) {
        await digits[i].type(code[i]);
      }
    }
    await Promise.all([
      page.click('button.saber-btn'),
      page.waitForTimeout(800),
    ]);
    // Expect error message to show
    await page.screenshot({ path: path.join(screenshotsDir, 'step-2-invalid.png') });

    // Clear and enter valid invite code
    for (const el of digits) { await el.click({ clickCount: 3 }); await el.press('Backspace'); }
    for (let i = 0; i < 8; i++) {
      await digits[i].type(inviteCode[i]);
    }

    // Submit and wait for redirect to form
    await Promise.all([
      page.click('button.saber-btn'),
      page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }).catch(() => {}),
      page.waitForTimeout(2200) // verify-access uses a 2s timeout before redirect
    ]);
    await page.screenshot({ path: path.join(screenshotsDir, 'step-3-form.png') });

    // We should now be on index.html form
    // Fill Step 1
    await page.waitForSelector('#epcOnboardingForm');
    await page.type('#companyName', 'Test EPC Ltd');
    await page.type('#tradingName', 'Test EPC');
    await page.type('#registeredOffice', '1 Test Street, Test City, TE1 2ST');
    await page.type('#companyRegNo', '12345678');
    await page.type('#vatNo', 'GB123');
    await page.type('#yearsTrading', '7');

    // Next
    await page.click('.form-step[data-step="1"] .next-step');

    // Step 2: Contact info (selectors rely on names defined in HTML)
    await page.waitForSelector('.form-step[data-step="2"]');
    await page.type('#primaryContactName', 'Jane Doe');
    await page.type('#primaryContactEmail', email);
    await page.type('#primaryContactPhone', '+44 1234 567890');

    // coverageRegion checkboxes
    const check = async (value) => {
      const sel = `input[name="coverageRegion"][value="${value}"]`;
      if (await page.$(sel)) await page.click(sel);
    };
    await check('North West');
    await check('Midlands');

    await page.click('.form-step[data-step="2"] .next-step');

    // Step 3: Compliance
    await page.waitForSelector('.form-step[data-step="3"]');
    const checkIso = async (value) => {
      const sel = `input[name="isoStandards"][value="${value}"]`;
      if (await page.$(sel)) await page.click(sel);
    };
    await checkIso('ISO 9001');
    await checkIso('ISO 14001');

    await page.click('input[name="actsAsPrincipalContractor"][value="Yes"]');
    await page.click('input[name="actsAsPrincipalDesigner"][value="No"]');
    await page.click('input[name="hasGDPRPolicy"][value="Yes"]');
    await page.type('#hsqIncidents', '0');
    await page.type('#riddor', '0');

    await page.click('.form-step[data-step="3"] .next-step');

    // Step 4: Documents & Terms
    await page.waitForSelector('.form-step[data-step="4"]');
    // Upload file via hidden input
    const fileInput = await page.$('#fileInput');
    if (fileInput) {
      await fileInput.uploadFile(uploadFile);
    }
    await page.type('#notes', 'E2E automated test');
    await page.click('#agreeToTerms');

    await page.screenshot({ path: path.join(screenshotsDir, 'step-4-before-submit.png') });

    // Submit
    await Promise.all([
      page.click('.form-step[data-step="4"] .submit-btn'),
      page.waitForTimeout(2500),
    ]);

    // Expect success modal
    await page.waitForSelector('#successModal', { timeout: 20000 });
    await page.screenshot({ path: path.join(screenshotsDir, 'step-5-success.png') });

    console.log('E2E completed. Screenshots at:', screenshotsDir);
  } finally {
    await browser.close();
  }
}

run().catch((err) => {
  console.error('E2E error:', err);
  process.exit(1);
});

