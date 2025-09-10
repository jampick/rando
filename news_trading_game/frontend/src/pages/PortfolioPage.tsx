import React, { useState, useEffect } from 'react'
import { Wallet, TrendingUp, TrendingDown, DollarSign } from 'lucide-react'
import { portfolioApi } from '../services/api'
import { Portfolio, Trade } from '../types'

const PortfolioPage: React.FC = () => {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPortfolio()
    fetchTrades()
  }, [])

  const fetchPortfolio = async () => {
    try {
      const response = await portfolioApi.getPortfolio()
      setPortfolio(response.data)
      setError(null)
    } catch (err) {
      setError('Failed to fetch portfolio')
      console.error('Error fetching portfolio:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchTrades = async () => {
    try {
      const response = await portfolioApi.getTrades()
      setTrades(response.data)
    } catch (err) {
      console.error('Error fetching trades:', err)
    }
  }

  const getPnLColor = (pnl: number) => {
    if (pnl > 0) return 'text-green-600'
    if (pnl < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  const getPnLIcon = (pnl: number) => {
    if (pnl > 0) return <TrendingUp className="w-4 h-4" />
    if (pnl < 0) return <TrendingDown className="w-4 h-4" />
    return <DollarSign className="w-4 h-4" />
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
          onClick={fetchPortfolio}
          className="btn btn-primary mt-4"
        >
          Retry
        </button>
      </div>
    )
  }

  if (!portfolio) return null

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Value</p>
              <p className="text-2xl font-bold text-gray-900">
                ${portfolio.total_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </p>
            </div>
            <Wallet className="w-8 h-8 text-blue-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Cash Balance</p>
              <p className="text-2xl font-bold text-gray-900">
                ${portfolio.cash_balance.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-green-600" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Unrealized P&L</p>
              <p className={`text-2xl font-bold ${getPnLColor(portfolio.total_unrealized_pnl)}`}>
                ${portfolio.total_unrealized_pnl.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </p>
            </div>
            {getPnLIcon(portfolio.total_unrealized_pnl)}
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Return %</p>
              <p className={`text-2xl font-bold ${getPnLColor(portfolio.total_unrealized_pnl_percent)}`}>
                {portfolio.total_unrealized_pnl_percent > 0 ? '+' : ''}
                {portfolio.total_unrealized_pnl_percent.toFixed(2)}%
              </p>
            </div>
            {getPnLIcon(portfolio.total_unrealized_pnl_percent)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Positions */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Positions</h2>
          
          {portfolio.positions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No positions</p>
          ) : (
            <div className="space-y-3">
              {portfolio.positions.map(position => (
                <div key={position.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-medium">{position.topic_ticker}</div>
                      <div className="text-sm text-gray-500">{position.topic_name}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">
                        {position.quantity > 0 ? 'LONG' : 'SHORT'}
                      </div>
                      <div className={`text-sm ${getPnLColor(position.unrealized_pnl)}`}>
                        {position.unrealized_pnl > 0 ? '+' : ''}
                        {position.unrealized_pnl.toFixed(2)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Quantity:</span>
                      <span className="ml-1 font-medium">{position.quantity}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Avg Cost:</span>
                      <span className="ml-1 font-medium">${position.average_cost.toFixed(4)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Current Price:</span>
                      <span className="ml-1 font-medium">${position.current_price.toFixed(4)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Market Value:</span>
                      <span className="ml-1 font-medium">${position.market_value.toFixed(2)}</span>
                    </div>
                  </div>
                  
                  <div className="mt-2">
                    <div className="text-sm text-gray-500">P&L %</div>
                    <div className={`font-medium ${getPnLColor(position.unrealized_pnl_percent)}`}>
                      {position.unrealized_pnl_percent > 0 ? '+' : ''}
                      {position.unrealized_pnl_percent.toFixed(2)}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Trades */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Recent Trades</h2>
          
          {trades.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No trades yet</p>
          ) : (
            <div className="space-y-3">
              {trades.slice(0, 10).map(trade => (
                <div key={trade.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-medium">{trade.topic_ticker}</div>
                      <div className="text-sm text-gray-500">{trade.topic_name}</div>
                    </div>
                    <div className="text-right">
                      <div className={`font-medium ${
                        trade.order_type === 'buy' ? 'text-green-600' : 
                        trade.order_type === 'sell' ? 'text-red-600' : 'text-orange-600'
                      }`}>
                        {trade.order_type.toUpperCase()}
                      </div>
                      <div className={`text-sm ${getPnLColor(trade.realized_pnl)}`}>
                        {trade.realized_pnl > 0 ? '+' : ''}
                        ${trade.realized_pnl.toFixed(2)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Quantity:</span>
                      <span className="ml-1 font-medium">{trade.quantity}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Price:</span>
                      <span className="ml-1 font-medium">${trade.price.toFixed(4)}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Auction:</span>
                      <span className="ml-1 font-medium">#{trade.auction_id}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Time:</span>
                      <span className="ml-1 font-medium">
                        {new Date(trade.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default PortfolioPage
