# Enhanced Configuration with 50+ Stocks and 50+ Mutual Funds
import os
import sys
from datetime import datetime, timedelta

# API Keys
ALPHA_VANTAGE_API_KEY = "3ZTEB9EMFP7GAAIY"
NEWS_API_KEY = "7b3a5054a78143be90dfdc9472ed5b20"
GROQ_API_KEY = "your_groq_api_key_here"

PROJECT_NAME = "सार्थक निवेश"
PROJECT_DESCRIPTION = "AI-Powered Indian Stock Market Analysis & IPO Prediction Platform"

# EXPANDED - 50+ Indian Stocks
STOCK_SYMBOLS = {
    'HDFCBANK.NS': 'HDFC Bank', 'ICICIBANK.NS': 'ICICI Bank', 'SBIN.NS': 'State Bank of India',
    'AXISBANK.NS': 'Axis Bank', 'KOTAKBANK.NS': 'Kotak Mahindra Bank', 'INDUSINDBK.NS': 'IndusInd Bank',
    'BAJFINANCE.NS': 'Bajaj Finance', 'BAJAJFINSV.NS': 'Bajaj Finserv', 'HDFCLIFE.NS': 'HDFC Life',
    'SBILIFE.NS': 'SBI Life', 'TCS.NS': 'TCS', 'INFY.NS': 'Infosys', 'WIPRO.NS': 'Wipro',
    'HCLTECH.NS': 'HCL Tech', 'TECHM.NS': 'Tech Mahindra', 'LTI.NS': 'LTIMindtree',
    'MPHASIS.NS': 'Mphasis', 'COFORGE.NS': 'Coforge', 'RELIANCE.NS': 'Reliance',
    'NTPC.NS': 'NTPC', 'POWERGRID.NS': 'Power Grid', 'ONGC.NS': 'ONGC', 'BPCL.NS': 'BPCL',
    'IOC.NS': 'IOC', 'ADANIGREEN.NS': 'Adani Green', 'TATAPOWER.NS': 'Tata Power',
    'HINDUNILVR.NS': 'HUL', 'ITC.NS': 'ITC', 'NESTLEIND.NS': 'Nestlé', 'BRITANNIA.NS': 'Britannia',
    'DABUR.NS': 'Dabur', 'MARICO.NS': 'Marico', 'GODREJCP.NS': 'Godrej CP',
    'MARUTI.NS': 'Maruti', 'TATAMOTORS.NS': 'Tata Motors', 'M&M.NS': 'M&M',
    'BAJAJ-AUTO.NS': 'Bajaj Auto', 'EICHERMOT.NS': 'Eicher', 'HEROMOTOCO.NS': 'Hero MotoCorp',
    'SUNPHARMA.NS': 'Sun Pharma', 'DRREDDY.NS': 'Dr Reddy', 'CIPLA.NS': 'Cipla',
    'DIVISLAB.NS': 'Divis Lab', 'BIOCON.NS': 'Biocon', 'AUROPHARMA.NS': 'Aurobindo',
    'LT.NS': 'L&T', 'TATASTEEL.NS': 'Tata Steel', 'HINDALCO.NS': 'Hindalco',
    'JSWSTEEL.NS': 'JSW Steel', 'ULTRACEMCO.NS': 'UltraTech', 'BHARTIARTL.NS': 'Airtel',
    'ZEEL.NS': 'Zee', 'HATHWAY.NS': 'Hathway', 'DMART.NS': 'DMart', 'TRENT.NS': 'Trent',
    'JUBLFOOD.NS': 'Jubilant Food'
}

