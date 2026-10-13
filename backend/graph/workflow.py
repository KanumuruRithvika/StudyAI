import sqlite3
from datetime import datetime, timezone

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from agents.adaptation import adapt_learning
from agents.context_analyzer import analyze_context
from agents.evaluator import evaluate_quiz
from agents.planner import create_learning_plan
from agents.quiz import generate_quiz
from agents.readiness import generate_readiness_report
from agents.skill_gap import analyze_skill_gaps
from agents.task import generate_tasks
from models.schemas import LearningRequest
from models.state import LearningState
from services.memory import complete_day, prepare_next_day


def _now() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _reset_topic_state(index: int, topic: str) -> dict:
    """Reset topic-specific state when entering a topic."""
    return {
        "current_topic_index": index,
        "current_topic": topic,
        "current_day": 1,
        "day_started_at": _now(),
        "completed_tasks": [],
        "unfinished_tasks": [],
        "skipped_tasks": [],
        "carried_forward_tasks": [],
        "tasks": [],
        "task_details": {},
        "learning_content": {},
        "quiz": [],
        "quiz_answers": [],
        "topic_completed": False,
        "adaptation_requested": False,
        "adaptive_action": "move_forward",
        "adaptive_recommendation": "",
        "improvement_days": 0,
        "improvement_time_minutes": 0,
        "improvement_description": "",
    }


def context_node(state: LearningState) -> dict:
    """Convert graph state into a normalized learning request."""
    user_id = state.get("user_id")

    if not user_id:
        raise ValueError("Missing 'user_id' in workflow state.")

    request = LearningRequest(
        user_id=user_id,
        learning_mode=state["learning_mode"],
        goal=state.get("goal"),
        current_level=state.get("current_level"),
        available_time_minutes=state["available_time_minutes"],
        duration_days=state.get("duration_days"),
        role=state.get("role"),
        project_name=state.get("project_name"),
        project_description=state.get("project_description"),
        current_skills=state.get("current_skills", []),
        required_technologies=state.get("required_technologies", []),
        learning_preferences=state.get("learning_preferences"),
        prior_experience=state.get("prior_experience"),
        additional_instructions=state.get("additional_instructions"),
    )

    return analyze_context(request)


def planner_node(state: LearningState) -> dict:
    """Generate the structured learning roadmap."""
    return create_learning_plan(state)


def approval_node(state: LearningState) -> dict:
    """Pause the workflow until the learner reviews the roadmap."""
    response = interrupt({
        "type": "plan_approval",
        "message": "Review the learning plan and approve or request changes.",
        "plan": state["plan"],
    })

    if not isinstance(response, dict):
        raise ValueError("Expected plan approval response.")

    feedback = response.get("feedback", "")
    if not isinstance(feedback, str):
        feedback = ""

    return {
        "plan_approved": bool(response.get("approved")),
        "plan_feedback": feedback.strip(),
    }


def approval_router(state: LearningState) -> str:
    """Route the workflow after plan approval."""
    return "approved" if state.get("plan_approved") else "modify"


def topic_node(state: LearningState) -> dict:
    """Load the current topic from the approved roadmap."""
    topics = state.get("plan", {}).get("topics", [])
    index = state.get("current_topic_index", 0)

    if index >= len(topics):
        return {"goal_completed": True, "topic_completed": True}

    topic = topics[index]
    title = (
        topic.get("title", f"Topic {index + 1}")
        if isinstance(topic, dict)
        else str(topic)
    )

    return _reset_topic_state(index, title)


def topic_entry_router(state: LearningState) -> str:
    """Route completed roadmaps to the readiness report."""
    return "complete" if state.get("goal_completed") else "tasks"


def task_node(state: LearningState) -> dict:
    """Generate tasks for the current topic and day."""
    return generate_tasks(state)


