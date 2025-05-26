from agents import Agent, Runner, set_default_openai_key 
from dotenv import load_dotenv
from tools.rename_drive_file_tool import rename_drive_file 
import os
import asyncio
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class RenameFileOutput(BaseModel): 
    filename: str

# Create the agent
rename_agent = Agent(
    name="Google Drive File Rename Agent",
    instructions=(
        "You are an agent that renames files in Google Drive. "
        "You will receive a dictionary as input containing: "
        "  'drive_service': The authenticated Google Drive API client, "
        "  'file_id': The ID of the file to rename, "
        "  'current_file_name': The current name of the file, "
        "  'context': Information extracted from the file's content by a previous agent, "
        "  'task_prompt': Specific instructions for this renaming task (e.g., 'Suggest a new, concise, and descriptive filename...')."
        "Your primary goal is to follow the 'task_prompt' to determine an appropriate new filename based on the 'current_file_name' and 'context'."
        "Once you have decided on the new filename, you MUST use the 'rename_drive_file' tool to actually rename the file in Google Drive. "
        "Provide the tool with the 'drive_service', 'file_id', and the 'new_name' you've decided on."
        "Your final output MUST be ONLY the new filename that the file was successfully renamed to (as returned by the tool), in the 'filename' field of the output model. "
        "Do not add any other description, explanation, or text."
    ),
    model="gpt-4.1-mini", 
    tools=[rename_drive_file],
    output_type=RenameFileOutput
)

async def main():
    test_run = await Runner.run(rename_agent, "Rename the file so it's matching the given input.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())