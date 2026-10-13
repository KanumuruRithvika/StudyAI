import uuid

from langgraph.types import Command

from database.connection import SessionLocal
from database.repository import (
    create_learning_session,
    save_task_attempt,
    save_quiz_attempt,
    update_session_progress,
)
from graph.workflow import build_graph
from models.database_models import LearningSession
from models.schemas import (
    LearningRequest,
    PlanApprovalRequest,
    DaySubmission,
    QuizSubmission,
    AdaptationRequest,
)


graph = build_graph()


def get_current_interrupt_type(state) -> str | None:
    if not state or not getattr(state, "tasks", None):
        return None

    for task in state.tasks:
        for interrupt in getattr(
            task,
            "interrupts",
            [],
        ):
            if isinstance(interrupt.value, dict):
                return interrupt.value.get("type")

    return None


def resolve_session_id(input_id: str) -> str:
    input_id = input_id.strip()

    state = graph.get_state({
        "configurable": {
            "thread_id": input_id,
        }
    })

    if getattr(state, "values", None):
        return input_id

    db = SessionLocal()

    try:
        sessions = (
            db.query(LearningSession)
            .order_by(
                LearningSession.created_at.desc()
            )
            .limit(50)
            .all()
        )

        for session in sessions:
            state = graph.get_state({
                "configurable": {
                    "thread_id": session.id,
                }
            })

            if state and state.tasks:
                for task in state.tasks:
                    for interrupt in task.interrupts:
                        if interrupt.id == input_id:
                            return session.id
    finally:
        db.close()

    return input_id


def get_session_state(session_id: str):
    """Return the raw LangGraph state for a session."""
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    return graph.get_state(config)


def validate_interrupt(
    session_id: str,
    expected_type: str,
):
    """
    Return the graph state for a session after verifying that
    the current interrupt type matches `expected_type`.

    Raises ValueError if the interrupt type does not match.
    """
    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    current_state = graph.get_state(config)

    if not getattr(current_state, "values", None):
        raise ValueError(
            f"Session '{session_id}' not found."
        )

    interrupt_type = get_current_interrupt_type(
        current_state
    )

    if interrupt_type and interrupt_type != expected_type:
        raise ValueError(
            f"Cannot proceed: session is currently "
            f"waiting for '{interrupt_type}'. "
            f"Expected '{expected_type}'."
        )

    return current_state


def update_progress(
    session_id: str,
    state: dict,
) -> None:
    topics = state.get(
        "plan",
        {},
    ).get(
        "topics",
        []
    )

    index = state.get(
        "current_topic_index",
        0,
    )

    progress = (
        round(
            (index / len(topics)) * 100,
            2,
        )
        if topics
        else 0.0
    )

    if state.get("goal_completed"):
        progress = 100.0

    db = SessionLocal()

    try:
        if state.get("goal_completed"):
            from database.repository import complete_session

            complete_session(
                db,
                session_id,
            )
        else:
            update_session_progress(
                db,
                session_id,
                state.get("current_topic"),
                progress,
            )
    finally:
        db.close()


def start_learning_session(
    request: LearningRequest,
) -> dict:
    session_id = str(uuid.uuid4())

    db = SessionLocal()

    try:
        create_learning_session(
            db,
            session_id,
            request.user_id,
            request.learning_mode,
            request.goal,
        )
    finally:
        db.close()

    state = request.model_dump()
    state["session_id"] = session_id

    result = graph.invoke(
        state,
        config={
            "configurable": {
                "thread_id": session_id,
            }
        },
    )

    return {
        "session_id": session_id,
        "state": result,
    }


def approve_plan(
    session_id: str,
    request: PlanApprovalRequest,
) -> dict:
    session_id = resolve_session_id(session_id)

    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    current_state = graph.get_state(config)

    if not getattr(
        current_state,
        "values",
        None,
    ):
        raise ValueError(
            f"Session '{session_id}' not found."
        )

    interrupt_type = get_current_interrupt_type(
        current_state
    )

    if (
        interrupt_type
        and interrupt_type != "plan_approval"
    ):
        if (
            isinstance(
                current_state.values,
                dict,
            )
            and current_state.values.get(
                "plan_approved"
            )
            and request.approved
        ):
            return {
                "session_id": session_id,
                "state": current_state.values,
            }

        raise ValueError(
            f"Cannot approve plan: session is currently "
            f"waiting for '{interrupt_type}'. "
            "Please proceed to that step."
        )

    result = graph.invoke(
        Command(
            resume={
                "approved": request.approved,
                "feedback": request.feedback or "",
            }
        ),
        config=config,
    )

    update_progress(
        session_id,
        result,
    )

    return {
        "session_id": session_id,
        "state": result,
    }


