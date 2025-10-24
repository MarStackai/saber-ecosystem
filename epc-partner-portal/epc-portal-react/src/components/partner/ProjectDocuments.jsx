'use client'

import { useState, useRef, useEffect } from 'react'

const FOLDER_STRUCTURE = [
  {
    id: '01_design',
    name: '01. Design',
    description: 'Concept drawings, layout plans, electrical schematics',
    subfolders: []
  },
  {
    id: '02_grid',
    name: '02. Grid',
    description: 'Grid connection documentation',
    subfolders: [
      { id: '02_g99_application', name: 'G99 Application', description: 'G99 grid connection applications' },
      { id: '02_g99_offer', name: 'G99 Offer', description: 'G99 connection offers and agreements' }
    ]
  },
  {
    id: '03_planning',
    name: '03. Planning',
    description: 'Planning applications and decisions',
    subfolders: [
      { id: '03_planning_application', name: 'Planning Application', description: 'Planning permission applications' },
      { id: '03_planning_decision', name: 'Planning Decision', description: 'Planning decisions and approvals' }
    ]
  },
  {
    id: '04_project_delivery',
    name: '04. Project Delivery',
    description: 'Project delivery documentation',
    subfolders: [
      { id: '04_01_epc_contract', name: '01. EPC Contract', description: 'EPC contract documents' },
      { id: '04_02_om_contract', name: '02. O&M Contract', description: 'Operations and maintenance contracts' },
      { id: '04_03_final_design', name: '03. Final Design', description: 'Final design documentation' },
      { id: '04_04_preconstruction_pack', name: '04. Pre-construction Pack', description: 'Pre-construction documentation' },
      { id: '04_05_epc_invoices', name: '05. EPC Invoices', description: 'EPC invoicing documentation' },
      { id: '04_06_handover_pack', name: '06. Handover Pack', description: 'Project handover documentation' }
    ]
  },
  {
    id: '05_survey',
    name: '05. Survey',
    description: 'Site surveys and assessments',
    subfolders: [
      { id: '05_site_survey', name: 'Site Survey', description: 'Site survey reports and data' },
      { id: '05_media', name: 'Media', description: 'Survey photos, videos, and media' }
    ]
  }
]

const ACCEPTED_FILE_TYPES = {
  'application/pdf': 'PDF',
  'application/msword': 'DOC',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX',
  'application/vnd.ms-excel': 'XLS',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'XLSX',
  'image/jpeg': 'JPG',
  'image/png': 'PNG',
  'text/plain': 'TXT',
  'application/vnd.ms-powerpoint': 'PPT',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PPTX'
}

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

