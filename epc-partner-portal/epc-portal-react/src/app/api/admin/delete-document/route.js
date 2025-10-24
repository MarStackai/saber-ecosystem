import { NextRequest, NextResponse } from 'next/server'

export const runtime = 'edge'

export async function DELETE(request) {
  try {
    const { fileId } = await request.json()

    if (!fileId) {
      return NextResponse.json(
        { error: 'Missing fileId' },
        { status: 400 }
      )
    }

    // Make request to Cloudflare Worker API
    const workerResponse = await fetch(`${process.env.WORKER_URL}/api/admin/delete-document`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ fileId })
    })

    if (!workerResponse.ok) {
      const errorData = await workerResponse.json()
      throw new Error(errorData.error || 'Worker delete failed')
    }

    return NextResponse.json({ success: true })

  } catch (error) {
    console.error('Document delete error:', error)
    return NextResponse.json(
      { error: 'Internal server error during delete' },
      { status: 500 }
    )
  }
}