const fs = require('fs');
const path = require('path');

/**
 * Test utilities for SharePoint integration testing
 */
class TestUtilities {
  constructor(page, config) {
    this.page = page;
    this.config = config;
  }

  /**
   * Create a new tender for testing
   */
  async createTestTender(tenderData = {}) {
    const defaultData = {
      projectName: 'Solar Farm Alpha - TEST',
      location: 'Test Location, UK',
      latitude: '51.5074',
      longitude: '-0.1278',
      projectType: 'Solar',
      description: 'Test tender for SharePoint integration testing'
    };

    const tender = { ...defaultData, ...tenderData };

    console.log(`📋 Creating test tender: ${tender.projectName}`);

    // Navigate to tender creation page
    await this.page.goto(`${this.config.baseURL}/admin/tenders/new`, {
      waitUntil: 'networkidle2'
    });

    // Fill tender form
    await this.page.type('#projectName', tender.projectName);
    await this.page.type('#location', tender.location);
    await this.page.type('#latitude', tender.latitude);
    await this.page.type('#longitude', tender.longitude);
    await this.page.select('#projectType', tender.projectType);
    await this.page.type('#description', tender.description);

    // Submit form
    await this.page.click('button[type="submit"]');

    // Wait for success message or redirect
    await this.page.waitForNavigation({ waitUntil: 'networkidle2' });

    // Extract tender ID from URL or page
    const url = this.page.url();
    const tenderId = this.extractTenderId(url);

    console.log(`✅ Tender created with ID: ${tenderId}`);

    return {
      ...tender,
      id: tenderId
    };
  }

  /**
   * Add partner to tender
   */
  async addPartnerToTender(tenderId, partnerData = {}) {
    const defaultPartner = {
      companyName: 'Green Energy Partners Ltd',
      email: 'contact@greenpartners.test',
      role: 'EPC Contractor'
    };

    const partner = { ...defaultPartner, ...partnerData };

    console.log(`👥 Adding partner: ${partner.companyName}`);

    // Navigate to tender partners page
    await this.page.goto(`${this.config.baseURL}/admin/tenders/${tenderId}?tab=partners`, {
      waitUntil: 'networkidle2'
    });

    // Click invite partners button
    await this.page.click('button:has-text("Invite Partner")');

    // Fill partner details
    await this.page.type('#partnerCompany', partner.companyName);
    await this.page.type('#partnerEmail', partner.email);
    await this.page.select('#partnerRole', partner.role);

    // Submit
    await this.page.click('button[type="submit"]');

    // Wait for success
    await this.page.waitForSelector('.success-message', { timeout: 5000 });

    console.log(`✅ Partner added: ${partner.companyName}`);

    return partner;
  }

  /**
   * Upload document to specific folder
   */
  async uploadDocument(tenderId, folderPath, documentPath) {
    console.log(`📤 Uploading to ${folderPath}: ${path.basename(documentPath)}`);

    // Navigate to documents tab
    await this.page.goto(`${this.config.baseURL}/admin/tenders/${tenderId}?tab=documents`, {
      waitUntil: 'networkidle2'
    });

    // Select folder from dropdown
    await this.page.select('#folderPath', folderPath);

    // Upload file
    const fileInput = await this.page.$('input[type="file"]');
    await fileInput.uploadFile(documentPath);

    // Wait for upload to complete
    await this.page.waitForSelector('.upload-success', { timeout: 10000 });

    console.log(`✅ Document uploaded: ${path.basename(documentPath)}`);

    return true;
  }

  /**
   * Verify document in SharePoint
   */
  async verifySharePointSync(tenderId, documentName) {
    console.log(`🔍 Verifying SharePoint sync for: ${documentName}`);

    // Make API call to check sync status
    const response = await this.page.evaluate(async (tenderId, documentName) => {
      const res = await fetch(`/api/admin/tender/${tenderId}/documents`);
      const data = await res.json();
      return data.documents.find(doc => doc.original_filename === documentName);
    }, tenderId, documentName);

    if (response && response.sync_status === 'synced') {
      console.log(`✅ Document synced to SharePoint: ${documentName}`);
      return true;
    } else {
      console.log(`❌ Document not synced: ${documentName}`);
      return false;
    }
  }

  /**
   * Verify folder structure
   */
  async verifyFolderStructure(tenderId, expectedFolders) {
    console.log('📁 Verifying folder structure...');

    const response = await this.page.evaluate(async (tenderId) => {
      const res = await fetch(`/api/admin/tender/${tenderId}/folder-structure`);
      return await res.json();
    }, tenderId);

    const missingFolders = expectedFolders.filter(
      folder => !response.folders.includes(folder)
    );

    if (missingFolders.length === 0) {
      console.log('✅ All folders created correctly');
      return true;
    } else {
      console.log('❌ Missing folders:', missingFolders);
      return false;
    }
  }

  /**
   * Test document versioning
   */
  async testDocumentVersioning(tenderId, folderPath, originalDoc, updatedDoc) {
    console.log('📝 Testing document versioning...');

    // Upload original
    await this.uploadDocument(tenderId, folderPath, originalDoc);

    // Get version 1 info
    const v1Info = await this.getDocumentInfo(tenderId, path.basename(originalDoc));
    console.log(`Version 1.0: ${v1Info.sharepoint_version}`);

    // Upload replacement
    await this.uploadDocument(tenderId, folderPath, updatedDoc);

    // Get version 2 info
    const v2Info = await this.getDocumentInfo(tenderId, path.basename(updatedDoc));
    console.log(`Version 2.0: ${v2Info.sharepoint_version}`);

    return v2Info.version_number === 2;
  }

