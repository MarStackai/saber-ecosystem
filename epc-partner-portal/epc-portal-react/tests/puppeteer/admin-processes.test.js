const puppeteer = require('puppeteer');
const config = require('./test-config');

describe('Admin Portal Tests', () => {
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

  describe('Admin Navigation', () => {
    test('Should navigate to admin dashboard', async () => {
      console.log('Testing: Navigate to admin dashboard');

      await page.goto(`${config.baseURL}/admin`, { waitUntil: 'networkidle2' });
      await page.waitForSelector('h1', { timeout: 10000 });

      const title = await page.$eval('h1', el => el.textContent);
      expect(title).toContain('Admin Dashboard');

      // Check if main stats are visible
      const statsVisible = await page.$$eval('.grid .rounded-lg', elements => elements.length > 0);
      expect(statsVisible).toBe(true);

      console.log('✓ Admin dashboard loaded successfully');
    });

    test('Should have working admin navigation', async () => {
      console.log('Testing: Admin navigation links');

      await page.goto(`${config.baseURL}/admin`, { waitUntil: 'networkidle2' });

      // Test Partners link
      const partnersLink = await page.$('a[href="/admin/partners"]');
      expect(partnersLink).not.toBeNull();

      await partnersLink.click();
      await page.waitForNavigation({ waitUntil: 'networkidle2' });

      const partnersUrl = page.url();
      expect(partnersUrl).toContain('/admin/partners');

      console.log('✓ Partners navigation working');

      // Test Tenders link
      await page.goto(`${config.baseURL}/admin`, { waitUntil: 'networkidle2' });
      const tendersLink = await page.$('a[href="/admin/tenders"]');
      expect(tendersLink).not.toBeNull();

      await tendersLink.click();
      await page.waitForNavigation({ waitUntil: 'networkidle2' });

      const tendersUrl = page.url();
      expect(tendersUrl).toContain('/admin/tenders');

      console.log('✓ Tenders navigation working');

      // Test Documents link
      await page.goto(`${config.baseURL}/admin`, { waitUntil: 'networkidle2' });
      const documentsLink = await page.$('a[href="/admin/documents"]');
      expect(documentsLink).not.toBeNull();

      await documentsLink.click();
      await page.waitForNavigation({ waitUntil: 'networkidle2' });

      const documentsUrl = page.url();
      expect(documentsUrl).toContain('/admin/documents');

      console.log('✓ Documents navigation working');
    });
  });

  describe('Partners Management', () => {
    test('Should display partners list', async () => {
      console.log('Testing: Partners list display');

      await page.goto(`${config.baseURL}/admin/partners`, { waitUntil: 'networkidle2' });

      // Check page title
      const title = await page.$eval('h1', el => el.textContent);
      expect(title).toContain('Partners');

      // Check if stats cards exist
      const statsCards = await page.$$('.grid .rounded-lg');
      expect(statsCards.length).toBeGreaterThan(0);

      // Check if table exists
      const table = await page.$('table');
      expect(table).not.toBeNull();

      console.log('✓ Partners list displayed');
    });

    test('Should navigate to partner applications', async () => {
      console.log('Testing: Partner applications page');

      await page.goto(`${config.baseURL}/admin/partners/applications`, { waitUntil: 'networkidle2' });

      const title = await page.$eval('h1', el => el.textContent);
      expect(title).toContain('Partner Applications');

      // Check for filter buttons
      const filterButtons = await page.$$('button');
      const hasFilters = filterButtons.length > 0;
      expect(hasFilters).toBe(true);

      console.log('✓ Partner applications page loaded');
    });

    test('Should navigate to approved partners', async () => {
      console.log('Testing: Approved partners page');

      await page.goto(`${config.baseURL}/admin/partners/approved`, { waitUntil: 'networkidle2' });

      const title = await page.$eval('h1', el => el.textContent);
      expect(title).toContain('Approved Partners');

      // Check for search input
      const searchInput = await page.$('input[placeholder*="Search"]');
      expect(searchInput).not.toBeNull();

      console.log('✓ Approved partners page loaded');
    });

    test('Should navigate to partner analytics', async () => {
      console.log('Testing: Partner analytics page');

      await page.goto(`${config.baseURL}/admin/partners/analytics`, { waitUntil: 'networkidle2' });

      const title = await page.$eval('h1', el => el.textContent);
      expect(title).toContain('Partner Analytics');

      // Check for time range selector
      const timeRangeButtons = await page.$$('.inline-flex button');
      expect(timeRangeButtons.length).toBeGreaterThan(0);

      console.log('✓ Partner analytics page loaded');
    });

    test('Should open partner details', async () => {
      console.log('Testing: Partner details page');

      await page.goto(`${config.baseURL}/admin/partners/1`, { waitUntil: 'networkidle2' });

      // Check if breadcrumb navigation exists
      const breadcrumb = await page.$('.text-slate-400');
      expect(breadcrumb).not.toBeNull();

      // Check for contact information section
      const contactSection = await page.$eval('h2', el => el.textContent);
      expect(contactSection).toContain('Contact Information');

      console.log('✓ Partner details page loaded');
    });

    test('Should check partner card buttons', async () => {
      console.log('Testing: Partner card buttons functionality');

      await page.goto(`${config.baseURL}/admin/partners/approved`, { waitUntil: 'networkidle2' });

      // Check View Projects button exists
      const viewProjectsLink = await page.$('a[href*="/projects"]');
      expect(viewProjectsLink).not.toBeNull();

      // Check Contact Partner button exists
      const contactLink = await page.$('a[href^="mailto:"]');
      expect(contactLink).not.toBeNull();

      console.log('✓ Partner card buttons present');
    });
  });

  describe('Tenders Management', () => {
    test('Should display tenders list', async () => {
      console.log('Testing: Tenders list display');

      await page.goto(`${config.baseURL}/admin/tenders`, { waitUntil: 'networkidle2' });

      // Check page title
      const titleElement = await page.$('h1');
      if (titleElement) {
        const title = await page.$eval('h1', el => el.textContent);
        console.log('  - Tender page title:', title);
      } else {
        console.log('  ! Tender page title not found');
      }

      // Check if Create Tender button exists
      const createButton = await page.$('a[href="/admin/tenders/new"]');
      if (createButton) {
        console.log('  ✓ Create Tender button found');
      } else {
        console.log('  ! Create Tender button not found');
      }

      // Check for tender items or loading state
      const tenderItems = await page.$$('.bg-slate-800\\/50');
      console.log(`  - Found ${tenderItems.length} tender items`);
    });

    test('Should navigate to tender analytics', async () => {
      console.log('Testing: Tender analytics page');

      await page.goto(`${config.baseURL}/admin/tenders/analytics`, { waitUntil: 'networkidle2' });

      const title = await page.$eval('h1', el => el.textContent);
      expect(title).toContain('Tender Analytics');

      // Check for overview cards
      const overviewCards = await page.$$('.grid .bg-slate-800\\/50');
      expect(overviewCards.length).toBeGreaterThan(0);

      console.log('✓ Tender analytics page loaded');
    });
  });

  describe('Documents Management', () => {
    test('Should display documents page', async () => {
      console.log('Testing: Documents page display');

      await page.goto(`${config.baseURL}/admin/documents`, { waitUntil: 'networkidle2' });

      const title = await page.$eval('h1', el => el.textContent);
      expect(title).toContain('Documents');

      // Check for search input
      const searchInput = await page.$('input[placeholder*="Search documents"]');
      expect(searchInput).not.toBeNull();

      // Check for upload button
      const uploadButton = await page.$eval('button', el => el.textContent);
      expect(uploadButton).toContain('Upload Document');

      // Check for category filters
      const categoryButtons = await page.$$('.flex-wrap button');
      expect(categoryButtons.length).toBeGreaterThan(0);

      console.log('✓ Documents page loaded with all elements');
    });

    test('Should display folder structure', async () => {
      console.log('Testing: Document folder structure');

      await page.goto(`${config.baseURL}/admin/documents`, { waitUntil: 'networkidle2' });

      // Check for folder structure section
      const folderSection = await page.$eval('h2', el => el.textContent);
      expect(folderSection).toContain('Document Organization');

      // Check for folder tree display
      const folderTree = await page.$('.font-mono');
      expect(folderTree).not.toBeNull();

      console.log('✓ Folder structure displayed');
    });
  });

  describe('Error Handling', () => {
    test('Should handle API errors gracefully', async () => {
      console.log('Testing: API error handling');

      // Test with invalid tender ID
      await page.goto(`${config.baseURL}/admin/tenders/invalid-id`, { waitUntil: 'networkidle2' });

      // Should either show error or redirect
      const currentUrl = page.url();
      console.log('  - Current URL after invalid ID:', currentUrl);

      // Check if any error message is displayed
      const errorMessages = await page.$$('.text-red-400, .text-red-500');
      console.log(`  - Found ${errorMessages.length} potential error messages`);
    });
  });
});

// Run tests
if (require.main === module) {
  const runner = async () => {
    console.log('\n🧪 Starting Admin Portal Tests...\n');
    console.log('================================\n');

    // Run Jest programmatically
    const jest = require('jest');
    await jest.run(['--testPathPattern=admin-processes']);
  };

  runner().catch(console.error);
}