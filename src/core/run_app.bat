@echo off
echo Starting सार्थक निवेश - Indian Stock Market Analysis Platform
echo.
echo Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani
echo.
echo Installing required packages...
pip install streamlit plotly yfinance alpha_vantage newsapi-python feedparser

echo.
echo Starting Streamlit application...
streamlit run main.py

pause