# Complete Agentic Learning System - Workflow Guide

## Overview

This is a **5-agent pipeline** that creates personalized learning plans, generates tasks, quizzes, and evaluates your progress with **human-in-the-loop** quiz participation.

---

## Complete Workflow Flow

```
START
  ↓
[1] PLANNER AGENT
    └─ Creates 3-day learning plan from your topic
    └─ Output: Learning plan → LangSmith
  ↓
[2] TASK AGENT (Loop 3x)
    ├─ Task 1: Generate first task
    ├─ Task 2: Generate second task  
    └─ Task 3: Generate third task
    └─ Output: All tasks → LangSmith
  ↓
[3] QUIZ AGENT  ⚡ HUMAN-IN-LOOP HERE ⚡
    ├─ Generates 5 multiple-choice questions
    ├─ Displays questions in Studio UI
    ├─ PAUSES: Waits for your answers
    ├─ You enter: a, b, c, or d for each question
    └─ Output: Questions + Your answers → LangSmith
  ↓
[4] EVALUATOR AGENT
    ├─ Scores your quiz (e.g., 4/5 = 80%)
    ├─ Identifies STRONG TOPICS (what you know)
    ├─ Identifies WEAK TOPICS (what to improve)
    └─ Output: Evaluation results → LangSmith
  ↓
[5] ADAPTIVE AGENT
    ├─ Recommends next learning steps
    ├─ Suggests focus areas based on weak topics
    └─ Output: Recommendations → LangSmith
  ↓
END (Full trace visible in LangSmith)
```

---

## How to Use (Step by Step)

### Step 1: Start LangGraph Dev Server

Open terminal and run:
```bash
cd C:\Users\ideal\agentstudy\backend
langgraph dev
```

**Expected Output:**
```
Graph loaded successfully
Listening on http://127.0.0.1:2024
```

### Step 2: Open Studio UI in Browser

Visit: **http://localhost:2024**

You should see:
- Graph visualization on the left (Planner → Task → Quiz → Evaluator → Adaptive)
- Input panel on the right
- State viewer at bottom

### Step 3: Start the Workflow

In the Studio UI, enter your learning topic:
```
"Learn Python in 3 Days"
```

Click **[START]** button

### Step 4: Watch the Planner Node

**What happens:**
- Planner agent generates a 3-day learning plan from your topic
- You see output in the **Planner node** (click it)
- Plan is stored in state

**In the UI:**
- Planner node turns **GREEN** (completed)
- Workflow automatically moves to Task node

### Step 5: Watch 3 Tasks Generate (Loop)

**What happens:**
```
Task 1 generates → Task node shows output → [INFO] Current task count: 1/3
Task 2 generates → Task node shows output → [INFO] Current task count: 2/3
Task 3 generates → Task node shows output → [INFO] Current task count: 3/3
```

**In the UI:**
- Task node loops 3 times
- Each iteration updates task_count in state
- After 3rd task → workflow moves to Quiz node

### Step 6: QUIZ NODE - Answer Questions

**Important:** This is where your interaction happens!

**What you see in Studio UI:**
- Quiz node becomes **PAUSED** (orange/yellow indicator)
- Right panel shows: `[INPUT REQUIRED]`
- Text input form appears with prompt:
  ```
  Question 1 - Enter your answer (a/b/c/d):
  ```

**What you do:**
1. Click the input field
2. Type your answer: `a` (or `b`, `c`, `d`)
3. Press **Enter**
4. UI moves to `Question 2 - Enter your answer...`
5. Repeat for all 5 questions

**Example:**
```
Question 1 - Enter your answer (a/b/c/d): a
Question 2 - Enter your answer (a/b/c/d): c
Question 3 - Enter your answer (a/b/c/d): b
Question 4 - Enter your answer (a/b/c/d): a
Question 5 - Enter your answer (a/b/c/d): d
```

1️⃣ **After you submit all 5 answers:**
- Quiz node turns GREEN
- Answers stored in state as: `["a", "c", "b", "a", "d"]`
- Workflow automatically moves to Evaluator node

### Step 7: Evaluator Node - See Results

**What happens:**
- Evaluator agent analyzes your answers
- Compares to correct answers
- Calculates **QUIZ SCORE**
- Identifies **STRONG TOPICS** (correct answers)
- Identifies **WEAK TOPICS** (incorrect answers)

**In Studio UI:**
- Click on **Evaluator node**
- Right panel shows:
  ```
  [SUCCESS] Quiz Evaluation:
  ---
  QUIZ SCORE: 4/5 (80%)
  
  STRONG TOPICS:
  - Python loops
  - Data structures
  - Functions
  
  WEAK TOPICS:
  - Exception handling
  ---
  ```

### Step 8: Adaptive Node - Next Steps

**What happens:**
- Adaptive agent recommends next learning steps
- Suggests which weak topics to focus on
- Creates new learning plan if needed

**In Studio UI:**
- Click on **Adaptive node**
- See recommendations between `---` markers

### Step 9: View Complete Trace in LangSmith

1. Open: **https://smith.langchain.com/o/projects/p/agentic-learning-system**
2. Find your latest run (at the top)
3. Click on it to open full trace
4. See the complete execution:
   - Each node's input/output
   - Your quiz answers
   - Evaluator's scoring
   - Strong/weak topics
   - Adaptive recommendations

