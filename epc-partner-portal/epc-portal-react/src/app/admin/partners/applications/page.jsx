'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function ApplicationsPage() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedStatus, setSelectedStatus] = useState('all')

  useEffect(() => {
    const loadApplications = async () => {
      try {
        // Simulated data - replace with actual API call
        setApplications([
          {
            id: 1,
            companyName: 'Renewable Energy Partners',
            contactName: 'John Smith',
            email: 'john@renewablepartners.com',
            phone: '+44 20 1234 5678',
            submittedDate: '2024-03-22',
            status: 'pending',
            companyType: 'Developer',
            projectsCompleted: 15
          },
          {
            id: 2,
            companyName: 'EcoTech Solutions',
            contactName: 'Sarah Johnson',
            email: 'sarah@ecotech.com',
            phone: '+44 20 9876 5432',
            submittedDate: '2024-03-21',
            status: 'pending',
            companyType: 'Installer',
            projectsCompleted: 28
          },
          {
            id: 3,
            companyName: 'Green Future Ltd',
            contactName: 'Michael Brown',
            email: 'michael@greenfuture.com',
            phone: '+44 20 5555 1234',
            submittedDate: '2024-03-20',
            status: 'under_review',
            companyType: 'Consultant',
            projectsCompleted: 8
          },
        ])
      } catch (error) {
        console.error('Error loading applications:', error)
      } finally {
        setLoading(false)
      }
    }

    loadApplications()
  }, [])

  const filteredApplications = selectedStatus === 'all'
    ? applications
    : applications.filter(app => app.status === selectedStatus)

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'bg-yellow-900/20 text-yellow-400 border-yellow-800/30',
      under_review: 'bg-blue-900/20 text-blue-400 border-blue-800/30',
      approved: 'bg-green-900/20 text-green-400 border-green-800/30',
      rejected: 'bg-red-900/20 text-red-400 border-red-800/30'
    }
    return badges[status] || badges.pending
  }

  const handleApprove = (id) => {
    console.log('Approving application:', id)
    // Add approval logic here
  }

  const handleReject = (id) => {
    console.log('Rejecting application:', id)
    // Add rejection logic here
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Partner Applications</h1>
        <p className="mt-2 text-slate-400">Review and process partner applications</p>
      </div>

      {/* Filters */}
      <div className="mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedStatus('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedStatus === 'all'
                ? 'bg-green-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            All Applications
          </button>
          <button
            onClick={() => setSelectedStatus('pending')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedStatus === 'pending'
                ? 'bg-green-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setSelectedStatus('under_review')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              selectedStatus === 'under_review'
                ? 'bg-green-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Under Review
          </button>
        </div>
      </div>

      {/* Applications List */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-8 text-slate-400">Loading applications...</div>
        ) : filteredApplications.length === 0 ? (
          <div className="text-center py-8 text-slate-400">No applications found</div>
        ) : (
          filteredApplications.map((application) => (
            <div key={application.id} className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white">{application.companyName}</h3>
                  <p className="text-slate-400">{application.companyType}</p>
                </div>
                <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full border ${getStatusBadge(application.status)}`}>
                  {application.status.replace('_', ' ')}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-slate-400">Contact</p>
                  <p className="text-white">{application.contactName}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Email</p>
                  <p className="text-white">{application.email}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Phone</p>
                  <p className="text-white">{application.phone}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Projects Completed</p>
                  <p className="text-white">{application.projectsCompleted}</p>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <p className="text-sm text-slate-400">
                  Submitted: {application.submittedDate}
                </p>
                <div className="flex gap-3">
                  <Link
                    href={`/admin/partners/${application.id}`}
                    className="inline-block px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors"
                  >
                    View Details
                  </Link>
                  {application.status === 'pending' || application.status === 'under_review' ? (
                    <>
                      <button
                        onClick={() => handleApprove(application.id)}
                        className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-500 transition-colors"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleReject(application.id)}
                        className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-500 transition-colors"
                      >
                        Reject
                      </button>
                    </>
                  ) : null}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}