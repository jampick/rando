#!/bin/bash

echo "Starting WorkerBooBoo with Network Access..."
echo "This will allow access from other devices on your local network"
echo

# Get local IP address
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "Your local IP address: $LOCAL_IP"
echo "Access the app from other devices at: http://$LOCAL_IP:5173"
echo

# Start backend in background
echo "Starting backend server..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Start backend with network access
python main.py &
BACKEND_PID=$!
cd ..

echo "Backend started with PID: $BACKEND_PID"
echo "Backend API available at: http://$LOCAL_IP:8000"
echo

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend
npm install
echo "Frontend starting... Access at: http://$LOCAL_IP:5173"
echo

# Start frontend with network access
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Frontend started with PID: $FRONTEND_PID"
echo
echo "Both services are now running!"
echo "Access from your computer: http://localhost:5173"
echo "Access from other devices: http://$LOCAL_IP:5173"
echo "Backend API: http://$LOCAL_IP:8000"
echo
echo "Press Ctrl+C to stop both services"

# Wait for user to stop
wait

# Cleanup on exit
echo "Stopping services..."
kill $BACKEND_PID 2>/dev/null
kill $FRONTEND_PID 2>/dev/null
echo "Services stopped."
