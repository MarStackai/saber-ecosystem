import { test, expect } from '@playwright/test'

test.describe('UI Apply (mocked API)', () => {
  test('validates and redirects with mocked API', async ({ page }) => {
    await page.route('**/api/validate-invitation', async (route) => {
      const body = JSON.stringify({
        valid: true,
        invitation: { code: 'ABCD1234', companyName: 'Acme Ltd', contactEmail: 'ops@acme.tld' },
        source: 'mock',
      })
      await route.fulfill({ status: 200, contentType: 'application/json', body })
    })

    await page.goto('/apply?invitationCode=ABCD1234')
    await page.waitForURL(/\/form\?invitationCode=ABCD1234/, { timeout: 10000 })
    await expect(page.locator('text=Company Information')).toBeVisible()
    await expect(page.locator('input[name="companyName"]').first()).toBeVisible()
  })
})

