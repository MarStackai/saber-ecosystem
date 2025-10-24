'use client'

import { useState, useRef } from 'react'

// Exact folder structure matching SharePoint EPC_Tender_Docs template
const FOLDER_STRUCTURE = [
  { id: '01. Design', name: '01. Design', path: '01. Design' },
  { id: '02_grid_g99_app', name: '02. Grid / G99 Application', path: '02. Grid/G99 Application' },
  { id: '02_grid_g99_offer', name: '02. Grid / G99 Offer', path: '02. Grid/G99 Offer' },
  { id: '03_planning_app', name: '03. Planning / Planning Application', path: '03. Planning/Planning Application' },
  { id: '03_planning_decision', name: '03. Planning / Planning Decision', path: '03. Planning/Planning Decision' },
  { id: '04_pd_epc', name: '04. Project Delivery / 01. EPC Contract', path: '04. Project Delivery/01. EPC Contract' },
  { id: '04_pd_om', name: '04. Project Delivery / 02. O&M Contract', path: '04. Project Delivery/02. O&M Contract' },
  { id: '04_pd_final', name: '04. Project Delivery / 03. Final Design', path: '04. Project Delivery/03. Final Design' },
  { id: '04_pd_precon', name: '04. Project Delivery / 04. Pre-construction Pack', path: '04. Project Delivery/04. Pre-construction Pack' },
  { id: '04_pd_invoices', name: '04. Project Delivery / 05. EPC Invoices', path: '04. Project Delivery/05. EPC Invoices' },
  { id: '04_pd_handover', name: '04. Project Delivery / 06. Handover Pack', path: '04. Project Delivery/06. Handover Pack' },
  { id: '05_survey_site', name: '05. Survey / Site Survey', path: '05. Survey/Site Survey' },
  { id: '05_survey_media', name: '05. Survey / Media', path: '05. Survey/Media' }
]

export default function DocumentUpload({ projectId, onUploadComplete }) {
  const [selectedFolder, setSelectedFolder] = useState('')
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef(null)

  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files)
    if (!selectedFolder) {
      setError('Please select a folder first')
      return
    }

    if (files.length === 0) return

    // Validate file types and sizes
    const validFiles = files.filter(file => {
      const isValidSize = file.size <= 10 * 1024 * 1024 // 10MB limit
      const isValidType = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image/jpeg',
        'image/png',
        'text/plain',
        'application/zip'
      ].includes(file.type)

      return isValidSize && isValidType
    })

    if (validFiles.length !== files.length) {
      setError('Some files were skipped due to size (>10MB) or unsupported format')
    } else {
      setError('')
    }

    uploadFiles(validFiles)
  }

  const uploadFiles = async (files) => {
    if (!projectId || !selectedFolder) {
      setError('Missing project ID or folder selection')
      return
    }

    setUploading(true)
    setError('')

    try {
      // Find the selected folder object to get its path
      const selectedFolderObj = FOLDER_STRUCTURE.find(f => f.id === selectedFolder)
      if (!selectedFolderObj) {
        setError('Invalid folder selection')
        return
      }

      const uploadPromises = files.map(async (file) => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('projectId', projectId)
        formData.append('folderPath', selectedFolderObj.path) // Use the path field for SharePoint

        const response = await fetch('/api/admin/upload-document', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Upload failed')
        }

        return await response.json()
      })

      const results = await Promise.all(uploadPromises)

      setUploadedFiles(prev => [...prev, ...results])

      if (onUploadComplete) {
        onUploadComplete(results)
      }

      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

    } catch (err) {
      console.error('Upload error:', err)
      setError(`Upload failed: ${err.message}`)
    } finally {
      setUploading(false)
    }
  }

  const removeFile = async (fileId) => {
    try {
      const response = await fetch('/api/admin/delete-document', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fileId })
      })

      if (!response.ok) {
        throw new Error('Failed to delete file')
      }

      setUploadedFiles(prev => prev.filter(file => file.id !== fileId))
    } catch (err) {
      setError(`Delete failed: ${err.message}`)
    }
  }

  const getFolderDisplayName = (folderId) => {
    return FOLDER_STRUCTURE.find(f => f.id === folderId)?.name || folderId
  }

  return (
    <div className="space-y-6">
      {/* Folder Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Project Folder
        </label>
        <select
          value={selectedFolder}
          onChange={(e) => setSelectedFolder(e.target.value)}
          className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        >
          <option value="">Choose a folder...</option>
          {FOLDER_STRUCTURE.map(folder => (
            <option key={folder.id} value={folder.id}>
              {folder.name}
            </option>
          ))}
        </select>
      </div>

      {/* File Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Documents
        </label>
        <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
          <div className="space-y-1 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="flex text-sm text-gray-600">
              <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                <span>Upload files</span>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleFileSelect}
                  disabled={!selectedFolder || uploading}
                  className="sr-only"
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.txt,.zip"
                />
              </label>
              <p className="pl-1">or drag and drop</p>
            </div>
            <p className="text-xs text-gray-500">
              PDF, Word, Excel, Images, Text, ZIP up to 10MB each
            </p>
            {!selectedFolder && (
              <p className="text-xs text-red-500 mt-2">
                Please select a folder first
              </p>
            )}
          </div>
        </div>
      </div>

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

      {/* Upload Progress */}
      {uploading && (
        <div className="rounded-md bg-blue-50 p-4">
          <div className="flex items-center">
            <svg className="animate-spin h-5 w-5 text-blue-600" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <p className="ml-3 text-sm text-blue-700">Uploading files...</p>
          </div>
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Uploaded Documents</h4>
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {uploadedFiles.map((file, index) => (
                <li key={index} className="px-4 py-4 flex items-center justify-between">
                  <div className="flex items-center">
                    <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-900">{file.original_filename}</p>
                      <p className="text-sm text-gray-500">
                        {getFolderDisplayName(file.folder_path)} • {Math.round(file.file_size / 1024)} KB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(file.id)}
                    className="text-red-600 hover:text-red-900 text-sm font-medium"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}