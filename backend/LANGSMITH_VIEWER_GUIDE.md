# 📊 LangSmith Workflow Viewer Guide

## 🚀 Quick Start

After running `python main.py`, the browser automatically opens LangSmith with your workflow trace.

---

## 📌 Viewing Your Workflow in LangSmith

### **Step 1: Navigate to Your Project**
```
URL: https://smith.langchain.com/o/projects/p/agentic-learning-system
```

### **Step 2: Select Your Run**
- Go to **Tracing** tab (left sidebar)
- You'll see `agentic-learning-system` project
- Click on your **latest run** (most recent timestamp)
- Project shows:
  - **Most Recent Run**: How long ago
  - **Trace Count**: Total number of nodes executed
  - **Error Rate**: Should be 0%

---

## 🔗 Workflow Node Trace Sequence

Your workflow executes in this exact order:

```
1. PLANNER AGENT
   Input:  goal (your learning topic)
   Output: plan (3-day detailed plan)
           
2. TASK AGENT (executes 3 times)
   Task 1:
   Input:  plan
   Output: Task 1 content
   
   Task 2:
   Input:  plan + task_count=1
   Output: Task 2 content
   
   Task 3:
   Input:  plan + task_count=2
   Output: Task 3 content (triggers quiz)
   
3. QUIZ AGENT
   Input:  plan + tasks_list + quiz_answers
   Output: quiz (5 questions)
           user_answers (your 5 responses)
   
4. EVALUATOR AGENT
   Input:  plan + tasks_list + quiz + quiz_answers
   Output: evaluation (strong/weak topics + score)
   
5. ADAPTIVE AGENT
   Input:  evaluation + plan + tasks_list
   Output: adapted_plan (next steps)
```

---

## 🎯 How to View Each Node's Intermediate Output

### In LangSmith Dashboard:

1. **Click on the Graph View** (default when you open a run)
   - You'll see a visual graph with all nodes connected
   - Green boxes = completed nodes
   - Shows the data flow between nodes

2. **Click any Node** (e.g., "planner", "task", "quiz")
   - Left panel shows: **Inputs**
   - Center/Right panel shows: **Outputs** 
   - Scroll down to see the actual values exchanged

3. **View Intermediate Data**:
   - **Planner Output**: See the full 3-day plan content
   - **Task Output**: See each task description
   - **Quiz Output**: See all 5 questions
   - **Evaluator Output**: See quiz score + strong/weak topics
   - **Adaptive Output**: See recommended next learning steps

---

## 💡 Key Things to Look For

### In Each Node Click:

- **Input State**: What data the node received
- **Output State**: What the node returned
- **LLM Calls**: 
  - Number of API calls to GROQ
  - Tokens used (input + output)
  - Model used: `llama-3.1-8b-instant`
  - Latency / Response time

- **Decision Functions**:
  - Conditional edges show branch choices
  - Task loop shows 3 iterations
  - Quiz triggers after task_count=3

---

## 📈 Example Workflow Trace Stats

```
Total Trace Count: 7 executions
├─ 1x Planner
├─ 3x Task (Task 1, 2, 3)
├─ 1x Quiz
├─ 1x Evaluator
└─ 1x Adaptive

Total Tokens Used: ~2000-3000
Total Latency: ~15-30 seconds
Error Rate: 0%
```

---

## 🔍 Debugging Tips

### If a node failed:
1. Click the red/failed node
2. Check the error message in the output
3. See the exact input that caused the issue
4. Review the LLM response

### To see all LLM calls:
- Under each node, scroll down
- Look for `LLMChain` or `chat` entries
- Click to expand and see:
  - Prompt sent to LLM
  - Model response
  - Tokens consumed

### To compare multiple runs:
- Go back to Tracing main view
- Click "Compare" button
- Select 2 runs to see differences
- Useful for testing different learning topics

---

## 🎯 What Each Agent Does (Visible in Trace)

| Agent | Input | Processing | Output |
|-------|-------|------------|--------|
| **Planner** | User's learning goal | LLM creates 3-day plan | Plan text |
| **Task (3x)** | Plan + task counter | LLM generates specific task | Task description |
| **Quiz** | Plan + all tasks | LLM creates 5 MCQ questions | Questions + Your answers |
| **Evaluator** | Plan + tasks + quiz answers | LLM scores & analyzes | Score + Strong/Weak topics |
| **Adaptive** | Evaluation results | LLM recommends next steps | Next learning path |

---

## 🚀 Next Steps to Try

1. **Run with different topics**: 
   - "Python Web Development"
   - "Data Science"
   - "Cloud Computing"
   - See how the workflow adapts!

2. **Answer quiz differently**: 
   - Try different quiz answers
   - See how weak topics change

3. **Monitor token usage**:
   - See how many tokens each topic uses
   - Optimize prompts if needed

4. **Share runs**:
   - In LangSmith, click "Share"
   - Get a public link to show others your workflow

---

## 📞 Troubleshooting

**Q: No trace showing in LangSmith?**  
A: Check that `LANGCHAIN_API_KEY` is in `.env` file and `LANGCHAIN_TRACING_V2=true`

**Q: Dashboard shows but graph is empty?**  
A: Run the agent again - first run sometimes takes time to process

**Q: LLM calls not showing?**  
A: Scroll down in the node details - they're under the agent output

**Q: Want to see raw JSON?**  
A: Click "Raw" button at the top of the run view

---

## 📊 Commands to Remember

```bash
# Run the agent with your learning goal
cd backend
python main.py

# Then enter your topic when prompted
# LangSmith will automatically open in browser

# View traces: https://smith.langchain.com/o/projects/p/agentic-learning-system
```

---

**Happy learning & tracing! 🎓✨**
