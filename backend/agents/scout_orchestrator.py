from agents import Agent, Runner, set_default_openai_key, trace, ItemHelpers
from dotenv import load_dotenv
import os
import asyncio
from backend.agents.reader_agent import reader_agent
from backend.agents.rename_agent import rename_agent
from backend.agents.file_mover_agent import file_mover_agent
from backend.agents.folder_agent import folder_agent

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

async def main():
    
    # Run entire workflow in one trace
    with trace("Scout Orchestrator Trace"): 
        msg = "Read the file 'test_file.pdf', then organize it with the given tools."

        read_file = await Runner.run(reader_agent, msg)

        input_items = read_file.to_input_list()

        print("Keyword for renaming the file: ", read_file.final_output)

        renamed_file = await Runner.run(rename_agent, input_items)

        input_items = renamed_file.to_input_list()
        print("File renamed to:", renamed_file.final_output)

        foldered_file = await Runner.run(folder_agent, f"Organize the file called {input_items}")

        print("File organized in:", foldered_file.final_output)

        moved_file = await Runner.run(file_mover_agent, f"Move the file called {renamed_file.final_output} to the folder {foldered_file.final_output}")

        print("File moved to:", moved_file.final_output)


if __name__ == "__main__":
    asyncio.run(main())