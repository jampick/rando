import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { TrendingUp, BarChart3, Wallet, Trophy, Activity } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()

  const navItems = [
    { path: '/markets', label: 'Markets', icon: TrendingUp },
    { path: '/trading', label: 'Trading', icon: BarChart3 },
    { path: '/portfolio', label: 'Portfolio', icon: Wallet },
    { path: '/leaderboard', label: 'Leaderboard', icon: Trophy },
  ]

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">📰</span>
                </div>
                <h1 className="text-xl font-bold text-white">
                  News Trading
                </h1>
              </div>
              <div className="hidden md:flex items-center space-x-4 text-sm text-gray-400">
                <span>Live Market</span>
                <div className="flex items-center space-x-2">
                  <div className="status-indicator status-online"></div>
                  <span>Online</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
              {/* Market Status */}
              <div className="hidden lg:flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-green-400" />
                  <span className="text-gray-300">Next Auction:</span>
                  <span className="text-white font-mono">15:23</span>
                </div>
              </div>
              
              {/* User Info */}
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <div className="text-sm text-gray-400">Portfolio Value</div>
                  <div className="text-lg font-bold text-white font-mono">$10,000.00</div>
                </div>
                <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
                  <span className="text-gray-300 text-sm font-semibold">U</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-gray-900 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-item ${isActive ? 'nav-item-active' : 'nav-item-inactive'}`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

export default Layout
