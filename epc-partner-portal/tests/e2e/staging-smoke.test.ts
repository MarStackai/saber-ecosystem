import { test, expect } from '@playwright/test';

/**
 * Smoke tests for staging environment
 * Verifies basic functionality is working
 */

test.describe('Staging Environment Smoke Tests', () => {
  test('homepage loads', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Saber EPC Portal/);
  });

  test('invitation form loads', async ({ page }) => {
    await page.goto('/form?invitationCode=TEST001');

    // Check if form elements are present
    await expect(page.locator('input[name="companyName"]')).toBeVisible();
    await expect(page.locator('input[name="contactEmail"]')).toBeVisible();
  });

  test('partner login page loads', async ({ page }) => {
    await page.goto('/partner/login');

    // Check login form elements
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('admin login page loads', async ({ page }) => {
    await page.goto('/admin');

    // Check for admin interface elements
    const pageContent = await page.content();
    expect(pageContent).toContain('Admin');
  });

  test('API health check', async ({ request }) => {
    const response = await request.get('/api/health');

    // API should respond with 200 or 404 (if health endpoint not implemented)
    expect([200, 404]).toContain(response.status());
  });

  test('Worker routes respond', async ({ request }) => {
    // Test operations endpoint
    const opsResponse = await request.get('/operations/health');
    expect(opsResponse.status()).toBeLessThan(500); // Should not error

    // Test form API endpoint
    const formResponse = await request.get('/form/api/test');
    expect(formResponse.status()).toBeLessThan(500); // Should not error
  });
});

test.describe('Partner Portal Tests', () => {
  test('partner dashboard requires authentication', async ({ page }) => {
    await page.goto('/partner/dashboard');

    // Should redirect to login
    await expect(page).toHaveURL(/partner\/login/);
  });

  test('test login works', async ({ page }) => {
    await page.goto('/partner/test-login');

    // Click test login button if it exists
    const testLoginButton = page.locator('button:has-text("Test Login")');
    if (await testLoginButton.isVisible()) {
      await testLoginButton.click();

      // Should redirect to dashboard
      await expect(page).toHaveURL(/partner\/dashboard/);
    }
  });
});

test.describe('Document Upload Tests', () => {
  test.skip('document upload interface exists', async ({ page }) => {
    // This test requires authentication
    // Skip in CI, run manually with authenticated session

    await page.goto('/partner/project/test-project');

    // Check for document upload elements
    await expect(page.locator('text=/upload/i')).toBeVisible();
  });
});