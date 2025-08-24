@echo off
echo Starting WorkerBooBoo - Complete Application
echo.

echo Starting Backend Server...
start "WorkerBooBoo Backend" cmd /k "cd backend && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat && python main.py) else (python -m venv venv && call venv\Scripts\activate.bat && pip install -r requirements.txt && python main.py)"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting Frontend...
start "WorkerBooBoo Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Press any key to open the application...
pause >nul

start http://localhost:5173

echo Application opened in your default browser!
pause
