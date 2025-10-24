'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function CreateTenderPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [nextTenderId, setNextTenderId] = useState('')
  const [formData, setFormData] = useState({
    projectName: '',
    location: '',
    latitude: '',
    longitude: '',
    description: '',
    projectType: 'EPC',
    tenderStatus: 'NEW'
  })
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [errors, setErrors] = useState({})

  useEffect(() => {
    // Fetch next tender ID
    // TODO: Replace with actual API call
    setTimeout(() => {
      setNextTenderId('SABER-0004')
    }, 500)
  }, [])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))

    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: null
      }))
    }
  }

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files)
    const newFiles = files.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type
    }))
    setUploadedFiles(prev => [...prev, ...newFiles])
  }

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.projectName.trim()) {
      newErrors.projectName = 'Project name is required'
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Project location is required'
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Project description is required'
    }

    if (formData.latitude && (isNaN(formData.latitude) || formData.latitude < -90 || formData.latitude > 90)) {
      newErrors.latitude = 'Latitude must be between -90 and 90'
    }

    if (formData.longitude && (isNaN(formData.longitude) || formData.longitude < -180 || formData.longitude > 180)) {
      newErrors.longitude = 'Longitude must be between -180 and 180'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setLoading(true)

    try {
      // TODO: Replace with actual API call
      const tenderData = {
        ...formData,
        tenderId: nextTenderId,
        files: uploadedFiles
      }

      console.log('Creating tender:', tenderData)

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Redirect to tender detail page
      router.push('/admin/tenders/1') // Replace with actual tender ID
    } catch (error) {
      console.error('Error creating tender:', error)
      // TODO: Show error message
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Create New Tender</h1>
          <p className="mt-2 text-sm text-slate-400">
            Set up a new project tender for EPC partner bidding.
          </p>
        </div>
        <Link
          href="/admin/tenders"
          className="inline-flex items-center px-3 py-2 border border-slate-600 rounded-md text-sm text-slate-300 hover:text-white hover:border-slate-500"
        >
          <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Tenders
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic Information */}
        <div className="bg-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-medium text-white mb-6">Basic Information</h2>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {/* Project Name */}
            <div className="sm:col-span-2">
              <label htmlFor="projectName" className="block text-sm font-medium text-white mb-2">
                Tender Name <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                id="projectName"
                name="projectName"
                value={formData.projectName}
                onChange={handleInputChange}
                className={`block w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 ${
                  errors.projectName ? 'border-red-500' : 'border-slate-600'
                }`}
                placeholder="Enter the tender project name"
              />
              {errors.projectName && (
                <p className="mt-1 text-sm text-red-400">{errors.projectName}</p>
              )}
            </div>

            {/* Tender ID */}
            <div>
              <label htmlFor="tenderId" className="block text-sm font-medium text-white mb-2">
                Tender ID
              </label>
              <input
                type="text"
                id="tenderId"
                value={nextTenderId}
                disabled
                className="block w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-600 text-slate-300 cursor-not-allowed"
                placeholder="Loading..."
              />
              <p className="mt-1 text-xs text-slate-500">Auto-generated sequential ID</p>
            </div>

            {/* Project Type */}
            <div>
              <label htmlFor="projectType" className="block text-sm font-medium text-white mb-2">
                Project Type
              </label>
              <select
                id="projectType"
                name="projectType"
                value={formData.projectType}
                onChange={handleInputChange}
                className="block w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="EPC">EPC (Engineering, Procurement, Construction)</option>
                <option value="G99">G99 (Grid Connection)</option>
                <option value="Planning">Planning Application</option>
              </select>
            </div>

            {/* Tender Status */}
            <div>
              <label htmlFor="tenderStatus" className="block text-sm font-medium text-white mb-2">
                Initial Status
              </label>
              <select
                id="tenderStatus"
                name="tenderStatus"
                value={formData.tenderStatus}
                onChange={handleInputChange}
                className="block w-full px-3 py-2 border border-slate-600 rounded-md bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="NEW">New</option>
                <option value="IN_REVIEW">In Review</option>
                <option value="PLANNING">Planning</option>
                <option value="LIVE">Live</option>
              </select>
            </div>
          </div>
        </div>

        {/* Location Information */}
        <div className="bg-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-medium text-white mb-6">Location Information</h2>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            {/* Address */}
            <div className="sm:col-span-2">
              <label htmlFor="location" className="block text-sm font-medium text-white mb-2">
                Project Address <span className="text-red-400">*</span>
              </label>
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                className={`block w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 ${
                  errors.location ? 'border-red-500' : 'border-slate-600'
                }`}
                placeholder="Enter the project address or general location"
              />
              {errors.location && (
                <p className="mt-1 text-sm text-red-400">{errors.location}</p>
              )}
            </div>

            {/* Latitude */}
            <div>
              <label htmlFor="latitude" className="block text-sm font-medium text-white mb-2">
                Latitude (Optional)
              </label>
              <input
                type="number"
                step="any"
                id="latitude"
                name="latitude"
                value={formData.latitude}
                onChange={handleInputChange}
                className={`block w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 ${
                  errors.latitude ? 'border-red-500' : 'border-slate-600'
                }`}
                placeholder="e.g., 53.4808"
              />
              {errors.latitude && (
                <p className="mt-1 text-sm text-red-400">{errors.latitude}</p>
              )}
            </div>

            {/* Longitude */}
            <div>
              <label htmlFor="longitude" className="block text-sm font-medium text-white mb-2">
                Longitude (Optional)
              </label>
              <input
                type="number"
                step="any"
                id="longitude"
                name="longitude"
                value={formData.longitude}
                onChange={handleInputChange}
                className={`block w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 ${
                  errors.longitude ? 'border-red-500' : 'border-slate-600'
                }`}
                placeholder="e.g., -2.2426"
              />
              {errors.longitude && (
                <p className="mt-1 text-sm text-red-400">{errors.longitude}</p>
              )}
            </div>
          </div>
        </div>

        {/* Project Description */}
        <div className="bg-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-medium text-white mb-6">Project Description</h2>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-white mb-2">
              Description <span className="text-red-400">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              rows={6}
              value={formData.description}
              onChange={handleInputChange}
              className={`block w-full px-3 py-2 border rounded-md bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 ${
                errors.description ? 'border-red-500' : 'border-slate-600'
              }`}
              placeholder="Provide a detailed description of the project scope, requirements, timeline, and any specific considerations for bidding partners..."
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-400">{errors.description}</p>
            )}
            <p className="mt-2 text-xs text-slate-500">
              Include project scope, technical requirements, timeline, deliverables, and any specific partner qualifications needed.
            </p>
          </div>
        </div>

        {/* Document Upload */}
        <div className="bg-slate-800 rounded-lg p-6">
          <h2 className="text-lg font-medium text-white mb-6">Supporting Documents</h2>

          <div className="space-y-4">
            {/* Upload Area */}
            <div className="border-2 border-dashed border-slate-600 rounded-lg p-6 text-center hover:border-slate-500 transition-colors">
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="mt-2 text-sm text-slate-300">
                  <span className="font-medium text-green-400">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-slate-500">
                  PDF, DOC, DOCX, XLS, XLSX, PNG, JPG up to 10MB each
                </p>
              </label>
            </div>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-white">Uploaded Files</h3>
                <div className="space-y-2">
                  {uploadedFiles.map((file) => (
                    <div key={file.id} className="flex items-center justify-between bg-slate-700 rounded p-3">
                      <div className="flex items-center space-x-3">
                        <svg className="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <div>
                          <p className="text-sm text-white">{file.name}</p>
                          <p className="text-xs text-slate-400">{formatFileSize(file.size)}</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile(file.id)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Form Actions */}
        <div className="flex items-center justify-end space-x-4 pt-6">
          <Link
            href="/admin/tenders"
            className="inline-flex items-center px-4 py-2 border border-slate-600 rounded-md text-sm font-medium text-slate-300 hover:text-white hover:border-slate-500"
          >
            Cancel
          </Link>
          <button
            type="submit"
            disabled={loading || !nextTenderId}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating Tender...
              </div>
            ) : (
              'Create Tender'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}