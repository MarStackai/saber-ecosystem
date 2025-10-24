'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function PartnerDashboard() {
  const [partner, setPartner] = useState(null)
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const router = useRouter()

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('partnerToken')
      const partnerData = localStorage.getItem('partnerData')

      if (!token || !partnerData) {
        router.push('/partner/login')
        return false
      }

      setPartner(JSON.parse(partnerData))
      return token
    }

    const fetchProjects = async (token) => {
      try {
        const response = await fetch('/api/partner/projects', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })

        const data = await response.json()

        if (data.success) {
          setProjects(data.projects)
        } else if (response.status === 401) {
          localStorage.removeItem('partnerToken')
          localStorage.removeItem('partnerData')
          router.push('/partner/login')
        } else {
          setError(data.error || 'Failed to fetch projects')
        }
      } catch (err) {
        setError('Network error loading projects')
      } finally {
        setLoading(false)
      }
    }

    const token = checkAuth()
    if (token) {
      fetchProjects(token)
    }
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('partnerToken')
    localStorage.removeItem('partnerData')
    router.push('/partner/login')
  }

  const handleInvitationResponse = async (invitationId, status) => {
    try {
      const token = localStorage.getItem('partnerToken')

      const response = await fetch(`/api/partner/invitation/${invitationId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ status })
      })

      const data = await response.json()

      if (data.success) {
        // Update the project status in local state
        setProjects(prevProjects =>
          prevProjects.map(project =>
            project.invitation_id === invitationId
              ? {
                  ...project,
                  invitation_status: status,
                  accepted_at: status === 'accepted' ? new Date().toISOString() : project.accepted_at
                }
              : project
          )
        )
      } else {
        setError(data.error || `Failed to ${status} invitation`)
      }
    } catch (err) {
      console.error('Error updating invitation:', err)
      setError(`Network error updating invitation`)
    }
  }

  const getStatusBadge = (status) => {
    const styles = {
      invited: 'bg-yellow-900/50 text-yellow-300 border-yellow-800',
      accepted: 'bg-green-900/50 text-green-300 border-green-800',
      declined: 'bg-red-900/50 text-red-300 border-red-800',
      revoked: 'bg-gray-900/50 text-gray-300 border-gray-800'
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status] || styles.invited}`}>
        {status}
      </span>
    )
  }

  const getProjectTypeBadge = (type) => {
    const styles = {
      'G99': 'bg-blue-900/50 text-blue-300',
      'Planning': 'bg-purple-900/50 text-purple-300',
      'EPC': 'bg-green-900/50 text-green-300'
    }

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${styles[type] || 'bg-slate-700 text-slate-300'}`}>
        {type}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-white">Loading dashboard...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <svg viewBox="0 0 173.11 101.48" className="h-8 w-auto" aria-hidden="true">
                <g>
                  <path fill="#ffffff" d="M65.11,24.31c-14.5-8.51-33.11-3.47-41.62,11.04-8.51,14.5-3.47,33.11,11.04,41.62,11.98,6.94,27.12,5.05,36.89-4.73l38.15-38.15c8.2-6.62,19.86-6.62,28.06.32l-51.71,51.71c-19.86,19.55-51.71,19.55-71.26,0-19.55-19.86-19.55-51.71,0-71.26C31.69-2.8,59.44-5.01,79.3,9.81l-14.5,14.5h.32Z"/>
                  <path fill="#7dbf61" d="M107.36,76.65c14.5,8.51,33.11,3.47,41.62-11.04,8.51-14.5,3.47-33.11-11.04-41.62-11.98-6.94-27.12-5.05-36.89,4.73l-38.15,38.15c-8.2,6.62-19.86,6.62-28.06-.32L87.18,14.85c19.86-19.55,51.71-19.55,71.26,0,19.55,19.86,19.55,51.71,0,71.26-19.55,19.55-45.41,19.55-65.27,5.05l14.5-14.5h-.32Z"/>
                </g>
              </svg>
              <div>
                <h1 className="text-xl font-semibold text-white">Partner Portal</h1>
                <p className="text-sm text-slate-400">{partner?.companyName}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-slate-400">{partner?.email}</span>
              <button
                onClick={handleLogout}
                className="inline-flex items-center px-3 py-2 border border-slate-600 rounded-md text-sm text-slate-300 hover:text-white hover:border-slate-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 rounded-md bg-red-900/50 border border-red-800 p-4">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">
            Welcome back, {partner?.companyName}
          </h2>
          <p className="text-slate-400">
            Manage your project invitations and tender submissions below.
          </p>
        </div>

        {/* Project Access Status */}
        {!partner?.canAccessProjects && (
          <div className="mb-8 bg-yellow-900/20 border border-yellow-800 rounded-lg p-6">
            <div className="flex items-center">
              <svg className="h-6 w-6 text-yellow-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.94-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <div>
                <h3 className="text-lg font-medium text-yellow-100">Project Access Pending</h3>
                <p className="text-yellow-200 mt-1">
                  Your partner application has been approved, but project access is not yet enabled.
                  Contact our team to activate project invitations.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Projects Section */}
        <div className="bg-slate-800 rounded-lg shadow-xl">
          <div className="px-6 py-4 border-b border-slate-700">
            <h3 className="text-lg font-medium text-white">Your Projects</h3>
            <p className="text-sm text-slate-400 mt-1">
              Project invitations and tender opportunities
            </p>
          </div>

          {projects.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <svg className="mx-auto h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="mt-4 text-sm font-medium text-slate-300">No projects yet</h3>
              <p className="mt-2 text-sm text-slate-500">
                You haven&apos;t been invited to any projects yet. Check back later for new opportunities.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-700">
              {projects.map((project) => (
                <div key={project.id} className="px-6 py-4 hover:bg-slate-700/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3 mb-2">
                        <h4 className="text-base font-medium text-white truncate">
                          {project.project_name}
                        </h4>
                        {getProjectTypeBadge(project.project_type)}
                        {getStatusBadge(project.invitation_status)}
                      </div>

                      <div className="flex items-center space-x-4 text-sm text-slate-400">
                        <span>Code: {project.project_code}</span>
                        {project.client_name && <span>Client: {project.client_name}</span>}
                        {project.location && <span>Location: {project.location}</span>}
                      </div>

                      {project.description && (
                        <p className="mt-2 text-sm text-slate-300 line-clamp-2">
                          {project.description}
                        </p>
                      )}

                      <div className="mt-2 flex items-center space-x-4 text-xs text-slate-500">
                        <span>Invited: {new Date(project.invited_at).toLocaleDateString()}</span>
                        {project.accepted_at && (
                          <span>Accepted: {new Date(project.accepted_at).toLocaleDateString()}</span>
                        )}
                        {project.target_completion && (
                          <span>Target: {new Date(project.target_completion).toLocaleDateString()}</span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-3 ml-4">
                      {project.invitation_status === 'invited' && (
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleInvitationResponse(project.invitation_id, 'accepted')}
                            className="inline-flex items-center px-3 py-1 border border-green-600 rounded text-xs font-medium text-green-400 hover:bg-green-600 hover:text-white"
                          >
                            Accept
                          </button>
                          <button
                            onClick={() => handleInvitationResponse(project.invitation_id, 'declined')}
                            className="inline-flex items-center px-3 py-1 border border-red-600 rounded text-xs font-medium text-red-400 hover:bg-red-600 hover:text-white"
                          >
                            Decline
                          </button>
                        </div>
                      )}

                      {project.invitation_status === 'accepted' && (
                        <Link
                          href={`/partner/project/${project.id}`}
                          className="inline-flex items-center px-3 py-1 bg-green-600 rounded text-xs font-medium text-white hover:bg-green-700"
                        >
                          View Project
                          <svg className="ml-1 h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </Link>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-sm text-slate-500">
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