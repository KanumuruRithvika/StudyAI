from unittest.mock import patch

import pytest

from agents.context_analyzer import analyze_context
from agents.planner import create_learning_plan
from models.schemas import LearningRequest


class FakeLLM:
    def __init__(self, response):
        self.response = response
        self.last_prompt = ""

    def invoke(self, prompt):
        self.last_prompt = prompt
        return self.response


def create_general_state():
    request = LearningRequest(
        user_id="test-user",
        learning_mode="general",
        goal="Learn Python",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=7,
    )

    return analyze_context(request)


def create_project_state():
    request = LearningRequest(
        user_id="test-user",
        learning_mode="project",
        goal="Become a backend developer",
        current_level="intermediate",
        available_time_minutes=120,
        duration_days=14,
        role="Backend Developer",
        project_name="E-commerce Backend",
        project_description=(
            "Build a backend service for an e-commerce application."
        ),
        current_skills=[
            "Java",
            "SQL",
            "Git",
        ],
        required_technologies=[
            "REST APIs",
            "Database Design",
            "Spring Boot",
            "PostgreSQL",
            "Redis",
        ],
    )

    return analyze_context(request)


def valid_plan_response():
    return """
    {
        "title": "Python Learning Plan",
        "summary": "A practical Python learning roadmap.",
        "topics": [
            {
                "title": "Python Basics",
                "description": "Learn Python fundamentals.",
                "estimated_days": 2,
                "objectives": [
                    "Understand Python syntax",
                    "Use variables and data types"
                ]
            },
            {
                "title": "Python Functions",
                "description": "Learn how to define and use functions.",
                "estimated_days": 2,
                "objectives": [
                    "Define functions",
                    "Use parameters and return values"
                ]
            }
        ]
    }
    """


def test_general_plan_generation():
    state = create_general_state()

    with patch(
        "agents.planner.get_llm",
        return_value=FakeLLM(valid_plan_response()),
    ):
        result = create_learning_plan(state)

    plan = result["plan"]

    assert plan["title"]
    assert plan["summary"]
    assert len(plan["topics"]) == 2
    assert plan["topics"][0]["title"] == "Python Basics"
    assert plan["topics"][1]["title"] == "Python Functions"
    assert result["plan_approved"] is False


def test_plan_contains_topic_objectives():
    state = create_general_state()

    with patch(
        "agents.planner.get_llm",
        return_value=FakeLLM(valid_plan_response()),
    ):
        result = create_learning_plan(state)

    for topic in result["plan"]["topics"]:
        assert topic["title"]
        assert topic["description"]
        assert topic["estimated_days"] > 0
        assert topic["objectives"]

        for objective in topic["objectives"]:
            assert objective.strip()


def test_plan_duration_cannot_exceed_requested_duration():
    state = create_general_state()

    invalid_plan = """
    {
        "title": "Python Learning Plan",
        "summary": "Too long.",
        "topics": [
            {
                "title": "Python Basics",
                "description": "Learn Python basics.",
                "estimated_days": 5,
                "objectives": [
                    "Understand Python basics"
                ]
            },
            {
                "title": "Python Functions",
                "description": "Learn functions.",
                "estimated_days": 5,
                "objectives": [
                    "Understand functions"
                ]
            }
        ]
    }
    """

    with patch(
        "agents.planner.get_llm",
        return_value=FakeLLM(invalid_plan),
    ):
        with pytest.raises(ValueError, match="exceeds"):
            create_learning_plan(state)


def test_project_plan_uses_project_context():
    state = create_project_state()

    project_plan = """
    {
        "title": "Backend Developer Roadmap",
        "summary": "Prepare for the e-commerce backend project.",
        "topics": [
            {
                "title": "Spring Boot",
                "description": "Build REST APIs with Spring Boot.",
                "estimated_days": 4,
                "objectives": [
                    "Create Spring Boot REST APIs",
                    "Structure a backend service"
                ]
            },
            {
                "title": "PostgreSQL",
                "description": "Use PostgreSQL for backend persistence.",
                "estimated_days": 3,
                "objectives": [
                    "Design relational schemas",
                    "Write PostgreSQL queries"
                ]
            }
        ]
    }
    """

    fake_llm = FakeLLM(project_plan)

    with patch(
        "agents.planner.get_llm",
        return_value=fake_llm,
    ):
        result = create_learning_plan(state)

    plan = result["plan"]

    assert plan["title"] == "Backend Developer Roadmap"
    assert plan["topics"][0]["title"] == "Spring Boot"
    assert plan["topics"][1]["title"] == "PostgreSQL"

    assert "Backend Developer" in fake_llm.last_prompt
    assert "E-commerce Backend" in fake_llm.last_prompt
    assert "Spring Boot" in fake_llm.last_prompt
    assert "PostgreSQL" in fake_llm.last_prompt
    assert "Redis" in fake_llm.last_prompt


def test_plan_prompt_does_not_request_daily_tasks():
    state = create_general_state()

    fake_llm = FakeLLM(valid_plan_response())

    with patch(
        "agents.planner.get_llm",
        return_value=fake_llm,
    ):
        create_learning_plan(state)

    assert "topic-based learning roadmap" in fake_llm.last_prompt
    assert "Create learning TOPICS" in fake_llm.last_prompt
    assert (
        "Daily tasks will be generated separately"
        in fake_llm.last_prompt
    )


def test_plan_revision_feedback_is_included():
    state = create_general_state()

    state["plan_feedback"] = "Add more practical exercises."

    fake_llm = FakeLLM(valid_plan_response())

    with patch(
        "agents.planner.get_llm",
        return_value=fake_llm,
    ):
        create_learning_plan(state)

    assert "Add more practical exercises." in fake_llm.last_prompt
    assert "rejected the previous plan" in fake_llm.last_prompt


def test_plan_approval_is_false_after_generation():
    state = create_general_state()

    with patch(
        "agents.planner.get_llm",
        return_value=FakeLLM(valid_plan_response()),
    ):
        result = create_learning_plan(state)

    assert result["plan_approved"] is False