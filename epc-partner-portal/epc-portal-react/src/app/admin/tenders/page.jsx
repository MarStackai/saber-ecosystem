'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { getApiUrl } from '@/lib/config'

export default function TendersPage() {
  const [tenders, setTenders] = useState([])
  const [filteredTenders, setFilteredTenders] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')

  useEffect(() => {
    fetchTenders()
  }, [])

  const fetchTenders = async () => {
    try {
      const apiUrl = getApiUrl('/api/admin/projects')
      console.log('Fetching tenders from:', apiUrl)

      const response = await fetch(apiUrl)
      const data = await response.json()

      if (data.success) {
        // Transform API data to match frontend expectations
        const transformedTenders = data.projects.map(project => ({
          id: project.id,
          tenderId: project.tender_id,
          projectName: project.project_name,
          location: project.location,
          latitude: project.latitude,
          longitude: project.longitude,
          projectType: project.project_type,
          tenderStatus: project.tender_status,
          description: project.description || 'No description provided',
          createdBy: project.created_by,
          createdAt: project.created_at,
          partnersInvited: 0, // TODO: Calculate from project_partners table
          partnersResponded: 0 // TODO: Calculate from project_partners table
        }))

        setTenders(transformedTenders)
        setFilteredTenders(transformedTenders)
      } else {
        console.error('Failed to fetch tenders:', data.error)
        // Fallback to empty array
        setTenders([])
        setFilteredTenders([])
      }
    } catch (error) {
      console.error('Error fetching tenders:', error)
      // Fallback to empty array
      setTenders([])
      setFilteredTenders([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let filtered = tenders

    // Filter by status
    if (statusFilter !== 'ALL') {
      filtered = filtered.filter(tender => tender.tenderStatus === statusFilter)
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(tender =>
        tender.projectName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tender.tenderId.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tender.location.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    setFilteredTenders(filtered)
  }, [tenders, statusFilter, searchTerm])

  const getStatusBadge = (status) => {
    const styles = {
      'NEW': 'bg-blue-900/50 text-blue-300 border-blue-700',
      'IN_REVIEW': 'bg-yellow-900/50 text-yellow-300 border-yellow-700',
      'PLANNING': 'bg-orange-900/50 text-orange-300 border-orange-700',
      'LIVE': 'bg-green-900/50 text-green-300 border-green-700'
    }

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles[status] || 'bg-slate-700 text-slate-300 border-slate-600'}`}>
        {status.replace('_', ' ')}
      </span>
    )
  }

  const getTypeBadge = (type) => {
    const styles = {
      'G99': 'bg-blue-900/30 text-blue-300',
      'Planning': 'bg-purple-900/30 text-purple-300',
      'EPC': 'bg-green-900/30 text-green-300'
    }

    return (
      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${styles[type] || 'bg-slate-700 text-slate-300'}`}>
        {type}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-white">Loading tenders...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Tender Management</h1>
          <p className="mt-2 text-sm text-slate-400">
            Create, manage, and track project tenders for EPC partner bidding.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link
            href="/admin/tenders/new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Create New Tender
          </Link>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-slate-800 rounded-lg p-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {/* Search */}
          <div className="sm:col-span-2">
            <label htmlFor="search" className="block text-sm font-medium text-white mb-2">
              Search Tenders
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                id="search"
                type="text"
                placeholder="Search by tender ID, project name, or location..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-slate-600 rounded-md bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
            </div>
          </div>

          {/* Status Filter */}
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-white mb-2">
              Filter by Status
            </label>
            <select
              id="status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="block w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="NEW">New</option>
              <option value="IN_REVIEW">In Review</option>
              <option value="PLANNING">Planning</option>
              <option value="LIVE">Live</option>
            </select>
          </div>
        </div>

        {/* Status Filter Pills */}
        <div className="mt-4 flex flex-wrap gap-2">
          {['ALL', 'NEW', 'IN_REVIEW', 'PLANNING', 'LIVE'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                statusFilter === status
                  ? 'bg-green-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {status === 'ALL' ? 'All' : status.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Tenders List */}
      <div className="bg-slate-800 shadow rounded-lg overflow-hidden">
        {filteredTenders.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-4 text-sm font-medium text-slate-300">No tenders found</h3>
            <p className="mt-2 text-sm text-slate-500">
              {searchTerm || statusFilter !== 'ALL'
                ? 'Try adjusting your search criteria.'
                : 'Get started by creating your first tender.'}
            </p>
            {(!searchTerm && statusFilter === 'ALL') && (
              <div className="mt-6">
                <Link
                  href="/admin/tenders/new"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Create New Tender
                </Link>
              </div>
            )}
          </div>
        ) : (
          <div className="divide-y divide-slate-700">
            {filteredTenders.map((tender) => (
              <div key={tender.id} className="p-6 hover:bg-slate-700/50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {/* Header */}
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-base font-medium text-white truncate">
                        {tender.projectName}
                      </h3>
                      <span className="text-sm text-slate-400">({tender.tenderId})</span>
                      {getTypeBadge(tender.projectType)}
                      {getStatusBadge(tender.tenderStatus)}
                    </div>

                    {/* Details */}
                    <div className="flex items-center space-x-4 text-sm text-slate-400 mb-2">
                      <div className="flex items-center">
                        <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {tender.location}
                      </div>
                      <div className="flex items-center">
                        <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        Created {new Date(tender.createdAt).toLocaleDateString()}
                      </div>
                      <div className="flex items-center">
                        <svg className="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                        By {tender.createdBy}
                      </div>
                    </div>

                    {/* Description */}
                    <p className="text-sm text-slate-300 mb-3 line-clamp-2">
                      {tender.description}
                    </p>

                    {/* Partner Stats */}
                    <div className="flex items-center space-x-4 text-xs text-slate-500">
                      <span>{tender.partnersInvited} partners invited</span>
                      <span>{tender.partnersResponded} responses received</span>
                      <span>
                        Response rate: {tender.partnersInvited > 0
                          ? Math.round((tender.partnersResponded / tender.partnersInvited) * 100)
                          : 0}%
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-3 ml-6">
                    <Link
                      href={`/admin/tenders/${tender.id}`}
                      className="inline-flex items-center px-3 py-1 border border-slate-600 rounded text-xs font-medium text-slate-300 hover:text-white hover:border-slate-500"
                    >
                      View Details
                    </Link>
                    <Link
                      href={`/admin/tenders/${tender.id}?tab=partners`}
                      className="inline-flex items-center px-3 py-1 border border-green-600 rounded text-xs font-medium text-green-400 hover:bg-green-600 hover:text-white"
                    >
                      Invite Partners
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Results Summary */}
      {filteredTenders.length > 0 && (
        <div className="text-sm text-slate-400 text-center">
          Showing {filteredTenders.length} of {tenders.length} tenders
          {(searchTerm || statusFilter !== 'ALL') && (
            <button
              onClick={() => {
                setSearchTerm('')
                setStatusFilter('ALL')
              }}
              className="ml-2 text-green-400 hover:text-green-300"
            >
              Clear filters
            </button>
          )}
        </div>
      )}
    </div>
  )
}