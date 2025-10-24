/*
 Local worker tests without external dependencies.
 Run: node tests/worker/test_worker.js
*/

import path from 'node:path';
import url from 'node:url';

// Simple test harness
const results = [];
function expect(name, assertion) {
  try {
    assertion();
    results.push({ name, ok: true });
  } catch (err) {
    results.push({ name, ok: false, err });
  }
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg || 'Assertion failed');
}

// Capture forwarded body from worker -> Power Automate fetch
let forwardedRequest = null;
const originalFetch = globalThis.fetch;
globalThis.fetch = async (request, options) => {
  // Support both fetch(url, options) and fetch(Request)
  const info = typeof request === 'string' ? { url: request } : { url: request.url };
  let body = null;
  if (options && options.body) {
    try { body = JSON.parse(options.body); } catch { body = options.body; }
  }
  forwardedRequest = { url: info.url, options: { ...options, body } };
  return new Response(JSON.stringify({ ok: true }), { status: 200, headers: { 'content-type': 'application/json' } });
};

// Resolve worker module path
const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const workerPath = path.resolve(__dirname, '../../cloudflare-worker/worker.js');
const workerMod = await import(url.pathToFileURL(workerPath));

async function testPreflight() {
  const req = new Request('https://example.com/anything', { method: 'OPTIONS' });
  const res = await workerMod.default.fetch(req, {}, {});
  expect('Preflight status', () => assert(res.status === 200, `Expected 200, got ${res.status}`));
  const origin = res.headers.get('Access-Control-Allow-Origin');
  expect('CORS allow origin header', () => assert(!!origin, 'Missing Access-Control-Allow-Origin'));
}

async function testDefaultGet() {
  const req = new Request('https://example.com/', { method: 'GET' });
  const res = await workerMod.default.fetch(req, {}, {});
  const text = await res.text();
  let json;
  try { json = JSON.parse(text); } catch { json = null; }
  expect('Default GET 200', () => assert(res.status === 200, `Expected 200, got ${res.status}`));
  expect('Default GET JSON', () => assert(json && json.endpoints, 'Expected JSON with endpoints'));
}

async function testSubmitTransform() {
  forwardedRequest = null;
  const raw = {
    invitationCode: 'ABCD1234',
    companyName: 'Test EPC Ltd',
    tradingName: 'Test EPC',
    companyRegNo: '12345678',
    vatNo: 'GB123',
    primaryContactName: 'Jane Doe',
    contactTitle: 'Director',
    primaryContactEmail: 'jane@example.com',
    primaryContactPhone: '+44 1234 567890',
    registeredOffice: '1 Test Street',
    services: ['Installation', 'Maintenance'],
    yearsTrading: '7',
    teamSize: '15',
    coverageRegion: ['North West', 'Midlands'],
    isoStandards: ['ISO 9001', 'ISO 14001'],
    actsAsPrincipalContractor: 'Yes',
    actsAsPrincipalDesigner: 'No',
    hasGDPRPolicy: 'Yes',
    hsqIncidents: '0',
    riddor: '0',
    notes: 'N/A',
    agreeToTerms: true,
    certifications: 'PAS 2035'
  };

  const req = new Request('https://example.com/submit-epc-application', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(raw),
  });

  const res = await workerMod.default.fetch(req, {}, {});
  const body = await res.json();
  expect('Submit status 200', () => assert(res.status === 200, `Expected 200, got ${res.status}`));
  expect('Submit success true', () => assert(body && body.success === true, 'Expected success true'));

  // Validate transform captured by stubbed fetch
  expect('Forwarded request captured', () => assert(!!forwardedRequest, 'No forwarded request captured'));
  const t = forwardedRequest?.options?.body;
  expect('Mapping: invitationCode', () => assert(t.invitationCode === 'ABCD1234', 'invitationCode mismatch'));
  expect('Mapping: companyName', () => assert(t.companyName === 'Test EPC Ltd', 'companyName mismatch'));
  expect('Mapping: registrationNumber', () => assert(t.registrationNumber === '12345678', 'registrationNumber mismatch'));
  expect('Mapping: email', () => assert(t.email === 'jane@example.com', 'email mismatch'));
  expect('Mapping: phone', () => assert(t.phone === '+44 1234 567890', 'phone mismatch'));
  expect('Mapping: address', () => assert(t.address === '1 Test Street', 'address mismatch'));
  expect('Mapping: services[]', () => assert(Array.isArray(t.services) && t.services.length === 2, 'services mapping'));
  expect('Mapping: yearsExperience', () => assert(t.yearsExperience === 7, 'yearsExperience mapping'));
  expect('Mapping: teamSize', () => assert(t.teamSize === 15, 'teamSize mapping'));
  expect('Mapping: coverage joined', () => assert(t.coverage === 'North West, Midlands', `coverage got ${t.coverage}`));
  expect('Mapping: isoStandards joined', () => assert(t.isoStandards.includes('ISO 9001'), 'isoStandards mapping'));
  expect('Mapping: flags', () => assert(t.actsAsPrincipalContractor === 'Yes' && t.actsAsPrincipalDesigner === 'No', 'flag mapping'));
  expect('Mapping: notes', () => assert(t.notes === 'N/A', 'notes mapping'));
  expect('Mapping: agreeToTerms', () => assert(t.agreeToTerms === true, 'agreeToTerms mapping'));
  expect('Meta: timestamp', () => assert(typeof t.timestamp === 'string', 'timestamp missing'));
  expect('Meta: source', () => assert(t.source === 'epc.saberrenewable.energy', 'source mapping'));
}

async function run() {
  await testPreflight();
  await testDefaultGet();
  await testSubmitTransform();

  // Restore fetch
  globalThis.fetch = originalFetch;

  // Report
  const passed = results.filter(r => r.ok).length;
  const failed = results.length - passed;
  console.log(`\nWorker Tests: ${passed} passed, ${failed} failed`);
  for (const r of results) {
    if (!r.ok) {
      console.error(`✗ ${r.name}: ${r.err?.message || r.err}`);
    } else {
      console.log(`✓ ${r.name}`);
    }
  }
  if (failed > 0) process.exit(1);
}

run();

