# Start LangGraph Dev Server - Windows PowerShell
# Run from: c:\Users\ideal\agentstudy\backend

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "LangGraph Dev Server Starting..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration Details:" -ForegroundColor Yellow
Write-Host "  Location: c:\Users\ideal\agentstudy\backend"
Write-Host "  Config: langgraph.json"
Write-Host "  Graph: learning-agent"
Write-Host "  Module: graph/workflow.py:build_graph"
Write-Host ""
Write-Host "Web Interface: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Endpoint: http://localhost:8000/api"
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "c:\Users\ideal\agentstudy\backend"
langgraph up
