export const runtime = 'edge'

export async function POST(request) {
  try {
    // Forward to Cloudflare Worker
    const workerUrl = process.env.WORKER_URL || 'http://localhost:8787'
    const authHeader = request.headers.get('Authorization')

    const response = await fetch(`${workerUrl}/api/partner/upload-document`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader || '',
        // Don't set Content-Type for FormData - let the browser set it with boundary
      },
      body: await request.formData()
    })

    const data = await response.text()

    return new Response(data, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  } catch (error) {
    console.error('Partner upload document proxy error:', error)
    return new Response(JSON.stringify({
      success: false,
      error: 'Service temporarily unavailable'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}