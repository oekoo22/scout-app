from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Create the agent
agent = Agent(
    name="Rename Agent",
    instructions="You rename a PDF file in the assets folder.",
    model="gpt-4.1-mini"
)

async def main():
    test_run = await Runner.run(agent, "Why is the sky blue?")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())
    