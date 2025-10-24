// Minimal local smoke tests for Pages Functions without network
// Run with: node epc-portal-react/tests/local/functions-smoke.mjs

import { onRequest as saveDraft } from '../../functions/api/save-draft.js'
import { onRequest as validateInvitation } from '../../functions/api/validate-invitation.js'

class FakeStmt {
  constructor(db, sql) {
    this.db = db
    this.sql = sql
    this.params = []
  }
  bind(...params) {
    this.params = params
    return this
  }
  async run() {
    // Handle INSERT/REPLACE patterns
    if (/INSERT OR REPLACE INTO draft_data/i.test(this.sql)) {
      const [invitationCode, formData, currentStep, lastSaved] = this.params
      this.db.draft_data.set(invitationCode, {
        form_data: JSON.stringify(formData),
        current_step: currentStep,
        last_saved: lastSaved,
      })
      return { success: true }
    }
    if (/INSERT OR REPLACE INTO invitations/i.test(this.sql)) {
      const [auth_code, title, company_name, contact_email, notes, status, created_at, updated_at] = this.params
      this.db.invitations.set(auth_code, {
        auth_code,
        title,
        company_name,
        contact_email,
        notes,
        status,
        created_at,
        updated_at,
      })
      return { success: true }
    }
    return { success: true }
  }
  async first() {
    // Handle SELECT patterns
    if (/FROM draft_data/i.test(this.sql)) {
      const [invitationCode] = this.params
      return this.db.draft_data.get(invitationCode) || null
    }
    if (/FROM invitations/i.test(this.sql)) {
      const [authCode] = this.params
      const row = this.db.invitations.get(authCode)
      if (row && row.status === 'active') return row
      return null
    }
    return null
  }
  async all() {
    return { results: [] }
  }
}

class FakeD1 {
  constructor() {
    this.invitations = new Map()
    this.draft_data = new Map()
  }
  prepare(sql) {
    return new FakeStmt(this, sql)
  }
}

function makeContext({ fn, method = 'GET', json, query } = {}) {
  const url = new URL('http://localhost' + (fn || '/'))
  if (query) {
    for (const [k, v] of Object.entries(query)) url.searchParams.set(k, v)
  }
  const init = { method, headers: {} }
  if (json) {
    init.headers['Content-Type'] = 'application/json'
    init.body = JSON.stringify(json)
  }
  const request = new Request(url.toString(), init)
  return { request, env: { epc_form_data: new FakeD1() } }
}

async function run() {
  console.log('▶ Running local functions smoke tests (no network)')

  // 1) validate-invitation via D1 fast path
  {
    const ctx = makeContext({ fn: '/api/validate-invitation', method: 'POST', json: { invitationCode: 'ABCD1234' } })
    // seed D1
    await ctx.env.epc_form_data
      .prepare('INSERT OR REPLACE INTO invitations (...) VALUES (?,?,?,?,?,?,?,?)')
      .bind('ABCD1234', 'Mr', 'Acme Ltd', 'ops@acme.tld', 'n/a', 'active', new Date().toISOString(), new Date().toISOString())
      .run()
    const res = await validateInvitation(ctx)
    const body = await res.json()
    console.log('validate-invitation (D1) →', res.status, body.valid, body.source)
    if (!(res.ok && body.valid && body.source === 'D1')) throw new Error('validate-invitation D1 path failed')
  }

  // 2) save-draft POST then GET
  {
    const ctx = makeContext({ fn: '/api/save-draft', method: 'POST', json: { invitationCode: 'TEST0001', formData: { companyName: 'ACME' }, currentStep: 2 } })
    let res = await saveDraft(ctx)
    let body = await res.json()
    console.log('save-draft POST →', res.status, body.success)
    if (!res.ok || !body.success) throw new Error('save-draft POST failed')

    const ctxGet = makeContext({ fn: '/api/save-draft', method: 'GET', query: { invitationCode: 'TEST0001' } })
    // reuse same D1 state
    ctxGet.env = ctx.env
    res = await saveDraft(ctxGet)
    body = await res.json()
    console.log('save-draft GET →', res.status, body.success, !!body.data)
    if (!res.ok || !body.success || !body.data) throw new Error('save-draft GET failed')
  }

  console.log('✅ All local function tests passed')
}

// Stub global fetch to avoid external calls during tests
globalThis.fetch = async (url, opts) => {
  return new Response(JSON.stringify({ ok: true }), { headers: { 'Content-Type': 'application/json' } })
}

run().catch((e) => {
  console.error('❌ Functions smoke test failed:', e)
  process.exit(1)
})

