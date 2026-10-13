from models.state import LearningState


def classify_score(score: float) -> str:
    """Classify quiz performance using the system's performance thresholds."""
    if score >= 80:
        return "strong"

    if score >= 60:
        return "medium"

    return "weak"


def build_topic_performance(
    existing_performance: dict,
    topic: str,
    score: float,
    correct: int,
    total: int,
    performance: str,
) -> dict:
    """Update performance history for the current topic."""
    topic_performance = dict(existing_performance)

    topic_performance[topic] = {
        "score": score,
        "correct": correct,
        "total": total,
        "performance": performance,
    }

    return topic_performance


def categorize_topics(
    topic_performance: dict,
) -> tuple[list[str], list[str], list[str]]:
    """Separate topics into strong, medium, and weak groups."""
    strong_topics = []
    medium_topics = []
    weak_topics = []

    for topic, result in topic_performance.items():
        performance = result.get("performance")

        if performance == "strong":
            strong_topics.append(topic)
        elif performance == "medium":
            medium_topics.append(topic)
        elif performance == "weak":
            weak_topics.append(topic)

    return strong_topics, medium_topics, weak_topics


import re


def normalize_str(s) -> str:
    if s is None:
        return ""
    return str(s).replace("\r\n", "\n").replace("\r", "\n").strip()


def strip_option_prefix(s: str) -> str:
    text = normalize_str(s)
    cleaned = re.sub(
        r"^(?:option\s+)?(?:\(?([A-Da-d0-9])\)?[\.\:\)\-]\s*|\(?([A-Da-d0-9])\)\s*)",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def extract_option_text(opt) -> str:
    if isinstance(opt, dict):
        return str(opt.get("text") or opt.get("label") or opt.get("value") or "")
    return str(opt) if opt is not None else ""


def get_option_index(value: str, options: list) -> int | None:
    if value is None or not options:
        return None
    val_str = normalize_str(value)
    val_clean = strip_option_prefix(val_str).lower()

    letter_match = re.match(r"^(?:option\s+)?([A-Da-d])$", val_str, re.IGNORECASE)
    if letter_match:
        letter = letter_match.group(1).upper()
        idx = ord(letter) - ord("A")
        if 0 <= idx < len(options):
            return idx

    if val_str.isdigit():
        idx = int(val_str)
        if 0 <= idx < len(options):
            return idx

    for i, opt in enumerate(options):
        opt_text = extract_option_text(opt)
        opt_str = normalize_str(opt_text)
        opt_clean = strip_option_prefix(opt_str).lower()
        if (
            val_clean == opt_clean
            or val_str.lower() == opt_str.lower()
            or val_clean == opt_str.lower()
        ):
            return i

    return None


def is_answer_correct(user_answer, question: dict) -> bool:
    if user_answer is None:
        return False

    correct_answer = question.get("correct_answer")
    if correct_answer is None:
        return False

    # Direct exact match (e.g. unit tests with "A" == "A")
    if user_answer == correct_answer:
        return True

    # Normalized case-insensitive match
    u_norm = normalize_str(user_answer)
    c_norm = normalize_str(correct_answer)
    if u_norm.lower() == c_norm.lower():
        return True

    # Prefix-stripped match (e.g. "A) Def" vs "Def")
    u_clean = strip_option_prefix(u_norm).lower()
    c_clean = strip_option_prefix(c_norm).lower()
    if u_clean and c_clean and u_clean == c_clean:
        return True

    # Option index match (e.g. user selected "Def", correct_answer is "A", or vice versa)
    options = question.get("options", [])
    if options:
        u_idx = get_option_index(user_answer, options)
        c_idx = get_option_index(correct_answer, options)
        if u_idx is not None and c_idx is not None and u_idx == c_idx:
            return True

    return False


def build_improvement_points(
    quiz: list[dict],
    answers: dict[str, str],
    current_topic: str,
) -> list[dict]:
    """
    Identify concepts that need review from incorrectly answered questions.

    These points provide remediation context. The actual decision to
    remediate is handled separately by the adaptation agent.
    """
    improvement_points = []

    for question in quiz:
        question_id = question["id"]
        user_answer = answers.get(question_id)

        if is_answer_correct(user_answer, question):
            continue

        question_topic = question.get("topic") or current_topic

        improvement_points.append({
            "topic": question_topic,
            "question": question["question"],
            "correct_answer": question["correct_answer"],
            "explanation": question.get("explanation", ""),
        })

    return improvement_points


def build_improvement_description(
    improvement_points: list[dict],
) -> str:
    """Convert incorrect-answer details into readable remediation guidance."""
    if not improvement_points:
        return ""

    return "\n".join(
        (
            f"- {item['topic']}: "
            f"Review the concept tested by "
            f"'{item['question']}'. "
            f"Correct answer: {item['correct_answer']}. "
            f"{item['explanation']}"
        )
        for item in improvement_points
    )


def evaluate_quiz(state: LearningState) -> dict:
    """Evaluate the submitted quiz and update learning performance."""
    quiz = state.get("quiz", [])
    quiz_answers = state.get("quiz_answers", [])

    if not quiz:
        raise ValueError("No quiz available for evaluation.")

    question_ids = {
        question["id"]
        for question in quiz
    }

    answers = {
        answer["question_id"]: answer["answer"]
        for answer in quiz_answers
    }

    if len(answers) != len(quiz_answers):
        raise ValueError(
            "Each quiz question can only be answered once."
        )

    invalid_ids = set(answers) - question_ids

    if invalid_ids:
        raise ValueError(
            "Quiz answers contain invalid question IDs."
        )

    correct = sum(
        is_answer_correct(answers.get(question["id"]), question)
        for question in quiz
    )

    total = len(quiz)
    score = round((correct / total) * 100, 2)
    performance = classify_score(score)

    topic = state.get("current_topic", "Unknown topic")

    topic_performance = build_topic_performance(
        existing_performance=state.get(
            "topic_performance",
            {},
        ),
        topic=topic,
        score=score,
        correct=correct,
        total=total,
        performance=performance,
    )

    strong_topics, medium_topics, weak_topics = categorize_topics(
        topic_performance
    )

    improvement_points = build_improvement_points(
        quiz=quiz,
        answers=answers,
        current_topic=topic,
    )

    improvement_description = build_improvement_description(
        improvement_points
    )

    quiz_history = list(
        state.get("quiz_history", [])
    )

    quiz_history.append({
        "topic": topic,
        "score": score,
        "correct": correct,
        "total": total,
    })

    learning_history = list(
        state.get("learning_history", [])
    )

    learning_history.append({
        "topic": topic,
        "score": score,
        "correct": correct,
        "total": total,
        "performance": performance,
    })

    return {
        "quiz_score": score,
        "correct_answers": correct,
        "correct": correct,
        "total_questions": total,
        "total": total,
        "strong_topics": strong_topics,
        "medium_topics": medium_topics,
        "weak_topics": weak_topics,
        "topic_performance": topic_performance,
        "quiz_history": quiz_history,
        "learning_history": learning_history,
        "improvement_description": improvement_description,
        "improvement_days": 1,
        "improvement_time_minutes": state.get(
            "available_time_minutes",
            60,
        ),
    }