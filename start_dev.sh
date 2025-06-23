#!/bin/bash

# Scout App Development Startup Script
# This script starts the backend in development mode (localhost)

echo "🚀 Starting Scout App Backend - Development Mode"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ Error: Please run this script from the scout-app root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set development environment variables
export SCOUT_ENV=development
export SCOUT_USE_LOCAL_IP=false
export SCOUT_DEBUG=true
export SCOUT_HOST=localhost
export SCOUT_PORT=8000

echo ""
echo "🔧 Configuration:"
echo "  Environment: $SCOUT_ENV"
echo "  Host: $SCOUT_HOST"
echo "  Port: $SCOUT_PORT"
echo "  Use Local IP: $SCOUT_USE_LOCAL_IP"
echo "  Debug: $SCOUT_DEBUG"
echo ""
echo "📱 For iOS Simulator testing:"
echo "  Backend URL: http://localhost:8000"
echo ""
echo "🌐 Access points:"
echo "  • Health Check: http://localhost:8000/health"
echo "  • Configuration: http://localhost:8000/config"
echo "  • Network Info: http://localhost:8000/network"
echo ""

# Start the backend
echo "🚀 Starting backend server..."
cd backend
python app.py