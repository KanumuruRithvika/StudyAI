#!/usr/bin/env python3
"""
Agentic Learning System - Fully Automatic 3-Day Learning Loop
All execution automatically traced to LangSmith
NO USER INTERACTION REQUIRED
"""

import sys
import os
from dotenv import load_dotenv
from langsmith_setup import setup_langsmith

# Fix module path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def run():
    """Automatic 3-day learning loop with no user interaction"""
    
    print("\n" + "=" * 70)
    print("AGENTIC LEARNING SYSTEM - FULLY AUTOMATIC 3-DAY LOOP")
    print("=" * 70)
    
    # Validate LangSmith
    langsmith_config = setup_langsmith()
    
    if langsmith_config is None:
        print("\n[ERROR] LangSmith configuration failed")
        sys.exit(1)
    
    print(f"\n[SUCCESS] LangSmith enabled - All traces recorded automatically")
    print(f"[DASHBOARD] https://smith.langchain.com/o/projects/p/agentic-learning-system")
    
    # Default learning goal (automatic)
    learning_goal = "Learn Python Programming Fundamentals"
    print(f"\n[GOAL] {learning_goal}")
    print("[MODE] Fully automatic - no user interaction\n")
    
    try:
        from graph.workflow import build_graph
        
        app = build_graph()
        
        # Initialize state for 3-day loop
        initial_state = {
            "goal": learning_goal,
            "plan": "",
            "current_day": 1,
            "day_tasks": {},
            "day_results": {},
            "daily_weak_topics": {},
            "tasks_list": [],
            "task_count": 0,
            "quiz": "",
            "quiz_answers": [],
            "evaluation": "",
            "adapted_plan": "",
            "weak_topics": [],
            "quiz_score": "",
            "topic_completed": False,
            "plan_completed": False,
            "day_complete": False,
            "history": "",
            "progress": "Starting 3-day automatic learning"
        }
        
        print("=" * 70)
        print("[EXECUTING] 3-Day Learning Loop")
        print("=" * 70 + "\n")
        
        # Execute workflow
        config = {"recursion_limit": 100}
        result = app.invoke(initial_state, config=config)
        
        # ============== FINAL SUMMARY ==============
        print("\n" + "=" * 70)
        print("[WORKFLOW COMPLETE - ALL 3 DAYS FINISHED]")
        print("=" * 70)
        
        print(f"\n[LEARNING GOAL] {result.get('goal', 'N/A')}")
        
        # Display 3-day results
        day_results = result.get("day_results", {})
        print(f"\n[3-DAY LEARNING SUMMARY]")
        print(f"{'=' * 70}")
        
        for day in range(1, 4):
            if day in day_results:
                day_info = day_results[day]
                score = day_info.get('score', 'N/A')
                weak = day_info.get('weak_topics', [])
                print(f"\nDay {day}:")
                print(f"  • Score: {score}")
                if weak:
                    print(f"  • Weak Topics: {', '.join(weak)}")
                else:
                    print(f"  • Weak Topics: None (Mastered!)")
            else:
                print(f"\nDay {day}: Completed")
        
        # LangSmith Details
        print(f"\n{'=' * 70}")
        print(f"[LANGSMITH TRACING]")
        print(f"  Dashboard: https://smith.langchain.com/o/projects/p/agentic-learning-system")
        print(f"\n[EXECUTION TRACE]")
        print(f"  Day 1: Planner → Tasks → Quiz → Evaluator → Adaptive (Replan for Day 2)")
        print(f"  Day 2: Tasks (weak topics focus) → Quiz → Evaluator → Adaptive (Replan for Day 3)")
        print(f"  Day 3: Tasks → Final Quiz → Final Evaluator → Complete")
        
        print(f"\n[OPENING] Dashboard in browser...")
        try:
            import webbrowser
            webbrowser.open("https://smith.langchain.com/o/projects/p/agentic-learning-system")
        except:
            print("[INFO] Visit dashboard manually at link above")
        
        print(f"\n{'=' * 70}\n")
        
    except Exception as e:
        print(f"\n[ERROR] Workflow failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if "--test-langsmith" in sys.argv:
        print("[TEST] LangSmith Configuration")
        setup_langsmith()
        print("[SUCCESS] Ready for automatic workflow!")
    else:
        run()
