from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from fastapi import HTTPException

# Import the main function from scout_orchestrator
from scout_agents.scout_orchestrator import main as run_scout_orchestration

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
    try:
        # The orchestrator's main function now accepts the filename
        # and returns a dictionary matching OrchestratorResponse.
        result_dict = await run_scout_orchestration(payload.file_name)
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
