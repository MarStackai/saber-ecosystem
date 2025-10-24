'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    partners: {
      new: 0,
      inReview: 0,
      approved: 0,
      rejected: 0
    },
    tenders: {
      new: 0,
      inReview: 0,
      planning: 0,
      live: 0
    }
  })
  const [recentApplications, setRecentApplications] = useState([])
  const [recentTenders, setRecentTenders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setStats({
        partners: {
          new: 12,
          inReview: 8,
          approved: 45,
          rejected: 3
        },
        tenders: {
          new: 2,
          inReview: 4,
          planning: 6,
          live: 3
        }
      })
      setRecentApplications([
        {
          id: 1,
          companyName: 'Green Energy Solutions Ltd',
          email: 'info@greenenergy.com',
          submittedAt: '2024-01-15T10:30:00Z',
          status: 'submitted'
        },
        {
          id: 2,
          companyName: 'Solar Innovations Inc',
          email: 'contact@solarinnovations.com',
          submittedAt: '2024-01-14T15:45:00Z',
          status: 'under_review'
        },
        {
          id: 3,
          companyName: 'Wind Power Systems',
          email: 'info@windpower.com',
          submittedAt: '2024-01-13T09:20:00Z',
          status: 'approved'
        }
      ])
      setRecentTenders([
        {
          id: 1,
          title: 'Birmingham Solar Installation',
          value: '£2.5M',
          deadline: '2024-02-15',
          status: 'live',
          submissions: 3
        },
        {
          id: 2,
          title: 'Manchester Wind Farm',
          value: '£5.2M',
          deadline: '2024-02-28',
          status: 'planning',
          submissions: 0
        }
      ])
      setLoading(false)
    }, 1000)
  }, [])

  const getStatusBadge = (status) => {
    const badges = {
      submitted: 'bg-blue-900/20 text-blue-400 border-blue-800/30',
      under_review: 'bg-yellow-900/20 text-yellow-400 border-yellow-800/30',
      approved: 'bg-green-900/20 text-green-400 border-green-800/30',
      rejected: 'bg-red-900/20 text-red-400 border-red-800/30',
      live: 'bg-green-900/20 text-green-400 border-green-800/30',
      planning: 'bg-blue-900/20 text-blue-400 border-blue-800/30'
    }
    return badges[status] || 'bg-slate-900/20 text-slate-400 border-slate-800/30'
  }

  return (
    <div className="space-y-8">
      {/* Page Header - Always visible */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
        <p className="mt-2 text-slate-400">
          Monitor partner applications, manage tenders, and track operational metrics.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center min-h-64">
          <div className="flex items-center space-x-2">
            <svg className="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="text-white">Loading dashboard data...</span>
          </div>
        </div>
      ) : (
        <>
          {/* Partner KPIs */}
          <div>
            <h2 className="text-lg font-medium text-white mb-4">Partner Applications</h2>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-slate-400 truncate">New Applications</dt>
                        <dd className="text-lg font-medium text-white">{stats.partners.new}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-slate-400 truncate">In Review</dt>
                        <dd className="text-lg font-medium text-white">{stats.partners.inReview}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-slate-400 truncate">Approved</dt>
                        <dd className="text-lg font-medium text-white">{stats.partners.approved}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-slate-400 truncate">Rejected</dt>
                        <dd className="text-lg font-medium text-white">{stats.partners.rejected}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Tender KPIs */}
          <div>
            <h2 className="text-lg font-medium text-white mb-4">Tender Management</h2>
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
                <div className="p-5">
                  <dl>
                    <dt className="text-sm font-medium text-slate-400 truncate">New Tenders</dt>
                    <dd className="text-lg font-medium text-white">{stats.tenders.new}</dd>
                  </dl>
                </div>
              </div>
              <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
                <div className="p-5">
                  <dl>
                    <dt className="text-sm font-medium text-slate-400 truncate">Under Review</dt>
                    <dd className="text-lg font-medium text-white">{stats.tenders.inReview}</dd>
                  </dl>
                </div>
              </div>
              <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
                <div className="p-5">
                  <dl>
                    <dt className="text-sm font-medium text-slate-400 truncate">Planning</dt>
                    <dd className="text-lg font-medium text-white">{stats.tenders.planning}</dd>
                  </dl>
                </div>
              </div>
              <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
                <div className="p-5">
                  <dl>
                    <dt className="text-sm font-medium text-slate-400 truncate">Live</dt>
                    <dd className="text-lg font-medium text-white">{stats.tenders.live}</dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Applications */}
          <div>
            <h2 className="text-lg font-medium text-white mb-4">Recent Partner Applications</h2>
            <div className="bg-slate-800/50 overflow-hidden shadow rounded-lg ring-1 ring-slate-700">
              <table className="min-w-full divide-y divide-slate-700">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Company</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {recentApplications.map((app) => (
                    <tr key={app.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-white">{app.companyName}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{app.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getStatusBadge(app.status)}`}>
                          {app.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <Link href={`/admin/partners/${app.id}`} className="text-green-400 hover:text-green-300">
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Tenders */}
          <div>
            <h2 className="text-lg font-medium text-white mb-4">Recent Tenders</h2>
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              {recentTenders.map((tender) => (
                <div key={tender.id} className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-lg font-medium text-white">{tender.title}</h3>
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getStatusBadge(tender.status)}`}>
                      {tender.status}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Value</span>
                      <span className="text-white">{tender.value}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Deadline</span>
                      <span className="text-white">{tender.deadline}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Submissions</span>
                      <span className="text-white">{tender.submissions}</span>
                    </div>
                  </div>
                  <div className="mt-4">
                    <Link
                      href={`/admin/tenders/${tender.id}`}
                      className="text-sm text-green-400 hover:text-green-300"
                    >
                      View Details →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <h2 className="text-lg font-medium text-white mb-4">Quick Actions</h2>
            <div className="flex gap-4">
              <Link
                href="/admin/tenders/new"
                className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Create Tender
              </Link>
              <Link
                href="/admin/partners"
                className="inline-flex items-center justify-center px-4 py-2 border border-slate-600 text-sm font-medium rounded-md text-slate-300 hover:text-white hover:border-slate-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
                Manage Partners
              </Link>
              <Link
                href="/admin/documents"
                className="inline-flex items-center justify-center px-4 py-2 border border-slate-600 text-sm font-medium rounded-md text-slate-300 hover:text-white hover:border-slate-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2v0" />
                </svg>
                View Documents
              </Link>
            </div>
          </div>
        </>
      )}
    </div>
  )
}