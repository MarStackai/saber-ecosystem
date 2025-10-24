'use client'

import { useState, useEffect } from 'react'

export default function PartnerAnalyticsPage() {
  const [analytics, setAnalytics] = useState({
    overview: {
      totalPartners: 32,
      newThisMonth: 5,
      averageRating: 4.7,
      activeProjects: 24
    },
    performance: [],
    categories: [],
    trends: []
  })
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('month')

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        // Simulated data - replace with actual API call
        setAnalytics({
          overview: {
            totalPartners: 32,
            newThisMonth: 5,
            averageRating: 4.7,
            activeProjects: 24
          },
          performance: [
            { name: 'Solar Solutions Ltd', projects: 45, revenue: 2450000, rating: 4.8 },
            { name: 'WindPower Systems', projects: 32, revenue: 1890000, rating: 4.9 },
            { name: 'GreenTech Innovations', projects: 28, revenue: 1560000, rating: 4.6 },
            { name: 'Sustainable Energy Co', projects: 56, revenue: 3200000, rating: 4.7 },
            { name: 'EcoFuture Partners', projects: 23, revenue: 980000, rating: 4.5 },
          ],
          categories: [
            { category: 'Installer', count: 12, percentage: 37.5 },
            { category: 'Developer', count: 8, percentage: 25 },
            { category: 'Consultant', count: 7, percentage: 21.9 },
            { category: 'Supplier', count: 5, percentage: 15.6 },
          ],
          trends: [
            { month: 'Jan', applications: 12, approvals: 8 },
            { month: 'Feb', applications: 15, approvals: 11 },
            { month: 'Mar', applications: 18, approvals: 14 },
            { month: 'Apr', applications: 22, approvals: 17 },
            { month: 'May', applications: 20, approvals: 16 },
            { month: 'Jun', applications: 25, approvals: 19 },
          ]
        })
      } catch (error) {
        console.error('Error loading analytics:', error)
      } finally {
        setLoading(false)
      }
    }

    loadAnalytics()
  }, [timeRange])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-slate-400">Loading analytics...</div>
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Partner Analytics</h1>
        <p className="mt-2 text-slate-400">Performance metrics and insights</p>
      </div>

      {/* Time Range Selector */}
      <div className="mb-6">
        <div className="inline-flex bg-slate-800/50 rounded-lg p-1">
          <button
            onClick={() => setTimeRange('week')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              timeRange === 'week'
                ? 'bg-green-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Week
          </button>
          <button
            onClick={() => setTimeRange('month')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              timeRange === 'month'
                ? 'bg-green-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Month
          </button>
          <button
            onClick={() => setTimeRange('quarter')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              timeRange === 'quarter'
                ? 'bg-green-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Quarter
          </button>
          <button
            onClick={() => setTimeRange('year')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              timeRange === 'year'
                ? 'bg-green-600 text-white'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Year
          </button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-400">Total Partners</p>
              <p className="mt-2 text-3xl font-bold text-white">{analytics.overview.totalPartners}</p>
            </div>
            <div className="ml-4">
              <div className="p-3 bg-green-600/20 rounded-lg">
                <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>
          <p className="mt-2 text-sm text-green-400">+{analytics.overview.newThisMonth} this month</p>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-400">Average Rating</p>
              <p className="mt-2 text-3xl font-bold text-white">{analytics.overview.averageRating}</p>
            </div>
            <div className="ml-4">
              <div className="p-3 bg-yellow-600/20 rounded-lg">
                <svg className="w-6 h-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
            </div>
          </div>
          <p className="mt-2 text-sm text-slate-400">Out of 5.0</p>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-400">Active Projects</p>
              <p className="mt-2 text-3xl font-bold text-white">{analytics.overview.activeProjects}</p>
            </div>
            <div className="ml-4">
              <div className="p-3 bg-blue-600/20 rounded-lg">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
            </div>
          </div>
          <p className="mt-2 text-sm text-slate-400">Across all partners</p>
        </div>

        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <div className="flex items-center">
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-400">Total Revenue</p>
              <p className="mt-2 text-3xl font-bold text-white">£10.1M</p>
            </div>
            <div className="ml-4">
              <div className="p-3 bg-green-600/20 rounded-lg">
                <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
          <p className="mt-2 text-sm text-green-400">+12% from last month</p>
        </div>
      </div>

      {/* Performance Table */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-4">Top Performing Partners</h2>
        <div className="overflow-hidden bg-slate-800/50 shadow ring-1 ring-slate-700 rounded-lg">
          <table className="min-w-full divide-y divide-slate-700">
            <thead className="bg-slate-800/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Partner
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Projects
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Revenue
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Rating
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {analytics.performance.map((partner, index) => (
                <tr key={index} className="hover:bg-slate-700/30">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {partner.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                    {partner.projects}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                    £{(partner.revenue / 1000000).toFixed(2)}M
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm text-yellow-400 mr-1">{partner.rating}</span>
                      <svg className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Partner Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Partner Categories</h2>
          <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
            {analytics.categories.map((category, index) => (
              <div key={index} className="mb-4 last:mb-0">
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-slate-300">{category.category}</span>
                  <span className="text-sm text-slate-400">{category.count} partners ({category.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${category.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Application Trends</h2>
          <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
            <div className="space-y-3">
              {analytics.trends.map((trend, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-slate-400 w-12">{trend.month}</span>
                  <div className="flex-1 mx-4">
                    <div className="flex gap-2">
                      <div className="flex-1">
                        <div className="text-xs text-slate-400 mb-1">Applications</div>
                        <div className="w-full bg-slate-700 rounded-full h-4">
                          <div
                            className="bg-blue-600 h-4 rounded-full flex items-center justify-end pr-1"
                            style={{ width: `${(trend.applications / 25) * 100}%` }}
                          >
                            <span className="text-xs text-white">{trend.applications}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex-1">
                        <div className="text-xs text-slate-400 mb-1">Approvals</div>
                        <div className="w-full bg-slate-700 rounded-full h-4">
                          <div
                            className="bg-green-600 h-4 rounded-full flex items-center justify-end pr-1"
                            style={{ width: `${(trend.approvals / 25) * 100}%` }}
                          >
                            <span className="text-xs text-white">{trend.approvals}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}