# LANGSMITH COMPLETE SETUP GUIDE

## What is LangSmith?

LangSmith is a cloud platform that **traces and monitors** all LLM calls in your application. It shows:
- Each agent's input and output
- Token usage and timing
- Complete execution flow
- Error tracking
- Performance analytics

---

## Step 1: Get Your API Key (REQUIRED)

### Option A: Generate New Key (Recommended)

1. **Visit**: https://smith.langchain.com
2. **Sign in** with your account (or create free account)
3. **Click** profile icon (top right) → **Settings**
4. **Select** "Organization" tab
5. **Click** "API Keys" in the left sidebar
6. **Click** "Create New API Key" button
7. **Copy** the generated key (starts with `lsv2_pt_`)
8. **Paste** into `.env` file as:
   ```
   LANGCHAIN_API_KEY=lsv2_pt_your_key_here
   ```

### Option B: Use Existing Key

If you already have an API key, verify it:
- Starts with `lsv2_pt_`
- Is 50+ characters long
- Has no extra spaces

---

## Step 2: Update .env File

Open `C:\Users\ideal\agentstudy\backend\.env` and verify:

```env
# Must have these 4 lines:
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=agentic-learning-system
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

**⚠️ IMPORTANT:**
- No extra spaces after values
- Key must be on single line
- Save file after changes

---

## Step 3: Test LangSmith Connection

Run this command to verify setup:

```bash
cd C:\Users\ideal\agentstudy\backend
python main.py --test-langsmith
```

**Expected Output:**
```
[LANGSMITH SETUP]
✅ LangSmith configured:
   Project: agentic-learning-system
   Tracing: Enabled
   Endpoint: https://api.smith.langchain.com

