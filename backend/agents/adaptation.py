from models.state import LearningState


def adapt_learning(state: LearningState) -> dict:
    """Decide whether the learner needs remediation or can move forward."""
    score = float(state.get("quiz_score", 0))
    topic = state.get("current_topic", "the current topic")

    if score < 60:
        action = "improve_weak_topics"
        recommendation = (
            f"{topic} needs additional practice before moving forward. "
            "Focus on the identified weak areas."
        )
    else:
        action = "move_forward"

        if score < 80:
            recommendation = (
                f"{topic} is sufficiently understood to continue. "
                "Keep the medium-performance areas in mind for future review."
            )
        else:
            recommendation = (
                f"{topic} is sufficiently understood. "
                "You can continue to the next topic."
            )

    return {
        "adaptive_action": action,
        "adaptive_recommendation": recommendation,
    }