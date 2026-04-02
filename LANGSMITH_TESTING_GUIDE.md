# 🚀 Complete Guide: Running LangGraph + Testing in LangSmith

## 📋 Prerequisites

### Required Software
- Python 3.9+
- pip package manager
- git (optional, already setup)

### Required API Keys
- **LangSmith API Key**: Get from https://smith.langchain.com/settings/organization/api-keys
- **GROQ API Key**: (Already in your .env)

---

## ✅ Step 1: Verify Environment Setup (.env Configuration)

### Check Your `.backend/.env` File

**File Location:** `c:\Users\ideal\agentstudy\backend\.env`

**Required Content:**
```env
GROQ_API_KEY=your_groq_api_key_here

LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=agentic-learning-system
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

✅ **Check:**
- `LANGCHAIN_API_KEY` starts with `lsv2_pt_`
- `LANGCHAIN_TRACING_V2` is set to `true`
- `LANGCHAIN_PROJECT` is set to your project name

---

## 📦 Step 2: Install Required Dependencies

### Run in PowerShell:

```powershell
cd c:\Users\ideal\agentstudy\backend

# Install LangGraph CLI and dependencies
pip install --upgrade langgraph-cli langchain langchain-core langchain-groq langsmith python-dotenv

# Verify installation
python -c "from graph.workflow import build_graph; print('✅ All imports successful')"
```

**Expected Output:**
```
✅ All imports successful
```

---

## 🎯 Step 3: Verify Configuration Files

### Check `langgraph.json`

**File Location:** `c:\Users\ideal\agentstudy\backend\langgraph.json`

**Required Content:**
```json
{
  "dependencies": ["."],
  "graphs": {
    "learning-agent": "./graph/workflow.py:build_graph",
    "learning-api": "./api.py:build_api_graph"
  },
  "env": ".env"
}
```

This file defines:
- `learning-agent` - Visual graph (from LangGraph Studio)
- `learning-api` - API with user input form

---

## 🚀 Step 4: Start LangGraph Dev Server

### Run in PowerShell:

```powershell
cd c:\Users\ideal\agentstudy\backend

# Start the dev server
langgraph dev
```

### Expected Output:
```
Welcome to LangGraph

🚀 API: http://127.0.0.1:2024
🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
📚 API Docs: http://127.0.0.1:2024/docs
```

✅ **Success Indicators:**
- No error messages
- Server is running on port 2024
- File changes are detected (normal - hot reload)

---

## 🌐 Step 5: Access LangGraph Studio

### Open Your Browser:

**Option A: Studio UI (Visual Graph)**
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

**Option B: API Docs (Direct Testing)**
```
http://127.0.0.1:2024/docs
```

---

## 🧪 Step 6: Test in LangSmith (Two Methods)

### **Method 1: Using LangGraph Studio UI**

1. **Open Studio URL** (from Step 5, Option A)
2. **Select Graph:**
   - Click dropdown → Select `learning-api`
3. **Enter Input:**
   - Fill the form with:
   ```json
   {
     "goal": "Learn Python Fundamentals in 3 Days"
   }
   ```
4. **Submit:**
   - Click "Invoke" or "Submit" button
5. **Watch Execution:**
   - See the graph nodes executing in real-time
   - Each agent (Planner, Task, Quiz, Evaluator, Adaptive) will run sequentially

---

### **Method 2: Using API Docs (Advanced)**

1. **Open API Docs URL** (from Step 5, Option B)
2. **Navigate to Invoke Endpoint:**
   - Scroll to POST `/invoke` endpoint
3. **Expand and Click "Try it out"**
4. **Paste Request Body:**
   ```json
   {
     "input": {
       "goal": "Learn Machine Learning Basics in 3 Days"
     }
   }
   ```
5. **Click "Execute"**
6. **View Response:**
   - Traces will show in response
   - Check LangSmith dashboard for detailed logs

---

## 📊 Step 7: View Traces in LangSmith Dashboard

### Open LangSmith Project Dashboard:

**URL:**
```
https://smith.langchain.com/o/projects/p/agentic-learning-system
```

### What You'll See:

1. **Run List:**
   - Each workflow execution appears as a "Run"
   - Click any run to see details

2. **Trace Details:**
   - **Input**: Your learning goal
   - **Nodes Executed**:
     - ✅ Planner (creates 3-day plan)
     - ✅ Task (generates learning tasks)
     - ✅ Quiz (creates quizzes)
     - ✅ Evaluator (analyzes performance)
     - ✅ Adaptive (provides recommendations)
   - **Output**: Final results (score, weak topics)
   - **Timing**: How long each step took
   - **Tokens Used**: LLM token consumption

3. **Visualize:**
   - Click "Visualization" tab to see step-by-step flow
   - Hover over nodes to see inputs/outputs

---

## 🔍 Step 8: Advanced Testing

### Test Different Learning Topics:

**Example 1: Web Development**
```json
{
  "goal": "Learn React.js Fundamentals in 3 Days"
}
```

**Example 2: Data Science**
```json
{
  "goal": "Learn Data Analysis with Pandas in 3 Days"
}
```

**Example 3: Cloud Computing**
```json
{
  "goal": "Learn AWS Lambda Functions in 3 Days"
}
```

### Monitor Traces for Each:
- Check LangSmith dashboard for each run
- Compare execution times and token usage
- Analyze which topics get flagged as weak

---

## 🐛 Troubleshooting

### Issue: Port 2024 already in use

**Solution:**
```powershell
# Find process using port 2024
Get-NetTCPConnection -LocalPort 2024

