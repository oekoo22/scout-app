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
    instructions="You organize the assets folder.",
    model="gpt-4.1-mini",
    tools=[create_folder, move_file]
)

async def main():
    test_run = await Runner.run(organizer_agent, "Create a folder named after the input you get and move the file you are delegated with into it.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())