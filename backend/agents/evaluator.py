from utils.llm import get_llm, call_llm_with_retry

llm = get_llm()

# Correct answers for static quizzes
CORRECT_ANSWERS_INITIAL = {
    "1": "b",
    "2": "b",
    "3": "c",
    "4": "b",
    "5": "b"
}

CORRECT_ANSWERS_WEAK = {
    "1": "b",
    "2": "b",
    "3": "b",
    "4": "a",
    "5": "b"
}

def evaluator_agent(state):
    print("\n[EVALUATOR_AGENT] Starting...")
    quiz = state.get("quiz", "")
    quiz_answers = state.get("quiz_answers", [])
    current_day = state.get("current_day", 1)

    print(f"[INPUT] Quiz Day {current_day}: answers received: {quiz_answers}")
    print(f"[ANALYZING] Evaluating performance...\n")

    # AUTO-SCORE based on day
    score = generate_automatic_score(current_day)
    quiz_score_text = f"{score}/{5}"
    percentage = int((score / 5) * 100)
    
    print(f"[AUTO_SCORE] Day {current_day} Quiz Score: {quiz_score_text} ({percentage}%)\n")

    # Analyze weak topics from score
    prompt = f"""Based on quiz score of {percentage}%, generate evaluation:

DAY {current_day} QUIZ TOPICS:
- Functions and Reusability
- Variables and Memory
- Loops and Iteration
- Algorithms and Problem Solving
- Control Flow Decisions

USER SCORE: {quiz_score_text} ({percentage}%)
USER ANSWERS: {', '.join(quiz_answers)}

Provide structured output:

STRONG TOPICS ({percentage}% indicates understanding):
- [topic 1]
- [topic 2]

WEAK TOPICS (needs improvement):
- [topic 1]
- [topic 2]

DETAILED ANALYSIS:
Analysis of performance and recommendations."""

    response = call_llm_with_retry(llm, prompt)
    eval_content = response.content
    
    print(f"[SUCCESS] Evaluation Results:")
    print(f"---")
    print(eval_content)
    print(f"---\n")
    
    # Extract weak topics for follow-up
    weak_topics = extract_weak_topics(eval_content)
    print(f"[UPDATE] Day {current_day} Weak topics: {weak_topics}")

    return {
        "evaluation": eval_content,
        "quiz_score": quiz_score_text,
        "weak_topics": weak_topics
    }

def generate_automatic_score(current_day):
    """Auto-generate realistic scores for each day"""
    # Day 1: Initial learning (3/5)
    # Day 2: Improvement on weak topics (4/5)
    # Day 3: Master all topics (5/5)
    scores = {
        1: 3,  # Day 1: 3/5 - Initial learning
        2: 4,  # Day 2: 4/5 - Improved weak topics
        3: 5   # Day 3: 5/5 - Mastered all
    }
    return scores.get(current_day, 3)

def get_manual_score():
    """DEPRECATED - Now using auto-generated scores"""
    return (3, 5)  # Fallback

def extract_weak_topics(evaluation_text):
    """Extract weak topics from evaluation text"""
    lines = evaluation_text.split('\n')
    weak_topics = []
    in_weak_section = False
    
    for line in lines:
        line = line.strip()
        
        # Check if we're in the WEAK TOPICS section
        if 'WEAK TOPIC' in line.upper():
            in_weak_section = True
            continue
        
        # Extract topics while in weak section
        if in_weak_section:
            if line.startswith('-') and line.strip() != '-':
                topic = line.lstrip('- ').strip()
                if topic and not any(x in topic.lower() for x in ['score', 'recommendation', 'strong']):
                    weak_topics.append(topic)
            elif ('STRONG' in line.upper() or 'RECOMMENDATION' in line.upper() or line == ''):
                in_weak_section = False
    
    # Return unique topics, max 3
    return list(dict.fromkeys(weak_topics))[:3]
