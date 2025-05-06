from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from backend.tools.manage_folder import move_file

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Create the agent
file_mover_agent = Agent(
    name="File Mover Agent",
    instructions=(
        "You are part of a multi-agent network. Your job is to move a file to a folder."
        "The input you get is the name of a file the agent network is trying to organize."
        "The file must be moved and it is your job to do so. You don't have to create a folder or evaluate in which it should move. Get that from the input."
        "Just move the file."
    ),
    model="gpt-4.1-mini",
    tools=[move_file]
)

async def main():
    test_run = await Runner.run(file_mover_agent, "You are delegated with a file. Create a folder with the same name as the file and move the file into it.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())