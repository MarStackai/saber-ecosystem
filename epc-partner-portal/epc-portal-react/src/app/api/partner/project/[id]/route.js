export const runtime = 'edge'

export async function GET(request, { params }) {
  try {
    // Forward to Cloudflare Worker
    const workerUrl = process.env.WORKER_URL || 'http://localhost:8787'
    const authHeader = request.headers.get('Authorization')

    const response = await fetch(`${workerUrl}/api/partner/project/${params.id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader || '',
      },
    })

    const data = await response.text()

    return new Response(data, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  } catch (error) {
    console.error('Partner project detail proxy error:', error)
    return new Response(JSON.stringify({
      success: false,
      error: 'Service temporarily unavailable'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}