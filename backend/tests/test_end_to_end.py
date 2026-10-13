from unittest.mock import patch

from langgraph.types import Command

from agents.context_analyzer import analyze_context
from graph.workflow import build_graph
from models.schemas import LearningRequest


def create_general_request():
    return LearningRequest(
        user_id="e2e-user",
        learning_mode="general",
        goal="Learn Python",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=1,
    )


def create_project_request():
    return LearningRequest(
        user_id="e2e-project-user",
        learning_mode="project",
        role="Backend Developer",
        project_name="E-commerce Backend",
        project_description=(
            "Build a production-style e-commerce backend "
            "with authentication, REST APIs and PostgreSQL."
        ),
        required_technologies=[
            "Python",
            "FastAPI",
            "REST APIs",
            "PostgreSQL",
        ],
        current_skills=[
            "Python",
        ],
        duration_days=1,
        available_time_minutes=90,
    )


def create_plan():
    return {
        "plan": {
            "title": "Python Backend Learning Plan",
            "summary": "Learn the fundamentals required for backend development.",
            "topics": [
                {
                    "title": "Python Basics",
                    "description": "Learn Python fundamentals.",
                    "estimated_days": 1,
                    "objectives": [
                        "Understand Python syntax and core concepts.",
                    ],
                }
            ],
        }
    }


def create_tasks():
    return {
        "tasks": [
            {
                "id": "e2e-task-1",
                "title": "Study Python fundamentals",
                "description": "Study variables, data types and control flow.",
                "task_type": "study",
                "estimated_minutes": 30,
                "objective": "Understand Python fundamentals.",
            }
        ],
        "completed_tasks": [],
        "unfinished_tasks": [],
        "skipped_tasks": [],
        "carried_forward_tasks": [],
    }


def create_quiz():
    return {
        "quiz": [
            {
                "id": f"e2e-q{i}",
                "question": f"Python question {i}",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "A is the correct answer.",
            }
            for i in range(1, 6)
        ]
    }


def resume_plan_approval(graph, config, approved=True, feedback=""):
    return graph.invoke(
        Command(
            resume={
                "approved": approved,
                "feedback": feedback,
            }
        ),
        config=config,
    )


def resume_day_submission(graph, config):
    return graph.invoke(
        Command(
            resume={
                "tasks": [
                    {
                        "task_id": "e2e-task-1",
                        "status": "done",
                        "notes": "Completed the task.",
                    }
                ]
            }
        ),
        config=config,
    )


def resume_quiz(graph, config, correct=True):
    answer = "A" if correct else "B"

    return graph.invoke(
        Command(
            resume={
                "answers": [
                    {
                        "question_id": f"e2e-q{i}",
                        "answer": answer,
                    }
                    for i in range(1, 6)
                ]
            }
        ),
        config=config,
    )


