// Native Pages Function for invitation code validation
// Checks D1 database first, then falls back to SharePoint if needed

export async function onRequest(context) {
  const { request, env } = context;
  
  if (request.method === 'POST') {
    try {
      const { invitationCode } = await request.json()
      
      console.log('🔍 Validating invitation code:', invitationCode)

      if (!invitationCode || invitationCode.length !== 8) {
        return new Response(JSON.stringify({
          valid: false,
          message: 'Invitation code must be exactly 8 characters'
        }), {
          status: 400,
          headers: { 
            "content-type": "application/json",
            "access-control-allow-origin": "*"
          }
        })
      }

      // Step 1: Check D1 database first (fast local lookup)
      try {
        const invitation = await env.epc_form_data.prepare(`
          SELECT auth_code, title, company_name, contact_email, notes, status
          FROM invitations 
          WHERE auth_code = ? AND status = 'active'
          LIMIT 1
        `).bind(invitationCode.toUpperCase()).first();

        if (invitation) {
          console.log(`✅ Invitation found in D1: ${invitation.company_name}`)
          
          return new Response(JSON.stringify({
            valid: true,
            message: 'Valid invitation code',
            invitation: {
              code: invitation.auth_code,
              title: invitation.title,
              companyName: invitation.company_name,
              contactEmail: invitation.contact_email,
              notes: invitation.notes
            },
            source: 'D1'
          }), {
            headers: { 
              "content-type": "application/json",
              "access-control-allow-origin": "*"
            }
          })
        }

        console.log('⚠️ Invitation not found in D1, checking SharePoint fallback...')

      } catch (d1Error) {
        console.error('❌ D1 validation error, falling back to SharePoint:', d1Error)
      }

      // Step 2: Fallback to SharePoint API (slower but comprehensive)
      try {
        const response = await fetch('https://epc-api-worker.robjamescarroll.workers.dev/validate-invitation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Saber-EPC-Portal/1.0'
          },
          body: JSON.stringify({ invitationCode }),
          signal: AbortSignal.timeout(8000) // 8 second timeout
        });

        if (response.ok) {
          const sharepointResult = await response.json();
          console.log('✅ SharePoint fallback validation successful')
          
          // If found in SharePoint, sync to D1 for future fast lookups
          if (sharepointResult.valid && sharepointResult.invitation) {
            try {
              const now = new Date().toISOString();
              await env.epc_form_data.prepare(`
                INSERT OR REPLACE INTO invitations (
                  auth_code, title, company_name, contact_email, 
                  notes, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
              `).bind(
                sharepointResult.invitation.code,
                sharepointResult.invitation.title || '',
                sharepointResult.invitation.companyName,
                sharepointResult.invitation.contactEmail,
                sharepointResult.invitation.notes || '',
                'active',
                now,
                now
              ).run();
              
              console.log('✅ Synced SharePoint invitation to D1 for future lookups')
            } catch (syncError) {
              console.error('⚠️ Failed to sync SharePoint invitation to D1:', syncError)
            }
          }

          return new Response(JSON.stringify({
            ...sharepointResult,
            source: 'SharePoint'
          }), {
            headers: { 
              "content-type": "application/json",
              "access-control-allow-origin": "*"
            }
          })
        } else {
          console.error('❌ SharePoint validation failed:', response.status)
        }

      } catch (sharePointError) {
        console.error('❌ SharePoint validation error:', sharePointError)
      }

      // Both D1 and SharePoint failed/not found
      return new Response(JSON.stringify({
        valid: false,
        message: 'Invalid or expired invitation code',
        source: 'validation_failed'
      }), {
        status: 404,
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })
      
    } catch (error) {
      console.error('💥 Invitation validation error:', error)
      return new Response(JSON.stringify({
        valid: false,
        message: 'Unable to validate invitation code at this time',
        error: 'Validation service error'
      }), {
        status: 500,
        headers: { 
          "content-type": "application/json",
          "access-control-allow-origin": "*"
        }
      })
    }
    
  } else if (request.method === 'GET') {
    return new Response(JSON.stringify({
      message: 'Invitation Validation API',
      usage: 'POST with { "invitationCode": "ABC12345" }',
      workflow: 'D1 lookup → SharePoint fallback → Auto-sync',
      requirements: 'Invitation code must be exactly 8 characters'
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