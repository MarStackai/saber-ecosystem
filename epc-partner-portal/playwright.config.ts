import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for EPC Portal testing
 * Supports development, staging, and production environments
 */
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    // Base URL configuration based on environment
    baseURL: process.env.TEST_ENV === 'staging'
      ? 'https://staging-epc.saberrenewable.energy'
      : process.env.TEST_ENV === 'production'
      ? 'https://epc.saberrenewable.energy'
      : 'http://localhost:4200',

    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Run local development server before tests (only in development)
  webServer: process.env.TEST_ENV ? undefined : [
    {
      command: 'cd epc-portal-react && npm run dev',
      port: 4200,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npx wrangler dev --local --port 8787',
      port: 8787,
      reuseExistingServer: !process.env.CI,
    },
  ],
});