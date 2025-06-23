from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from tools.move_local_file import move_local_file
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class FileMoveConfirmation(BaseModel):
    source_file_path: str
    target_folder_path: str
    new_file_path: str | None = None
    status: str # e.g., 'success' or 'failure'
    error: str | None = None

# Create the agent
file_mover_agent = Agent(
    name="Local File Mover Agent",
    instructions=(
        "You are an agent that moves local files to a specified folder. "
        "You will receive a task prompt containing information about moving a local file. "
        "The task prompt will include the source file path, target folder path, file name, and target folder name. "
        
        "Your sole responsibility is to move the file from its current location to the target folder. "
        "You MUST use the 'move_local_file' tool to perform this action. "
        "Extract the source file path and target folder path from the task prompt and provide them to the tool. "
        "Your final output MUST be the confirmation returned by the 'move_local_file' tool, matching the FileMoveConfirmation model."
    ),
    model="gpt-4.1-mini",
    tools=[move_local_file],
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