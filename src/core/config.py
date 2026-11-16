# सार्थक निवेश - Configuration File
# Author: Aman Jain (B.Tech 2023-27)

import os
import sys
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Ensure Unicode output works even on consoles that don't support emojis
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

# API Keys — loaded from .env, never hardcoded
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")  # Set via .env / env var; never hardcode a key here

# Project Configuration
PROJECT_NAME = "सार्थक निवेश"
PROJECT_DESCRIPTION = "AI-Powered Indian Stock Market Analysis & IPO Prediction Platform"

# Stock Universe - 100+ Selected Indian Stocks (Real NSE symbols)
STOCK_SYMBOLS = {
    # Banking & Financial Services (15 stocks)
    'HDFCBANK.NS': 'HDFC Bank',
    'ICICIBANK.NS': 'ICICI Bank', 
    'SBIN.NS': 'State Bank of India',
    'AXISBANK.NS': 'Axis Bank',
    'KOTAKBANK.NS': 'Kotak Mahindra Bank',
    'INDUSINDBK.NS': 'IndusInd Bank',
    'BANDHANBNK.NS': 'Bandhan Bank',
    'FEDERALBNK.NS': 'Federal Bank',
    'IDFCFIRSTB.NS': 'IDFC First Bank',
    'PNB.NS': 'Punjab National Bank',
    'BANKBARODA.NS': 'Bank of Baroda',
    'CANBK.NS': 'Canara Bank',
    'BAJFINANCE.NS': 'Bajaj Finance',
    'BAJAJFINSV.NS': 'Bajaj Finserv',
    'HDFCLIFE.NS': 'HDFC Life Insurance',
    
    # Information Technology (12 stocks)
    'TCS.NS': 'Tata Consultancy Services',
    'INFY.NS': 'Infosys',
    'WIPRO.NS': 'Wipro',
    'HCLTECH.NS': 'HCL Technologies',
    'TECHM.NS': 'Tech Mahindra',
    'LTI.NS': 'LTI Mindtree',
    'COFORGE.NS': 'Coforge',
    'MPHASIS.NS': 'Mphasis',
    'PERSISTENT.NS': 'Persistent Systems',
    'LTTS.NS': 'L&T Technology Services',
    'TATAELXSI.NS': 'Tata Elxsi',
    'OFSS.NS': 'Oracle Financial Services',
    
    # Energy & Infrastructure (15 stocks)
    'RELIANCE.NS': 'Reliance Industries',
    'NTPC.NS': 'NTPC',
    'POWERGRID.NS': 'Power Grid Corporation',
    'ONGC.NS': 'Oil & Natural Gas Corporation',
    'BPCL.NS': 'Bharat Petroleum',
    'IOC.NS': 'Indian Oil Corporation',
    'GAIL.NS': 'GAIL India',
    'COALINDIA.NS': 'Coal India',
    'ADANIGREEN.NS': 'Adani Green Energy',
    'ADANIPORTS.NS': 'Adani Ports',
    'ADANIENT.NS': 'Adani Enterprises',
    'TATAPOWER.NS': 'Tata Power',
    'TORNTPOWER.NS': 'Torrent Power',
    'NHPC.NS': 'NHPC',
    'SJVN.NS': 'SJVN',
    
    # FMCG & Consumer (12 stocks)
    'HINDUNILVR.NS': 'Hindustan Unilever',
    'ITC.NS': 'ITC',
    'NESTLEIND.NS': 'Nestlé India',
    'BRITANNIA.NS': 'Britannia Industries',
    'DABUR.NS': 'Dabur India',
    'MARICO.NS': 'Marico',
    'GODREJCP.NS': 'Godrej Consumer Products',
    'COLPAL.NS': 'Colgate-Palmolive India',
    'TATACONSUM.NS': 'Tata Consumer Products',
    'EMAMILTD.NS': 'Emami',
    'VBL.NS': 'Varun Beverages',
    'PGHH.NS': 'Procter & Gamble Hygiene',
    
    # Automobile & Auto Components (12 stocks)
    'MARUTI.NS': 'Maruti Suzuki',
    'TATAMOTORS.NS': 'Tata Motors',
    'M&M.NS': 'Mahindra & Mahindra',
    'BAJAJ-AUTO.NS': 'Bajaj Auto',
    'HEROMOTOCO.NS': 'Hero MotoCorp',
    'EICHERMOT.NS': 'Eicher Motors',
    'TVSMOTOR.NS': 'TVS Motor Company',
    'ASHOKLEY.NS': 'Ashok Leyland',
    'MOTHERSON.NS': 'Samvardhana Motherson',
    'BOSCHLTD.NS': 'Bosch',
    'APOLLOTYRE.NS': 'Apollo Tyres',
    'MRF.NS': 'MRF',
    
    # Pharmaceuticals & Healthcare (12 stocks)
    'SUNPHARMA.NS': 'Sun Pharmaceutical',
    'DRREDDY.NS': 'Dr Reddy\'s Laboratories',
    'CIPLA.NS': 'Cipla',
    'DIVISLAB.NS': 'Divi\'s Laboratories',
    'BIOCON.NS': 'Biocon',
    'LUPIN.NS': 'Lupin',
    'TORNTPHARM.NS': 'Torrent Pharmaceuticals',
    'ALKEM.NS': 'Alkem Laboratories',
    'AUROPHARMA.NS': 'Aurobindo Pharma',
    'ZYDUSLIFE.NS': 'Zydus Lifesciences',
    'APOLLOHOSP.NS': 'Apollo Hospitals',
    'FORTIS.NS': 'Fortis Healthcare',
    
    # Metals & Mining (10 stocks)
    'TATASTEEL.NS': 'Tata Steel',
    'JSWSTEEL.NS': 'JSW Steel',
    'HINDALCO.NS': 'Hindalco Industries',
    'VEDL.NS': 'Vedanta',
    'SAIL.NS': 'SAIL',
    'JINDALSTEL.NS': 'Jindal Steel & Power',
    'NMDC.NS': 'NMDC',
    'NATIONALUM.NS': 'National Aluminium',
    'HINDZINC.NS': 'Hindustan Zinc',
    'RATNAMANI.NS': 'Ratnamani Metals',
    
    # Cement & Construction (10 stocks)
    'LT.NS': 'Larsen & Toubro',
    'ULTRACEMCO.NS': 'UltraTech Cement',
    'GRASIM.NS': 'Grasim Industries',
    'AMBUJACEM.NS': 'Ambuja Cements',
    'ACC.NS': 'ACC',
    'SHREECEM.NS': 'Shree Cement',
    'JKCEMENT.NS': 'JK Cement',
    'RAMCOCEM.NS': 'Ramco Cements',
    'DALBHARAT.NS': 'Dalmia Bharat',
    'HEIDELBERG.NS': 'Heidelberg Cement India',
    
    # Telecom & Media (8 stocks)
    'BHARTIARTL.NS': 'Bharti Airtel',
    'IDEA.NS': 'Vodafone Idea',
    'INDIAMART.NS': 'IndiaMART InterMESH',
    'ZEEL.NS': 'Zee Entertainment',
    'SUNTV.NS': 'Sun TV Network',
    'PVRINOX.NS': 'PVR INOX',
    'NAZARA.NS': 'Nazara Technologies',
    'ROUTE.NS': 'Route Mobile',
    
    # Real Estate (8 stocks)
    'DLF.NS': 'DLF',
    'GODREJPROP.NS': 'Godrej Properties',
    'OBEROIRLTY.NS': 'Oberoi Realty',
    'PRESTIGE.NS': 'Prestige Estates',
    'BRIGADE.NS': 'Brigade Enterprises',
    'PHOENIXLTD.NS': 'Phoenix Mills',
    'SOBHA.NS': 'Sobha',
    'MAHLIFE.NS': 'Mahindra Lifespace',
    
    # Retail & E-commerce (6 stocks)
    'TRENT.NS': 'Trent (Westside)',
    'DMART.NS': 'Avenue Supermarts (DMart)',
    'ABFRL.NS': 'Aditya Birla Fashion',
    'SHOPERSTOP.NS': 'Shoppers Stop',
    'VMART.NS': 'V-Mart Retail',
    'SPENCERS.NS': 'Spencer\'s Retail',
}

