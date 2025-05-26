from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from tools.read_drive_file_content_tool import get_drive_file_text_content
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
    name="Google Drive File Reader Agent",
    instructions=(
        "You are an agent that processes files stored in Google Drive. "
        "You will receive a dictionary as input containing 'drive_service' (an authenticated Google Drive API client), "
        "'file_id' (the ID of the file to process), and 'task_prompt' (specific instructions for this task)."
        "Your primary goal is to follow the 'task_prompt'. To do this, you MUST use the 'get_drive_file_text_content' tool "
        "to fetch and extract text content from the specified Google Drive file using the provided 'drive_service' and 'file_id'."
        "After obtaining the text content, analyze it based on the 'task_prompt' (e.g., summarize, extract keywords, etc.)."
        "Your final output should be the processed information (e.g., keywords, summary) as a string in the 'content' field of the output model."
        "Focus on extracting one or two main keywords or a very short summary as per the typical task prompt unless specified otherwise."
    ),
    model="gpt-4.1-mini", 
    tools=[get_drive_file_text_content],
    output_type=ExtractedContent 
)

async def main():
    test_run = await Runner.run(reader_agent, "Read the file 'downloaded_test_file_1.pdf' in the assets folder.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())