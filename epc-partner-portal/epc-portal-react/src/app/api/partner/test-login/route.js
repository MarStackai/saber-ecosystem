export const runtime = 'edge'

export async function POST(request) {
  try {
    // Forward to Cloudflare Worker
    const workerUrl = process.env.WORKER_URL || 'http://localhost:8787'
    const body = await request.text()

    const response = await fetch(`${workerUrl}/api/partner/test-login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body
    })

    const data = await response.text()

    return new Response(data, {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  } catch (error) {
    console.error('Partner test login proxy error:', error)
    return new Response(JSON.stringify({
      success: false,
      error: 'Service temporarily unavailable'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}