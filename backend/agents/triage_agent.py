from agents import Agent, set_default_openai_key
from dotenv import load_dotenv
import os

load_dotenv()

# Set the default OpenAI key
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Create the agent
agent = Agent(
    name="Triage Agent",
    instructions="You decide to which agent you handoff the task.",
    model="gpt-4.1-mini",
)    