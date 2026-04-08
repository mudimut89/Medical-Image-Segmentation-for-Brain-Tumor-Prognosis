#!/bin/bash

# Brain Tumor Segmentation - Startup Script
# Runs both backend (FastAPI) and frontend (React/Vite) concurrently

set -e

echo "=========================================="
echo "  Brain Tumor Segmentation System"
echo "  Starting services..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD=$(command -v python3 || command -v python)

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}Services stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Setup Backend
echo -e "\n${YELLOW}[1/4] Setting up backend...${NC}"
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt --quiet

# Setup Frontend
echo -e "\n${YELLOW}[2/4] Setting up frontend...${NC}"
cd "$FRONTEND_DIR"

# Install frontend dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start Backend
echo -e "\n${YELLOW}[3/4] Starting backend server...${NC}"
cd "$BACKEND_DIR"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo -e "${GREEN}Backend started on http://localhost:8000${NC}"

# Wait for backend to be ready
sleep 3

# Start Frontend
echo -e "\n${YELLOW}[4/4] Starting frontend server...${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend started on http://localhost:5173${NC}"

echo -e "\n=========================================="
echo -e "${GREEN}All services are running!${NC}"
echo -e "=========================================="
echo -e "Backend API:  ${GREEN}http://localhost:8000${NC}"
echo -e "Frontend UI:  ${GREEN}http://localhost:5173${NC}"
echo -e "API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
echo -e "==========================================\n"
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
