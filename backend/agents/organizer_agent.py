from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
from backend.tools.manage_folder import create_folder, move_file
import os
import asyncio
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class FolderValidator(BaseModel):
    folder_name: str
    folder_is_already_created: bool

folder_preparator = Agent(
    name="Folder Preparator",
    instructions=(
        "You are an assistant for the organizer_agent. Your job is to evaluate if there is a folder in the assets folder in which you can sort the file or create a new one if it doesn't exist."
        "Your final_output must be maching the FolderValidator model. You need to give the folder_name as a string and validate if their is already existing a folder, where the file could go in and give that as a boolean."
    ),
    model="gpt-4.1-mini",
    output_type=FolderValidator
)

# Create the agent
organizer_agent = Agent(
    name="Organizer Agent",
    instructions=(
    "First, before doing any action, you MUST use the tool folder_preparator."
    "You are part of a multi agent network and your job is to organize a file. You'll get input from another agent who's job is to read the file and give you a keyword as output."
    "If folder_is_already_created is True, you can move the file in the folder."
    "If folder_is_already_created is False, you need to create a new folder and then move the file in it. The name of the folder should be self explanatory to the user and should match the meaning of the file."
    ),
    model="gpt-4.1-mini",
    tools=[folder_preparator.as_tool(
        tool_name="folder_preparator",
        tool_description="Get the preperation for a file and see if there is already existing a folder and/or how the folder or a new one is named."
    ), create_folder, move_file],
)

async def main():
    test_run = await Runner.run(organizer_agent, "You are delegated with a file. Create a folder with the same name as the file and move the file into it.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())