from models.state import LearningState


def build_remediation_context(state: LearningState) -> dict:
    """
    Prepare focused remediation information for weak topics.

    Remediation is created only when the learner's performance
    is classified as weak by the adaptation policy.
    """
    topic = state.get("current_topic", "the current topic")
    weak_topics = list(state.get("weak_topics", []))
    improvement_description = state.get(
        "improvement_description",
        "",
    )

    if not weak_topics:
        weak_topics = [topic]

    return {
        "weak_topics": weak_topics,
        "improvement_description": improvement_description,
        "improvement_days": 1,
        "improvement_time_minutes": state.get(
            "available_time_minutes",
            60,
        ),
    }


def adapt_learning(state: LearningState) -> dict:
    """
    Prepare the adaptive-learning state after quiz evaluation.

    Weak performance receives remediation context. Medium and strong
    performance are allowed to continue to the next topic.
    """
    score = float(state.get("quiz_score", 0))

    if score < 60:
        remediation = build_remediation_context(state)

        return {
            "adaptive_action": "improve_weak_topics",
            "adaptive_recommendation": (
                "The learner needs additional practice. "
                "Generate focused remediation tasks for the identified "
                "weak topics before continuing."
            ),
            **remediation,
        }

    topic = state.get("current_topic", "the current topic")

    if score < 80:
        recommendation = (
            f"{topic} is sufficiently understood to continue. "
            "The medium-performance areas should remain available "
            "for progress tracking and future review."
        )
    else:
        recommendation = (
            f"{topic} is sufficiently understood. "
            "Continue to the next topic."
        )

    return {
        "adaptive_action": "move_forward",
        "adaptive_recommendation": recommendation,
    }