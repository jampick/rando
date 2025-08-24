#!/bin/bash

echo "Starting WorkerBooBoo Frontend..."
echo

cd frontend

# Check if virtual environment exists and activate it (for any Python tools)
if [ -d "../backend/venv" ]; then
    echo "Activating virtual environment..."
    source ../backend/venv/bin/activate
fi

echo "Installing Node.js dependencies..."
npm install

echo
echo "Starting development server..."
echo "Frontend will be available at: http://localhost:5173"
echo

npm run dev
