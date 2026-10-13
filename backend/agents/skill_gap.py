from models.state import LearningState


FOUNDATIONAL_SKILLS = {
    "spring boot",
    "python",
    "java",
    "javascript",
    "sql",
    "postgresql",
    "mysql",
}


def normalize_skill(skill: str) -> str:
    """Normalize a skill name for reliable comparison."""
    return " ".join(skill.lower().split())


def normalize_skills(skills: list[str]) -> list[str]:
    """Remove empty skills and case-insensitive duplicates."""
    cleaned = []
    seen = set()

    for skill in skills:
        skill = skill.strip()

        if not skill:
            continue

        normalized = normalize_skill(skill)

        if normalized in seen:
            continue

        seen.add(normalized)
        cleaned.append(skill)

    return cleaned


def get_priority(skill: str) -> str:
    """Assign a priority based on whether the skill is foundational."""
    normalized_skill = normalize_skill(skill)

    if normalized_skill in FOUNDATIONAL_SKILLS:
        return "high"

    return "medium"


def priority_order(priority: str) -> int:
    """Return the sorting order used for skill-gap prioritization."""
    return {
        "high": 1,
        "medium": 2,
        "low": 3,
    }.get(priority, 2)


def analyze_skill_gaps(state: LearningState) -> dict:
    """
    Identify missing project skills by comparing required skills
    and technologies against the user's current skills.
    """
    if state.get("learning_mode", "general") == "general":
        return {"skill_gaps": []}

    current = normalize_skills(
        state.get("current_skills", [])
    )

    required = normalize_skills(
        state.get("required_technologies", [])
    )

    current_lookup = {
        normalize_skill(skill)
        for skill in current
    }

    gaps = []

    for skill in required:
        normalized_skill = normalize_skill(skill)

        if normalized_skill in current_lookup:
            continue

        gaps.append({
            "skill": skill,
            "priority": get_priority(skill),
            "status": "missing",
        })

    gaps.sort(
        key=lambda gap: priority_order(gap["priority"])
    )

    return {"skill_gaps": gaps}