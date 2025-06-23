#!/bin/bash

# Scout App - Complete Development Environment Startup Script
# This script sets up and starts the complete development environment

echo "🚀 Starting Scout App - Complete Development Environment"
echo "========================================================"

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

# Step 1: Check and setup virtual environment
echo
echo "📦 Setting up Python environment..."
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Running setup..."
    if [ -f "setup.sh" ]; then
        chmod +x setup.sh
        ./setup.sh
    else
        print_info "Creating virtual environment manually..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install fastapi uvicorn python-multipart python-dotenv
        pip install agents 2>/dev/null || print_warning "AI agents package not available"
    fi
else
    print_status "Virtual environment found"
fi

# Step 2: Activate virtual environment
echo
print_info "Activating virtual environment..."
source venv/bin/activate

# Step 3: Install/update dependencies if needed
if [ -f "requirements.txt" ]; then
    echo
    print_info "Installing/updating dependencies..."
    pip install -r requirements.txt
fi

# Step 4: Set development environment variables
export SCOUT_ENV=development
export SCOUT_USE_LOCAL_IP=false
export SCOUT_DEBUG=true
export SCOUT_HOST=localhost
export SCOUT_PORT=8000

# Step 5: Check iOS app configuration
echo
echo "📱 Checking iOS app configuration..."
IOS_API_SERVICE="frontend/ScoutApp/Network/APIService.swift"

if [ -f "$IOS_API_SERVICE" ]; then
    CURRENT_URL=$(grep "private let baseURL = " "$IOS_API_SERVICE" | sed 's/.*= "\(.*\)"/\1/')
    if [[ "$CURRENT_URL" == *"localhost:8000"* ]]; then
        print_status "iOS app configured for development (localhost)"
    else
        print_warning "iOS app is configured for: $CURRENT_URL"
        print_info "For iOS Simulator, it should be: http://localhost:8000"
        print_info "Run ./configure_network.sh to reconfigure for localhost"
    fi
else
    print_warning "iOS APIService.swift not found"
fi

# Step 6: Check port availability
echo
echo "🌐 Checking network configuration..."
if lsof -i :8000 > /dev/null 2>&1; then
    print_warning "Port 8000 is already in use"
    print_info "Current processes on port 8000:"
    lsof -i :8000
    echo
    read -p "Kill existing process and continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
        print_status "Port 8000 cleared"
    else
        print_info "Exiting. Stop the existing process or use a different port."
        exit 1
    fi
else
    print_status "Port 8000 is available"
fi

# Step 7: Display configuration
echo
echo "🔧 Development Configuration:"
echo "=============================="
echo "  🌍 Environment: $SCOUT_ENV"
echo "  🖥️  Host: $SCOUT_HOST"
echo "  🔌 Port: $SCOUT_PORT"
echo "  📱 iOS Target: iOS Simulator"
echo "  🔍 Debug Mode: $SCOUT_DEBUG"
echo "  🌐 Use Local IP: $SCOUT_USE_LOCAL_IP"
echo

print_info "Development Access Points:"
echo "  📊 Health Check: http://localhost:8000/health"
echo "  ⚙️  Configuration: http://localhost:8000/config"
echo "  🌐 Network Info: http://localhost:8000/network"
echo "  📄 API Docs: http://localhost:8000/docs"
echo

print_info "Available Endpoints:"
echo "  📁 POST /process-local-pdf - Process PDFs locally"
echo "  ☁️  POST /upload-pdf - Process with Google Drive"
echo "  🔐 GET /auth/google - Google OAuth (if configured)"
echo

print_info "Next Steps:"
echo "  1. 🏗️  Open frontend/ScoutApp.xcodeproj in Xcode"
echo "  2. 📱 Select iOS Simulator as target"
echo "  3. ▶️  Build and run the iOS app (⌘+R)"
echo "  4. 📸 Test document scanning functionality"
echo

# Step 8: Create necessary directories
print_info "Creating necessary directories..."
mkdir -p backend/local_storage/processed_pdfs
mkdir -p logs
print_status "Directories created"

# Step 9: Start the backend server
echo
print_status "Starting FastAPI development server..."
echo "======================================="
print_info "Server will start with auto-reload enabled"
print_info "Press Ctrl+C to stop the server"
echo

# Change to backend directory and start server
cd backend
uvicorn app:app \
    --host localhost \
    --port 8000 \
    --reload \
    --log-level info

# This will execute when the server stops
echo
print_info "Development server stopped"