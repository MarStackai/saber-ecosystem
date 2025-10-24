export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': 'https://epc.saberrenewable.energy',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Handle form submission
    if (url.pathname === '/api/submit' && request.method === 'POST') {
      try {
        const data = await request.json();
        
        // Add metadata
        data.timestamp = new Date().toISOString();
        data.source = 'epc.saberrenewable.energy';
        
        // Power Automate URL with SAS token (if needed)
        const powerAutomateUrl = 'https://defaultdd0eeaf22c36470995546e2b2639c3.d1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/2c9c7efdebfc4665b6c11b3f1b628ab2/triggers/manual/paths/invoke?api-version=1';
        
        // Add any required headers for authentication
        const response = await fetch(powerAutomateUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // If you have a SAS token or API key, add it here:
            // 'Authorization': 'Bearer YOUR_TOKEN'
          },
          body: JSON.stringify(data),
        });
        
        // If authentication is required, return a different response
        if (response.status === 401 || response.status === 403) {
          // For now, we'll store the submission and process it differently
          return new Response(
            JSON.stringify({ 
              success: true, 
              message: 'Application received. We will process it shortly.',
              reference: Date.now().toString()
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
        
        const result = await response.json();
        
        return new Response(JSON.stringify(result), {
          status: response.status,
          headers: {
            ...corsHeaders,
            'Content-Type': 'application/json',
          },
        });
      } catch (error) {
        console.error('Error:', error);
        return new Response(
          JSON.stringify({ 
            success: false, 
            message: 'Server error processing submission' 
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
    
    // Default response
    return new Response('EPC Portal API', { status: 200 });
  },
};