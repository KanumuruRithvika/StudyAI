from models.schemas import LearningPlan
from models.state import LearningState
from utils.llm import get_llm
from utils.parser import parse_json_response


def build_planner_prompt(state: LearningState) -> str:
    """Build the structured roadmap prompt from the current learning state."""
    feedback = state.get("plan_feedback", "")
    learning_mode = state.get("learning_mode", "general")

    project_context = ""

    if learning_mode == "project":
        skill_gaps = state.get("skill_gaps", [])

        project_context = f"""
Role:
{state.get("role", "")}

Project:
{state.get("project_name", "")}

Project description:
{state.get("project_description", "")}

Current skills:
{", ".join(state.get("current_skills", []))}

Required technologies and skills:
{", ".join(state.get("required_technologies", []))}

Identified skill gaps:
{", ".join(
    gap.get("skill", "")
    for gap in skill_gaps
)}
"""

    learner_context = f"""
Learning preferences:
{state.get("learning_preferences", "")}

Prior experience:
{state.get("prior_experience", "")}

Additional instructions:
{state.get("additional_instructions", "")}
"""

    revision_context = ""

    if feedback:
        revision_context = f"""
The learner rejected the previous plan.

Learner feedback:
{feedback}

Revise the roadmap according to the feedback while
preserving useful parts of the existing plan.
"""

    duration = state.get("duration_days")

    duration_context = (
        f"{duration} days"
        if duration
        else "an appropriate duration based on the learner's request"
    )

    return f"""
Create a practical topic-based learning roadmap.

Learning mode:
{learning_mode}

Goal:
{state.get("goal", "")}

Current level:
{state.get("current_level", "beginner")}

Available time per day:
{state.get("available_time_minutes", 60)} minutes

Total learning duration:
{duration_context}

{learner_context}

{project_context}

{revision_context}

Rules:
- Create learning TOPICS, not daily tasks.
- Each topic must represent one complete learning unit.
- Each topic must have clear learning objectives.
- estimated_days represents the expected number of learning days for that topic.
- Topics may span multiple days.
- Do not use Day 1, Day 2, Day 3, etc. as topic names.
- Do not include individual tasks in the roadmap.
- Daily tasks will be generated separately.
- Progress from foundational concepts toward more advanced concepts.
- Keep the number of topics realistic for the available duration.
- If a duration is provided, the total estimated topic days must fit within it.
- For project mode, prioritize identified skill gaps and required technologies.
- Do not create unrelated topics.
- Do not invent project requirements that were not provided.
- Keep the roadmap practical and achievable within the learner's available time.
- If learner feedback is provided, revise the previous plan accordingly.

Return only valid JSON:

{{
    "title": "Learning plan title",
    "summary": "Short summary of the learning roadmap",
    "topics": [
        {{
            "title": "Topic title",
            "description": "What this complete topic covers",
            "estimated_days": 3,
            "objectives": [
                "Learning objective 1",
                "Learning objective 2",
                "Learning objective 3"
            ]
        }}
    ]
}}
""".strip()


def validate_plan_duration(
    plan: LearningPlan,
    duration_days: int | None,
) -> None:
    """Ensure the generated roadmap fits within the requested duration."""
    if not duration_days:
        return

    total_days = sum(
        float(topic.estimated_days)
        for topic in plan.topics
    )

    if total_days > duration_days:
        raise ValueError(
            "The generated learning plan exceeds "
            f"the requested duration of {duration_days} days."
        )


def create_learning_plan(state: LearningState) -> dict:
    """Generate and validate a structured learning roadmap."""
    response = get_llm().invoke(
        build_planner_prompt(state)
    )

    data = parse_json_response(response)
    plan = LearningPlan.model_validate(data)

    if not plan.topics:
        raise ValueError(
            "The generated learning plan contains no topics."
        )

    validate_plan_duration(
        plan,
        state.get("duration_days"),
    )

    return {
        "plan": plan.model_dump(),
        "plan_approved": False,
    }