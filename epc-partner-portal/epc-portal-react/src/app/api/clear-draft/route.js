import { NextResponse } from 'next/server'
import { getRequestContext } from '@cloudflare/next-on-pages'
import { getD1Database } from '../../../lib/d1.js'

export const runtime = 'edge'

export async function POST(request) {
  try {
    const { invitationCode } = await request.json()
    
    if (!invitationCode) {
      return NextResponse.json(
        { success: false, message: 'Invitation code is required' },
        { status: 400 }
      )
    }

    console.log(`🗑️ Clearing draft for invitation: ${invitationCode}`)
    
    const { env } = getRequestContext()
    const d1 = getD1Database(env)
    const result = await d1.clearDraft(invitationCode)
    
    return NextResponse.json({
      success: true,
      message: 'Draft cleared successfully',
      cleared: result.success
    })
    
  } catch (error) {
    console.error('❌ Error clearing draft:', error)
    return NextResponse.json(
      { success: false, message: 'Failed to clear draft' },
      { status: 500 }
    )
  }
}