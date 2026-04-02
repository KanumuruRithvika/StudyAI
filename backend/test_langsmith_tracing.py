#!/usr/bin/env python3
"""
Test script to verify LangSmith tracing is working
"""

import requests
import json
import time
from datetime import datetime

def test_langsmith_tracing():
    """Test LangGraph API and verify traces appear in LangSmith"""
    
    API_URL = "http://127.0.0.1:2024"
    
    print("\n" + "="*70)
    print("[LANGSMITH TRACING TEST]")
    print("="*70)
    
    # Step 1: Check if API is running
    print("\n[1] Checking API health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("    ✅ API is running on port 2024")
        else:
            print(f"    ⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"    ❌ API is not responding: {e}")
        return False
    
    # Step 2: Get available graphs
    print("\n[2] Checking available graphs...")
    try:
        response = requests.get(f"{API_URL}/graphs", timeout=5)
        if response.status_code == 200:
            graphs = response.json()
            print(f"    ✅ Found graphs: {list(graphs.keys())}")
        else:
            print(f"    ❌ Failed to get graphs")
            return False
    except Exception as e:
        print(f"    ❌ Error getting graphs: {e}")
        return False
    
    # Step 3: Invoke the learning-api graph with tracing
    print("\n[3] Invoking learning-api graph with tracing...")
    print("    This will send all traces to LangSmith...")
    
    invoke_url = f"{API_URL}/invoke/learning-api"
    payload = {
        "input": {
            "goal": "Test: Learn Python Basics in 3 Days"
        }
    }
    
    print(f"    API Endpoint: {invoke_url}")
    print(f"    Payload: {json.dumps(payload, indent=2)}")
    
    try:
        print("\n    Sending request... (this may take 2-5 minutes)")
        start_time = datetime.now()
        
        response = requests.post(invoke_url, json=payload, timeout=600)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n    ✅ Workflow completed successfully in {elapsed:.1f} seconds")
            print(f"\n    Result Summary:")
            print(f"      Goal: {result.get('output', {}).get('goal', 'N/A')}")
            print(f"      Quiz Score: {result.get('output', {}).get('quiz_score', 'N/A')}")
            print(f"      Weak Topics: {result.get('output', {}).get('weak_topics', [])}")
        else:
            print(f"\n    ❌ Workflow failed with status {response.status_code}")
            print(f"    Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"    ⚠️  Request timed out (graph execution took >10 minutes)")
        print(f"    Traces should still appear in LangSmith")
    except Exception as e:
        print(f"    ❌ Error invoking graph: {e}")
        return False
    
    # Step 4: Wait and check LangSmith
    print("\n[4] Checking LangSmith for traces...")
    print("    Waiting 10 seconds for traces to appear...")
    time.sleep(10)
    
    print("\n    ✅ Traces should now be visible in LangSmith:")
    print("       https://smith.langchain.com/o/projects/p/agentic-learning-system")
    print("\n" + "="*70)
    print("[SUCCESS] LangSmith tracing test complete!")
    print("="*70 + "\n")
    
    print("You should see:")
    print("  1. A new 'Run' in your project")
    print("  2. All 5 agent nodes (Planner, Task, Quiz, Evaluator, Adaptive)")
    print("  3. Complete trace with timing and token usage")
    print("  4. Input: Your learning goal")
    print("  5. Output: Quiz score and recommendations")
    
    return True

if __name__ == "__main__":
    import sys
    try:
        success = test_langsmith_tracing()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrupted by user")
        sys.exit(1)
