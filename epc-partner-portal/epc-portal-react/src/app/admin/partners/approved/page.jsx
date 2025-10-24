'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function ApprovedPartnersPage() {
  const [partners, setPartners] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const loadApprovedPartners = async () => {
      try {
        // Simulated data - replace with actual API call
        setPartners([
          {
            id: 1,
            companyName: 'Solar Solutions Ltd',
            contactName: 'David Wilson',
            email: 'david@solarsolutions.com',
            phone: '+44 20 1234 5678',
            approvalDate: '2024-03-18',
            category: 'Installer',
            activeProjects: 3,
            completedProjects: 45,
            rating: 4.8
          },
          {
            id: 2,
            companyName: 'WindPower Systems',
            contactName: 'Emma Davis',
            email: 'emma@windpower.com',
            phone: '+44 20 9876 5432',
            approvalDate: '2024-03-12',
            category: 'Developer',
            activeProjects: 5,
            completedProjects: 32,
            rating: 4.9
          },
          {
            id: 3,
            companyName: 'GreenTech Innovations',
            contactName: 'James Miller',
            email: 'james@greentech.com',
            phone: '+44 20 5555 1234',
            approvalDate: '2024-03-05',
            category: 'Consultant',
            activeProjects: 2,
            completedProjects: 18,
            rating: 4.6
          },
          {
            id: 4,
            companyName: 'Sustainable Energy Co',
            contactName: 'Lisa Anderson',
            email: 'lisa@sustainableenergy.com',
            phone: '+44 20 7777 8888',
            approvalDate: '2024-02-28',
            category: 'Supplier',
            activeProjects: 7,
            completedProjects: 56,
            rating: 4.7
          },
        ])
      } catch (error) {
        console.error('Error loading approved partners:', error)
      } finally {
        setLoading(false)
      }
    }

    loadApprovedPartners()
  }, [])

  const filteredPartners = partners.filter(partner =>
    partner.companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.contactName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getRatingColor = (rating) => {
    if (rating >= 4.8) return 'text-green-400'
    if (rating >= 4.5) return 'text-yellow-400'
    return 'text-slate-400'
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Approved Partners</h1>
        <p className="mt-2 text-slate-400">Manage active EPC partners</p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <input
            type="text"
            placeholder="Search partners..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 bg-slate-700/50 text-white rounded-lg pl-10 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <svg
            className="absolute left-3 top-2.5 h-5 w-5 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </div>
      </div>

      {/* Partners Grid */}
      {loading ? (
        <div className="text-center py-8 text-slate-400">Loading approved partners...</div>
      ) : filteredPartners.length === 0 ? (
        <div className="text-center py-8 text-slate-400">No partners found</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredPartners.map((partner) => (
            <div key={partner.id} className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white">{partner.companyName}</h3>
                  <span className="inline-flex px-2 py-1 mt-1 text-xs font-semibold text-green-400 bg-green-900/20 rounded-full border border-green-800/30">
                    {partner.category}
                  </span>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${getRatingColor(partner.rating)}`}>
                    {partner.rating}
                  </div>
                  <div className="text-xs text-slate-400">Rating</div>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Contact</span>
                  <span className="text-sm text-white">{partner.contactName}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Email</span>
                  <span className="text-sm text-white">{partner.email}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Phone</span>
                  <span className="text-sm text-white">{partner.phone}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-slate-400">Approved</span>
                  <span className="text-sm text-white">{partner.approvalDate}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 py-4 border-t border-slate-700">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">{partner.activeProjects}</div>
                  <div className="text-xs text-slate-400">Active Projects</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{partner.completedProjects}</div>
                  <div className="text-xs text-slate-400">Completed Projects</div>
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <Link
                  href={`/admin/partners/${partner.id}/projects`}
                  className="flex-1 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-500 transition-colors text-center"
                >
                  View Projects
                </Link>
                <a
                  href={`mailto:${partner.email}?subject=Partner Communication - ${partner.companyName}`}
                  className="flex-1 px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors text-center"
                >
                  Contact Partner
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}