---

## Data Flow Map

```
LangGraph Studio UI
    ↓
    ├─ You enter topic
    ↓
Agent Pipeline (sequential execution)
    ├─ Planner: topic → plan
    ├─ Task (1x): plan → task_1
    ├─ Task (2x): plan → task_2
    ├─ Task (3x): plan → task_3
    ├─ Quiz: plan + tasks → questions
    │   ⚡ PAUSES HERE for your input ⚡
    ├─ Evaluator: questions + your_answers → score + topics
    └─ Adaptive: score + weak_topics → recommendations
    ↓
State Dict (Updated after each node)
    ├─ goal: "Learn Python in 3 Days"
    ├─ plan: "Day 1: Variables and types..."
    ├─ tasks_list: ["Task 1: ...", "Task 2: ...", "Task 3: ..."]
    ├─ quiz: "Q1: What is...? a)... b)... c)... d)..."
    ├─ quiz_answers: ["a", "c", "b", "a", "d"]
    ├─ evaluation: "SCORE: 4/5, STRONG: loops/functions, WEAK: exceptions"
    └─ adapted_plan: "Focus on exception handling next..."
    ↓
LangSmith Cloud Trace
    └─ Complete record of all nodes + state changes
```

---

## What to Expect at Each Stage

| Node | Input | Process | Output | Time |
|------|-------|---------|--------|------|
| **Planner** | Your topic | LLM creates 3-day plan | 3-day plan text | 2-3s |
| **Task 1** | Plan | Generate 1st task | Task description | 2-3s |
| **Task 2** | Plan + Task 1 | Generate 2nd task | Task description | 2-3s |
| **Task 3** | Plan + Tasks 1,2 | Generate 3rd task | Task description | 2-3s |
| **Quiz** | Plan + all tasks | Generate 5 questions | Questions + **awaits input** | ⏸️ |
| **Evaluator** | Questions + answers | Score & analyze | Score + strong/weak topics | 2-3s |
| **Adaptive** | Evaluation | Recommend next steps | Recommendations | 2-3s |

---

## Troubleshooting

### Problem: Quiz node shows PAUSED but no input field

**Solution:**
- Refresh browser: `Ctrl+R`
- Check LangGraph dev server terminal (should show no errors)
- Ensure you're at `http://localhost:2024` (not HTTPS)

### Problem: I typed an answer but nothing happened

**Solution:**
- Ensure you typed only: `a`, `b`, `c`, or `d`
- No extra spaces or characters
- Press **Enter** after typing
- Check browser console for errors (F12)

### Problem: Workflow moved to Evaluator but my answers weren't recorded

**Solution:**
- Check LangSmith trace: https://smith.langchain.com/...
- Click Evaluator node → check `quiz_answers` field in state
- If empty: click Quiz node and re-check the input

### Problem: Terminal shows error "langgraph dev not found"

**Solution:**
```bash
pip install langgraph
pip install --upgrade langgraph
langgraph dev --version  # Verify installation
```

---

## Key Files

| File | Purpose |
|------|---------|
| `agents/quiz.py` | Quiz generation + human-in-loop input collection |
| `agents/evaluator.py` | Score calculation + topic identification |
| `agents/adaptive.py` | Recommendation generator |
| `graph/workflow.py` | Pipeline orchestration with conditional routing |
| `main.py` | Entry point + configuration |
| `.env` | API keys (GROQ, LangChain) |
| `langgraph.json` | Studio configuration |

---

## Command Reference

```bash
# Start dev server
langgraph dev

# Run direct (non-UI, for testing)
python main.py "Learn Python Basics"

# Interactive mode
python main.py

# Check if modules load
python -c "from agents.quiz import quiz_agent; print('OK')"

# View LangSmith cloud traces
# → Open: https://smith.langchain.com/o/projects/p/agentic-learning-system
```

---

## Complete Example Session

### Terminal 1: Start Dev Server
```bash
$ langgraph dev
Graph loaded successfully
Studio running at http://127.0.0.1:2024
```

### Terminal 2 (or Browser): Use Studio UI
```
1. Open http://localhost:2024
2. Enter topic: "Learn Python in 3 Days"
3. Click START
4. Watch: Planner → Tasks → Quiz
5. When Quiz pauses: Enter answers (a/b/c/d)
6. Watch: Evaluator → Adaptive
7. Click nodes to see outputs
```

### Browser Tab 2: View LangSmith Trace
```
Go to: https://smith.langchain.com/o/projects/p/agentic-learning-system
→ See full execution with all intermediate outputs
→ View your quiz answers and evaluation
```

---

## Architecture Summary

- **Framework**: LangGraph (StateGraph)
- **LLM**: GROQ (llama-3.1-8b-instant)
- **Tracing**: LangSmith cloud
- **UI**: LangGraph Studio (local)
- **Input Method**: Interrupt mechanism (pauses workflow, waits for user)
- **State Management**: TypedDict with proper schema

---

**Last Updated**: 2026-04-02  
**Status**: ✅ Production Ready  
**Ready to test?** Start with: `langgraph dev`
