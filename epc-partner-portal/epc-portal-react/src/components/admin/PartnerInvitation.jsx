'use client'

import { useState, useEffect } from 'react'
import { getApiUrl } from '@/lib/config'

export default function PartnerInvitation({ projectId }) {
  const [availablePartners, setAvailablePartners] = useState([])
  const [invitedPartners, setInvitedPartners] = useState([])
  const [selectedPartners, setSelectedPartners] = useState([])
  const [loading, setLoading] = useState(true)
  const [inviting, setInviting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchData()
  }, [projectId])

  const fetchData = async () => {
    try {
      const [partnersResponse, invitedResponse] = await Promise.all([
        fetch(getApiUrl('/api/admin/partners/approved')),
        fetch(getApiUrl(`/api/admin/project/${projectId}/partners`))
      ])

      const partnersData = await partnersResponse.json()
      const invitedData = await invitedResponse.json()

      if (partnersData.success) {
        // Filter out already invited partners
        const invitedPartnerIds = invitedData.success ?
          invitedData.partners.map(p => p.partner_id) : []

        const available = partnersData.partners.filter(
          partner => !invitedPartnerIds.includes(partner.id)
        )

        setAvailablePartners(available)
        setInvitedPartners(invitedData.success ? invitedData.partners : [])
      } else {
        setError('Failed to load partners')
      }
    } catch (err) {
      setError('Network error loading data')
    } finally {
      setLoading(false)
    }
  }

  const handlePartnerSelect = (partnerId) => {
    setSelectedPartners(prev =>
      prev.includes(partnerId)
        ? prev.filter(id => id !== partnerId)
        : [...prev, partnerId]
    )
  }

  const handleInvitePartners = async () => {
    if (selectedPartners.length === 0) return

    setInviting(true)
    setError('')

    try {
      const response = await fetch(getApiUrl(`/api/admin/project/${projectId}/invite-partners`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          partnerIds: selectedPartners,
          role: 'contributor'
        })
      })

      const data = await response.json()

      if (data.success) {
        setSelectedPartners([])
        await fetchData() // Refresh the lists
      } else {
        setError(data.error || 'Failed to invite partners')
      }
    } catch (err) {
      setError('Network error sending invitations')
    } finally {
      setInviting(false)
    }
  }

  const handleUpdateInvitationStatus = async (invitationId, status) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_WORKER_URL}/api/admin/project-invitation/${invitationId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })

      const data = await response.json()

      if (data.success) {
        await fetchData() // Refresh the lists
      } else {
        setError(data.error || 'Failed to update invitation')
      }
    } catch (err) {
      setError('Network error updating invitation')
    }
  }

  const getStatusBadge = (status) => {
    const styles = {
      invited: 'bg-yellow-100 text-yellow-800',
      accepted: 'bg-green-100 text-green-800',
      declined: 'bg-red-100 text-red-800',
      revoked: 'bg-gray-100 text-gray-800'
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status] || styles.invited}`}>
        {status}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="bg-slate-800 rounded-lg p-6">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-white">Loading partners...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Invite New Partners */}
      <div className="bg-slate-800 rounded-lg p-6">
        <h3 className="text-lg font-medium text-white mb-4">Invite Partners</h3>

        {availablePartners.length === 0 ? (
          <p className="text-slate-400">All approved partners have been invited to this project.</p>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-3 mb-4">
              {availablePartners.map((partner) => (
                <label
                  key={partner.id}
                  className="flex items-center p-3 border border-slate-600 rounded-lg hover:bg-slate-700 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedPartners.includes(partner.id)}
                    onChange={() => handlePartnerSelect(partner.id)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-slate-600 rounded"
                  />
                  <div className="ml-3 flex-1">
                    <p className="text-sm font-medium text-white">{partner.company_name}</p>
                    <div className="flex items-center space-x-4 text-xs text-slate-400">
                      <span>{partner.email}</span>
                      {partner.coverage_region && <span>Coverage: {partner.coverage_region}</span>}
                      {partner.specializations && <span>Specializations: {partner.specializations}</span>}
                    </div>
                  </div>
                </label>
              ))}
            </div>

            {selectedPartners.length > 0 && (
              <button
                onClick={handleInvitePartners}
                disabled={inviting}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {inviting ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Inviting...
                  </>
                ) : (
                  `Invite ${selectedPartners.length} Partner${selectedPartners.length > 1 ? 's' : ''}`
                )}
              </button>
            )}
          </>
        )}
      </div>

      {/* Current Project Partners */}
      <div className="bg-slate-800 rounded-lg p-6">
        <h3 className="text-lg font-medium text-white mb-4">Project Partners ({invitedPartners.length})</h3>

        {invitedPartners.length === 0 ? (
          <p className="text-slate-400">No partners have been invited to this project yet.</p>
        ) : (
          <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
            <table className="min-w-full divide-y divide-slate-700">
              <thead className="bg-slate-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Partner
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                    Invited
                  </th>
                  <th className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-slate-800 divide-y divide-slate-700">
                {invitedPartners.map((invitation) => (
                  <tr key={invitation.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-white">{invitation.company_name}</div>
                        <div className="text-sm text-slate-400">{invitation.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(invitation.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      {invitation.role}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                      {new Date(invitation.invited_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {invitation.status === 'invited' && (
                        <button
                          onClick={() => handleUpdateInvitationStatus(invitation.id, 'revoked')}
                          className="text-red-400 hover:text-red-300"
                        >
                          Revoke
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}