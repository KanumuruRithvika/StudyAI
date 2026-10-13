from unittest.mock import patch

import pytest

from agents.quiz import generate_quiz


class FakeLLM:
    def invoke(self, prompt):
        return """
        {
            "questions": [
                {
                    "id": "q1",
                    "question": "What is a Python function?",
                    "options": [
                        "A reusable block of code",
                        "A database",
                        "A loop only",
                        "A variable"
                    ],
                    "correct_answer": "A reusable block of code",
                    "explanation": "A function is a reusable block of code."
                },
                {
                    "id": "q2",
                    "question": "Which keyword defines a function?",
                    "options": [
                        "def",
                        "function",
                        "func",
                        "define"
                    ],
                    "correct_answer": "def",
                    "explanation": "Python uses the def keyword."
                },
                {
                    "id": "q3",
                    "question": "What is a parameter?",
                    "options": [
                        "A value accepted by a function",
                        "A Python file",
                        "A loop",
                        "An error"
                    ],
                    "correct_answer": "A value accepted by a function",
                    "explanation": "Parameters allow functions to receive values."
                },
                {
                    "id": "q4",
                    "question": "Which statement returns a value?",
                    "options": [
                        "return",
                        "yield_only",
                        "send",
                        "output"
                    ],
                    "correct_answer": "return",
                    "explanation": "The return statement sends a value back from a function."
                },
                {
                    "id": "q5",
                    "question": "Why are functions useful?",
                    "options": [
                        "They support code reuse",
                        "They remove all variables",
                        "They replace Python",
                        "They prevent execution"
                    ],
                    "correct_answer": "They support code reuse",
                    "explanation": "Functions allow logic to be reused."
                }
            ]
        }
        """


def create_state():
    return {
        "current_topic": "Python Functions",
        "current_level": "beginner",
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
    }


def test_quiz_generation():
    state = create_state()

    with patch(
        "agents.quiz.get_llm",
        return_value=FakeLLM(),
    ):
        result = generate_quiz(state)

    assert "quiz" in result
    assert len(result["quiz"]) == 5

    for question in result["quiz"]:
        assert question["id"]
        assert question["question"]
        assert len(question["options"]) == 4
        assert question["correct_answer"]
        assert question["correct_answer"] in question["options"]
        assert question["explanation"]


def test_quiz_contains_unique_question_ids():
    state = create_state()

    with patch(
        "agents.quiz.get_llm",
        return_value=FakeLLM(),
    ):
        result = generate_quiz(state)

    question_ids = [
        question["id"]
        for question in result["quiz"]
    ]

    assert len(question_ids) == len(set(question_ids))


def test_quiz_generation_rejects_wrong_question_count():
    class InvalidLLM:
        def invoke(self, prompt):
            return """
            {
                "questions": [
                    {
                        "id": "q1",
                        "question": "Question",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    }
                ]
            }
            """

    state = create_state()

    with patch(
        "agents.quiz.get_llm",
        return_value=InvalidLLM(),
    ):
        with pytest.raises(
            ValueError,
            match="Quiz must contain exactly 5 questions",
        ):
            generate_quiz(state)


def test_quiz_generation_rejects_wrong_option_count():
    class InvalidLLM:
        def invoke(self, prompt):
            return """
            {
                "questions": [
                    {
                        "id": "q1",
                        "question": "Question 1",
                        "options": ["A", "B", "C"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    },
                    {
                        "id": "q2",
                        "question": "Question 2",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    },
                    {
                        "id": "q3",
                        "question": "Question 3",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    },
                    {
                        "id": "q4",
                        "question": "Question 4",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    },
                    {
                        "id": "q5",
                        "question": "Question 5",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    }
                ]
            }
            """

    state = create_state()

    with patch(
        "agents.quiz.get_llm",
        return_value=InvalidLLM(),
    ):
        with pytest.raises(
            ValueError,
            match="must contain exactly 4 options",
        ):
            generate_quiz(state)


def test_quiz_generation_rejects_invalid_correct_answer():
    class InvalidLLM:
        def invoke(self, prompt):
            return """
            {
                "questions": [
                    {
                        "id": "q1",
                        "question": "Question 1",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "X",
                        "explanation": "Invalid."
                    },
                    {
                        "id": "q2",
                        "question": "Question 2",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    },
                    {
                        "id": "q3",
                        "question": "Question 3",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    },
                    {
                        "id": "q4",
                        "question": "Question 4",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    },
                    {
                        "id": "q5",
                        "question": "Question 5",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A",
                        "explanation": "Correct."
                    }
                ]
            }
            """

    state = create_state()

    with patch(
        "agents.quiz.get_llm",
        return_value=InvalidLLM(),
    ):
        with pytest.raises(
            ValueError,
            match="must match one of the options",
        ):
            generate_quiz(state)