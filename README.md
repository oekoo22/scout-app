# Scout App

A mobile document processing application with AI-powered organization using Google Drive integration.

## Architecture

- **Backend**: Python FastAPI server with Google Drive API integration
- **Frontend**: SwiftUI iOS app with camera scanning capabilities
- **AI Processing**: OpenAI agents for document analysis and organization

## Quick Start

### 1. Initial Setup
```bash
./setup.sh
```

### 2. Development Mode (iOS Simulator)
```bash
./start_dev.sh
```

### 3. Mobile Testing Mode (Physical Device)
```bash
./start_mobile.sh
```

## Features

### Mobile OAuth Fix ✅
- **Problem**: Mobile devices couldn't access OAuth redirect at `localhost:8000`
- **Solution**: Dynamic configuration supporting both localhost and local network IP
- **Usage**: Scripts automatically detect and configure the correct IP address

### Configuration System
- Environment-based configuration (development/production)
- Dynamic network detection and IP resolution
- Configurable CORS origins
- OAuth redirect URI management

### iOS App Enhancements
- Dynamic backend URL configuration
- Built-in backend health checking
- Settings panel for network configuration
- Improved error handling with specific error messages

### Backend Improvements
- Comprehensive logging with emoji indicators
- Better error handling and debugging
- Network utilities and IP detection
- Health check and configuration endpoints

## Project Structure

```
scout-app/
├── backend/                    # Python FastAPI backend
│   ├── app.py                 # Main application
│   ├── config.py              # Configuration management
│   ├── network_utils.py       # Network utilities
│   ├── google_drive_auth.py   # Google OAuth handling
│   └── scout_agents/          # AI processing agents
├── frontend/                  # iOS SwiftUI app
│   └── ScoutApp/
│       ├── Config.swift       # App configuration
│       ├── AuthService.swift  # Authentication service
│       └── SettingsView.swift # Settings with backend config
├── start_dev.sh              # Development startup script
├── start_mobile.sh           # Mobile testing startup script
├── setup.sh                  # Initial setup script
├── setup_oauth.py            # OAuth configuration helper
└── OAUTH_SETUP.md           # OAuth setup guide
```

## Configuration

### Environment Variables (.env)
```bash
SCOUT_ENV=development
SCOUT_USE_LOCAL_IP=false        # Set to true for mobile testing
SCOUT_DEBUG=true
SCOUT_HOST=0.0.0.0
SCOUT_PORT=8000
```

### iOS App Configuration
- **Development**: Uses `localhost:8000` automatically
- **Mobile Testing**: Configure custom backend URL in Settings
- **Health Check**: Built-in backend connectivity testing

## Google OAuth Setup

### Required Redirect URIs
Add these to your Google Cloud Console OAuth configuration:
- `http://localhost:8000/auth/google/callback` (development)
- `http://YOUR_LOCAL_IP:8000/auth/google/callback` (mobile testing)

### Setup Helper
```bash
python3 setup_oauth.py
```

## Testing Workflows

### Development Testing (Simulator)
1. Run `./start_dev.sh`
2. Backend runs on `localhost:8000`
3. iOS Simulator can access localhost directly
4. OAuth works with localhost redirect URI

### Mobile Device Testing
1. Run `./start_mobile.sh`
2. Backend runs on `0.0.0.0:8000` (all interfaces)
3. Script shows your local IP (e.g., `192.168.1.100`)
4. Configure iOS app to use `http://192.168.1.100:8000`
5. Add network IP redirect URI to Google Console
6. Test OAuth flow on physical device

## API Endpoints

- `GET /` - Hello World
- `GET /health` - Backend health check
- `GET /config` - Configuration information
- `GET /network` - Network information
- `GET /auth/google` - Initiate Google OAuth
- `GET /auth/google/callback` - OAuth callback handler
- `POST /process-file` - Process document with AI agents

## Troubleshooting

### Common Issues

1. **Mobile device can't reach backend**
   - Ensure both devices are on the same network
   - Check firewall settings
   - Verify IP address is correct

2. **OAuth redirect_uri_mismatch**
   - Make sure Google Console has correct redirect URIs
   - Check backend logs for actual redirect URI being used
   - Use `/config` endpoint to verify configuration

3. **iOS app connection issues**
   - Use Settings > Backend Configuration to test health
   - Try accessing backend URL directly in mobile browser
   - Check backend logs for connection attempts

### Debug Commands
```bash
# Check your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Test backend health
curl http://localhost:8000/health

# Test mobile access (replace IP)
curl http://192.168.1.100:8000/health

# View backend configuration
curl http://localhost:8000/config
```

## Development

### Backend Development
```bash
cd backend
source ../venv/bin/activate
python app.py
```

### iOS Development
Open `frontend/ScoutApp.xcodeproj` in Xcode

### Adding New Features
1. Update backend APIs in `app.py`
2. Add iOS networking code in `APIService.swift`
3. Update configuration if needed
4. Test in both development and mobile modes

## License

[Your license here]