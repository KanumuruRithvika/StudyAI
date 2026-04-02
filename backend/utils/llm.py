import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import time
import random

load_dotenv()

# 🔥 LANGSMITH TRACING SETUP
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "agentic-learning"
# Make sure LANGCHAIN_API_KEY is set in .env file

def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.4,
        max_tokens=400,   # 🔥 INCREASED FOR FULL QUIZ OUTPUT (5 questions with 4 options each)
        api_key=os.getenv("GROQ_API_KEY"),
        max_retries=3,    
        timeout=30.0      
    )

def call_llm_with_retry(llm, prompt, max_retries=5):
    """Call LLM with exponential backoff on rate limit"""
    from groq import RateLimitError
    
    for attempt in range(max_retries):
        try:
            time.sleep(0.5)  # 🔥 SMALL DELAY BETWEEN CALLS
            return llm.invoke(prompt)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"⏳ Rate limited. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                raise