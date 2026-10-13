from agents.context_analyzer import analyze_context
from models.schemas import LearningRequest


def test_general_context():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="general",
        goal="  Learn Python  ",
        current_level="  BEGINNER ",
        available_time_minutes=60,
        duration_days=30,
    )

    result = analyze_context(request)

    assert result["user_id"] == "user-1"
    assert result["learning_mode"] == "general"
    assert result["goal"] == "Learn Python"
    assert result["current_level"] == "beginner"
    assert result["available_time_minutes"] == 60
    assert result["duration_days"] == 30

    assert result["role"] == ""
    assert result["project_name"] == ""
    assert result["project_description"] == ""
    assert result["current_skills"] == []
    assert result["required_technologies"] == []


def test_project_context():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Become a backend developer",
        current_level="Intermediate",
        available_time_minutes=120,
        duration_days=21,
        role=" Backend Developer ",
        project_name=" E-commerce Backend ",
        project_description=(
            " Build a backend system for an e-commerce application. "
        ),
        current_skills=[
            "Java",
            "SQL",
            "Java",
            " Git ",
            "",
        ],
        required_technologies=[
            "REST APIs",
            "Database Design",
            "Spring Boot",
            "PostgreSQL",
            "Spring Boot",
        ],
    )

    result = analyze_context(request)

    assert result["learning_mode"] == "project"
    assert result["current_level"] == "intermediate"

    assert result["role"] == "Backend Developer"
    assert result["project_name"] == "E-commerce Backend"

    assert result["project_description"] == (
        "Build a backend system for an e-commerce application."
    )

    assert result["current_skills"] == [
        "Java",
        "SQL",
        "Git",
    ]

    assert result["required_technologies"] == [
        "REST APIs",
        "Database Design",
        "Spring Boot",
        "PostgreSQL",
    ]


def test_skill_lists_remove_case_insensitive_duplicates():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Backend development",
        role="Backend Developer",
        project_name="Test Project",
        project_description="Test project",
        current_skills=[
            "Java",
            "java",
            " SQL ",
        ],
        required_technologies=[
            "Spring Boot",
            "spring boot",
            " Docker ",
        ],
    )

    result = analyze_context(request)

    assert result["current_skills"] == [
        "Java",
        "SQL",
    ]

    assert result["required_technologies"] == [
        "Spring Boot",
        "Docker",
    ]


def test_empty_skill_values_are_removed():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="project",
        goal="Backend development",
        role="Backend Developer",
        project_name="Test Project",
        project_description="Test project",
        current_skills=[
            "",
            " ",
            "Python",
        ],
        required_technologies=[
            "",
            "SQL",
            " ",
            "Docker",
        ],
    )

    result = analyze_context(request)

    assert result["current_skills"] == [
        "Python"
    ]

    assert result["required_technologies"] == [
        "SQL",
        "Docker",
    ]


def test_optional_project_fields_default_to_empty_strings():
    request = LearningRequest(
        user_id="user-1",
        learning_mode="general",
        goal="Learn Machine Learning",
        available_time_minutes=60,
    )

    result = analyze_context(request)

    assert result["role"] == ""
    assert result["project_name"] == ""
    assert result["project_description"] == ""