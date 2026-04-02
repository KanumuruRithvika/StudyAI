from utils.llm import get_llm, call_llm_with_retry

llm = get_llm()

def adaptive_agent(state):
    print("\n[ADAPTIVE_AGENT] Starting...")
    
    evaluation = state.get("evaluation", "")
    weak_topics = state.get("weak_topics", [])
    quiz_score = state.get("quiz_score", "")
    current_day = state.get("current_day", 1)
    plan = state.get("plan", "")

    print(f"[INPUT] Day {current_day} - Evaluation analyzed")
    print(f"[INPUT] Weak topics: {weak_topics}")
    print(f"[INPUT] Quiz score: {quiz_score}")
    print(f"[ANALYZING] Creating recommendations...\n")

    # Generate recommendations based on weak topics
    if weak_topics and len(weak_topics) > 0:
        topics_text = ", ".join(weak_topics)
        prompt = f"""Based on weak areas identified in: {topics_text}

{evaluation}

Create 3 specific next learning steps to improve in these weak areas."""
    else:
        prompt = f"""Based on the evaluation:
{evaluation}

Suggest 3 specific next learning steps to reinforce knowledge."""

    response = call_llm_with_retry(llm, prompt)
    adapted_content = response.content
    
    print(f"[SUCCESS] Recommended Next Steps:")
    print(f"---")
    print(adapted_content)
    print(f"---\n")
    
    # AUTOMATIC DAY PROGRESSION (no user interaction)
    print(f"[DECISION] Completing Day {current_day}...")
    
    # Determine what to do next
    if current_day < 3:
        # More days to go - prepare for next day with weak topics focus
        next_day = current_day + 1
        print(f"[MOVING] Advancing to Day {next_day}")
        print(f"[REPLAN] Day {next_day} will focus on weak topics from Day {current_day}")
        
        # Store day results and weak topics
        day_results = state.get("day_results", {})
        day_results[current_day] = {
            "evaluation": evaluation,
            "score": quiz_score,
            "weak_topics": weak_topics,
            "tasks": state.get("tasks_list", [])
        }
        
        daily_weak_topics = state.get("daily_weak_topics", {})
        daily_weak_topics[current_day] = weak_topics
        
        return {
            "adapted_plan": adapted_content,
            "plan_completed": False,  # Continue to next day
            "day_complete": True,
            "current_day": next_day,
            "weak_topics": weak_topics,  # Pass weak topics to next day
            "task_count": 0,  # Reset for next day's tasks
            "tasks_list": [],  # Reset for next day
            "day_results": day_results,
            "daily_weak_topics": daily_weak_topics
        }
    else:
        # Day 3 complete - end workflow
        print(f"[COMPLETE] All 3 days completed!")
        print(f"[SUMMARY] Final results saved")
        
        day_results = state.get("day_results", {})
        day_results[current_day] = {
            "evaluation": evaluation,
            "score": quiz_score,
            "weak_topics": weak_topics,
            "tasks": state.get("tasks_list", [])
        }
        
        return {
            "adapted_plan": adapted_content,
            "plan_completed": True,  # End workflow
            "day_complete": True,
            "day_results": day_results
        }
    
    print(f"[UPDATE] Learning journey completed!")

    return {
        "adapted_plan": adapted_content,
        "plan_completed": True
    }