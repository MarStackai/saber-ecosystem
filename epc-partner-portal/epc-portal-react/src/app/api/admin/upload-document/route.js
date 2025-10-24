import { NextResponse } from 'next/server'
import { getApiUrl } from '@/lib/config'

export const runtime = 'edge'

export async function POST(request) {
  try {
    const formData = await request.formData()
    const file = formData.get('file')
    const projectId = formData.get('projectId')
    const folderPath = formData.get('folderPath')

    if (!file || !projectId || !folderPath) {
      return NextResponse.json(
        { error: 'Missing required fields: file, projectId, or folderPath' },
        { status: 400 }
      )
    }

    // Validate file
    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      return NextResponse.json(
        { error: 'File size exceeds 10MB limit' },
        { status: 400 }
      )
    }

    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'image/jpeg',
      'image/png',
      'text/plain',
      'application/zip'
    ]

    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: 'Unsupported file type' },
        { status: 400 }
      )
    }

    // Generate unique filename
    const timestamp = Date.now()
    const sanitizedOriginalName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_')
    const r2Key = `projects/${projectId}/${folderPath}/${timestamp}_${sanitizedOriginalName}`

    // Convert file to ArrayBuffer for R2 upload
    const fileBuffer = await file.arrayBuffer()

    // Make request to Cloudflare Worker API with SharePoint integration
    const workerResponse = await fetch(getApiUrl('/api/admin/tender-document/upload'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        projectId: parseInt(projectId),
        folderPath,
        originalFilename: file.name,
        contentType: file.type,
        fileSize: file.size,
        r2Key,
        fileData: Array.from(new Uint8Array(fileBuffer)) // Convert to array for JSON
      })
    })

    if (!workerResponse.ok) {
      const errorData = await workerResponse.json()
      throw new Error(errorData.error || 'Worker upload failed')
    }

    const result = await workerResponse.json()

    return NextResponse.json({
      success: true,
      file: {
        id: result.documentId,
        original_filename: file.name,
        folder_path: folderPath,
        file_size: file.size,
        content_type: file.type,
        r2_key: r2Key,
        uploaded_at: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Document upload error:', error)
    return NextResponse.json(
      { error: 'Internal server error during upload' },
      { status: 500 }
    )
  }
}