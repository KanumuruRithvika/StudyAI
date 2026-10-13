from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from langgraph.types import Command

from models.schemas import (
    DaySubmission,
    LearningRequest,
    PlanApprovalRequest,
    QuizAnswer,
    QuizSubmission,
)
from services import orchestrator


def create_request():
    return LearningRequest(
        user_id="test-user",
        learning_mode="general",
        goal="Learn Python",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=1,
    )


def create_plan_state():
    return {
        "plan": {
            "title": "Python Learning Plan",
            "summary": "Learn Python basics.",
            "topics": [
                {
                    "title": "Python Basics",
                    "description": "Learn Python fundamentals.",
                    "estimated_days": 1,
                    "objectives": [
                        "Understand Python basics",
                    ],
                }
            ],
        },
        "plan_approved": False,
        "current_topic": "",
    }


def create_day_state():
    return {
        "plan": {
            "topics": [
                {
                    "title": "Python Basics",
                    "description": "Learn Python fundamentals.",
                    "estimated_days": 1,
                    "objectives": [
                        "Understand Python basics",
                    ],
                }
            ]
        },
        "plan_approved": True,
        "current_topic": "Python Basics",
        "current_day": 1,
        "tasks": [
            {
                "id": "task-1",
                "title": "Study Python basics",
                "description": "Study Python fundamentals.",
                "task_type": "study",
                "estimated_minutes": 30,
                "objective": "Understand Python basics",
            }
        ],
        "completed_tasks": [],
        "unfinished_tasks": ["task-1"],
        "skipped_tasks": [],
    }


def create_quiz_state():
    return {
        "plan": {
            "topics": [
                {
                    "title": "Python Basics",
                    "description": "Learn Python fundamentals.",
                    "estimated_days": 1,
                    "objectives": [
                        "Understand Python basics",
                    ],
                }
            ]
        },
        "plan_approved": True,
        "current_topic": "Python Basics",
        "current_day": 1,
        "quiz": [
            {
                "id": f"q{i}",
                "question": f"Question {i}",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "A is correct.",
            }
            for i in range(1, 6)
        ],
    }


def interrupt_state(interrupt_type, values):
    interrupt = SimpleNamespace(
        value={
            "type": interrupt_type,
        }
    )

    task = SimpleNamespace(
        interrupts=[interrupt],
    )

    return SimpleNamespace(
        values=values,
        tasks=[task],
    )


def test_start_learning_session_creates_session():
    fake_graph = MagicMock()

    fake_graph.invoke.return_value = {
        "plan": create_plan_state()["plan"],
    }

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ), patch.object(
        orchestrator,
        "create_learning_session",
    ) as create_session, patch.object(
        orchestrator,
        "update_progress",
    ):

        result = orchestrator.start_learning_session(
            create_request()
        )

    assert result["session_id"]
    assert result["state"]

    create_session.assert_called_once()
    fake_graph.invoke.assert_called_once()

    call_args = fake_graph.invoke.call_args

    assert (
        call_args.kwargs["config"]["configurable"]["thread_id"]
        == result["session_id"]
    )


def test_approve_plan_resumes_plan_approval():
    fake_graph = MagicMock()

    fake_graph.get_state.return_value = interrupt_state(
        "plan_approval",
        create_plan_state(),
    )

    fake_graph.invoke.return_value = {
        **create_plan_state(),
        "plan_approved": True,
    }

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ), patch.object(
        orchestrator,
        "update_progress",
    ):

        result = orchestrator.approve_plan(
            "session-1",
            PlanApprovalRequest(
                approved=True,
                feedback="",
            ),
        )

    assert result["session_id"] == "session-1"
    assert result["state"]["plan_approved"] is True

    fake_graph.invoke.assert_called_once()

    command = fake_graph.invoke.call_args.args[0]

    assert isinstance(command, Command)
    assert command.resume == {
        "approved": True,
        "feedback": "",
    }


def test_rejecting_plan_resumes_with_feedback():
    fake_graph = MagicMock()

    fake_graph.get_state.return_value = interrupt_state(
        "plan_approval",
        create_plan_state(),
    )

    fake_graph.invoke.return_value = {
        **create_plan_state(),
        "plan_approved": False,
        "plan_feedback": "Add practical work.",
    }

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ), patch.object(
        orchestrator,
        "update_progress",
    ):

        result = orchestrator.approve_plan(
            "session-1",
            PlanApprovalRequest(
                approved=False,
                feedback="Add practical work.",
            ),
        )

    assert result["state"]["plan_approved"] is False
    assert (
        result["state"]["plan_feedback"]
        == "Add practical work."
    )

    command = fake_graph.invoke.call_args.args[0]

    assert command.resume == {
        "approved": False,
        "feedback": "Add practical work.",
    }


