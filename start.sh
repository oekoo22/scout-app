#!/bin/bash

# Scout App - Unified Backend Startup Script
# This script intelligently starts the backend with proper configuration
# for both iOS Simulator and physical device testing

set -e  # Exit on any error

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

# Check if setup has been run
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Running setup first..."
    if [ -f "setup.sh" ]; then
        chmod +x setup.sh
        ./setup.sh
    else
        print_error "setup.sh not found. Please run the setup manually."
        exit 1
    fi
fi

# Function to get local IP address
get_local_ip() {
    local ip=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    print(ip)
except:
    import subprocess
    result = subprocess.run(['ifconfig', '|', 'grep', 'inet ', '|', 'grep', '-v', '127.0.0.1'], 
                          shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.split()[1])
    else:
        print('unknown')
" 2>/dev/null)
    echo "$ip"
}

# Function to update iOS app configuration
update_ios_config() {
    local target_url="$1"
    local ios_api_service="frontend/ScoutApp/Network/APIService.swift"
    
    if [ ! -f "$ios_api_service" ]; then
        print_warning "iOS APIService.swift not found - skipping iOS app configuration"
        return 1
    fi

    # Create backup
    cp "$ios_api_service" "${ios_api_service}.backup" 2>/dev/null || true

    # Update the baseURL
    if grep -q "private let baseURL = " "$ios_api_service"; then
        if sed -i '' "s|private let baseURL = \"http://.*:8000\"|private let baseURL = \"$target_url\"|g" "$ios_api_service" 2>/dev/null; then
            print_status "iOS app configured for: $target_url"
            return 0
        else
            print_warning "Could not automatically update iOS configuration"
            print_info "Please manually update baseURL in APIService.swift to: $target_url"
            return 1
        fi
    else
        print_warning "Could not find baseURL in APIService.swift"
        return 1
    fi
}

# Function to detect target environment
detect_environment() {
    echo
    print_info "Detecting target environment..."
    
    # Check if there are any iOS devices connected (for Xcode development)
    if command -v xcrun &> /dev/null; then
        local devices=$(xcrun simctl list devices | grep "Booted" | wc -l)
        if [ "$devices" -gt 0 ]; then
            print_info "iOS Simulator detected as likely target"
            echo "simulator"
            return
        fi
        
        # Check for connected physical devices
        local physical_devices=$(xcrun devicectl list devices 2>/dev/null | grep -c "Connected" || echo "0")
        if [ "$physical_devices" -gt 0 ]; then
            print_info "Physical iOS device detected"
            echo "device"
            return
        fi
    fi
    
    # Ask user to choose
    echo
    print_info "Please select your target environment:"
    echo "  1) iOS Simulator (localhost)"
    echo "  2) Physical iOS Device (network IP)"
    echo "  3) Auto-detect based on network"
    echo
    read -p "Choice (1-3): " -n 1 -r
    echo
    
    case $REPLY in
        1) echo "simulator" ;;
        2) echo "device" ;;
        3) 
            # Auto-detect: if we can get a local IP, assume device testing
            local ip=$(get_local_ip)
            if [ "$ip" != "unknown" ] && [ "$ip" != "127.0.0.1" ]; then
                echo "device"
            else
                echo "simulator"
            fi
            ;;
        *) echo "simulator" ;;  # Default to simulator
    esac
}

# Get the target environment
TARGET_ENV=$(detect_environment)

# Configure based on environment
if [ "$TARGET_ENV" = "simulator" ]; then
    print_info "Configuring for iOS Simulator..."
    BACKEND_HOST="localhost"
    BACKEND_URL="http://localhost:8000"
    UVICORN_HOST="127.0.0.1"
    export SCOUT_USE_LOCAL_IP=false
    
    # Update iOS app for localhost
    update_ios_config "$BACKEND_URL"
    
    print_status "Configuration: iOS Simulator"
    echo "  📱 Target: iOS Simulator"
    echo "  🌐 Backend URL: $BACKEND_URL"
    echo "  🔧 Host binding: $UVICORN_HOST"

