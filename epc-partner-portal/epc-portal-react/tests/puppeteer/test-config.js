// Puppeteer Test Configuration
module.exports = {
  baseURL: 'http://localhost:4200',
  workerURL: 'http://localhost:8787',
  timeout: 30000,
  headless: false, // Set to true for CI/CD
  slowMo: 50, // Slow down by 50ms to see what's happening

  // Test credentials
  testInvitationCodes: ['TEST001', 'TEST2024', 'DEMO2024'],

  // Admin test user
  adminUser: {
    email: 'admin@saberrenewables.com',
    password: 'test-password'
  },

  // Test partner data
  testPartner: {
    companyName: 'Test Solar Solutions Ltd',
    contactName: 'John Test',
    email: 'test@solarsolutions.com',
    phone: '+44 20 1234 5678'
  },

  // Viewport settings
  viewport: {
    width: 1920,
    height: 1080
  }
}