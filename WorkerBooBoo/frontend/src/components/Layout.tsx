import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  MapIcon, 
  ChartBarIcon, 
  HomeIcon, 
  InformationCircleIcon,
  Bars3Icon,
  XMarkIcon
} from '@heroicons/react/24/outline'
import ThemeToggle from './ThemeToggle'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Map View', href: '/map', icon: MapIcon },
    { name: 'Statistics', href: '/statistics', icon: ChartBarIcon },
    { name: 'About', href: '/about', icon: InformationCircleIcon },
  ]

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar - Full screen overlay */}
      <div className={`fixed inset-0 z-90 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        {/* Backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm" 
          onClick={() => setSidebarOpen(false)} 
        />
        
        {/* Sidebar */}
        <div className="fixed inset-y-0 left-0 flex w-80 max-w-[85vw] flex-col bg-white dark:bg-gray-800 shadow-2xl">
          <div className="flex h-16 items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="h-10 w-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-lg">WB</span>
              </div>
              <span className="ml-3 text-xl font-bold text-gray-900 dark:text-white">WorkerBooBoo</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              <XMarkIcon className="h-7 w-7" />
            </button>
          </div>
          
          <nav className="flex-1 space-y-2 px-4 py-6">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`group flex items-center px-4 py-4 text-base font-medium rounded-xl transition-all duration-200 ${
                  isActive(item.href)
                    ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-900 dark:text-primary-100 shadow-sm'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <item.icon
                  className={`mr-4 h-6 w-6 ${
                    isActive(item.href) ? 'text-primary-500' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'
                  }`}
                />
                {item.name}
              </Link>
            ))}
          </nav>
          
          {/* Mobile footer */}
          <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-4">
            <div className="text-sm text-gray-500 dark:text-gray-400 text-center">
              Workplace Safety Data
            </div>
          </div>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          <div className="flex items-center h-16 px-4">
            <div className="h-8 w-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">WB</span>
            </div>
            <span className="ml-2 text-lg font-semibold text-gray-900 dark:text-white">WorkerBooBoo</span>
          </div>
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`group flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                  isActive(item.href)
                    ? 'bg-primary-100 dark:bg-primary-900/20 text-primary-900 dark:text-primary-100'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <item.icon
                  className={`mr-3 h-5 w-5 ${
                    isActive(item.href) ? 'text-primary-500' : 'text-gray-400 dark:text-gray-500 group-hover:text-gray-500 dark:group-hover:text-gray-400'
                  }`}
                />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar - Mobile optimized */}
        <div className="sticky top-0 z-80 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          {/* Mobile menu button - Larger touch target */}
          <button
            type="button"
            className="lg:hidden p-2 -m-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-7 w-7" />
          </button>
          
          <div className="flex flex-1 gap-x-4 self-stretch lg:gap-x-6">
            <div className="flex flex-1"></div>
            <div className="flex items-center gap-x-4 lg:gap-x-6">
              {/* Theme Toggle */}
              <ThemeToggle />
              
              {/* Mobile title */}
              <div className="lg:hidden text-lg font-semibold text-gray-900 dark:text-white">
                {navigation.find(item => isActive(item.href))?.name || 'WorkerBooBoo'}
              </div>
            </div>
          </div>
        </div>

        {/* Page content - Mobile optimized padding */}
        <main className="py-4 sm:py-6">
          <div className="mx-auto max-w-7xl px-3 sm:px-4 lg:px-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout
