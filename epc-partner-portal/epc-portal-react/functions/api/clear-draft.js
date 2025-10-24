// Native Pages Function for clearing draft data
// Replaces src/app/api/clear-draft/route.js to bypass Next.js adapter issues

export async function onRequest(context) {
  const { request, env } = context;
  
  if (request.method === 'POST') {
    try {
      const { invitationCode } = await request.json()
      
      if (!invitationCode) {
        return new Response(JSON.stringify({
          success: false, 
          message: 'Invitation code is required' 
        }), {
          status: 400,
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
      }

      console.log(`🗑️ Clearing draft for invitation: ${invitationCode}`)
      
      // Clear draft from D1 database
      const result = await env.epc_form_data.prepare(`
        DELETE FROM draft_data 
        WHERE invitation_code = ?
      `).bind(invitationCode).run();
      
      console.log(`✅ Draft cleared for invitation: ${invitationCode}`);
      
      return new Response(JSON.stringify({
        success: true,
        message: 'Draft cleared successfully',
        cleared: true
      }), {
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })
      
    } catch (error) {
      console.error('❌ Error clearing draft:', error)
      return new Response(JSON.stringify({
        success: false, 
        message: 'Failed to clear draft',
        error: error.message
      }), {
        status: 500,
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })
    }
  } else {
    return new Response(JSON.stringify({
      message: 'Clear Draft API endpoint',
      usage: 'POST with invitationCode to clear draft'
    }), {
      status: 405,
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      }
    })
  }
}