# Kill the process (replace PID with actual process ID)
Stop-Process -Id <PID> -Force
```

### Issue: Module not found errors

**Solution:**
```powershell
cd c:\Users\ideal\agentstudy\backend
pip install -r requirments.txt
```

### Issue: LangSmith traces not showing

**Solution:**
1. Verify `LANGCHAIN_API_KEY` is set correctly
2. Check network connection to https://api.smith.langchain.com
3. Verify `LANGCHAIN_TRACING_V2=true` in .env
4. Wait 5-10 seconds for traces to appear

### Issue: Graph import takes too long

**Solution:**
- This is normal for first run (warm-up)
- Subsequent runs will be faster

---

## ✨ Step 9: Full Workflow Test

### Complete End-to-End Test:

```powershell
# 1. Ensure you're in backend directory
cd c:\Users\ideal\agentstudy\backend

# 2. Start LangGraph dev server
langgraph dev

# 3. Open in a new PowerShell window:
Start-Process "https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"

# 4. Fill form with learning goal
# Goal: "Learn Python Decorators in 3 Days"

# 5. Submit and watch execution

# 6. Open LangSmith dashboard in another tab:
Start-Process "https://smith.langchain.com/o/projects/p/agentic-learning-system"

# 7. See traces appear in real-time
```

---

## 📈 Testing Checklist

- [ ] `.env` file has correct API keys
- [ ] `langgraph.json` has both graphs defined
- [ ] `langgraph dev` starts without errors
- [ ] Studio UI loads at http://127.0.0.1:2024
- [ ] Can select both `learning-agent` and `learning-api`
- [ ] Can submit a learning goal via form
- [ ] Workflow executes without errors
- [ ] Traces appear in LangSmith dashboard within 10 seconds
- [ ] All 5 agents are visible in traces (Planner, Task, Quiz, Evaluator, Adaptive)
- [ ] Results include quiz score and weak topics

---

## 🎯 Key URLs Reference

| Component | URL |
|-----------|-----|
| **Studio UI** | https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024 |
| **API Docs** | http://127.0.0.1:2024/docs |
| **LangSmith Dashboard** | https://smith.langchain.com/o/projects/p/agentic-learning-system |
| **LangSmith API Keys** | https://smith.langchain.com/settings/organization/api-keys |

---

## 💡 Pro Tips

1. **Keep Terminal Open:** Keep the `langgraph dev` terminal window open while testing
2. **Hot Reload:** Code changes automatically reload (watch for file change notifications)
3. **Check Logs:** Look at terminal for timing information and any warnings
4. **Multiple Tests:** Run several tests with different topics to build up trace history
5. **Share Results:** LangSmith traces can be shared with team members via dashboard URLs

---

## 🚀 Next Steps

Once testing is complete:
1. Review all traces in LangSmith
2. Analyze performance metrics
3. Check token usage and costs
4. Prepare for demo/presentation
5. (Optional) Deploy to production using `langgraph up` with Docker

---

**Status: ✅ Your system is ready to test!**

Start with Step 4 (langgraph dev) and follow through all steps.
