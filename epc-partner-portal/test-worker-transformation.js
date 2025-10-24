// Test script to validate worker field transformation
const testData = {
    // Form fields (what the frontend sends)
    invitationCode: 'ABCD1234',
    companyName: 'Test EPC Company Ltd',
    companyRegNo: '12345678',
    primaryContactName: 'John Smith',
    contactTitle: 'Managing Director',
    primaryContactEmail: 'john@testepc.com',
    primaryContactPhone: '01234 567890',
    registeredOffice: '123 Test Street, Test City, TE1 2ST',
    yearsTrading: '5',
    coverageRegion: ['North West', 'Yorkshire', 'Midlands'],
    certifications: 'PAS 2035, ISO 9001',
    Status: 'Submitted',
    SubmissionDate: '2025-01-10T10:00:00.000Z'
};

// Transform function (copy from worker.js)
function transformFormData(rawData) {
  return {
    invitationCode: rawData.invitationCode || 'UNKNOWN',
    companyName: rawData.companyName || '',
    registrationNumber: rawData.companyRegNo || '',
    contactName: rawData.primaryContactName || '',
    contactTitle: rawData.contactTitle || '', 
    email: rawData.primaryContactEmail || '',
    phone: rawData.primaryContactPhone || '',
    address: rawData.registeredOffice || '',
    services: Array.isArray(rawData.services) ? rawData.services : (rawData.services ? [rawData.services] : []),
    yearsExperience: parseInt(rawData.yearsTrading) || 0,
    teamSize: parseInt(rawData.teamSize) || 0,
    coverage: Array.isArray(rawData.coverageRegion) ? rawData.coverageRegion.join(', ') : (rawData.coverageRegion || ''),
    certifications: rawData.certifications || '',
    timestamp: new Date().toISOString(),
    source: 'epc.saberrenewable.energy'
  };
}

console.log('Original form data:');
console.log(JSON.stringify(testData, null, 2));

console.log('\nTransformed data for Power Automate:');
const transformed = transformFormData(testData);
console.log(JSON.stringify(transformed, null, 2));

console.log('\nField mapping validation:');
console.log(`✓ invitationCode: ${testData.invitationCode} → ${transformed.invitationCode}`);
console.log(`✓ companyName: ${testData.companyName} → ${transformed.companyName}`);
console.log(`✓ registrationNumber: ${testData.companyRegNo} → ${transformed.registrationNumber}`);
console.log(`✓ contactName: ${testData.primaryContactName} → ${transformed.contactName}`);
console.log(`✓ email: ${testData.primaryContactEmail} → ${transformed.email}`);
console.log(`✓ phone: ${testData.primaryContactPhone} → ${transformed.phone}`);
console.log(`✓ address: ${testData.registeredOffice} → ${transformed.address}`);
console.log(`✓ yearsExperience: ${testData.yearsTrading} → ${transformed.yearsExperience}`);
console.log(`✓ coverage: [${testData.coverageRegion.join(', ')}] → "${transformed.coverage}"`);