# EXPANDED - 50+ Mutual Funds Database
MUTUAL_FUNDS_DATABASE = {
    'large_cap': [
        {'name': 'SBI Bluechip Fund', 'nav': 89.45, 'return_1y': 12.5, 'return_3y': 14.2, 'return_5y': 11.8, 'expense_ratio': 0.65, 'rating': 4.5, 'aum': 25000},
        {'name': 'HDFC Top 100 Fund', 'nav': 156.78, 'return_1y': 13.2, 'return_3y': 15.1, 'return_5y': 12.4, 'expense_ratio': 0.58, 'rating': 4.3, 'aum': 18500},
        {'name': 'ICICI Pru Bluechip', 'nav': 112.34, 'return_1y': 11.8, 'return_3y': 13.9, 'return_5y': 11.2, 'expense_ratio': 0.72, 'rating': 4.2, 'aum': 22000},
        {'name': 'Axis Bluechip Fund', 'nav': 78.90, 'return_1y': 14.1, 'return_3y': 16.2, 'return_5y': 13.5, 'expense_ratio': 0.55, 'rating': 4.6, 'aum': 19500},
        {'name': 'Mirae Large Cap', 'nav': 145.67, 'return_1y': 13.8, 'return_3y': 15.8, 'return_5y': 12.9, 'expense_ratio': 0.48, 'rating': 4.4, 'aum': 16800},
        {'name': 'Kotak Bluechip', 'nav': 98.23, 'return_1y': 12.9, 'return_3y': 14.7, 'return_5y': 11.9, 'expense_ratio': 0.62, 'rating': 4.3, 'aum': 15200},
        {'name': 'Nippon Large Cap', 'nav': 87.56, 'return_1y': 11.5, 'return_3y': 13.2, 'return_5y': 10.8, 'expense_ratio': 0.68, 'rating': 4.0, 'aum': 12500},
        {'name': 'UTI Mastershare', 'nav': 134.89, 'return_1y': 12.3, 'return_3y': 14.0, 'return_5y': 11.5, 'expense_ratio': 0.70, 'rating': 4.1, 'aum': 11800},
        {'name': 'Franklin Bluechip', 'nav': 156.12, 'return_1y': 13.5, 'return_3y': 15.4, 'return_5y': 12.7, 'expense_ratio': 0.59, 'rating': 4.4, 'aum': 14300},
        {'name': 'DSP Top 100', 'nav': 92.45, 'return_1y': 12.1, 'return_3y': 13.8, 'return_5y': 11.3, 'expense_ratio': 0.66, 'rating': 4.2, 'aum': 10900},
    ],
    'mid_cap': [
        {'name': 'HDFC Mid-Cap Opp', 'nav': 234.56, 'return_1y': 15.8, 'return_3y': 18.5, 'return_5y': 14.9, 'expense_ratio': 0.75, 'rating': 4.7, 'aum': 18900},
        {'name': 'Axis Midcap', 'nav': 123.45, 'return_1y': 16.2, 'return_3y': 19.1, 'return_5y': 15.3, 'expense_ratio': 0.68, 'rating': 4.8, 'aum': 16500},
        {'name': 'Kotak Emerging Eq', 'nav': 178.90, 'return_1y': 14.9, 'return_3y': 17.8, 'return_5y': 14.2, 'expense_ratio': 0.72, 'rating': 4.5, 'aum': 14200},
        {'name': 'DSP Midcap', 'nav': 145.67, 'return_1y': 15.5, 'return_3y': 18.2, 'return_5y': 14.7, 'expense_ratio': 0.70, 'rating': 4.6, 'aum': 12800},
        {'name': 'SBI Magnum Midcap', 'nav': 198.34, 'return_1y': 14.3, 'return_3y': 17.1, 'return_5y': 13.8, 'expense_ratio': 0.78, 'rating': 4.3, 'aum': 11500},
        {'name': 'ICICI Pru Midcap', 'nav': 167.89, 'return_1y': 15.1, 'return_3y': 17.9, 'return_5y': 14.4, 'expense_ratio': 0.74, 'rating': 4.4, 'aum': 13200},
        {'name': 'Nippon Growth', 'nav': 212.45, 'return_1y': 16.8, 'return_3y': 19.5, 'return_5y': 15.8, 'expense_ratio': 0.69, 'rating': 4.7, 'aum': 15600},
        {'name': 'Mirae Midcap', 'nav': 189.12, 'return_1y': 15.9, 'return_3y': 18.7, 'return_5y': 15.1, 'expense_ratio': 0.65, 'rating': 4.6, 'aum': 14800},
        {'name': 'Tata Midcap Growth', 'nav': 156.78, 'return_1y': 14.7, 'return_3y': 17.4, 'return_5y': 14.0, 'expense_ratio': 0.76, 'rating': 4.3, 'aum': 10200},
        {'name': 'Invesco Midcap', 'nav': 134.56, 'return_1y': 15.3, 'return_3y': 18.0, 'return_5y': 14.5, 'expense_ratio': 0.73, 'rating': 4.4, 'aum': 9800},
    ],
    'small_cap': [
        {'name': 'Axis Small Cap', 'nav': 98.76, 'return_1y': 18.5, 'return_3y': 21.8, 'return_5y': 17.2, 'expense_ratio': 0.82, 'rating': 4.8, 'aum': 12500},
        {'name': 'SBI Small Cap', 'nav': 145.23, 'return_1y': 17.9, 'return_3y': 21.2, 'return_5y': 16.8, 'expense_ratio': 0.85, 'rating': 4.6, 'aum': 10800},
        {'name': 'HDFC Small Cap', 'nav': 167.89, 'return_1y': 19.2, 'return_3y': 22.5, 'return_5y': 18.1, 'expense_ratio': 0.78, 'rating': 4.9, 'aum': 14200},
        {'name': 'Kotak Small Cap', 'nav': 189.45, 'return_1y': 18.1, 'return_3y': 21.4, 'return_5y': 17.0, 'expense_ratio': 0.80, 'rating': 4.7, 'aum': 11900},
        {'name': 'Nippon Small Cap', 'nav': 123.67, 'return_1y': 17.5, 'return_3y': 20.8, 'return_5y': 16.5, 'expense_ratio': 0.83, 'rating': 4.5, 'aum': 9500},
        {'name': 'DSP Small Cap', 'nav': 156.34, 'return_1y': 18.8, 'return_3y': 22.1, 'return_5y': 17.6, 'expense_ratio': 0.79, 'rating': 4.7, 'aum': 10200},
        {'name': 'ICICI Pru Smallcap', 'nav': 134.12, 'return_1y': 17.2, 'return_3y': 20.5, 'return_5y': 16.2, 'expense_ratio': 0.84, 'rating': 4.4, 'aum': 8900},
        {'name': 'Tata Small Cap', 'nav': 112.89, 'return_1y': 16.9, 'return_3y': 20.2, 'return_5y': 15.9, 'expense_ratio': 0.86, 'rating': 4.3, 'aum': 7800},
    ],
    'debt': [
        {'name': 'HDFC Corporate Bond', 'nav': 45.67, 'return_1y': 7.2, 'return_3y': 7.8, 'return_5y': 7.5, 'expense_ratio': 0.35, 'rating': 4.5, 'aum': 18500},
        {'name': 'ICICI Pru Corp Bond', 'nav': 38.90, 'return_1y': 7.0, 'return_3y': 7.6, 'return_5y': 7.3, 'expense_ratio': 0.38, 'rating': 4.3, 'aum': 16200},
        {'name': 'Axis Banking PSU', 'nav': 52.34, 'return_1y': 7.5, 'return_3y': 8.1, 'return_5y': 7.8, 'expense_ratio': 0.32, 'rating': 4.6, 'aum': 14800},
        {'name': 'SBI Magnum Income', 'nav': 67.89, 'return_1y': 6.8, 'return_3y': 7.4, 'return_5y': 7.1, 'expense_ratio': 0.40, 'rating': 4.2, 'aum': 12500},
        {'name': 'Kotak Bond', 'nav': 56.12, 'return_1y': 7.3, 'return_3y': 7.9, 'return_5y': 7.6, 'expense_ratio': 0.36, 'rating': 4.4, 'aum': 11900},
        {'name': 'UTI Bond', 'nav': 43.45, 'return_1y': 6.9, 'return_3y': 7.5, 'return_5y': 7.2, 'expense_ratio': 0.39, 'rating': 4.1, 'aum': 10200},
        {'name': 'Nippon Income', 'nav': 78.23, 'return_1y': 7.1, 'return_3y': 7.7, 'return_5y': 7.4, 'expense_ratio': 0.37, 'rating': 4.3, 'aum': 9800},
        {'name': 'Franklin Income Opp', 'nav': 89.56, 'return_1y': 7.4, 'return_3y': 8.0, 'return_5y': 7.7, 'expense_ratio': 0.34, 'rating': 4.5, 'aum': 11200},
        {'name': 'DSP Bond', 'nav': 34.78, 'return_1y': 6.7, 'return_3y': 7.3, 'return_5y': 7.0, 'expense_ratio': 0.41, 'rating': 4.0, 'aum': 8500},
        {'name': 'Aditya Birla Corp Bond', 'nav': 61.23, 'return_1y': 7.2, 'return_3y': 7.8, 'return_5y': 7.5, 'expense_ratio': 0.35, 'rating': 4.4, 'aum': 10800},
    ],
    'hybrid': [
        {'name': 'HDFC Balanced Adv', 'nav': 312.45, 'return_1y': 10.5, 'return_3y': 12.2, 'return_5y': 10.8, 'expense_ratio': 0.58, 'rating': 4.6, 'aum': 22500},
        {'name': 'ICICI Pru Eq & Debt', 'nav': 267.89, 'return_1y': 10.2, 'return_3y': 11.9, 'return_5y': 10.5, 'expense_ratio': 0.62, 'rating': 4.4, 'aum': 19800},
        {'name': 'SBI Equity Hybrid', 'nav': 189.34, 'return_1y': 9.8, 'return_3y': 11.5, 'return_5y': 10.2, 'expense_ratio': 0.65, 'rating': 4.3, 'aum': 17200},
        {'name': 'Mirae Hybrid Equity', 'nav': 234.67, 'return_1y': 10.8, 'return_3y': 12.5, 'return_5y': 11.1, 'expense_ratio': 0.55, 'rating': 4.7, 'aum': 20500},
        {'name': 'Axis Balanced Adv', 'nav': 156.12, 'return_1y': 10.3, 'return_3y': 12.0, 'return_5y': 10.6, 'expense_ratio': 0.60, 'rating': 4.5, 'aum': 18900},
        {'name': 'Kotak Equity Hybrid', 'nav': 198.45, 'return_1y': 9.9, 'return_3y': 11.6, 'return_5y': 10.3, 'expense_ratio': 0.63, 'rating': 4.2, 'aum': 15600},
        {'name': 'DSP Equity & Bond', 'nav': 223.78, 'return_1y': 10.1, 'return_3y': 11.8, 'return_5y': 10.4, 'expense_ratio': 0.61, 'rating': 4.4, 'aum': 16800},
        {'name': 'UTI Balanced Adv', 'nav': 178.90, 'return_1y': 9.7, 'return_3y': 11.4, 'return_5y': 10.1, 'expense_ratio': 0.66, 'rating': 4.1, 'aum': 14200},
    ],
    'elss': [
        {'name': 'Axis Long Term Eq', 'nav': 89.45, 'return_1y': 13.8, 'return_3y': 16.2, 'return_5y': 13.5, 'expense_ratio': 0.68, 'rating': 4.8, 'aum': 16500},
        {'name': 'Mirae Tax Saver', 'nav': 67.89, 'return_1y': 14.2, 'return_3y': 16.8, 'return_5y': 14.1, 'expense_ratio': 0.62, 'rating': 4.9, 'aum': 18200},
        {'name': 'HDFC TaxSaver', 'nav': 123.45, 'return_1y': 13.5, 'return_3y': 15.9, 'return_5y': 13.2, 'expense_ratio': 0.70, 'rating': 4.6, 'aum': 14800},
        {'name': 'ICICI Pru LT Equity', 'nav': 98.76, 'return_1y': 13.1, 'return_3y': 15.5, 'return_5y': 12.9, 'expense_ratio': 0.72, 'rating': 4.5, 'aum': 13500},
        {'name': 'DSP Tax Saver', 'nav': 112.34, 'return_1y': 13.9, 'return_3y': 16.3, 'return_5y': 13.6, 'expense_ratio': 0.66, 'rating': 4.7, 'aum': 15200},
        {'name': 'Kotak Tax Saver', 'nav': 78.90, 'return_1y': 12.8, 'return_3y': 15.2, 'return_5y': 12.6, 'expense_ratio': 0.74, 'rating': 4.3, 'aum': 11900},
    ]
}

