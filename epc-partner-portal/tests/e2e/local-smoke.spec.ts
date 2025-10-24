import { test, expect } from '@playwright/test'

test.describe('Local Smoke', () => {
  test.beforeAll(async ({ request }) => {
    await request.post('/api/sync-invitation', {
      data: {
        AuthCode: 'ABCD1234',
        Title: 'Mr',
        CompanyName: 'Acme Ltd',
        ContactEmail: 'ops@acme.tld',
        Notes: 'seeded by test',
      },
      headers: { 'Content-Type': 'application/json' },
    })
  })
  test('home loads', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/\//)
    await expect(page.locator('text=Infinite Power In Partnership')).toBeVisible()
  })

  test('apply validates and redirects', async ({ page }) => {
    // Seed known code scenario: test assumes D1 has ABCD1234 (see README or seed step)
    await page.goto('/apply?invitationCode=ABCD1234')
    // auto-redirect on valid code
    await page.waitForURL(/\/form\?invitationCode=ABCD1234/, { timeout: 10000 })
    await expect(page.locator('text=Company Information')).toBeVisible()
    await expect(page.locator('input[name="companyName"]')).toBeVisible()
  })

  test('validate-invitation API responds', async ({ request }) => {
    const res = await request.post('/api/validate-invitation', {
      data: { invitationCode: 'ABCD1234' },
      headers: { 'Content-Type': 'application/json' },
    })
    expect(res.ok()).toBeTruthy()
    const body = await res.json()
    expect(body.valid).toBeTruthy()
  })
})
