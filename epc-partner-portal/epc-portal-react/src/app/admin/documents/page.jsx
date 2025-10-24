'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function DocumentsPage() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        // Simulated data - replace with actual API call
        setDocuments([
          {
            id: 1,
            name: 'Partner Agreement Template',
            category: 'legal',
            type: 'pdf',
            size: '245 KB',
            uploadedDate: '2024-03-20',
            uploadedBy: 'Admin',
            version: '2.1',
            status: 'active',
            path: '/templates/legal/partner-agreement.pdf'
          },
          {
            id: 2,
            name: 'Solar Installation Guidelines',
            category: 'technical',
            type: 'pdf',
            size: '1.2 MB',
            uploadedDate: '2024-03-18',
            uploadedBy: 'Engineering Team',
            version: '1.5',
            status: 'active',
            path: '/guidelines/solar-installation.pdf'
          },
          {
            id: 3,
            name: 'Tender Submission Template',
            category: 'tender',
            type: 'docx',
            size: '180 KB',
            uploadedDate: '2024-03-15',
            uploadedBy: 'Operations',
            version: '3.0',
            status: 'active',
            path: '/templates/tender/submission-template.docx'
          },
          {
            id: 4,
            name: 'Financial Requirements',
            category: 'financial',
            type: 'xlsx',
            size: '95 KB',
            uploadedDate: '2024-03-12',
            uploadedBy: 'Finance Team',
            version: '1.2',
            status: 'active',
            path: '/requirements/financial.xlsx'
          },
          {
            id: 5,
            name: 'Safety Compliance Checklist',
            category: 'compliance',
            type: 'pdf',
            size: '520 KB',
            uploadedDate: '2024-03-10',
            uploadedBy: 'Safety Team',
            version: '2.0',
            status: 'active',
            path: '/compliance/safety-checklist.pdf'
          },
          {
            id: 6,
            name: 'Project Completion Certificate',
            category: 'certificates',
            type: 'pdf',
            size: '150 KB',
            uploadedDate: '2024-03-08',
            uploadedBy: 'Admin',
            version: '1.0',
            status: 'active',
            path: '/templates/certificates/completion.pdf'
          }
        ])
      } catch (error) {
        console.error('Error loading documents:', error)
      } finally {
        setLoading(false)
      }
    }

    loadDocuments()
  }, [])

  const categories = [
    { id: 'all', name: 'All Documents', count: documents.length },
    { id: 'legal', name: 'Legal', count: documents.filter(d => d.category === 'legal').length },
    { id: 'technical', name: 'Technical', count: documents.filter(d => d.category === 'technical').length },
    { id: 'tender', name: 'Tender', count: documents.filter(d => d.category === 'tender').length },
    { id: 'financial', name: 'Financial', count: documents.filter(d => d.category === 'financial').length },
    { id: 'compliance', name: 'Compliance', count: documents.filter(d => d.category === 'compliance').length },
    { id: 'certificates', name: 'Certificates', count: documents.filter(d => d.category === 'certificates').length }
  ]

  const filteredDocuments = documents.filter(doc => {
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const getFileIcon = (type) => {
    const icons = {
      pdf: '📄',
      docx: '📝',
      xlsx: '📊',
      pptx: '📊',
      zip: '📦'
    }
    return icons[type] || '📎'
  }

  const getCategoryColor = (category) => {
    const colors = {
      legal: 'bg-purple-900/20 text-purple-400 border-purple-800/30',
      technical: 'bg-blue-900/20 text-blue-400 border-blue-800/30',
      tender: 'bg-green-900/20 text-green-400 border-green-800/30',
      financial: 'bg-yellow-900/20 text-yellow-400 border-yellow-800/30',
      compliance: 'bg-red-900/20 text-red-400 border-red-800/30',
      certificates: 'bg-indigo-900/20 text-indigo-400 border-indigo-800/30'
    }
    return colors[category] || 'bg-slate-900/20 text-slate-400 border-slate-800/30'
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Documents</h1>
        <p className="mt-2 text-slate-400">Manage templates, guidelines, and shared documents</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">Total Documents</p>
              <p className="text-2xl font-bold text-white">{documents.length}</p>
            </div>
            <div className="p-3 bg-blue-600/20 rounded-lg">
              <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">Categories</p>
              <p className="text-2xl font-bold text-white">{categories.length - 1}</p>
            </div>
            <div className="p-3 bg-green-600/20 rounded-lg">
              <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">This Month</p>
              <p className="text-2xl font-bold text-white">12</p>
            </div>
            <div className="p-3 bg-yellow-600/20 rounded-lg">
              <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
            </div>
          </div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-400">Storage Used</p>
              <p className="text-2xl font-bold text-white">2.4 GB</p>
            </div>
            <div className="p-3 bg-purple-600/20 rounded-lg">
              <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Actions Bar */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700/50 text-white rounded-lg pl-10 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <svg className="absolute left-3 top-2.5 h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
        </div>
        <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-500 transition-colors flex items-center gap-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          Upload Document
        </button>
      </div>

      {/* Categories */}
      <div className="mb-6">
        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === cat.id
                  ? 'bg-green-600 text-white'
                  : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {cat.name} ({cat.count})
            </button>
          ))}
        </div>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="text-center py-8 text-slate-400">Loading documents...</div>
      ) : filteredDocuments.length === 0 ? (
        <div className="text-center py-8 text-slate-400">No documents found</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocuments.map((doc) => (
            <div key={doc.id} className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700 hover:ring-slate-600 transition-all">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getFileIcon(doc.type)}</span>
                  <div className="flex-1">
                    <h3 className="font-medium text-white line-clamp-1">{doc.name}</h3>
                    <p className="text-xs text-slate-400">{doc.type.toUpperCase()} • {doc.size}</p>
                  </div>
                </div>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${getCategoryColor(doc.category)}`}>
                  {doc.category}
                </span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Version</span>
                  <span className="text-slate-300">v{doc.version}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Uploaded</span>
                  <span className="text-slate-300">{doc.uploadedDate}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">By</span>
                  <span className="text-slate-300">{doc.uploadedBy}</span>
                </div>
              </div>

              <div className="mt-4 flex gap-2">
                <button className="flex-1 px-3 py-1.5 text-xs font-medium text-white bg-green-600 rounded hover:bg-green-500 transition-colors">
                  Download
                </button>
                <button className="flex-1 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-700 rounded hover:bg-slate-600 transition-colors">
                  Preview
                </button>
                <button className="px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-700 rounded hover:bg-slate-600 transition-colors">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Folder Structure Info */}
      <div className="mt-8 bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
        <h2 className="text-lg font-semibold text-white mb-4">Document Organization</h2>
        <div className="text-sm text-slate-300 space-y-2">
          <div className="font-mono bg-slate-900/50 p-4 rounded">
            <div>/documents</div>
            <div className="ml-4">├── /templates</div>
            <div className="ml-8">├── /legal</div>
            <div className="ml-8">├── /tender</div>
            <div className="ml-8">└── /certificates</div>
            <div className="ml-4">├── /guidelines</div>
            <div className="ml-8">└── /technical</div>
            <div className="ml-4">├── /compliance</div>
            <div className="ml-4">├── /financial</div>
            <div className="ml-4">└── /partner-submissions</div>
            <div className="ml-8">└── /[partner-id]</div>
            <div className="ml-12">└── /[tender-id]</div>
          </div>
        </div>
      </div>
    </div>
  )
}