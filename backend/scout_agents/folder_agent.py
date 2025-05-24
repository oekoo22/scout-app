from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from tools.manage_folder import create_folder
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class FolderPreparatorOutput(BaseModel):
    folder_is_already_created: bool

folder_preparator = Agent(
    name="Folder Preparator",
    instructions=(
        "You are a tool for the folder_agent. Your job is to evaluate if there is the need to create a new folder."
        "Your final_output must be maching the FolderValidator model. Your output is just one boolean True when there is the need to create a new folder, False when there is no need to create a new folder."
    ),
    model="gpt-4.1-mini",
    output_type=FolderPreparatorOutput
)

class FolderName(BaseModel):
    folder_name: str
    
# Create the agent
folder_agent = Agent(
    name="Folder Agent",
    instructions=(
    "First, before doing any action, you MUST use the tool folder_preparator."  
    "You are part of a multi-agent network. Your job is to take the input and evaluate if there is a folder which is matching the meaning of the input."
    "The input you get is the name of a file the agent network is trying to organize. Interpret the name of the file and evaluate if there is a folder which is matching the meaning of the input."
    "If folder_is_already_created is True, you have no job and just give the name of the folder as final_output."
    "If folder_is_already_created is False, you need to create a new folder. The name of the folder should be self explanatory to the user and should match the meaning of the file. Give the name of the folder as final_output."
    """The naming of the folder should follow the following naming convention:
    - The name of the folder should be in user friendly with camelCase.
    - The name of the folder should be in the language the user is using.
    """
    
    ),
    model="gpt-4.1-mini",
    tools=[create_folder],
    output_type=FolderName
)

async def main():
    test_run = await Runner.run(folder_agent, "You are delegated with a file. Create a folder with the same name as the file and move the file into it.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())