  /**
   * Get document information
   */
  async getDocumentInfo(tenderId, documentName) {
    return await this.page.evaluate(async (tenderId, documentName) => {
      const res = await fetch(`/api/admin/tender/${tenderId}/documents`);
      const data = await res.json();
      return data.documents.find(doc => doc.original_filename === documentName);
    }, tenderId, documentName);
  }

  /**
   * Delete document
   */
  async deleteDocument(tenderId, documentName) {
    console.log(`🗑️ Deleting document: ${documentName}`);

    await this.page.goto(`${this.config.baseURL}/admin/tenders/${tenderId}?tab=documents`, {
      waitUntil: 'networkidle2'
    });

    // Find and click delete button for specific document
    await this.page.evaluate((documentName) => {
      const rows = Array.from(document.querySelectorAll('tr'));
      const row = rows.find(r => r.textContent.includes(documentName));
      if (row) {
        const deleteBtn = row.querySelector('button.delete-btn');
        if (deleteBtn) deleteBtn.click();
      }
    }, documentName);

    // Confirm deletion
    await this.page.waitForSelector('.confirm-dialog', { timeout: 3000 });
    await this.page.click('button.confirm-delete');

    await this.page.waitForSelector('.delete-success', { timeout: 5000 });
    console.log(`✅ Document deleted: ${documentName}`);

    return true;
  }

  /**
   * Clean up test data
   */
  async cleanupTestData(tenderId) {
    console.log('🧹 Cleaning up test data...');

    try {
      // Delete tender via API
      const response = await this.page.evaluate(async (tenderId) => {
        const res = await fetch(`/api/admin/tender/${tenderId}`, {
          method: 'DELETE'
        });
        return res.ok;
      }, tenderId);

      if (response) {
        console.log(`✅ Test tender deleted: ${tenderId}`);
      }
    } catch (error) {
      console.error('Failed to cleanup test data:', error);
    }
  }

  /**
   * Extract tender ID from URL
   */
  extractTenderId(url) {
    const match = url.match(/tenders\/(\d+)/);
    return match ? match[1] : null;
  }

  /**
   * Wait for element and return it
   */
  async waitForElement(selector, timeout = 5000) {
    await this.page.waitForSelector(selector, { timeout });
    return await this.page.$(selector);
  }

  /**
   * Take screenshot for debugging
   */
  async takeScreenshot(name) {
    const screenshotPath = path.join(__dirname, '..', 'screenshots', `${name}.png`);
    await this.page.screenshot({ path: screenshotPath, fullPage: true });
    console.log(`📸 Screenshot saved: ${screenshotPath}`);
  }

  /**
   * Check if SharePoint is accessible (mock or real)
   */
  async checkSharePointConnection() {
    console.log('🔗 Checking SharePoint connection...');

    const isConnected = await this.page.evaluate(async () => {
      try {
        const res = await fetch('/api/admin/sharepoint/status');
        const data = await res.json();
        return data.connected;
      } catch {
        return false;
      }
    });

    console.log(isConnected ? '✅ SharePoint connected' : '⚠️ SharePoint not connected (using mock)');
    return isConnected;
  }
}

/**
 * Expected folder structure for validation
 */
const EXPECTED_FOLDER_STRUCTURE = [
  'EPC Uploads',
  'EPC Uploads/01. Design',
  'EPC Uploads/02. Grid',
  'EPC Uploads/02. Grid/G99 Application',
  'EPC Uploads/02. Grid/G99 Offer',
  'EPC Uploads/03. Planning',
  'EPC Uploads/03. Planning/Planning Application',
  'EPC Uploads/03. Planning/Planning Decision',
  'EPC Uploads/04. Project Delivery',
  'EPC Uploads/04. Project Delivery/01. EPC Contract',
  'EPC Uploads/04. Project Delivery/02. O&M Contract',
  'EPC Uploads/04. Project Delivery/03. Final Design',
  'EPC Uploads/04. Project Delivery/04. Pre-construction Pack',
  'EPC Uploads/04. Project Delivery/05. EPC Invoices',
  'EPC Uploads/04. Project Delivery/06. Handover Pack',
  'EPC Uploads/05. Survey',
  'EPC Uploads/05. Survey/Site Survey',
  'EPC Uploads/05. Survey/Media'
];

/**
 * Document mapping for testing
 */
const DOCUMENT_FOLDER_MAPPING = {
  'design_spec.pdf': '01. Design',
  'g99_application.pdf': '02_grid_g99_app',
  'g99_offer.pdf': '02_grid_g99_offer',
  'planning_application.pdf': '03_planning_app',
  'planning_decision.pdf': '03_planning_decision',
  'epc_contract.docx': '04_pd_epc',
  'om_contract.docx': '04_pd_om',
  'final_design.pdf': '04_pd_final',
  'precon_pack.txt': '04_pd_precon',
  'invoice_001.txt': '04_pd_invoices',
  'handover_checklist.txt': '04_pd_handover',
  'site_survey.pdf': '05_survey_site',
  'site_photo.jpg': '05_survey_media'
};

module.exports = {
  TestUtilities,
  EXPECTED_FOLDER_STRUCTURE,
  DOCUMENT_FOLDER_MAPPING
};