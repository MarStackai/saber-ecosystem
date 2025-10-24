import { NextResponse } from 'next/server'
import { getRequestContext } from '@cloudflare/next-on-pages'
import { getD1Database } from '../../../lib/d1.js'

export const runtime = 'edge'

export async function POST(request) {
  try {
    const requestData = await request.json()
    
    console.log('EPC Application submitted to React API:', {
      companyName: requestData.companyInfo?.companyName || requestData.companyName,
      email: requestData.primaryContact?.email || requestData.email,
      invitationCode: requestData.submission?.invitationCode || requestData.invitationCode,
      timestamp: new Date().toISOString()
    })

    // Extract invitation code for D1 storage
    const invitationCode = requestData.submission?.invitationCode || 
                          requestData.invitationCode || 
                          `temp-${Date.now()}`

    // Store in D1 first for reliability
    try {
      const { env } = getRequestContext()
      const d1 = getD1Database(env)
      const result = await d1.submitApplication(
        invitationCode, 
        requestData, 
        requestData.files || {}
      )
      
      console.log('📦 Stored in D1:', result.referenceNumber)
      
      // Attempt immediate SharePoint submission
      try {
        const response = await fetch('https://epc.saberrenewable.energy/api/epc-application', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'User-Agent': 'Saber-EPC-Portal/1.0'
          },
          body: JSON.stringify(requestData),
          signal: AbortSignal.timeout(10000) // 10 second timeout
        })
        
        if (response.ok) {
          const result = await response.json()
          console.log('✅ Immediate SharePoint success:', result)
          
          // Update D1 with success status
          await d1.updateApplicationStatus(invitationCode, 'completed', result.referenceNumber)
          
          // Clear draft after successful submission
          try {
            await d1.clearDraft(invitationCode)
            console.log('✅ Draft cleared after successful SharePoint submission')
          } catch (draftError) {
            console.error('⚠️ Failed to clear draft:', draftError)
          }
          
          return NextResponse.json({
            success: true,
            message: 'Application submitted successfully',
            referenceNumber: result.referenceNumber,
            applicationId: result.referenceNumber,
            processingStatus: 'completed'
          })
        } else {
          throw new Error(`SharePoint API error: ${response.status}`)
        }
        
      } catch (sharePointError) {
        console.log('⚠️  SharePoint submission failed, queued for background processing:', sharePointError.message)
        
        // Update D1 status to indicate background processing needed
        await d1.updateApplicationStatus(invitationCode, 'processing')
        
        // Return success with background processing status
        return NextResponse.json({
          success: true,
          message: 'Application received and queued for processing',
          referenceNumber: result.referenceNumber,
          applicationId: result.referenceNumber,
          processingStatus: 'background_processing'
        })
      }
      
    } catch (d1Error) {
      console.error('❌ D1 storage failed:', d1Error)
      
      // Fallback to direct SharePoint submission if D1 fails
      console.log('📤 Falling back to direct SharePoint submission...')
      
      const response = await fetch('https://epc.saberrenewable.energy/api/epc-application', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'Saber-EPC-Portal/1.0'
        },
        body: JSON.stringify(requestData)
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('SharePoint fallback failed:', response.status, errorText)
        
        return NextResponse.json(
          { success: false, message: 'Failed to process application. Please try again.' },
          { status: 500 }
        )
      }
      
      const result = await response.json()
      console.log('✅ SharePoint fallback success:', result)
      
      return NextResponse.json({
        success: true,
        message: 'Application submitted successfully',
        referenceNumber: result.referenceNumber,
        processingStatus: 'direct_submission'
      })
    }
    
  } catch (error) {
    console.error('💥 Critical error in EPC application API:', error)
    return NextResponse.json(
      { success: false, message: 'Internal server error. Please try again.' },
      { status: 500 }
    )
  }
}

// Handle other HTTP methods
export async function GET() {
  return NextResponse.json({ message: 'EPC Application API endpoint' })
}