'use client'

import { useEffect, useState, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

function PartnerAuthContent() {
  const [status, setStatus] = useState('verifying') // verifying, success, error
  const [message, setMessage] = useState('')
  const router = useRouter()
  const searchParams = useSearchParams()

  useEffect(() => {
    const token = searchParams.get('token')

    if (!token) {
      setStatus('error')
      setMessage('Invalid authentication link')
      return
    }

    const verifyAuth = async () => {
      try {
        const response = await fetch(`/api/partner/auth?token=${token}`)
        const data = await response.json()

        if (data.success) {
          // Store authentication token
          localStorage.setItem('partnerToken', data.token)
          localStorage.setItem('partnerData', JSON.stringify(data.partner))

          setStatus('success')
          setMessage('Authentication successful! Redirecting to dashboard...')

          // Redirect to dashboard after 2 seconds
          setTimeout(() => {
            router.push('/partner/dashboard')
          }, 2000)
        } else {
          setStatus('error')
          setMessage(data.error || 'Authentication failed')
        }
      } catch (error) {
        setStatus('error')
        setMessage('Network error during authentication')
      }
    }

    verifyAuth()
  }, [searchParams, router])

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        <div className="bg-slate-800 rounded-lg p-8 shadow-xl">
          <div className="flex justify-center mb-6">
            <svg viewBox="0 0 173.11 101.48" className="h-12 w-auto" aria-hidden="true">
              <g>
                <path fill="#ffffff" d="M65.11,24.31c-14.5-8.51-33.11-3.47-41.62,11.04-8.51,14.5-3.47,33.11,11.04,41.62,11.98,6.94,27.12,5.05,36.89-4.73l38.15-38.15c8.2-6.62,19.86-6.62,28.06.32l-51.71,51.71c-19.86,19.55-51.71,19.55-71.26,0-19.55-19.86-19.55-51.71,0-71.26C31.69-2.8,59.44-5.01,79.3,9.81l-14.5,14.5h.32Z"/>
                <path fill="#7dbf61" d="M107.36,76.65c14.5,8.51,33.11,3.47,41.62-11.04,8.51-14.5,3.47-33.11-11.04-41.62-11.98-6.94-27.12-5.05-36.89,4.73l-38.15,38.15c-8.2,6.62-19.86,6.62-28.06-.32L87.18,14.85c19.86-19.55,51.71-19.55,71.26,0,19.55,19.86,19.55,51.71,0,71.26-19.55,19.55-45.41,19.55-65.27,5.05l14.5-14.5h-.32Z"/>
              </g>
            </svg>
          </div>

          {status === 'verifying' && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <svg className="animate-spin h-8 w-8 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white">Verifying Authentication</h2>
              <p className="text-slate-400">Please wait while we verify your access...</p>
            </div>
          )}

          {status === 'success' && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <svg className="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-green-400">Authentication Successful</h2>
              <p className="text-slate-300">{message}</p>
            </div>
          )}

          {status === 'error' && (
            <div className="space-y-4">
              <div className="flex justify-center">
                <svg className="h-8 w-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.94-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-red-400">Authentication Failed</h2>
              <p className="text-slate-300">{message}</p>
              <div className="pt-4">
                <button
                  onClick={() => router.push('/partner/login')}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function PartnerAuth() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-white">Loading...</span>
        </div>
      </div>
    }>
      <PartnerAuthContent />
    </Suspense>
  )
}