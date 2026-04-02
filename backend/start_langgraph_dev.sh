#!/bin/bash
# Start LangGraph Dev Server
# Run from: c:\Users\ideal\agentstudy\backend

echo "Starting LangGraph Dev Server..."
echo "================================"
echo ""
echo "Configuration: langgraph.json"
echo "Graph: learning-agent"
echo "Module: graph/workflow.py:build_graph"
echo ""
echo "Opening: http://localhost:8000"
echo ""

cd c:\Users\ideal\agentstudy\backend
langgraph up
