import uuid
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_full_system_integration():
    # 1. Signup user
    unique_email = f"learner_{uuid.uuid4().hex[:8]}@example.com"
    signup_res = client.post(
        "/auth/signup",
        json={
            "name": "Integration Learner",
            "email": unique_email,
            "password": "Password123!",
        },
    )
    assert signup_res.status_code == 200
    token = signup_res.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login user
    login_res = client.post(
        "/auth/login",
        json={
            "email": unique_email,
            "password": "Password123!",
        },
    )
    assert login_res.status_code == 200

    # 3. Create learning session
    start_res = client.post(
        "/learning/start",
        headers=headers,
        json={
            "learning_mode": "general",
            "goal": "Learn Python Data Structures",
            "current_level": "beginner",
            "available_time_minutes": 60,
            "duration_days": 3,
        },
    )
    assert start_res.status_code == 200
    session_data = start_res.json()
    session_id = session_data["session_id"]
    assert session_id

    # 4. Check progress has plan
    prog_res = client.get(
        f"/learning/{session_id}/progress",
        headers=headers,
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["session_id"] == session_id
    assert "plan" in prog_res.json()

    # 5. Check performance endpoint works
    perf_res = client.get(
        f"/learning/{session_id}/performance",
        headers=headers,
    )
    assert perf_res.status_code == 200
    assert perf_res.json()["session_id"] == session_id
    assert "overall_progress" in perf_res.json()