def day_submission_node(state: LearningState) -> dict:
    """Pause until the learner submits today's task statuses."""
    response = interrupt({
        "type": "day_submission",
        "message": "Submit the status of every task for today.",
        "tasks": state.get("tasks", []),
        "current_day": state.get("current_day", 1),
        "current_topic": state.get("current_topic", ""),
        "revision_mode": state.get("adaptive_action") == "improve_weak_topics",
    })

    if not isinstance(response, dict) or "tasks" not in response:
        raise ValueError("Expected task statuses for the day.")

    return complete_day(state, response["tasks"])


def next_day_node(state: LearningState) -> dict:
    """Move to the next study day or finish the current topic."""
    topics = state.get("plan", {}).get("topics", [])
    index = state.get("current_topic_index", 0)

    if index >= len(topics):
        return {"topic_completed": True}

    if state.get("adaptive_action") == "improve_weak_topics":
        return {
            "topic_completed": True,
            "tasks": [],
            "completed_tasks": [],
            "unfinished_tasks": [],
            "skipped_tasks": [],
            "carried_forward_tasks": [],
        }

    topic = topics[index]
    estimated_days = max(1, int(topic.get("estimated_days", 1)))
    current_day = state.get("current_day", 1)
    unfinished_tasks = state.get("unfinished_tasks", [])

    if current_day >= estimated_days and not unfinished_tasks:
        return {"topic_completed": True}

    next_state = prepare_next_day(state)

    return {
        **next_state,
        "topic_completed": False,
        "day_started_at": _now(),
    }


def next_day_router(state: LearningState) -> str:
    """Route to another task day or to the topic quiz."""
    return "quiz" if state.get("topic_completed") else "tasks"


def quiz_node(state: LearningState) -> dict:
    """Generate a quiz after completing the topic."""
    return generate_quiz(state)


def quiz_answer_node(state: LearningState) -> dict:
    """Pause until the learner submits quiz answers."""
    quiz = [
        {
            "id": question["id"],
            "question": question["question"],
            "options": question["options"],
        }
        for question in state.get("quiz", [])
    ]

    response = interrupt({
        "type": "quiz_submission",
        "message": "Submit your answers for the quiz.",
        "quiz": quiz,
    })

    if not isinstance(response, dict) or "answers" not in response:
        raise ValueError("Expected quiz answers.")

    return {"quiz_answers": response["answers"]}


def adaptation_node(state: LearningState) -> dict:
    """
    Evaluate quiz performance and set the adaptive action.
    """
    from agents.adaptive import (
        adapt_learning as _adapt_full,
    )

    return _adapt_full(state)


def adaptation_decision_node(state: LearningState) -> dict:
    """
    Ask the learner to confirm the next learning action.
    """
    score = float(state.get("quiz_score", 0))

    if score < 60:
        required_action = "improve_weak_topics"
        message = (
            "Your score is below 60%. Additional practice is "
            "recommended before moving to the next topic."
        )
        options = [
            {
                "action": "improve_weak_topics",
                "label": "Start remediation",
            }
        ]
    else:
        required_action = "move_forward"

        if score < 80:
            message = (
                "Your score is in the medium range. You can "
                "continue to the next topic. The medium-performance "
                "areas will be kept in your learning history."
            )
        else:
            message = (
                "Your score is strong. "
                "You can continue to the next topic."
            )

        options = [
            {
                "action": "move_forward",
                "label": "Continue to next topic",
            }
        ]

    response = interrupt({
        "type": "adaptation_decision",
        "message": message,
        "score": score,
        "strong_topics": state.get("strong_topics", []),
        "medium_topics": state.get("medium_topics", []),
        "weak_topics": state.get("weak_topics", []),
        "improvement_guidance": state.get("improvement_description", ""),
        "required_action": required_action,
        "options": options,
    })

    if not isinstance(response, dict):
        raise ValueError("Expected adaptation decision.")

    action = response.get("action")

    if action not in ("improve_weak_topics", "move_forward"):
        raise ValueError(
            f"Invalid adaptation action: {action}. Expected 'improve_weak_topics' or 'move_forward'."
        )

    return {
        "adaptive_action": action,
        "adaptation_requested": True,
    }


