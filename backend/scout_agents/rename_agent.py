from agents import Agent, Runner, set_default_openai_key 
from dotenv import load_dotenv
from tools.rename_local_file import rename_local_file 
import os
import asyncio
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class RenameFileOutput(BaseModel): 
    filename: str

# Create the agent
rename_agent = Agent(
    name="Local File Rename Agent",
    instructions=(
        "You are an agent that renames local files. "
        "You will receive a task prompt containing information about a local file to rename. "
        "The task prompt will include the current file path, current file name, and context from the file content. "
        "Your primary goal is to follow the 'task_prompt' to determine an appropriate new filename based on the current name and context. "
        "Once you have decided on the new filename, you MUST use the 'rename_local_file' tool to actually rename the file. "
        "Extract the current file path from the task prompt and provide it along with your suggested new filename to the tool. "
        "Your final output MUST be ONLY the new filename that the file was successfully renamed to, in the 'filename' field of the output model. "
        "Do not add any other description, explanation, or text."
    ),
    model="gpt-4.1-mini", 
    tools=[rename_local_file],
    output_type=RenameFileOutput
)

async def main():
    test_run = await Runner.run(rename_agent, "Rename the file so it's matching the given input.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())