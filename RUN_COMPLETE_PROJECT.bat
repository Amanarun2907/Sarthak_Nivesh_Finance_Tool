@echo off
echo â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
echo â•‘                                                                            â•‘
echo â•‘   ðŸš€ SARTHAK NIVESH - COMPLETE FULL STACK PROJECT                         â•‘
echo â•‘   Starting Frontend + Backend Together                                     â•‘
echo â•‘                                                                            â•‘
echo â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
echo.

REM Set Groq API Key
REM GROQ_API_KEY is read from .env - set it there, never hardcode it in this file
set PYTHONPATH=%CD%

echo ðŸ“¦ Step 1: Installing Backend Dependencies...
echo â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
cd web\backend
pip install -q fastapi uvicorn[standard] python-dotenv yfinance pandas numpy requests beautifulsoup4 feedparser textblob vaderSentiment groq httpx lxml scipy
cd ..\..
echo âœ… Backend dependencies installed!
echo.

echo ðŸ“¦ Step 2: Checking Frontend Dependencies...
echo â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
cd web\frontend
if not exist "node_modules\" (
    echo Installing Node modules...
    call npm install
) else (
    echo âœ… Node modules already installed!
)
cd ..\..
echo.

echo â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
echo    ðŸŽ¯ STARTING BOTH SERVERS
echo â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
echo.
echo Backend will run on:  http://localhost:8000
echo Frontend will run on: http://localhost:3000
echo.
echo API Documentation:    http://localhost:8000/docs
echo IPO Intelligence:     http://localhost:8000/api/ipo_intelligence/health
echo.
echo â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
echo.

REM Start backend in a new window
start "Backend Server - Port 8000" cmd /k "cd /d %CD%\web\backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait 5 seconds for backend to start
echo â³ Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak > nul

REM Start frontend in a new window
start "Frontend Server - Port 3000" cmd /k "cd /d %CD%\web\frontend && npm start"

echo.
echo â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
echo    âœ… BOTH SERVERS STARTED!
echo â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
echo.
echo ðŸŒ Open your browser:
echo.
echo    Frontend:  http://localhost:3000
echo    Backend:   http://localhost:8000
echo    API Docs:  http://localhost:8000/docs
echo.
echo ðŸŽ¯ All 6 IPO Intelligence Agents Active:
echo    1. Subscription Analysis
echo    2. GMP Analysis
echo    3. Financials ^& Fundamentals
echo    4. Listing Day Predictor
echo    5. Post-Listing Tracker
echo    6. Risk Assessment
echo.
echo â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
echo.
echo ðŸ’¡ To stop servers:
echo    - Close the Backend window
echo    - Close the Frontend window
echo    - Or press Ctrl+C in each window
echo.
echo Press any key to exit this window (servers will keep running)...
pause > nul
