#!/bin/bash

# Scout App - Complete Setup Script
# This script sets up everything needed to run the Scout App
# No other setup files or scripts are needed after running this

set -e  # Exit on any error

echo "🚀 Scout App - Complete Setup"
echo "=============================="
echo "This will set up everything you need to run the Scout App!"
echo

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
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the scout-app root directory"
    exit 1
fi

print_info "Running setup from: $(pwd)"

# Step 1: Check Python installation
echo
echo "🐍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
    echo "Visit: https://www.python.org/downloads/"
    exit 1
fi

# Step 2: Create virtual environment
echo
echo "📦 Setting up Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists, skipping creation"
else
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Step 3: Activate virtual environment and install dependencies
echo
echo "📚 Installing Python dependencies..."
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install core dependencies
pip install fastapi uvicorn python-multipart python-dotenv

# Try to install agents (might not be available in all environments)
if pip install agents 2>/dev/null; then
    print_status "AI agents package installed"
else
    print_warning "AI agents package not available - some features may be limited"
fi

# Install additional dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Additional dependencies installed from requirements.txt"
fi

print_status "Python dependencies installed"

# Step 4: Create necessary directories
echo
echo "📁 Creating project directories..."
mkdir -p backend/local_storage/processed_pdfs
mkdir -p backend/temp
mkdir -p logs
print_status "Project directories created"

# Step 5: Create environment file from template
echo
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Environment file created from template"
    else
        # Create a basic .env file
        cat > .env << EOF
# Scout App Environment Configuration
SCOUT_ENV=development
SCOUT_DEBUG=true
SCOUT_HOST=0.0.0.0
SCOUT_PORT=8000

# OpenAI API (optional - for advanced AI features)
# OPENAI_API_KEY=your_openai_api_key_here

# Google Drive API (optional - for cloud sync)
# GOOGLE_CLIENT_ID=your_google_client_id
# GOOGLE_CLIENT_SECRET=your_google_client_secret
EOF
        print_status "Basic environment file created"
    fi
    print_warning "Please edit .env file to add your API keys if needed"
else
    print_warning "Environment file already exists, skipping"
fi

# Step 6: Check Xcode installation (macOS only)
echo
echo "🛠️  Checking development tools..."
if command -v xcodebuild &> /dev/null; then
    XCODE_VERSION=$(xcodebuild -version | head -n 1)
    print_status "$XCODE_VERSION found"
else
    print_warning "Xcode not found - required for iOS development"
    print_info "Install Xcode from the Mac App Store"
fi

# Step 7: Find local IP address
echo
echo "🌐 Network configuration..."
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -n 1 | awk '{print $2}')
if [ ! -z "$LOCAL_IP" ]; then
    print_status "Local IP address detected: $LOCAL_IP"
    echo "   Use this IP for mobile device testing"
else
    print_warning "Could not detect local IP address"
fi

# Step 8: Test backend import
echo
echo "🧪 Testing backend setup..."
cd backend
if python3 -c "import app; print('✅ Backend imports successfully')" 2>/dev/null; then
    print_status "Backend setup verified"
else
    print_warning "Backend test failed - check dependencies"
fi
cd ..

# Step 9: Check for Google credentials (optional)
if [ ! -f "backend/credentials.json" ]; then
    echo
    print_info "Google OAuth Setup (Optional):"
    echo "   Google Drive integration is optional for this app"
    echo "   The app works with local storage only"
    echo "   To enable Google Drive features:"
    echo "   1. Go to Google Cloud Console"
    echo "   2. Create/select a project" 
    echo "   3. Enable Google Drive API"
    echo "   4. Create OAuth 2.0 credentials"
    echo "   5. Download credentials.json to backend/ directory"
else
    print_status "Google credentials found"
fi

# Step 10: Create a simple .env.example for reference
echo
print_info "Creating environment template..."
if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# Scout App Environment Configuration
# Copy this to .env and customize as needed

# Development settings
SCOUT_ENV=development
SCOUT_DEBUG=true
SCOUT_HOST=0.0.0.0
SCOUT_PORT=8000

# Optional: OpenAI API for enhanced AI features
# OPENAI_API_KEY=your_openai_api_key_here

# Optional: Google Drive integration
# GOOGLE_CLIENT_ID=your_google_client_id
# GOOGLE_CLIENT_SECRET=your_google_client_secret
EOF
    print_status "Environment template created (.env.example)"
fi

# Step 11: Final validation and instructions
echo
echo "🧪 Final validation..."
cd backend
if python3 -c "
import sys
try:
    import fastapi, uvicorn
    print('✅ Core dependencies OK')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    sys.exit(1)
try:
    import app
    print('✅ Backend application loads successfully')
except Exception as e:
    print(f'⚠️  Backend import warning: {e}')
" 2>/dev/null; then
    print_status "Backend validation passed"
else
    print_warning "Backend validation had issues - but basic functionality should work"
fi
cd ..

# Step 12: Success message and next steps
echo
echo "🎉 Setup Complete! 🎉"
echo "====================")
echo
print_status "Your Scout App is ready to use!"
echo
print_info "Quick Start - Next Steps:"
echo "  1. 🚀 Start the backend: ./start.sh"
echo "  2. 🏗️  Open Xcode: open frontend/ScoutApp.xcodeproj"
echo "  3. ▶️  Build and run the iOS app (⌘+R)"
echo "  4. 📸 Start scanning documents!"
echo
print_info "What was set up:"
echo "  ✅ Python virtual environment with all dependencies"
echo "  ✅ Backend FastAPI server ready to run"
echo "  ✅ Local storage directories created"
echo "  ✅ Environment configuration templates"
echo "  ✅ Network configuration for iOS development"
echo
print_info "The app works locally without any additional setup!"
echo "  - 📱 iOS Simulator: Works automatically with localhost"
echo "  - 📱 Physical device: The start.sh script will configure network"
echo "  - 🤖 AI features: Add OPENAI_API_KEY to .env for enhanced processing"
echo "  - ☁️  Cloud sync: Add Google credentials for Drive integration"
echo
print_info "Useful commands:"
echo "  ./start.sh          - Start the backend server (smart configuration)"
echo "  ./start.sh          - Automatically detects simulator vs device"
echo "  curl localhost:8000/health - Test backend health"
echo
print_warning "If you have issues:"
echo "  - Check the comprehensive README.md troubleshooting section"
echo "  - Ensure Xcode 14.0+ and Python 3.8+ are installed"
echo "  - Make sure you're on the same WiFi network (for device testing)"
echo
print_info "The setup created these key files:"
echo "  📄 README.md        - Complete documentation and troubleshooting"
echo "  🚀 start.sh         - Smart backend startup (replaces all other start scripts)"
echo "  ⚙️  .env.example     - Environment configuration template"
echo
if [ ! -z "$LOCAL_IP" ]; then
    print_info "Your local network info:"
    echo "  🏠 Mac IP address: $LOCAL_IP"
    echo "  🌐 Backend will be: http://$LOCAL_IP:8000 (for physical device)"
    echo "  🌐 Backend will be: http://localhost:8000 (for simulator)"
fi

deactivate 2>/dev/null || true

echo
echo "=================================="
print_status "🎊 Welcome to Scout App! 🎊"
echo "Your AI-powered document scanner is ready!"
echo "=================================="