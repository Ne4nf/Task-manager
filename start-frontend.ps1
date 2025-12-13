# Quick Start Script - Frontend

# ============================================
# Frontend Development Server
# ============================================
Write-Host "🎨 Starting Task Manager Frontend..." -ForegroundColor Green

# Navigate to frontend
Set-Location "c:\Users\THUC\Task-manager\frontend"

Write-Host "✅ Checking dependencies..." -ForegroundColor Green

# Check if node_modules exists
if (-Not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies (first time only)..." -ForegroundColor Yellow
    npm install
}

Write-Host "📍 Frontend will run on http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Vite dev server
npm run dev
