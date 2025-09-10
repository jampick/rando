import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import MarketsPage from './pages/MarketsPage'
import TradingPage from './pages/TradingPage'
import PortfolioPage from './pages/PortfolioPage'
import LeaderboardPage from './pages/LeaderboardPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<MarketsPage />} />
        <Route path="/markets" element={<MarketsPage />} />
        <Route path="/trading" element={<TradingPage />} />
        <Route path="/portfolio" element={<PortfolioPage />} />
        <Route path="/leaderboard" element={<LeaderboardPage />} />
      </Routes>
    </Layout>
  )
}

export default App
