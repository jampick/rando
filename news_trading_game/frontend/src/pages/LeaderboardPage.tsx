import React, { useState, useEffect } from 'react'
import { Trophy, TrendingUp, Users } from 'lucide-react'
import { marketsApi } from '../services/api'

interface LeaderboardEntry {
  user_id: number
  username: string
  total_value: number
  cash_balance: number
  total_unrealized_pnl: number
  return_percent: number
}

const LeaderboardPage: React.FC = () => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [timeframe, setTimeframe] = useState('daily')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchLeaderboard()
  }, [timeframe])

  const fetchLeaderboard = async () => {
    try {
      setLoading(true)
      const response = await marketsApi.getLeaderboard(timeframe, 100)
      setLeaderboard(response.data.leaderboard)
      setError(null)
    } catch (err) {
      setError('Failed to fetch leaderboard')
      console.error('Error fetching leaderboard:', err)
    } finally {
      setLoading(false)
    }
  }

  const getRankIcon = (index: number) => {
    switch (index) {
      case 0: return '🥇'
      case 1: return '🥈'
      case 2: return '🥉'
      default: return `#${index + 1}`
    }
  }

  const getReturnColor = (returnPercent: number) => {
    if (returnPercent > 0) return 'text-green-600'
    if (returnPercent < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">{error}</p>
        <button 
          onClick={fetchLeaderboard}
          className="btn btn-primary mt-4"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Leaderboard</h1>
        
        {/* Timeframe Selector */}
        <div className="flex space-x-2">
          {['daily', 'weekly', 'all_time'].map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`btn ${
                timeframe === tf ? 'btn-primary' : 'btn-secondary'
              }`}
            >
              {tf.replace('_', ' ').toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Players</p>
              <p className="text-2xl font-bold text-gray-900">{leaderboard.length}</p>
            </div>
            <Users className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Top Performer</p>
              <p className="text-2xl font-bold text-green-600">
                {leaderboard.length > 0 ? leaderboard[0].username : 'N/A'}
              </p>
            </div>
            <Trophy className="w-8 h-8 text-yellow-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Best Return</p>
              <p className={`text-2xl font-bold ${
                leaderboard.length > 0 ? getReturnColor(leaderboard[0].return_percent) : 'text-gray-600'
              }`}>
                {leaderboard.length > 0 ? `${leaderboard[0].return_percent.toFixed(2)}%` : 'N/A'}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="card">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Player
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Total Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cash Balance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unrealized P&L
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Return %
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {leaderboard.map((entry, index) => (
                <tr key={entry.user_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className="text-lg font-bold">
                        {getRankIcon(index)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {entry.username}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      ${entry.total_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      ${entry.cash_balance.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`text-sm font-medium ${getReturnColor(entry.total_unrealized_pnl)}`}>
                      {entry.total_unrealized_pnl > 0 ? '+' : ''}
                      ${entry.total_unrealized_pnl.toLocaleString(undefined, { maximumFractionDigits: 2 })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`text-sm font-medium ${getReturnColor(entry.return_percent)}`}>
                      {entry.return_percent > 0 ? '+' : ''}
                      {entry.return_percent.toFixed(2)}%
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {leaderboard.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No players found</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default LeaderboardPage
