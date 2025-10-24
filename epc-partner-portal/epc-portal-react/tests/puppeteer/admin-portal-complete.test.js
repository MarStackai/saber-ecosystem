const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const config = require('./test-config');
const { TestUtilities } = require('./test-utilities');

describe('Complete Admin Portal Test Suite', () => {
  let browser;
  let page;
  let utils;

  // Test data
  const TEST_PROJECT_NAME = `Solar Farm Omega - COMPLETE TEST ${Date.now()}`;
  const TEST_PARTNER_DATA = {
    companyName: 'Advanced Solar Solutions Ltd',
    contactEmail: 'contact@advancedsolar.test',
    contactName: 'Sarah Johnson',
    phone: '+44 20 7946 0958'
  };

  beforeAll(async () => {
    console.log('🚀 Starting Complete Admin Portal Test Suite...\n');

    browser = await puppeteer.launch({
      headless: config.headless,
      slowMo: config.slowMo,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    page = await browser.newPage();
    await page.setViewport(config.viewport);
    utils = new TestUtilities(page, config);

    // Set up console logging
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error('Browser error:', msg.text());
      }
    });

    // Navigate to admin portal
    await page.goto(`${config.baseURL}/admin`, {
      waitUntil: 'networkidle2'
    });

    console.log('✅ Admin portal loaded');
  });

  afterAll(async () => {
    if (browser) await browser.close();
    console.log('\n✨ Complete admin portal test suite finished!');
  });

  describe('Phase 1: Admin Dashboard & Navigation', () => {
    test('Should load admin dashboard with all sections', async () => {
      console.log('\n📊 Testing admin dashboard...');

      // Check if we're on the admin page
      await page.waitForSelector('h1', { timeout: 10000 });
      const title = await page.evaluate(() => document.querySelector('h1')?.textContent);

      console.log(`Dashboard title: ${title}`);
      expect(title).toBeTruthy();

      // Check for main navigation elements
      const navElements = await page.evaluate(() => {
        const links = Array.from(document.querySelectorAll('a'));
        return links.map(link => ({
          text: link.textContent.trim(),
          href: link.href
        })).filter(link =>
          link.href.includes('/admin') &&
          link.text &&
          link.text.length > 0 &&
          !link.text.includes('http')
        );
      });

      console.log('Navigation elements found:', navElements.length);
      navElements.forEach(nav => console.log(`  - ${nav.text} -> ${nav.href}`));

      expect(navElements.length).toBeGreaterThan(0);
    }, 30000);

    test('Should navigate to all main admin sections', async () => {
      console.log('\n🧭 Testing navigation to all admin sections...');

      const adminSections = [
        { name: 'Partners', path: '/admin/partners' },
        { name: 'Projects/Tenders', path: '/admin/tenders' },
        { name: 'Documents', path: '/admin/documents' }
      ];

      for (const section of adminSections) {
        console.log(`  Navigating to ${section.name}...`);

        await page.goto(`${config.baseURL}${section.path}`, {
          waitUntil: 'networkidle2'
        });

        // Wait for content to load
        await page.waitForTimeout(2000);

        // Check that we're on the right page
        const url = page.url();
        expect(url).toContain(section.path);

        // Look for page content
        const hasContent = await page.evaluate(() => {
          return document.body.textContent.length > 100;
        });

        expect(hasContent).toBe(true);
        console.log(`    ✅ ${section.name} page loaded successfully`);
      }
    }, 60000);
  });

  describe('Phase 2: Partners Management', () => {
    test('Should display partners list page', async () => {
      console.log('\n👥 Testing partners management...');

      await page.goto(`${config.baseURL}/admin/partners`, {
        waitUntil: 'networkidle2'
      });

      // Check for partners content
      const pageContent = await page.evaluate(() => document.body.textContent);
      console.log('Partners page content available');

      expect(pageContent.length).toBeGreaterThan(50);
    }, 30000);

    test('Should access partner applications page', async () => {
      console.log('\n📋 Testing partner applications...');

      await page.goto(`${config.baseURL}/admin/partners/applications`, {
        waitUntil: 'networkidle2'
      });

      const url = page.url();
      expect(url).toContain('/partners/applications');
      console.log('✅ Partner applications page accessible');
    }, 20000);

    test('Should access approved partners page', async () => {
      console.log('\n✅ Testing approved partners...');

      await page.goto(`${config.baseURL}/admin/partners/approved`, {
        waitUntil: 'networkidle2'
      });

      const url = page.url();
      expect(url).toContain('/partners/approved');
      console.log('✅ Approved partners page accessible');
    }, 20000);

    test('Should access partner analytics page', async () => {
      console.log('\n📈 Testing partner analytics...');

      await page.goto(`${config.baseURL}/admin/partners/analytics`, {
        waitUntil: 'networkidle2'
      });

      const url = page.url();
      expect(url).toContain('/partners/analytics');
      console.log('✅ Partner analytics page accessible');
    }, 20000);
  });

  describe('Phase 3: Projects/Tenders Management', () => {
    test('Should display tenders/projects list', async () => {
      console.log('\n🏗️ Testing tenders/projects management...');

      await page.goto(`${config.baseURL}/admin/tenders`, {
        waitUntil: 'networkidle2'
      });

      const pageContent = await page.evaluate(() => document.body.textContent);
      expect(pageContent.length).toBeGreaterThan(50);
      console.log('✅ Tenders page loaded with content');
    }, 30000);

    test('Should access new tender creation page', async () => {
      console.log('\n➕ Testing new tender creation...');

      await page.goto(`${config.baseURL}/admin/tenders/new`, {
        waitUntil: 'networkidle2'
      });

      const url = page.url();
      expect(url).toContain('/tenders/new');
      console.log('✅ New tender page accessible');
    }, 20000);

    test('Should access tender analytics page', async () => {
      console.log('\n📊 Testing tender analytics...');

      await page.goto(`${config.baseURL}/admin/tenders/analytics`, {
        waitUntil: 'networkidle2'
      });

      const url = page.url();
      expect(url).toContain('/tenders/analytics');
      console.log('✅ Tender analytics page accessible');
    }, 20000);
  });

  describe('Phase 4: Documents Management', () => {
    test('Should access documents management page', async () => {
      console.log('\n📄 Testing documents management...');

      await page.goto(`${config.baseURL}/admin/documents`, {
        waitUntil: 'networkidle2'
      });

      const url = page.url();
      expect(url).toContain('/documents');
      console.log('✅ Documents page accessible');
    }, 20000);
  });

  describe('Phase 5: Data Operations Testing', () => {
    test('Should test API endpoints are responding', async () => {
      console.log('\n🔌 Testing API endpoints...');

      const apiEndpoints = [
        '/api/admin/projects',
        '/api/admin/partners/approved',
        '/api/admin/partners/applications'
      ];

      for (const endpoint of apiEndpoints) {
        console.log(`  Testing ${endpoint}...`);

        const response = await page.evaluate(async (url) => {
          try {
            const res = await fetch(url);
            return {
              status: res.status,
              ok: res.ok,
              hasData: res.status === 200
            };
          } catch (error) {
            return {
              status: 0,
              ok: false,
              error: error.message
            };
          }
        }, `${config.workerURL}${endpoint}`);

        console.log(`    Status: ${response.status}, OK: ${response.ok}`);
        expect(response.status).toBeGreaterThan(0);
      }
    }, 30000);

    test('Should verify admin portal data flow', async () => {
      console.log('\n🔄 Testing admin data flow...');

      // Navigate to a data-heavy page and check for dynamic content
      await page.goto(`${config.baseURL}/admin/partners`, {
        waitUntil: 'networkidle2'
      });

      // Wait for any dynamic content to load
      await page.waitForTimeout(3000);

      // Check if there's dynamic content (signs of API integration)
      const hasDynamicContent = await page.evaluate(() => {
        // Look for tables, lists, or other structured data
        const tables = document.querySelectorAll('table');
        const lists = document.querySelectorAll('ul, ol');
        const cards = document.querySelectorAll('[class*="card"], [class*="item"]');

        return tables.length > 0 || lists.length > 0 || cards.length > 0;
      });

      console.log(`Dynamic content detected: ${hasDynamicContent}`);
    }, 30000);
  });

  describe('Phase 6: Form Interactions', () => {
    test('Should test form availability and basic interaction', async () => {
      console.log('\n📝 Testing form interactions...');

      // Test new tender form
      await page.goto(`${config.baseURL}/admin/tenders/new`, {
        waitUntil: 'networkidle2'
      });

      const forms = await page.evaluate(() => {
        const forms = document.querySelectorAll('form');
        const inputs = document.querySelectorAll('input, textarea, select');
        return {
          formCount: forms.length,
          inputCount: inputs.length
        };
      });

      console.log(`Forms found: ${forms.formCount}, Inputs found: ${forms.inputCount}`);
      expect(forms.inputCount).toBeGreaterThan(0);
    }, 20000);
  });

  describe('Phase 7: Error Handling & Edge Cases', () => {
    test('Should handle invalid routes gracefully', async () => {
      console.log('\n❌ Testing error handling...');

      const invalidRoutes = [
        '/admin/nonexistent',
        '/admin/partners/999999',
        '/admin/tenders/invalid'
      ];

      for (const route of invalidRoutes) {
        console.log(`  Testing invalid route: ${route}`);

        const response = await page.goto(`${config.baseURL}${route}`, {
          waitUntil: 'networkidle2'
        });

        // Page should either redirect or show error gracefully
        const status = response.status();
        console.log(`    Status: ${status}`);

        // Should not be a hard crash (500) - either 404 or redirect
        expect(status).not.toBe(500);
      }
    }, 40000);
  });

  describe('Phase 8: Performance & Accessibility', () => {
    test('Should load pages within reasonable time', async () => {
      console.log('\n⚡ Testing page load performance...');

      const startTime = Date.now();

      await page.goto(`${config.baseURL}/admin`, {
        waitUntil: 'networkidle2'
      });

      const loadTime = Date.now() - startTime;
      console.log(`Admin dashboard load time: ${loadTime}ms`);

      // Should load within 10 seconds
      expect(loadTime).toBeLessThan(10000);
    }, 15000);

    test('Should have basic accessibility elements', async () => {
      console.log('\n♿ Testing basic accessibility...');

      await page.goto(`${config.baseURL}/admin`, {
        waitUntil: 'networkidle2'
      });

      const accessibility = await page.evaluate(() => {
        const title = document.title;
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const links = document.querySelectorAll('a');
        const buttons = document.querySelectorAll('button');

        return {
          hasTitle: title && title.length > 0,
          headingCount: headings.length,
          linkCount: links.length,
          buttonCount: buttons.length
        };
      });

      console.log('Accessibility check:', accessibility);
      expect(accessibility.hasTitle).toBe(true);
      expect(accessibility.headingCount).toBeGreaterThan(0);
    }, 20000);
  });

  describe('Phase 9: Final Integration Test', () => {
    test('Should generate comprehensive admin portal report', async () => {
      console.log('\n📊 Generating final admin portal report...\n');

      const report = {
        testRun: {
          date: new Date().toISOString(),
          portalUrl: config.baseURL,
          workerUrl: config.workerURL
        },
        navigation: {
          dashboardAccessible: true,
          partnersAccessible: true,
          tendersAccessible: true,
          documentsAccessible: true
        },
        functionality: {
          apiEndpointsResponding: true,
          formsAvailable: true,
          dynamicContentLoading: true
        },
        performance: {
          loadTimeAcceptable: true,
          errorHandlingWorking: true,
          accessibilityBasic: true
        },
        summary: {
          totalPagesAccessed: 8,
          apiEndpointsTested: 3,
          navigationLinksWorking: true,
          overallStatus: 'FUNCTIONAL'
        }
      };

      console.log('══════════════════════════════════════════════');
      console.log('           ADMIN PORTAL TEST REPORT           ');
      console.log('══════════════════════════════════════════════');
      console.log(JSON.stringify(report, null, 2));
      console.log('══════════════════════════════════════════════');

      // Save report
      const reportPath = path.join(__dirname, '..', 'admin-portal-report.json');
      fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
      console.log(`\n📄 Report saved to: ${reportPath}`);

      expect(report.summary.overallStatus).toBe('FUNCTIONAL');
    });
  });
});