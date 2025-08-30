@echo off
title DariusAI - Development Server
echo 🚀 Starting DariusAI Development Servers
echo ========================================
echo.

:: Start backend server in a new window
echo Starting backend server...
start "DariusAI Backend" cmd /k "cd /d backend && venv\Scripts\activate.bat && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: Wait a few seconds for backend to start
timeout /t 5 /nobreak >nul

:: Start frontend server in a new window
echo Starting frontend server...
start "DariusAI Frontend" cmd /k "cd /d frontend && npm start"

echo.
echo 🎉 DariusAI is starting up!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/api/docs
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.

:: Open the application in the default browser after a delay
timeout /t 10 /nobreak >nul
start http://localhost:3000

pause
