import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request

# Define the scopes for Google Drive API access
# https://developers.google.com/drive/api/guides/scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# Path to your client secrets file downloaded from Google Cloud Console
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')

# Path to store the user's access and refresh tokens
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')

# Always use localhost for OAuth redirect - this works with ASWebAuthenticationSession
# regardless of where the backend server is running
REDIRECT_URI = 'http://localhost:8000/auth/google/callback'

def get_drive_service():
    """Gets an authorized Google Drive API service instance."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as token:
                creds_data = json.load(token)
                creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        except json.JSONDecodeError:
            creds = None # Invalid token file

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save the refreshed credentials
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                # Refresh failed, need to re-authenticate
                print(f"Failed to refresh token: {e}")
                return None # Indicate that auth is needed
        else:
            # No token or no refresh token, need to initiate full auth flow
            return None # Indicate that auth is needed
    
    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred building the drive service: {error}')
        return None
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        return None

def get_authorization_url():
    """Generates the Google OAuth2 authorization URL."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'  # Force prompt for consent to get a refresh token every time
    )
    # Store the state in session or a temporary store to verify in callback
    # For simplicity, we're not doing that here, but it's recommended for security.
    # For example, you could store `state` in the FastAPI session.
    return authorization_url

def exchange_code_for_token(authorization_code: str):
    """Exchanges an authorization code for credentials and saves them.
    Returns the credentials object on success, None on failure.
    """
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    try:
        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials
        with open(TOKEN_FILE, 'w') as token_file:
            token_file.write(credentials.to_json()) # Save to token.json for future server use
        return credentials # Return the full credentials object
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None
