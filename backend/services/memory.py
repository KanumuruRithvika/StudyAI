from datetime import datetime, timezone

from models.state import LearningState
from utils.validators import validate_task_ids


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def calculate_task_progress(
    completed_count: int,
    total_count: int,
) -> float:
    """Calculate completion percentage for active tasks."""
    if total_count <= 0:
        return 0.0

    return round(
        (completed_count / total_count) * 100,
        2,
    )


def complete_task(
    state: LearningState,
    task_id: str,
    status: str = "done",
    notes: str | None = None,
    completed: bool | None = None,
) -> dict:
    """Update one task while preserving the current task state."""
    if completed is not None:
        status = "done" if completed else "not_done"

    tasks = state.get("tasks", [])
    task_ids = [task["id"] for task in tasks]

    validate_task_ids(
        task_id,
        task_ids,
    )

    if status not in {"done", "not_done", "skip"}:
        raise ValueError(
            "Status must be 'done', 'not_done', or 'skip'."
        )

    completed_tasks = [
        item
        for item in state.get("completed_tasks", [])
        if item != task_id
    ]

    skipped_tasks = [
        item
        for item in state.get("skipped_tasks", [])
        if item != task_id
    ]

    if status == "done":
        completed_tasks.append(task_id)
    elif status == "skip":
        skipped_tasks.append(task_id)

    unfinished_tasks = [
        current_id
        for current_id in task_ids
        if current_id not in completed_tasks
        and current_id not in skipped_tasks
    ]

    active_count = len(task_ids) - len(skipped_tasks)

    return {
        "completed_tasks": completed_tasks,
        "unfinished_tasks": unfinished_tasks,
        "skipped_tasks": skipped_tasks,
        "task_progress": calculate_task_progress(
            len(completed_tasks),
            active_count,
        ),
        "last_task_update": {
            "task_id": task_id,
            "status": status,
            "notes": notes,
            "updated_at": _now(),
        },
    }


def complete_day(
    state: LearningState,
    task_updates: list[dict],
) -> dict:
    """Process all task statuses submitted for the current day."""
    tasks = list(state.get("tasks", []))

    if not tasks:
        raise ValueError(
            "No tasks available for this day."
        )

    task_ids = [task["id"] for task in tasks]
    updates = list(task_updates)

    submitted_ids = [
        update["task_id"]
        for update in updates
    ]

    if len(submitted_ids) != len(set(submitted_ids)):
        raise ValueError(
            "Each task can only be submitted once."
        )

    submitted_set = set(submitted_ids)

    for task_id in task_ids:
        if task_id not in submitted_set:
            updates.append({
                "task_id": task_id,
                "status": "not_done",
                "notes": None,
            })

    completed_tasks = []
    unfinished_tasks = []
    skipped_tasks = []
    task_history = []

    for update in updates:
        task_id = update["task_id"]
        status = update["status"]

        validate_task_ids(
            task_id,
            task_ids,
        )

        if status == "done":
            completed_tasks.append(task_id)
        elif status == "not_done":
            unfinished_tasks.append(task_id)
        elif status == "skip":
            skipped_tasks.append(task_id)
        else:
            raise ValueError(
                "Status must be 'done', 'not_done', or 'skip'."
            )

        task_history.append({
            "task_id": task_id,
            "status": status,
            "notes": update.get("notes"),
            "updated_at": _now(),
        })

    active_task_count = (
        len(task_ids) - len(skipped_tasks)
    )

    carried_forward_tasks = [
        dict(task)
        for task in tasks
        if task["id"] in unfinished_tasks
    ]

    return {
        "completed_tasks": completed_tasks,
        "unfinished_tasks": unfinished_tasks,
        "skipped_tasks": skipped_tasks,
        "carried_forward_tasks": carried_forward_tasks,
        "task_progress": calculate_task_progress(
            len(completed_tasks),
            active_task_count,
        ),
        "last_task_update": {
            "type": "day_submission",
            "tasks": task_history,
            "updated_at": _now(),
        },
    }


def prepare_next_day(
    state: LearningState,
) -> dict:
    """Carry unfinished tasks into the next learning day."""
    carried_forward_tasks = [
        dict(task)
        for task in state.get(
            "carried_forward_tasks",
            [],
        )
    ]

    return {
        "unfinished_tasks": [
            task["id"]
            for task in carried_forward_tasks
        ],
        "carried_forward_tasks": carried_forward_tasks,
        "current_day": state.get(
            "current_day",
            1,
        ) + 1,
        "completed_tasks": [],
        "skipped_tasks": [],
        "task_progress": 0.0,
        "tasks": [],
    }