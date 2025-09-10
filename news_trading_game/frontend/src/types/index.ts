// API Types
export interface Topic {
  id: number
  name: string
  ticker: string
  description?: string
  category_id: number
  current_price: number
  previous_price: number
  price_change_percent: number
  total_shares: number
  available_shares: number
  mentions_count: number
  fatigue_level: number
  is_active: boolean
}

export interface TopicDetail extends Topic {
  category: Category
  volume_24h: number
  high_24h: number
  low_24h: number
}

export interface Category {
  id: number
  name: string
  display_name: string
  market_cap: number
  is_active: boolean
}

export interface MarketData {
  topic_id: number
  ticker: string
  name: string
  current_price: number
  previous_price: number
  price_change: number
  price_change_percent: number
  volume_24h: number
  mentions_count: number
  fatigue_level: number
}

export interface MarketSnapshot {
  timestamp: string
  topics: MarketData[]
}

export interface Order {
  id: number
  user_id: number
  topic_id: number
  order_type: 'buy' | 'sell' | 'short'
  quantity: number
  price_limit?: number
  status: 'pending' | 'filled' | 'cancelled' | 'partially_filled'
  filled_quantity: number
  average_fill_price?: number
  created_at: string
  updated_at: string
}

export interface Position {
  id: number
  topic_id: number
  topic_name: string
  topic_ticker: string
  quantity: number
  average_cost: number
  current_price: number
  market_value: number
  unrealized_pnl: number
  unrealized_pnl_percent: number
}

export interface Portfolio {
  total_value: number
  cash_balance: number
  positions: Position[]
  total_unrealized_pnl: number
  total_unrealized_pnl_percent: number
}

export interface Trade {
  id: number
  topic_id: number
  topic_name: string
  topic_ticker: string
  order_type: 'buy' | 'sell' | 'short'
  quantity: number
  price: number
  realized_pnl: number
  auction_id: number
  created_at: string
}

export interface User {
  id: number
  username: string
  email: string
  cash_balance: number
  is_active: boolean
  created_at: string
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

export interface PriceUpdateMessage {
  type: 'price_update'
  topic_id: number
  ticker: string
  price: number
  change_percent: number
  volume: number
  timestamp: string
}

export interface AuctionStatusMessage {
  type: 'auction_status'
  status: 'scheduled' | 'running' | 'completed'
  next_auction_time?: string
  current_auction_id?: number
  timestamp: string
}
