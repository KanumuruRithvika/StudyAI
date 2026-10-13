from models.schemas import (
    LearningActivity,
    PerformanceResponse,
    QuizPerformance,
    TopicPerformance,
)
from models.state import LearningState


def calculate_overall_progress(state: LearningState) -> float:
    """Calculate overall learning progress from the roadmap position."""
    if state.get("goal_completed"):
        return 100.0

    plan = state.get("plan", {})
    topics = plan.get("topics", [])

    if not topics:
        return 0.0

    current_index = state.get(
        "current_topic_index",
        0,
    )

    progress = (current_index / len(topics)) * 100

    return round(
        min(progress, 100.0),
        2,
    )


def calculate_quiz_accuracy(
    quiz_history: list[dict],
) -> float:
    """Calculate average quiz accuracy across completed quizzes."""
    if not quiz_history:
        return 0.0

    total_correct = sum(
        item.get("correct", 0)
        for item in quiz_history
    )

    total_questions = sum(
        item.get("total", 0)
        for item in quiz_history
    )

    if total_questions == 0:
        return 0.0

    return round(
        (total_correct / total_questions) * 100,
        2,
    )


def build_topic_performance(
    topic_performance: dict,
) -> list[TopicPerformance]:
    """Convert internal topic performance into API response models."""
    performance = []

    for topic, result in topic_performance.items():
        score = float(result.get("score", 0))
        status = result.get("performance", "weak")

        if status not in {
            "weak",
            "medium",
            "strong",
        }:
            status = "weak"

        performance.append(
            TopicPerformance(
                topic=topic,
                score=score,
                status=status,
            )
        )

    return performance


def build_quiz_history(
    quiz_history: list[dict],
) -> list[QuizPerformance]:
    """Convert stored quiz history into response models."""
    result = []
    for item in quiz_history:
        total = int(item.get("total", 0))
        score = float(item.get("score", 0))
        # correct_answers stored directly, or computed from score % and total
        correct = int(
            item.get("correct_answers",
                item.get("correct",
                    round((score / 100.0) * total) if total else 0
                )
            )
        )
        result.append(
            QuizPerformance(
                topic=item.get("topic", "Unknown topic"),
                score=score,
                total_questions=total,
                correct_answers=correct,
            )
        )
    return result


def build_recent_activity(
    state: LearningState,
) -> list[LearningActivity]:
    """Build recent learning activity from the available state history."""
    activities = []

    for item in state.get(
        "learning_history",
        [],
    )[-10:]:
        topic = item.get(
            "topic",
            "Unknown topic",
        )

        score = item.get(
            "score",
            0,
        )

        activities.append(
            LearningActivity(
                activity_type="quiz",
                description=(
                    f"Completed quiz for {topic} "
                    f"with a score of {score}%."
                ),
                timestamp=item.get(
                    "timestamp",
                    "",
                ),
            )
        )

    return activities


def build_performance(
    session_id: str,
    state: LearningState,
) -> PerformanceResponse:
    """
    Build the complete performance response for a learning session.

    The service aggregates task progress, quiz performance,
    topic performance, learning history, and adaptive results.
    """
    quiz_history = list(
        state.get(
            "quiz_history",
            [],
        )
    )

    topic_performance = dict(
        state.get(
            "topic_performance",
            {},
        )
    )

    completed_tasks = len(
        state.get(
            "completed_tasks",
            [],
        )
    )

    skipped_tasks = len(
        state.get(
            "skipped_tasks",
            [],
        )
    )

    current_tasks = state.get(
        "tasks",
        [],
    )

    carried_forward_tasks = state.get(
        "carried_forward_tasks",
        [],
    )

    tasks_total = (
        completed_tasks
        + skipped_tasks
        + len(carried_forward_tasks)
    )

    if not tasks_total:
        tasks_total = len(current_tasks)

    return PerformanceResponse(
        session_id=session_id,
        overall_progress=calculate_overall_progress(state),
        tasks_completed=completed_tasks,
        tasks_total=tasks_total,
        tasks_skipped=skipped_tasks,
        quiz_accuracy=calculate_quiz_accuracy(
            quiz_history
        ),
        quizzes_completed=len(quiz_history),
        study_time_minutes=int(
            state.get(
                "study_time_minutes",
                0,
            )
        ),
        current_streak=int(
            state.get(
                "current_streak",
                0,
            )
        ),
        topic_performance=build_topic_performance(
            topic_performance
        ),
        quiz_history=build_quiz_history(
            quiz_history
        ),
        strong_topics=list(
            state.get(
                "strong_topics",
                [],
            )
        ),
        medium_topics=list(
            state.get(
                "medium_topics",
                [],
            )
        ),
        weak_topics=list(
            state.get(
                "weak_topics",
                [],
            )
        ),
        recent_activity=build_recent_activity(
            state
        ),
    )