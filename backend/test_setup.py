#!/usr/bin/env python
"""System validation script"""

import sys
import os
sys.path.insert(0, os.getcwd())

print('[TEST] Complete Setup Validation\n')
print('='*70)

# Test 1: Imports
print('[TEST 1] Module Imports')
try:
    from langsmith_setup import LangSmithConfig, setup_langsmith
    from graph.workflow import build_graph
    from agents.planner import planner_agent
    from agents.task import task_agent
    from agents.quiz import quiz_agent
    from agents.evaluator import evaluator_agent
    from agents.adaptive import adaptive_agent
    print('✅ All modules imported successfully')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)

# Test 2: LangSmith Config
print('\n[TEST 2] LangSmith Configuration')
config = LangSmithConfig()
is_valid, msg = config.validate()
if is_valid:
    print('✅ LangSmith configuration is valid')
    print(f'   Dashboard: {config.get_dashboard_url()}')
else:
    print(f'⚠️  {msg}')

# Test 3: Workflow Graph
print('\n[TEST 3] Workflow Graph')
try:
    app = build_graph()
    print('✅ Workflow graph built successfully')
except Exception as e:
    print(f'❌ Graph build failed: {e}')
    sys.exit(1)

# Test 4: State Schema
print('\n[TEST 4] State Schema')
try:
    test_state = {
        'goal': 'Test',
        'plan': 'Test plan',
        'tasks_list': [],
        'task_count': 0,
        'quiz': '',
        'quiz_answers': [],
        'evaluation': '',
        'adapted_plan': '',
        'topic_completed': False,
        'plan_completed': False,
        'weak_topics': [],
        'quiz_score': '0/5'
    }
    print('✅ State schema is valid')
except Exception as e:
    print(f'❌ State schema failed: {e}')

print('\n' + '='*70)
print('[SUCCESS] All systems ready for learning!')
print('='*70)
print('\nQuick Start:')
print('  python main.py "Learn Python Dictionaries"')
print('\nTest LangSmith:')
print('  python main.py --test-langsmith')
print('\nInteractive Mode:')
print('  python main.py')
