#!/bin/bash

echo "Starting WorkerBooBoo - Complete Application"
echo

# Start backend in background
echo "Starting Backend Server..."
./start_backend.sh &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 5

# Start frontend in background
echo "Starting Frontend..."
./start_frontend.sh &
FRONTEND_PID=$!

echo
echo "Both services are starting..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo
echo "Press Ctrl+C to stop both services"
echo

# Wait for user to stop
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Open browser
sleep 3
open http://localhost:5173

echo "Application opened in your default browser!"
echo "Keep this terminal open to run the services."

# Wait for background processes
wait
