import { NextResponse } from 'next/server'
import { getRequestContext } from '@cloudflare/next-on-pages'
import { getD1Database } from '../../../lib/d1.js'

export const runtime = 'edge'

export async function POST(request) {
  try {
    const { invitationCode, formData, currentStep } = await request.json()
    
    if (!invitationCode) {
      return NextResponse.json(
        { success: false, message: 'Invitation code is required' },
        { status: 400 }
      )
    }

    console.log(`💾 Saving draft for invitation: ${invitationCode}, step: ${currentStep}`)
    
    // Get Cloudflare bindings from request context
    const { env } = getRequestContext()
    const d1 = getD1Database(env)
    const result = await d1.saveDraft(invitationCode, formData, currentStep)
    
    return NextResponse.json({
      success: true,
      message: 'Draft saved successfully',
      lastSaved: result.lastSaved
    })
    
  } catch (error) {
    console.error('❌ Error saving draft:', error)
    return NextResponse.json(
      { success: false, message: 'Failed to save draft' },
      { status: 500 }
    )
  }
}

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url)
    const invitationCode = searchParams.get('invitationCode')
    
    if (!invitationCode) {
      return NextResponse.json(
        { success: false, message: 'Invitation code is required' },
        { status: 400 }
      )
    }

    // Get Cloudflare bindings from request context
    const { env } = getRequestContext()
    const d1 = getD1Database(env)
    const draftData = await d1.getDraft(invitationCode)
    
    if (!draftData) {
      return NextResponse.json({
        success: false,
        message: 'No draft found'
      })
    }

    console.log(`📖 Retrieved draft for invitation: ${invitationCode}`)
    
    return NextResponse.json({
      success: true,
      data: draftData
    })
    
  } catch (error) {
    console.error('❌ Error retrieving draft:', error)
    return NextResponse.json(
      { success: false, message: 'Failed to retrieve draft' },
      { status: 500 }
    )
  }
}