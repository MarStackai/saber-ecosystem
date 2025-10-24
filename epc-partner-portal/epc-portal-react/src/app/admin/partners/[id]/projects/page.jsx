'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

export default function PartnerProjectsPage() {
  const params = useParams()
  const [projects, setProjects] = useState([])
  const [partner, setPartner] = useState(null)
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    const loadPartnerProjects = async () => {
      try {
        // Simulated data - replace with actual API call using params.id
        setPartner({
          id: params.id,
          companyName: 'Solar Solutions Ltd',
          rating: 4.8
        })

        setProjects([
          {
            id: 1,
            tenderId: 'SABER-2024-001',
            projectName: 'Birmingham Solar Farm',
            status: 'in-progress',
            value: '£2.8M',
            startDate: '2024-03-01',
            completionDate: '2024-09-30',
            progress: 35,
            client: 'Birmingham City Council'
          },
          {
            id: 2,
            tenderId: 'SABER-2024-002',
            projectName: 'Manchester Office Complex',
            status: 'in-progress',
            value: '£850K',
            startDate: '2024-02-15',
            completionDate: '2024-06-30',
            progress: 65,
            client: 'Manchester Business Park'
          },
          {
            id: 3,
            tenderId: 'SABER-2023-045',
            projectName: 'Leeds Warehouse Solar',
            status: 'completed',
            value: '£1.2M',
            startDate: '2023-09-01',
            completionDate: '2024-02-28',
            progress: 100,
            client: 'Leeds Distribution Center',
            rating: 4.9
          },
          {
            id: 4,
            tenderId: 'SABER-2023-032',
            projectName: 'Liverpool Residential Development',
            status: 'completed',
            value: '£620K',
            startDate: '2023-06-15',
            completionDate: '2023-11-30',
            progress: 100,
            client: 'Liverpool Housing Association',
            rating: 4.7
          },
          {
            id: 5,
            tenderId: 'SABER-2024-008',
            projectName: 'Bristol Battery Storage',
            status: 'bidding',
            value: '£1.5M',
            submissionDate: '2024-04-15',
            client: 'Bristol Energy Hub'
          }
        ])
      } catch (error) {
        console.error('Error loading partner projects:', error)
      } finally {
        setLoading(false)
      }
    }

    loadPartnerProjects()
  }, [params.id])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-slate-400">Loading projects...</div>
      </div>
    )
  }

  const getStatusBadge = (status) => {
    const badges = {
      'in-progress': 'bg-blue-900/20 text-blue-400 border-blue-800/30',
      'completed': 'bg-green-900/20 text-green-400 border-green-800/30',
      'bidding': 'bg-yellow-900/20 text-yellow-400 border-yellow-800/30',
      'cancelled': 'bg-red-900/20 text-red-400 border-red-800/30'
    }
    return badges[status] || badges['in-progress']
  }

  const filteredProjects = filter === 'all'
    ? projects
    : projects.filter(p => p.status === filter)

  const stats = {
    total: projects.length,
    active: projects.filter(p => p.status === 'in-progress').length,
    completed: projects.filter(p => p.status === 'completed').length,
    totalValue: projects.reduce((sum, p) => {
      const value = parseFloat(p.value.replace(/[£M,K]/g, ''))
      return sum + (p.value.includes('M') ? value * 1000000 : value * 1000)
    }, 0)
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-2 text-sm text-slate-400 mb-4">
          <Link href="/admin/partners" className="hover:text-white">Partners</Link>
          <span>/</span>
          <Link href={`/admin/partners/${params.id}`} className="hover:text-white">{partner?.companyName}</Link>
          <span>/</span>
          <span className="text-white">Projects</span>
        </div>
        <h1 className="text-3xl font-bold text-white">{partner?.companyName} - Projects</h1>
        <p className="mt-2 text-slate-400">All tender projects and submissions</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
          <p className="text-sm text-slate-400">Total Projects</p>
          <p className="text-2xl font-bold text-white">{stats.total}</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
          <p className="text-sm text-slate-400">Active Projects</p>
          <p className="text-2xl font-bold text-blue-400">{stats.active}</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
          <p className="text-sm text-slate-400">Completed</p>
          <p className="text-2xl font-bold text-green-400">{stats.completed}</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
          <p className="text-sm text-slate-400">Total Value</p>
          <p className="text-2xl font-bold text-white">£{(stats.totalValue / 1000000).toFixed(1)}M</p>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-6">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-green-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            All Projects
          </button>
          <button
            onClick={() => setFilter('in-progress')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'in-progress'
                ? 'bg-green-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            In Progress
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'completed'
                ? 'bg-green-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Completed
          </button>
          <button
            onClick={() => setFilter('bidding')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'bidding'
                ? 'bg-green-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Bidding
          </button>
        </div>
      </div>

      {/* Projects List */}
      {filteredProjects.length === 0 ? (
        <div className="text-center py-8 text-slate-400">No projects found</div>
      ) : (
        <div className="space-y-4">
          {filteredProjects.map((project) => (
            <div key={project.id} className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white">{project.projectName}</h3>
                  <p className="text-sm text-slate-400 mt-1">Tender: {project.tenderId} • Client: {project.client}</p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-white">{project.value}</p>
                  <span className={`inline-flex px-2 py-1 mt-1 text-xs font-semibold rounded-full border ${getStatusBadge(project.status)}`}>
                    {project.status}
                  </span>
                </div>
              </div>

              {project.status === 'in-progress' && (
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-slate-400">Progress</span>
                    <span className="text-white">{project.progress}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 mt-2">
                    <span>Started: {project.startDate}</span>
                    <span>Due: {project.completionDate}</span>
                  </div>
                </div>
              )}

              {project.status === 'completed' && (
                <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
                  <div>
                    <p className="text-slate-400">Started</p>
                    <p className="text-white">{project.startDate}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Completed</p>
                    <p className="text-white">{project.completionDate}</p>
                  </div>
                  {project.rating && (
                    <div>
                      <p className="text-slate-400">Rating</p>
                      <div className="flex items-center gap-1">
                        <span className="text-yellow-400">{project.rating}</span>
                        <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {project.status === 'bidding' && (
                <div className="mb-4">
                  <p className="text-sm text-slate-400">
                    Submission deadline: <span className="text-white">{project.submissionDate}</span>
                  </p>
                </div>
              )}

              <div className="flex gap-3">
                <Link
                  href={`/admin/tenders/${project.id}`}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-500 transition-colors"
                >
                  View Tender
                </Link>
                {project.status === 'in-progress' && (
                  <button className="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors">
                    View Documents
                  </button>
                )}
                {project.status === 'completed' && (
                  <button className="px-4 py-2 text-sm font-medium text-slate-300 bg-slate-700 rounded-lg hover:bg-slate-600 transition-colors">
                    Download Report
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}