# Flatten for easy access
ALL_MUTUAL_FUNDS = []
for category, funds in MUTUAL_FUNDS_DATABASE.items():
    for fund in funds:
        fund['category'] = category.replace('_', ' ').title()
        ALL_MUTUAL_FUNDS.append(fund)

# Configuration
HISTORICAL_YEARS = 5
UPDATE_FREQUENCY = "15m"
START_DATE = (datetime.now() - timedelta(days=365*HISTORICAL_YEARS)).strftime('%Y-%m-%d')
END_DATE = datetime.now().strftime('%Y-%m-%d')

NEWS_SOURCES = {
    'google_finance': 'https://news.google.com/rss/search?q=indian+stock+market&hl=en-IN&gl=IN&ceid=IN:en',
    'google_ipo': 'https://news.google.com/rss/search?q=IPO+india&hl=en-IN&gl=IN&ceid=IN:en',
    'et_market': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
    'et_stocks': 'https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms',
    'moneycontrol_market': 'https://www.moneycontrol.com/rss/marketreports.xml',
    'moneycontrol_results': 'https://www.moneycontrol.com/rss/results.xml'
}

DATABASE_PATH = "data/sarthak_nivesh.db"
DATA_FOLDER = "data"
PREDICTION_DAYS = [7, 30, 90]
CONFIDENCE_THRESHOLD = 0.7
IPO_ANALYSIS_DAYS = [30, 60, 90]
PAGE_TITLE = "सार्थक निवेश - Smart Investment Platform"
PAGE_ICON = "📈"
LAYOUT = "wide"

TEAM_MEMBERS = ["Aman Jain", "Rohit Fogla", "Vanshita Mehta", "Disita Tirthani"]

print(f"✅ Enhanced Config: {len(STOCK_SYMBOLS)} stocks, {len(ALL_MUTUAL_FUNDS)} mutual funds")
