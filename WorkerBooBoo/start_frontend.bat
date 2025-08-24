@echo off
echo Starting WorkerBooBoo Frontend...
echo.

cd frontend

echo Installing Node.js dependencies...
npm install

echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:5173
echo.

npm run dev

pause