def test_general_learning_end_to_end():
    config = {
        "configurable": {
            "thread_id": "e2e-general-flow",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(),
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ), patch(
        "graph.workflow.generate_quiz",
        return_value=create_quiz(),
    ):
        graph = build_graph()

        initial_state = analyze_context(
            create_general_request()
        )

        # 1. Start learning workflow.
        result = graph.invoke(
            initial_state,
            config=config,
        )

        assert "__interrupt__" in result
        assert result["plan"]["title"] == "Python Backend Learning Plan"

        # 2. Approve generated roadmap.
        result = resume_plan_approval(
            graph,
            config,
        )

        assert "__interrupt__" in result
        assert result["current_topic"] == "Python Basics"
        assert result["current_day"] == 1

        # 3. Complete daily tasks.
        result = resume_day_submission(
            graph,
            config,
        )

        assert "__interrupt__" in result
        assert result["topic_completed"] is True

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "quiz_submission"
        assert len(interrupt_data["quiz"]) == 5

        # 4. Submit perfect quiz.
        result = resume_quiz(
            graph,
            config,
            correct=True,
        )

        # 5. Verify evaluation and completion.
        assert result["quiz_score"] == 100.0
        assert result["strong_topics"] == ["Python Basics"]
        assert result["adaptive_action"] == "move_forward"
        assert result["goal_completed"] is True


def test_project_learning_end_to_end():
    config = {
        "configurable": {
            "thread_id": "e2e-project-flow",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(),
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ), patch(
        "graph.workflow.generate_quiz",
        return_value=create_quiz(),
    ):
        graph = build_graph()

        initial_state = analyze_context(
            create_project_request()
        )

        # Project context should preserve required technologies.
        assert initial_state["learning_mode"] == "project"
        assert initial_state["role"] == "Backend Developer"
        assert "FastAPI" in initial_state["required_technologies"]
        assert "PostgreSQL" in initial_state["required_technologies"]

        # 1. Start project workflow.
        result = graph.invoke(
            initial_state,
            config=config,
        )

        assert "__interrupt__" in result
        assert result["plan"]["title"] == "Python Backend Learning Plan"

        # 2. Approve roadmap.
        result = resume_plan_approval(
            graph,
            config,
        )

        assert "__interrupt__" in result
        assert result["current_topic"] == "Python Basics"

        # 3. Complete first day's tasks.
        result = resume_day_submission(
            graph,
            config,
        )

        assert "__interrupt__" in result

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "quiz_submission"

        # 4. Submit quiz.
        result = resume_quiz(
            graph,
            config,
            correct=True,
        )

        assert result["quiz_score"] == 100.0
        assert result["goal_completed"] is True


def test_weak_performance_enters_remediation_end_to_end():
    config = {
        "configurable": {
            "thread_id": "e2e-remediation-flow",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(),
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ), patch(
        "graph.workflow.generate_quiz",
        return_value=create_quiz(),
    ):
        graph = build_graph()

        initial_state = analyze_context(
            create_general_request()
        )

        # 1. Start.
        graph.invoke(
            initial_state,
            config=config,
        )

        # 2. Approve.
        resume_plan_approval(
            graph,
            config,
        )

        # 3. Complete daily tasks.
        resume_day_submission(
            graph,
            config,
        )

        # 4. Submit incorrect answers.
        result = resume_quiz(
            graph,
            config,
            correct=False,
        )

        # 5. Verify weak performance.
        assert result["quiz_score"] == 0.0
        assert result["weak_topics"] == ["Python Basics"]
        assert result["adaptive_action"] == "improve_weak_topics"

        assert result["improvement_days"] > 0
        assert result["improvement_time_minutes"] > 0
        assert result["improvement_description"]

        # 6. The workflow should return to task/day execution
        # for remediation rather than completing the goal.
        assert "__interrupt__" in result

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "day_submission"
        assert result["goal_completed"] is False


def test_plan_rejection_and_revision_end_to_end():
    config = {
        "configurable": {
            "thread_id": "e2e-plan-revision",
        }
    }

    revised_plan = {
        "plan": {
            "title": "Revised Python Learning Plan",
            "summary": "A revised plan with additional practical work.",
            "topics": [
                {
                    "title": "Python Basics",
                    "description": (
                        "Learn Python fundamentals through practical exercises."
                    ),
                    "estimated_days": 1,
                    "objectives": [
                        "Understand Python fundamentals.",
                        "Practice Python fundamentals.",
                    ],
                }
            ],
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        side_effect=[
            create_plan(),
            revised_plan,
        ],
    ) as mock_planner:
        graph = build_graph()

        # 1. Initial plan.
        result = graph.invoke(
            analyze_context(create_general_request()),
            config=config,
        )

        assert "__interrupt__" in result
        assert mock_planner.call_count == 1

        # 2. Reject with feedback.
        result = resume_plan_approval(
            graph,
            config,
            approved=False,
            feedback="Add more practical work.",
        )

        assert "__interrupt__" in result
        assert mock_planner.call_count == 2

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "plan_approval"
        assert (
            interrupt_data["plan"]["title"]
            == "Revised Python Learning Plan"
        )