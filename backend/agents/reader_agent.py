from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from backend.tools.read_pdf import read_pdf

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Create the agent
reader_agent = Agent(
    name="Reader Agent",
    instructions="You read a PDF file in the assets folder and interpret its content. Give the interpretet content to the next agent as a keyword so the agent understands what the file is about.",
    model="gpt-4.1-mini",
    tools=[read_pdf]
)

async def main():
    test_run = await Runner.run(reader_agent, "Read the file 'downloaded_test_file_1.pdf' in the assets folder.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())