def adaptation_router(state: LearningState) -> str:
    """Route weak performance to remediation, others forward."""
    return (
        "improve"
        if state.get("adaptive_action") == "improve_weak_topics"
        else "forward"
    )


def improvement_node(state: LearningState) -> dict:
    """Reset task execution for weak-topic remediation."""
    return {
        "current_day": 1,
        "topic_completed": False,
        "goal_completed": False,
        "tasks": [],
        "completed_tasks": [],
        "unfinished_tasks": [],
        "skipped_tasks": [],
        "carried_forward_tasks": [],
        "quiz": [],
        "quiz_answers": [],
        "adaptation_requested": False,
    }


def next_topic_node(state: LearningState) -> dict:
    """Move to the next topic in the approved roadmap."""
    topics = state.get("plan", {}).get("topics", [])
    next_index = state.get("current_topic_index", 0) + 1

    if next_index >= len(topics):
        return {"goal_completed": True, "topic_completed": True}

    topic = topics[next_index]
    title = (
        topic.get("title", f"Topic {next_index + 1}")
        if isinstance(topic, dict)
        else str(topic)
    )

    return _reset_topic_state(next_index, title)


def goal_router(state: LearningState) -> str:
    """Route completed learning goals to the readiness report."""
    return "complete" if state.get("goal_completed") else "continue"


def build_graph():
    """Build and compile the complete learning workflow."""
    graph = StateGraph(LearningState)

    graph.add_node("context", context_node)
    graph.add_node("skill_gap", analyze_skill_gaps)
    graph.add_node("planner", planner_node)
    graph.add_node("approval", approval_node)
    graph.add_node("topic", topic_node)
    graph.add_node("tasks", task_node)
    graph.add_node("day_submission", day_submission_node)
    graph.add_node("next_day", next_day_node)
    graph.add_node("quiz", quiz_node)
    graph.add_node("quiz_answer", quiz_answer_node)
    graph.add_node("evaluator", evaluate_quiz)
    graph.add_node("adaptation", adaptation_node)
    graph.add_node("improvement", improvement_node)
    graph.add_node("next_topic", next_topic_node)
    graph.add_node("readiness", generate_readiness_report)

    graph.add_edge(START, "context")
    graph.add_edge("context", "skill_gap")
    graph.add_edge("skill_gap", "planner")
    graph.add_edge("planner", "approval")

    graph.add_conditional_edges(
        "approval",
        approval_router,
        {"approved": "topic", "modify": "planner"},
    )

    graph.add_conditional_edges(
        "topic",
        topic_entry_router,
        {"tasks": "tasks", "complete": "readiness"},
    )

    graph.add_edge("tasks", "day_submission")
    graph.add_edge("day_submission", "next_day")

    graph.add_conditional_edges(
        "next_day",
        next_day_router,
        {"tasks": "tasks", "quiz": "quiz"},
    )

    graph.add_edge("quiz", "quiz_answer")
    graph.add_edge("quiz_answer", "evaluator")
    graph.add_edge("evaluator", "adaptation")

    # Automatically route after adaptation — no interrupt needed.
    # Weak score → improvement (remediation tasks).
    # Strong/medium score → next topic.
    graph.add_conditional_edges(
        "adaptation",
        adaptation_router,
        {"improve": "improvement", "forward": "next_topic"},
    )

    graph.add_edge("improvement", "tasks")

    graph.add_conditional_edges(
        "next_topic",
        goal_router,
        {"continue": "tasks", "complete": "readiness"},
    )

    graph.add_edge("readiness", END)

    connection = sqlite3.connect(
        "learning_checkpoints.db",
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(connection)

    return graph.compile(checkpointer=checkpointer)
