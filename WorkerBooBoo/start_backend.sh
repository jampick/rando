#!/bin/bash

echo "Starting WorkerBooBoo Backend Server..."
echo

cd backend

echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo
echo "Starting FastAPI server..."
echo "Server will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo

python3 main.py
