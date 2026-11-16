@echo off
echo ════════════════════════════════════════════════════════════════════════════
echo    🚀 SARTHAK NIVESH - COMPLETE FULL STACK SYSTEM
echo    IPO Intelligence Hub with All 6 Agents
echo ════════════════════════════════════════════════════════════════════════════
echo.

REM Set environment variables
set GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
set PYTHONPATH=%CD%

echo 📦 Installing/Updating dependencies...
echo.

REM Install backend dependencies
cd web\backend
pip install -r requirements.txt
cd ..\..

echo.
echo ════════════════════════════════════════════════════════════════════════════
echo    ✅ Setup Complete!
echo ════════════════════════════════════════════════════════════════════════════
echo.
echo 🎯 Starting Backend Server on http://localhost:8000
echo 📚 API Documentation: http://localhost:8000/docs
echo.
echo All 6 IPO Intelligence Agents Active:
echo   1. 📊 Subscription Analysis Agent
echo   2. 💰 GMP Analysis Agent
echo   3. 📈 Financials ^& Fundamentals Agent
echo   4. 🎯 Listing Day Predictor Agent
echo   5. 📅 Post-Listing Tracker Agent
echo   6. ⚠️  Risk Assessment Agent
echo.
echo ════════════════════════════════════════════════════════════════════════════
echo.

REM Start backend
cd web\backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
