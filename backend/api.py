"""
LangSmith API Integration - Run graph with user input from LangSmith interface
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# Load env
load_dotenv()

# Setup LangSmith
from langsmith_setup import setup_langsmith
langsmith_config = setup_langsmith()

if langsmith_config is None:
    print("\n[ERROR] LangSmith not configured properly")
    sys.exit(1)

# Import graph
from graph.workflow import build_graph as build_main_graph, LearningState


def build_api_graph():
    """
    Create a simplified graph wrapper for LangSmith invocation with user input
    
    This allows users to submit a goal string directly from LangSmith
    and get the full workflow execution with tracing.
    """
    
    class APIInput(TypedDict):
        goal: str
    
    def run_workflow(state: APIInput) -> Dict[str, Any]:
        """Run the main learning workflow with user-provided goal"""
        
        goal = state.get("goal", "").strip()
        
        if not goal:
            return {"error": "Goal cannot be empty"}
        
        print(f"\n{'='*70}")
        print(f"[LEARNING WORKFLOW - FROM LANGSMITH]")
        print(f"{'='*70}")
        print(f"\n📚 Learning Goal: {goal}")
        print(f"📊 Dashboard: {langsmith_config.get_dashboard_url()}\n")
        
        # Initialize state for main workflow
        workflow_state = {
            "goal": goal,
            "history": "",
            "topic_completed": False,
            "plan_completed": False,
            "progress": "Starting learning journey",
            "weak_topics": [],
            "quiz_score": "0/5"
        }
        
        print("="*70)
        print("[⚙️  WORKFLOW EXECUTION]")
        print("="*70 + "\n")
        
        try:
            # Run main workflow
            main_app = build_main_graph()
            result = main_app.invoke(workflow_state)
            
            print("\n" + "="*70)
            print("[✅ WORKFLOW COMPLETED]")
            print("="*70)
            print(f"\n[📋 RESULTS]")
            print(f"  Goal: {result.get('goal', 'N/A')}")
            print(f"  Score: {result.get('quiz_score', '0/5')}")
            print(f"  Weak Topics: {result.get('weak_topics', [])}\n")
            
            return result
            
        except Exception as e:
            print(f"\n❌ [ERROR] Workflow failed: {str(e)}\n")
            return {"error": str(e), "goal": goal}
    
    # Create simple graph
    graph = StateGraph(APIInput)
    graph.add_node("run_workflow", run_workflow)
    graph.set_entry_point("run_workflow")
    graph.add_edge("run_workflow", END)
    
    return graph.compile()


def run_learning_workflow(goal: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run the agentic learning workflow with a user-provided goal
    
    For direct Python invocation.
    
    Args:
        goal: The learning topic/goal (e.g., "Learn Python Fundamentals")
        config: Optional configuration overrides
    
    Returns:
        Complete workflow result with all states
    """
    
    if not goal or not isinstance(goal, str):
        raise ValueError("Goal must be a non-empty string")
    
    app = build_api_graph()
    return app.invoke({"goal": goal})


if __name__ == "__main__":
    # If run directly with arguments
    if len(sys.argv) > 1:
        learning_goal = " ".join(sys.argv[1:])
        result = run_learning_workflow(learning_goal)
        print(json.dumps({
            "goal": result.get("goal"),
            "quiz_score": result.get("quiz_score"),
            "weak_topics": result.get("weak_topics"),
            "status": "completed"
        }, indent=2))
    else:
        print("❌ Please provide a learning goal as argument")
        print("   Usage: python api.py 'Your learning topic'")

