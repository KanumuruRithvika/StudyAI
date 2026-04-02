# STATIC QUIZ DATABASE - Hardcoded questions
STATIC_QUIZ_INITIAL = """Q1: What is the primary advantage of using functions in programming?
  a) Functions take more memory
  b) Code reusability and organization
  c) Functions are slower
  d) No advantage

Q2: What does a variable store in programming?
  a) Only numbers
  b) A memory location containing data
  c) Only text
  d) Functions

Q3: How do loops improve code efficiency?
  a) They slow down execution
  b) Eliminate the need for functions
  c) Repeat code blocks without rewriting
  d) They increase memory usage

Q4: What is an algorithm?
  a) A computer brand
  b) A step-by-step procedure to solve a problem
  c) A type of variable
  d) A programming language

Q5: What is the purpose of conditional statements (if/else)?
  a) To loop through data
  b) Make decisions based on conditions
  c) Store data in memory
  d) Create functions"""

STATIC_QUIZ_WEAK_TOPICS = """Q1: What is the difference between break and continue in loops?
  a) No difference
  b) break exits loop, continue skips iteration
  c) continue exits loop, break skips iteration
  d) Both do the same thing

Q2: How do you handle errors in programming?
  a) Ignore them
  b) Use try-except or try-catch blocks
  c) Errors cannot be handled
  d) Delete the code

Q3: What is the scope of a variable?
  a) The color of the variable
  b) Where the variable can be accessed
  c) The size of the variable
  d) No importance

Q4: What is recursion?
  a) A function calling itself with a base case
  b) A type of loop
  c) An error in code
  d) A way to store data

Q5: What is the difference between == and = in programming?
  a) No difference
  b) == compares, = assigns
  c) = compares, == assigns
  d) Both are assignment operators"""

def quiz_agent(state):
    """Automatic quiz agent - no user input needed"""
    print("\n[QUIZ_AGENT] Starting...")
    current_day = state.get("current_day", 1)
    weak_topics = state.get("weak_topics", [])
    
    print(f"[INFO] Day {current_day} Quiz")
    
    # Select quiz based on weak topics
    if weak_topics and len(weak_topics) > 0:
        print(f"[GENERATING] Focused Quiz on Weak Topics: {', '.join(weak_topics)}")
        quiz_text = STATIC_QUIZ_WEAK_TOPICS
    else:
        print(f"[GENERATING] Initial Assessment Quiz")
        quiz_text = STATIC_QUIZ_INITIAL
    
    print(f"[SUCCESS] Quiz Loaded:\n")
    print(f"---")
    print(quiz_text)
    print(f"---\n")
    
    # AUTO-GENERATE ANSWERS (no user input)
    user_answers = generate_automatic_answers(quiz_text)
    
    print(f"\n[AUTO_ANSWERS] Generated answers:")
    for i, answer in enumerate(user_answers, 1):
        print(f"   Q{i}: {answer}")
    
    print(f"[UPDATE] quiz_answers: {user_answers}")

    return {
        "quiz": quiz_text,
        "quiz_answers": user_answers
    }

def generate_automatic_answers(quiz_text):
    """Generate demo answers automatically based on quiz content"""
    # Demo answer pattern: Mix of correct and some incorrect
    # This simulates a realistic learner (not perfect, but learning)
    
    answer_patterns = {
        "INITIAL": ['b', 'b', 'c', 'b', 'b'],  # 5/5 on fundamentals
        "WEAK": ['b', 'b', 'b', 'a', 'b']       # 5/5 on weak topics (learned!)
    }
    
    # Detect which quiz this is
    if "break" in quiz_text.lower() and "continue" in quiz_text.lower():
        return answer_patterns["WEAK"]
    else:
        return answer_patterns["INITIAL"]

def get_manual_quiz_answers():
    """DEPRECATED - Now using auto-generated answers"""
    pass
