@echo off
echo Starting WorkerBooBoo with Network Access...
echo This will allow access from other devices on your local network
echo.

REM Get local IP address (Windows)
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set LOCAL_IP=%%a
    set LOCAL_IP=!LOCAL_IP: =!
    goto :found_ip
)
:found_ip

echo Your local IP address: %LOCAL_IP%
echo Access the app from other devices at: http://%LOCAL_IP%:5173
echo.

REM Start backend
echo Starting backend server...
cd backend
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

REM Start backend with network access
start "Backend Server" python main.py
cd ..

echo Backend started!
echo Backend API available at: http://%LOCAL_IP%:8000
echo.

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend...
cd frontend
npm install
echo Frontend starting... Access at: http://%LOCAL_IP%:5173
echo.

REM Start frontend with network access
start "Frontend Server" npm run dev
cd ..

echo.
echo Both services are now running!
echo Access from your computer: http://localhost:5173
echo Access from other devices: http://%LOCAL_IP%:5173
echo Backend API: http://%LOCAL_IP%:8000
echo.
echo Press any key to stop this script (services will continue running)
echo To stop services, close the command windows that opened
pause >nul
