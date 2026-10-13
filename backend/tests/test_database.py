import uuid

from database.connection import SessionLocal
from database.repository import (
    complete_session,
    create_learning_session,
    get_learning_session,
    get_quiz_attempts,
    get_task_attempts,
    save_quiz_attempt,
    save_task_attempt,
    update_session_progress,
)


def create_test_session_id() -> str:
    return f"test-{uuid.uuid4()}"


def test_create_and_get_learning_session():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-1",
            "general",
            "Learn Python",
        )

        session = get_learning_session(
            db,
            test_session_id,
        )

        assert session is not None
        assert session.id == test_session_id
        assert session.user_id == "user-1"
        assert session.learning_mode == "general"
        assert session.goal == "Learn Python"

    finally:
        db.close()


def test_update_session_progress():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-1",
            "general",
            "Learn Python",
        )

        update_session_progress(
            db,
            test_session_id,
            "Python Functions",
            50.0,
        )

        session = get_learning_session(
            db,
            test_session_id,
        )

        assert session is not None
        assert session.current_topic == "Python Functions"
        assert session.progress_percent == 50.0
        assert session.status == "active"

    finally:
        db.close()


def test_save_and_get_task_attempts():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-1",
            "general",
            "Learn Python",
        )

        save_task_attempt(
            db,
            test_session_id,
            "task-1",
            True,
            "Completed successfully.",
        )

        save_task_attempt(
            db,
            test_session_id,
            "task-2",
            False,
            "Needs more practice.",
        )

        attempts = get_task_attempts(
            db,
            test_session_id,
        )

        assert len(attempts) == 2

        assert attempts[0].task_id == "task-1"
        assert attempts[0].completed is True
        assert attempts[0].notes == "Completed successfully."

        assert attempts[1].task_id == "task-2"
        assert attempts[1].completed is False
        assert attempts[1].notes == "Needs more practice."

    finally:
        db.close()


def test_save_and_get_quiz_attempts():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-1",
            "general",
            "Learn Python",
        )

        save_quiz_attempt(
            db,
            test_session_id,
            "Python Basics",
            80.0,
            5,
        )

        attempts = get_quiz_attempts(
            db,
            test_session_id,
        )

        assert len(attempts) == 1
        assert attempts[0].topic == "Python Basics"
        assert attempts[0].score == 80.0
        assert attempts[0].total_questions == 5

    finally:
        db.close()


def test_complete_session():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-1",
            "general",
            "Learn Python",
        )

        complete_session(
            db,
            test_session_id,
        )

        session = get_learning_session(
            db,
            test_session_id,
        )

        assert session is not None
        assert session.status == "completed"
        assert session.progress_percent == 100.0

    finally:
        db.close()


def test_get_learning_session_returns_none_for_unknown_session():
    db = SessionLocal()

    try:
        session = get_learning_session(
            db,
            create_test_session_id(),
        )

        assert session is None

    finally:
        db.close()