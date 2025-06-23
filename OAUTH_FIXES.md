# Google OAuth Callback Fixes

## Overview
This document outlines the fixes applied to resolve Google OAuth redirect issues in the Scout App backend.

## Issues Identified and Fixed

### 1. Redirect URI Configuration
**Problem**: OAuth was hardcoded to use `localhost:8000` but the server could run on local IP, causing redirect URI mismatches.

**Solution**: 
- Added dynamic redirect URI configuration based on environment variables
- New environment variables:
  - `SCOUT_OAUTH_HOST`: Override the OAuth host (e.g., `localhost` or `192.168.1.100`)
  - `SCOUT_OAUTH_REDIRECT_URI`: Complete override of the redirect URI

### 2. State Management
**Problem**: OAuth states were stored in simple in-memory dictionary without expiration, causing potential security issues and memory leaks.

**Solution**:
- Implemented `OAuthStateManager` class with automatic expiration (10 minutes)
- Added proper cleanup of expired states
- Enhanced state validation with better error messages

### 3. Error Handling and Debugging
**Problem**: OAuth errors were difficult to debug due to limited logging and generic error messages.

**Solution**:
- Added comprehensive logging throughout the OAuth flow
- Enhanced error messages with specific details about redirect URI mismatches
- Added OAuth debug endpoint (`/oauth/debug`) for configuration troubleshooting
- Improved error categorization (redirect_uri_mismatch, invalid_grant, etc.)

### 4. Network Configuration Validation
**Problem**: No validation or warnings when OAuth configuration might not work for mobile devices.

**Solution**:
- Added startup validation that warns about potential configuration issues
- OAuth debug endpoint provides accessibility checks and recommendations
- Clear logging about when mobile devices might not be able to complete OAuth flow

## New Features

### OAuth Debug Endpoint
Access `GET /oauth/debug` to get comprehensive information about:
- Current OAuth configuration
- Google Client configuration (from credentials.json)
- Configuration warnings and recommendations
- Accessibility check for mobile devices
- Active OAuth states count

### Enhanced Configuration
The `config.py` now provides:
- Better network detection and configuration
- OAuth-specific configuration validation
- Detailed logging about configuration choices
- Warnings about potential issues

### Improved Error Messages
OAuth callback now provides detailed error information:
- Specific error types (redirect_uri_mismatch, invalid_grant, etc.)
- URL encoding of error details for safe transport to mobile app
- Comprehensive logging for server-side debugging

## Environment Variables

```bash
# OAuth Host Configuration
SCOUT_OAUTH_HOST=localhost              # Use localhost (default for development)
SCOUT_OAUTH_HOST=192.168.1.100         # Use specific local IP for mobile testing

# Complete OAuth Redirect URI Override
SCOUT_OAUTH_REDIRECT_URI=http://localhost:8000/auth/google/callback

# Network Configuration
SCOUT_USE_LOCAL_IP=false                # Server runs on localhost (default)
SCOUT_USE_LOCAL_IP=true                 # Server runs on local IP for mobile access
```

## Google Cloud Console Setup

For proper OAuth functionality, ensure your Google Cloud Console is configured with:

1. **Authorized Redirect URIs**:
   - `http://localhost:8000/auth/google/callback` (for development)
   - `http://YOUR_LOCAL_IP:8000/auth/google/callback` (for mobile testing)

2. **Authorized JavaScript Origins** (if needed):
   - `http://localhost:8000`
   - `http://YOUR_LOCAL_IP:8000`

## Testing the Fixes

1. **Check Configuration**: Visit `GET /oauth/debug` to verify your setup
2. **Test OAuth Flow**: Use `GET /auth/google` to initiate OAuth
3. **Monitor Logs**: Watch server logs for detailed OAuth flow information
4. **Validate Mobile Access**: Ensure mobile devices can reach the configured redirect URI

## Troubleshooting

### Common Issues

1. **Redirect URI Mismatch**:
   - Check Google Cloud Console configuration
   - Verify `SCOUT_OAUTH_HOST` matches your setup
   - Use `/oauth/debug` endpoint to see current configuration

2. **Mobile Devices Can't Complete OAuth**:
   - Set `SCOUT_OAUTH_HOST` to your local IP address
   - Add the local IP redirect URI to Google Cloud Console
   - Ensure your firewall allows connections on port 8000

3. **Invalid State Parameter**:
   - States expire after 10 minutes for security
   - Check server logs for state validation details
   - Ensure OAuth flow completes within the timeout window

## Files Modified

- `/backend/config.py`: Enhanced OAuth configuration and validation
- `/backend/app.py`: Improved state management, error handling, and debug endpoint
- `/backend/google_drive_auth.py`: Enhanced logging and error categorization
- `/.env.example`: Updated with new OAuth configuration options