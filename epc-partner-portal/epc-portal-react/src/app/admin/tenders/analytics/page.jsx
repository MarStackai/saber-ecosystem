'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function TenderAnalyticsPage() {
  const [analytics, setAnalytics] = useState({
    overview: {
      totalTenders: 48,
      activeTenders: 12,
      totalValue: 45200000,
      averageSubmissions: 8.5,
      successRate: 78
    },
    byCategory: [],
    byStatus: [],
    timeline: [],
    topPartners: []
  })
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('quarter')

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        // Simulated data - replace with actual API call
        setAnalytics({
          overview: {
            totalTenders: 48,
            activeTenders: 12,
            totalValue: 45200000,
            averageSubmissions: 8.5,
            successRate: 78
          },
          byCategory: [
            { category: 'Solar Installation', count: 18, value: 22500000 },
            { category: 'Energy Storage', count: 8, value: 12000000 },
            { category: 'EV Infrastructure', count: 12, value: 8500000 },
            { category: 'Wind Power', count: 5, value: 1800000 },
            { category: 'Maintenance', count: 5, value: 400000 }
          ],
          byStatus: [
            { status: 'Open', count: 12, percentage: 25 },
            { status: 'Evaluating', count: 8, percentage: 16.7 },
            { status: 'Closed', count: 25, percentage: 52.1 },
            { status: 'Cancelled', count: 3, percentage: 6.2 }
          ],
          timeline: [
            { month: 'Jan', created: 6, closed: 4, value: 3200000 },
            { month: 'Feb', created: 8, closed: 5, value: 4500000 },
            { month: 'Mar', created: 10, closed: 7, value: 5800000 },
            { month: 'Apr', created: 9, closed: 6, value: 4200000 },
            { month: 'May', created: 7, closed: 8, value: 3900000 },
            { month: 'Jun', created: 8, closed: 5, value: 4100000 }
          ],
          topPartners: [
            { name: 'Solar Solutions Ltd', wins: 8, value: 8500000, successRate: 72 },
            { name: 'GreenTech Innovations', wins: 6, value: 5200000, successRate: 66 },
            { name: 'WindPower Systems', wins: 5, value: 4800000, successRate: 83 },
            { name: 'EcoFuture Partners', wins: 4, value: 3200000, successRate: 57 },
            { name: 'Sustainable Energy Co', wins: 3, value: 2100000, successRate: 60 }
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
        <h1 className="text-3xl font-bold text-white">Tender Analytics</h1>
        <p className="mt-2 text-slate-400">Performance metrics and insights for tender management</p>
      </div>

      {/* Time Range Selector */}
      <div className="mb-6">
        <div className="inline-flex bg-slate-800/50 rounded-lg p-1">
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <p className="text-sm font-medium text-slate-400">Total Tenders</p>
          <p className="mt-2 text-3xl font-bold text-white">{analytics.overview.totalTenders}</p>
          <p className="mt-1 text-sm text-green-400">+15% from last period</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <p className="text-sm font-medium text-slate-400">Active Tenders</p>
          <p className="mt-2 text-3xl font-bold text-green-400">{analytics.overview.activeTenders}</p>
          <p className="mt-1 text-sm text-slate-400">Currently open</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <p className="text-sm font-medium text-slate-400">Total Value</p>
          <p className="mt-2 text-3xl font-bold text-white">£{(analytics.overview.totalValue / 1000000).toFixed(1)}M</p>
          <p className="mt-1 text-sm text-green-400">+22% from last period</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <p className="text-sm font-medium text-slate-400">Avg Submissions</p>
          <p className="mt-2 text-3xl font-bold text-white">{analytics.overview.averageSubmissions}</p>
          <p className="mt-1 text-sm text-slate-400">Per tender</p>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <p className="text-sm font-medium text-slate-400">Success Rate</p>
          <p className="mt-2 text-3xl font-bold text-green-400">{analytics.overview.successRate}%</p>
          <p className="mt-1 text-sm text-slate-400">Completion rate</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Tender Timeline */}
        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <h2 className="text-lg font-semibold text-white mb-4">Tender Timeline</h2>
          <div className="space-y-3">
            {analytics.timeline.map((month, index) => (
              <div key={index}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">{month.month}</span>
                  <span className="text-slate-300">£{(month.value / 1000000).toFixed(1)}M</span>
                </div>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <div className="text-xs text-slate-400 mb-1">Created ({month.created})</div>
                    <div className="w-full bg-slate-700 rounded-full h-3">
                      <div
                        className="bg-green-600 h-3 rounded-full"
                        style={{ width: `${(month.created / 10) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-slate-400 mb-1">Closed ({month.closed})</div>
                    <div className="w-full bg-slate-700 rounded-full h-3">
                      <div
                        className="bg-blue-600 h-3 rounded-full"
                        style={{ width: `${(month.closed / 10) * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* By Category */}
        <div className="bg-slate-800/50 rounded-lg p-6 ring-1 ring-slate-700">
          <h2 className="text-lg font-semibold text-white mb-4">Tenders by Category</h2>
          <div className="space-y-3">
            {analytics.byCategory.map((cat, index) => (
              <div key={index}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm text-slate-300">{cat.category}</span>
                  <span className="text-sm text-slate-400">{cat.count} tenders • £{(cat.value / 1000000).toFixed(1)}M</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${(cat.count / 18) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Status Distribution */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-white mb-4">Status Distribution</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {analytics.byStatus.map((status, index) => {
            const colors = {
              'Open': 'bg-green-600/20 text-green-400 border-green-800/30',
              'Evaluating': 'bg-yellow-600/20 text-yellow-400 border-yellow-800/30',
              'Closed': 'bg-slate-600/20 text-slate-400 border-slate-800/30',
              'Cancelled': 'bg-red-600/20 text-red-400 border-red-800/30'
            }
            return (
              <div key={index} className="bg-slate-800/50 rounded-lg p-4 ring-1 ring-slate-700">
                <div className="flex items-center justify-between mb-2">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${colors[status.status]}`}>
                    {status.status}
                  </span>
                  <span className="text-2xl font-bold text-white">{status.count}</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${status.status === 'Open' ? 'bg-green-600' : status.status === 'Evaluating' ? 'bg-yellow-600' : status.status === 'Closed' ? 'bg-slate-600' : 'bg-red-600'}`}
                    style={{ width: `${status.percentage}%` }}
                  />
                </div>
                <p className="mt-1 text-xs text-slate-400">{status.percentage}% of total</p>
              </div>
            )
          })}
        </div>
      </div>

      {/* Top Performing Partners */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Top Performing Partners</h2>
        <div className="overflow-hidden bg-slate-800/50 shadow ring-1 ring-slate-700 rounded-lg">
          <table className="min-w-full divide-y divide-slate-700">
            <thead className="bg-slate-800/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Partner
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Wins
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Total Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Success Rate
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {analytics.topPartners.map((partner, index) => (
                <tr key={index} className="hover:bg-slate-700/30">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {partner.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                    {partner.wins}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                    £{(partner.value / 1000000).toFixed(1)}M
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-sm text-green-400 mr-2">{partner.successRate}%</span>
                      <div className="w-16 bg-slate-700 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${partner.successRate}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <Link href={`/admin/partners/${index + 1}`} className="text-green-400 hover:text-green-300">
                      View Profile
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}