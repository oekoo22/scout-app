from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from tools.read_local_pdf import read_local_pdf
from pydantic import BaseModel

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

class ExtractedContent(BaseModel):
    content: str
    # Optionally, we can add file_id or name if needed in the output structure
    # file_id: str | None = None 
    # file_name: str | None = None

# Create the agent
reader_agent = Agent(
    name="Local PDF File Reader Agent",
    instructions=(
        "You are an agent that processes local PDF files. "
        "You will receive a task prompt containing the path to a local PDF file to process. "
        "Your primary goal is to follow the 'task_prompt'. To do this, you MUST use the 'read_local_pdf' tool "
        "to fetch and extract text content from the specified local PDF file using the file path. "
        "The read_local_pdf tool expects the full file path as provided in the task prompt. "
        "After obtaining the text content, analyze it based on the 'task_prompt' (e.g., summarize, extract keywords, etc.). "
        "Your final output should be the processed information (e.g., keywords, summary) as a string in the 'content' field of the output model. "
        "Focus on extracting one or two main keywords or a very short summary as per the typical task prompt unless specified otherwise."
    ),
    model="gpt-4.1-mini", 
    tools=[read_local_pdf],
    output_type=ExtractedContent 
)

async def main():
    test_run = await Runner.run(reader_agent, "Read the local PDF file 'downloaded_test_file_1.pdf' and extract key information for organization.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())