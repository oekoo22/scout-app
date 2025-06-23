#!/bin/bash

# Scout App - Backend Server Startup Script
# This script starts the FastAPI backend server with proper network configuration

echo "🚀 Starting Scout App Backend Server..."
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    print_error "Please run this script from the scout-app root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run ./setup.sh first"
    exit 1
fi

# Get local IP address for display
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -n 1 | awk '{print $2}')

# Display startup information
echo
print_info "Server Configuration:"
echo "  📁 Backend directory: $(pwd)/backend"
echo "  🐍 Virtual environment: $(pwd)/venv"
if [ ! -z "$LOCAL_IP" ]; then
    echo "  🌐 Local network access: http://$LOCAL_IP:8000"
fi
echo "  🖥️  Localhost access: http://localhost:8000"
echo "  📱 iOS device access: http://$LOCAL_IP:8000"

# Check if port 8000 is already in use
if lsof -i :8000 > /dev/null 2>&1; then
    echo
    print_warning "Port 8000 is already in use"
    print_info "Checking what's running on port 8000:"
    lsof -i :8000
    echo
    read -p "Do you want to kill the existing process and continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Stopping existing process on port 8000..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    else
        print_info "Exiting. You can manually stop the process or use a different port."
        exit 1
    fi
fi

# Activate virtual environment
echo
print_info "Activating virtual environment..."
source venv/bin/activate

# Change to backend directory
cd backend

# Check if app.py exists and can be imported
echo
print_info "Validating backend application..."
if ! python3 -c "import app" 2>/dev/null; then
    print_error "Backend application validation failed"
    print_info "Please check that all dependencies are installed"
    exit 1
fi

print_status "Backend application validated"

# Display available endpoints
echo
print_info "Available API Endpoints:"
echo "  📄 GET  /                    - Health check"
echo "  📋 GET  /health              - Detailed health status"
echo "  📊 GET  /config              - Configuration info"
echo "  🌐 GET  /network             - Network information"
echo "  📁 POST /process-local-pdf   - Process PDF locally (recommended)"
echo "  ☁️  POST /upload-pdf          - Process PDF with Google Drive"
echo "  🔐 GET  /auth/google          - Google OAuth (if configured)"

# Display environment information
if [ -f "../.env" ]; then
    print_status "Environment configuration loaded"
else
    print_warning "No .env file found - using default settings"
fi

# Start the server
echo
print_status "Starting FastAPI server..."
echo
print_info "Server starting with:"
echo "  - Host: 0.0.0.0 (accessible from network)"
echo "  - Port: 8000"
echo "  - Auto-reload: enabled"
echo "  - Log level: info"
echo
print_info "Press Ctrl+C to stop the server"
echo "================================="
echo

# Start uvicorn with proper configuration
uvicorn app:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level info \
    --access-log

# This will only execute if the server stops
echo
print_info "Backend server stopped"