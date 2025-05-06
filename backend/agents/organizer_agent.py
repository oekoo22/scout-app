from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
from backend.tools.manage_folder import create_folder, move_file
import os
import asyncio

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Create the agent
organizer_agent = Agent(
    name="Organizer Agent",
    instructions=
    "Look how the file is named. Decide, if there is a folder in the assets folder in which you can sort the file. Decide logic-wise, e.g. wage documents go to private/wage_documents/., business documents go to private/business_documents/. and so on." 
    "If there is no matching folder, create a new one so the user can find it easily." 
    "Then move the file in the folder you evaluated it belongs to.",
    model="gpt-4.1-mini",
    tools=[create_folder, move_file]
)

async def main():
    test_run = await Runner.run(organizer_agent, "You are delegated with a file. Create a folder with the same name as the file and move the file into it.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())