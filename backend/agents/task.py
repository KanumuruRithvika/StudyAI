from utils.llm import get_llm, call_llm_with_retry

llm = get_llm()

def task_agent(state):
    print("\n[TASK_AGENT] Starting...")
    plan = state.get("plan", "")
    task_count = state.get("task_count", 0)
    tasks_list = state.get("tasks_list", [])
    current_day = state.get("current_day", 1)
    weak_topics = state.get("weak_topics", [])
    
    print(f"[INFO] Day {current_day} - Current task: {task_count}/3")
    if weak_topics:
        print(f"[INFO] Focus on weak topics: {', '.join(weak_topics)}")
    
    # Generate 3 tasks autonomously
    if task_count < 3:
        task_num = task_count + 1
        print(f"\n[GENERATING] Day {current_day} - Task {task_num}/3...")
        
        # Include weak topics focus if available
        if weak_topics and len(weak_topics) > 0:
            prompt = f"""Generate 1 specific learning task for day {current_day}, task {task_num} based on this plan:
{plan}

FOCUS on these weak topics that need improvement:
{', '.join(weak_topics)}

Make the task focused on helping understand weak topics better."""
        else:
            prompt = f"""Generate 1 specific learning task for day {current_day}, task {task_num} based on this plan:
{plan}

The task should progressively build on the learning plan."""
        
        response = call_llm_with_retry(llm, prompt)
        task_content = response.content
        
        print(f"\n[SUCCESS] Day {current_day} Task {task_num} Generated:")
        print(f"---")
        print(task_content)
        print(f"---\n")
        
        # Accumulate tasks
        tasks_list.append(task_content)
        new_task_count = task_count + 1
        
        # Check if all 3 tasks for this day are done
        is_complete = (new_task_count >= 3)
        
        print(f"[UPDATE] task_count: {task_count} -> {new_task_count}")
        print(f"[UPDATE] topic_completed: {is_complete}")
        
        return {
            "task_count": new_task_count,
            "tasks_list": tasks_list,
            "topic_completed": is_complete
        }
    else:
        print(f"[COMPLETE] Day {current_day} - All 3 tasks completed!")
        return {
            "task_count": task_count,
            "tasks_list": tasks_list,
            "topic_completed": True
        }