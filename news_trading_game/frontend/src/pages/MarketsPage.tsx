import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { TrendingUp, TrendingDown, Activity, Eye, BarChart3, Zap, Clock } from 'lucide-react'
import { marketsApi } from '../services/api'
import { MarketData } from '../types'
import { usePriceUpdates } from '../hooks/useWebSocket'

const MarketsPage: React.FC = () => {
  const navigate = useNavigate()
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [auctionStatus, setAuctionStatus] = useState<any>(null)
  const [countdown, setCountdown] = useState<number>(0)

  // Get all topic IDs for price updates
  const topicIds = marketData.map(topic => topic.topic_id)
  const priceUpdates = usePriceUpdates(topicIds)

  useEffect(() => {
    fetchMarketData()
    fetchAuctionStatus()
    
    // Refresh market data every 30 seconds
    const marketInterval = setInterval(fetchMarketData, 30000)
    
    // Refresh auction status every second for countdown
    const auctionInterval = setInterval(fetchAuctionStatus, 1000)
    
    return () => {
      clearInterval(marketInterval)
      clearInterval(auctionInterval)
    }
  }, [])

  const fetchMarketData = async () => {
    try {
      const response = await marketsApi.getMarketSnapshot()
      setMarketData(response.data.topics)
      setError(null)
    } catch (err) {
      setError('Failed to fetch market data')
      console.error('Error fetching market data:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchAuctionStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/markets/auction-status')
      const data = await response.json()
      setAuctionStatus(data)
      setCountdown(data.seconds_until_next_auction || 0)
    } catch (err) {
      console.error('Error fetching auction status:', err)
    }
  }

  const getPriceChangeColor = (change: number) => {
    if (change > 0) return 'price-positive'
    if (change < 0) return 'price-negative'
    return 'price-neutral'
  }

  const getPriceChangeIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="w-4 h-4" />
    if (change < 0) return <TrendingDown className="w-4 h-4" />
    return <Activity className="w-4 h-4" />
  }

  const handleTradeClick = (topic: MarketData) => {
    // Navigate to trading page with the selected topic
    navigate('/trading', { 
      state: { 
        selectedTopic: {
          id: topic.topic_id,
          ticker: topic.ticker,
          name: topic.name,
          current_price: topic.current_price
        }
      }
    })
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-400">{error}</p>
        <button 
          onClick={fetchMarketData}
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
        <div>
          <h1 className="text-3xl font-bold text-white">Live Markets</h1>
          <p className="text-gray-400 mt-1">Real-time news topic trading</p>
        </div>
        <div className="flex items-center space-x-4 text-sm text-gray-400">
          <div className="flex items-center space-x-2">
            <div className="status-indicator status-online"></div>
            <span>Live</span>
          </div>
          {auctionStatus && (
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>Next Reset:</span>
              </div>
              <div className={`px-2 py-1 rounded text-xs font-mono ${
                countdown <= 10 ? 'bg-red-600 text-white' : 
                countdown <= 30 ? 'bg-yellow-600 text-black' : 
                'bg-green-600 text-white'
              }`}>
                {Math.floor(countdown / 60)}:{(countdown % 60).toString().padStart(2, '0')}
              </div>
            </div>
          )}
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Market Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Active Topics</p>
              <p className="text-3xl font-bold text-white font-mono">{marketData.length}</p>
            </div>
            <Activity className="w-8 h-8 text-blue-400" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Gainers</p>
              <p className="text-3xl font-bold text-green-400 font-mono">
                {marketData.filter(t => t.price_change_percent > 0).length}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-400" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Losers</p>
              <p className="text-3xl font-bold text-red-400 font-mono">
                {marketData.filter(t => t.price_change_percent < 0).length}
              </p>
            </div>
            <TrendingDown className="w-8 h-8 text-red-400" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-400">Total Volume</p>
              <p className="text-3xl font-bold text-white font-mono">
                {(marketData.reduce((sum, t) => sum + t.volume_24h, 0) / 1000).toFixed(0)}K
              </p>
            </div>
            <BarChart3 className="w-8 h-8 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Market Table */}
      <div className="market-table">
        <div className="card-header">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Market Overview</h2>
            <div className="flex items-center space-x-2 text-sm text-gray-400">
              <Zap className="w-4 h-4" />
              <span>Real-time updates</span>
            </div>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Change
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Volume
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Mentions
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Fatigue
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody>
              {marketData.map((topic) => {
                // Use real-time price update if available
                const currentPrice = priceUpdates.get(topic.topic_id)?.price || topic.current_price
                const priceChange = currentPrice - topic.previous_price
                const priceChangePercent = topic.previous_price > 0 
                  ? (priceChange / topic.previous_price) * 100 
                  : 0

                return (
                  <tr key={topic.topic_id} className="hover:bg-gray-800 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-semibold text-white">
                          {topic.ticker}
                        </div>
                        <div className="text-sm text-gray-400">
                          {topic.name}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="ticker-price text-white">
                        ${currentPrice.toFixed(4)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`flex items-center ${getPriceChangeColor(priceChangePercent)}`}>
                        {getPriceChangeIcon(priceChangePercent)}
                        <span className="ml-2 ticker-change">
                          {priceChangePercent > 0 ? '+' : ''}{priceChangePercent.toFixed(2)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 font-mono">
                      {(topic.volume_24h / 1000).toFixed(0)}K
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 font-mono">
                      {topic.mentions_count.toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-full bg-gray-700 rounded-full h-2 mr-2">
                          <div 
                            className={`h-2 rounded-full transition-all ${
                              topic.fatigue_level > 0.7 ? 'bg-red-500' : 
                              topic.fatigue_level > 0.4 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${topic.fatigue_level * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-400 font-mono">
                          {(topic.fatigue_level * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button 
                        onClick={() => handleTradeClick(topic)}
                        className="btn btn-primary text-xs px-3 py-1 hover:bg-blue-600 transition-colors"
                      >
                        Trade
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default MarketsPage
