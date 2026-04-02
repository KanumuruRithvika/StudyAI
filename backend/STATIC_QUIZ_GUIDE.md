# Static Quiz - Complete Guide

## What's New ✨

Your system now uses **hardcoded static quiz questions** that run completely in **LangSmith Cloud**:

- **No LLM API calls** for quiz generation (faster!)
- **Hardcoded 10 questions** (5 initial + 5 weak topics)
- **Complete interactive input** shown in LangSmith traces
- **Full workflow visibility** in cloud dashboard

---

## The Static Quizzes

### Quiz 1: Initial Assessment (Default)
5 questions testing:
1. Functions and Reusability
2. Variables and Memory
3. Loops and Iteration
4. Algorithms and Problem Solving
5. Control Flow Decisions

### Quiz 2: Weak Topics (Follow-up)
5 questions testing:
1. Loop Control (break/continue)
2. Error Handling
3. Variable Scope
4. Recursion
5. Operators (== vs =)

---

## Workflow Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  YOU: Input learning goal                                       │
│  "Learn Python in 3 Days"                                       │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  [PLANNER_AGENT] Generates 3-day learning plan                  │
│  ✅ Traced in LangSmith                                         │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  [TASK_AGENT] x3 - Generates 3 sequential tasks                 │
│  ✅ Each task traced in LangSmith                               │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  [QUIZ_AGENT] Shows STATIC Quiz (5 questions a/b/c/d)           │
│  YOU: Answer each question (a/b/c/d)                            │
│  ✅ Your answers recorded in LangSmith trace                    │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  [EVALUATOR_AGENT] Asks for your score                          │
│  YOU: Enter score (e.g., 4 for 4/5)                             │
│  ✅ Score and evaluation recorded in LangSmith                  │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│  [ADAPTIVE_AGENT] Recommendations + Follow-up option            │
│  YOU: Enter yes/no for follow-up quiz                           │
│  ✅ Decision recorded in LangSmith trace                        │
└────────────────────┬────────────────────────────────────────────┘
                     ↓
        ┌────────────────────────┐
        │   Follow-up quiz?      │
        │   yes    or    no      │
        └────────────────────────┘
         ↓                      ↓
       YES                      NO
       ↓                        ↓
  [QUIZ_AGENT]              [END]
  (Weak topics)           Workflow
       ↓                  Complete
  [EVALUATOR_AGENT]
       ↓
  [ADAPTIVE_AGENT]
       ↓
     Loop back
```

---

## Running the System

### 1. Start Interactive Mode
```bash
python main.py
```

**What happens:**
```
========================================================================
AGENTIC LEARNING SYSTEM
========================================================================

What would you like to learn today?
>> Learn Python Dictionaries

[SUCCESS] LangSmith enabled and ready

========================================================================
[WORKFLOW EXECUTION]
========================================================================

[PLANNER_AGENT] Starting...
[SUCCESS] 3-Day Plan:
---
Day 1: Python Dictionaries Basics
  - Dictionary creation and access
  - Keys and values concepts

Day 2: Dictionary Operations
  - Adding and removing items
  - Dictionary methods

Day 3: Advanced Dictionary Patterns
  - Nested dictionaries
  - Dictionary comprehensions
---

[TASK_AGENT] Starting... (Task 1/3)
[SUCCESS] Task 1: Create a simple dictionary...

[TASK_AGENT] Starting... (Task 2/3)
[SUCCESS] Task 2: Access and modify dictionary...

[TASK_AGENT] Starting... (Task 3/3)
[SUCCESS] Task 3: Use dictionary methods...

[QUIZ_AGENT] Starting...
[GENERATING] 5 Quiz Questions (Initial Assessment)
[SUCCESS] Quiz Loaded:

---
Q1: What is the primary advantage of using functions in programming?
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
  d) Create functions
---

[QUIZ_TIME] Answer the following questions!
============================================================
... (questions repeated) ...
============================================================

Question 1 - Your answer (a/b/c/d): b
Question 2 - Your answer (a/b/c/d): b
Question 3 - Your answer (a/b/c/d): c
Question 4 - Your answer (a/b/c/d): b
Question 5 - Your answer (a/b/c/d): b

[SUCCESS] Your answers recorded:
   Q1: b
   Q2: b
   Q3: c
   Q4: b
   Q5: b

[EVALUATOR_AGENT] Starting...
[INPUT] Quiz answers received: ['b', 'b', 'c', 'b', 'b']
[ANALYZING] Evaluating performance...

============================================================
[MANUAL SCORING] Enter your score
============================================================

Enter your score (e.g., 4 for 4/5): 5

[SUCCESS] Your Quiz Score: 5/5 (100%)

[SUCCESS] Evaluation Results:
---
STRONG TOPICS (100% indicates understanding):
- Functions and Reusability
- Variables and Memory
- Loops and Iteration
- Algorithms and Problem Solving
- Control Flow Decisions

WEAK TOPICS (needs improvement):
- None

DETAILED ANALYSIS:
Perfect score! You have strong understanding of all topics.
---

[UPDATE] Weak topics identified: []

[ADAPTIVE_AGENT] Starting...
[SUCCESS] Recommended Next Steps:
---
1. Continue expanding your knowledge
2. Explore advanced concepts
3. Practice complex problem solving
---

[OPTION] You can request a follow-up quiz on weak topics

Would you like a follow-up quiz on weak topics? (yes/no): no

========================================================================
[WORKFLOW COMPLETED SUCCESSFULLY]
========================================================================

