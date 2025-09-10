import axios from 'axios'
import { Topic, TopicDetail, Category, MarketSnapshot, Order, Portfolio, Trade, User } from '../types'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Markets API
export const marketsApi = {
  getCategories: () => api.get<Category[]>('/markets/categories'),
  getTopics: (categoryId?: number, limit = 50) => 
    api.get<Topic[]>('/markets/topics', { 
      params: { category_id: categoryId, limit } 
    }),
  getTopicDetail: (topicId: number) => 
    api.get<TopicDetail>(`/markets/topics/${topicId}`),
  getMarketSnapshot: () => 
    api.get<MarketSnapshot>('/markets/market-snapshot'),
  getPriceHistory: (topicId: number, hours = 24) =>
    api.get(`/markets/topics/${topicId}/price-history`, {
      params: { hours }
    }),
  getLeaderboard: (timeframe = 'daily', limit = 100) =>
    api.get('/markets/leaderboard', {
      params: { timeframe, limit }
    }),
}

// Trading API
export const tradingApi = {
  createOrder: (orderData: {
    topic_id: number
    order_type: 'buy' | 'sell' | 'short'
    quantity: number
    price_limit?: number
  }) => api.post<Order>('/trading/orders', orderData),
  
  getOrders: (status?: string, limit = 50) =>
    api.get<Order[]>('/trading/orders', {
      params: { status, limit }
    }),
  
  getOrder: (orderId: number) =>
    api.get<Order>(`/trading/orders/${orderId}`),
  
  cancelOrder: (orderId: number) =>
    api.delete(`/trading/orders/${orderId}`),
  
  getOrderBook: (topicId: number) =>
    api.get(`/trading/order-book/${topicId}`),
  
  getRecentTrades: (topicId: number, limit = 20) =>
    api.get(`/trading/recent-trades/${topicId}`, {
      params: { limit }
    }),
}

// Portfolio API
export const portfolioApi = {
  getPortfolio: () => api.get<Portfolio>('/portfolio/portfolio'),
  getPositions: () => api.get<Position[]>('/portfolio/positions'),
  getTrades: (limit = 50, topicId?: number) =>
    api.get<Trade[]>('/portfolio/trades', {
      params: { limit, topic_id: topicId }
    }),
  getPerformance: (timeframe = 'daily') =>
    api.get('/portfolio/performance', {
      params: { timeframe }
    }),
}

// Users API
export const usersApi = {
  register: (userData: {
    username: string
    email: string
    password: string
  }) => api.post<User>('/users/register', userData),
  
  getCurrentUser: () => api.get<User>('/users/me'),
  getUser: (userId: number) => api.get<User>(`/users/users/${userId}`),
}

export default api
