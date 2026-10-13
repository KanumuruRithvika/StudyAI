from models.schemas import TaskList
from models.state import LearningState
from utils.llm import get_llm
from utils.parser import parse_json_response


def build_task_prompt(state: LearningState) -> str:
    if state.get("adaptive_action") == "improve_weak_topics":
        return build_improvement_prompt(state)

    topic = state.get("current_topic", "")

    topic_data = next(
        (
            item
            for item in state.get("plan", {}).get("topics", [])
            if item["title"] == topic
        ),
        {},
    )

    objectives = topic_data.get("objectives", [])

    project_context = ""

    if state.get("learning_mode") == "project":
        project_context = f"""
Project:
{state.get("project_name", "")}

Project description:
{state.get("project_description", "")}

Required technologies:
{", ".join(state.get("required_technologies", []))}
"""

    carried_forward = state.get(
        "carried_forward_tasks",
        [],
    )

    carried_forward_text = ""

    if carried_forward:
        carried_forward_text = """
Unfinished tasks from the previous day:

""" + "\n".join(
            f"- {task['id']}: {task['title']} "
            f"({task['estimated_minutes']} minutes)"
            for task in carried_forward
        ) + """

Include these tasks using their original IDs and details.
Do not replace them with different tasks.
"""

    return f"""
Create today's learning tasks for the current topic.

Topic:
{topic}

Topic objectives:
{chr(10).join(f"- {objective}" for objective in objectives)}

Current day:
{state.get("current_day", 1)}

Available time today:
{state.get("available_time_minutes", 60)} minutes

{project_context}

{carried_forward_text}

Rules:
- Generate tasks only for the current topic.
- Tasks must directly support the topic objectives.
- Do not create tasks for another topic.
- Never mark a task as completed.
- Include every unfinished carried-forward task.
- Keep original IDs and details for carried-forward tasks.
- Add new tasks only when time remains.
- Keep the total workload realistic.
- Do not create duplicate tasks.
- Do not generate all remaining topic work in one day.
- Tasks may be study, practice, coding, problem-solving, or project work.
- Every new task must have a unique ID.
- task_type must be exactly "study", "practice", or "project".

Return only valid JSON:

{{
    "tasks": [
        {{
            "id": "task-1",
            "title": "Task title",
            "description": "What the learner must do",
            "task_type": "study",
            "estimated_minutes": 20,
            "objective": "What this task develops"
        }}
    ]
}}
""".strip()


def build_improvement_prompt(state: LearningState) -> str:
    weak_topics = state.get("weak_topics", [])
    improvement_description = state.get(
        "improvement_description",
        "",
    )
    improvement_days = state.get(
        "improvement_days",
        1,
    )
    improvement_time = state.get(
        "improvement_time_minutes",
        state.get("available_time_minutes", 60),
    )

    project_context = ""

    if state.get("learning_mode") == "project":
        project_context = f"""
Project:
{state.get("project_name", "")}

Project description:
{state.get("project_description", "")}

Required technologies:
{", ".join(state.get("required_technologies", []))}
"""

    return f"""
Create a small focused improvement task set for the learner.

Weak areas:
{chr(10).join(f"- {topic}" for topic in weak_topics)}

Improvement guidance:
{improvement_description}

Improvement duration:
{improvement_days} day(s)

Available improvement time:
{improvement_time} minutes

{project_context}

Rules:
- Focus only on the identified weak areas.
- Do not repeat the complete original topic.
- Generate AT MOST 3 remediation tasks. If 1 or 2 tasks are sufficient, generate only 1 or 2. Never generate more than 3 tasks.
- Prioritize the concepts the learner performed poorly on.
- Include a short study task when conceptual understanding is weak.
- Include practice or problem-solving when application is weak.
- Include a project task only when practical implementation is the weakness.
- Tasks must directly address the improvement guidance.
- Do not create unrelated tasks.
- Keep the total workload within the available improvement time.
- Every task must have a unique ID.
- task_type must be exactly "study", "practice", or "project".

Return only valid JSON:

{{
    "tasks": [
        {{
            "id": "improvement-1",
            "title": "Focused improvement task",
            "description": "What the learner must do",
            "task_type": "practice",
            "estimated_minutes": 20,
            "objective": "Specific weak area being improved"
        }}
    ]
}}
""".strip()


def normalize_task_types(data: dict) -> dict:
    aliases = {
        "coding": "practice",
        "reading": "study",
        "research": "study",
        "theory": "study",
        "implementation": "project",
        "development": "project",
        "hands_on": "project",
    }

    for task in data.get("tasks", []):
        task_type = str(
            task.get("task_type", "")
        ).strip().lower()

        task["task_type"] = aliases.get(
            task_type,
            task_type,
        )

    return data


def generate_tasks(state: LearningState) -> dict:
    response = get_llm().invoke(
        build_task_prompt(state)
    )

    data = normalize_task_types(
        parse_json_response(response)
    )

    task_list = TaskList.model_validate(data)

    if state.get("adaptive_action") == "improve_weak_topics":
        tasks = []

        # Enforce at most 3 remediation tasks
        for task in task_list.tasks[:3]:
            task_data = task.model_dump()

            task_data["id"] = get_unique_task_id(
                task_data["id"],
                state,
                tasks,
            )

            tasks.append(task_data)

        return {
            "tasks": tasks,
            "completed_tasks": [],
            "unfinished_tasks": [],
            "skipped_tasks": [],
            "carried_forward_tasks": [],
        }

    carried_forward = {
        task["id"]: task
        for task in state.get(
            "carried_forward_tasks",
            [],
        )
    }

    tasks = []

    for task in task_list.tasks:
        task_data = task.model_dump()

        if task_data["id"] in carried_forward:
            tasks.append(
                carried_forward[task_data["id"]]
            )
            continue

        task_data["id"] = get_unique_task_id(
            task_data["id"],
            state,
            tasks,
        )

        tasks.append(task_data)

    existing_ids = {
        task["id"]
        for task in tasks
    }

    for task in carried_forward.values():
        if task["id"] not in existing_ids:
            tasks.insert(0, task)

    return {
        "tasks": tasks,
        "completed_tasks": [],
        "unfinished_tasks": [
            task["id"]
            for task in carried_forward.values()
        ],
        "skipped_tasks": [],
        "carried_forward_tasks": [],
    }


def are_tasks_complete(state: LearningState) -> bool:
    tasks = state.get("tasks", [])

    if not tasks:
        return False

    completed = set(
        state.get("completed_tasks", [])
    )

    skipped = set(
        state.get("skipped_tasks", [])
    )

    return all(
        task["id"] in completed
        or task["id"] in skipped
        for task in tasks
    )


def get_unique_task_id(
    task_id: str,
    state: LearningState,
    current_tasks: list[dict],
) -> str:
    existing_ids = {
        task["id"]
        for task in state.get("tasks", [])
    }

    existing_ids.update(
        task["id"]
        for task in current_tasks
    )

    if task_id not in existing_ids:
        return task_id

    counter = 2

    while f"{task_id}-{counter}" in existing_ids:
        counter += 1

    return f"{task_id}-{counter}"