from unittest.mock import patch
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_submit_day_with_undone_tasks_carry_over():
    # 1. Start session
    start_res = client.post(
        "/learning/start",
        json={
            "learning_mode": "general",
            "goal": "Python Mastery",
            "current_level": "beginner",
            "available_time_minutes": 60,
            "duration_days": 2,
        },
    )
    assert start_res.status_code == 200
    session_id = start_res.json()["session_id"]

    # 2. Approve plan
    approve_res = client.post(
        f"/learning/{session_id}/approve",
        json={"approved": True, "feedback": ""},
    )
    assert approve_res.status_code == 200

    # 3. Check day 1 progress
    prog_day1 = client.get(f"/learning/{session_id}/progress").json()
    assert prog_day1["current_day"] == 1
    day1_tasks = prog_day1["tasks"]
    assert len(day1_tasks) >= 2

    # Mark 1 task done, leave the remaining undone
    done_id = day1_tasks[0]["id"]
    undone_id = day1_tasks[1]["id"]

    submit_payload = [
        {"task_id": done_id, "status": "done", "notes": ""},
        {"task_id": undone_id, "status": "not_done", "notes": ""},
    ]
    for task in day1_tasks[2:]:
        submit_payload.append({"task_id": task["id"], "status": "not_done", "notes": ""})

    # 4. Submit day
    submit_res = client.post(
        f"/learning/{session_id}/day/submit",
        json={"tasks": submit_payload},
    )
    assert submit_res.status_code == 200

    # 5. Check day 2 progress has carried forward undone task
    prog_day2 = client.get(f"/learning/{session_id}/progress").json()
    assert prog_day2["current_day"] == 2
    day2_task_ids = [t["id"] for t in prog_day2["tasks"]]

    assert undone_id in day2_task_ids, f"Expected {undone_id} to be carried forward into day 2 tasks"

