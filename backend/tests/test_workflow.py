from unittest.mock import patch

from langgraph.types import Command

from agents.context_analyzer import analyze_context
from graph.workflow import build_graph
from models.schemas import LearningRequest


def create_initial_state():
    request = LearningRequest(
        user_id="test-user",
        learning_mode="general",
        goal="Learn Python",
        current_level="beginner",
        available_time_minutes=60,
        duration_days=7,
    )

    return analyze_context(request)


def create_plan(estimated_days=1):
    return {
        "plan": {
            "title": "Python Learning Plan",
            "summary": "Learn Python",
            "topics": [
                {
                    "title": "Python Basics",
                    "description": "Learn Python fundamentals.",
                    "estimated_days": estimated_days,
                    "objectives": [
                        "Understand Python basics",
                    ],
                }
            ],
        }
    }


def create_tasks():
    return {
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
        "unfinished_tasks": [],
        "skipped_tasks": [],
        "carried_forward_tasks": [],
    }


def create_quiz():
    return {
        "quiz": [
            {
                "id": f"q{i}",
                "question": f"Question {i}",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "A is correct.",
            }
            for i in range(1, 6)
        ]
    }


def approve_plan(graph, config):
    return graph.invoke(
        Command(
            resume={
                "approved": True,
                "feedback": "",
            }
        ),
        config=config,
    )


def submit_task(graph, config):
    return graph.invoke(
        Command(
            resume={
                "tasks": [
                    {
                        "task_id": "task-1",
                        "status": "done",
                        "notes": "",
                    }
                ]
            }
        ),
        config=config,
    )


def submit_quiz(graph, config, answer="A"):
    return graph.invoke(
        Command(
            resume={
                "answers": [
                    {
                        "question_id": f"q{i}",
                        "answer": answer,
                    }
                    for i in range(1, 6)
                ]
            }
        ),
        config=config,
    )


