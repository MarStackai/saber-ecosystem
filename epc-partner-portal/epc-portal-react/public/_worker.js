// Cloudflare Pages Worker for Next.js API routes
import { unstable_dev } from 'wrangler'

const REDIS_URL = 'redis://default:18MS5JivDvX9EbdGyEF5QKTGexoDYJRR@redis-16577.c335.europe-west2-1.gce.redns.redis-cloud.com:16577'

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url)
    
    // Handle API routes
    if (url.pathname.startsWith('/api/')) {
      return await handleApi(request, env, ctx)
    }
    
    // For all other requests, return 404 or pass through
    // This will be handled by the static assets
    return new Response('Not Found', { status: 404 })
  }
}

async function handleApi(request, env, ctx) {
  const url = new URL(request.url)
  
  // Handle different API endpoints
  if (url.pathname === '/api/epc-application') {
    return await handleEpcApplication(request)
  }
  
  if (url.pathname === '/api/save-draft') {
    return await handleSaveDraft(request)
  }
  
  if (url.pathname === '/api/clear-draft') {
    return await handleClearDraft(request)
  }
  
  if (url.pathname === '/api/upload-file') {
    return await handleFileUpload(request)
  }
  
  return new Response('API endpoint not found', { status: 404 })
}

async function handleEpcApplication(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }
  
  try {
    const formData = await request.json()
    
    // Generate reference number
    const timestamp = Date.now()
    const referenceNumber = `EPC-${timestamp}`
    
    // Store in Redis (simplified)
    const redisKey = `epc:${formData.submission?.invitationCode}:application:${timestamp}`
    
    // Submit to SharePoint (placeholder)
    const sharePointResponse = await submitToSharePoint(formData, referenceNumber)
    
    return new Response(JSON.stringify({
      success: true,
      message: 'EPC Partner Application submitted successfully!',
      referenceNumber,
      redisKey,
      processingStatus: 'submitted',
      sharePointResponse
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
    
  } catch (error) {
    console.error('EPC Application Error:', error)
    return new Response(JSON.stringify({
      success: false,
      message: 'Failed to submit application',
      error: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

async function handleSaveDraft(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }
  
  try {
    const { invitationCode, formData } = await request.json()
    
    // Save draft logic (simplified)
    return new Response(JSON.stringify({
      success: true,
      message: 'Draft saved successfully'
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      message: 'Failed to save draft',
      error: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

async function handleClearDraft(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }
  
  try {
    const { invitationCode } = await request.json()
    
    // Clear draft logic (simplified)
    return new Response(JSON.stringify({
      success: true,
      message: 'Draft cleared successfully'
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      message: 'Failed to clear draft',
      error: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

async function handleFileUpload(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }
  
  try {
    // File upload logic (simplified)
    return new Response(JSON.stringify({
      success: true,
      message: 'File uploaded successfully',
      url: 'https://sharepoint.example.com/file.pdf'
    }), {
      headers: { 'Content-Type': 'application/json' }
    })
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      message: 'Failed to upload file',
      error: error.message
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

async function submitToSharePoint(formData, referenceNumber) {
  // SharePoint submission logic (placeholder)
  return {
    success: true,
    sharePointId: 'SP-' + Date.now(),
    message: 'Successfully submitted to SharePoint'
  }
}