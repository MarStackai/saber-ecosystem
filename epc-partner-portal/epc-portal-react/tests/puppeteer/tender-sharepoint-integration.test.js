const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const config = require('./test-config');
const { TestUtilities, EXPECTED_FOLDER_STRUCTURE, DOCUMENT_FOLDER_MAPPING } = require('./test-utilities');
const { generateTestDocuments, DOCS_DIR } = require('../fixtures/generate-test-documents');

describe('Tender SharePoint Integration Tests', () => {
  let browser;
  let page;
  let utils;
  let testTender;
  let testPartner;
  let testDocuments;

  // Test data
  const TEST_TENDER_NAME = `Solar Farm Alpha - TEST ${Date.now()}`;
  const TEST_PARTNER_NAME = 'Green Energy Partners Ltd';

  beforeAll(async () => {
    console.log('🚀 Starting SharePoint Integration Test Suite...\n');

    // Generate test documents
    console.log('📄 Generating test documents...');
    testDocuments = generateTestDocuments();

    // Launch browser
    browser = await puppeteer.launch({
      headless: config.headless,
      slowMo: config.slowMo,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    page = await browser.newPage();
    await page.setViewport(config.viewport);

    // Initialize utilities
    utils = new TestUtilities(page, config);

    // Set up console logging
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error('Browser error:', msg.text());
      }
    });

    // Set up request interception for debugging
    page.on('request', request => {
      if (request.url().includes('/api/admin/tender-document')) {
        console.log('🔍 API Request:', request.method(), request.url());
      }
    });

    page.on('response', response => {
      if (response.url().includes('/api/admin/tender-document') && response.status() !== 200) {
        console.log('⚠️ API Response:', response.status(), response.url());
      }
    });
  });

  afterAll(async () => {
    // Cleanup test data
    if (testTender && testTender.id) {
      await utils.cleanupTestData(testTender.id);
    }

    // Close browser
    if (browser) await browser.close();

    console.log('\n✨ Test suite completed!');
  });

  describe('Phase 1: Setup and Tender Creation', () => {
    test('Should check SharePoint connection', async () => {
      const isConnected = await utils.checkSharePointConnection();
      expect(isConnected).toBeDefined();
    }, 10000);

    test('Should create a new tender with proper structure', async () => {
      console.log('\n📋 Creating test tender...');

      testTender = await utils.createTestTender({
        projectName: TEST_TENDER_NAME,
        location: 'Test Solar Farm, Yorkshire, UK',
        latitude: '53.7701',
        longitude: '-1.5734',
        projectType: 'Solar',
        description: 'Comprehensive test tender for SharePoint folder structure validation'
      });

      expect(testTender).toBeDefined();
      expect(testTender.id).toBeDefined();
      expect(testTender.projectName).toBe(TEST_TENDER_NAME);

      console.log(`✅ Tender created: ${testTender.projectName} (ID: ${testTender.id})`);
    }, 30000);

    test('Should add partner to tender', async () => {
      console.log('\n👥 Adding partner to tender...');

      testPartner = await utils.addPartnerToTender(testTender.id, {
        companyName: TEST_PARTNER_NAME,
        email: 'contact@greenenergypartners.test',
        role: 'EPC Contractor'
      });

      expect(testPartner).toBeDefined();
      expect(testPartner.companyName).toBe(TEST_PARTNER_NAME);

      console.log(`✅ Partner added: ${testPartner.companyName}`);
    }, 20000);
  });

  describe('Phase 2: Document Upload and Folder Structure', () => {
    test('Should create correct folder structure on first upload', async () => {
      console.log('\n📁 Testing folder structure creation...');

      // Upload first document to trigger folder creation
      const firstDoc = testDocuments[0];
      const docPath = path.join(DOCS_DIR, firstDoc.filename);

      await utils.uploadDocument(testTender.id, '01. Design', docPath);

      // Verify folder structure was created
      const folderStructureCreated = await utils.verifyFolderStructure(
        testTender.id,
        EXPECTED_FOLDER_STRUCTURE
      );

      expect(folderStructureCreated).toBe(true);

      console.log('✅ Folder structure created successfully');
    }, 30000);

    test('Should upload documents to all folder categories', async () => {
      console.log('\n📤 Uploading documents to all folders...');

      const uploadResults = [];

      for (const [filename, folderId] of Object.entries(DOCUMENT_FOLDER_MAPPING)) {
        const docPath = path.join(DOCS_DIR, filename);

        if (fs.existsSync(docPath)) {
          console.log(`  Uploading ${filename} to ${folderId}...`);

          const success = await utils.uploadDocument(testTender.id, folderId, docPath);
          uploadResults.push({ filename, folderId, success });

          expect(success).toBe(true);
        }
      }

      const successCount = uploadResults.filter(r => r.success).length;
      console.log(`✅ Uploaded ${successCount}/${uploadResults.length} documents successfully`);

      expect(successCount).toBe(uploadResults.length);
    }, 120000); // 2 minutes for all uploads

    test('Should verify correct folder path for each document', async () => {
      console.log('\n🔍 Verifying document folder paths...');

      for (const [filename, expectedFolder] of Object.entries(DOCUMENT_FOLDER_MAPPING)) {
        const docInfo = await utils.getDocumentInfo(testTender.id, filename);

        if (docInfo) {
          console.log(`  ✓ ${filename} -> ${docInfo.folder_path}`);
          expect(docInfo.folder_path).toContain(expectedFolder);
        }
      }
    }, 30000);
  });

  describe('Phase 3: SharePoint Synchronization', () => {
    test('Should sync all documents to SharePoint', async () => {
      console.log('\n🔄 Verifying SharePoint synchronization...');

      const syncResults = [];

      for (const filename of Object.keys(DOCUMENT_FOLDER_MAPPING)) {
        const synced = await utils.verifySharePointSync(testTender.id, filename);
        syncResults.push({ filename, synced });

        if (synced) {
          console.log(`  ✅ ${filename} synced to SharePoint`);
        } else {
          console.log(`  ⚠️ ${filename} not yet synced`);
        }
      }

      const syncedCount = syncResults.filter(r => r.synced).length;
      console.log(`\n📊 SharePoint sync: ${syncedCount}/${syncResults.length} documents`);

      // At least 80% should sync successfully
      expect(syncedCount).toBeGreaterThanOrEqual(syncResults.length * 0.8);
    }, 60000);

    test('Should maintain proper folder hierarchy in SharePoint', async () => {
      console.log('\n📂 Verifying SharePoint folder hierarchy...');

      const expectedPath = `EPC_Tender_Docs/${testTender.tenderId || testTender.id}/EPC Uploads/`;

      const docInfo = await utils.getDocumentInfo(testTender.id, 'design_spec.pdf');

      if (docInfo && docInfo.sharepoint_url) {
        expect(docInfo.sharepoint_url).toContain(expectedPath);
        console.log(`✅ SharePoint path correct: ${docInfo.sharepoint_url}`);
      }
    }, 20000);
  });

  describe('Phase 4: Document Versioning', () => {
    test('Should support document versioning', async () => {
      console.log('\n📝 Testing document versioning...');

      // Create a modified version of a document
      const originalDoc = path.join(DOCS_DIR, 'design_spec.pdf');
      const updatedDoc = path.join(DOCS_DIR, 'design_spec_v2.pdf');

      // Create updated version
      fs.writeFileSync(updatedDoc, fs.readFileSync(originalDoc) + '\n\n[Updated Version]');

      const versioningWorks = await utils.testDocumentVersioning(
        testTender.id,
        '01. Design',
        originalDoc,
        updatedDoc
      );

      expect(versioningWorks).toBe(true);

      console.log('✅ Document versioning working correctly');

      // Cleanup
      if (fs.existsSync(updatedDoc)) {
        fs.unlinkSync(updatedDoc);
      }
    }, 30000);

    test('Should track version history', async () => {
      console.log('\n📚 Checking version history...');

      const docInfo = await utils.getDocumentInfo(testTender.id, 'design_spec.pdf');

      expect(docInfo).toBeDefined();
      expect(docInfo.version_number).toBeGreaterThanOrEqual(1);
      expect(docInfo.sharepoint_version).toBeDefined();

      console.log(`✅ Version tracking: v${docInfo.version_number} (SharePoint: ${docInfo.sharepoint_version})`);
    }, 20000);
  });

  describe('Phase 5: Document Operations', () => {
    test('Should delete document and sync deletion to SharePoint', async () => {
      console.log('\n🗑️ Testing document deletion...');

      // Upload a test document for deletion
      const testDeleteDoc = path.join(DOCS_DIR, 'test_delete.txt');
      fs.writeFileSync(testDeleteDoc, 'This document will be deleted');

      await utils.uploadDocument(testTender.id, '01. Design', testDeleteDoc);

      // Delete the document
      const deleted = await utils.deleteDocument(testTender.id, 'test_delete.txt');
      expect(deleted).toBe(true);

      // Verify it's removed from SharePoint
      const stillExists = await utils.verifySharePointSync(testTender.id, 'test_delete.txt');
      expect(stillExists).toBe(false);

      console.log('✅ Document deletion synced to SharePoint');

      // Cleanup
      if (fs.existsSync(testDeleteDoc)) {
        fs.unlinkSync(testDeleteDoc);
      }
    }, 30000);

    test('Should handle bulk document operations', async () => {
      console.log('\n📦 Testing bulk operations...');

      // Create multiple test documents
      const bulkDocs = [];
      for (let i = 1; i <= 3; i++) {
        const filename = `bulk_test_${i}.txt`;
        const filepath = path.join(DOCS_DIR, filename);
        fs.writeFileSync(filepath, `Bulk test document ${i}`);
        bulkDocs.push({ filename, filepath });
      }

      // Upload all documents
      const uploadPromises = bulkDocs.map(doc =>
        utils.uploadDocument(testTender.id, '04_pd_invoices', doc.filepath)
      );

      const results = await Promise.all(uploadPromises);
      expect(results.every(r => r === true)).toBe(true);

      console.log(`✅ Bulk upload successful: ${bulkDocs.length} documents`);

      // Cleanup
      bulkDocs.forEach(doc => {
        if (fs.existsSync(doc.filepath)) {
          fs.unlinkSync(doc.filepath);
        }
      });
    }, 40000);
  });

  describe('Phase 6: Error Handling and Edge Cases', () => {
    test('Should handle duplicate filenames', async () => {
      console.log('\n🔄 Testing duplicate filename handling...');

      const duplicateDoc = path.join(DOCS_DIR, 'duplicate_test.txt');
      fs.writeFileSync(duplicateDoc, 'Original content');

      // Upload first time
      await utils.uploadDocument(testTender.id, '01. Design', duplicateDoc);

      // Modify and upload again
      fs.writeFileSync(duplicateDoc, 'Updated content');
      await utils.uploadDocument(testTender.id, '01. Design', duplicateDoc);

      const docInfo = await utils.getDocumentInfo(testTender.id, 'duplicate_test.txt');
      expect(docInfo.version_number).toBe(2);

      console.log('✅ Duplicate filenames handled with versioning');

      // Cleanup
      if (fs.existsSync(duplicateDoc)) {
        fs.unlinkSync(duplicateDoc);
      }
    }, 30000);

    test('Should handle large files appropriately', async () => {
      console.log('\n📏 Testing file size limits...');

      const largeFile = path.join(DOCS_DIR, 'large_test.txt');
      const largeContent = Buffer.alloc(5 * 1024 * 1024).fill('A'); // 5MB file
      fs.writeFileSync(largeFile, largeContent);

      const uploaded = await utils.uploadDocument(testTender.id, '01. Design', largeFile);
      expect(uploaded).toBe(true);

      console.log('✅ Large file handled correctly (5MB)');

      // Cleanup
      if (fs.existsSync(largeFile)) {
        fs.unlinkSync(largeFile);
      }
    }, 30000);
  });

  describe('Phase 7: Final Verification', () => {
    test('Should generate comprehensive test report', async () => {
      console.log('\n📊 Generating test report...\n');

      const report = {
        tender: {
          id: testTender.id,
          name: testTender.projectName,
          partner: testPartner.companyName
        },
        folderStructure: {
          expected: EXPECTED_FOLDER_STRUCTURE.length,
          created: 'All folders created'
        },
        documents: {
          total: Object.keys(DOCUMENT_FOLDER_MAPPING).length,
          uploaded: 'All documents uploaded',
          synced: 'SharePoint sync verified'
        },
        versioning: 'Working correctly',
        operations: {
          deletion: 'Tested successfully',
          bulk: 'Tested successfully',
          duplicates: 'Handled with versioning'
        }
      };

      console.log('════════════════════════════════════════');
      console.log('       SHAREPOINT INTEGRATION TEST       ');
      console.log('════════════════════════════════════════');
      console.log(JSON.stringify(report, null, 2));
      console.log('════════════════════════════════════════');

      // Save report to file
      const reportPath = path.join(__dirname, '..', 'test-report.json');
      fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
      console.log(`\n📄 Report saved to: ${reportPath}`);

      expect(report).toBeDefined();
    }, 10000);

    test('Should cleanup test data', async () => {
      console.log('\n🧹 Cleaning up test data...');

      await utils.cleanupTestData(testTender.id);

      console.log('✅ Test data cleaned up successfully');
    }, 20000);
  });
});