#!/usr/bin/env node

// Direct Power Automate Flow Test
// This script tests the Power Automate flow directly to diagnose authentication issues

const https = require('https');
const url = require('url');

const POWER_AUTOMATE_URL = 'https://defaultdd0eeaf22c36470995546e2b2639c3.d1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/2c9c7efdebfc4665b6c11b3f1b628ab2/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=gxDjRFHbP6ExBdUyQCCsCsA1D2ykjv4387MtS2oDcLA';

const testData = {
  invitationCode: "TEST2024",
  companyName: "Debug Test Company",
  registrationNumber: "DEBUG-123",
  contactName: "Debug Tester",
  contactTitle: "Test Manager",
  email: "debug@test.com",
  phone: "555-0123",
  address: "123 Debug Street",
  services: ["Testing"],
  yearsExperience: 1,
  teamSize: 1,
  coverage: "Test Area",
  certifications: "None",
  timestamp: new Date().toISOString(),
  source: "debug-test"
};

console.log('================================================');
console.log('POWER AUTOMATE DIRECT TEST');
console.log('================================================\n');

console.log('Testing URL:', POWER_AUTOMATE_URL);
console.log('\nTest Data:', JSON.stringify(testData, null, 2));
console.log('\n------------------------------------------------\n');

const parsedUrl = url.parse(POWER_AUTOMATE_URL);
const postData = JSON.stringify(testData);

const options = {
  hostname: parsedUrl.hostname,
  port: parsedUrl.port || 443,
  path: parsedUrl.path,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

console.log('Sending request...\n');

const req = https.request(options, (res) => {
  console.log('Response Status:', res.statusCode);
  console.log('Response Headers:', JSON.stringify(res.headers, null, 2));
  console.log('\n');
  
  let data = '';
  
  res.on('data', (chunk) => {
    data += chunk;
  });
  
  res.on('end', () => {
    console.log('Response Body:');
    try {
      const parsed = JSON.parse(data);
      console.log(JSON.stringify(parsed, null, 2));
    } catch (e) {
      console.log(data);
    }
    
    console.log('\n================================================');
    console.log('DIAGNOSIS:');
    console.log('================================================\n');
    
    if (res.statusCode === 401 || res.statusCode === 403) {
      console.log('❌ AUTHENTICATION REQUIRED');
      console.log('\nThe Power Automate flow requires authentication.');
      console.log('\nPOSSIBLE SOLUTIONS:');
      console.log('1. In Power Automate, change the HTTP trigger to accept anonymous requests:');
      console.log('   - Edit the flow');
      console.log('   - Click on the HTTP trigger');
      console.log('   - Look for "Who can trigger the flow" setting');
      console.log('   - Change to "Anyone"');
      console.log('\n2. OR use a SAS URL with sig= parameter:');
      console.log('   - The URL should contain authentication token');
      console.log('   - Example: ...invoke?api-version=1&sig=<token>');
      console.log('\n3. OR implement OAuth2 authentication in the Worker');
    } else if (res.statusCode === 200 || res.statusCode === 202) {
      console.log('✅ FLOW TRIGGERED SUCCESSFULLY');
      console.log('\nThe flow accepted the request. Check:');
      console.log('- Power Automate run history');
      console.log('- SharePoint lists for new records');
      console.log('- Email for notifications');
    } else if (res.statusCode === 400) {
      console.log('⚠️ BAD REQUEST');
      console.log('\nThe flow rejected the data format. Check:');
      console.log('- Flow expects different JSON structure');
      console.log('- Required fields are missing');
    } else {
      console.log('❓ UNEXPECTED RESPONSE');
      console.log('\nCheck Power Automate flow configuration');
    }
    
    console.log('\n================================================\n');
  });
});

req.on('error', (e) => {
  console.error('Request Error:', e);
});

req.write(postData);
req.end();