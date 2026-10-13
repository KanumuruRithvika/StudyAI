from models.state import LearningState


def generate_readiness_report(state: LearningState) -> dict:
    """Generate the final learning/readiness report."""
    plan = state.get("plan", {})
    topics = plan.get("topics", [])
    topic_performance = state.get("topic_performance", {})

    strong_topics = state.get("strong_topics", [])
    medium_topics = state.get("medium_topics", [])
    weak_topics = state.get("weak_topics", [])

    completed_topics = len(topic_performance)
    total_topics = len(topics)

    progress = (
        round((completed_topics / total_topics) * 100, 2)
        if total_topics
        else 0.0
    )

    if state.get("goal_completed"):
        progress = 100.0

    skill_gaps = state.get("skill_gaps", [])
    recommendations = build_recommendations(
        state,
        weak_topics,
        medium_topics,
        skill_gaps,
    )

    if state.get("learning_mode") == "project":
        report = build_project_report(
            state,
            progress,
            strong_topics,
            medium_topics,
            weak_topics,
            skill_gaps,
            recommendations,
        )
    else:
        report = build_general_report(
            state,
            progress,
            strong_topics,
            medium_topics,
            weak_topics,
            recommendations,
        )

    return {
        "readiness_report": {
            "progress_percent": progress,
            "strong_topics": strong_topics,
            "medium_topics": medium_topics,
            "weak_topics": weak_topics,
            "skill_gaps": [
                gap["skill"]
                for gap in skill_gaps
                if isinstance(gap, dict) and gap.get("skill")
            ],
            "recommendations": recommendations,
            "report": report,
        }
    }


def build_recommendations(
    state: LearningState,
    weak_topics: list[str],
    medium_topics: list[str],
    skill_gaps: list[dict],
) -> list[str]:
    """Build actionable recommendations from learning performance."""
    recommendations = []

    if weak_topics:
        recommendations.append(
            "Review weak topics and complete additional practice."
        )

    if medium_topics:
        recommendations.append(
            "Strengthen medium-level topics with additional practice."
        )

    if state.get("learning_mode") == "project" and skill_gaps:
        recommendations.append(
            "Continue practicing the remaining project skill gaps."
        )

    if not recommendations:
        recommendations.append(
            "Apply the learned concepts through practical work."
        )

    return recommendations


def build_general_report(
    state: LearningState,
    progress: float,
    strong_topics: list[str],
    medium_topics: list[str],
    weak_topics: list[str],
    recommendations: list[str],
) -> str:
    """Build a final report for a general learning goal."""
    return (
        f"Learning goal: {state.get('goal', '')}. "
        f"Overall progress: {progress}%. "
        f"Strong topics: {', '.join(strong_topics) or 'None'}. "
        f"Medium topics: {', '.join(medium_topics) or 'None'}. "
        f"Weak topics: {', '.join(weak_topics) or 'None'}. "
        f"Recommendations: {'; '.join(recommendations)}."
    )


def build_project_report(
    state: LearningState,
    progress: float,
    strong_topics: list[str],
    medium_topics: list[str],
    weak_topics: list[str],
    skill_gaps: list[dict],
    recommendations: list[str],
) -> str:
    """Build a final report for a project-based learning goal."""
    remaining_gaps = [
        gap["skill"]
        for gap in skill_gaps
        if isinstance(gap, dict) and gap.get("skill")
    ]

    return (
        f"Project: {state.get('project_name', '')}. "
        f"Target role: {state.get('role', '')}. "
        f"Overall learning progress: {progress}%. "
        f"Strong topics: {', '.join(strong_topics) or 'None'}. "
        f"Medium topics: {', '.join(medium_topics) or 'None'}. "
        f"Weak topics: {', '.join(weak_topics) or 'None'}. "
        f"Remaining skill gaps: "
        f"{', '.join(remaining_gaps) or 'None'}. "
        f"Recommendations: {'; '.join(recommendations)}."
    )