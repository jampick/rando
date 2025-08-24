import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { 
  MapIcon, 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  ShieldExclamationIcon,
  BuildingOfficeIcon,
  CalendarIcon
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'
import axios from 'axios'

interface DashboardStats {
  total_incidents: number
  total_fatalities: number
  total_injuries: number
  average_penalty: number
  total_penalties: number
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      setLoading(true)
      const response = await axios.get('http://localhost:8000/api/statistics/overview')
      setStats(response.data)
    } catch (err) {
      setError('Failed to load dashboard statistics')
      console.error('Error fetching stats:', err)
    } finally {
      setLoading(false)
    }
  }

  const quickActions = [
    {
      name: 'View Map',
      description: 'Explore incidents on an interactive map',
      href: '/map',
      icon: MapIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'Statistics',
      description: 'Detailed analytics and trends',
      href: '/statistics',
      icon: ChartBarIcon,
      color: 'bg-green-500',
    },
    {
      name: 'Recent Incidents',
      description: 'Latest workplace safety incidents',
      href: '/map',
      icon: ExclamationTriangleIcon,
      color: 'bg-red-500',
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading dashboard</h3>
        <p className="mt-1 text-sm text-gray-500">{error}</p>
        <div className="mt-6">
          <button
            onClick={fetchDashboardStats}
            className="btn-primary"
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Workplace Safety Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Monitor and analyze workplace injuries, fatalities, and safety violations
        </p>
        <p className="mt-1 text-sm text-gray-500">
          Last updated: {format(new Date(), 'MMM dd, yyyy HH:mm')}
        </p>
      </div>

      {/* Key Statistics */}
      {stats && (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-red-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Incidents</p>
                <p className="text-2xl font-semibold text-gray-900">{stats.total_incidents.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ShieldExclamationIcon className="h-8 w-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Fatalities</p>
                <p className="text-2xl font-semibold text-red-600">{stats.total_fatalities.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-8 w-8 text-orange-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Injuries</p>
                <p className="text-2xl font-semibold text-orange-600">{stats.total_injuries.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BuildingOfficeIcon className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Avg. Penalty</p>
                <p className="text-2xl font-semibold text-blue-600">
                  ${stats.average_penalty.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {quickActions.map((action) => (
            <Link
              key={action.name}
              to={action.href}
              className="card hover:shadow-md transition-shadow duration-200"
            >
              <div className="flex items-center">
                <div className={`flex-shrink-0 p-2 rounded-lg ${action.color}`}>
                  <action.icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <h3 className="text-sm font-medium text-gray-900">{action.name}</h3>
                  <p className="text-sm text-gray-500">{action.description}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900">Recent Activity</h2>
          <Link to="/map" className="text-sm text-primary-600 hover:text-primary-500">
            View all →
          </Link>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-red-100 rounded-full flex items-center justify-center">
                <ExclamationTriangleIcon className="h-4 w-4 text-red-600" />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                New fatality incident reported
              </p>
              <p className="text-sm text-gray-500">
                Construction industry - New York, NY
              </p>
            </div>
            <div className="flex-shrink-0 text-sm text-gray-500">
              <CalendarIcon className="h-4 w-4 inline mr-1" />
              2 hours ago
            </div>
          </div>

          <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-orange-100 rounded-full flex items-center justify-center">
                <ExclamationTriangleIcon className="h-4 w-4 text-orange-600" />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                Injury incident investigation closed
              </p>
              <p className="text-sm text-gray-500">
                Manufacturing industry - Chicago, IL
              </p>
            </div>
            <div className="flex-shrink-0 text-sm text-gray-500">
              <CalendarIcon className="h-4 w-4 inline mr-1" />
              1 day ago
            </div>
          </div>

          <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex-shrink-0">
              <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                <BuildingOfficeIcon className="h-4 w-4 text-blue-600" />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                New company added to database
              </p>
              <p className="text-sm text-gray-500">
                Chemical manufacturing - Houston, TX
              </p>
            </div>
            <div className="flex-shrink-0 text-sm text-gray-500">
              <CalendarIcon className="h-4 w-4 inline mr-1" />
              3 days ago
            </div>
          </div>
        </div>
      </div>

      {/* Safety Tips */}
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <h2 className="text-lg font-medium text-blue-900 mb-3">Safety Tip of the Day</h2>
        <p className="text-blue-800">
          Always ensure proper fall protection equipment is worn when working at heights above 6 feet. 
          Regular safety training and equipment inspections can prevent serious workplace accidents.
        </p>
        <div className="mt-4 text-sm text-blue-700">
          <strong>Remember:</strong> Safety is everyone's responsibility. Report hazards immediately.
        </div>
      </div>
    </div>
  )
}

export default Dashboard
