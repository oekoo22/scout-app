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
        "The following workflow should be treated as a one time per input task. You get one input and performe the workflow one time. Don't repeat the workflow."
        "Because this is workflow will be performed one time, be precise and work the workflow strictly from 1 to 3. Don't skip any step. Don't repeat any step."
        "The workflow is in the following order:"
        "1. Reader Agent - Read the file and interpret its content."
        "2. Rename Agent - Rename the file so it's matching the content of the file."
        "3. Organizer Agent - Organize folder structure."
        "It is important to keep context between the agents. Make sure that all the agents and tools always understand that their job is related to the file you get as an input."
        "Don't ask the user for instructions, you already know them! Go ahead with the workflow. Read the file, let it interpret the content, then rename it and organize it. There is no Human-in-the-Loop!"
        "You don't need any confirmation from the user. Do all steps by your own. Rename the file, you are allowed to do it. Create a folder, you are allowed to do it. Move the file, you are allowed to do it."
    ),
    model="gpt-4.1-mini",
    tools=[
        reader_agent.as_tool(
            tool_name="reader_agent",
            tool_description="You read a PDF file in the assets folder and interpret its content.",
        ), 
        rename_agent.as_tool(
            tool_name="rename_agent",
            tool_description="You rename a PDF file in the assets folder.",
        ), 
        organizer_agent.as_tool(
            tool_name="organizer_agent",
            tool_description="You organize the assets folder.",
        )]
)

async def main():
    test_run = await Runner.run(scout_orchestrator, "Read the file 'test_file.pdf', then organize it with the given tools.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())