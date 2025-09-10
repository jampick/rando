@echo off
REM News Trading Game MVP - Windows Startup Script

echo 🚀 Starting News Trading Game MVP...

REM Check if we're in the right directory
if not exist "README.md" (
    echo ❌ Please run this script from the news_trading_game directory
    pause
    exit /b 1
)

REM Setup backend
echo 🔧 Setting up backend...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Initialize database
echo 🗄️ Initializing database...
python init_db.py

echo ✅ Backend setup complete

REM Setup frontend
echo 🔧 Setting up frontend...
cd ..\frontend

REM Install dependencies
echo 📥 Installing Node.js dependencies...
npm install

echo ✅ Frontend setup complete

REM Start services
echo 🚀 Starting services...

REM Start backend in background
echo 🔧 Starting backend server...
cd ..\backend
call venv\Scripts\activate.bat
start /b python main.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo 🎨 Starting frontend server...
cd ..\frontend
start /b npm run dev

echo.
echo 🎉 News Trading Game MVP is running!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📊 API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all services
pause

echo 🛑 Stopping services...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo ✅ All services stopped
