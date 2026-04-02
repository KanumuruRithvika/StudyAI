# ⚡ Quick Reference: Run & Test in 5 Minutes

## 🏃 Ultra-Quick Start

### Terminal 1: Start Dev Server
```powershell
cd c:\Users\ideal\agentstudy\backend
langgraph dev
```

**Wait for:**
```
✅ API: http://127.0.0.1:2024
✅ Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

---

### Browser Window 1: Open Studio
```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

**Steps:**
1. Select graph → `learning-api`
2. Enter goal:
   ```json
   {
     "goal": "Learn Python Fundamentals in 3 Days"
   }
   ```
3. Click "Invoke" / "Submit"
4. Watch execution

---

### Browser Window 2: View Traces
```
https://smith.langchain.com/o/projects/p/agentic-learning-system
```

**What to see:**
- ✅ New run appears (refreshing every few seconds)
- ✅ Click run to see full trace
- ✅ All 5 agents should be listed
- ✅ Token usage and timing shown

---

## ✅ Verification Checklist

- [ ] `.env` file exists with LANGCHAIN_API_KEY
- [ ] `langgraph.json` has 2 graphs defined
- [ ] `langgraph dev` runs without errors
- [ ] Studio UI loads
- [ ] Can submit learning goal
- [ ] Traces appear in LangSmith within 10 seconds

---

## 📱 Key Shortcuts

**Check imports:**
```powershell
python -c "from graph.workflow import build_graph; print('OK')"
```

**Check API is running:**
```powershell
curl http://127.0.0.1:2024/docs
```

**View available graphs:**
```powershell
curl http://127.0.0.1:2024/graphs
```

---

## 🔗 All URLs

| Purpose | URL |
|---------|-----|
| Studio + Test | https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024 |
| View Traces | https://smith.langchain.com/o/projects/p/agentic-learning-system |
| API Docs | http://127.0.0.1:2024/docs |
| Project Name | `agentic-learning-system` |

---

## 💬 Common Test Inputs

```json
{"goal": "Learn Python Fundamentals in 3 Days"}
{"goal": "Learn React.js in 3 Days"}
{"goal": "Learn Data Science in 3 Days"}
{"goal": "Learn Web Development in 3 Days"}
```

---

## ⏱️ Typical Execution Time

- **Planner node**: 10-15 seconds
- **Task node**: 5-10 seconds (per task)
- **Quiz node**: 5-10 seconds
- **Evaluator node**: 5-10 seconds
- **Adaptive node**: 5-10 seconds

**Total**: ~2-5 minutes per workflow

---

## 🎯 Success Criteria

✅ Studio loads and displays graph  
✅ Graph nodes execute in order  
✅ LangSmith dashboard shows traces  
✅ All 5 agents appear in trace  
✅ Final results include score and weak topics  

---

**You're all set! Start with `langgraph dev` →**
