from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from tools.move_drive_file_tool import move_drive_file
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class FileMoveConfirmation(BaseModel):
    file_id: str
    moved_to_folder_id: str
    status: str # e.g., 'success' or 'failure'

# Create the agent
file_mover_agent = Agent(
    name="Google Drive File Mover Agent",
    instructions=(
        "You are an agent that moves files to a specified folder within Google Drive. "
        "You will receive a dictionary as input containing: "
        "  'drive_service': The authenticated Google Drive API client, "
        "  'file_id': The ID of the file to be moved, "
        "  'target_folder_id': The ID of the destination folder in Google Drive, "
        "  'file_name': (For context) The name of the file being moved, "
        "  'target_folder_name': (For context) The name of the target folder, "
        "  'task_prompt': Specific instructions for this moving task (usually straightforward, e.g., 'Move the file to the target folder.')."
        
        "Your sole responsibility is to move the file specified by 'file_id' into the folder specified by 'target_folder_id'."
        "You MUST use the 'move_drive_file' tool to perform this action. Provide it with 'drive_service', 'file_id', and 'target_folder_id' from your input."
        "Your final output MUST be the confirmation returned by the 'move_drive_file' tool, matching the FileMoveConfirmation model (containing 'file_id', 'moved_to_folder_id', and 'status')."
    ),
    model="gpt-4.1-mini", # Or your preferred model
    tools=[move_drive_file],
    output_type=FileMoveConfirmation
)

# async def main():
#     test_run = await Runner.run(file_mover_agent, {
#         "drive_service": {}, 
#         "file_id": "some_file_id_to_move",
#         "target_folder_id": "some_target_folder_id",
#         "file_name": "MyDocument.gdoc",
#         "target_folder_name": "Project Documents",
#         "task_prompt": "Move the file to the designated project folder."
#     })
#     print(test_run.final_output)

# if __name__ == "__main__":
#     asyncio.run(main())
pass