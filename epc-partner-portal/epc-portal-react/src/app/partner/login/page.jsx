'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/Button'

export default function PartnerLogin() {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    setError('')

    try {
      const response = await fetch('/api/partner/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (data.success) {
        setMessage('Magic link sent to your email address. Please check your inbox.')
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
            Partner Portal
          </h2>
          <p className="text-slate-400">
            Access your EPC project dashboard
          </p>
        </div>

        <div className="bg-slate-800 rounded-lg p-8 shadow-xl">
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
                placeholder="Enter your registered email address"
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

            {message && (
              <div className="rounded-md bg-green-900/50 border border-green-800 p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-green-300">{message}</p>
                  </div>
                </div>
              </div>
            )}

            <Button
              type="submit"
              disabled={loading || !email}
              className="w-full"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Sending magic link...
                </div>
              ) : (
                'Send Magic Link'
              )}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-700">
            <div className="flex items-center justify-center text-sm text-slate-400">
              <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              Secure authentication via email
            </div>
            <p className="text-center text-xs text-slate-500 mt-2">
              Only approved EPC partners can access this portal
            </p>
          </div>
        </div>

        <div className="text-center">
          <p className="text-sm text-slate-400">
            Need help? Contact{' '}
            <a href="mailto:partners@saberrenewables.com" className="text-green-400 hover:text-green-300">
              partners@saberrenewables.com
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}