#!/bin/bash

# Scout App Setup Script
# This script sets up the development environment

echo "🔧 Scout App Setup"
echo "=================="

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ Error: Please run this script from the scout-app root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        echo "   Please ensure Python 3 is installed"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created from example"
else
    echo "✅ .env file already exists"
fi

# Check for Google credentials
if [ ! -f "backend/credentials.json" ]; then
    echo ""
    echo "⚠️  Google OAuth Setup Required:"
    echo "   1. Go to Google Cloud Console"
    echo "   2. Create/select a project"
    echo "   3. Enable Google Drive API"
    echo "   4. Create OAuth 2.0 credentials"
    echo "   5. Download credentials.json to backend/ directory"
    echo ""
else
    echo "✅ Google credentials found"
fi

# Run OAuth setup helper
echo ""
echo "🔧 Running OAuth setup helper..."
python3 setup_oauth.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   For development (iOS Simulator):"
echo "     ./start_dev.sh"
echo ""
echo "   For mobile testing (physical device):"
echo "     ./start_mobile.sh"
echo ""
echo "📚 Documentation:"
echo "   • README.md - Project overview"
echo "   • OAUTH_SETUP.md - OAuth configuration guide"
echo ""