# Additional stock mapping for easy access
INDIAN_STOCKS = {k.replace('.NS', ''): v for k, v in STOCK_SYMBOLS.items()}

# Data Configuration
HISTORICAL_YEARS = 5
UPDATE_FREQUENCY = "1h"  # Hourly updates
START_DATE = (datetime.now() - timedelta(days=365*HISTORICAL_YEARS)).strftime('%Y-%m-%d')
END_DATE = datetime.now().strftime('%Y-%m-%d')

# News Sources (No API Keys Required)
NEWS_SOURCES = {
    'google_finance': 'https://news.google.com/rss/search?q=indian+stock+market&hl=en-IN&gl=IN&ceid=IN:en',
    'google_ipo': 'https://news.google.com/rss/search?q=IPO+india&hl=en-IN&gl=IN&ceid=IN:en',
    'et_market': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
    'et_stocks': 'https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms',
    'moneycontrol_market': 'https://www.moneycontrol.com/rss/marketreports.xml',
    'moneycontrol_results': 'https://www.moneycontrol.com/rss/results.xml'
}

# Database Configuration
DATABASE_PATH = "data/sarthak_nivesh.db"
DATA_FOLDER = "data"

# Model Configuration
PREDICTION_DAYS = [7, 30, 90]  # Prediction horizons
CONFIDENCE_THRESHOLD = 0.7
IPO_ANALYSIS_DAYS = [30, 60, 90]  # Post-IPO analysis periods

# Streamlit Configuration
PAGE_TITLE = "सार्थक निवेश - Smart Investment Platform"
PAGE_ICON = "📈"
LAYOUT = "wide"

# Team Information
TEAM_MEMBERS = ["Aman Jain"]

print(f"✅ Configuration loaded for {PROJECT_NAME}")
print(f"📊 Tracking {len(STOCK_SYMBOLS)} stocks across multiple sectors")
print(f"👤 Author: {TEAM_MEMBERS[0]}")