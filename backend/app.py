from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from urllib.parse import urlencode

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
async def auth_google(request: Request):
    drive_service = get_drive_service()
    if drive_service:
        pass
        
    app_callback_scheme = request.query_params.get("callback_scheme", "scoutapp")
    
    authorization_url = get_authorization_url()
    final_auth_url = get_authorization_url() # Called twice, but okay for now
    print(f"---- DEBUG: Attempting to redirect to Google auth URL: {final_auth_url} ----") # DEBUG PRINT
    return RedirectResponse(final_auth_url)

@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, code: str = None, state: str = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code from Google.")
    
    app_callback_scheme = "scoutapp"

    credentials = exchange_code_for_token(authorization_code=code)
    
    if credentials and credentials.token:
        access_token = credentials.token
        redirect_params = {"token": access_token}
        
        app_redirect_url = f"{app_callback_scheme}://?status=success" # Temporary change for debugging
        
        print(f"Redirecting to Swift app: {app_redirect_url}")
        return RedirectResponse(app_redirect_url)
    else:
        error_detail = "Failed to exchange authorization code for token or token missing in credentials."
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

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
        raise HTTPException(
            status_code=401,
            detail="Not authenticated with Google Drive. Please authenticate via /auth/google endpoint."
        )

    try:
        result_dict = await run_scout_orchestration(
            file_id_to_process=payload.file_name, 
            drive_service=drive_service,
            original_file_name=payload.file_name 
        )
        return OrchestratorResponse(**result_dict)
    except Exception as e:
        print(f"Error in /process-file endpoint: {e}")
        return OrchestratorResponse(
            original_file=payload.file_name,
            status_updates=[f"Endpoint error: {str(e)}"],
            error_message=str(e)
        )

# New endpoint to handle PDF uploads from the mobile app
@app.post("/upload-pdf", response_model=OrchestratorResponse)
async def upload_pdf_endpoint(file: UploadFile = File(...)):
    drive_service = get_drive_service()
    if not drive_service:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated with Google Drive. Please authenticate via /auth/google endpoint."
        )

    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="File must be a PDF"
        )

    try:
        # Save the uploaded PDF temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Upload to Google Drive first
        from googleapiclient.http import MediaFileUpload
        
        file_metadata = {
            'name': file.filename,
            'parents': []  # Will be organized by the orchestrator
        }
        
        media = MediaFileUpload(temp_file_path, mimetype='application/pdf')
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = uploaded_file.get('id')
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        # Now run the orchestrator on the uploaded file
        result_dict = await run_scout_orchestration(
            file_id_to_process=file_id, 
            drive_service=drive_service,
            original_file_name=file.filename 
        )
        return OrchestratorResponse(**result_dict)
        
    except Exception as e:
        print(f"Error in /upload-pdf endpoint: {e}")
        return OrchestratorResponse(
            original_file=file.filename,
            status_updates=[f"Upload error: {str(e)}"],
            error_message=str(e)
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
