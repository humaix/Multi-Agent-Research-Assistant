
# import os
# from dotenv import load_dotenv
# from langchain_groq import ChatGroq

# # Load environment variables
# load_dotenv()

# # Read API key
# api_key = os.getenv("GROQ_API_KEY")

# if not api_key:
#     raise ValueError("GROQ_API_KEY is missing from .env")

# # Initialize Groq LLM
# llm = ChatGroq(
#     model="openai/gpt-oss-20b",
#     api_key=api_key,
#     temperature=0.2,
#     max_tokens=1200,
#     timeout=30,
#     max_retries=2,
#     reasoning_format="hidden"
# )



import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Read API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing from .env")


# Main LLM for Planner, Analyst and other agents
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=api_key,
    temperature=0.2,
    max_tokens=4096,
    timeout=30,
    max_retries=2,
    reasoning_effort="low",
    # include_reasoning=False
)


# Dedicated LLM for Fact Checker
fact_checker_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=api_key,
    temperature=0.1,
    max_tokens=4096,
    timeout=30,
    max_retries=2,
    reasoning_effort="low",
    # include_reasoning=False
)
