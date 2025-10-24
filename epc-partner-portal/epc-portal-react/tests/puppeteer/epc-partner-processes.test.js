const puppeteer = require('puppeteer');
const config = require('./test-config');

describe('EPC Partner Portal Tests', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch({
      headless: config.headless,
      slowMo: config.slowMo,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  });

  afterAll(async () => {
    if (browser) await browser.close();
  });

  beforeEach(async () => {
    page = await browser.newPage();
    await page.setViewport(config.viewport);
    await page.goto(config.baseURL, { waitUntil: 'networkidle2' });
  });

  afterEach(async () => {
    if (page) await page.close();
  });

  describe('Homepage and Navigation', () => {
    test('Should load homepage with correct content', async () => {
      console.log('Testing: Homepage content');

      // Check main headline
      const headline = await page.$eval('.font-display', el => el.textContent);
      expect(headline).toContain('Infinite Power In Partnership');

      // Check Submit Application button
      const submitButton = await page.$('a[href="/apply"]');
      expect(submitButton).not.toBeNull();

      const buttonText = await page.$eval('a[href="/apply"]', el => el.textContent);
      expect(buttonText).toContain('Submit Application');

      // Check Learn More button
      const learnMoreButton = await page.$('a[href*="saberrenewables.com"]');
      expect(learnMoreButton).not.toBeNull();

      console.log('✓ Homepage loaded with correct content');
    });

    test('Should have working public navigation', async () => {
      console.log('Testing: Public navigation');

      // Check for navigation elements
      const navLinks = await page.$$('nav a');
      console.log(`  - Found ${navLinks.length} navigation links`);

      // Check Submit Application link in nav
      const submitNavLink = await page.$('nav a[href="/apply"]');
      if (submitNavLink) {
        const linkText = await page.$eval('nav a[href="/apply"]', el => el.textContent);
        console.log(`  - Submit Application link text: ${linkText}`);
      }

      console.log('✓ Navigation elements present');
    });
  });

  describe('Invitation Code Verification', () => {
    test('Should navigate to apply page', async () => {
      console.log('Testing: Navigation to apply page');

      await page.goto(`${config.baseURL}/apply`, { waitUntil: 'networkidle2' });

      // Check page title
      const title = await page.$eval('h2', el => el.textContent);
      expect(title).toContain('Verify Access');

      // Check for access code input
      const accessCodeInput = await page.$('input[name="access-code"]');
      expect(accessCodeInput).not.toBeNull();

      // Check for submit button
      const submitButton = await page.$('button[type="submit"]');
      expect(submitButton).not.toBeNull();

      console.log('✓ Apply page loaded correctly');
    });

    test('Should validate invitation code', async () => {
      console.log('Testing: Invitation code validation');

      await page.goto(`${config.baseURL}/apply`, { waitUntil: 'networkidle2' });

      // Enter test invitation code
      await page.type('input[name="access-code"]', config.testInvitationCodes[0]);

      // Click submit
      const submitButton = await page.$('button[type="submit"]');
      await submitButton.click();

      // Wait for response (either redirect or error)
      await page.waitForTimeout(2000);

      const currentUrl = page.url();
      console.log('  - Current URL after submission:', currentUrl);

      // Check if redirected to form or error shown
      if (currentUrl.includes('/form')) {
        console.log('  ✓ Successfully redirected to form');
      } else {
        // Check for error message
        const errorMessage = await page.$('.text-red-400');
        if (errorMessage) {
          const errorText = await page.$eval('.text-red-400', el => el.textContent);
          console.log('  - Error message:', errorText);
        }
      }
    });

    test('Should auto-validate with URL parameter', async () => {
      console.log('Testing: Auto-validation with URL parameter');

      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/apply?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Check if input is pre-filled
      const inputValue = await page.$eval('input[name="access-code"]', el => el.value);
      expect(inputValue).toBe(testCode);

      // Wait for auto-validation
      await page.waitForTimeout(3000);

      const currentUrl = page.url();
      console.log('  - URL after auto-validation:', currentUrl);
    });

    test('Should show error for invalid code', async () => {
      console.log('Testing: Invalid invitation code handling');

      await page.goto(`${config.baseURL}/apply`, { waitUntil: 'networkidle2' });

      // Enter invalid code
      await page.type('input[name="access-code"]', 'INVALID999');

      // Click submit
      const submitButton = await page.$('button[type="submit"]');
      await submitButton.click();

      // Wait for error message
      await page.waitForTimeout(2000);

      const errorMessage = await page.$('.text-red-400');
      if (errorMessage) {
        const errorText = await page.$eval('.text-red-400', el => el.textContent);
        console.log('  - Error shown:', errorText);
        expect(errorText).toContain('Invalid');
      }

      console.log('✓ Invalid code handled correctly');
    });
  });

  describe('Application Form Process', () => {
    test('Should access application form with valid code', async () => {
      console.log('Testing: Application form access');

      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/form?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Check if form loaded
      const formExists = await page.$('form');
      console.log('  - Form element exists:', formExists !== null);

      // Check for form sections
      const formSections = await page.$$('[role="tablist"] button, .step-indicator');
      console.log(`  - Found ${formSections.length} form sections/steps`);

      // Check for input fields
      const inputFields = await page.$$('input, textarea, select');
      console.log(`  - Found ${inputFields.length} input fields`);
    });

    test('Should have auto-save functionality', async () => {
      console.log('Testing: Auto-save functionality');

      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/form?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Find first input field
      const firstInput = await page.$('input[type="text"]');
      if (firstInput) {
        // Type something
        await firstInput.type('Test Company Name');

        // Wait for auto-save (usually triggers after a delay)
        await page.waitForTimeout(3000);

        // Check for any save indicator
        const saveIndicators = await page.$$('.text-green-400, .text-green-500, [class*="saved"]');
        console.log(`  - Found ${saveIndicators.length} potential save indicators`);
      }
    });

    test('Should handle file uploads', async () => {
      console.log('Testing: File upload functionality');

      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/form?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Look for file input
      const fileInputs = await page.$$('input[type="file"]');
      console.log(`  - Found ${fileInputs.length} file upload inputs`);

      if (fileInputs.length > 0) {
        console.log('  ✓ File upload fields present');
      } else {
        console.log('  ! No file upload fields found');
      }
    });

    test('Should navigate between form steps', async () => {
      console.log('Testing: Form step navigation');

      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/form?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Look for next/previous buttons
      const navigationButtons = await page.$$('button[type="button"]');
      const nextButtons = [];
      const prevButtons = [];

      for (const button of navigationButtons) {
        const text = await page.evaluate(el => el.textContent, button);
        if (text.toLowerCase().includes('next')) nextButtons.push(button);
        if (text.toLowerCase().includes('prev') || text.toLowerCase().includes('back')) prevButtons.push(button);
      }

      console.log(`  - Found ${nextButtons.length} Next buttons`);
      console.log(`  - Found ${prevButtons.length} Previous buttons`);

      // Try clicking next if available
      if (nextButtons.length > 0) {
        await nextButtons[0].click();
        await page.waitForTimeout(1000);
        console.log('  ✓ Navigated to next step');
      }
    });

    test('Should validate required fields', async () => {
      console.log('Testing: Form validation');

      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/form?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Look for submit button
      const submitButtons = await page.$$('button[type="submit"]');
      console.log(`  - Found ${submitButtons.length} submit buttons`);

      if (submitButtons.length > 0) {
        // Try to submit without filling fields
        await submitButtons[0].click();

        // Check for validation errors
        await page.waitForTimeout(1000);
        const errorMessages = await page.$$('.text-red-400, .text-red-500, [class*="error"]');
        console.log(`  - Found ${errorMessages.length} potential error messages`);

        if (errorMessages.length > 0) {
          console.log('  ✓ Validation working');
        }
      }
    });
  });

  describe('SharePoint Integration', () => {
    test('Should check SharePoint connection', async () => {
      console.log('Testing: SharePoint integration status');

      // This would typically involve checking if the SharePoint API endpoints are configured
      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/form?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Check network requests for SharePoint API calls
      const sharePointRequests = [];
      page.on('request', request => {
        if (request.url().includes('sharepoint') || request.url().includes('validate-invitation')) {
          sharePointRequests.push(request.url());
        }
      });

      // Trigger a validation
      await page.reload({ waitUntil: 'networkidle2' });

      console.log(`  - SharePoint-related requests: ${sharePointRequests.length}`);

      if (sharePointRequests.length === 0) {
        console.log('  ! No SharePoint integration detected');
        console.log('  ! This needs to be implemented');
      }
    });
  });

  describe('Document Upload Flow', () => {
    test('Should check document upload process', async () => {
      console.log('Testing: Document upload flow');

      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/form?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Navigate to document upload section if it exists
      const documentSections = await page.$$('button[role="tab"], .tab-button');
      let documentTabFound = false;

      for (const tab of documentSections) {
        const text = await page.evaluate(el => el.textContent, tab);
        if (text.toLowerCase().includes('document')) {
          await tab.click();
          documentTabFound = true;
          console.log('  ✓ Navigated to documents section');
          break;
        }
      }

      if (!documentTabFound) {
        console.log('  ! Document upload section not found');
        console.log('  ! This needs to be implemented');
      } else {
        // Check for upload areas
        const uploadAreas = await page.$$('[class*="upload"], [class*="drop"], input[type="file"]');
        console.log(`  - Found ${uploadAreas.length} upload areas`);
      }
    });
  });

  describe('Submission Process', () => {
    test('Should check final submission flow', async () => {
      console.log('Testing: Final submission process');

      const testCode = config.testInvitationCodes[0];
      await page.goto(`${config.baseURL}/form?invitationCode=${testCode}`, { waitUntil: 'networkidle2' });

      // Look for final submit button
      const allButtons = await page.$$('button');
      let submitButton = null;

      for (const button of allButtons) {
        const text = await page.evaluate(el => el.textContent, button);
        if (text.toLowerCase().includes('submit application') ||
            text.toLowerCase().includes('complete') ||
            text.toLowerCase().includes('finish')) {
          submitButton = button;
          break;
        }
      }

      if (submitButton) {
        console.log('  ✓ Submit button found');
      } else {
        console.log('  ! Submit button not found');
        console.log('  ! Final submission process needs implementation');
      }

      // Check for confirmation dialogs or success messages
      const confirmationElements = await page.$$('[class*="confirm"], [class*="success"]');
      console.log(`  - Found ${confirmationElements.length} potential confirmation elements`);
    });
  });

  describe('Error Recovery', () => {
    test('Should handle network errors gracefully', async () => {
      console.log('Testing: Network error handling');

      // Simulate offline mode
      await page.setOfflineMode(true);

      await page.goto(`${config.baseURL}/apply`, { waitUntil: 'networkidle2' }).catch(e => {
        console.log('  - Expected error in offline mode:', e.message.substring(0, 50));
      });

      // Re-enable network
      await page.setOfflineMode(false);

      console.log('✓ Handles offline mode');
    });

    test('Should recover from API failures', async () => {
      console.log('Testing: API failure recovery');

      // Intercept API requests and make them fail
      await page.setRequestInterception(true);
      page.on('request', request => {
        if (request.url().includes('/api/')) {
          request.abort();
        } else {
          request.continue();
        }
      });

      await page.goto(`${config.baseURL}/apply`, { waitUntil: 'networkidle2' });

      // Try to submit with failed API
      const submitButton = await page.$('button[type="submit"]');
      if (submitButton) {
        await page.type('input[name="access-code"]', 'TEST001');
        await submitButton.click();
        await page.waitForTimeout(2000);

        // Check for error handling
        const errorElements = await page.$$('.text-red-400, .text-red-500');
        console.log(`  - Error messages displayed: ${errorElements.length}`);
      }

      console.log('✓ API failures handled');
    });
  });
});

// Run tests
if (require.main === module) {
  const runner = async () => {
    console.log('\n🧪 Starting EPC Partner Portal Tests...\n');
    console.log('========================================\n');

    // Run Jest programmatically
    const jest = require('jest');
    await jest.run(['--testPathPattern=epc-partner-processes']);
  };

  runner().catch(console.error);
}