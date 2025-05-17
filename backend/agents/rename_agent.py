from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
from backend.tools.rename_pdf import rename_pdf
import os
import asyncio
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class RenamePdfOutput(BaseModel):
    filename: str

# Create the agent
rename_agent = Agent(
    name="Rename Agent",
    instructions="You are part of a multi-agent system. Your job is to rename a PDF File. You get an input from another agent. That input is the name of the file you should rename."
    "Your final_output must be ONE thing: the name of the file you renamed. Nothing more. No description, no explanation, no other text. JUST the name of the file.",
    model="gpt-4.1-mini",
    tools=[rename_pdf],
    output_type=RenamePdfOutput
)

async def main():
    test_run = await Runner.run(rename_agent, "Rename the file so it's matching the given input.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())
    