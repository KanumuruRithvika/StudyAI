from models.schemas import LearningRequest
from models.state import LearningState


def clean_list(values: list[str]) -> list[str]:
    """Remove empty values and case-insensitive duplicates while preserving order."""
    cleaned = []
    seen = set()

    for value in values:
        value = value.strip()

        if not value:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(value)

    return cleaned


def analyze_context(request: LearningRequest) -> dict:
    """Normalize the learning request into the shared LangGraph state."""
    goal = request.goal.strip() if request.goal else ""

    if request.learning_mode == "project" and not goal:
        goal = request.project_description.strip()

    state: LearningState = {
        "user_id": request.user_id,
        "learning_mode": request.learning_mode,
        "goal": goal,
        "current_level": (
            request.current_level.strip().lower()
            if request.current_level
            else ""
        ),
        "available_time_minutes": request.available_time_minutes,
        "duration_days": request.duration_days or 0,
        "role": request.role.strip() if request.role else "",
        "project_name": (
            request.project_name.strip()
            if request.project_name
            else ""
        ),
        "project_description": (
            request.project_description.strip()
            if request.project_description
            else ""
        ),
        "current_skills": clean_list(request.current_skills),
        "required_technologies": clean_list(
            request.required_technologies
        ),
        "learning_preferences": (
            request.learning_preferences.strip()
            if request.learning_preferences
            else ""
        ),
        "prior_experience": (
            request.prior_experience.strip()
            if request.prior_experience
            else ""
        ),
        "additional_instructions": (
            request.additional_instructions.strip()
            if request.additional_instructions
            else ""
        ),
    }

    return state