import { NextResponse } from 'next/server'
import { getRequestContext } from '@cloudflare/next-on-pages'
import { getR2Storage } from '../../../lib/r2.js'
import { getD1Database } from '../../../lib/d1.js'

export const runtime = 'edge'

export async function POST(request) {
  try {
    const formData = await request.formData()
    const file = formData.get('file')
    const invitationCode = formData.get('invitationCode')
    const fieldName = formData.get('fieldName')
    
    if (!file || !invitationCode || !fieldName) {
      return NextResponse.json(
        { success: false, message: 'File, invitation code, and field name are required' },
        { status: 400 }
      )
    }

    console.log(`📁 Uploading ${fieldName} for invitation: ${invitationCode}`)
    console.log(`📄 File: ${file.name} (${file.size} bytes)`)

    // Get Cloudflare bindings from request context
    const { env } = getRequestContext()
    const r2 = getR2Storage(env)
    
    // Upload file to R2 with organized folder structure
    const uploadResult = await r2.uploadFile(invitationCode, fieldName, file, {
      userAgent: request.headers.get('user-agent'),
      uploadIP: request.headers.get('cf-connecting-ip'),
    })

    if (!uploadResult.success) {
      return NextResponse.json(
        { success: false, message: 'Failed to upload file to storage. Please try again.' },
        { status: 500 }
      )
    }

    // Record file upload in D1 database
    try {
      const d1 = getD1Database(env)
      await d1.db?.prepare(`
        INSERT INTO application_files (
          invitation_code, field_name, original_filename, file_size, 
          content_type, storage_path, upload_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
      `).bind(
        invitationCode,
        fieldName,
        file.name,
        file.size,
        file.type,
        uploadResult.fileKey,
        new Date().toISOString()
      ).run()
      
      console.log(`📝 File upload recorded in D1: ${uploadResult.fileKey}`)
    } catch (dbError) {
      console.warn('⚠️  Could not record file in D1 (using fallback):', dbError.message)
      // Continue without failing - file is uploaded to R2 successfully
    }

    console.log('✅ File uploaded successfully to R2:', uploadResult)

    return NextResponse.json({
      success: true,
      message: 'File uploaded successfully',
      fileUrl: uploadResult.url,
      fileKey: uploadResult.fileKey,
      fieldName,
      metadata: uploadResult.metadata,
      storagePath: uploadResult.fileKey
    })

  } catch (error) {
    console.error('💥 File upload error:', error)
    return NextResponse.json(
      { success: false, message: 'Internal server error during file upload.' },
      { status: 500 }
    )
  }
}

// Handle other HTTP methods
export async function GET() {
  return NextResponse.json({ 
    message: 'File Upload API endpoint',
    usage: 'POST multipart/form-data with file, invitationCode, and fieldName'
  })
}