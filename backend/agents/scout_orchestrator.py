from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from backend.agents.reader_agent import reader_agent
from backend.agents.rename_agent import rename_agent
from backend.agents.organizer_agent import organizer_agent

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Create the agent
scout_orchestrator = Agent(
    name="Scout Orchestrator",
    instructions=(
        "You are the scout orchestrator. You decide to which agent you use to complete the task."
        "The workflow is in the following order:"
        "1. Reader Agent"
        "2. Rename Agent"
        "3. Organizer Agent"
    ),
    model="gpt-4.1-mini",
    tools=[
        reader_agent.as_tool(
            tool_name="Reader Agent",
            tool_description="You read a PDF file in the assets folder and interpret its content.",
        ), 
        rename_agent.as_tool(
            tool_name="Rename Agent",
            tool_description="You rename a PDF file in the assets folder.",
        ), 
        organizer_agent.as_tool(
            tool_name="Organizer Agent",
            tool_description="You organize the assets folder.",
        )]
)

async def main():
    test_run = await Runner.run(scout_orchestrator, "Read the file 'Lorem Ipsum.pdf' in the assets folder.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())