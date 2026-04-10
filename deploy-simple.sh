#!/bin/bash

echo "========================================"
echo "Brain Tumor Segmentation - Simple Deployment"
echo "========================================"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3 from: https://www.python.org/"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js from: https://nodejs.org/"
    exit 1
fi

echo "Creating virtual environment..."
python3 -m venv brain_tumor_env

echo "Activating virtual environment..."
source brain_tumor_env/bin/activate

echo "Installing backend dependencies..."
cd objective3_interface/backend
pip install fastapi uvicorn tensorflow opencv-python numpy pillow python-multipart

echo "Starting backend server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "Installing frontend dependencies..."
cd ../frontend
npm install

echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo
echo "Access your application:"
echo "- Frontend: http://localhost:5173"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo
echo "Both servers are running in background."
echo "Press Ctrl+C to stop all servers."
echo

# Wait for user interrupt
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait

echo "Servers stopped."
