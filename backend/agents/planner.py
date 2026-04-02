from utils.llm import get_llm, call_llm_with_retry
from langchain_core.prompts import ChatPromptTemplate

llm = get_llm()

def planner_agent(state):
    print("\n[PLANNER_AGENT] Starting...")
    goal = state["goal"]
    print(f"[INPUT] Goal: {goal}")

    prompt = ChatPromptTemplate.from_template("""
    Create a 3-DAY LEARNING PLAN for: {goal}
    
    Format exactly:
    Day 1: [topic]
    Day 2: [topic]
    Day 3: [topic]
    """)

    chain = prompt | llm

    response = chain.invoke({"goal": goal})
    plan_content = response.content
    
    print(f"\n[SUCCESS] 3-Day Plan Created:")
    print(f"---")
    print(plan_content)
    print(f"---\n")
    
    print(f"[UPDATE] Initializing: task_count=0, tasks_list=[]")

    return {
        "plan": plan_content,
        "task_count": 0,
        "tasks_list": [],
        "progress": "Started learning journey"
    }