def test_plan_approval_pauses_workflow():
    config = {
        "configurable": {
            "thread_id": "workflow-plan-approval",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(),
    ):
        graph = build_graph()

        result = graph.invoke(
            create_initial_state(),
            config=config,
        )

        assert "__interrupt__" in result

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "plan_approval"
        assert (
            interrupt_data["plan"]["title"]
            == "Python Learning Plan"
        )


def test_plan_approval_continues_to_daily_tasks():
    config = {
        "configurable": {
            "thread_id": "workflow-approved-plan",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(),
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ):
        graph = build_graph()

        graph.invoke(
            create_initial_state(),
            config=config,
        )

        result = approve_plan(graph, config)

        assert "__interrupt__" in result

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "day_submission"
        assert result["current_topic"] == "Python Basics"
        assert result["current_day"] == 1


def test_plan_rejection_reopens_planner():
    config = {
        "configurable": {
            "thread_id": "workflow-plan-revision",
        }
    }

    planner_results = [
        create_plan(),
        {
            "plan": {
                "title": "Updated Python Plan",
                "summary": "Updated plan",
                "topics": [
                    {
                        "title": "Python Basics",
                        "description": (
                            "Learn Python fundamentals with practice."
                        ),
                        "estimated_days": 1,
                        "objectives": [
                            "Understand Python basics",
                            "Practice Python basics",
                        ],
                    }
                ],
            }
        },
    ]

    with patch(
        "graph.workflow.create_learning_plan",
        side_effect=planner_results,
    ) as mock_planner:
        graph = build_graph()

        graph.invoke(
            create_initial_state(),
            config=config,
        )

        result = graph.invoke(
            Command(
                resume={
                    "approved": False,
                    "feedback": "Add more practical work.",
                }
            ),
            config=config,
        )

        assert "__interrupt__" in result
        assert mock_planner.call_count == 2

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "plan_approval"
        assert (
            interrupt_data["plan"]["title"]
            == "Updated Python Plan"
        )


def test_multi_day_topic_continues_before_quiz():
    config = {
        "configurable": {
            "thread_id": "workflow-multi-day",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(estimated_days=2),
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ):
        graph = build_graph()

        graph.invoke(
            create_initial_state(),
            config=config,
        )

        result = approve_plan(graph, config)

        assert "__interrupt__" in result
        assert result["current_day"] == 1

        result = submit_task(graph, config)

        assert "__interrupt__" in result

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "day_submission"
        assert result["current_day"] == 2
        assert result["topic_completed"] is False


def test_topic_completion_moves_to_quiz():
    config = {
        "configurable": {
            "thread_id": "workflow-topic-quiz",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(estimated_days=1),
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ), patch(
        "graph.workflow.generate_quiz",
        return_value=create_quiz(),
    ):
        graph = build_graph()

        graph.invoke(
            create_initial_state(),
            config=config,
        )

        approve_plan(graph, config)

        result = submit_task(graph, config)

        assert "__interrupt__" in result

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "quiz_submission"
        assert result["topic_completed"] is True
        assert len(interrupt_data["quiz"]) == 5


def test_quiz_evaluation_moves_to_completion():
    config = {
        "configurable": {
            "thread_id": "workflow-quiz-evaluation",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(estimated_days=1),
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ), patch(
        "graph.workflow.generate_quiz",
        return_value=create_quiz(),
    ):
        graph = build_graph()

        graph.invoke(
            create_initial_state(),
            config=config,
        )

        approve_plan(graph, config)
        submit_task(graph, config)

        result = submit_quiz(graph, config)

        assert result["quiz_score"] == 100.0
        assert result["goal_completed"] is True
        assert result["current_topic"] == "Python Basics"
        assert result["strong_topics"] == ["Python Basics"]
        assert result["adaptive_action"] == "move_forward"


def test_weak_quiz_score_enters_remediation_flow():
    config = {
        "configurable": {
            "thread_id": "workflow-weak-remediation",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(estimated_days=1),
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ), patch(
        "graph.workflow.generate_quiz",
        return_value=create_quiz(),
    ):
        graph = build_graph()

        graph.invoke(
            create_initial_state(),
            config=config,
        )

        approve_plan(graph, config)
        submit_task(graph, config)

        result = submit_quiz(graph, config, answer="B")

        assert result["quiz_score"] == 0.0
        assert result["weak_topics"] == ["Python Basics"]
        assert result["adaptive_action"] == "improve_weak_topics"

        assert result["improvement_description"]
        assert result["improvement_days"] > 0
        assert result["improvement_time_minutes"] > 0

        assert "__interrupt__" in result

        interrupt_data = result["__interrupt__"][0].value

        assert interrupt_data["type"] == "day_submission"


def test_planner_runs_only_once_after_approval():
    config = {
        "configurable": {
            "thread_id": "workflow-planner-once",
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=create_plan(estimated_days=2),
    ) as mock_planner, patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ):
        graph = build_graph()

        graph.invoke(
            create_initial_state(),
            config=config,
        )

        assert mock_planner.call_count == 1

        approve_plan(graph, config)

        assert mock_planner.call_count == 1

        submit_task(graph, config)

        assert mock_planner.call_count == 1


def test_multi_topic_quiz_score_preserved_on_advance():
    config = {
        "configurable": {
            "thread_id": "workflow-multi-topic-score-preserved",
        }
    }

    two_topic_plan = {
        "plan": {
            "title": "Python Plan",
            "summary": "Plan",
            "topics": [
                {
                    "title": "Topic 1",
                    "description": "First topic",
                    "estimated_days": 1,
                    "objectives": ["Obj 1"],
                },
                {
                    "title": "Topic 2",
                    "description": "Second topic",
                    "estimated_days": 1,
                    "objectives": ["Obj 2"],
                },
            ],
        }
    }

    with patch(
        "graph.workflow.create_learning_plan",
        return_value=two_topic_plan,
    ), patch(
        "graph.workflow.generate_tasks",
        return_value=create_tasks(),
    ), patch(
        "graph.workflow.generate_quiz",
        return_value=create_quiz(),
    ):
        graph = build_graph()
        graph.invoke(create_initial_state(), config=config)
        approve_plan(graph, config)
        submit_task(graph, config)
        result = submit_quiz(graph, config, answer="A")

        assert result["quiz_score"] == 100.0
        assert result["current_topic"] == "Topic 2"
        assert result["current_topic_index"] == 1