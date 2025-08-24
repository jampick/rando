@echo off
echo Starting WorkerBooBoo Backend Server...
echo.

cd backend

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server...
echo Server will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.

python main.py

pause
