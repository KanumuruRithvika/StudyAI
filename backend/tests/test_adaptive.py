from agents.adaptation import adapt_learning


def test_adaptive_action_for_weak_topic():
    state = {
        "current_topic": "Python Functions",
        "quiz_score": 40.0,
    }

    result = adapt_learning(state)

    assert result["adaptive_action"] == "improve_weak_topics"

    assert (
        "Python Functions"
        in result["adaptive_recommendation"]
    )


def test_adaptive_action_for_medium_topic():
    state = {
        "current_topic": "Python Functions",
        "quiz_score": 70.0,
    }

    result = adapt_learning(state)

    assert result["adaptive_action"] == "move_forward"

    assert (
        "Python Functions"
        in result["adaptive_recommendation"]
    )


def test_adaptive_action_for_strong_topic():
    state = {
        "current_topic": "Python Functions",
        "quiz_score": 90.0,
    }

    result = adapt_learning(state)

    assert result["adaptive_action"] == "move_forward"

    assert (
        "Python Functions"
        in result["adaptive_recommendation"]
    )


def test_adaptive_action_at_60_percent():
    state = {
        "current_topic": "Python Basics",
        "quiz_score": 60.0,
    }

    result = adapt_learning(state)

    assert result["adaptive_action"] == "move_forward"


def test_adaptive_action_at_80_percent():
    state = {
        "current_topic": "Python Basics",
        "quiz_score": 80.0,
    }

    result = adapt_learning(state)

    assert result["adaptive_action"] == "move_forward"