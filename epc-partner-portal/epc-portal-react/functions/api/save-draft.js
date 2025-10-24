// Native Pages Function for draft saving
// Replaces src/app/api/save-draft/route.js to bypass Next.js adapter issues

export async function onRequest(context) {
  const { request, env } = context;
  
  if (request.method === 'POST') {
    try {
      const { invitationCode, formData, currentStep } = await request.json()
      
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

      console.log(`💾 Saving draft for invitation: ${invitationCode}, step: ${currentStep}`)
      
      // Save draft to D1 database
      const now = new Date().toISOString();
      
      await env.epc_form_data.prepare(`
        INSERT OR REPLACE INTO draft_data (
          invitation_code, form_data, current_step, last_saved
        ) VALUES (?, ?, ?, ?)
      `).bind(
        invitationCode,
        JSON.stringify(formData),
        currentStep,
        now
      ).run();
      
      console.log(`✅ Draft saved for invitation: ${invitationCode}`);
      
      return new Response(JSON.stringify({
        success: true,
        message: 'Draft saved successfully',
        lastSaved: now
      }), {
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })
      
    } catch (error) {
      console.error('❌ Error saving draft:', error)
      return new Response(JSON.stringify({
        success: false, 
        message: 'Failed to save draft',
        error: error.message
      }), {
        status: 500,
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })
    }
    
  } else if (request.method === 'GET') {
    try {
      const url = new URL(request.url)
      const invitationCode = url.searchParams.get('invitationCode')
      
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

      // Get draft from D1 database
      const result = await env.epc_form_data.prepare(`
        SELECT form_data, current_step, last_saved
        FROM draft_data 
        WHERE invitation_code = ?
        ORDER BY last_saved DESC
        LIMIT 1
      `).bind(invitationCode).first();

      if (!result) {
        return new Response(JSON.stringify({
          success: false,
          message: 'No draft found'
        }), {
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
      }

      console.log(`📖 Retrieved draft for invitation: ${invitationCode}`)
      
      return new Response(JSON.stringify({
        success: true,
        data: {
          formData: JSON.parse(result.form_data),
          currentStep: result.current_step,
          lastSaved: result.last_saved
        }
      }), {
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })
      
    } catch (error) {
      console.error('❌ Error retrieving draft:', error)
      return new Response(JSON.stringify({
        success: false, 
        message: 'Failed to retrieve draft',
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
      message: 'Save Draft API endpoint',
      usage: 'POST to save draft, GET with invitationCode to retrieve'
    }), {
      status: 405,
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      }
    })
  }
}