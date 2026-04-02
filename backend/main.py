"""
Agentic Learning System - Main Entry Point

Complete 5-agent pipeline with LangSmith integration:
1. Planner - Creates learning plans
2. Task - Generates tasks (loops 3x)
3. Quiz - Creates quizzes with manual scoring
4. Evaluator - Analyzes performance & extracts topics
5. Adaptive - Provides recommendations & follow-ups
"""

import sys
import os
import webbrowser
from typing import Dict, Any

# Fix module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup LangSmith
from langsmith_setup import setup_langsmith, get_langsmith_config

# Configure LangSmith (this validates everything)
langsmith_config = setup_langsmith()

if langsmith_config is None:
    print("\n[ERROR] LangSmith configuration failed. Please fix .env file.")
    sys.exit(1)

# Now import graph after LangSmith is configured
from graph.workflow import build_graph


def run():
    """
    Main workflow execution function
    
    Flow:
    1. Planner: Creates 3-day learning plan
    2. Task (loop 3x): Generate sequential tasks
    3. Quiz: Present questions for manual scoring
    4. Evaluator: Score & identify strong/weak topics
    5. Adaptive: Recommendations & optional follow-up quiz
    """
    
    # Get learning topic
    if len(sys.argv) > 1:
        learning_goal = " ".join(sys.argv[1:]).strip()
        print(f"[STARTING] Learning Goal: {learning_goal}")
    else:
        print("\n" + "="*70)
        print("[AGENTIC LEARNING SYSTEM]")
        print("="*70)
        print("\nWhat would you like to learn today?")
        learning_goal = input(">> ").strip()
        
        if not learning_goal:
            learning_goal = "Learn Python Fundamentals in 3 Days"
        print(f"\n[STARTING] Learning Goal: {learning_goal}")
    
    print("\n[INFO] All execution details will be traced in LangSmith")
    print(f"[INFO] Dashboard: {langsmith_config.get_dashboard_url()}\n")
    
    # Initialize state
    state = {
        "goal": learning_goal,
        "history": "",
        "topic_completed": False,
        "plan_completed": False,
        "progress": "Starting learning journey",
        "weak_topics": [],
        "quiz_score": "0/5"
    }
    
    print("="*70)
    print("[WORKFLOW EXECUTION]")
    print("="*70 + "\n")
    
    try:
        # Build and run graph
        app = build_graph()
        result = app.invoke(state)
        
        print("\n" + "="*70)
        print("[WORKFLOW COMPLETED SUCCESSFULLY]")
        print("="*70)
        
        # Display results
        print(f"\n[RESULTS]")
        print(f"  Goal: {result.get('goal', 'N/A')}")
        print(f"  Score: {result.get('quiz_score', '0/5')}")
        print(f"  Weak Topics: {result.get('weak_topics', [])}")
        
        # Display LangSmith details
        print(f"\n[LANGSMITH DASHBOARD]")
        print(f"  URL: {langsmith_config.get_dashboard_url()}")
        print(f"  Project: {langsmith_config.project_name}")
        print(f"  Status: All agent executions are traced\n")
        
        # Open dashboard
        print("[OPENING] LangSmith Dashboard in browser...")
        webbrowser.open(langsmith_config.get_dashboard_url())
        
        print("\n[NEXT STEPS]")
        print("  1. Open LangSmith dashboard (should open automatically)")
        print("  2. Find your latest run (at the top)")
        print("  3. Click agents to see:")
        print("     - Planner: Generated learning plan")
        print("     - Task: 3 sequential tasks")
        print("     - Quiz: 5 questions + your answers")
        print("     - Evaluator: Score + Strong/Weak topics")
        print("     - Adaptive: Recommendations + Follow-up option")
        print("  4. View full trace of all interactions\n")
        
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Workflow cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {str(e)}")
        print(f"[DEBUG] Check LangSmith trace for details: {langsmith_config.get_dashboard_url()}")
        sys.exit(1)


def test_langsmith_only():
    """Test LangSmith connection without running full workflow"""
    config = get_langsmith_config()
    if config:
        print(f"\n✅ LangSmith is properly configured")
        print(f"   Dashboard: {config.get_dashboard_url()}")
        webbrowser.open(config.get_dashboard_url())
    else:
        print("\n❌ LangSmith configuration failed")
        sys.exit(1)


if __name__ == "__main__":
    # Check for test flag
    if "--test-langsmith" in sys.argv:
        test_langsmith_only()
    else:
        run()
