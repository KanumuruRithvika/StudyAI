from agents.planner import planner_agent
from agents.task import task_agent
from agents.evaluator import evaluator_agent

def orchestrator(state):
    print("🚀 Starting Workflow...")

    # Step 1: Plan
    plan_output = planner_agent(state)
    state.update(plan_output)

    # Step 2: Select Topic (basic version)
    state["current_topic"] = "Basics of the subject"

    # Step 3: Generate Tasks
    task_output = task_agent(state)
    state.update(task_output)

    # Step 4: Simulate Progress
    state["progress"] = "User completed 70% tasks"

    # Step 5: Evaluate
    eval_output = evaluator_agent(state)
    state.update(eval_output)

    return state