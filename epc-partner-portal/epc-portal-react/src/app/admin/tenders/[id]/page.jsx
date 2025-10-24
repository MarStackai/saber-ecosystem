'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import DocumentUpload from '@/components/admin/DocumentUpload'
import PartnerInvitation from '@/components/admin/PartnerInvitation'
import { getApiUrl } from '@/lib/config'

export default function TenderDetail() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [tender, setTender] = useState(null)
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('overview')

  useEffect(() => {
    if (params.id) {
      fetchTenderDetails()
      fetchDocuments()
    }
  }, [params.id])

  useEffect(() => {
    // Check for tab query parameter and set active tab
    const tab = searchParams.get('tab')
    if (tab && ['overview', 'documents', 'partners', 'timeline'].includes(tab)) {
      setActiveTab(tab)
    }
  }, [searchParams])

  const fetchTenderDetails = async () => {
    try {
      const response = await fetch(getApiUrl(`/api/admin/project/${params.id}`))
      const data = await response.json()

      if (data.success) {
        setTender(data.project)
      } else {
        setError('Failed to load tender details')
      }
    } catch (err) {
      setError('Failed to load tender details')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchDocuments = async () => {
    try {
      const response = await fetch(getApiUrl(`/api/admin/project/${params.id}/documents`))
      const data = await response.json()

      if (data.success) {
        setDocuments(data.documents)
      }
    } catch (err) {
      console.error('Error fetching documents:', err)
    }
  }

  const handleUploadComplete = (newDocuments) => {
    setDocuments(prev => [...newDocuments, ...prev])
  }

  const updateTenderStatus = async (newStatus) => {
    try {
      const response = await fetch(getApiUrl(`/api/admin/project/${params.id}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tender_status: newStatus })
      })

      const data = await response.json()
      if (data.success) {
        setTender(prev => ({ ...prev, tender_status: newStatus }))
      }
    } catch (err) {
      console.error('Error updating status:', err)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'NEW': return 'bg-blue-100 text-blue-800'
      case 'IN_REVIEW': return 'bg-yellow-100 text-yellow-800'
      case 'PLANNING': return 'bg-purple-100 text-purple-800'
      case 'LIVE': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Loading tender details...</p>
        </div>
      </div>
    )
  }

  if (error || !tender) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error || 'Tender not found'}</p>
          <Link
            href="/admin/tenders"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
          >
            Back to Tenders
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Link
              href="/admin/tenders"
              className="text-slate-400 hover:text-white"
            >
              <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-white">{tender.project_name}</h1>
              <p className="text-slate-400">{tender.tender_id}</p>
            </div>
          </div>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(tender.tender_status)}`}>
            {tender.tender_status}
          </span>
        </div>

        {/* Status Update Bar */}
        <div className="bg-slate-800 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-between">
            <span className="text-slate-300 font-medium">Status:</span>
            <div className="flex space-x-2">
              {['NEW', 'IN_REVIEW', 'PLANNING', 'LIVE'].map((status) => (
                <button
                  key={status}
                  onClick={() => updateTenderStatus(status)}
                  className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                    tender.tender_status === status
                      ? 'bg-blue-600 text-white'
                      : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-slate-700 mb-6">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Overview' },
              { id: 'documents', name: `Documents (${documents.length})` },
              { id: 'partners', name: 'Partners' },
              { id: 'timeline', name: 'Timeline' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-400'
                    : 'border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-300'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-4">Project Details</h3>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm font-medium text-slate-400">Project Name</dt>
                  <dd className="text-sm text-white">{tender.project_name}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-slate-400">Tender ID</dt>
                  <dd className="text-sm text-white">{tender.tender_id}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-slate-400">Type</dt>
                  <dd className="text-sm text-white">{tender.project_type}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-slate-400">Location</dt>
                  <dd className="text-sm text-white">{tender.location}</dd>
                </div>
                {tender.latitude && tender.longitude && (
                  <div>
                    <dt className="text-sm font-medium text-slate-400">Coordinates</dt>
                    <dd className="text-sm text-white">{tender.latitude}, {tender.longitude}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-sm font-medium text-slate-400">Created</dt>
                  <dd className="text-sm text-white">{new Date(tender.created_at).toLocaleDateString()}</dd>
                </div>
              </dl>
            </div>

            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-4">Description</h3>
              <p className="text-sm text-slate-300 whitespace-pre-wrap">
                {tender.description || 'No description provided.'}
              </p>
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="space-y-6">
            {/* Document Upload */}
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-4">Upload Documents</h3>
              <DocumentUpload
                projectId={tender.id}
                onUploadComplete={handleUploadComplete}
              />
            </div>

            {/* Document List */}
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-lg font-medium text-white mb-4">Project Documents</h3>
              {documents.length === 0 ? (
                <p className="text-slate-400">No documents uploaded yet.</p>
              ) : (
                <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                  <table className="min-w-full divide-y divide-slate-700">
                    <thead className="bg-slate-900">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                          Document
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                          Folder
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                          Size
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                          Uploaded
                        </th>
                        <th className="relative px-6 py-3">
                          <span className="sr-only">Actions</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-slate-800 divide-y divide-slate-700">
                      {documents.map((doc) => (
                        <tr key={doc.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <svg className="h-8 w-8 text-slate-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                              <div>
                                <div className="text-sm font-medium text-white">{doc.original_filename}</div>
                                <div className="text-sm text-slate-400">{doc.content_type}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                            {doc.document_type}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                            {formatFileSize(doc.file_size)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                            {new Date(doc.uploaded_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button className="text-red-400 hover:text-red-300">
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'partners' && (
          <PartnerInvitation projectId={tender.id} />
        )}

        {activeTab === 'timeline' && (
          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-lg font-medium text-white mb-4">Project Timeline</h3>
            <p className="text-slate-400">Timeline view coming soon...</p>
          </div>
        )}
      </div>
    </div>
  )
}