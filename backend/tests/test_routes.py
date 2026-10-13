from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routes import router
from auth.dependencies import get_current_user


app = FastAPI()
app.include_router(router)


class FakeUser:
    id = "authenticated-user"


app.dependency_overrides[get_current_user] = lambda: FakeUser()

client = TestClient(app)


def test_start_learning():
    fake_result = {
        "session_id": "session-1",
        "state": {
            "goal": "Learn Python",
            "learning_mode": "general",
        },
    }

    with patch(
        "api.routes.start_learning_session",
        return_value=fake_result,
    ) as start_session:

        response = client.post(
            "/learning/start",
            json={
                "user_id": "user-from-client",
                "learning_mode": "general",
                "goal": "Learn Python",
                "current_level": "beginner",
                "available_time_minutes": 60,
                "duration_days": 7,
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result
    start_session.assert_called_once()

    request = start_session.call_args.args[0]

    assert request.user_id == "authenticated-user"
    assert request.goal == "Learn Python"


def test_start_project_learning():
    fake_result = {
        "session_id": "session-2",
        "state": {
            "goal": "Become job ready",
            "learning_mode": "project",
        },
    }

    with patch(
        "api.routes.start_learning_session",
        return_value=fake_result,
    ):

        response = client.post(
            "/learning/start",
            json={
                "user_id": "user-from-client",
                "learning_mode": "project",
                "goal": "Become job ready",
                "current_level": "intermediate",
                "available_time_minutes": 90,
                "duration_days": 21,
                "role": "Backend Developer",
                "project_name": "E-commerce Backend",
                "project_description": (
                    "Build a scalable e-commerce backend."
                ),
                "current_skills": [
                    "Java",
                    "SQL",
                    "Git",
                ],
                "required_technologies": [
                    "Spring Boot",
                    "PostgreSQL",
                    "Redis",
                    "Docker",
                ],
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result


def test_start_learning_rejects_invalid_mode():
    response = client.post(
        "/learning/start",
        json={
            "learning_mode": "invalid",
            "goal": "Learn Python",
            "current_level": "beginner",
            "available_time_minutes": 60,
            "duration_days": 7,
        },
    )

    assert response.status_code == 422


def test_start_learning_rejects_empty_goal():
    response = client.post(
        "/learning/start",
        json={
            "learning_mode": "general",
            "goal": "",
            "current_level": "beginner",
            "available_time_minutes": 60,
            "duration_days": 7,
        },
    )

    assert response.status_code == 422


def test_approve_learning_plan():
    fake_result = {
        "session_id": "session-1",
        "state": {
            "plan_approved": True,
        },
    }

    with patch(
        "api.routes.approve_plan",
        return_value=fake_result,
    ) as approve:

        response = client.post(
            "/learning/session-1/approve",
            json={
                "approved": True,
                "feedback": "",
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result
    approve.assert_called_once()


def test_reject_learning_plan_with_feedback():
    fake_result = {
        "session_id": "session-1",
        "state": {
            "plan_approved": False,
            "plan_feedback": "Add more practical work.",
        },
    }

    with patch(
        "api.routes.approve_plan",
        return_value=fake_result,
    ):

        response = client.post(
            "/learning/session-1/approve",
            json={
                "approved": False,
                "feedback": "Add more practical work.",
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result


def test_complete_task():
    fake_result = {
        "session_id": "session-1",
        "state": {
            "completed_tasks": ["task-1"],
        },
    }

    with patch(
        "api.routes.complete_task",
        return_value=fake_result,
    ) as complete:

        response = client.post(
            "/learning/session-1/tasks/complete",
            json={
                "task_id": "task-1",
                "completed": True,
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result

    complete.assert_called_once_with(
        "session-1",
        "task-1",
        True,
    )


def test_complete_task_with_status():
    fake_result = {
        "session_id": "session-1",
        "state": {
            "completed_tasks": [],
            "skipped_tasks": ["task-1"],
        },
    }

    with patch(
        "api.routes.complete_task",
        return_value=fake_result,
    ) as complete:

        response = client.post(
            "/learning/session-1/tasks/complete",
            json={
                "task_id": "task-1",
                "status": "skip",
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result

    complete.assert_called_once_with(
        "session-1",
        "task-1",
        False,
    )


def test_submit_day():
    fake_result = {
        "session_id": "session-1",
        "state": {
            "current_day": 2,
            "completed_tasks": ["task-1"],
        },
    }

    with patch(
        "api.routes.submit_day",
        return_value=fake_result,
    ) as submit:

        response = client.post(
            "/learning/session-1/day/submit",
            json={
                "tasks": [
                    {
                        "task_id": "task-1",
                        "status": "done",
                        "notes": "Completed.",
                    }
                ]
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result
    submit.assert_called_once()


def test_submit_quiz():
    fake_result = {
        "session_id": "session-1",
        "state": {
            "quiz_score": 80.0,
        },
    }

    with patch(
        "api.routes.submit_quiz",
        return_value=fake_result,
    ) as submit:

        response = client.post(
            "/learning/session-1/quiz/submit",
            json={
                "answers": [
                    {
                        "question_id": "q1",
                        "answer": "A",
                    }
                ]
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_result
    submit.assert_called_once()


def test_approve_plan_handles_value_error():
    with patch(
        "api.routes.approve_plan",
        side_effect=ValueError(
            "Session 'session-1' not found."
        ),
    ):

        response = client.post(
            "/learning/session-1/approve",
            json={
                "approved": True,
                "feedback": "",
            },
        )

    assert response.status_code == 404
    assert (
        response.json()["detail"]
        == "Session 'session-1' not found."
    )


def test_submit_day_handles_value_error():
    with patch(
        "api.routes.submit_day",
        side_effect=ValueError(
            "Cannot submit day tasks: session is currently waiting "
            "for 'quiz_submission'."
        ),
    ):

        response = client.post(
            "/learning/session-1/day/submit",
            json={
                "tasks": [
                    {
                        "task_id": "task-1",
                        "status": "done",
                        "notes": None,
                    }
                ]
            },
        )

    assert response.status_code == 400


def test_submit_quiz_handles_value_error():
    with patch(
        "api.routes.submit_quiz",
        side_effect=ValueError(
            "Cannot submit quiz: session is currently waiting "
            "for 'day_submission'."
        ),
    ):

        response = client.post(
            "/learning/session-1/quiz/submit",
            json={
                "answers": [
                    {
                        "question_id": "q1",
                        "answer": "A",
                    }
                ]
            },
        )

    assert response.status_code == 400


def test_progress_not_found():
    with patch(
        "api.routes.get_learning_session",
        return_value=None,
    ):

        response = client.get(
            "/learning/session-1/progress"
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_progress_returns_learning_data():
    class FakeSession:
        id = "session-1"
        status = "active"
        current_topic = "Python Basics"
        progress_percent = 50.0

    class FakeTaskAttempt:
        completed = True

    class FakeTaskAttempt2:
        completed = False

    class FakeQuizAttempt:
        topic = "Python Basics"
        score = 80.0
        total_questions = 5

    with patch(
        "api.routes.get_learning_session",
        return_value=FakeSession(),
    ), patch(
        "api.routes.get_task_attempts",
        return_value=[
            FakeTaskAttempt(),
            FakeTaskAttempt2(),
        ],
    ), patch(
        "api.routes.get_quiz_attempts",
        return_value=[
            FakeQuizAttempt(),
        ],
    ):

        response = client.get(
            "/learning/session-1/progress"
        )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "session-1"
    assert data["status"] == "active"
    assert data["current_topic"] == "Python Basics"
    assert data["progress_percent"] == 50.0
    assert data["completed_tasks"] == 1
    assert data["total_task_attempts"] == 2
    assert data["quiz_attempts"] == [
        {
            "topic": "Python Basics",
            "score": 80.0,
            "total_questions": 5,
        }
    ]