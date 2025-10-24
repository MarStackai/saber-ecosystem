export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const invitationCode = url.searchParams.get('invitationCode');
  
  if (!invitationCode) {
    return new Response('No invitation code provided', { status: 400 });
  }

  try {
    // Get D1 database
    const db = env.D1_DATABASE || env.DB;
    if (!db) {
      console.error('D1 database not available');
      return new Response('Database configuration error', { status: 500 });
    }

    // Check if invitation exists and is valid
    const query = `
      SELECT company_name, email, status, expires_at 
      FROM invitations 
      WHERE invitation_code = ? 
      LIMIT 1
    `;
    
    const result = await db.prepare(query).bind(invitationCode.toUpperCase()).first();
    
    if (!result) {
      return new Response(JSON.stringify({
        valid: false,
        message: 'Invalid invitation code'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Check if expired
    if (result.expires_at && new Date(result.expires_at) < new Date()) {
      return new Response(JSON.stringify({
        valid: false,
        message: 'This invitation has expired'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Check status
    if (result.status === 'used') {
      return new Response(JSON.stringify({
        valid: false,
        message: 'This invitation has already been used'
      }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Valid invitation - redirect to form
    const redirectUrl = new URL('/form', url.origin);
    redirectUrl.searchParams.set('invitationCode', invitationCode.toUpperCase());
    
    return Response.redirect(redirectUrl.toString(), 302);
    
  } catch (error) {
    console.error('Validation error:', error);
    return new Response('Internal server error', { status: 500 });
  }
}