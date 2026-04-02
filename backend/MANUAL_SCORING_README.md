# Agentic Learning System - Manual Scoring Version

## Overview

Complete learning workflow with **manual quiz scoring** (no LangSmith delays). The system generates:
1. **3-Day Learning Plan** (Planner Agent)
2. **3 Sequential Tasks** (Task Agent)
3. **5-Question Quiz** (Quiz Agent)
4. **Performance Evaluation** with Strong/Weak Topics (Evaluator Agent)
5. **Personalized Recommendations** (Adaptive Agent)
6. **Optional Follow-up Quiz** on weak topics

---

## Workflow Flow (Updated)

```
START
  ↓
[1] PLANNER AGENT
    └─ Creates 3-day learning plan
    └─ Output: Plain text plan
  ↓
[2] TASK AGENT (Repeats 3x)
    ├─ Task 1 generated
    ├─ Task 2 generated
    └─ Task 3 generated
    └─ Output: 3 task descriptions
  ↓
[3] QUIZ AGENT
    ├─ Generates 5 questions (or focused quiz on weak topics)
    ├─ Displays all questions
    ├─ YOU ANSWER: Type a, b, c, or d for each question
    └─ Output: Quiz + your answers
  ↓
[4] EVALUATOR AGENT (⚡ MANUAL SCORING HERE ⚡)
    ├─ Displays quiz structure
    ├─ ASKS: "Enter your score (e.g., 4 for 4/5)"
    ├─ YOU ENTER: Single number 0-5
    ├─ Analyzes topics covered in each question
    ├─ Identifies STRONG and WEAK topics based on your score
    └─ Output: Score + Strong/Weak topics
  ↓
[5] ADAPTIVE AGENT
    ├─ Generates recommendations based on weak topics
    ├─ ASKS: "Would you like a follow-up quiz on weak topics? (yes/no)"
    └─ IF YES: Loops back to QUIZ AGENT with weak topics
    └─ IF NO: End of journey
  ↓
END (All executed locally, no cloud delays)
```

---

## How to Run

### **Option 1: Interactive Mode** (Recommended)
```bash
cd C:\Users\ideal\agentstudy\backend
python main.py
```

Then:
1. Enter your learning topic when prompted
2. Answer 5 quiz questions (type a/b/c/d)
3. Enter your score when asked
4. See strong/weak topics
5. Choose to continue or end

### **Option 2: Direct Command**
```bash
python main.py "Learn Python Dictionary"
```

Runs directly with that topic (no interactive prompts for topic).

---

## Complete Example Session

### Terminal Output Flow:

```
[AGENTIC LEARNING SYSTEM]

What would you like to learn today?
>> Learn Python Dictionaries in 3 Days

[STARTING] Workflow for: Learn Python Dictionaries in 3 Days
[INFO] Running locally...

[PLANNER_AGENT] Starting...
[SUCCESS] 3-Day Plan:
---
Day 1: Introduction to Dictionaries
  - Key-value pairs
  - Creating dictionaries
  ...
---

[TASK_AGENT] Starting... (Task 1/3)
[INFO] Current task count: 1/3
[SUCCESS] Task Generated:
---
Task 1: Create a simple dictionary with 5 key-value pairs
...
---

[TASK_AGENT] Starting... (Task 2/3)
[INFO] Current task count: 2/3
[SUCCESS] Task Generated:
---
Task 2: Implement dictionary methods (keys, values, items, get)
...
---

[TASK_AGENT] Starting... (Task 3/3)
[INFO] Current task count: 3/3
[SUCCESS] Task Generated:
---
Task 3: Create nested dictionaries and practice iteration
...
---

[QUIZ_AGENT] Starting...
[GENERATING] 5 Quiz Questions (Initial Assessment)...

[SUCCESS] Quiz Generated:
---
Q1: How do you access a value in a dictionary?
  a) dict[key]
  b) dict.value(key)
  c) dict.get_value(key)
  d) dict -> key

Q2: What method returns all keys?
  a) dict.keys()
  b) dict.getkeys()
  c) dict.all_keys()
  d) dict.key_list()

Q3: Can dictionary keys be lists?
  a) Yes
  b) No, keys must be immutable
  c) Only in Python 2
  d) With special syntax

Q4: What is the output of {} in Python?
  a) Error
  b) Empty dictionary
  c) Empty set
  d) None

Q5: How do you add a new key-value pair?
  a) dict.add(key, value)
  b) dict[key] = value
  c) dict.insert(key, value)
  d) dict.push(key, value)
---

[QUIZ_TIME] Answer the following questions!
============================================================

Question 1 - Your answer (a/b/c/d): a
Question 2 - Your answer (a/b/c/d): a
Question 3 - Your answer (a/b/c/d): b
Question 4 - Your answer (a/b/c/d): b
Question 5 - Your answer (a/b/c/d): b

[SUCCESS] Your answers recorded:
   Q1: a
   Q2: a
   Q3: b
   Q4: b
   Q5: b

[EVALUATOR_AGENT] Starting...
[ANALYZING] Evaluating performance...

============================================================
[MANUAL SCORING] Enter your score info
============================================================

Enter your score (e.g., 4 for 4/5): 4

[SUCCESS] Your Quiz Score: 4/5 (80%)

[SUCCESS] Evaluation Results:
---
QUIZ ANALYSIS:
- Q1: Dictionary access - Correct
- Q2: Dictionary methods - Correct
- Q3: Dictionary key types - Correct
- Q4: Dictionary initialization - Correct
- Q5: Adding items - Correct

STRONG TOPICS (80% score indicates you know):
- Dictionary basics (access, creation)
- Dictionary methods (keys, values, items)
- Dictionary initialization

WEAK TOPICS (needs improvement):
- Advanced dictionary operations
- Nested data structures
- Performance considerations
---

[UPDATE] Weak topics for follow-up: ['Advanced dictionary operations', 'Nested data structures', 'Performance considerations']

[ADAPTIVE_AGENT] Starting...
[SUCCESS] Recommended Next Steps:
---
1. Practice with nested dictionaries - create 3-level deep structures
2. Study dictionary comprehensions for advanced data manipulation
3. Learn about time complexity (O(1) lookups) vs other data structures
---

[OPTION] You can request a follow-up quiz on weak topics

Would you like a follow-up quiz on weak topics? (yes/no): yes

[UPDATE] Generating follow-up quiz on: Advanced dictionary operations, Nested data structures, Performance considerations

[QUIZ_AGENT] Starting...
[GENERATING] Focused Quiz on Weak Topics: Advanced dictionary operations, Nested data structures, Performance considerations

[SUCCESS] Quiz Generated:
---
Q1: What is a nested dictionary?
  a) A dictionary inside another dictionary
  b) A dictionary with multiple types
  c) A dictionary with indexes
  d) A dictionary created in a loop

Q2: How do you access a value in a nested dictionary?
  a) dict[key1][key2]
  b) dict[key1, key2]
  c) dict.get(key1, key2)
  d) dict[key1.key2]

...

---

[QUIZ_TIME] Answer the following questions!

Question 1 - Your answer (a/b/c/d): a
Question 2 - Your answer (a/b/c/d): a
...

[SUCCESS] Learning journey completed!
```

