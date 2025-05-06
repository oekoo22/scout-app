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
    "Look how the file is named. Decide, if there is a folder in the assets folder in which you can sort the file. Decide logic-wise, e.g. wage documents go to private/wage_documents/., business documents go to private/business_documents/. and so on." 
    "If there is no matching folder, create a new one so the user can find it easily.",
    model="gpt-4.1-mini",
    tools=[create_folder]
)

async def main():
    test_run = await Runner.run(folder_agent, "You are delegated with a file. Create a folder with the same name as the file and move the file into it.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())