def test_submit_day_resumes_day_submission():
    fake_graph = MagicMock()

    fake_graph.get_state.return_value = interrupt_state(
        "day_submission",
        create_day_state(),
    )

    fake_graph.invoke.return_value = {
        **create_day_state(),
        "completed_tasks": ["task-1"],
        "unfinished_tasks": [],
    }

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ), patch.object(
        orchestrator,
        "save_task_attempt",
    ), patch.object(
        orchestrator,
        "update_progress",
    ):

        result = orchestrator.submit_day(
            "session-1",
            DaySubmission(
                tasks=[
                    {
                        "task_id": "task-1",
                        "status": "done",
                        "notes": "Completed.",
                    }
                ]
            ),
        )

    assert result["session_id"] == "session-1"
    assert result["state"]["completed_tasks"] == ["task-1"]

    command = fake_graph.invoke.call_args.args[0]

    assert isinstance(command, Command)
    assert command.resume == {
        "tasks": [
            {
                "task_id": "task-1",
                "status": "done",
                "notes": "Completed.",
            }
        ]
    }


def test_submit_quiz_resumes_quiz_submission():
    fake_graph = MagicMock()

    fake_graph.get_state.return_value = interrupt_state(
        "quiz_submission",
        create_quiz_state(),
    )

    fake_graph.invoke.return_value = {
        **create_quiz_state(),
        "quiz_score": 100.0,
        "goal_completed": True,
    }

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ), patch.object(
        orchestrator,
        "save_quiz_attempt",
    ), patch.object(
        orchestrator,
        "update_progress",
    ):

        result = orchestrator.submit_quiz(
            "session-1",
            QuizSubmission(
                answers=[
                    QuizAnswer(
                        question_id=f"q{i}",
                        answer="A",
                    )
                    for i in range(1, 6)
                ]
            ),
        )

    assert result["session_id"] == "session-1"
    assert result["state"]["quiz_score"] == 100.0
    assert result["state"]["goal_completed"] is True

    command = fake_graph.invoke.call_args.args[0]

    assert isinstance(command, Command)
    assert command.resume == {
        "answers": [
            {
                "question_id": f"q{i}",
                "answer": "A",
            }
            for i in range(1, 6)
        ]
    }


def test_approve_plan_rejects_wrong_interrupt():
    fake_graph = MagicMock()

    state = create_day_state()
    state["plan_approved"] = False

    fake_graph.get_state.return_value = interrupt_state(
        "day_submission",
        state,
    )

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ):
        with pytest.raises(
            ValueError,
            match="currently waiting for 'day_submission'",
        ):
            orchestrator.approve_plan(
                "session-1",
                PlanApprovalRequest(
                    approved=True,
                    feedback="",
                ),
            )


def test_submit_day_rejects_wrong_interrupt():
    fake_graph = MagicMock()

    fake_graph.get_state.return_value = interrupt_state(
        "quiz_submission",
        create_quiz_state(),
    )

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ):
        with pytest.raises(
            ValueError,
            match="currently waiting for 'quiz_submission'",
        ):
            orchestrator.submit_day(
                "session-1",
                DaySubmission(
                    tasks=[
                        {
                            "task_id": "task-1",
                            "status": "done",
                            "notes": None,
                        }
                    ]
                ),
            )


def test_submit_quiz_rejects_wrong_interrupt():
    fake_graph = MagicMock()

    fake_graph.get_state.return_value = interrupt_state(
        "day_submission",
        create_day_state(),
    )

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ):
        with pytest.raises(
            ValueError,
            match="currently waiting for 'day_submission'",
        ):
            orchestrator.submit_quiz(
                "session-1",
                QuizSubmission(
                    answers=[
                        QuizAnswer(
                            question_id="q1",
                            answer="A",
                        )
                    ]
                ),
            )


def test_resolve_session_id_returns_existing_id():
    fake_graph = MagicMock()

    fake_state = MagicMock()
    fake_state.values = {
        "current_topic": "Python Basics",
    }

    fake_graph.get_state.return_value = fake_state

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ):
        result = orchestrator.resolve_session_id(
            "session-1"
        )

    assert result == "session-1"


def test_get_session_state_returns_graph_state():
    fake_graph = MagicMock()

    fake_state = MagicMock()
    fake_state.values = {
        "current_topic": "Python Basics",
        "current_day": 1,
    }

    fake_graph.get_state.return_value = fake_state

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ):
        result = orchestrator.get_session_state(
            "session-1"
        )

    assert result is fake_state
    fake_graph.get_state.assert_called_once()


def test_validate_interrupt_accepts_expected_interrupt():
    fake_graph = MagicMock()

    fake_graph.get_state.return_value = interrupt_state(
        "plan_approval",
        create_plan_state(),
    )

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ):
        state = orchestrator.validate_interrupt(
            "session-1",
            "plan_approval",
        )

    assert state.values == create_plan_state()


def test_validate_interrupt_rejects_wrong_interrupt():
    fake_graph = MagicMock()

    fake_graph.get_state.return_value = interrupt_state(
        "quiz_submission",
        create_quiz_state(),
    )

    with patch.object(
        orchestrator,
        "graph",
        fake_graph,
    ):
        with pytest.raises(
            ValueError,
            match="currently waiting for 'quiz_submission'",
        ):
            orchestrator.validate_interrupt(
                "session-1",
                "plan_approval",
            )