Dashboard: https://smith.langchain.com/o/projects/p/agentic-learning-system
```

If you see errors, go to **Troubleshooting** section below.

---

## Step 4: Run Complete Workflow

```bash
python main.py "Learn Python Dictionaries"
```

**What happens:**
1. ✅ LangSmith setup validates
2. ✅ Workflow starts (Planner → Tasks → Quiz → Evaluator → Adaptive)
3. ✅ Browser opens LangSmith dashboard automatically
4. ✅ All agent executions are traced in real-time

---

## Step 5: View in LangSmith Dashboard

### After Workflow Completes:

1. **LangSmith Dashboard opens automatically**
   - URL: https://smith.langchain.com/o/projects/p/agentic-learning-system

2. **Find your run** (latest at top of list)

3. **Click on run** to expand full trace

4. **View each agent:**
   - **Planner** node → See generated learning plan
   - **Task** nodes (1, 2, 3) → See each task
   - **Quiz** node → See questions + your answers
   - **Evaluator** node → See score + strong/weak topics
   - **Adaptive** node → See recommendations

---

## Complete Workflow in LangSmith

```
Run: [Your learning goal]
├─ Planner
│  ├─ Input: goal
│  └─ Output: 3-day learning plan
│
├─ Task (iteration 1)
│  ├─ Input: plan
│  └─ Output: Task 1 description
│
├─ Task (iteration 2)
│  ├─ Input: plan + previous tasks
│  └─ Output: Task 2 description
│
├─ Task (iteration 3)
│  ├─ Input: plan + all tasks
│  └─ Output: Task 3 description
│
├─ Quiz
│  ├─ Input: plan + all tasks
│  ├─ Output: 5 questions
│  └─ User answers: [a, b, c, d, a]
│
├─ Evaluator
│  ├─ Input: questions + answers + score (4/5)
│  ├─ Output: Analysis
│  └─ STRONG TOPICS: [list]
│  └─ WEAK TOPICS: [list]
│
├─ Adaptive
│  ├─ Input: evaluation + weak topics
│  └─ Output: Recommendations + Follow-up option
│
└─ (Optional) Follow-up Quiz on Weak Topics
```

---

## What to Look For in LangSmith

### Planner Node
- ✅ Input shows your learning goal
- ✅ Output shows complete 3-day plan
- ✅ Token usage and timing displayed

### Task Nodes (1, 2, 3)
- ✅ Each creates task incrementally
- ✅ Shows input plan
- ✅ Shows task description output
- ✅ task_count increments (0/3 → 1/3 → 2/3 → 3/3)

### Quiz Node
- ✅ Input shows learning plan + all tasks
- ✅ Output shows 5 complete questions
- ✅ Shows all questions with a/b/c/d options
- ✅ User answers are recorded

### Evaluator Node
- ✅ Input shows quiz + user answers + score
- ✅ Output shows:
  - Quiz score and percentage
  - STRONG TOPICS (what you know)
  - WEAK TOPICS (what to improve)
- ✅ Topic analysis visible

### Adaptive Node
- ✅ Input shows evaluation + weak topics
- ✅ Output shows:
  - 3 specific recommendations
  - Follow-up options
- ✅ Shows plan_completed status

---

## Troubleshooting LangSmith

### Problem 1: "API Key not found" or "Invalid configuration"

**Solution:**
1. Verify `.env` file has:
   ```
   LANGCHAIN_API_KEY=lsv2_pt_your_actual_key
   ```
2. Check key starts with `lsv2_pt_`
3. No extra spaces or quotes
4. Save file (Ctrl+S)
5. Restart terminal/PowerShell
6. Try again

### Problem 2: Dashboard doesn't load in browser

**Solution:**
1. Check internet connection
2. Try opening manually: https://smith.langchain.com
3. If manual open works, try workflow again
4. If still fails, check firewall settings

### Problem 3: Runs not appearing in dashboard

**Solution:**
1. Verify `LANGCHAIN_PROJECT=agentic-learning-system`
2. Check dashboard URL matches project name
3. Wait 5-10 seconds for dashboard to sync
4. Refresh browser (F5)
5. Check for project in sidebar (might be collapsed)

### Problem 4: Incomplete traces (missing agents)

**Solution:**
1. Check GROQ API key is also valid
2. Look for errors in terminal output
3. Verify all agents have correct imports
4. Run: `python -c "from agents import *; print('OK')"`

### Problem 5: "Connection timeout" or "Network error"

**Solution:**
1. Check internet connection
2. Verify firewall allows: `api.smith.langchain.com`
3. Try different network (corporate vs home WiFi)
4. Check if LangSmith service is up: https://status.langchain.dev
5. Try running later

---

## FAQ

**Q: Do I need LangSmith?**
A: No, system works without it. But LangSmith provides visibility into all agent executions.

**Q: Is LangSmith free?**
A: Yes, free tier includes tracing. Upgrade available for advanced features.

**Q: What if API key expires?**
A: Generate new key at https://smith.langchain.com/settings/organization/api-keys

**Q: Can I use multiple projects?**
A: Yes, change `LANGCHAIN_PROJECT` to any name you want.

**Q: Are my queries logged?**
A: Yes, LangSmith stores all traces. Check their privacy policy.

---

## Quick Commands

```bash
# Test LangSmith connection only
python main.py --test-langsmith

# Run full workflow with auto-open dashboard
python main.py "Your learning topic"

# Interactive mode (prompts for topic)
python main.py

# View specific project
# Open: https://smith.langchain.com/o/projects/p/agentic-learning-system
```

---

## Key Files

| File | Purpose |
|------|---------|
| `.env` | Configuration (API keys) |
| `langsmith_setup.py` | LangSmith configuration & validation |
| `main.py` | Entry point (validates LangSmith, runs workflow) |
| `graph/workflow.py` | Agent orchestration (all agents traced) |

---

## Next Steps

1. ✅ Generate API key at https://smith.langchain.com
2. ✅ Update `.env` with your key
3. ✅ Test: `python main.py --test-langsmith`
4. ✅ Run: `python main.py "Your learning topic"`
5. ✅ View results in LangSmith dashboard

---

**Status**: Ready to use  
**Last Updated**: 2026-04-02  
**Support**: Check LangSmith docs at https://api.smith.langchain.com/docs
