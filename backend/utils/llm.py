import os
import re
import time

from dotenv import load_dotenv
from groq import RateLimitError
from langchain_groq import ChatGroq


load_dotenv(override=True)


class RetryingChatGroq(ChatGroq):
    """ChatGroq client with bounded retry handling for rate limits."""

    def invoke(self, *args, **kwargs):
        for attempt in range(4):
            try:
                return super().invoke(
                    *args,
                    **kwargs,
                )

            except RateLimitError as error:
                if attempt == 3:
                    raise

                match = re.search(
                    r"try again in ([0-9.]+)s",
                    str(error),
                )

                if not match:
                    raise

                wait_time = float(
                    match.group(1)
                ) + 1

                if wait_time > 30:
                    raise

                time.sleep(wait_time)


def get_llm() -> RetryingChatGroq:
    """Create the configured Groq LLM client."""
    api_key = os.getenv("GROQ_API_KEY")
    model_name = os.getenv("GROQ_MODEL")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set."
        )

    if not model_name:
        raise RuntimeError(
            "GROQ_MODEL is not set."
        )

    return RetryingChatGroq(
        model=model_name,
        api_key=api_key,
        temperature=0.2,
        max_tokens=4096,
        max_retries=2,
    )