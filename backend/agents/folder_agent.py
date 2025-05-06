from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from backend.tools.manage_folder import create_folder

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Create the agent
folder_agent = Agent(
    name="Folder Agent",
    instructions=
    "You are part of a multi-agent network. Your job is to take the input and evaluate if there is a folder which is matching the meaning of the input."
    "The input you get is the name of a file the agent network is trying to organize. Interpret the name of the file and evaluate if there is a folder which is matching the meaning of the input."
    "If there is no matching folder, create a new one so the user can find it easily."
    "If there is a matching folder, you just tell which folder matches the input.",
    model="gpt-4.1-mini",
    tools=[create_folder]
)

async def main():
    test_run = await Runner.run(folder_agent, "You are delegated with a file. Create a folder with the same name as the file and move the file into it.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())