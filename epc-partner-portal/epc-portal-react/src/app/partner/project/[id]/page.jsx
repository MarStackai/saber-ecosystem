'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import ProjectDocuments from '@/components/partner/ProjectDocuments'

export default function ProjectDetail() {
  const [project, setProject] = useState(null)
  const [partner, setPartner] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const router = useRouter()
  const params = useParams()

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('partnerToken')
      const partnerData = localStorage.getItem('partnerData')

      if (!token || !partnerData) {
        router.push('/partner/login')
        return null
      }

      setPartner(JSON.parse(partnerData))
      return token
    }

    const fetchProjectDetails = async (token) => {
      try {
        const response = await fetch(`/api/partner/projects/${params.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        const data = await response.json()

        if (data.success) {
          setProject(data.project)
        } else if (response.status === 401) {
          localStorage.removeItem('partnerToken')
          localStorage.removeItem('partnerData')
          router.push('/partner/login')
        } else {
          setError(data.error || 'Failed to fetch project details')
        }
      } catch (err) {
        setError('Network error loading project')
      } finally {
        setLoading(false)
      }
    }

    const token = checkAuth()
    if (token) {
      fetchProjectDetails(token)
    }
  }, [params.id, router])


  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-white">Loading project...</span>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-white mb-4">Project Not Found</h2>
          <Link href="/partner/dashboard" className="text-green-400 hover:text-green-300">
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center space-x-4">
              <Link
                href="/partner/dashboard"
                className="text-slate-400 hover:text-white"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </Link>
              <div>
                <h1 className="text-xl font-semibold text-white">{project.project_name}</h1>
                <p className="text-sm text-slate-400">Project Code: {project.project_code}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 rounded-md bg-red-900/50 border border-red-800 p-4">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {/* Project Overview */}
        <div className="bg-slate-800 rounded-lg shadow-xl p-6 mb-8">
          <h2 className="text-lg font-medium text-white mb-4">Project Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm text-slate-400">Client</dt>
                  <dd className="text-sm text-white">{project.client_name || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm text-slate-400">Location</dt>
                  <dd className="text-sm text-white">{project.location || 'N/A'}</dd>
                </div>
                <div>
                  <dt className="text-sm text-slate-400">Project Type</dt>
                  <dd className="text-sm text-white">{project.project_type}</dd>
                </div>
              </dl>
            </div>
            <div>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm text-slate-400">Start Date</dt>
                  <dd className="text-sm text-white">
                    {project.start_date ? new Date(project.start_date).toLocaleDateString() : 'TBD'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-slate-400">Target Completion</dt>
                  <dd className="text-sm text-white">
                    {project.target_completion ? new Date(project.target_completion).toLocaleDateString() : 'TBD'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-slate-400">Status</dt>
                  <dd className="text-sm text-white">{project.status}</dd>
                </div>
              </dl>
            </div>
          </div>
          {project.description && (
            <div className="mt-6">
              <dt className="text-sm text-slate-400 mb-2">Description</dt>
              <dd className="text-sm text-white">{project.description}</dd>
            </div>
          )}
        </div>

        {/* Document Management */}
        <div className="bg-slate-800 rounded-lg shadow-xl">
          <div className="px-6 py-4 border-b border-slate-700">
            <h3 className="text-lg font-medium text-white">Tender Documentation</h3>
            <p className="text-sm text-slate-400 mt-1">
              Upload required documents for each project phase
            </p>
          </div>
          <div className="p-6">
            <ProjectDocuments project={project} partner={partner} />
          </div>
        </div>
      </div>
    </div>
  )
}