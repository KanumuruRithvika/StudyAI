import pytest

from models.schemas import LearningRequest
from utils.validators import (
    validate_learning_request,
    validate_project_request,
    validate_quiz_answers,
    validate_task_ids,
)


def test_general_learning_request_is_valid():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="general",
        goal="Learn Python",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=7,
    )

    validate_learning_request(request)


def test_project_learning_request_is_valid():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Become a backend developer",
        current_level="intermediate",
        available_time_minutes=90,
        duration_days=21,
        role="Backend Developer",
        project_name="E-commerce Backend",
        project_description="Build an e-commerce backend.",
        required_technologies=[
            "REST APIs",
            "Spring Boot",
        ],
        current_skills=[
            "Java",
            "SQL",
        ],
    )

    validate_learning_request(request)


def test_project_requires_role():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Learn backend development",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=14,
        project_name="E-commerce Backend",
        project_description="Build an e-commerce backend.",
        required_technologies=[
            "REST APIs",
        ],
    )

    with pytest.raises(
        ValueError,
        match="Role is required",
    ):
        validate_project_request(request)


def test_project_requires_project_name():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Learn backend development",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=14,
        role="Backend Developer",
        project_description="Build an e-commerce backend.",
        required_technologies=[
            "REST APIs",
        ],
    )

    with pytest.raises(
        ValueError,
        match="Project name is required",
    ):
        validate_project_request(request)


def test_project_requires_project_description():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Learn backend development",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=14,
        role="Backend Developer",
        project_name="E-commerce Backend",
        required_technologies=[
            "REST APIs",
        ],
    )

    with pytest.raises(
        ValueError,
        match="Project description is required",
    ):
        validate_project_request(request)


def test_project_requires_skill_or_technology():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Learn backend development",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=14,
        role="Backend Developer",
        project_name="E-commerce Backend",
        project_description="Build an e-commerce backend.",
        required_technologies=[],
    )

    with pytest.raises(
        ValueError,
        match="At least one required skill or technology",
    ):
        validate_project_request(request)


def test_project_can_use_required_technology_without_skill():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Learn backend development",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=14,
        role="Backend Developer",
        project_name="E-commerce Backend",
        project_description="Build an e-commerce backend.",
        required_technologies=[
            "Spring Boot",
        ],
    )

    validate_project_request(request)


def test_validate_task_id_accepts_current_task():
    validate_task_ids(
        "task-1",
        [
            "task-1",
            "task-2",
        ],
    )


def test_validate_task_id_rejects_unknown_task():
    with pytest.raises(
        ValueError,
        match="Task does not belong",
    ):
        validate_task_ids(
            "task-99",
            [
                "task-1",
                "task-2",
            ],
        )


def test_validate_quiz_answers_accepts_expected_count():
    validate_quiz_answers(
        [
            "A",
            "B",
            "C",
            "D",
            "A",
        ],
        5,
    )


def test_validate_quiz_answers_rejects_wrong_count():
    with pytest.raises(
        ValueError,
        match="Expected 5 answers",
    ):
        validate_quiz_answers(
            [
                "A",
                "B",
            ],
            5,
        )


def test_learning_request_defaults():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="general",
        goal="Learn Python",
        available_time_minutes=60,
    )

    assert request.current_level == "beginner"
    assert request.available_time_minutes == 60
    assert request.duration_days is None
    assert request.current_skills == []
    assert request.required_technologies == []


def test_learning_request_rejects_empty_goal():
    with pytest.raises(ValueError):
        LearningRequest(
            user_id="user-1",
            learning_mode="general",
            goal="",
            available_time_minutes=60,
        )