from models.schemas import Quiz
from models.state import LearningState
from utils.llm import get_llm
from utils.parser import parse_json_response


def build_quiz_prompt(state: LearningState) -> str:
    topic = state.get("current_topic", "")

    topic_data = next(
        (
            item
            for item in state.get("plan", {}).get("topics", [])
            if item.get("title") == topic
        ),
        {},
    )

    objectives = topic_data.get("objectives", [])
    weak_topics = state.get("weak_topics", [])

    if state.get("adaptive_action") == "improve_weak_topics" and weak_topics:
        focus_title = f"{topic} (Remediation: {', '.join(weak_topics)})"
        objectives_text = f"Weak topic areas to evaluate for remediation:\n" + chr(10).join(f"- {w}" for w in weak_topics)
    else:
        focus_title = topic
        objectives_text = "Topic objectives:\n" + chr(10).join(f"- {objective}" for objective in objectives)

    return f"""
Create a short assessment for the current learning topic.

Topic:
{focus_title}

{objectives_text}

Learner level:
{state.get("current_level", "beginner")}

Create exactly 5 multiple-choice questions.

Question distribution:
- 2 conceptual questions
- 1 scenario-based question
- 1 practical application question
- 1 problem-solving question

Rules:
- Every question must have exactly 4 options.
- There must be exactly one correct answer.
- Questions must test understanding, not simple memorization.
- Match the learner's current level.
- Questions must be based only on the current topic and objectives.
- Do not test unrelated topics.
- Avoid duplicate questions or repeated answer patterns.
- Include a concise explanation for the correct answer.
- The correct answer must exactly match one option.
- Use question_type values exactly as:
  "conceptual", "scenario", "application", or "code".
- Use "code" only when the topic genuinely requires code.
- Return only valid JSON.

JSON format:

{{
    "questions": [
        {{
            "id": "q1",
            "question": "Question text",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "correct_answer": "Option A",
            "explanation": "Why this answer is correct",
            "question_type": "conceptual",
            "topic": "{topic}"
        }}
    ]
}}
""".strip()


def generate_quiz(state: LearningState) -> dict:
    """Generate and validate a five-question topic quiz."""
    response = get_llm().invoke(
        build_quiz_prompt(state)
    )

    data = parse_json_response(response)
    quiz = Quiz.model_validate(data)

    if len(quiz.questions) != 5:
        raise ValueError(
            "Quiz must contain exactly 5 questions."
        )

    question_ids = set()

    for question in quiz.questions:
        if question.id in question_ids:
            raise ValueError(
                f"Duplicate quiz question ID: {question.id}"
            )

        question_ids.add(question.id)

        if len(question.options) != 4:
            raise ValueError(
                f"Question '{question.id}' must contain exactly 4 options."
            )

        if len(set(question.options)) != 4:
            raise ValueError(
                f"Question '{question.id}' contains duplicate options."
            )

        if question.correct_answer not in question.options:
            raise ValueError(
                f"Correct answer for '{question.id}' "
                "must match one of the options."
            )

    return {
        "quiz": [
            question.model_dump()
            for question in quiz.questions
        ]
    }