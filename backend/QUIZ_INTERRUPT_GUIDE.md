# Quiz Answer Input via LangGraph Interrupt Mechanism

## Overview
The quiz agent now uses **LangGraph's interrupt mechanism** to pause workflow execution and wait for user answers. This enables multiple input methods.

## How It Works

### Architecture Flow
```
Quiz Agent → interrupt() call
           ↓
        Pauses workflow
           ↓
    [User input via UI or API]
           ↓
    Workflow resumes with answer
           ↓
    Evaluator processes answers
           ↓
    Shows strong/weak topics
```

## Using Different Input Methods

### Option 1: LangGraph Studio UI (Recommended)
1. **Start the dev server**:
   ```bash
   langgraph dev
   ```
2. **Open in browser**: http://localhost:2024 or https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

3. **When workflow reaches Quiz node**:
   - Studio UI shows an **[INPUT REQUIRED]** state
   - A text input form appears in the right panel
   - Type your answer: `a`, `b`, `c`, or `d`
   - Press Enter to submit
   - Studio proceeds to next question automatically

4. **View Results**:
   - After all 5 answers submitted
   - Evaluator node processes them
   - Click **Evaluator node** → see QUIZ SCORE, STRONG TOPICS, WEAK TOPICS

### Option 2: Terminal (Fallback - Still Works)
1. **Run directly**:
   ```bash
   python main.py "Learn Python"
   ```

2. **When quiz appears**:
   - Terminal prompts: `Question 1 - Enter your answer (a/b/c/d):`
   - Type: `a` (or b, c, d)
   - Press Enter
   - Terminal repeats for Q2-Q5

### Option 3: API Call (Programmatic)
1. **Submit answer via HTTP**:
   ```bash
   curl -X POST http://localhost:2024/runs/[run_id]/interrupt \
     -H "Content-Type: application/json" \
     -d '{"value": "a"}'
   ```

## Implementation Details

### Modified Code
**File**: `agents/quiz.py`
- **Old Function**: `get_quiz_answers()` — used `input()` (terminal only)
- **New Function**: `collect_quiz_answers_via_interrupt()` — uses `interrupt()` (multi-method)

### Key Changes
```python
# OLD (Terminal-only)
answer = input(f"Question {q_num} - Your answer (a/b/c/d): ")

# NEW (UI + Terminal + API)
answer = interrupt(f"Question {q_num} - Enter your answer (a/b/c/d):")
```

### Import Added
```python
from langgraph.types import interrupt
```

## Validation Logic
- **Valid inputs**: `a`, `b`, `c`, `d` (case-insensitive, whitespace trimmed)
- **Invalid inputs**: Letters other than a-d return error + re-prompt
- **Type validation**: Ensures answer is string, else re-prompts

## Viewing Quiz Results

### In LangGraph Studio UI
1. Workflow completes all nodes
2. Click on **Evaluator** node in the graph
3. Right panel shows:
   ```
   [SUCCESS] Quiz Evaluation:
   ---
   QUIZ SCORE: 4/5 (80%)
   
   STRONG TOPICS:
   - Python loops
   - Data structures
   
   WEAK TOPICS:
   - Exception handling
   ---
   ```

### In LangSmith Dashboard
1. Go to: https://smith.langchain.com/o/projects/p/agentic-learning-system
2. Click latest run
3. Expand **Evaluator** node
4. View complete evaluation output

### In Terminal Output
- Direct run: `python main.py "topic"`
- Full results shown in console

## Error Handling
```
[ERROR] Invalid answer 'x'. Please enter a, b, c, or d for Q1
→ Re-prompts for Q1 answer (doesn't skip)

[ERROR] Invalid input type. Please enter a, b, c, or d for Q2
→ Re-prompts for Q2 answer (if non-string value received)
```

## Troubleshooting

### Issue: UI Shows "PAUSED" But No Input Form
**Solution**: 
- Refresh browser: `Cmd+R` (Mac) or `Ctrl+R` (Windows)
- Check browser console for errors
- Ensure LangGraph server is running: `langgraph dev`

### Issue: Terminal Says "Question 1" But No Input Prompt
**Solution**:
- If running `langgraph dev`: Use Studio UI instead (terminal input works but not visible in dev server)
- Direct run: `python main.py "topic"` — terminal input() works normally

### Issue: Answer Submitted But Workflow Doesn't Continue
**Solution**:
- Check that answer was valid (a/b/c/d only)
- Look at terminal/server logs for validation errors
- Ensure LangSmith API key is valid (LANGCHAIN_API_KEY set)

## Advanced: Customizing Interrupt Behavior

To modify interrupt message format:
```python
# Current format (Question 1 - Enter your answer (a/b/c/d):)
prompt = f"Question {q_num} - Enter your answer (a/b/c/d):"

# Custom format example
prompt = f"\n[Q{q_num}/5] {QUESTION_TEXT}\nAnswer (a/b/c/d): "
```

Edit in `agents/quiz.py` line ~52 (inside `collect_quiz_answers_via_interrupt()`)

## Testing Checklist

- [ ] `langgraph dev` starts without errors
- [ ] Studio UI loads at http://localhost:2024
- [ ] Workflow starts, planner generates plan
- [ ] Tasks generate 3 times in succession
- [ ] Quiz node shows all 5 questions
- [ ] Quiz state shows **[INPUT REQUIRED]** in Studio
- [ ] Entering answer "a" → accepted
- [ ] Entering answer "x" → rejected with error message
- [ ] All 5 answers collected → Evaluator runs
- [ ] Evaluator shows QUIZ SCORE, STRONG TOPICS, WEAK TOPICS
- [ ] Terminal run `python main.py "topic"` shows full results
- [ ] LangSmith dashboard shows complete trace with all nodes

---

**Last Updated**: 2026-04-02
**Framework**: LangGraph 0.1+
**Python**: 3.13+
