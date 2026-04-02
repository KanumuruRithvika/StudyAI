from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langgraph.types import Send as LGSend

from agents.planner import planner_agent
from agents.task import task_agent
from agents.quiz import quiz_agent
from agents.evaluator import evaluator_agent
from agents.adaptive import adaptive_agent

# ---------------------------
# State Definition
# ---------------------------

class LearningState(TypedDict, total=False):
    """State schema for 3-day learning workflow"""
    goal: str
    plan: str
    
    # Day tracking
    current_day: int  # 1, 2, or 3
    day_tasks: dict  # {1: {...}, 2: {...}, 3: {...}}
    day_results: dict  # {1: {...}, 2: {...}, 3: {...}}
    daily_weak_topics: dict  # {1: [...], 2: [...], 3: [...]}
    
    # Current iteration
    tasks_list: list
    task_count: int
    quiz: str
    quiz_answers: list
    evaluation: str
    adapted_plan: str
    weak_topics: list
    quiz_score: str
    
    # Control flags
    topic_completed: bool
    plan_completed: bool
    day_complete: bool
    history: str
    progress: str

# ---------------------------
# Node Wrapper Functions to Log Outputs
# ---------------------------

def planner_wrapper(state):
    """Wrapper to trace planner output - all tracing goes to LangSmith"""
    result = planner_agent(state)
    return result

def task_wrapper(state):
    """Wrapper to trace task output - all tracing goes to LangSmith"""
    result = task_agent(state)
    return result

def quiz_wrapper(state):
    """Wrapper to trace quiz output - all tracing goes to LangSmith"""
    result = quiz_agent(state)
    return result

def evaluate_wrapper(state):
    """Wrapper to trace evaluator output - all tracing goes to LangSmith"""
    result = evaluator_agent(state)
    return result

def adaptive_wrapper(state):
    """Wrapper to trace adaptive output - all tracing goes to LangSmith"""
    result = adaptive_agent(state)
    return result

# ---------------------------
# Decision Functions
# ---------------------------

def check_topic_completion(state):
    decision = "quiz" if state.get("topic_completed", False) else "task"
    return decision

def check_plan_completion(state):
    """Decide if workflow ends or continues to next day"""
    # If plan_completed is True, end the workflow
    # Otherwise, loop back to task generation for next day
    decision = END if state.get("plan_completed", False) else "task"
    return decision

# ---------------------------
# Graph Builder
# ---------------------------

def build_graph():

    graph = StateGraph(LearningState)

    # Nodes with logging wrappers
    graph.add_node("planner", planner_wrapper)
    graph.add_node("task", task_wrapper)
    graph.add_node("quiz", quiz_wrapper)
    graph.add_node("evaluate", evaluate_wrapper)
    graph.add_node("adaptive", adaptive_wrapper)

    # Entry
    graph.set_entry_point("planner")

    # Flow
    graph.add_edge("planner", "task")

    # Loop: Task → Decision
    graph.add_conditional_edges(
        "task",
        check_topic_completion,
        {
            "quiz": "quiz",
            "task": "task"
        }
    )

    # After Quiz
    graph.add_edge("quiz", "evaluate")

    # Evaluation → Adaptive
    graph.add_edge("evaluate", "adaptive")

    # Adaptive → Next Step Decision
    graph.add_conditional_edges(
        "adaptive",
        check_plan_completion,
        {
            "task": "task",
            END: END
        }
    )

    return graph.compile()