import os

from tavily import TavilyClient

from models.schemas import LearningContent
from models.state import LearningState
from utils.llm import get_llm
from utils.parser import parse_json_response


def search_learning_sources(
    query: str,
    max_results: int = 5,
) -> list[dict]:
    """Search external learning resources using Tavily."""
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return []

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
        include_raw_content=False,
    )

    return [
        {
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
        }
        for result in response.get("results", [])
        if result.get("url")
    ]


def should_use_external_sources(state: LearningState) -> bool:
    """
    Determine whether current or external information is useful
    for generating the task content.
    """
    task = state.get("task_details", {})
    topic = state.get("current_topic", "").lower()

    task_text = " ".join(
        [
            str(task.get("title", "")),
            str(task.get("description", "")),
            str(task.get("objective", "")),
        ]
    ).lower()

    external_keywords = {
        "latest",
        "current",
        "recent",
        "new",
        "updated",
        "version",
        "documentation",
        "official docs",
        "best practices",
        "release",
        "api",
        "framework",
        "library",
    }

    search_text = f"{topic} {task_text}"

    return any(
        keyword in search_text
        for keyword in external_keywords
    )


def build_source_text(sources: list[dict]) -> str:
    """Format retrieved sources so the LLM can use them as evidence."""
    if not sources:
        return "No external sources were retrieved."

    return "\n\n".join(
        (
            f"Source {index}:\n"
            f"Title: {source['title']}\n"
            f"URL: {source['url']}\n"
            f"Content: {source['content']}"
        )
        for index, source in enumerate(sources, start=1)
    )


def build_content_prompt(
    state: LearningState,
    sources: list[dict],
) -> str:
    """Build the prompt used to generate detailed learning content."""
    topic = state.get("current_topic", "")
    task = state.get("task_details", {})

    source_text = build_source_text(sources)

    return f"""
Create detailed learning content for the learner.

Current topic:
{topic}

Task:
{task}

Learner level:
{state.get("current_level", "beginner")}

Learning goal:
{state.get("goal", "")}

Learning mode:
{state.get("learning_mode", "general")}

Project:
{state.get("project_name", "")}

Use the external sources below when they are available.
Treat them as supporting evidence and do not invent facts
that are presented as coming from those sources.

External sources:
{source_text}

Create practical, understandable learning material.

Return only valid JSON with this structure:

{{
  "title": "...",
  "explanation": "...",
  "learning_objective": "...",
  "key_concepts": ["..."],
  "step_by_step": ["..."],
  "examples": ["..."],
  "common_mistakes": ["..."],
  "practice": ["..."],
  "mini_challenge": "...",
  "expected_outcome": "...",
  "completion_criteria": ["..."]
}}

Rules:
- Explain the topic at the learner's level.
- Focus only on the current topic and task.
- Use technical terminology accurately.
- Include practical examples where appropriate.
- Include code examples when the task requires implementation.
- Explain concepts step by step.
- Include common mistakes that learners should avoid.
- Include practical practice activities.
- Include a small challenge when appropriate.
- Define a clear expected outcome.
- Define practical completion criteria.
- Do not mention that you are an AI.
- Do not include URLs inside the generated explanation.
- Return only valid JSON.
""".strip()


def build_external_search_query(state: LearningState) -> str:
    """Build a focused search query for external learning resources."""
    topic = state.get("current_topic", "")
    task = state.get("task_details", {})

    query_parts = [
        topic,
        task.get("title", ""),
        task.get("description", ""),
        state.get("goal", ""),
    ]

    if state.get("learning_mode") == "project":
        query_parts.extend(
            [
                state.get("role", ""),
                state.get("project_name", ""),
                "official documentation tutorial",
            ]
        )

    return " ".join(
        part.strip()
        for part in query_parts
        if isinstance(part, str) and part.strip()
    )


def generate_learning_content(
    state: LearningState,
) -> dict:
    """
    Generate detailed learning material for the current task.

    External retrieval is used only when the task benefits from
    current or externally verified information.
    """
    sources = []

    if should_use_external_sources(state):
        query = build_external_search_query(state)
        sources = search_learning_sources(
            query,
            max_results=5,
        )

    response = get_llm().invoke(
        build_content_prompt(
            state,
            sources,
        )
    )

    content_data = parse_json_response(response)

    content = LearningContent(
        **content_data,
        external_sources=[
            {
                "title": source["title"],
                "url": source["url"],
            }
            for source in sources
        ],
    )

    return {
        "learning_content": content.model_dump(),
    }