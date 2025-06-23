#!/usr/bin/env python3
"""
Google OAuth Setup Helper
This script helps configure Google OAuth for mobile testing.
"""

import socket
import json
import os
from typing import Optional

def get_local_ip() -> Optional[str]:
    """Get the local network IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return None

def check_credentials_file():
    """Check if credentials.json exists"""
    creds_path = os.path.join('backend', 'credentials.json')
    if not os.path.exists(creds_path):
        print("❌ credentials.json not found in backend directory")
        print("   Please download it from Google Cloud Console")
        return False
    return True

def get_redirect_uris(local_ip: str, port: int = 8000) -> list:
    """Get list of redirect URIs to add to Google Console"""
    return [
        f"http://localhost:{port}/auth/google/callback",
        f"http://127.0.0.1:{port}/auth/google/callback",
        f"http://{local_ip}:{port}/auth/google/callback"
    ]

def main():
    print("🔧 Google OAuth Setup Helper")
    print("=" * 50)
    
    # Check credentials file
    if not check_credentials_file():
        return
    
    # Get local IP
    local_ip = get_local_ip()
    if not local_ip:
        print("❌ Could not determine local IP address")
        return
    
    print(f"🌐 Local IP Address: {local_ip}")
    print()
    
    # Get redirect URIs
    redirect_uris = get_redirect_uris(local_ip)
    
    print("📝 Add these Redirect URIs to Google Cloud Console:")
    print("   (APIs & Services > Credentials > OAuth 2.0 Client ID > Edit)")
    print()
    for uri in redirect_uris:
        print(f"   {uri}")
    print()
    
    # Environment setup
    print("🔧 Environment Setup:")
    print("   For mobile testing, set these environment variables:")
    print(f"   SCOUT_USE_LOCAL_IP=true")
    print(f"   SCOUT_HOST=0.0.0.0")
    print(f"   SCOUT_PORT=8000")
    print()
    
    # iOS app setup
    print("📱 iOS App Setup:")
    print("   In the iOS app Settings, set custom backend URL to:")
    print(f"   http://{local_ip}:8000")
    print()
    
    # Create .env file
    env_path = '.env'
    if not os.path.exists(env_path):
        with open(env_path, 'w') as f:
            f.write("# Scout App Environment Configuration\n")
            f.write("SCOUT_ENV=development\n")
            f.write("SCOUT_USE_LOCAL_IP=false\n")
            f.write("SCOUT_DEBUG=true\n")
            f.write("\n")
            f.write("# Set to true for mobile testing\n")
            f.write("# SCOUT_USE_LOCAL_IP=true\n")
        print(f"✅ Created {env_path} file")
    else:
        print(f"ℹ️  {env_path} already exists")
    
    print()
    print("🚀 Testing Steps:")
    print("   1. Add redirect URIs to Google Console")
    print("   2. Start backend: cd backend && python app.py")
    print("   3. For mobile testing:")
    print("      - Set SCOUT_USE_LOCAL_IP=true in .env")
    print("      - Configure iOS app with your local IP")
    print("      - Test OAuth flow on device")
    print()
    print("✅ Setup helper complete!")

if __name__ == "__main__":
    main()