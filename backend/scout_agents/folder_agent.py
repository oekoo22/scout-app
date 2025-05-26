from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from tools.search_drive_folders_tool import search_drive_folders
from tools.create_drive_folder_tool import create_drive_folder
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class DriveFolderOutput(BaseModel):
    folder_name: str
    folder_id: str

folder_agent = Agent(
    name="Google Drive Folder Agent",
    instructions=(
        "You are an agent that determines or creates an appropriate folder in Google Drive for a given file. "
        "You will receive a dictionary as input containing: "
        "  'drive_service': The authenticated Google Drive API client, "
        "  'file_id': The ID of the file being processed (for context, not direct action by this agent), "
        "  'file_name': The name of the file being processed, "
        "  'context': Information extracted from the file's content by a previous agent, "
        "  'task_prompt': Specific instructions for folder selection/creation (e.g., 'Find or create a folder named ProjectX for this file.')."
        
        "Your process is as follows:"
        "1. Based on the 'file_name', 'context', and 'task_prompt', determine the ideal target folder name. The 'task_prompt' is the primary guide for the folder name."
        "2. Use the 'search_drive_folders' tool with the 'drive_service' and the determined folder name (or a relevant query derived from it) to check if a suitable folder already exists. "
        "   If multiple folders are returned, use the 'task_prompt' and your judgment to select the most appropriate one. An exact name match is preferred if available."
        "3. If a suitable existing folder is found and selected, use its 'name' and 'id' for your output."
        "4. If no suitable folder is found, or if the 'task_prompt' explicitly directs creation, use the 'create_drive_folder' tool. "
        "   Provide it with 'drive_service' and the target folder name. You can optionally specify 'parent_folder_id' if the 'task_prompt' gives clear instructions for a nested structure, otherwise, the folder will be created in the root."
        "5. Your final output MUST be the 'folder_name' and 'folder_id' of the selected or newly created folder, matching the DriveFolderOutput model."
        "   Ensure the 'folder_id' is the actual ID from Google Drive."
    ),
    model="gpt-4.1-mini",
    tools=[search_drive_folders, create_drive_folder],
    output_type=DriveFolderOutput
)

# async def main():
#     # This local test won't work without mock/real drive_service, file details, etc.
#     # and the Agent/Runner framework correctly handling the new input structure.
#     # Example payload:
#     # mock_drive_service = {} 
#     # payload = {
#     #     "drive_service": mock_drive_service,
#     #     "file_id": "some_file_id",
#     #     "file_name": "Q3_Report_ProjectAlpha.pdf",
#     #     "context": "Quarterly financial report for Project Alpha.",
#     #     "task_prompt": "Organize this into a folder named 'Project Alpha Reports'. If it doesn't exist, create it."
#     # }
#     # test_run = await Runner.run(folder_agent, payload)
#     # print(test_run.final_output)

# if __name__ == "__main__":
#     # asyncio.run(main())

pass