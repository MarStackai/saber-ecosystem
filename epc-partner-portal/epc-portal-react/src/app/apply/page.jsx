'use client'

import { useEffect, useState, Suspense } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { SaberLayout } from '@/components/SaberLayout'

// Separate component to handle search params (required for Suspense boundary)
function ApplyContent() {
  const searchParams = useSearchParams()
  // Use relative API path so Next dev can proxy via rewrites.
  // This avoids hardcoding localhost which breaks remote/Tailscale previews.
  const API_PATH = '/api'
  const [accessCode, setAccessCode] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [autoMode, setAutoMode] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      // Call the validation API endpoint (configurable base URL)
      const response = await fetch(`${API_PATH}/validate-invitation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ invitationCode: accessCode })
      })

      const result = await response.json()

      if (result.valid) {
        // Valid invitation code - proceed to form
        window.location.href = `/form?invitationCode=${accessCode}`
      } else {
        setError(result.message || 'Invalid access code. Please contact Saber Renewables for assistance.')
      }
    } catch (error) {
      console.error('Validation error:', error)
      setError('Unable to validate access code. Please try again or contact Saber Renewables for assistance.')
    }
    
    setIsLoading(false)
  }

  // Auto-validate and redirect when arriving with ?invitationCode=...
  useEffect(() => {
    const code = searchParams.get('invitationCode')
    if (!code) return

    const normalized = code.toUpperCase()
    setAccessCode(normalized)
    setAutoMode(true)
    setIsLoading(true)
    setError('')

    ;(async () => {
      try {
        const response = await fetch(`${API_PATH}/validate-invitation`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ invitationCode: normalized })
        })
        const result = await response.json()
        if (result.valid) {
          window.location.replace(`/form?invitationCode=${encodeURIComponent(normalized)}`)
          return
        }
        setError(result.message || 'Invalid access code. Please contact Saber Renewables for assistance.')
      } catch (err) {
        console.error('Auto-validation error:', err)
        setError('Unable to validate access code. Please try again or contact Saber Renewables for assistance.')
      } finally {
        setIsLoading(false)
        setAutoMode(false)
      }
    })()
  }, [searchParams])

  return (
    <div className="min-h-[calc(100vh-200px)] flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Glass card effect */}
        <div className="relative">
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-green-300/20 via-green-300/10 to-blue-300/20 opacity-30 blur-lg" />
          <div className="relative rounded-2xl bg-slate-800/80 ring-1 ring-white/10 backdrop-blur-sm p-8">
            <div className="absolute -top-px right-11 left-20 h-px bg-gradient-to-r from-green-300/0 via-green-300/40 to-green-300/0" />
            <div className="absolute right-20 -bottom-px left-11 h-px bg-gradient-to-r from-blue-400/0 via-blue-400/40 to-blue-400/0" />
            
            <div>
              <h2 className="text-center text-3xl font-bold tracking-tight text-white">
                Verify Access
              </h2>
              <p className="mt-2 text-center text-sm text-slate-400">
                {autoMode ? 'Verifying your invitation…' : 'Enter your invitation code to continue'}
              </p>
            </div>
            
            <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
              <div>
                <label htmlFor="access-code" className="sr-only">
                  Access Code
                </label>
                <input
                  id="access-code"
                  name="access-code"
                  type="text"
                  required
                  className="relative block w-full rounded-lg border-0 bg-slate-700/50 px-4 py-3 text-white placeholder-slate-400 ring-1 ring-slate-600 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-slate-800 sm:text-sm"
                  placeholder="Enter access code"
                  value={accessCode}
                  onChange={(e) => setAccessCode(e.target.value.toUpperCase())}
                />
              </div>

              {error && (
                <div className="rounded-lg bg-red-900/20 border border-red-800/30 p-3">
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="group relative flex w-full justify-center rounded-lg bg-green-600 px-4 py-3 text-sm font-semibold text-white hover:bg-green-500 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 focus:ring-offset-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Verifying...' : 'Continue to Application'}
                </button>
              </div>

              <div className="text-center">
                <p className="text-sm text-slate-400">
                  Don&apos;t have an access code?{' '}
                  <Link 
                    href="mailto:sysadmin@saberrenewables.com" 
                    className="font-medium text-green-400 hover:text-green-300 transition-colors"
                  >
                    Contact us
                  </Link>
                </p>
              </div>
            </form>
          </div>
        </div>
        
        <div className="text-center">
          <Link 
            href="/" 
            className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
          >
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}

// Main component with Suspense boundary for search params
export default function ApplyPage() {
  return (
    <SaberLayout>
      <Suspense fallback={
        <div className="min-h-[calc(100vh-200px)] flex items-center justify-center">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-white mb-4">Loading...</h2>
          </div>
        </div>
      }>
        <ApplyContent />
      </Suspense>
    </SaberLayout>
  )
}

// Remove edge runtime as it causes issues with client-side navigation
// Static export: allow SSG by removing force-dynamic
