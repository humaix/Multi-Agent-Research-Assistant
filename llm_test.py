
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load API key from .env
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Initialize Groq model
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=200,
    timeout=30,
    max_retries=2,
    reasoning_format="hidden"
)

try:
    print("Connecting to Groq...")

    response = llm.invoke(
        "Explain what an AI research assistant does in three sentences."
    )

    print("\n========== GROQ RESPONSE ==========\n")
    print(response.content)

except Exception as e:
    print("\nGroq API Error:")
    print(type(e).__name__, str(e))
