const fs = require('fs');
const path = require('path');

// Directory for test documents
const DOCS_DIR = path.join(__dirname, 'documents');

// Ensure documents directory exists
if (!fs.existsSync(DOCS_DIR)) {
  fs.mkdirSync(DOCS_DIR, { recursive: true });
}

/**
 * Generate test documents for each folder in the SharePoint structure
 */
const generateTestDocuments = () => {
  console.log('🔨 Generating test documents...');

  const documents = [
    // 01. Design
    {
      filename: 'design_spec.pdf',
      folder: '01. Design',
      content: createPDFContent('Solar Farm Alpha - Design Specification', 'Technical design documentation for the solar installation including layout, electrical schematics, and component specifications.'),
      type: 'application/pdf'
    },

    // 02. Grid - G99 Application
    {
      filename: 'g99_application.pdf',
      folder: '02. Grid/G99 Application',
      content: createPDFContent('G99 Grid Connection Application', 'Application for grid connection under G99 regulations for Solar Farm Alpha project.'),
      type: 'application/pdf'
    },

    // 02. Grid - G99 Offer
    {
      filename: 'g99_offer.pdf',
      folder: '02. Grid/G99 Offer',
      content: createPDFContent('G99 Grid Connection Offer', 'Grid connection offer from DNO for Solar Farm Alpha - 10MW capacity approved.'),
      type: 'application/pdf'
    },

    // 03. Planning - Application
    {
      filename: 'planning_application.pdf',
      folder: '03. Planning/Planning Application',
      content: createPDFContent('Planning Application - Solar Farm Alpha', 'Full planning application submitted to local authority for 50-acre solar farm development.'),
      type: 'application/pdf'
    },

    // 03. Planning - Decision
    {
      filename: 'planning_decision.pdf',
      folder: '03. Planning/Planning Decision',
      content: createPDFContent('Planning Decision Notice', 'Planning permission GRANTED with conditions for Solar Farm Alpha development.'),
      type: 'application/pdf'
    },

    // 04. Project Delivery - EPC Contract
    {
      filename: 'epc_contract.docx',
      folder: '04. Project Delivery/01. EPC Contract',
      content: createWordContent('EPC Contract - Solar Farm Alpha', 'Engineering, Procurement, and Construction contract between Saber Renewables and Green Energy Partners Ltd.'),
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    },

    // 04. Project Delivery - O&M Contract
    {
      filename: 'om_contract.docx',
      folder: '04. Project Delivery/02. O&M Contract',
      content: createWordContent('Operations & Maintenance Contract', '25-year O&M agreement for Solar Farm Alpha including performance guarantees.'),
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    },

    // 04. Project Delivery - Final Design
    {
      filename: 'final_design.pdf',
      folder: '04. Project Delivery/03. Final Design',
      content: createPDFContent('Final Design Package', 'As-built drawings and final design documentation post construction changes.'),
      type: 'application/pdf'
    },

    // 04. Project Delivery - Pre-construction Pack
    {
      filename: 'precon_pack.txt',
      folder: '04. Project Delivery/04. Pre-construction Pack',
      content: 'Pre-Construction Information Pack\n\n- Site access arrangements\n- Health & Safety File\n- Environmental Management Plan\n- Traffic Management Plan\n- Emergency Procedures',
      type: 'text/plain'
    },

    // 04. Project Delivery - EPC Invoices
    {
      filename: 'invoice_001.txt',
      folder: '04. Project Delivery/05. EPC Invoices',
      content: createInvoiceContent('INV-2024-001', 'Milestone 1: Site Preparation Complete', '£500,000'),
      type: 'text/plain'
    },

    // 04. Project Delivery - Handover Pack
    {
      filename: 'handover_checklist.txt',
      folder: '04. Project Delivery/06. Handover Pack',
      content: 'Project Handover Documentation\n\n✓ As-built drawings\n✓ O&M manuals\n✓ Warranty documentation\n✓ Commissioning certificates\n✓ Grid compliance certificates\n✓ Safety file',
      type: 'text/plain'
    },

    // 05. Survey - Site Survey
    {
      filename: 'site_survey.pdf',
      folder: '05. Survey/Site Survey',
      content: createPDFContent('Topographical Site Survey', 'Complete topographical survey of the 50-acre site including boundaries, levels, and existing features.'),
      type: 'application/pdf'
    },

    // 05. Survey - Media
    {
      filename: 'site_photo.jpg',
      folder: '05. Survey/Media',
      content: createImagePlaceholder(),
      type: 'image/jpeg'
    },

    // Additional test document
    {
      filename: 'test_spreadsheet.csv',
      folder: '04. Project Delivery/05. EPC Invoices',
      content: 'Invoice Number,Date,Description,Amount\nINV-001,2024-01-15,Site Preparation,500000\nINV-002,2024-02-15,Foundation Works,750000\nINV-003,2024-03-15,Panel Installation,1200000',
      type: 'text/csv'
    }
  ];

  // Generate each document
  documents.forEach(doc => {
    const filePath = path.join(DOCS_DIR, doc.filename);

    if (typeof doc.content === 'string') {
      fs.writeFileSync(filePath, doc.content);
    } else {
      fs.writeFileSync(filePath, doc.content);
    }

    console.log(`✅ Generated: ${doc.filename} for ${doc.folder}`);
  });

  // Also create a metadata file for easy reference
  const metadata = documents.map(doc => ({
    filename: doc.filename,
    folder: doc.folder,
    type: doc.type,
    size: fs.statSync(path.join(DOCS_DIR, doc.filename)).size
  }));

  fs.writeFileSync(
    path.join(DOCS_DIR, 'test-documents-metadata.json'),
    JSON.stringify(metadata, null, 2)
  );

  console.log(`\n✨ Generated ${documents.length} test documents successfully!`);
  console.log(`📁 Documents saved in: ${DOCS_DIR}`);

  return metadata;
};

