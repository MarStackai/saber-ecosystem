'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'

export default function PartnerDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const [partner, setPartner] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadPartnerDetails = async () => {
      try {
        // Simulated data - replace with actual API call using params.id
        const mockPartner = {
          id: params.id,
          companyName: 'Solar Solutions Ltd',
          contactName: 'David Wilson',
          email: 'david@solarsolutions.com',
          phone: '+44 20 1234 5678',
          website: 'https://solarsolutions.com',
          address: '123 Business Park, London, UK',
          status: 'approved',
          approvalDate: '2024-03-18',
          submittedDate: '2024-03-15',
          category: 'Installer',
          description: 'Leading solar panel installation company with over 10 years of experience in residential and commercial projects.',
          certifications: ['MCS', 'RECC', 'ISO 9001'],
          projectsCompleted: 45,
          activeProjects: 3,
          rating: 4.8,
          capabilities: [
            'Residential Solar Installation',
            'Commercial Solar Systems',
            'Battery Storage Solutions',
            'EV Charging Points'
          ],
          recentProjects: [
            { name: 'Birmingham Office Complex', value: '£250,000', status: 'completed' },
            { name: 'Manchester Warehouse', value: '£180,000', status: 'in-progress' },
            { name: 'Leeds Residential Development', value: '£320,000', status: 'in-progress' }
          ]
        }
        setPartner(mockPartner)
      } catch (error) {
        console.error('Error loading partner details:', error)
      } finally {
        setLoading(false)
      }
    }

    loadPartnerDetails()
  }, [params.id])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-slate-400">Loading partner details...</div>
      </div>
    )
  }

  if (!partner) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-slate-400">Partner not found</div>
      </div>
    )
  }

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
        <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
          <Link href="/admin/partners" className="hover:text-white">Partners</Link>
          <span>/</span>
          <span className="text-white">{partner.companyName}</span>
        </div>
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-white">{partner.companyName}</h1>
            <p className="mt-2 text-slate-400">{partner.description}</p>
          </div>
          <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full border ${getStatusBadge(partner.status)}`}>
            {partner.status}
          </span>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Information */}
          <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">Contact Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-slate-400">Contact Person</p>
                <p className="text-white">{partner.contactName}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Email</p>
                <p className="text-white">{partner.email}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Phone</p>
                <p className="text-white">{partner.phone}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Website</p>
                <a href={partner.website} target="_blank" rel="noopener noreferrer" className="text-green-400 hover:text-green-300">
                  {partner.website}
                </a>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-slate-400">Address</p>
                <p className="text-white">{partner.address}</p>
              </div>
            </div>
          </div>

          {/* Capabilities */}
          <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">Capabilities</h2>
            <div className="flex flex-wrap gap-2">
              {partner.capabilities.map((capability, index) => (
                <span key={index} className="px-3 py-1 bg-slate-700/50 text-slate-300 rounded-full text-sm">
                  {capability}
                </span>
              ))}
            </div>
          </div>

          {/* Recent Projects */}
          <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">Recent Projects</h2>
            <div className="space-y-3">
              {partner.recentProjects.map((project, index) => (
                <div key={index} className="flex justify-between items-center py-3 border-b border-slate-700 last:border-0">
                  <div>
                    <p className="text-white font-medium">{project.name}</p>
                    <p className="text-sm text-slate-400">Value: {project.value}</p>
                  </div>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    project.status === 'completed'
                      ? 'bg-green-900/20 text-green-400 border border-green-800/30'
                      : 'bg-blue-900/20 text-blue-400 border border-blue-800/30'
                  }`}>
                    {project.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Stats & Actions */}
        <div className="space-y-6">
          {/* Stats */}
          <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">Performance</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-slate-400">Rating</p>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-yellow-400">{partner.rating}</span>
                  <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                </div>
              </div>
              <div>
                <p className="text-sm text-slate-400">Completed Projects</p>
                <p className="text-2xl font-bold text-white">{partner.projectsCompleted}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Active Projects</p>
                <p className="text-2xl font-bold text-green-400">{partner.activeProjects}</p>
              </div>
            </div>
          </div>

          {/* Certifications */}
          <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">Certifications</h2>
            <div className="space-y-2">
              {partner.certifications.map((cert, index) => (
                <div key={index} className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-slate-300">{cert}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Dates */}
          <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
            <h2 className="text-lg font-semibold text-white mb-4">Timeline</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-slate-400">Application Submitted</p>
                <p className="text-white">{partner.submittedDate}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Approved</p>
                <p className="text-white">{partner.approvalDate}</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-3">
            <button className="w-full px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-500 transition-colors">
              Send Message
            </button>
            <button className="w-full px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors">
              View Documents
            </button>
            <button className="w-full px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors">
              Edit Partner
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}