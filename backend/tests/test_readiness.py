from agents.readiness import generate_readiness_report


def test_general_readiness_report():
    state = {
        "learning_mode": "general",
        "goal": "Learn Python",
        "plan": {
            "topics": [
                {"title": "Python Basics"},
                {"title": "Python Functions"},
            ]
        },
        "topic_performance": {
            "Python Basics": {
                "score": 90,
                "correct": 9,
                "total": 10,
                "performance": "strong",
            },
            "Python Functions": {
                "score": 70,
                "correct": 7,
                "total": 10,
                "performance": "medium",
            },
        },
        "strong_topics": ["Python Basics"],
        "medium_topics": ["Python Functions"],
        "weak_topics": [],
        "goal_completed": True,
    }

    result = generate_readiness_report(state)
    report = result["readiness_report"]

    assert report["progress_percent"] == 100.0
    assert report["strong_topics"] == ["Python Basics"]
    assert report["medium_topics"] == ["Python Functions"]
    assert report["weak_topics"] == []
    assert report["skill_gaps"] == []
    assert report["recommendations"]
    assert report["report"]


def test_general_readiness_calculates_progress_from_completed_topics():
    state = {
        "learning_mode": "general",
        "goal": "Learn Python",
        "plan": {
            "topics": [
                {"title": "Python Basics"},
                {"title": "Python Functions"},
                {"title": "Python OOP"},
                {"title": "Python Testing"},
            ]
        },
        "topic_performance": {
            "Python Basics": {
                "score": 90,
                "correct": 9,
                "total": 10,
                "performance": "strong",
            },
            "Python Functions": {
                "score": 50,
                "correct": 5,
                "total": 10,
                "performance": "weak",
            },
        },
        "strong_topics": ["Python Basics"],
        "medium_topics": [],
        "weak_topics": ["Python Functions"],
        "goal_completed": False,
    }

    result = generate_readiness_report(state)
    report = result["readiness_report"]

    assert report["progress_percent"] == 50.0
    assert report["strong_topics"] == ["Python Basics"]
    assert report["weak_topics"] == ["Python Functions"]
    assert "Review weak topics" in report["recommendations"][0]


def test_project_readiness_includes_skill_gaps():
    state = {
        "learning_mode": "project",
        "goal": "Become a Backend Developer",
        "role": "Backend Developer",
        "project_name": "E-commerce Backend",
        "plan": {
            "topics": [
                {"title": "Spring Boot"},
                {"title": "PostgreSQL"},
            ]
        },
        "skill_gaps": [
            {
                "skill": "Spring Boot",
                "priority": "high",
                "status": "missing",
            },
            {
                "skill": "Redis",
                "priority": "medium",
                "status": "missing",
            },
        ],
        "topic_performance": {
            "Spring Boot": {
                "score": 80,
                "correct": 8,
                "total": 10,
                "performance": "strong",
            },
        },
        "strong_topics": ["Spring Boot"],
        "medium_topics": [],
        "weak_topics": [],
        "goal_completed": False,
    }

    result = generate_readiness_report(state)
    report = result["readiness_report"]

    assert report["progress_percent"] == 50.0
    assert report["skill_gaps"] == [
        "Spring Boot",
        "Redis",
    ]
    assert report["strong_topics"] == ["Spring Boot"]

    assert any(
        "remaining project skill gaps" in recommendation
        for recommendation in report["recommendations"]
    )

    assert "E-commerce Backend" in report["report"]
    assert "Backend Developer" in report["report"]
    assert "Spring Boot" in report["report"]
    assert "Redis" in report["report"]


def test_project_readiness_with_no_skill_gaps():
    state = {
        "learning_mode": "project",
        "goal": "Become a Backend Developer",
        "role": "Backend Developer",
        "project_name": "E-commerce Backend",
        "plan": {
            "topics": [
                {"title": "Spring Boot"},
            ]
        },
        "skill_gaps": [],
        "topic_performance": {
            "Spring Boot": {
                "score": 100,
                "correct": 5,
                "total": 5,
                "performance": "strong",
            },
        },
        "strong_topics": ["Spring Boot"],
        "medium_topics": [],
        "weak_topics": [],
        "goal_completed": True,
    }

    result = generate_readiness_report(state)
    report = result["readiness_report"]

    assert report["progress_percent"] == 100.0
    assert report["skill_gaps"] == []
    assert report["strong_topics"] == ["Spring Boot"]

    assert (
        "Continue to the next learning stage"
        not in report["recommendations"]
    )


def test_weak_and_medium_topics_generate_recommendations():
    state = {
        "learning_mode": "general",
        "goal": "Learn Machine Learning",
        "plan": {
            "topics": [
                {"title": "Python"},
                {"title": "Machine Learning"},
            ]
        },
        "topic_performance": {
            "Python": {
                "score": 70,
                "correct": 7,
                "total": 10,
                "performance": "medium",
            },
            "Machine Learning": {
                "score": 40,
                "correct": 4,
                "total": 10,
                "performance": "weak",
            },
        },
        "strong_topics": [],
        "medium_topics": ["Python"],
        "weak_topics": ["Machine Learning"],
        "goal_completed": False,
    }

    result = generate_readiness_report(state)

    recommendations = result["readiness_report"]["recommendations"]

    assert any(
        "weak topics" in recommendation
        for recommendation in recommendations
    )

    assert any(
        "medium-level topics" in recommendation
        for recommendation in recommendations
    )


def test_empty_plan_returns_zero_progress():
    state = {
        "learning_mode": "general",
        "goal": "Learn Python",
        "plan": {
            "topics": []
        },
        "topic_performance": {},
        "strong_topics": [],
        "medium_topics": [],
        "weak_topics": [],
        "goal_completed": False,
    }

    result = generate_readiness_report(state)
    report = result["readiness_report"]

    assert report["progress_percent"] == 0.0
    assert report["strong_topics"] == []
    assert report["medium_topics"] == []
    assert report["weak_topics"] == []
    assert report["skill_gaps"] == []
    assert report["recommendations"]
    assert report["report"]