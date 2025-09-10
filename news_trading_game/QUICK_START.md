# 📰 News Trading Game MVP - Quick Start Guide

## 🎮 What is this?

A digital market simulator where **assets = news topics** and **prices = relative news attention**. Players trade topics like stocks (buy, sell, short) with the goal of growing their portfolio.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

### Option 2: Manual Setup

**1. Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python init_db.py
python main.py
```

**2. Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 How to Play

### 1. **Markets View**
- See all available news topics with real-time prices
- Monitor price changes, volume, and attention metrics
- Track fatigue levels (topics that dominate too long crash)

### 2. **Trading**
- Place buy, sell, or short orders
- Use market orders (immediate execution) or limit orders (specific price)
- Orders execute in batch auctions every 15 minutes

### 3. **Portfolio**
- Track your positions and unrealized P&L
- View trade history and performance metrics
- Monitor cash balance and total portfolio value

### 4. **Leaderboard**
- Compete with other players
- Rankings by total portfolio value and returns
- Daily, weekly, and all-time leaderboards

## 🎲 Game Mechanics

### **Zero-Sum Pricing**
- If one topic spikes in attention, others in the same category drop
- Prices reflect relative attention within categories

### **Batch Auctions**
- All trades execute every 15 minutes (±2 minutes randomization)
- Uniform clearing price for all orders in each auction
- Prevents last-second sniping and ensures fair execution

### **Fatigue System**
- Topics that dominate too long (high fatigue) experience sharp corrections
- Prevents any single topic from staying expensive forever

### **Short Selling**
- Borrow shares to sell at current price, hoping to buy back cheaper
- Limited to 20% of total shares per topic
- Short squeezes possible when prices spike

## 🏗️ Technical Architecture

### **Backend (FastAPI + PostgreSQL)**
- Server-authoritative market engine
- Batch auction system with zero-sum pricing
- Real-time WebSocket updates
- Hybrid share supply model

### **Frontend (React + TypeScript)**
- Real-time market data via WebSockets
- Modern UI with Tailwind CSS
- Responsive design for mobile/desktop

## 📊 Sample Data

The MVP includes:
- **2 Categories**: Politics, Technology
- **10 Topics**: AI Regulation, Climate Policy, Cryptocurrency, etc.
- **Simulated News**: Attention metrics and price movements
- **Starting Cash**: $10,000 per player

## 🔧 Development

### **Adding New Topics**
1. Edit `backend/app/services/news_simulator.py`
2. Add topic to `SAMPLE_TOPICS` list
3. Restart backend to initialize

### **Modifying Game Rules**
- Auction intervals: `backend/app/core/config.py`
- Pricing mechanics: `backend/app/services/market_engine.py`
- UI components: `frontend/src/components/`

## 🐛 Troubleshooting

### **Backend won't start**
- Check if PostgreSQL is running
- Verify Python dependencies are installed
- Check database connection in `backend/app/core/config.py`

### **Frontend won't connect**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify WebSocket connection

### **Database issues**
- Run `python backend/init_db.py` to reset
- Check PostgreSQL logs
- Verify database URL in config

## 🚀 Next Steps

This MVP demonstrates the core concept. Future enhancements could include:

- **Real News Integration**: Connect to NewsAPI or Google Trends
- **More Categories**: Sports, Entertainment, Science
- **Advanced Features**: Options trading, futures, social features
- **Mobile App**: React Native or native apps
- **Analytics**: Advanced charts and market analysis tools

## 📝 License

This is a prototype/demo project. Feel free to use and modify for learning purposes.

---

**Happy Trading! 📈📰**
