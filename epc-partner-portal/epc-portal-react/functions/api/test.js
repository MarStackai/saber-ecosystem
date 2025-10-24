// Simple test function for Pages Functions deployment
// This bypasses the Next.js adapter to test core functionality

export async function onRequest(context) {
  const { request, env, cf } = context;
  
  try {
    const info = {
      ok: true,
      url: new URL(request.url).pathname,
      now: new Date().toISOString(),
      region: cf?.colo ?? null,
      envKeys: Object.keys(env || {}),
      hasD1: !!env.epc_form_data,
      hasR2: !!env.EPC_PARTNER_FILES,
      nodeCompat: typeof globalThis.process !== "undefined",
      method: request.method
    };

    return new Response(JSON.stringify(info, null, 2), {
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      },
    });
  } catch (err) {
    return new Response(JSON.stringify({ 
      ok: false, 
      error: String(err),
      stack: err.stack 
    }), {
      status: 500,
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      },
    });
  }
}