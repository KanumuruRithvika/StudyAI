from services.memory import (
    calculate_task_progress,
    complete_day,
    complete_task,
    prepare_next_day,
)


def create_state():
    return {
        "current_day": 1,
        "tasks": [
            {
                "id": "task-1",
                "title": "Study functions",
                "description": "Learn Python functions.",
                "task_type": "study",
                "estimated_minutes": 20,
                "objective": "Understand functions",
            },
            {
                "id": "task-2",
                "title": "Practice functions",
                "description": "Write Python functions.",
                "task_type": "practice",
                "estimated_minutes": 30,
                "objective": "Practice functions",
            },
            {
                "id": "task-3",
                "title": "Build a small example",
                "description": "Create a small functions program.",
                "task_type": "project",
                "estimated_minutes": 30,
                "objective": "Apply functions",
            },
        ],
        "completed_tasks": [],
        "unfinished_tasks": [],
        "skipped_tasks": [],
        "carried_forward_tasks": [],
        "task_progress": 0.0,
    }


def test_complete_task_marks_task_done():
    state = create_state()

    result = complete_task(
        state,
        "task-1",
        status="done",
    )

    assert result["completed_tasks"] == ["task-1"]
    assert result["unfinished_tasks"] == ["task-2", "task-3"]
    assert result["skipped_tasks"] == []
    assert result["task_progress"] == 33.33


def test_complete_task_marks_task_not_done():
    state = create_state()

    result = complete_task(
        state,
        "task-1",
        status="not_done",
    )

    assert result["completed_tasks"] == []
    assert result["unfinished_tasks"] == [
        "task-1",
        "task-2",
        "task-3",
    ]
    assert result["skipped_tasks"] == []
    assert result["task_progress"] == 0.0


def test_complete_task_marks_task_skipped():
    state = create_state()

    result = complete_task(
        state,
        "task-1",
        status="skip",
    )

    assert result["completed_tasks"] == []
    assert result["unfinished_tasks"] == ["task-2", "task-3"]
    assert result["skipped_tasks"] == ["task-1"]
    assert result["task_progress"] == 0.0


def test_complete_task_supports_completed_boolean():
    state = create_state()

    result = complete_task(
        state,
        "task-1",
        completed=True,
    )

    assert result["completed_tasks"] == ["task-1"]


def test_complete_day_records_all_task_statuses():
    state = create_state()

    result = complete_day(
        state,
        [
            {
                "task_id": "task-1",
                "status": "done",
                "notes": "Completed the exercises.",
            },
            {
                "task_id": "task-2",
                "status": "skip",
                "notes": "Not required today.",
            },
            {
                "task_id": "task-3",
                "status": "not_done",
                "notes": "Need more time.",
            },
        ],
    )

    assert result["completed_tasks"] == ["task-1"]
    assert result["unfinished_tasks"] == ["task-3"]
    assert result["skipped_tasks"] == ["task-2"]
    assert result["task_progress"] == 50.0


def test_complete_day_marks_omitted_tasks_not_done():
    state = create_state()

    result = complete_day(
        state,
        [
            {
                "task_id": "task-1",
                "status": "done",
                "notes": None,
            }
        ],
    )

    assert result["completed_tasks"] == ["task-1"]
    assert set(result["unfinished_tasks"]) == {
        "task-2",
        "task-3",
    }
    assert result["skipped_tasks"] == []
    assert result["task_progress"] == 33.33


def test_complete_day_carries_full_unfinished_tasks():
    state = create_state()

    result = complete_day(
        state,
        [
            {
                "task_id": "task-1",
                "status": "done",
                "notes": None,
            },
            {
                "task_id": "task-2",
                "status": "not_done",
                "notes": "Need more practice.",
            },
            {
                "task_id": "task-3",
                "status": "skip",
                "notes": None,
            },
        ],
    )

    assert result["unfinished_tasks"] == ["task-2"]
    assert result["carried_forward_tasks"] == [
        {
            "id": "task-2",
            "title": "Practice functions",
            "description": "Write Python functions.",
            "task_type": "practice",
            "estimated_minutes": 30,
            "objective": "Practice functions",
        }
    ]


def test_prepare_next_day_carries_unfinished_tasks():
    state = {
        "current_day": 1,
        "carried_forward_tasks": [
            {
                "id": "task-2",
                "title": "Practice functions",
                "description": "Write Python functions.",
                "task_type": "practice",
                "estimated_minutes": 30,
                "objective": "Practice functions",
            }
        ],
        "unfinished_tasks": ["task-2"],
        "completed_tasks": ["task-1"],
        "skipped_tasks": [],
        "task_progress": 50.0,
        "tasks": [],
    }

    result = prepare_next_day(state)

    assert result["current_day"] == 2
    assert result["unfinished_tasks"] == ["task-2"]

    assert result["carried_forward_tasks"] == [
        {
            "id": "task-2",
            "title": "Practice functions",
            "description": "Write Python functions.",
            "task_type": "practice",
            "estimated_minutes": 30,
            "objective": "Practice functions",
        }
    ]

    assert result["completed_tasks"] == []
    assert result["skipped_tasks"] == []
    assert result["task_progress"] == 0.0
    assert result["tasks"] == []


def test_prepare_next_day_does_not_modify_original_tasks():
    carried_task = {
        "id": "task-2",
        "title": "Practice functions",
        "description": "Write Python functions.",
        "task_type": "practice",
        "estimated_minutes": 30,
        "objective": "Practice functions",
    }

    state = {
        "current_day": 1,
        "carried_forward_tasks": [carried_task],
    }

    result = prepare_next_day(state)

    result["carried_forward_tasks"][0]["title"] = "Changed"

    assert (
        state["carried_forward_tasks"][0]["title"]
        == "Practice functions"
    )


def test_task_progress_calculation():
    assert calculate_task_progress(0, 3) == 0.0
    assert calculate_task_progress(1, 3) == 33.33
    assert calculate_task_progress(2, 3) == 66.67
    assert calculate_task_progress(3, 3) == 100.0


def test_zero_total_tasks_returns_zero_progress():
    assert calculate_task_progress(0, 0) == 0.0