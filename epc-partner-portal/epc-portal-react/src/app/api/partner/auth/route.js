export const runtime = 'edge'

export async function GET(request) {
  try {
    // Forward to Cloudflare Worker
    const workerUrl = process.env.WORKER_URL || 'http://localhost:8787'
    const url = new URL(request.url)
    const token = url.searchParams.get('token')

    const response = await fetch(`${workerUrl}/api/partner/auth?token=${token}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
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
    console.error('Partner auth proxy error:', error)
    return new Response(JSON.stringify({
      success: false,
      error: 'Service temporarily unavailable'
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}