from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
from backend.tools.rename_pdf import rename_pdf
import os
import asyncio

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Create the agent
agent = Agent(
    name="Rename Agent",
    instructions="You rename a PDF file in the assets folder.",
    model="gpt-4.1-mini",
    tools=[rename_pdf]
)

async def main():
    test_run = await Runner.run(agent, "Rename the file 'scout_pdf_test.pdf' to 'Lorem Ipsum")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())
    