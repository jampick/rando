# 📰 News Trading Game MVP

A digital market simulator where assets = news topics and prices = relative news attention.

## 🎮 Core Concept

- **Assets**: News topics (e.g., "AI Regulation", "Climate Change", "SpaceX Launch")
- **Prices**: Relative attention (mentions per topic vs others in same category)
- **Goal**: Grow portfolio by trading topics like stocks (buy, sell, short)

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- Market engine with batch auctions (15m intervals)
- Zero-sum pricing mechanics
- Hybrid share supply model
- Server-authoritative trading system

### Frontend (React + TypeScript)
- Real-time market data via WebSockets
- Trading interface (buy/sell/short)
- Portfolio dashboard
- Leaderboards

## 🚀 MVP Scope

- **Categories**: Politics + Tech
- **Topics**: 5 per category
- **Data**: Simulated news mentions
- **Updates**: 15-minute batch auctions

## 📁 Project Structure

```
news_trading_game/
├── backend/          # FastAPI server
├── frontend/         # React app
├── docs/            # Documentation
└── README.md
```

## 🔧 Development

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Key Features

- **Batch Auctions**: All trades clear at uniform price every 15 minutes
- **Zero-Sum Pricing**: Topic spikes cause others in category to drop
- **Fatigue Crashes**: Dominant topics correct sharply
- **Short Selling**: Up to % of float with squeeze mechanics
- **Real-time Updates**: Live price feeds and portfolio tracking
