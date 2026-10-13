from unittest.mock import patch

from agents.task import generate_tasks


class FakeLLM:
    def invoke(self, prompt):
        return """
        {
            "tasks": [
                {
                    "id": "task-1",
                    "title": "Define Python functions",
                    "description": "Study function syntax and parameters.",
                    "task_type": "study",
                    "estimated_minutes": 20,
                    "objective": "Understand Python functions"
                },
                {
                    "id": "task-2",
                    "title": "Practice functions",
                    "description": "Write simple Python functions.",
                    "task_type": "practice",
                    "estimated_minutes": 30,
                    "objective": "Practice defining functions"
                }
            ]
        }
        """


def test_task_generation():
    state = {
        "learning_mode": "general",
        "current_topic": "Python Functions",
        "current_day": 1,
        "available_time_minutes": 60,
        "plan": {
            "topics": [
                {
                    "title": "Python Functions",
                    "description": "Learn Python functions.",
                    "estimated_days": 2,
                    "objectives": [
                        "Understand Python functions",
                        "Practice defining functions",
                    ],
                }
            ]
        },
        "carried_forward_tasks": [],
    }

    with patch(
        "agents.task.get_llm",
        return_value=FakeLLM(),
    ):
        result = generate_tasks(state)

    assert len(result["tasks"]) == 2
    assert result["completed_tasks"] == []
    assert result["unfinished_tasks"] == []
    assert result["skipped_tasks"] == []
    assert result["carried_forward_tasks"] == []

    for task in result["tasks"]:
        assert task["id"]
        assert task["title"]
        assert task["description"]
        assert task["task_type"]
        assert task["estimated_minutes"] > 0
        assert task["objective"]


def test_carried_forward_tasks_are_preserved():
    carried_task = {
        "id": "task-old",
        "title": "Review function parameters",
        "description": "Review positional and keyword parameters.",
        "task_type": "study",
        "estimated_minutes": 20,
        "objective": "Understand function parameters",
    }

    state = {
        "learning_mode": "general",
        "current_topic": "Python Functions",
        "current_day": 2,
        "available_time_minutes": 60,
        "plan": {
            "topics": [
                {
                    "title": "Python Functions",
                    "description": "Learn Python functions.",
                    "estimated_days": 2,
                    "objectives": [
                        "Understand Python functions",
                    ],
                }
            ]
        },
        "carried_forward_tasks": [carried_task],
    }

    with patch(
        "agents.task.get_llm",
        return_value=FakeLLM(),
    ):
        result = generate_tasks(state)

    task_ids = [task["id"] for task in result["tasks"]]

    assert "task-old" in task_ids
    assert "task-1" in task_ids
    assert "task-2" in task_ids

    preserved_task = next(
        task
        for task in result["tasks"]
        if task["id"] == "task-old"
    )

    assert preserved_task == carried_task
    assert result["unfinished_tasks"] == ["task-old"]
    assert result["carried_forward_tasks"] == []


def test_new_task_id_is_made_unique():
    state = {
        "learning_mode": "general",
        "current_topic": "Python Functions",
        "current_day": 2,
        "available_time_minutes": 60,
        "plan": {
            "topics": [
                {
                    "title": "Python Functions",
                    "description": "Learn Python functions.",
                    "estimated_days": 2,
                    "objectives": [
                        "Understand Python functions",
                    ],
                }
            ]
        },
        "tasks": [
            {
                "id": "task-1",
                "title": "Previous task",
                "description": "Already used.",
                "task_type": "study",
                "estimated_minutes": 20,
                "objective": "Previous objective",
            }
        ],
        "carried_forward_tasks": [],
    }

    with patch(
        "agents.task.get_llm",
        return_value=FakeLLM(),
    ):
        result = generate_tasks(state)

    task_ids = [task["id"] for task in result["tasks"]]

    assert "task-2" in task_ids
    assert len(task_ids) == len(set(task_ids))