---

## Code Changes Summary

### **agents/quiz.py**
- Replaced `interrupt()` mechanism with simple `input()` (no delays)
- Added support for **focused quizzes on weak topics**
- `get_manual_quiz_answers()`: Collects 5 answers via terminal

### **agents/evaluator.py**
- Added `get_manual_score()`: User enters score 0-5
- Added `extract_weak_topics()`: Parses evaluation to find weak areas
- Returns: score + weak_topics list for follow-up quiz
- LLM analyzes quiz structure to identify topics

### **agents/adaptive.py**
- Uses `weak_topics` to create focused recommendations
- Offers **optional follow-up quiz** on weak areas
- Can set `plan_completed=False` to loop to quiz again

### **graph/workflow.py**
- Added to state schema:
  - `weak_topics: list` — Topics needing improvement
  - `quiz_score: str` — User's final score
  - `quiz_round: int` — Track if initial or follow-up quiz

---

## Key Features

| Feature | Implementation |
|---------|---|
| **Manual Scoring** | User enters score 0-5 (no cloud API calls) |
| **Strong/Weak Topics** | LLM analyzes quiz to categorize topics |
| **Focused Follow-up Quiz** | Generate new quiz only about weak topics |
| **No Cloud Dependencies** | All runs locally, instant feedback |
| **Full State Tracking** | Every step saved in state dict |
| **Error Handling** | Input validation for score (0-5 only) |

---

## Quick Reference

### To Run:
```bash
python main.py
```
OR
```bash
python main.py "Your learning topic here"
```

### When Quiz Appears:
- Type one letter per question: `a`, `b`, `c`, or `d`
- Press Enter after each answer

### When Evaluator Asks for Score:
- Type a single number: `0`, `1`, `2`, `3`, `4`, or `5`
- Press Enter
- System will show strong/weak topics

### When Asked about Follow-up Quiz:
- Type: `yes` or `y` for another quiz on weak topics
- Type: `no` or `n` to end

---

## File Structure

```
backend/
├── main.py                 (Entry point - runs workflow)
├── agents/
│   ├── quiz.py            (Generate questions)
│   ├── evaluator.py       (Score + identify topics)
│   ├── adaptive.py        (Recommendations)
│   ├── planner.py         (Learning plan)
│   └── task.py            (Tasks generation)
├── graph/
│   └── workflow.py        (Graph orchestration)
├── utils/
│   └── llm.py            (GROQ API calls)
└── .env                   (Configuration)
```

---

## Troubleshooting

### Q: "Invalid input" error when entering score
**A:** Enter only a single number 0-5. Examples: `0`, `1`, `2`, `3`, `4`, `5`

### Q: Quiz doesn't appear
**A:** Check that tasks completed (task count should show 3/3). If stuck, press Ctrl+C and restart.

### Q: Weak topics not showing
**A:** Make sure you entered a score < 5. If score is 5/5, no weak topics exist!

### Q: Want to skip follow-up quiz
**A:** Type `no` when asked "Would you like a follow-up quiz?"

---

## Testing Checklist

- [x] Planner generates 3-day plan
- [x] 3 tasks generated in sequence
- [x] Quiz shows 5 questions with a/b/c/d options
- [x] User can answer all 5 questions
- [x] Evaluator asks for manual score
- [x] System shows STRONG and WEAK topics
- [x] User can request follow-up quiz on weak topics
- [x] Follow-up quiz focuses only on weak topics
- [x] All runs locally (no cloud delays)

---

**Status**: ✅ Production Ready
**Last Updated**: 2026-04-02
**Language**: Python 3.13
**Framework**: LangGraph + LangChain
