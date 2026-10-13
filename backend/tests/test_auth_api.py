import uuid
from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_auth_signup_login_flow():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123"

    # Signup
    signup_res = client.post(
        "/auth/signup",
        json={
            "name": "Integration User",
            "email": email,
            "password": password,
        },
    )
    assert signup_res.status_code == 200
    token = signup_res.json()["access_token"]
    assert token

    # Duplicate signup fails
    dup_res = client.post(
        "/auth/signup",
        json={
            "name": "Integration User",
            "email": email,
            "password": password,
        },
    )
    assert dup_res.status_code == 400

    # Login
    login_res = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_res.status_code == 200
    assert login_res.json()["access_token"]

    # Me
    me_res = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email


def test_auth_login_invalid_password():
    email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/signup",
        json={
            "name": "User",
            "email": email,
            "password": "Password123",
        },
    )

    bad_login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "WrongPassword",
        },
    )
    assert bad_login.status_code == 401

