import React, { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { ArrowUpDown, TrendingUp, TrendingDown, DollarSign, Clock, Target } from 'lucide-react'
import { marketsApi, tradingApi } from '../services/api'
import { Topic, Order } from '../types'

const TradingPage: React.FC = () => {
  const location = useLocation()
  const [topics, setTopics] = useState<Topic[]>([])
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null)
  const [orderType, setOrderType] = useState<'buy' | 'sell' | 'short'>('buy')
  const [quantity, setQuantity] = useState<number>(1)
  const [priceLimit, setPriceLimit] = useState<number>(0)
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [auctionStatus, setAuctionStatus] = useState<any>(null)
  const [countdown, setCountdown] = useState<number>(0)

  useEffect(() => {
    fetchTopics()
    fetchOrders()
    fetchAuctionStatus()
    
    // Check if a topic was selected from the markets page
    if (location.state?.selectedTopic) {
      const { selectedTopic: navTopic } = location.state
      // Set the selected topic immediately, will be updated when topics are fetched
      setSelectedTopic({
        id: navTopic.id,
        ticker: navTopic.ticker,
        name: navTopic.name,
        current_price: navTopic.current_price,
        previous_price: navTopic.current_price,
        price_change_percent: 0,
        total_shares: 1000000,
        available_shares: 1000000,
        mentions_count: 0,
        fatigue_level: 0,
        is_active: true,
        category_id: 1,
        description: ''
      })
      setPriceLimit(navTopic.current_price)
    }

    // Refresh auction status every second for countdown
    const auctionInterval = setInterval(fetchAuctionStatus, 1000)
    
    return () => clearInterval(auctionInterval)
  }, [location.state])

  const fetchTopics = async () => {
    try {
      const response = await marketsApi.getTopics()
      setTopics(response.data)
      
      // If no topic was selected from navigation, select the first one
      if (!location.state?.selectedTopic && response.data.length > 0) {
        setSelectedTopic(response.data[0])
        setPriceLimit(response.data[0].current_price)
      } else if (location.state?.selectedTopic) {
        // Find the full topic data for the selected topic
        const fullTopic = response.data.find(t => t.id === location.state.selectedTopic.id)
        if (fullTopic) {
          setSelectedTopic(fullTopic)
          setPriceLimit(fullTopic.current_price)
        }
      }
    } catch (err) {
      console.error('Error fetching topics:', err)
    }
  }

  const fetchOrders = async () => {
    try {
      const response = await tradingApi.getOrders()
      setOrders(response.data)
    } catch (err) {
      console.error('Error fetching orders:', err)
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

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedTopic) return

    setLoading(true)
    setError(null)

    try {
      await tradingApi.createOrder({
        topic_id: selectedTopic.id,
        order_type: orderType,
        quantity,
        price_limit: priceLimit || undefined
      })
      
      // Refresh orders
      await fetchOrders()
      
      // Reset form
      setQuantity(1)
      setPriceLimit(selectedTopic.current_price)
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create order')
    } finally {
      setLoading(false)
    }
  }

  const handleCancelOrder = async (orderId: number) => {
    try {
      await tradingApi.cancelOrder(orderId)
      await fetchOrders()
    } catch (err) {
      console.error('Error cancelling order:', err)
    }
  }

  const getOrderTypeColor = (type: string) => {
    switch (type) {
      case 'buy': return 'text-green-400 bg-green-900 border-green-600'
      case 'sell': return 'text-red-400 bg-red-900 border-red-600'
      case 'short': return 'text-orange-400 bg-orange-900 border-orange-600'
      default: return 'text-gray-400 bg-gray-800 border-gray-600'
    }
  }

  const getOrderStatusColor = (status: string) => {
    switch (status) {
      case 'filled': return 'text-green-400 bg-green-900 border-green-600'
      case 'pending': return 'text-yellow-400 bg-yellow-900 border-yellow-600'
      case 'cancelled': return 'text-gray-400 bg-gray-800 border-gray-600'
      default: return 'text-gray-400 bg-gray-800 border-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Trading Terminal</h1>
          <p className="text-gray-400 mt-1">Place orders and manage positions</p>
        </div>
        <div className="flex items-center space-x-4 text-sm text-gray-400">
          {auctionStatus && (
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span>Next Reset:</span>
              <div className={`px-2 py-1 rounded text-xs font-mono ${
                countdown <= 10 ? 'bg-red-600 text-white' : 
                countdown <= 30 ? 'bg-yellow-600 text-black' : 
                'bg-green-600 text-white'
              }`}>
                {Math.floor(countdown / 60)}:{(countdown % 60).toString().padStart(2, '0')}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trading Form */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-white">Place Order</h2>
          </div>
          
          <form onSubmit={handleSubmitOrder} className="space-y-6 mt-6">
            {/* Topic Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Select Symbol
              </label>
              <select
                value={selectedTopic?.id || ''}
                onChange={(e) => {
                  const topic = topics.find(t => t.id === parseInt(e.target.value))
                  setSelectedTopic(topic || null)
                  if (topic) setPriceLimit(topic.current_price)
                }}
                className="input"
                required
              >
                <option value="">Choose a symbol...</option>
                {topics.map(topic => (
                  <option key={topic.id} value={topic.id}>
                    {topic.ticker} - {topic.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Order Type */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Order Type
              </label>
              <div className="grid grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setOrderType('buy')}
                  className={`btn ${orderType === 'buy' ? 'btn-buy' : 'btn-secondary'}`}
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  BUY
                </button>
                <button
                  type="button"
                  onClick={() => setOrderType('sell')}
                  className={`btn ${orderType === 'sell' ? 'btn-sell' : 'btn-secondary'}`}
                >
                  <TrendingDown className="w-4 h-4 mr-2" />
                  SELL
                </button>
                <button
                  type="button"
                  onClick={() => setOrderType('short')}
                  className={`btn ${orderType === 'short' ? 'btn-short' : 'btn-secondary'}`}
                >
                  <ArrowUpDown className="w-4 h-4 mr-2" />
                  SHORT
                </button>
              </div>
            </div>

            {/* Quantity */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Quantity
              </label>
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                className="input"
                required
              />
            </div>

            {/* Price Limit */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-3">
                Price Limit (optional)
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="number"
                  step="0.0001"
                  min="0"
                  value={priceLimit}
                  onChange={(e) => setPriceLimit(parseFloat(e.target.value) || 0)}
                  className="input pl-10"
                  placeholder="Market price"
                />
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Leave empty for market order
              </p>
            </div>

            {/* Current Price Display */}
            {selectedTopic && (
              <div className="bg-gray-800 border border-gray-700 p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-gray-400">Current Price</div>
                  <Target className="w-4 h-4 text-gray-400" />
                </div>
                <div className="text-2xl font-bold text-white font-mono">
                  ${selectedTopic.current_price.toFixed(4)}
                </div>
                <div className={`text-sm font-semibold ${
                  selectedTopic.price_change_percent > 0 ? 'text-green-400' : 
                  selectedTopic.price_change_percent < 0 ? 'text-red-400' : 'text-gray-400'
                }`}>
                  {selectedTopic.price_change_percent > 0 ? '+' : ''}
                  {selectedTopic.price_change_percent.toFixed(2)}%
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-900 border border-red-600 text-red-400 px-4 py-3 rounded">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !selectedTopic}
              className={`btn w-full text-lg py-4 ${
                orderType === 'buy' ? 'btn-buy' : 
                orderType === 'sell' ? 'btn-sell' : 'btn-short'
              }`}
            >
              {loading ? 'Placing Order...' : `${orderType.toUpperCase()} ${quantity} ${selectedTopic?.ticker || 'SHARES'}`}
            </button>
          </form>
        </div>

        {/* Orders List */}
        <div className="card">
          <div className="card-header">
            <h2 className="text-xl font-semibold text-white">Active Orders</h2>
          </div>
          
          {orders.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-gray-400">No active orders</p>
              <p className="text-sm text-gray-500 mt-1">Place your first order to get started</p>
            </div>
          ) : (
            <div className="space-y-4 mt-6">
              {orders.map(order => (
                <div key={order.id} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <div className="font-semibold text-white text-lg">
                        {topics.find(t => t.id === order.topic_id)?.ticker || 'Unknown'}
                      </div>
                      <div className="text-sm text-gray-400">
                        {topics.find(t => t.id === order.topic_id)?.name || 'Unknown Topic'}
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`px-3 py-1 rounded text-xs font-bold border ${getOrderTypeColor(order.order_type)}`}>
                        {order.order_type.toUpperCase()}
                      </span>
                      <div className={`mt-2 px-3 py-1 rounded text-xs font-bold border ${getOrderStatusColor(order.status)}`}>
                        {order.status.toUpperCase()}
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Quantity:</span>
                      <span className="ml-2 font-semibold text-white">{order.quantity}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Price:</span>
                      <span className="ml-2 font-semibold text-white font-mono">
                        {order.price_limit ? `$${order.price_limit.toFixed(4)}` : 'Market'}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-400">Filled:</span>
                      <span className="ml-2 font-semibold text-white">{order.filled_quantity}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Time:</span>
                      <span className="ml-2 font-semibold text-white">
                        {new Date(order.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                  
                  {order.status === 'pending' && (
                    <div className="mt-4 pt-3 border-t border-gray-700">
                      <button
                        onClick={() => handleCancelOrder(order.id)}
                        className="btn btn-danger text-sm"
                      >
                        Cancel Order
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TradingPage