/**
 * Create a simple PDF-like text content
 */
function createPDFContent(title, description) {
  return `%PDF-1.4
%%Title: ${title}
%%Description: ${description}

This is a test PDF document for: ${title}

${description}

Document generated for testing SharePoint integration.
Generated at: ${new Date().toISOString()}

%%EOF`;
}

/**
 * Create a simple Word-like text content
 */
function createWordContent(title, description) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<document>
  <title>${title}</title>
  <body>
    <h1>${title}</h1>
    <p>${description}</p>
    <p>This is a test document generated for SharePoint integration testing.</p>
    <p>Generated at: ${new Date().toISOString()}</p>
  </body>
</document>`;
}

/**
 * Create invoice content
 */
function createInvoiceContent(invoiceNumber, description, amount) {
  return `INVOICE
=====================================
Invoice Number: ${invoiceNumber}
Date: ${new Date().toLocaleDateString()}
Project: Solar Farm Alpha

Description: ${description}
Amount: ${amount}

Payment Terms: Net 30 days
=====================================

This is a test invoice for SharePoint integration testing.`;
}

/**
 * Create a simple image placeholder (tiny valid JPEG)
 */
function createImagePlaceholder() {
  // Minimal valid JPEG file (1x1 pixel, red)
  const hex = 'ffd8ffe000104a46494600010101006000600000ffdb004300080606070605080707070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d0d1832211c213232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232ffc0001108000100010301220002110103110001ffc4001f0000010501010101010100000000000000000102030405060708090a0bffc400b5100002010303020403050504040000017d01020300041105122131410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a25262728292a3435363738393a434445464748494a535455565758595a636465666768696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000102030405060708090a0bffc400b51100020102040403040705040400010277000102031104052131061241510761711322328108144291a1b1c109233352f0156272d10a162434e125f11718191a262728292a35363738393a434445464748494a535455565758595a636465666768696a737475767778797a82838485868788898a92939495969798999aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00f1ff00ffd9';
  return Buffer.from(hex, 'hex');
}

// Export functions for use in tests
module.exports = {
  generateTestDocuments,
  DOCS_DIR
};

// Run if executed directly
if (require.main === module) {
  generateTestDocuments();
}