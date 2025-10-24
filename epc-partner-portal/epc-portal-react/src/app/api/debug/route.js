import { NextResponse } from 'next/server'

export const runtime = 'edge'

export async function GET(request) {
  try {
    console.log('🔍 Starting environment debug')
    
    // Try to get Cloudflare bindings from multiple sources
    let env = {}
    let contextError = null
    
    // Try getRequestContext (Pages Functions)
    try {
      const { getRequestContext } = await import('@cloudflare/next-on-pages')
      const context = getRequestContext()
      env = context.env || {}
      console.log('✅ Got context from getRequestContext')
    } catch (error) {
      contextError = error.message
      console.log('⚠️ getRequestContext failed:', error.message)
      
      // Try accessing bindings directly from request
      try {
        env = request.env || {}
        console.log('✅ Got env from request')
      } catch (error2) {
        console.log('⚠️ request.env failed:', error2.message)
      }
    }
    
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
    
    return NextResponse.json({
      success: true,
      bindings: {
        available_keys: Object.keys(env),
        d1_available: d1Available,
        d1_type: typeof env.epc_form_data,
        r2_available: r2Available,
        r2_type: typeof env.EPC_PARTNER_FILES,
        environment: env.ENVIRONMENT || 'unknown',
        context_error: contextError,
        runtime: 'edge'
      }
    })
    
  } catch (error) {
    console.error('❌ Debug error:', error)
    return NextResponse.json({
      success: false,
      error: error.message,
      stack: error.stack,
      runtime: 'edge'
    }, { status: 500 })
  }
}