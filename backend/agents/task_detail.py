"""
Task detail generator — produces a structured how-to guide
with step-by-step instructions and external tool/resource recommendations.
"""
from models.state import LearningState
from utils.llm import get_llm
from utils.parser import parse_json_response


def build_task_detail_prompt(task: dict, topic: str, learning_mode: str) -> str:
    task_type = task.get("task_type", "study")
    return f"""
You are a learning assistant. Generate a structured completion guide for the following learning task.

Topic: {topic}
Task title: {task.get("title", "")}
Task description: {task.get("description", "")}
Task type: {task_type}
Objective: {task.get("objective", "")}
Estimated time: {task.get("estimated_minutes", 30)} minutes
Learning mode: {learning_mode}

Return a JSON object with:
- "how_to_complete": Array of 3-6 clear step-by-step instructions telling the learner exactly HOW to complete this task.
- "key_concepts": Array of 2-5 important concepts or terms the learner needs to understand for this task.
- "tips": Array of 2-4 practical tips or common mistakes to avoid.
- "tools": Array of 3-6 tool/resource objects, each with:
  - "name": Name of the tool, website, or resource
  - "url": Direct URL to the resource
  - "description": One sentence describing how it helps with THIS specific task
  - "type": one of "documentation", "tutorial", "tool", "practice", "video", "reference"

Rules for tools:
- ONLY include real, working URLs (e.g., docs.python.org, developer.mozilla.org, leetcode.com, youtube.com, github.com, w3schools.com, freecodecamp.org, etc.)
- Tailor tools specifically to the task topic and task type
- For study tasks: include official docs, tutorials, video resources
- For practice tasks: include interactive platforms (LeetCode, HackerRank, Exercism, Replit, CodePen)
- For project tasks: include GitHub examples, scaffold tools, deployment platforms
- Never make up URLs

Return only valid JSON, no explanation:

{{
    "how_to_complete": [
        "Step 1: ...",
        "Step 2: ...",
        "Step 3: ..."
    ],
    "key_concepts": [
        "Concept 1: explanation",
        "Concept 2: explanation"
    ],
    "tips": [
        "Tip 1",
        "Tip 2"
    ],
    "tools": [
        {{
            "name": "Tool name",
            "url": "https://example.com",
            "description": "How this helps with the task",
            "type": "documentation"
        }}
    ]
}}
""".strip()


def generate_task_detail(task: dict, state: dict) -> dict:
    """Generate structured completion guide + tools for a single task."""
    topic = state.get("current_topic", "")
    learning_mode = state.get("learning_mode", "general")

    prompt = build_task_detail_prompt(task, topic, learning_mode)
    response = get_llm().invoke(prompt)
    data = parse_json_response(response)

    return {
        "task_id": task.get("id", ""),
        "title": task.get("title", ""),
        "description": task.get("description", ""),
        "objective": task.get("objective", ""),
        "task_type": task.get("task_type", "study"),
        "estimated_minutes": task.get("estimated_minutes", 30),
        "how_to_complete": data.get("how_to_complete", []),
        "key_concepts": data.get("key_concepts", []),
        "tips": data.get("tips", []),
        "tools": data.get("tools", []),
    }

