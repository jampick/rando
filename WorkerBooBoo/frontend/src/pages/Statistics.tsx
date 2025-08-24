import React, { useState, useEffect } from 'react'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  ExclamationTriangleIcon,
  ChartBarIcon,
  MapPinIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'

interface StatisticsData {
  total_incidents: number
  total_fatalities: number
  total_injuries: number
  incidents_by_year: Record<string, number>
  incidents_by_state: Record<string, number>
  incidents_by_industry: Record<string, number>
  incidents_by_type: Record<string, number>
  average_penalty: number
  total_penalties: number
}

interface TrendData {
  period: string
  total: number
  fatalities: number
  injuries: number
}

const Statistics: React.FC = () => {
  const [stats, setStats] = useState<StatisticsData | null>(null)
  const [trends, setTrends] = useState<TrendData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPeriod, setSelectedPeriod] = useState('monthly')

  useEffect(() => {
    fetchStatistics()
    fetchTrends()
  }, [selectedPeriod])

  const fetchStatistics = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/statistics/overview')
      setStats(response.data)
    } catch (err) {
      setError('Failed to load statistics')
      console.error('Error fetching stats:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchTrends = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/statistics/trends?period=${selectedPeriod}`)
      setTrends(response.data.trends)
    } catch (err) {
      console.error('Error fetching trends:', err)
    }
  }

  const COLORS = ['#dc2626', '#ea580c', '#ca8a04', '#16a34a', '#0891b2']

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="mx-auto h-12 w-12 text-red-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error loading statistics</h3>
        <p className="mt-1 text-sm text-gray-500">{error}</p>
      </div>
    )
  }

  // Prepare data for charts
  const yearData = Object.entries(stats.incidents_by_year).map(([year, count]) => ({
    year,
    incidents: count
  }))

  const stateData = Object.entries(stats.incidents_by_state)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10)
    .map(([state, count]) => ({
      state,
      incidents: count
    }))

  const industryData = Object.entries(stats.incidents_by_industry)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 8)
    .map(([industry, count]) => ({
      industry: industry.length > 20 ? industry.substring(0, 20) + '...' : industry,
      incidents: count
    }))

  const typeData = Object.entries(stats.incidents_by_type).map(([type, count]) => ({
    name: type.charAt(0).toUpperCase() + type.slice(1),
    value: count
  }))

  const trendData = trends.map(trend => ({
    period: trend.period,
    total: trend.total,
    fatalities: trend.fatalities,
    injuries: trend.injuries
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Safety Statistics</h1>
        <p className="mt-2 text-gray-600">
          Comprehensive analysis of workplace safety incidents and trends
        </p>
      </div>

      {/* Summary Cards */}
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
              <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
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

      {/* Trends Chart */}
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-medium text-gray-900">Incident Trends Over Time</h2>
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            className="input-field w-32"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="total" stroke="#3b82f6" strokeWidth={2} name="Total Incidents" />
            <Line type="monotone" dataKey="fatalities" stroke="#dc2626" strokeWidth={2} name="Fatalities" />
            <Line type="monotone" dataKey="injuries" stroke="#ea580c" strokeWidth={2} name="Injuries" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Incidents by Year */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Incidents by Year</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={yearData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="incidents" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Incidents by Type */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Incidents by Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={typeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {typeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Geographic and Industry Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top States */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top States by Incidents</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stateData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="state" type="category" width={80} />
              <Tooltip />
              <Bar dataKey="incidents" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Industries */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top Industries by Incidents</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={industryData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="industry" type="category" width={100} />
              <Tooltip />
              <Bar dataKey="incidents" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Statistics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Financial Impact</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total Penalties Issued</span>
              <span className="font-semibold text-gray-900">
                ${stats.total_penalties.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Average Penalty Amount</span>
              <span className="font-semibold text-gray-900">
                ${stats.average_penalty.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Incidents with Citations</span>
              <span className="font-semibold text-gray-900">
                {((stats.total_incidents * 0.3)).toFixed(0)} (estimated)
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Safety Insights</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-start">
              <div className="flex-shrink-0 w-2 h-2 bg-red-500 rounded-full mt-2 mr-3"></div>
              <p className="text-gray-700">
                <strong>Fatalities:</strong> {((stats.total_fatalities / stats.total_incidents) * 100).toFixed(1)}% of all incidents
              </p>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3"></div>
              <p className="text-gray-700">
                <strong>Injuries:</strong> {((stats.total_injuries / stats.total_incidents) * 100).toFixed(1)}% of all incidents
              </p>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></div>
              <p className="text-gray-700">
                <strong>Prevention:</strong> Early reporting and proper training can reduce incidents by up to 60%
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Statistics
