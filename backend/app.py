from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from fastapi import HTTPException

# Import the main function from scout_orchestrator
from scout_agents.scout_orchestrator import main as run_scout_orchestration
# Import Google Drive auth functions
from google_drive_auth import get_drive_service, get_authorization_url, exchange_code_for_token

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello_world():
    return {"message": "Hello World!"}

# Google Authentication Endpoints
@app.get("/auth/google")
async def auth_google():
    drive_service = get_drive_service()
    if drive_service:
        return {"message": "Already authenticated with Google Drive."}
    authorization_url = get_authorization_url()
    return RedirectResponse(authorization_url)

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, code: str = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code from Google.")
    
    # The 'code' is the authorization code from Google.
    # We need to pass the full request URL to exchange_code_for_token if it needs it
    # for redirect_uri validation, though our current exchange_code_for_token doesn't explicitly use it.
    # However, the flow object internally might.
    
    success = exchange_code_for_token(authorization_code=code)
    if success:
        # Optionally, redirect to a frontend page indicating success
        return {"message": "Successfully authenticated with Google Drive and token saved."}
    else:
        raise HTTPException(status_code=500, detail="Failed to exchange authorization code for token.")

# Pydantic model for the request to the orchestrator endpoint
class OrchestratorRequest(BaseModel):
    file_name: str

# Pydantic model for the response from the orchestrator endpoint
class OrchestratorResponse(BaseModel):
    original_file: str
    renamed_file: str | None = None
    target_folder: str | None = None
    final_path_suggestion: str | None = None
    status_updates: list[str]
    error_message: str | None = None

# New endpoint to trigger the scout orchestrator
@app.post("/process-file", response_model=OrchestratorResponse)
async def trigger_orchestrator_endpoint(payload: OrchestratorRequest):
    drive_service = get_drive_service()
    if not drive_service:
        # If not authenticated, instruct client to initiate auth flow.
        # The client would then call /auth/google
        raise HTTPException(
            status_code=401,
            detail="Not authenticated with Google Drive. Please authenticate via /auth/google endpoint."
        )

    try:
        # The orchestrator's main function now accepts the filename (as file_id)
        # AND the drive_service object, and optionally original_file_name.
        # Assuming payload.file_name is now the Google Drive File ID.
        # If the client can also send the original display name, that would be helpful.
        # For now, let's assume OrchestratorRequest might be extended to include original_file_name.
        # If not, scout_orchestrator's main will use file_id as a placeholder for name.
        
        # Let's assume payload.file_name is the file_id.
        # We'll need to adjust OrchestratorRequest if we want to pass more than just the ID from client.
        # For now, we pass file_name from payload as both file_id and a hint for original_file_name.
        result_dict = await run_scout_orchestration(
            file_id_to_process=payload.file_name, 
            drive_service=drive_service,
            original_file_name=payload.file_name # Passing it as original name too, assuming it might be name or ID
        )
        return OrchestratorResponse(**result_dict)
    except Exception as e:
        # Log the exception for debugging on the server side
        print(f"Error in /process-file endpoint: {e}")
        # Return a structured error response
        return OrchestratorResponse(
            original_file=payload.file_name,
            status_updates=[f"Endpoint error: {str(e)}"],
            error_message=str(e)
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