[RESULTS]
  Goal: Learn Python Dictionaries
  Final Score: 5/5
  Topics Weak: None remaining!

[LANGSMITH DASHBOARD]
  URL: https://smith.langchain.com/o/projects/p/agentic-learning
  Project: agentic-learning-system
  Status: All agent executions are traced

[OPENING] LangSmith Dashboard in browser...

[NEXT STEPS]
  1. Open the dashboard URL above
  2. Find your latest run (at the top)
  3. Click agents to explore:
     - Click PLANNER_AGENT to see generated plan
     - Click TASK_AGENT to see 3 tasks
     - Click QUIZ_AGENT to see questions + answers
     - Click EVALUATOR_AGENT to see score + topics
     - Click ADAPTIVE_AGENT to see recommendations
  4. View full trace of all interactions
```

### 2. With Specific Topic
```bash
python main.py "Learn Python Exception Handling"
```

### 3. Test LangSmith Only
```bash
python main.py --test-langsmith
```

---

## Viewing in LangSmith

### Step 1: Dashboard Opens Automatically
After workflow completes, your browser should open LangSmith dashboard.

### Step 2: Find Your Run
- Click "Runs" tab
- Your latest run is at the top
- Each run shows all 5 agents

### Step 3: Explore Agents

**Click QUIZ_AGENT to see:**
```
Input:
  weak_topics: []              (no weak topics yet)
  quiz_round: 1                (first quiz)

Processing:
  Question 1 - Your answer (a/b/c/d): b
  Question 2 - Your answer (a/b/c/d): b
  ...

Output:
  quiz: "Q1: ... Q5: ..."      (full quiz questions)
  quiz_answers: ['b', 'b', 'c', 'b', 'b']
  quiz_round: 2
```

**Click EVALUATOR_AGENT to see:**
```
Input:
  quiz_answers: ['b', 'b', 'c', 'b', 'b']
  quiz_round: 2

Processing:
  Enter your score (e.g., 4 for 4/5): 5

Output:
  evaluation: "STRONG TOPICS: ..."
  quiz_score: "5/5"
  weak_topics: []
```

**Click ADAPTIVE_AGENT to see:**
```
Input:
  weak_topics: []
  quiz_score: "5/5"

Processing:
  Would you like a follow-up quiz on weak topics? (yes/no): no

Output:
  plan_completed: True
  adapted_plan: "..."
```

---

## Key Features

✅ **Static Quizzes**
- 5 hardcoded initial assessment questions
- 5 hardcoded weak topics practice questions
- Instant, no LLM generation needed

✅ **Complete Input Tracking**
- All your answers visible in LangSmith
- All your scores recorded
- All decisions (yes/no follow-ups) logged

✅ **Cloud Tracing**
- Every agent call traced
- Input/output for each agent visible
- Full state at each step recorded

✅ **Fast Execution**
- No LLM API calls for quiz generation
- Instant quiz display
- Quicker overall loop

---

## Architecture

```
main.py
  ├─ LangSmith validated ✅
  ├─ LearningState initialized
  └─ graph.workflow.build_graph()
      └─ PLANNER_AGENT
      ├─ TASK_AGENT (loop 3x)
      ├─ QUIZ_AGENT → quiz.py
      │   ├─ STATIC_QUIZ_INITIAL (5 questions)
      │   └─ STATIC_QUIZ_WEAK_TOPICS (5 questions)
      ├─ EVALUATOR_AGENT → evaluator.py
      │   ├─ get_manual_score()
      │   └─ LLM analyzes topics
      └─ ADAPTIVE_AGENT
          └─ Loop back if weak topics exist
```

---

## Static Quiz Content

### Initial Assessment Questions (Default)

```
Q1: What is the primary advantage of using functions?
Q2: What does a variable store?
Q3: How do loops improve code efficiency?
Q4: What is an algorithm?
Q5: What is the purpose of conditional statements?
```

### Weak Topics Questions (Follow-up)

```
Q1: What is the difference between break and continue?
Q2: How do you handle errors?
Q3: What is the scope of a variable?
Q4: What is recursion?
Q5: What is the difference between == and =?
```

---

## Troubleshooting

### Issue: LangSmith not opening
**Solution**: Manually visit: `https://smith.langchain.com/o/projects/p/agentic-learning`

### Issue: Input not appearing in LangSmith
**Solution**: 
- Inputs are recorded when you do `input()` in terminal
- They appear in the agent's execution trace
- Wait for page to load fully

### Issue: Quiz doesn't show all 5 questions
**Solution**: 
- Scroll down in terminal to see all questions
- Or resize terminal window wider

### Issue: Static quizzes feel too generic
**Solution**: 
- Plan: You can modify `STATIC_QUIZ_INITIAL` and `STATIC_QUIZ_WEAK_TOPICS` in `agents/quiz.py`
- Topic-specific quizzes coming in next version

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python main.py` | Interactive mode - enter topic |
| `python main.py "Topic"` | Run with specific topic |
| `python main.py --test-langsmith` | Test LangSmith connection |
| `python test_setup.py` | Validate entire system |

---

## Summary

You now have a **complete, production-ready learning system** with:

✅ Static hardcoded quizzes (no generation delays)
✅ Complete input tracking in LangSmith
✅ Full workflow visibility in cloud
✅ Fast execution and instant feedback
✅ Professional documentation

**Start learning now:**
```bash
python main.py
```

Dashboard opens automatically after completion!
