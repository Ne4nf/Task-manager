# Quick Start Script - Windows PowerShell

# ============================================
# Backend Server
# ============================================
Write-Host "🚀 Starting Task Manager Backend..." -ForegroundColor Green

# Navigate to backend
Set-Location "c:\Users\THUC\Task-manager\backend"

# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Set PYTHONPATH
$env:PYTHONPATH = "c:\Users\THUC\Task-manager\backend"

Write-Host "✅ Environment ready!" -ForegroundColor Green
Write-Host "📍 Backend will run on http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs at http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "" 
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
