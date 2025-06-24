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
        "PROCESSING APPROACH: "
        "1. For scanned documents (images), prioritize vision analysis using 'analyze_pdf_images' tool first "
        "2. Always attempt text extraction using 'read_local_pdf' tool as well "
        "3. If vision analysis is available, use it as the primary source of information "
        "4. If text extraction returns minimal content, rely heavily on vision analysis "
        "5. Combine both analyses to provide the most comprehensive understanding possible "
        "FOCUS: Identify document type, main topics, key information, and suitable organizational categories. "
        "OUTPUT: Provide comprehensive information about the document content in the 'content' field, suitable for file organization and categorization. "
        "Be thorough but concise, focusing on the most important aspects for organizing and categorizing the file. "
        "For scanned documents, emphasize what you can see in the images over limited text extraction results."
    ),
    model="gpt-4o-mini", 
    tools=[read_local_pdf, analyze_pdf_images],
    output_type=ExtractedContent 
)

async def main():
    test_run = await Runner.run(reader_agent, "Read the local PDF file 'downloaded_test_file_1.pdf' and extract key information for organization.")
    print(test_run.final_output)

if __name__ == "__main__":
    asyncio.run(main())