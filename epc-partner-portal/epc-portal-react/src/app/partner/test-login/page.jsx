'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function PartnerTestLogin() {
  const [email, setEmail] = useState('test@greenenergy.com')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/partner/test-login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (data.success) {
        // Store token and partner data
        localStorage.setItem('partnerToken', data.token)
        localStorage.setItem('partnerData', JSON.stringify(data.partner))

        // Redirect to dashboard
        router.push('/partner/dashboard')
      } else {
        setError(data.error || 'Login failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center mb-6">
            <svg viewBox="0 0 173.11 101.48" className="h-12 w-auto" aria-hidden="true">
              <g>
                <path fill="#ffffff" d="M65.11,24.31c-14.5-8.51-33.11-3.47-41.62,11.04-8.51,14.5-3.47,33.11,11.04,41.62,11.98,6.94,27.12,5.05,36.89-4.73l38.15-38.15c8.2-6.62,19.86-6.62,28.06.32l-51.71,51.71c-19.86,19.55-51.71,19.55-71.26,0-19.55-19.86-19.55-51.71,0-71.26C31.69-2.8,59.44-5.01,79.3,9.81l-14.5,14.5h.32Z"/>
                <path fill="#7dbf61" d="M107.36,76.65c14.5,8.51,33.11,3.47,41.62-11.04,8.51-14.5,3.47-33.11-11.04-41.62-11.98-6.94-27.12-5.05-36.89,4.73l-38.15,38.15c-8.2,6.62-19.86,6.62-28.06-.32L87.18,14.85c19.86-19.55,51.71-19.55,71.26,0,19.55,19.86,19.55,51.71,0,71.26-19.55,19.55-45.41,19.55-65.27,5.05l14.5-14.5h-.32Z"/>
              </g>
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-white mb-2">
            Partner Test Login
          </h2>
          <p className="text-slate-400">
            Simplified login for development testing
          </p>
        </div>

        <div className="bg-slate-800 rounded-lg p-8 shadow-xl">
          <div className="mb-4 p-4 bg-blue-900/20 border border-blue-800 rounded-lg">
            <h3 className="text-sm font-medium text-blue-300 mb-2">Test Credentials:</h3>
            <p className="text-xs text-blue-200">Email: test@greenenergy.com</p>
            <p className="text-xs text-blue-200 mt-1">This bypasses the magic link system for testing</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-white mb-2">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-md text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
                placeholder="Enter partner email address"
                disabled={loading}
              />
            </div>

            {error && (
              <div className="rounded-md bg-red-900/50 border border-red-800 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-red-300">{error}</p>
                  </div>
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !email}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Logging in...
                </div>
              ) : (
                'Login (Test Mode)'
              )}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-700">
            <div className="text-center">
              <p className="text-sm text-slate-400">
                Production login:{' '}
                <a href="/partner/login" className="text-green-400 hover:text-green-300">
                  Use Magic Link Login
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}