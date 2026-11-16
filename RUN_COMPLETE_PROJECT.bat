@echo off
echo ╔════════════════════════════════════════════════════════════════════════════╗
echo ║                                                                            ║
echo ║   🚀 SARTHAK NIVESH - COMPLETE FULL STACK PROJECT                         ║
echo ║   Starting Frontend + Backend Together                                     ║
echo ║                                                                            ║
echo ╚════════════════════════════════════════════════════════════════════════════╝
echo.

REM Set Groq API Key
set GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
set PYTHONPATH=%CD%

echo 📦 Step 1: Installing Backend Dependencies...
echo ════════════════════════════════════════════════════════════════════════════
cd web\backend
pip install -q fastapi uvicorn[standard] python-dotenv yfinance pandas numpy requests beautifulsoup4 feedparser textblob vaderSentiment groq httpx lxml scipy
cd ..\..
echo ✅ Backend dependencies installed!
echo.

echo 📦 Step 2: Checking Frontend Dependencies...
echo ════════════════════════════════════════════════════════════════════════════
cd web\frontend
if not exist "node_modules\" (
    echo Installing Node modules...
    call npm install
) else (
    echo ✅ Node modules already installed!
)
cd ..\..
echo.

echo ════════════════════════════════════════════════════════════════════════════
echo    🎯 STARTING BOTH SERVERS
echo ════════════════════════════════════════════════════════════════════════════
echo.
echo Backend will run on:  http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
echo API Documentation:    http://localhost:8000/docs
echo IPO Intelligence:     http://localhost:8000/api/ipo_intelligence/health
echo.
echo ════════════════════════════════════════════════════════════════════════════
echo.

REM Start backend in a new window
start "Backend Server - Port 8000" cmd /k "cd /d %CD%\web\backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait 5 seconds for backend to start
echo ⏳ Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak > nul

REM Start frontend in a new window
start "Frontend Server - Port 3000" cmd /k "cd /d %CD%\web\frontend && npm start"

echo.
echo ════════════════════════════════════════════════════════════════════════════
echo    ✅ BOTH SERVERS STARTED!
echo ════════════════════════════════════════════════════════════════════════════
echo.
echo 🌐 Open your browser:
echo.
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo 🎯 All 6 IPO Intelligence Agents Active:
echo    1. Subscription Analysis
echo    2. GMP Analysis
echo    3. Financials ^& Fundamentals
echo    4. Listing Day Predictor
echo    5. Post-Listing Tracker
echo    6. Risk Assessment
echo.
echo ════════════════════════════════════════════════════════════════════════════
echo.
echo 💡 To stop servers:
echo    - Close the Backend window
echo    - Close the Frontend window
echo    - Or press Ctrl+C in each window
echo.
echo Press any key to exit this window (servers will keep running)...
pause > nul
