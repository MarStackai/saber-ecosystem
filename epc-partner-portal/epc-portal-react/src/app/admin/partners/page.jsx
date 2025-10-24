'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function PartnersPage() {
  const [partners, setPartners] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    total: 0,
    approved: 0,
    pending: 0,
    rejected: 0
  })

  useEffect(() => {
    // Simulate loading partners data
    const loadPartners = async () => {
      try {
        // This would be replaced with actual API call
        setStats({
          total: 45,
          approved: 32,
          pending: 10,
          rejected: 3
        })

        // Sample partners data
        setPartners([
          {
            id: 1,
            name: 'Solar Solutions Ltd',
            email: 'contact@solarsolutions.com',
            status: 'approved',
            submittedDate: '2024-03-15',
            reviewedDate: '2024-03-18'
          },
          {
            id: 2,
            name: 'GreenTech Innovations',
            email: 'info@greentech.com',
            status: 'pending',
            submittedDate: '2024-03-20',
            reviewedDate: null
          },
          {
            id: 3,
            name: 'WindPower Systems',
            email: 'admin@windpower.com',
            status: 'approved',
            submittedDate: '2024-03-10',
            reviewedDate: '2024-03-12'
          },
        ])
      } catch (error) {
        console.error('Error loading partners:', error)
      } finally {
        setLoading(false)
      }
    }

    loadPartners()
  }, [])

  const getStatusBadge = (status) => {
    const badges = {
      approved: 'bg-green-900/20 text-green-400 border-green-800/30',
      pending: 'bg-yellow-900/20 text-yellow-400 border-yellow-800/30',
      rejected: 'bg-red-900/20 text-red-400 border-red-800/30'
    }
    return badges[status] || badges.pending
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Partners</h1>
        <p className="mt-2 text-slate-400">Manage EPC partner applications and approvals</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="relative overflow-hidden rounded-lg bg-slate-800/50 px-4 py-5 shadow sm:px-6">
          <dt className="text-sm font-medium text-slate-400">Total Partners</dt>
          <dd className="mt-1 text-3xl font-semibold text-white">{stats.total}</dd>
        </div>
        <div className="relative overflow-hidden rounded-lg bg-slate-800/50 px-4 py-5 shadow sm:px-6">
          <dt className="text-sm font-medium text-slate-400">Approved</dt>
          <dd className="mt-1 text-3xl font-semibold text-green-400">{stats.approved}</dd>
        </div>
        <div className="relative overflow-hidden rounded-lg bg-slate-800/50 px-4 py-5 shadow sm:px-6">
          <dt className="text-sm font-medium text-slate-400">Pending Review</dt>
          <dd className="mt-1 text-3xl font-semibold text-yellow-400">{stats.pending}</dd>
        </div>
        <div className="relative overflow-hidden rounded-lg bg-slate-800/50 px-4 py-5 shadow sm:px-6">
          <dt className="text-sm font-medium text-slate-400">Rejected</dt>
          <dd className="mt-1 text-3xl font-semibold text-red-400">{stats.rejected}</dd>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Link
            href="/admin/partners/applications"
            className="rounded-lg bg-slate-800/50 p-4 hover:bg-slate-700/50 transition-colors"
          >
            <h3 className="font-medium text-white">Review Applications</h3>
            <p className="mt-1 text-sm text-slate-400">
              {stats.pending} applications awaiting review
            </p>
          </Link>
          <Link
            href="/admin/partners/approved"
            className="rounded-lg bg-slate-800/50 p-4 hover:bg-slate-700/50 transition-colors"
          >
            <h3 className="font-medium text-white">Approved Partners</h3>
            <p className="mt-1 text-sm text-slate-400">
              View and manage {stats.approved} active partners
            </p>
          </Link>
          <Link
            href="/admin/partners/analytics"
            className="rounded-lg bg-slate-800/50 p-4 hover:bg-slate-700/50 transition-colors"
          >
            <h3 className="font-medium text-white">Analytics</h3>
            <p className="mt-1 text-sm text-slate-400">
              View partner performance metrics
            </p>
          </Link>
        </div>
      </div>

      {/* Recent Applications */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Recent Applications</h2>
        <div className="overflow-hidden bg-slate-800/50 shadow ring-1 ring-slate-700 rounded-lg">
          <table className="min-w-full divide-y divide-slate-700">
            <thead className="bg-slate-800/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Submitted
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {loading ? (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-slate-400">
                    Loading...
                  </td>
                </tr>
              ) : partners.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-slate-400">
                    No partners found
                  </td>
                </tr>
              ) : (
                partners.map((partner) => (
                  <tr key={partner.id} className="hover:bg-slate-700/30">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                      {partner.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                      {partner.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getStatusBadge(partner.status)}`}>
                        {partner.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                      {partner.submittedDate}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        href={`/admin/partners/${partner.id}`}
                        className="text-green-400 hover:text-green-300"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}