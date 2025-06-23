from agents import Agent, Runner, set_default_openai_key
from dotenv import load_dotenv
import os
import asyncio
from tools.read_local_pdf import read_local_pdf
from tools.analyze_pdf_images import analyze_pdf_images
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
        "You are an agent that processes local PDF files for organization purposes. "
        "You have access to two tools: 'read_local_pdf' for text extraction and 'analyze_pdf_images' for vision analysis. "
        "Your primary goal is to follow the 'task_prompt' instructions. "
        "PROCESSING APPROACH: "
        "1. If the task prompt contains PDF images data (JSON string), use 'analyze_pdf_images' tool to get visual understanding of the PDF content. "
        "2. Always use 'read_local_pdf' tool to extract text content from the PDF file path provided in the task prompt. "
        "3. Combine both vision analysis and text extraction to provide comprehensive understanding. "
        "4. If no images data is provided, rely solely on text extraction using 'read_local_pdf' tool. "
        "FOCUS: Identify document type, main topics, key information, and suitable organizational categories. "
        "OUTPUT: Your final output should be comprehensive information about the document content in the 'content' field, suitable for file organization and categorization. "
        "Be thorough but concise, focusing on the most important aspects for organizing and categorizing the file."
    ),
    model="gpt-4.1-mini", 
    tools=[read_local_pdf, analyze_pdf_images],
    output_type=ExtractedContent 
)

async def main():
    test_run = await Runner.run(reader_agent, "Read the local PDF file 'downloaded_test_file_1.pdf' and extract key information for organization.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())