export default function ProjectDocuments({ project, partner }) {
  const [selectedFolder, setSelectedFolder] = useState('')
  const [selectedSubfolder, setSelectedSubfolder] = useState('')
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('upload')
  const fileInputRef = useRef(null)

  useEffect(() => {
    if (project?.id) {
      fetchDocuments()
    }
  }, [project?.id])

  const fetchDocuments = async () => {
    try {
      const token = localStorage.getItem('partnerToken')
      const response = await fetch(`/api/partner/project/${project.id}/documents`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()
      if (data.success) {
        setDocuments(data.documents)
      } else {
        setError('Failed to load documents')
      }
    } catch (err) {
      setError('Network error loading documents')
    } finally {
      setLoading(false)
    }
  }

  const handleFolderChange = (folderId) => {
    setSelectedFolder(folderId)
    setSelectedSubfolder('') // Reset subfolder when main folder changes
  }

  const getSelectedFolderPath = () => {
    if (!selectedFolder) return ''

    const folder = FOLDER_STRUCTURE.find(f => f.id === selectedFolder)
    if (!folder) return selectedFolder

    if (selectedSubfolder && folder.subfolders.length > 0) {
      const subfolder = folder.subfolders.find(sf => sf.id === selectedSubfolder)
      return `${folder.name}/${subfolder?.name || selectedSubfolder}`
    }

    return folder.name
  }

  const getUploadFolderId = () => {
    return selectedSubfolder || selectedFolder
  }

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files)
    const uploadFolder = getUploadFolderId()

    if (!uploadFolder) {
      setError('Please select a folder first')
      return
    }

    if (files.length === 0) return

    // Validate files
    const validFiles = []
    const errors = []

    files.forEach(file => {
      if (!ACCEPTED_FILE_TYPES[file.type]) {
        errors.push(`${file.name}: Unsupported file type`)
        return
      }

      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name}: File too large (max 10MB)`)
        return
      }

      validFiles.push(file)
    })

    if (errors.length > 0) {
      setError(errors.join(', '))
      return
    }

    if (validFiles.length > 0) {
      uploadFiles(validFiles)
    }
  }

  const uploadFiles = async (files) => {
    setUploading(true)
    setError('')

    try {
      const token = localStorage.getItem('partnerToken')
      const uploadPromises = files.map(async (file) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('projectId', project.id)
        formData.append('partnerId', partner.id)
        formData.append('partnerName', partner.companyName)
        formData.append('tenderId', project.project_code)
        const uploadFolder = getUploadFolderId()
        const folderPath = getSelectedFolderPath()
        formData.append('folder', uploadFolder)
        formData.append('folderName', folderPath)

        const response = await fetch('/api/partner/upload-document', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData
        })

        return response.json()
      })

      const results = await Promise.all(uploadPromises)
      const successful = results.filter(r => r.success)
      const failed = results.filter(r => !r.success)

      if (successful.length > 0) {
        await fetchDocuments() // Refresh document list
        setSelectedFolder('')
        setSelectedSubfolder('')
        if (fileInputRef.current) {
          fileInputRef.current.value = ''
        }
      }

      if (failed.length > 0) {
        setError(`Failed to upload ${failed.length} file(s)`)
      }

    } catch (err) {
      setError('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFolderDocuments = (folderId) => {
    return documents.filter(doc => doc.document_type === folderId)
  }

  const getFileIcon = (contentType) => {
    if (contentType?.includes('pdf')) {
      return (
        <svg className="h-8 w-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
        </svg>
      )
    }

    if (contentType?.includes('image')) {
      return (
        <svg className="h-8 w-8 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
        </svg>
      )
    }

    if (contentType?.includes('word') || contentType?.includes('document')) {
      return (
        <svg className="h-8 w-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
        </svg>
      )
    }

    return (
      <svg className="h-8 w-8 text-slate-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
      </svg>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="flex items-center space-x-2">
          <svg className="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-white">Loading documents...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-white">Project Documents</h3>
          <p className="text-sm text-slate-400 mt-1">
            Upload documents for {project.project_name} ({project.project_code})
          </p>
        </div>
        <div className="text-xs text-slate-500">
          Path: {project.project_code}/{partner.companyName}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="rounded-md bg-red-900/50 border border-red-800 p-4">
          <div className="flex">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <p className="text-sm text-red-300">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-slate-700">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'upload', label: 'Upload Documents' },
            { key: 'browse', label: 'Browse by Folder' }
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-green-500 text-green-400'
                  : 'border-transparent text-slate-500 hover:text-slate-300 hover:border-slate-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          {/* Folder Selection */}
          <div className="bg-slate-800 rounded-lg p-6">
            <h4 className="text-sm font-medium text-white mb-4">1. Select Document Folder</h4>
            <div className="space-y-4">
              {FOLDER_STRUCTURE.map((folder) => (
                <div key={folder.id} className="space-y-2">
                  {/* Main Folder */}
                  <label
                    className={`relative flex items-start p-4 border rounded-lg cursor-pointer transition-colors ${
                      selectedFolder === folder.id && !selectedSubfolder
                        ? 'border-green-500 bg-green-900/20'
                        : 'border-slate-600 hover:border-slate-500 hover:bg-slate-700/50'
                    }`}
                  >
                    <input
                      type="radio"
                      name="folder"
                      value={folder.id}
                      checked={selectedFolder === folder.id && !selectedSubfolder}
                      onChange={(e) => handleFolderChange(e.target.value)}
                      className="h-4 w-4 text-green-600 focus:ring-green-500 border-slate-600 rounded"
                    />
                    <div className="ml-3 flex-1">
                      <div className="text-sm font-medium text-white">{folder.name}</div>
                      <div className="text-xs text-slate-400 mt-1">{folder.description}</div>
                      <div className="text-xs text-slate-500 mt-1">
                        {getFolderDocuments(folder.id).length} document(s)
                      </div>
                    </div>
                    {folder.subfolders.length > 0 && (
                      <div className="text-slate-400">
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    )}
                  </label>

                  {/* Subfolders */}
                  {folder.subfolders.length > 0 && selectedFolder === folder.id && (
                    <div className="ml-6 space-y-2">
                      {folder.subfolders.map((subfolder) => (
                        <label
                          key={subfolder.id}
                          className={`relative flex items-start p-3 border rounded-lg cursor-pointer transition-colors ${
                            selectedSubfolder === subfolder.id
                              ? 'border-green-500 bg-green-900/20'
                              : 'border-slate-600 hover:border-slate-500 hover:bg-slate-700/50'
                          }`}
                        >
                          <input
                            type="radio"
                            name="subfolder"
                            value={subfolder.id}
                            checked={selectedSubfolder === subfolder.id}
                            onChange={(e) => setSelectedSubfolder(e.target.value)}
                            className="h-4 w-4 text-green-600 focus:ring-green-500 border-slate-600 rounded"
                          />
                          <div className="ml-3 flex-1">
                            <div className="text-sm font-medium text-white">{subfolder.name}</div>
                            <div className="text-xs text-slate-400 mt-1">{subfolder.description}</div>
                            <div className="text-xs text-slate-500 mt-1">
                              {getFolderDocuments(subfolder.id).length} document(s)
                            </div>
                          </div>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* File Upload */}
          <div className="bg-slate-800 rounded-lg p-6">
            <h4 className="text-sm font-medium text-white mb-4">2. Upload Files</h4>

            <div className="mb-4">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt,.ppt,.pptx"
                onChange={handleFileSelect}
                disabled={!selectedFolder || uploading}
                className="hidden"
              />
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={!selectedFolder || uploading}
                className="inline-flex items-center px-4 py-2 border border-slate-600 rounded-md shadow-sm text-sm font-medium text-white bg-slate-700 hover:bg-slate-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                {uploading ? 'Uploading...' : 'Choose Files'}
              </button>
            </div>

            <div className="text-xs text-slate-500 space-y-1">
              <p>• Maximum file size: 10MB per file</p>
              <p>• Accepted formats: PDF, Word, Excel, PowerPoint, Images, Text</p>
              <p>• Files will be organized in: {project.project_code}/{partner.companyName}/{getSelectedFolderPath() || '[Select Folder]'}</p>
            </div>
          </div>
        </div>
      )}

      {/* Browse Tab */}
      {activeTab === 'browse' && (
        <div className="space-y-4">
          {FOLDER_STRUCTURE.map((folder) => {
            const folderDocs = getFolderDocuments(folder.id)
            return (
              <div key={folder.id} className="bg-slate-800 rounded-lg">
                <div className="px-6 py-4 border-b border-slate-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-white flex items-center">
                        <svg className="h-4 w-4 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clipRule="evenodd" />
                        </svg>
                        {folder.name}
                      </h4>
                      <p className="text-xs text-slate-400 mt-1">{folder.description}</p>
                    </div>
                    <span className="text-xs text-slate-500">
                      {folderDocs.length} document(s)
                    </span>
                  </div>
                </div>

                {/* Main Folder Documents */}
                {folderDocs.length === 0 ? (
                  <div className="px-6 py-8 text-center">
                    <svg className="mx-auto h-8 w-8 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <p className="text-sm text-slate-500 mt-2">No documents uploaded yet</p>
                  </div>
                ) : (
                  <div className="px-6 py-4">
                    <div className="space-y-3">
                      {folderDocs.map((doc) => (
                        <div key={doc.id} className="flex items-center space-x-3 p-3 bg-slate-700/50 rounded-lg">
                          {getFileIcon(doc.content_type)}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">{doc.original_filename}</p>
                            <div className="flex items-center space-x-4 text-xs text-slate-400">
                              <span>{formatFileSize(doc.file_size)}</span>
                              <span>Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <button className="text-green-400 hover:text-green-300 text-xs">
                            Download
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Subfolders */}
                {folder.subfolders.length > 0 && (
                  <div className="border-t border-slate-700">
                    {folder.subfolders.map((subfolder) => {
                      const subfolderDocs = getFolderDocuments(subfolder.id)
                      return (
                        <div key={subfolder.id} className="px-6 py-4 border-b border-slate-700 last:border-b-0">
                          <div className="flex items-center justify-between mb-3">
                            <div>
                              <h5 className="text-sm font-medium text-white flex items-center ml-4">
                                <svg className="h-4 w-4 text-blue-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clipRule="evenodd" />
                                </svg>
                                {subfolder.name}
                              </h5>
                              <p className="text-xs text-slate-400 mt-1 ml-4">{subfolder.description}</p>
                            </div>
                            <span className="text-xs text-slate-500">
                              {subfolderDocs.length} document(s)
                            </span>
                          </div>

                          {subfolderDocs.length === 0 ? (
                            <div className="ml-4 py-4 text-center">
                              <p className="text-xs text-slate-500">No documents uploaded yet</p>
                            </div>
                          ) : (
                            <div className="ml-4 space-y-2">
                              {subfolderDocs.map((doc) => (
                                <div key={doc.id} className="flex items-center space-x-3 p-2 bg-slate-600/50 rounded-lg">
                                  {getFileIcon(doc.content_type)}
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-white truncate">{doc.original_filename}</p>
                                    <div className="flex items-center space-x-4 text-xs text-slate-400">
                                      <span>{formatFileSize(doc.file_size)}</span>
                                      <span>Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}</span>
                                    </div>
                                  </div>
                                  <button className="text-green-400 hover:text-green-300 text-xs">
                                    Download
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}