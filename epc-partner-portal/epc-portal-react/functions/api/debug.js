// Native Pages Function for environment debugging
// Replaces src/app/api/debug/route.js to bypass Next.js adapter issues

export async function onRequest(context) {
  const { request, env, cf } = context;
  
  try {
    console.log('🔍 Starting environment debug (Native Pages Function)')
    
    console.log('📊 Environment keys:', Object.keys(env))
    console.log('📊 Environment values preview:', Object.keys(env).reduce((acc, key) => {
      acc[key] = typeof env[key]
      return acc
    }, {}))
    
    // Check D1 binding
    const d1Available = !!env.epc_form_data
    console.log('💾 D1 binding available:', d1Available)
    console.log('💾 D1 binding type:', typeof env.epc_form_data)
    
    // Check R2 binding  
    const r2Available = !!env.EPC_PARTNER_FILES
    console.log('📁 R2 binding available:', r2Available)
    console.log('📁 R2 binding type:', typeof env.EPC_PARTNER_FILES)
    
    return new Response(JSON.stringify({
      success: true,
      bindings: {
        available_keys: Object.keys(env),
        d1_available: d1Available,
        d1_type: typeof env.epc_form_data,
        r2_available: r2Available,
        r2_type: typeof env.EPC_PARTNER_FILES,
        environment: env.ENVIRONMENT || 'unknown',
        runtime: 'native-pages-function',
        region: cf?.colo ?? null,
        url: new URL(request.url).pathname,
        now: new Date().toISOString(),
        nodeCompat: typeof globalThis.process !== "undefined",
        method: request.method
      }
    }, null, 2), {
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      },
    });
    
  } catch (error) {
    console.error('❌ Debug error:', error)
    return new Response(JSON.stringify({
      success: false,
      error: error.message,
      stack: error.stack,
      runtime: 'native-pages-function'
    }, null, 2), {
      status: 500,
      headers: { 
        "content-type": "application/json",
        "access-control-allow-origin": "*"
      },
    });
  }
}