import pytest

from agents.evaluator import evaluate_quiz


def create_quiz():
    return [
        {
            "id": "q1",
            "question": "Question 1",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "A is correct.",
        },
        {
            "id": "q2",
            "question": "Question 2",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "B",
            "explanation": "B is correct.",
        },
        {
            "id": "q3",
            "question": "Question 3",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "C",
            "explanation": "C is correct.",
        },
        {
            "id": "q4",
            "question": "Question 4",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "D",
            "explanation": "D is correct.",
        },
        {
            "id": "q5",
            "question": "Question 5",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "A is correct.",
        },
    ]


def create_answers():
    return [
        {"question_id": "q1", "answer": "A"},
        {"question_id": "q2", "answer": "B"},
        {"question_id": "q3", "answer": "C"},
        {"question_id": "q4", "answer": "D"},
        {"question_id": "q5", "answer": "A"},
    ]


def test_perfect_quiz_score():
    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": create_answers(),
    }

    result = evaluate_quiz(state)

    assert result["quiz_score"] == 100.0
    assert result["strong_topics"] == ["Python Functions"]
    assert result["medium_topics"] == []
    assert result["weak_topics"] == []


def test_medium_quiz_score():
    answers = create_answers()
    answers[2]["answer"] = "X"
    answers[3]["answer"] = "X"

    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": answers,
    }

    result = evaluate_quiz(state)

    assert result["quiz_score"] == 60.0
    assert result["strong_topics"] == []
    assert result["medium_topics"] == ["Python Functions"]
    assert result["weak_topics"] == []


def test_weak_quiz_score():
    answers = create_answers()
    answers[0]["answer"] = "X"
    answers[1]["answer"] = "X"
    answers[2]["answer"] = "X"

    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": answers,
    }

    result = evaluate_quiz(state)

    assert result["quiz_score"] == 40.0
    assert result["strong_topics"] == []
    assert result["medium_topics"] == []
    assert result["weak_topics"] == ["Python Functions"]


def test_quiz_score_is_deterministic():
    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": [
            {"question_id": "q1", "answer": "A"},
            {"question_id": "q2", "answer": "B"},
            {"question_id": "q3", "answer": "X"},
            {"question_id": "q4", "answer": "X"},
            {"question_id": "q5", "answer": "X"},
        ],
    }

    first_result = evaluate_quiz(state)
    second_result = evaluate_quiz(state)

    assert first_result["quiz_score"] == 40.0
    assert second_result["quiz_score"] == 40.0
    assert (
        first_result["topic_performance"]
        == second_result["topic_performance"]
    )


def test_learning_history_records_topic_result():
    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": create_answers(),
        "learning_history": [],
    }

    result = evaluate_quiz(state)

    assert len(result["learning_history"]) == 1

    history = result["learning_history"][0]

    assert history["topic"] == "Python Functions"
    assert history["score"] == 100.0
    assert history["correct"] == 5
    assert history["total"] == 5
    assert history["performance"] == "strong"


def test_existing_topic_performance_is_preserved():
    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": create_answers(),
        "topic_performance": {
            "Python Basics": {
                "score": 80.0,
                "correct": 4,
                "total": 5,
                "performance": "strong",
            }
        },
    }

    result = evaluate_quiz(state)

    assert "Python Basics" in result["topic_performance"]
    assert "Python Functions" in result["topic_performance"]

    assert result["strong_topics"] == [
        "Python Basics",
        "Python Functions",
    ]


def test_duplicate_quiz_answers_are_rejected():
    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": [
            {"question_id": "q1", "answer": "A"},
            {"question_id": "q1", "answer": "B"},
            {"question_id": "q2", "answer": "B"},
            {"question_id": "q3", "answer": "C"},
            {"question_id": "q4", "answer": "D"},
        ],
    }

    with pytest.raises(
        ValueError,
        match="Each quiz question can only be answered once.",
    ):
        evaluate_quiz(state)


def test_invalid_question_id_is_rejected():
    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": [
            {"question_id": "q1", "answer": "A"},
            {"question_id": "q2", "answer": "B"},
            {"question_id": "q3", "answer": "C"},
            {"question_id": "q4", "answer": "D"},
            {"question_id": "q99", "answer": "A"},
        ],
    }

    with pytest.raises(
        ValueError,
        match="Quiz answers contain invalid question IDs.",
    ):
        evaluate_quiz(state)


def test_missing_answers_are_counted_as_incorrect():
    state = {
        "current_topic": "Python Functions",
        "quiz": create_quiz(),
        "quiz_answers": [
            {"question_id": "q1", "answer": "A"},
            {"question_id": "q2", "answer": "B"},
        ],
    }

    result = evaluate_quiz(state)

    assert result["quiz_score"] == 40.0
    assert (
        result["topic_performance"]["Python Functions"]["correct"]
        == 2
    )


def test_evaluator_handles_text_and_letter_matching():
    quiz = [
        {
            "id": "q1",
            "question": "What keyword defines a function?",
            "options": ["def", "function", "func", "define"],
            "correct_answer": "def",
        },
        {
            "id": "q2",
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "correct_answer": "4",
        },
        {
            "id": "q3",
            "question": "Which is mutable?",
            "options": ["tuple", "list", "int", "str"],
            "correct_answer": "B",  # letter in correct_answer
        },
    ]

    # User answers:
    # q1: user sent option letter "A" while correct_answer was "def"
    # q2: user sent option text with prefix "B) 4" while correct_answer was "4"
    # q3: user sent option text "list" while correct_answer was "B"
    state = {
        "current_topic": "Python Basics",
        "quiz": quiz,
        "quiz_answers": [
            {"question_id": "q1", "answer": "A"},
            {"question_id": "q2", "answer": "B) 4"},
            {"question_id": "q3", "answer": "list"},
        ],
    }

    result = evaluate_quiz(state)

    assert result["quiz_score"] == 100.0
    assert result["correct_answers"] == 3
    assert result["total_questions"] == 3