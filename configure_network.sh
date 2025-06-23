#!/bin/bash

# Scout App - Network Configuration Script
# This script automatically configures network settings for iOS device testing

echo "🌐 Configuring Scout App Network Settings..."
echo "============================================"

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

# Step 1: Find local IP address
echo
echo "🔍 Detecting network configuration..."
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -n 1 | awk '{print $2}')

if [ -z "$LOCAL_IP" ]; then
    print_error "Could not detect local IP address"
    echo "   Please check your network connection and try again"
    echo "   You can manually find your IP with: ifconfig | grep 'inet '"
    exit 1
fi

print_status "Local IP address detected: $LOCAL_IP"

# Step 2: Display network information
echo
print_info "Network Information:"
echo "  🖥️  Mac IP Address: $LOCAL_IP"
echo "  🌐 Backend will be accessible at: http://$LOCAL_IP:8000"
echo "  📱 Configure your iOS device to use this address"

# Step 3: Update iOS app configuration
echo
echo "📱 Updating iOS app configuration..."

IOS_API_SERVICE="frontend/ScoutApp/Network/APIService.swift"

if [ ! -f "$IOS_API_SERVICE" ]; then
    print_error "iOS APIService.swift not found at: $IOS_API_SERVICE"
    print_info "Please update the baseURL manually in your iOS app:"
    echo "   private let baseURL = \"http://$LOCAL_IP:8000\""
    exit 1
fi

# Create backup of the original file
BACKUP_FILE="${IOS_API_SERVICE}.backup"
cp "$IOS_API_SERVICE" "$BACKUP_FILE"
print_info "Created backup: $BACKUP_FILE"

# Update the baseURL in APIService.swift
if grep -q "private let baseURL = " "$IOS_API_SERVICE"; then
    # Replace existing baseURL
    if sed -i '' "s|private let baseURL = \"http://.*:8000\"|private let baseURL = \"http://$LOCAL_IP:8000\"|g" "$IOS_API_SERVICE"; then
        print_status "iOS app configured for IP: $LOCAL_IP"
    else
        print_error "Failed to update iOS app configuration"
        # Restore backup
        cp "$BACKUP_FILE" "$IOS_API_SERVICE"
        exit 1
    fi
else
    print_warning "Could not find baseURL in APIService.swift"
    print_info "Please manually update the baseURL to: http://$LOCAL_IP:8000"
fi

# Step 4: Verify the change
echo
echo "🔍 Verifying configuration..."
CURRENT_URL=$(grep "private let baseURL = " "$IOS_API_SERVICE" | sed 's/.*= "\(.*\)"/\1/')
if [ "$CURRENT_URL" = "http://$LOCAL_IP:8000" ]; then
    print_status "Configuration verified: $CURRENT_URL"
else
    print_warning "Configuration may not have updated correctly"
    print_info "Current URL: $CURRENT_URL"
    print_info "Expected URL: http://$LOCAL_IP:8000"
fi

# Step 5: Network connectivity test
echo
echo "🧪 Testing network connectivity..."

# Check if we can bind to the address
if python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('$LOCAL_IP', 0))
    s.close()
    print('✅ Network binding test successful')
except Exception as e:
    print(f'❌ Network binding test failed: {e}')
    exit(1)
" 2>/dev/null; then
    print_status "Network binding test passed"
else
    print_warning "Network binding test failed - check firewall settings"
fi

# Step 6: Final instructions
echo
echo "🎉 Network Configuration Complete!"
echo "=================================="
echo
print_info "Next steps:"
echo "  1. 🚀 Start the backend server: ./start_backend.sh"
echo "  2. 📱 Build and run the iOS app in Xcode"
echo "  3. 📶 Ensure your iOS device is on the same WiFi network"
echo
print_info "Network details:"
echo "  🖥️  Mac IP: $LOCAL_IP"
echo "  🌐 Backend URL: http://$LOCAL_IP:8000"
echo "  📱 iOS app configured to use: $CURRENT_URL"
echo
print_info "Testing checklist:"
echo "  ☐ Start backend server"
echo "  ☐ Build iOS app in Xcode"
echo "  ☐ Connect iOS device to same WiFi"
echo "  ☐ Test document scanning"
echo
print_warning "Troubleshooting:"
echo "  - If connection fails, check macOS firewall settings"
echo "  - Verify both devices are on the same WiFi network"
echo "  - Try accessing http://$LOCAL_IP:8000 in mobile Safari"
echo "  - Check backend logs for connection attempts"
echo
print_info "To restore original configuration:"
echo "  cp \"$BACKUP_FILE\" \"$IOS_API_SERVICE\""

echo
print_status "Network configuration completed successfully! 🌐"