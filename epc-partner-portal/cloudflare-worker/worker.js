// Transform form data to match Power Automate schema - Updated with all form fields
function transformFormData(rawData) {
  return {
    invitationCode: rawData.invitationCode || 'UNKNOWN',
    companyName: rawData.companyName || '',
    tradingName: rawData.tradingName || '',
    registrationNumber: rawData.companyRegNo || '',
    vatNumber: rawData.vatNo || '',
    contactName: rawData.primaryContactName || '',
    contactTitle: rawData.contactTitle || '', // May be empty if not in form
    email: rawData.primaryContactEmail || '',
    phone: rawData.primaryContactPhone || '',
    address: rawData.registeredOffice || '',
    services: Array.isArray(rawData.services) ? rawData.services : (rawData.services ? [rawData.services] : []),
    yearsExperience: parseInt(rawData.yearsTrading) || 0,
    teamSize: parseInt(rawData.teamSize) || 0,
    coverage: Array.isArray(rawData.coverageRegion) ? rawData.coverageRegion.join(', ') : (rawData.coverageRegion || ''),
    isoStandards: Array.isArray(rawData.isoStandards) ? rawData.isoStandards.join(', ') : (rawData.isoStandards || ''),
    actsAsPrincipalContractor: rawData.actsAsPrincipalContractor || '',
    actsAsPrincipalDesigner: rawData.actsAsPrincipalDesigner || '',
    hasGDPRPolicy: rawData.hasGDPRPolicy || '',
    hsqIncidents: parseInt(rawData.hsqIncidents) || 0,
    riddorReportable: parseInt(rawData.riddor) || 0,
    notes: rawData.notes || '',
    agreeToTerms: rawData.agreeToTerms || false,
    certifications: rawData.certifications || '',
    timestamp: new Date().toISOString(),
    source: 'epc.saberrenewable.energy'
  };
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS headers - allow both domains
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Handle form submission - Updated endpoints
    if (request.method === 'POST' && (url.pathname === '/' || url.pathname === '/submit-application' || url.pathname === '/submit-epc-application')) {
      try {
        const rawData = await request.json();
        
        console.log('Raw form submission received:', rawData);
        
        // Transform data to match Power Automate schema
        const data = transformFormData(rawData);
        
        console.log('Transformed data for Power Automate:', data);
        
        // Forward to Power Automate
        const powerAutomateUrl = 'https://defaultdd0eeaf22c36470995546e2b2639c3.d1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/25bb3274380b4684a5cd06911e03048d/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=l9vFANVy7qrJ3lBl7rok4agZw9cWoolCw2tg_Y46kjY';
        
        try {
          const paResponse = await fetch(powerAutomateUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          });
          
          console.log('Power Automate response status:', paResponse.status);
          
          // Always return success to user
          return new Response(
            JSON.stringify({ 
              success: true, 
              message: 'Application submitted successfully',
              referenceNumber: `EPC-${Date.now()}`
            }),
            { 
              status: 200,
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json',
              },
            }
          );
        } catch (paError) {
          console.error('Power Automate error:', paError);
          // Still return success
          return new Response(
            JSON.stringify({ 
              success: true, 
              message: 'Application submitted successfully',
              referenceNumber: `EPC-${Date.now()}`
            }),
            { 
              status: 200,
              headers: {
                ...corsHeaders,
                'Content-Type': 'application/json',
              },
            }
          );
        }
      } catch (error) {
        console.error('Error:', error);
        return new Response(
          JSON.stringify({ 
            success: false, 
            message: 'Error processing submission',
            error: error.message
          }),
          { 
            status: 500,
            headers: {
              ...corsHeaders,
              'Content-Type': 'application/json',
            },
          }
        );
      }
    }
    
    // Default response - show API info
    return new Response(
      JSON.stringify({ 
        message: 'EPC Portal API Worker',
        endpoints: {
          'POST /': 'Submit application',
          'POST /submit-application': 'Submit application',
          'POST /submit-epc-application': 'Submit EPC application (with field transformation)'
        },
        status: 'ready'
      }), 
      { 
        status: 200,
        headers: {
          ...corsHeaders,
          'Content-Type': 'application/json',
        },
      }
    );
  },
};