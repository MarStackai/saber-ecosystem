// Native Pages Function for invitation synchronization
// Called by Power Automate when SharePoint creates new invitations

export async function onRequest(context) {
  const { request, env } = context;
  
  if (request.method === 'POST') {
    try {
      const invitationData = await request.json()
      
      console.log('📧 Syncing invitation from SharePoint:', {
        title: invitationData.Title,
        companyName: invitationData.CompanyName,
        contactEmail: invitationData.ContactEmail,
        authCode: invitationData.AuthCode,
        timestamp: new Date().toISOString()
      })

      // Validate required fields
      if (!invitationData.AuthCode || !invitationData.CompanyName || !invitationData.ContactEmail) {
        return new Response(JSON.stringify({
          success: false,
          message: 'Missing required fields: AuthCode, CompanyName, and ContactEmail are required'
        }), {
          status: 400,
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
      }

      // Store invitation in D1 database
      const now = new Date().toISOString();
      
      try {
        // Insert or update invitation in D1
        await env.epc_form_data.prepare(`
          INSERT OR REPLACE INTO invitations (
            auth_code, title, company_name, contact_email, 
            notes, status, created_at, updated_at
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
          invitationData.AuthCode,
          invitationData.Title || '',
          invitationData.CompanyName,
          invitationData.ContactEmail,
          invitationData.Notes || '',
          'active',
          now,
          now
        ).run();

        console.log(`✅ Invitation synced to D1: ${invitationData.AuthCode}`);

        return new Response(JSON.stringify({
          success: true,
          message: 'Invitation synchronized successfully',
          authCode: invitationData.AuthCode,
          companyName: invitationData.CompanyName,
          syncedAt: now
        }), {
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })

      } catch (dbError) {
        console.error('❌ D1 sync error:', dbError)
        
        return new Response(JSON.stringify({
          success: false,
          message: 'Database sync failed',
          error: dbError.message
        }), {
          status: 500,
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
      }
      
    } catch (error) {
      console.error('💥 Invitation sync error:', error)
      return new Response(JSON.stringify({
        success: false,
        message: 'Failed to sync invitation',
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
    // Test endpoint - return instructions
    return new Response(JSON.stringify({
      message: 'Invitation Sync API',
      usage: 'POST with SharePoint invitation data',
      requiredFields: ['AuthCode', 'CompanyName', 'ContactEmail'],
      optionalFields: ['Title', 'Notes'],
      workflow: 'SharePoint → Power Automate → This endpoint → D1 database',
      testUrl: 'POST to this endpoint with invitation data'
    }), {
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      }
    })
    
  } else {
    return new Response(JSON.stringify({
      message: 'Method not allowed'
    }), {
      status: 405,
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      }
    })
  }
}