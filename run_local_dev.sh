#!/bin/bash

# Kill any existing uvicorn processes
pkill -f uvicorn

# Set up environment variables
export PYTHONPATH="$PWD:$PYTHONPATH"

# Start backend in the background
cd backend
echo "Starting FastAPI backend..."
python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Start frontend in a new terminal
cd ../frontend
echo "Starting React frontend..."
npm start &
FRONTEND_PID=$!

# Trap SIGINT to kill both processes when Ctrl+C is pressed
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Keep script running
echo "Development servers running. Press Ctrl+C to stop."
wait