def submit_day(
    session_id: str,
    request: DaySubmission,
) -> dict:
    session_id = resolve_session_id(session_id)

    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    current_state = graph.get_state(config)

    if not getattr(
        current_state,
        "values",
        None,
    ):
        raise ValueError(
            f"Session '{session_id}' not found."
        )

    interrupt_type = get_current_interrupt_type(
        current_state
    )

    if (
        interrupt_type
        and interrupt_type != "day_submission"
    ):
        raise ValueError(
            f"Cannot submit day tasks: session is "
            f"currently waiting for '{interrupt_type}'. "
            "Please proceed to that step."
        )

    tasks = [
        {
            "task_id": task.task_id,
            "status": task.status,
            "notes": task.notes,
        }
        for task in request.tasks
    ]

    result = graph.invoke(
        Command(
            resume={
                "tasks": tasks,
            }
        ),
        config=config,
    )

    db = SessionLocal()

    try:
        for task in request.tasks:
            save_task_attempt(
                db,
                session_id,
                task.task_id,
                task.status == "done",
                task.notes,
            )
    finally:
        db.close()

    update_progress(
        session_id,
        result,
    )

    return {
        "session_id": session_id,
        "state": result,
    }


def complete_task(
    session_id: str,
    task_id: str,
    completed: bool = True,
) -> dict:
    session_id = resolve_session_id(session_id)

    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    current_state = graph.get_state(config)

    if not getattr(
        current_state,
        "values",
        None,
    ):
        raise ValueError(
            f"Session '{session_id}' not found."
        )

    interrupt_type = get_current_interrupt_type(
        current_state
    )

    if (
        interrupt_type
        and interrupt_type != "day_submission"
    ):
        raise ValueError(
            f"Cannot complete task: session is "
            f"currently waiting for '{interrupt_type}'. "
            "Current step is not task submission."
        )

    existing_tasks = current_state.values.get(
        "tasks",
        [],
    )

    completed_tasks = set(
        current_state.values.get(
            "completed_tasks",
            [],
        )
    )

    skipped_tasks = set(
        current_state.values.get(
            "skipped_tasks",
            [],
        )
    )

    all_task_updates = []
    found = False

    for task in existing_tasks:
        current_task_id = task.get("id")

        if current_task_id == task_id:
            found = True

            all_task_updates.append({
                "task_id": current_task_id,
                "status": (
                    "done"
                    if completed
                    else "not_done"
                ),
                "notes": None,
            })

        elif current_task_id in completed_tasks:
            all_task_updates.append({
                "task_id": current_task_id,
                "status": "done",
                "notes": None,
            })

        elif current_task_id in skipped_tasks:
            all_task_updates.append({
                "task_id": current_task_id,
                "status": "skip",
                "notes": None,
            })

        else:
            all_task_updates.append({
                "task_id": current_task_id,
                "status": "not_done",
                "notes": None,
            })

    if not found:
        raise ValueError(
            f"Task '{task_id}' not found."
        )

    result = graph.invoke(
        Command(
            resume={
                "tasks": all_task_updates,
            }
        ),
        config=config,
    )

    db = SessionLocal()

    try:
        save_task_attempt(
            db,
            session_id,
            task_id,
            completed,
            None,
        )
    finally:
        db.close()

    update_progress(
        session_id,
        result,
    )

    return {
        "session_id": session_id,
        "state": result,
    }


