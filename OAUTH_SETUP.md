# Google OAuth Setup Guide

This guide explains how to configure Google OAuth for both development and mobile testing.

## Updated Setup (Fixed State Preservation Issues)

Your OAuth redirect URI is now dynamically configured based on the `SCOUT_USE_LOCAL_IP` environment variable:
- **Development** (`SCOUT_USE_LOCAL_IP=false`): `http://localhost:8000/auth/google/callback`
- **Mobile Testing** (`SCOUT_USE_LOCAL_IP=true`): `http://YOUR_LOCAL_IP:8000/auth/google/callback`

## Key Improvements

✅ **Real Token Handling**: Frontend now receives actual OAuth access/refresh tokens
✅ **State Preservation**: Tokens are properly stored and synchronized between frontend/backend  
✅ **Dynamic Redirect URIs**: Automatic switching between localhost and local IP for mobile testing
✅ **Token Validation**: Backend validates tokens and handles refresh automatically
✅ **OAuth State Validation**: Enhanced security with proper state parameter validation

## Google Cloud Console Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** > **Credentials**
4. Find your OAuth 2.0 Client ID
5. Click **Edit**

### Add Redirect URIs

In the **Authorized redirect URIs** section, add both:

```
http://localhost:8000/auth/google/callback
http://192.168.178.187:8000/auth/google/callback
```

**Note**: Replace `192.168.178.187` with your actual local network IP address.

## Finding Your Local IP Address

### On macOS/Linux:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

### On Windows:
```cmd
ipconfig | findstr "IPv4"
```

### From the Backend:
When you start the backend server, it will print your local IP:
```
📱 For mobile testing:
   Update iOS app to use: 192.168.178.187:8000
   Add to Google OAuth: http://192.168.178.187:8000/auth/google/callback
```

## Testing the Setup

### 1. Development Testing (Simulator)
- Use default settings
- Backend URL: `http://localhost:8000`
- OAuth should work in iOS Simulator

### 2. Mobile Device Testing
- Start backend with: `SCOUT_USE_LOCAL_IP=true python app.py` or use `./start_mobile.sh`
- In iOS app Settings, set custom backend URL to: `http://YOUR_LOCAL_IP:8000`
- Backend will automatically use your local IP for OAuth redirect URI
- Make sure Google OAuth console has both localhost and your local IP redirect URIs

## Environment Variables

Create a `.env` file in the backend directory:

```env
# For mobile testing
SCOUT_USE_LOCAL_IP=true
SCOUT_DEBUG=true
```

## New API Endpoints

The backend now includes additional endpoints for better token management:

### `/auth/validate` (POST)
Validates an access token and returns user information:
```json
{
    "access_token": "your_access_token"
}
```

### `/auth/refresh` (POST)  
Refreshes an access token using a refresh token:
```json
{
    "refresh_token": "your_refresh_token"
}
```

## How the Fixed Flow Works

1. **Frontend** initiates OAuth via `/auth/google`
2. **Backend** generates authorization URL with dynamic redirect URI based on environment
3. **User** completes OAuth flow in browser/webview
4. **Google** redirects to backend callback with authorization code
5. **Backend** exchanges code for tokens and returns real tokens to frontend via custom URL scheme
6. **Frontend** stores real access/refresh tokens and expiry information
7. **Frontend** can now validate tokens with backend and refresh them as needed

## Troubleshooting

### Common Issues:

1. **"redirect_uri_mismatch" error**
   - Make sure the redirect URI in Google Console matches exactly
   - Check that you're using the correct IP address
   - Verify the backend is running on the expected port

2. **Mobile device can't reach backend**
   - Make sure both devices are on the same network
   - Check firewall settings
   - Try accessing `http://YOUR_IP:8000/health` from mobile browser

3. **iOS Simulator vs Device**
   - Simulator: Use `localhost:8000`
   - Device: Use your local IP address (e.g., `192.168.178.187:8000`)

### Debug Steps:

1. Check backend health: `/health` endpoint
2. Check configuration: `/config` endpoint
3. Verify IP address matches between backend and iOS app
4. Check Google Console redirect URIs

## Quick Setup Commands

```bash
# Find your IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Start backend for mobile testing
cd backend
SCOUT_USE_LOCAL_IP=true python app.py

# The backend will show you the URLs to add to Google Console
```