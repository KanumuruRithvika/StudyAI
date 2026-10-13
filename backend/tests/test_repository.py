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


def create_test_session_id():
    return f"test-{uuid.uuid4()}"


def test_create_learning_session():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        session = create_learning_session(
            db,
            test_session_id,
            "user-1",
            "general",
            "Learn Python",
        )

        assert session.id == test_session_id
        assert session.user_id == "user-1"
        assert session.learning_mode == "general"
        assert session.goal == "Learn Python"
        assert session.status == "active"
    finally:
        db.close()


def test_get_learning_session():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-2",
            "general",
            "Learn Machine Learning",
        )

        session = get_learning_session(
            db,
            test_session_id,
        )

        assert session is not None
        assert session.id == test_session_id
        assert session.user_id == "user-2"
        assert session.goal == "Learn Machine Learning"
    finally:
        db.close()


def test_get_learning_session_returns_none():
    db = SessionLocal()

    try:
        session = get_learning_session(
            db,
            create_test_session_id(),
        )

        assert session is None
    finally:
        db.close()


def test_update_session_progress():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-3",
            "project",
            "Build an e-commerce backend",
        )

        update_session_progress(
            db,
            test_session_id,
            "Spring Boot",
            40.0,
        )

        session = get_learning_session(
            db,
            test_session_id,
        )

        assert session.current_topic == "Spring Boot"
        assert session.progress_percent == 40.0
        assert session.status == "active"
    finally:
        db.close()


def test_save_task_attempt():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-4",
            "general",
            "Learn Python",
        )

        attempt = save_task_attempt(
            db,
            test_session_id,
            "task-1",
            True,
            "Completed.",
        )

        assert attempt.session_id == test_session_id
        assert attempt.task_id == "task-1"
        assert attempt.completed is True
        assert attempt.notes == "Completed."
    finally:
        db.close()


def test_get_task_attempts():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-5",
            "general",
            "Learn Python",
        )

        save_task_attempt(
            db,
            test_session_id,
            "task-1",
            True,
            "Done.",
        )

        save_task_attempt(
            db,
            test_session_id,
            "task-2",
            False,
            "Incomplete.",
        )

        attempts = get_task_attempts(
            db,
            test_session_id,
        )

        assert len(attempts) == 2
        assert attempts[0].task_id == "task-1"
        assert attempts[0].completed is True
        assert attempts[1].task_id == "task-2"
        assert attempts[1].completed is False
    finally:
        db.close()


def test_save_quiz_attempt():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-6",
            "general",
            "Learn Python",
        )

        attempt = save_quiz_attempt(
            db,
            test_session_id,
            "Python Basics",
            80.0,
            5,
        )

        assert attempt.session_id == test_session_id
        assert attempt.topic == "Python Basics"
        assert attempt.score == 80.0
        assert attempt.total_questions == 5
    finally:
        db.close()


def test_get_quiz_attempts():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-7",
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

        save_quiz_attempt(
            db,
            test_session_id,
            "Functions",
            100.0,
            5,
        )

        attempts = get_quiz_attempts(
            db,
            test_session_id,
        )

        assert len(attempts) == 2
        assert attempts[0].topic == "Python Basics"
        assert attempts[0].score == 80.0
        assert attempts[1].topic == "Functions"
        assert attempts[1].score == 100.0
    finally:
        db.close()


def test_complete_session():
    db = SessionLocal()
    test_session_id = create_test_session_id()

    try:
        create_learning_session(
            db,
            test_session_id,
            "user-8",
            "general",
            "Learn Python",
        )

        result = complete_session(
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
        assert result is not None
    finally:
        db.close()