else
    print_info "Configuring for physical iOS device..."
    LOCAL_IP=$(get_local_ip)
    
    if [ "$LOCAL_IP" = "unknown" ]; then
        print_error "Could not detect local IP address"
        print_info "Please ensure you're connected to a network and try again"
        exit 1
    fi
    
    BACKEND_HOST="0.0.0.0"
    BACKEND_URL="http://$LOCAL_IP:8000"
    UVICORN_HOST="0.0.0.0"
    export SCOUT_USE_LOCAL_IP=true
    
    # Update iOS app for network IP
    update_ios_config "$BACKEND_URL"
    
    print_status "Configuration: Physical iOS Device"
    echo "  📱 Target: Physical iOS Device"
    echo "  🌐 Backend URL: $BACKEND_URL"
    echo "  🔧 Host binding: $UVICORN_HOST (all interfaces)"
    echo "  🏠 Local IP: $LOCAL_IP"
    
    echo
    print_info "Device Setup Instructions:"
    echo "  1. 📶 Ensure your iOS device is on the same WiFi network"
    echo "  2. 🔧 iOS app has been automatically configured"
    echo "  3. 🧪 Test connection: try $BACKEND_URL/health in mobile Safari"
    
    if [ -f "backend/credentials.json" ]; then
        echo
        print_info "Google OAuth Setup (if needed):"
        echo "  Add this redirect URI to Google Cloud Console:"
        echo "  $BACKEND_URL/auth/google/callback"
    fi
fi

# Set environment variables
export SCOUT_ENV=development
export SCOUT_DEBUG=true
export SCOUT_HOST=$BACKEND_HOST
export SCOUT_PORT=8000

# Check if port 8000 is in use
echo
print_info "Checking port availability..."
if lsof -i :8000 > /dev/null 2>&1; then
    print_warning "Port 8000 is already in use"
    echo
    lsof -i :8000
    echo
    read -p "Kill existing process and continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Killing existing process..."
        lsof -ti:8000 | xargs kill -9 2>/dev/null || true
        sleep 2
        print_status "Port 8000 is now available"
    else
        print_info "Exiting. You can manually stop the process first."
        exit 1
    fi
else
    print_status "Port 8000 is available"
fi

# Activate virtual environment
echo
print_info "Activating virtual environment..."
source venv/bin/activate

# Validate backend
print_info "Validating backend application..."
cd backend
if ! python3 -c "import app" 2>/dev/null; then
    print_error "Backend validation failed"
    print_info "Installing missing dependencies..."
    cd ..
    pip install -r requirements.txt 2>/dev/null || true
    cd backend
    
    if ! python3 -c "import app" 2>/dev/null; then
        print_error "Backend still cannot be imported. Check dependencies."
        exit 1
    fi
fi

print_status "Backend application validated"

# Display startup information
echo
echo "🎯 Server Configuration Summary:"
echo "================================"
echo "  🎯 Target: $TARGET_ENV"
echo "  🌐 Access URL: $BACKEND_URL"
echo "  🔧 Binding: $UVICORN_HOST:8000"
echo "  📁 Working Dir: $(pwd)"
echo "  🐍 Virtual Env: Active"
echo

print_info "Available Endpoints:"
echo "  📄 GET  /                    - Health check"
echo "  📋 GET  /health              - Detailed status"
echo "  📊 GET  /config              - Configuration info"
echo "  📁 POST /process-local-pdf   - Local PDF processing (recommended)"
if [ -f "credentials.json" ]; then
    echo "  ☁️  POST /upload-pdf          - Google Drive integration"
    echo "  🔐 GET  /auth/google          - Google OAuth"
fi

echo
print_info "Testing Instructions:"
echo "  1. 🏗️  Open frontend/ScoutApp.xcodeproj in Xcode"
if [ "$TARGET_ENV" = "simulator" ]; then
    echo "  2. 📱 Select iOS Simulator as target"
else
    echo "  2. 📱 Select your physical iOS device as target"
fi
echo "  3. ▶️  Build and run (⌘+R)"
echo "  4. 🧪 Test with 'API Test' tab > 'Test Local PDF Processing'"

# Create necessary directories
mkdir -p local_storage/processed_pdfs 2>/dev/null || true

# Start the server
echo
print_status "Starting FastAPI server..."
echo "Press Ctrl+C to stop"
echo "=========================="
echo

# Start uvicorn with the determined configuration
uvicorn app:app \
    --host "$UVICORN_HOST" \
    --port 8000 \
    --reload \
    --log-level info

# This executes when server stops
echo
print_info "Backend server stopped"
deactivate 2>/dev/null || true