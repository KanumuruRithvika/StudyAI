# 🎓 LangGraph Studio Setup - QUICK START

## ✅ What's Already Done

- ✅ `langgraph.json` created with correct graph path
- ✅ `graph/workflow.py` has `return graph.compile()`
- ✅ Model set to `llama-3.1-8b-instant` (lightweight)
- ✅ All agents configured with node wrappers for tracing

---

## 🚀 STEPS TO RUN LANGGRAPH STUDIO

### **STEP 1: Install LangGraph CLI**
```bash
pip install langgraph-cli
```

### **STEP 2: Navigate to Backend Folder**
```bash
cd C:\Users\ideal\agentstudy\backend
```

### **STEP 3: Verify langgraph.json Exists**
```bash
# You should see: langgraph.json
dir langgraph.json
```

### **STEP 4: Start LangGraph Studio**
```bash
langgraph dev
```

### **STEP 5: Open in Browser**
- Automatically opens: `http://localhost:8123`
- Or manually paste: `http://localhost:8123`

---

## 🎯 What You'll See in Studio

### **The Graph Visualization**:
```
Input Box
  ↓
[Run Button]
  ↓
Workflow Graph:
┌─────────────┐
│  Planner    │──────┐
└─────────────┘      │
                     ↓
              ┌─────────────┐
              │  Task 1/2/3 │──────┐
              └─────────────┘      │
                                   ↓
                            ┌─────────────┐
                            │  Quiz       │──────┐
                            └─────────────┘      │
                                                 ↓
                                          ┌─────────────┐
                                          │ Evaluator   │──────┐
                                          └─────────────┘      │
                                                               ↓
                                               ┌─────────────────┐
                                               │  Adaptive       │
                                               └─────────────────┘
                                                      ↓
                                                   Output
```

### **Nodes You Can Click**:
1. **Planner** - Creates 3-day plan
2. **Task 1** - First task generated
3. **Task 2** - Second task generated
4. **Task 3** - Third task generated
5. **Quiz** - Shows 5 questions + waits for answers
6. **Evaluator** - Scores quiz & analyzes
7. **Adaptive** - Recommends next steps

---

## 🧪 HOW TO RUN (FOR YOUR JURY DEMO)

### **Inside Studio UI**:

1. **Click in the Input Box** (top left)
2. **Type**: `Learn Python in 3 days`
3. **Click "Run" button**
4. **Watch the workflow execute**:
   - Planner node → Output shows plan
   - Task nodes → Execute 3 times
   - Quiz node → Shows 5 questions
   - **PAUSES** - Waiting for your answers
   - Answer quiz (enter: `a`, `b`, `c`, `a`, `b`)
   - Evaluator → Shows scores
   - Adaptive → Shows next steps

---

## 💡 FOR JURY PRESENTATION

Show them:

✅ **Live Node Execution**
   - Watch each node run sequentially
   - See nodes turn green when complete

✅ **Click Each Node**
   - Show input state
   - Show output state
   - Show intermediate data flowing

✅ **Graph Visualization**
   - Show the path: Planner → Tasks → Quiz → Evaluator → Adaptive
   - Show conditional edges & loops
   - Show the 3 task iterations

✅ **Human-in-Loop**
   - Show quiz waiting for input
   - Enter your answers live
   - Watch evaluation happen

✅ **Real Data**
   - Plan text visible
   - Task descriptions
   - Quiz questions
   - Strong/weak topics identified
   - Recommended next steps

---

## ⚡ QUICK COMMANDS

```bash
# Terminal 1: Start Studio
cd C:\Users\ideal\agentstudy\backend
langgraph dev

# Terminal 2 (optional): Run system from command line
cd C:\Users\ideal\agentstudy\backend
python main.py
```

---

## 🎉 EXAMPLE DEMO SCRIPT

**For Your Jury:**

1. **Show the graph structure** (before running)
   - "This is our AI learning agent with 5 nodes"
   - Point to each node: Planner, Task, Quiz, Evaluator, Adaptive

2. **Run a workflow** 
   - Input: "Learn Web Development with Flask"
   - Click Run
   - Let it execute to the Quiz node

3. **Answer the quiz**
   - "Now I'm the human in the loop"
   - "I answer the 5 questions"
   - "The system automatically evaluates my answers"

4. **Show the outputs**
   - Click Planner → "See the 3-day plan"
   - Click Quiz → "See my answers"
   - Click Evaluator → "See my score & weak topics"
   - Click Adaptive → "See my next learning steps"

5. **Key Points**:
   - ✅ Fully autonomous agent workflow
   - ✅ Human-in-the-loop at quiz stage
   - ✅ Personalized learning paths
   - ✅ All traced in LangSmith

---

## 🔧 TROUBLESHOOTING

**Q: `langgraph dev` command not found**
- Make sure you installed: `pip install langgraph-cli`
- Try: `python -m langgraph dev`

**Q: Port 8123 already in use**
- Try: `langgraph dev --port 8124`
- Or close other local apps

**Q: Graph doesn't load**
- Check `langgraph.json` exists in backend folder
- Verify path: `"./graph/workflow.py:build_graph"`
- Check `graph/workflow.py` has `return graph.compile()`

**Q: Quiz won't accept answers**
- Make sure you're typing: `a`, `b`, or `c` (lowercase)
- Press Enter after each answer
- One answer per question

---

## 📝 FILE CHECKLIST

Before running `langgraph dev`:

- ✅ `backend/langgraph.json` exists
- ✅ `backend/graph/workflow.py` ends with `return graph.compile()`
- ✅ `backend/.env` has GROQ_API_KEY
- ✅ `backend/.env` has LANGCHAIN_API_KEY
- ✅ All agent files in `backend/agents/` exist
- ✅ `backend/utils/llm.py` has correct model

---

**Ready to demo to your jury! 🚀**
