from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from tools.search_local_folders import search_local_folders
from tools.create_local_folder import create_local_folder
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class LocalFolderOutput(BaseModel):
    folder_name: str
    folder_path: str

folder_agent = Agent(
    name="Local Folder Agent",
    instructions=(
        "You are an agent that determines or creates an appropriate local folder for organizing a given file. "
        "You will receive a task prompt containing information about a local file to organize. "
        "The task prompt will include the file path, file name, and context from the file content. "
        
        "Your process is as follows:"
        "1. Based on the file name, context, and task prompt, determine the ideal target folder name. The task prompt is the primary guide for the folder name."
        "2. Extract the base directory from the file path (usually the directory containing the file). "
        "3. Use the 'search_local_folders' tool with the base directory and the determined folder name to check if a suitable folder already exists. "
        "   If multiple folders are returned, select the most appropriate one based on exact or close name matching."
        "4. If a suitable existing folder is found, use its name and path for your output."
        "5. If no suitable folder is found, use the 'create_local_folder' tool to create a new folder. "
        "   Provide it with the base directory and the target folder name."
        "6. Your final output MUST be the 'folder_name' and 'folder_path' of the selected or newly created folder, matching the LocalFolderOutput model."
        "   The folder_path should be the full absolute path to the folder."
    ),
    model="gpt-4o-mini",
    tools=[search_local_folders, create_local_folder],
    output_type=LocalFolderOutput
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