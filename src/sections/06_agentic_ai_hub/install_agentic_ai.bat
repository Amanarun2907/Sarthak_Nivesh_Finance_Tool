@echo off
echo ========================================
echo AGENTIC AI - AUTOMATIC INSTALLATION
echo ========================================
echo.

echo Step 1: Installing required libraries...
echo This may take 3-5 minutes...
echo.

pip install crewai==0.28.8 crewai-tools==0.1.6 langchain-groq==0.0.3 langchain-community==0.0.34 chromadb==0.4.24

echo.
echo ========================================
echo Step 2: Testing installation...
echo ========================================
echo.

python test_agentic_ai.py

echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Run: streamlit run main_ultimate_final.py
echo 2. Open: http://localhost:8502
echo 3. Click: "Agentic AI Hub" in sidebar
echo.
echo Press any key to exit...
pause >nul
