import traceback

from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies import get_current_user
from models.schemas import (
    LearningRequest,
    PlanApprovalRequest,
    TaskCompletionRequest,
    DaySubmission,
    QuizSubmission,
    AdaptationRequest,
)
from services.orchestrator import (
    approve_plan,
    complete_task,
    start_learning_session,
    submit_day,
    submit_quiz,
    submit_adaptation,
    resolve_session_id,
    get_session_state,
)
from services.performance import build_performance
from database.connection import SessionLocal
from database.repository import (
    get_learning_session,
    get_task_attempts,
    get_quiz_attempts,
)


router = APIRouter(
    prefix="/learning",
    tags=["learning"],
)


def build_quiz_response(quiz: list[dict]) -> dict:
    return {
        "questions": [
            {
                "id": question["id"],
                "question": question["question"],
                "options": question["options"],
            }
            for question in quiz
        ]
    }


def handle_value_error(exc: ValueError):
    detail = str(exc)

    status_code = (
        404
        if "not found" in detail.lower()
        else 400
    )

    raise HTTPException(
        status_code=status_code,
        detail=detail,
    )


@router.post("/start")
def start_learning(
    request: LearningRequest,
    current_user=Depends(get_current_user),
):
    try:
        # Override the client-supplied user_id with the
        # authenticated user's ID.
        request.user_id = current_user.id
        return start_learning_session(request)

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/{session_id}/approve")
def approve_learning_plan(
    session_id: str,
    request: PlanApprovalRequest,
):
    try:
        return approve_plan(
            session_id,
            request,
        )

    except ValueError as exc:
        handle_value_error(exc)

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/{session_id}/tasks/complete")
def complete_learning_task(
    session_id: str,
    request: TaskCompletionRequest,
):
    try:
        return complete_task(
            session_id,
            request.task_id,
            request.completed,
        )

    except ValueError as exc:
        handle_value_error(exc)

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/{session_id}/day/submit")
def submit_learning_day(
    session_id: str,
    request: DaySubmission,
):
    try:
        return submit_day(
            session_id,
            request,
        )

    except ValueError as exc:
        handle_value_error(exc)

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.post("/{session_id}/quiz/submit")
def submit_learning_quiz(
    session_id: str,
    request: QuizSubmission,
):
    try:
        return submit_quiz(
            session_id,
            request,
        )

    except ValueError as exc:
        handle_value_error(exc)

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{session_id}/progress")
def get_learning_progress(session_id: str):
    session_id = resolve_session_id(
        session_id
    )

    db = SessionLocal()

    try:
        session = get_learning_session(
            db,
            session_id,
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Learning session "
                    f"'{session_id}' not found"
                ),
            )

        task_attempts = get_task_attempts(
            db,
            session_id,
        )

        quiz_attempts = get_quiz_attempts(
            db,
            session_id,
        )

        completed_tasks = sum(
            attempt.completed
            for attempt in task_attempts
        )

        state_values = {}
        try:
            graph_state = get_session_state(session_id)
            if getattr(graph_state, "values", None):
                state_values = graph_state.values
        except Exception:
            pass

        return {
            "session_id": session.id,
            "status": session.status,
            "current_topic": session.current_topic or state_values.get("current_topic", ""),
            "current_day": state_values.get("current_day", 1),
            "progress_percent": session.progress_percent,
            "tasks": state_values.get("tasks", []),
            "current_tasks": state_values.get("tasks", []),
            "plan": state_values.get("plan"),
            "state": state_values,
            "quiz": state_values.get("quiz", []),
            "completed_tasks": completed_tasks,
            "total_task_attempts": len(
                task_attempts
            ),
            "quiz_attempts": [
                {
                    "topic": attempt.topic,
                    "score": attempt.score,
                    "total_questions": (
                        attempt.total_questions
                    ),
                }
                for attempt in quiz_attempts
            ],
        }

    finally:
        db.close()


@router.get("/{session_id}/performance")
def get_performance_endpoint(session_id: str):
    session_id = resolve_session_id(session_id)
    state = get_session_state(session_id)
    if not getattr(state, "values", None):
        raise HTTPException(
            status_code=404,
            detail=f"Learning session '{session_id}' not found.",
        )
    return build_performance(session_id, state.values)


@router.post("/{session_id}/adapt")
def submit_learning_adaptation(
    session_id: str,
    request: AdaptationRequest,
):
    try:
        return submit_adaptation(
            session_id,
            request,
        )

    except ValueError as exc:
        handle_value_error(exc)

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{session_id}/tasks/{task_id}/detail")
def get_task_detail(session_id: str, task_id: str):
    """Generate a structured completion guide for a specific task."""
    try:
        session_id = resolve_session_id(session_id)
        state = get_session_state(session_id)

        if not getattr(state, "values", None):
            raise HTTPException(
                status_code=404,
                detail=f"Session '{session_id}' not found.",
            )

        values = state.values
        tasks = values.get("tasks", [])
        task = next((t for t in tasks if t.get("id") == task_id), None)

        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task '{task_id}' not found in current session.",
            )

        from agents.task_detail import generate_task_detail
        detail = generate_task_detail(task, values)
        return detail

    except HTTPException:
        raise

    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc))
