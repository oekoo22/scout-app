#!/bin/bash

# Scout App Mobile Testing Startup Script
# This script starts the backend in mobile testing mode (local network IP)

echo "📱 Starting Scout App Backend - Mobile Testing Mode"
echo "==================================================="

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

# Get local IP address
LOCAL_IP=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    print(ip)
except:
    print('unknown')
")

if [ "$LOCAL_IP" = "unknown" ]; then
    echo "❌ Error: Could not determine local IP address"
    echo "   Please ensure you're connected to a network"
    exit 1
fi

# Set mobile testing environment variables
export SCOUT_ENV=development
export SCOUT_USE_LOCAL_IP=true
export SCOUT_DEBUG=true
export SCOUT_HOST=0.0.0.0
export SCOUT_PORT=8000

echo ""
echo "🔧 Configuration:"
echo "  Environment: $SCOUT_ENV"
echo "  Local IP: $LOCAL_IP"
echo "  Host: $SCOUT_HOST"
echo "  Port: $SCOUT_PORT"
echo "  Use Local IP: $SCOUT_USE_LOCAL_IP"
echo "  Debug: $SCOUT_DEBUG"
echo ""
echo "📱 For mobile device testing:"
echo "  Backend URL: http://$LOCAL_IP:8000"
echo ""
echo "🔗 Google OAuth Setup:"
echo "  Add this redirect URI to Google Console:"
echo "  http://$LOCAL_IP:8000/auth/google/callback"
echo ""
echo "📱 iOS App Setup:"
echo "  1. Open Scout App on your device"
echo "  2. Go to Settings"
echo "  3. Set custom backend URL to: http://$LOCAL_IP:8000"
echo "  4. Test backend health check"
echo ""
echo "🌐 Access points:"
echo "  • Health Check: http://$LOCAL_IP:8000/health"
echo "  • Configuration: http://$LOCAL_IP:8000/config"
echo "  • Network Info: http://$LOCAL_IP:8000/network"
echo ""

# Start the backend
echo "🚀 Starting backend server for mobile testing..."
cd backend
python app.py