def submit_quiz(
    session_id: str,
    request: QuizSubmission,
) -> dict:
    session_id = resolve_session_id(session_id)

    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    current_state = graph.get_state(config)

    if not getattr(
        current_state,
        "values",
        None,
    ):
        raise ValueError(
            f"Session '{session_id}' not found."
        )

    interrupt_type = get_current_interrupt_type(
        current_state
    )

    if (
        interrupt_type
        and interrupt_type != "quiz_submission"
    ):
        raise ValueError(
            f"Cannot submit quiz: session is "
            f"currently waiting for '{interrupt_type}'. "
            "Please complete today's tasks or finish "
            "earlier steps first."
        )

    quiz_topic = current_state.values.get(
        "current_topic",
        "",
    )

    quiz_questions = current_state.values.get(
        "quiz",
        [],
    )

    answers = [
        {
            "question_id": answer.question_id,
            "answer": answer.answer,
        }
        for answer in request.answers
    ]

    result = graph.invoke(
        Command(
            resume={
                "answers": answers,
            }
        ),
        config=config,
    )

    # Preserve quiz questions in result for frontend display if topic transition occurred
    if not result.get("quiz") and quiz_questions:
        result["quiz"] = quiz_questions

    quiz_score = float(result.get("quiz_score", 0.0))
    total_q = len(quiz_questions) if quiz_questions else len(result.get("quiz", []))
    correct_answers = int(result.get("correct_answers", result.get("correct", round((quiz_score / 100) * total_q) if total_q else 0)))

    db = SessionLocal()

    try:
        save_quiz_attempt(
            db,
            session_id,
            quiz_topic,
            quiz_score,
            total_q,
        )
    finally:
        db.close()

    update_progress(
        session_id,
        result,
    )

    return {
        "session_id": session_id,
        "state": result,
        "quiz_score": quiz_score,
        "score": quiz_score,
        "correct_answers": correct_answers,
        "correct": correct_answers,
        "total_questions": total_q,
        "total": total_q,
        "weak_topics": result.get("weak_topics", []),
        "strong_topics": result.get("strong_topics", []),
        "medium_topics": result.get("medium_topics", []),
        "adaptive_action": result.get("adaptive_action", "move_forward"),
    }


def submit_adaptation(
    session_id: str,
    request: AdaptationRequest,
) -> dict:
    """Apply the user's adaptation decision: 'improve_weak_topics' or 'move_forward'."""
    session_id = resolve_session_id(session_id)

    config = {
        "configurable": {
            "thread_id": session_id,
        }
    }

    current_state = graph.get_state(config)

    if not getattr(current_state, "values", None):
        raise ValueError(
            f"Session '{session_id}' not found."
        )

    values = dict(current_state.values)
    action = request.action

    interrupt_type = get_current_interrupt_type(current_state)

    if interrupt_type == "adaptation_decision":
        resume_payload = {
            "action": action,
        }

        if request.available_time_minutes is not None:
            resume_payload[
                "available_time_minutes"
            ] = request.available_time_minutes

        if request.duration_days is not None:
            resume_payload[
                "duration_days"
            ] = request.duration_days

        if request.description is not None:
            resume_payload[
                "description"
            ] = request.description

        result = graph.invoke(
            Command(resume=resume_payload),
            config=config,
        )
    else:
        if action == "improve_weak_topics":
            from agents.adaptive import build_remediation_context
            from agents.task import generate_tasks

            remediation_info = build_remediation_context(values)
            if request.description:
                remediation_info["improvement_description"] = request.description
            if request.duration_days:
                remediation_info["improvement_days"] = request.duration_days
            if request.available_time_minutes:
                remediation_info["improvement_time_minutes"] = request.available_time_minutes

            remediation_state = {
                **values,
                **remediation_info,
                "adaptive_action": "improve_weak_topics",
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

            # Generate at most 3 remediation tasks targeting weak topics
            tasks_result = generate_tasks(remediation_state)
            remediation_tasks = tasks_result.get("tasks", [])[:3]

            update_payload = {
                **remediation_info,
                "adaptive_action": "improve_weak_topics",
                "current_day": 1,
                "topic_completed": False,
                "goal_completed": False,
                "tasks": remediation_tasks,
                "completed_tasks": [],
                "unfinished_tasks": [],
                "skipped_tasks": [],
                "carried_forward_tasks": [],
                "quiz": [],
                "quiz_answers": [],
                "adaptation_requested": False,
            }

            graph.update_state(config, update_payload)
            updated = graph.get_state(config)
            result = updated.values
        else:
            from graph.workflow import next_topic_node
            from agents.task import generate_tasks
            from agents.readiness import generate_readiness_report

            next_topic_update = next_topic_node(values)

            if next_topic_update.get("goal_completed"):
                completed_state = {
                    **values,
                    **next_topic_update,
                    "adaptive_action": "move_forward",
                }
                report_result = generate_readiness_report(completed_state)
                update_payload = {
                    **next_topic_update,
                    "adaptive_action": "move_forward",
                    **report_result,
                }
                graph.update_state(config, update_payload)
                updated = graph.get_state(config)
                result = updated.values
            else:
                new_topic_state = {
                    **values,
                    **next_topic_update,
                    "adaptive_action": "move_forward",
                }
                new_tasks_result = generate_tasks(new_topic_state)
                update_payload = {
                    **next_topic_update,
                    "adaptive_action": "move_forward",
                    **new_tasks_result,
                }
                graph.update_state(config, update_payload)
                updated = graph.get_state(config)
                result = updated.values

    update_progress(session_id, result)

    return {
        "session_id": session_id,
        "state": result,
    }
