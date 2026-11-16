# सार्थक निवेश - Enhanced Configuration File
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import os
import sys
from datetime import datetime, timedelta

# Ensure Unicode output works even on consoles that don't support emojis
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

# API Keys
ALPHA_VANTAGE_API_KEY = "3ZTEB9EMFP7GAAIY"
NEWS_API_KEY = "7b3a5054a78143be90dfdc9472ed5b20"
GROQ_API_KEY = "your_groq_api_key_here"

# Project Configuration
PROJECT_NAME = "सार्थक निवेश"
PROJECT_DESCRIPTION = "AI-Powered Indian Stock Market Analysis & IPO Prediction Platform"

# EXPANDED STOCK UNIVERSE - 50+ Indian Stocks
STOCK_SYMBOLS = {
    # Banking & Financial Services (15 stocks)
    'HDFCBANK.NS': 'HDFC Bank',
    'ICICIBANK.NS': 'ICICI Bank', 
    'SBIN.NS': 'State Bank of India',
    'AXISBANK.NS': 'Axis Bank',
    'KOTAKBANK.NS': 'Kotak Mahindra Bank',
    'INDUSINDBK.NS': 'IndusInd Bank',
    'FEDERALBNK.NS': 'Federal Bank',
    'BANDHANBNK.NS': 'Bandhan Bank',
    'IDFCFIRSTB.NS': 'IDFC First Bank',
    'PNB.NS': 'Punjab National Bank',
    'BANKBARODA.NS': 'Bank of Baroda',
    'CANBK.NS': 'Canara Bank',
    'BAJFINANCE.NS': 'Bajaj Finance',
    'BAJAJFINSV.NS': 'Bajaj Finserv',
    'HDFCLIFE.NS': 'HDFC Life Insurance',
    
    # Information Technology (10 stocks)
    'TCS.NS': 'Tata Consultancy Services',
    'INFY.NS': 'Infosys',
    'WIPRO.NS': 'Wipro',
    'HCLTECH.NS': 'HCL Technologies',
    'TECHM.NS': 'Tech Mahindra',
    'LTI.NS': 'LTI Mindtree',
    'MPHASIS.NS': 'Mphasis',
    'COFORGE.NS': 'Coforge',
    'PERSISTENT.NS': 'Persistent Systems',
    'LTTS.NS': 'L&T Technology Services',
    
    # Energy & Infrastructure (8 stocks)
    'RELIANCE.NS': 'Reliance Industries',
    'NTPC.NS': 'NTPC',
    'POWERGRID.NS': 'Power Grid Corporation',
    'ONGC.NS': 'Oil & Natural Gas Corporation',
    'IOC.NS': 'Indian Oil Corporation',
    'BPCL.NS': 'Bharat Petroleum Corporation',
    'GAIL.NS': 'GAIL India',
    'ADANIGREEN.NS': 'Adani Green Energy',
    
    # FMCG (8 stocks)
    'HINDUNILVR.NS': 'Hindustan Unilever',
    'ITC.NS': 'ITC',
    'NESTLEIND.NS': 'Nestlé India',
    'BRITANNIA.NS': 'Britannia Industries',
    'DABUR.NS': 'Dabur India',
    'MARICO.NS': 'Marico',
    'GODREJCP.NS': 'Godrej Consumer Products',
    'COLPAL.NS': 'Colgate-Palmolive India',
    
    # Automobile (6 stocks)
    'MARUTI.NS': 'Maruti Suzuki',
    'TATAMOTORS.NS': 'Tata Motors',
    'M&M.NS': 'Mahindra & Mahindra',
    'BAJAJ-AUTO.NS': 'Bajaj Auto',
    'HEROMOTOCO.NS': 'Hero MotoCorp',
    'EICHERMOT.NS': 'Eicher Motors',
    
    # Pharmaceuticals (6 stocks)
    'SUNPHARMA.NS': 'Sun Pharma',
    'DRREDDY.NS': 'Dr Reddy\'s Laboratories',
    'CIPLA.NS': 'Cipla',
    'DIVISLAB.NS': 'Divi\'s Laboratories',
    'BIOCON.NS': 'Biocon',
    'LUPIN.NS': 'Lupin',
    
    # Metals & Heavy Industry (5 stocks)
    'LT.NS': 'Larsen & Toubro',
    'TATASTEEL.NS': 'Tata Steel',
    'HINDALCO.NS': 'Hindalco Industries',
    'JSWSTEEL.NS': 'JSW Steel',
    'VEDL.NS': 'Vedanta',
    
    # Telecom & Media (4 stocks)
    'BHARTIARTL.NS': 'Bharti Airtel',
    'JIO.NS': 'Reliance Jio',
    'ZEEL.NS': 'Zee Entertainment',
    'SUNTV.NS': 'Sun TV Network'
}

# EXPANDED MUTUAL FUNDS UNIVERSE - 50+ Funds
MUTUAL_FUNDS = {
    # Large Cap Equity Funds (15 funds)
    'SBI_BLUECHIP': {
        'name': 'SBI Bluechip Fund',
        'category': 'Large Cap',
        'nav': 89.45,
        'return_1y': 12.5,
        'return_3y': 14.2,
        'return_5y': 11.8,
        'expense_ratio': 0.65,
        'rating': 4.5,
        'aum': 25000,
        'fund_house': 'SBI Mutual Fund',
        'min_sip': 500
    },
    'HDFC_TOP100': {
        'name': 'HDFC Top 100 Fund',
        'category': 'Large Cap',
        'nav': 156.78,
        'return_1y': 13.2,
        'return_3y': 15.1,
        'return_5y': 12.4,
        'expense_ratio': 0.58,
        'rating': 4.3,
        'aum': 18500,
        'fund_house': 'HDFC Mutual Fund',
        'min_sip': 1000
    },
    'ICICI_BLUECHIP': {
        'name': 'ICICI Prudential Bluechip Fund',
        'category': 'Large Cap',
        'nav': 234.56,
        'return_1y': 11.8,
        'return_3y': 13.5,
        'return_5y': 10.9,
        'expense_ratio': 0.72,
        'rating': 4.1,
        'aum': 12300,
        'fund_house': 'ICICI Prudential MF',
        'min_sip': 1000
    },
    'AXIS_BLUECHIP': {
        'name': 'Axis Bluechip Fund',
        'category': 'Large Cap',
        'nav': 67.89,
        'return_1y': 12.8,
        'return_3y': 14.5,
        'return_5y': 11.2,
        'expense_ratio': 0.68,
        'rating': 4.2,
        'aum': 8900,
        'fund_house': 'Axis Mutual Fund',
        'min_sip': 500
    },
    'KOTAK_BLUECHIP': {
        'name': 'Kotak Bluechip Fund',
        'category': 'Large Cap',
        'nav': 145.23,
        'return_1y': 13.5,
        'return_3y': 15.8,
        'return_5y': 12.1,
        'expense_ratio': 0.61,
        'rating': 4.4,
        'aum': 15600,
        'fund_house': 'Kotak Mutual Fund',
        'min_sip': 1000
    },
    'UTI_MASTERSHARE': {
        'name': 'UTI Mastershare Fund',
        'category': 'Large Cap',
        'nav': 98.76,
        'return_1y': 11.9,
        'return_3y': 13.8,
        'return_5y': 10.5,
        'expense_ratio': 0.75,
        'rating': 3.9,
        'aum': 7800,
        'fund_house': 'UTI Mutual Fund',
        'min_sip': 500
    },
    'FRANKLIN_BLUECHIP': {
        'name': 'Franklin India Bluechip Fund',
        'category': 'Large Cap',
        'nav': 178.45,
        'return_1y': 12.3,
        'return_3y': 14.1,
        'return_5y': 11.6,
        'expense_ratio': 0.69,
        'rating': 4.0,
        'aum': 9200,
        'fund_house': 'Franklin Templeton MF',
        'min_sip': 1000
    },
    'MIRAE_LARGECAP': {
        'name': 'Mirae Asset Large Cap Fund',
        'category': 'Large Cap',
        'nav': 123.67,
        'return_1y': 13.8,
        'return_3y': 16.2,
        'return_5y': 13.1,
        'expense_ratio': 0.55,
        'rating': 4.6,
        'aum': 11400,
        'fund_house': 'Mirae Asset MF',
        'min_sip': 1000
    },
    'NIPPON_LARGECAP': {
        'name': 'Nippon India Large Cap Fund',
        'category': 'Large Cap',
        'nav': 87.34,
        'return_1y': 12.1,
        'return_3y': 13.9,
        'return_5y': 10.8,
        'expense_ratio': 0.71,
        'rating': 4.1,
        'aum': 6700,
        'fund_house': 'Nippon India MF',
        'min_sip': 500
    },
    'CANARA_BLUECHIP': {
        'name': 'Canara Robeco Bluechip Equity Fund',
        'category': 'Large Cap',
        'nav': 156.89,
        'return_1y': 11.7,
        'return_3y': 13.4,
        'return_5y': 10.3,
        'expense_ratio': 0.78,
        'rating': 3.8,
        'aum': 5400,
        'fund_house': 'Canara Robeco MF',
        'min_sip': 1000
    },
    'INVESCO_LARGECAP': {
        'name': 'Invesco India Large Cap Fund',
        'category': 'Large Cap',
        'nav': 134.56,
        'return_1y': 12.6,
        'return_3y': 14.7,
        'return_5y': 11.4,
        'expense_ratio': 0.66,
        'rating': 4.2,
        'aum': 8100,
        'fund_house': 'Invesco Mutual Fund',
        'min_sip': 1000
    },
    'TATA_LARGECAP': {
        'name': 'Tata Large Cap Fund',
        'category': 'Large Cap',
        'nav': 76.23,
        'return_1y': 11.4,
        'return_3y': 13.1,
        'return_5y': 9.8,
        'expense_ratio': 0.82,
        'rating': 3.7,
        'aum': 4200,
        'fund_house': 'Tata Mutual Fund',
        'min_sip': 500
    },
    'MAHINDRA_BLUECHIP': {
        'name': 'Mahindra Manulife Large Cap Fund',
        'category': 'Large Cap',
        'nav': 198.45,
        'return_1y': 12.9,
        'return_3y': 15.3,
        'return_5y': 12.0,
        'expense_ratio': 0.63,
        'rating': 4.3,
        'aum': 6800,
        'fund_house': 'Mahindra Manulife MF',
        'min_sip': 1000
    },
    'EDELWEISS_LARGECAP': {
        'name': 'Edelweiss Large Cap Fund',
        'category': 'Large Cap',
        'nav': 89.67,
        'return_1y': 11.8,
        'return_3y': 13.6,
        'return_5y': 10.7,
        'expense_ratio': 0.74,
        'rating': 3.9,
        'aum': 3900,
        'fund_house': 'Edelweiss Mutual Fund',
        'min_sip': 500
    },
    'BARODA_LARGECAP': {
        'name': 'Baroda BNP Paribas Large Cap Fund',
        'category': 'Large Cap',
        'nav': 167.34,
        'return_1y': 12.4,
        'return_3y': 14.0,
        'return_5y': 11.1,
        'expense_ratio': 0.69,
        'rating': 4.0,
        'aum': 5600,
        'fund_house': 'Baroda BNP Paribas MF',
        'min_sip': 1000
    },
    
    # Mid Cap Equity Funds (12 funds)
    'HDFC_MIDCAP': {
        'name': 'HDFC Mid-Cap Opportunities Fund',
        'category': 'Mid Cap',
        'nav': 234.78,
        'return_1y': 18.5,
        'return_3y': 22.1,
        'return_5y': 16.8,
        'expense_ratio': 0.85,
        'rating': 4.7,
        'aum': 14200,
        'fund_house': 'HDFC Mutual Fund',
        'min_sip': 1000
    },
    'SBI_MIDCAP': {
        'name': 'SBI Magnum Midcap Fund',
        'category': 'Mid Cap',
        'nav': 156.89,
        'return_1y': 17.2,
        'return_3y': 20.8,
        'return_5y': 15.4,
        'expense_ratio': 0.92,
        'rating': 4.4,
        'aum': 9800,
        'fund_house': 'SBI Mutual Fund',
        'min_sip': 500
    },
    'ICICI_MIDCAP': {
        'name': 'ICICI Prudential Midcap Fund',
        'category': 'Mid Cap',
        'nav': 189.45,
        'return_1y': 16.8,
        'return_3y': 19.9,
        'return_5y': 14.7,
        'expense_ratio': 0.88,
        'rating': 4.2,
        'aum': 11600,
        'fund_house': 'ICICI Prudential MF',
        'min_sip': 1000
    },
    'AXIS_MIDCAP': {
        'name': 'Axis Midcap Fund',
        'category': 'Mid Cap',
        'nav': 123.67,
        'return_1y': 19.1,
        'return_3y': 23.4,
        'return_5y': 17.9,
        'expense_ratio': 0.79,
        'rating': 4.8,
        'aum': 8900,
        'fund_house': 'Axis Mutual Fund',
        'min_sip': 500
    },
    'KOTAK_MIDCAP': {
        'name': 'Kotak Emerging Equity Fund',
        'category': 'Mid Cap',
        'nav': 267.34,
        'return_1y': 20.3,
        'return_3y': 24.7,
        'return_5y': 18.6,
        'expense_ratio': 0.81,
        'rating': 4.9,
        'aum': 16800,
        'fund_house': 'Kotak Mutual Fund',
        'min_sip': 1000
    },
    'MIRAE_MIDCAP': {
        'name': 'Mirae Asset Emerging Bluechip Fund',
        'category': 'Mid Cap',
        'nav': 198.76,
        'return_1y': 21.5,
        'return_3y': 26.2,
        'return_5y': 19.8,
        'expense_ratio': 0.76,
        'rating': 5.0,
        'aum': 22400,
        'fund_house': 'Mirae Asset MF',
        'min_sip': 1000
    },
    'FRANKLIN_MIDCAP': {
        'name': 'Franklin India Prima Fund',
        'category': 'Mid Cap',
        'nav': 145.23,
        'return_1y': 16.4,
        'return_3y': 19.1,
        'return_5y': 14.2,
        'expense_ratio': 0.94,
        'rating': 4.1,
        'aum': 7300,
        'fund_house': 'Franklin Templeton MF',
        'min_sip': 1000
    },
    'UTI_MIDCAP': {
        'name': 'UTI Mid Cap Fund',
        'category': 'Mid Cap',
        'nav': 178.45,
        'return_1y': 17.8,
        'return_3y': 21.3,
        'return_5y': 15.9,
        'expense_ratio': 0.89,
        'rating': 4.3,
        'aum': 6700,
        'fund_house': 'UTI Mutual Fund',
        'min_sip': 500
    },
    'NIPPON_MIDCAP': {
        'name': 'Nippon India Growth Fund',
        'category': 'Mid Cap',
        'nav': 234.67,
        'return_1y': 18.9,
        'return_3y': 22.6,
        'return_5y': 16.5,
        'expense_ratio': 0.86,
        'rating': 4.5,
        'aum': 9200,
        'fund_house': 'Nippon India MF',
        'min_sip': 500
    },
    'CANARA_MIDCAP': {
        'name': 'Canara Robeco Emerging Equities Fund',
        'category': 'Mid Cap',
        'nav': 167.89,
        'return_1y': 16.7,
        'return_3y': 19.8,
        'return_5y': 14.6,
        'expense_ratio': 0.91,
        'rating': 4.0,
        'aum': 5400,
        'fund_house': 'Canara Robeco MF',
        'min_sip': 1000
    },
    'INVESCO_MIDCAP': {
        'name': 'Invesco India Mid Cap Fund',
        'category': 'Mid Cap',
        'nav': 189.34,
        'return_1y': 17.6,
        'return_3y': 20.9,
        'return_5y': 15.3,
        'expense_ratio': 0.87,
        'rating': 4.2,
        'aum': 7800,
        'fund_house': 'Invesco Mutual Fund',
        'min_sip': 1000
    },
    'TATA_MIDCAP': {
        'name': 'Tata Mid Cap Growth Fund',
        'category': 'Mid Cap',
        'nav': 134.56,
        'return_1y': 16.2,
        'return_3y': 18.7,
        'return_5y': 13.9,
        'expense_ratio': 0.95,
        'rating': 3.8,
        'aum': 4600,
        'fund_house': 'Tata Mutual Fund',
        'min_sip': 500
    },
    
    # Small Cap Equity Funds (8 funds)
    'SBI_SMALLCAP': {
        'name': 'SBI Small Cap Fund',
        'category': 'Small Cap',
        'nav': 267.89,
        'return_1y': 25.4,
        'return_3y': 28.7,
        'return_5y': 21.3,
        'expense_ratio': 1.15,
        'rating': 4.6,
        'aum': 8900,
        'fund_house': 'SBI Mutual Fund',
        'min_sip': 500
    },
    'HDFC_SMALLCAP': {
        'name': 'HDFC Small Cap Fund',
        'category': 'Small Cap',
        'nav': 198.45,
        'return_1y': 23.8,
        'return_3y': 26.9,
        'return_5y': 19.7,
        'expense_ratio': 1.08,
        'rating': 4.4,
        'aum': 12400,
        'fund_house': 'HDFC Mutual Fund',
        'min_sip': 1000
    },
    'AXIS_SMALLCAP': {
        'name': 'Axis Small Cap Fund',
        'category': 'Small Cap',
        'nav': 156.78,
        'return_1y': 27.2,
        'return_3y': 31.5,
        'return_5y': 23.8,
        'expense_ratio': 1.02,
        'rating': 4.8,
        'aum': 6700,
        'fund_house': 'Axis Mutual Fund',
        'min_sip': 500
    },
    'KOTAK_SMALLCAP': {
        'name': 'Kotak Small Cap Fund',
        'category': 'Small Cap',
        'nav': 234.67,
        'return_1y': 26.8,
        'return_3y': 30.1,
        'return_5y': 22.4,
        'expense_ratio': 1.12,
        'rating': 4.7,
        'aum': 9800,
        'fund_house': 'Kotak Mutual Fund',
        'min_sip': 1000
    },
    'NIPPON_SMALLCAP': {
        'name': 'Nippon India Small Cap Fund',
        'category': 'Small Cap',
        'nav': 189.34,
        'return_1y': 24.6,
        'return_3y': 27.8,
        'return_5y': 20.1,
        'expense_ratio': 1.18,
        'rating': 4.3,
        'aum': 7200,
        'fund_house': 'Nippon India MF',
        'min_sip': 500
    },
    'UTI_SMALLCAP': {
        'name': 'UTI Small Cap Fund',
        'category': 'Small Cap',
        'nav': 145.89,
        'return_1y': 22.9,
        'return_3y': 25.4,
        'return_5y': 18.6,
        'expense_ratio': 1.25,
        'rating': 4.0,
        'aum': 5400,
        'fund_house': 'UTI Mutual Fund',
        'min_sip': 500
    },
    'FRANKLIN_SMALLCAP': {
        'name': 'Franklin India Smaller Companies Fund',
        'category': 'Small Cap',
        'nav': 178.67,
        'return_1y': 23.5,
        'return_3y': 26.2,
        'return_5y': 19.3,
        'expense_ratio': 1.21,
        'rating': 4.1,
        'aum': 6100,
        'fund_house': 'Franklin Templeton MF',
        'min_sip': 1000
    },
    'MIRAE_SMALLCAP': {
        'name': 'Mirae Asset India Opportunities Fund',
        'category': 'Small Cap',
        'nav': 267.45,
        'return_1y': 28.7,
        'return_3y': 33.2,
        'return_5y': 25.1,
        'expense_ratio': 0.98,
        'rating': 4.9,
        'aum': 11600,
        'fund_house': 'Mirae Asset MF',
        'min_sip': 1000
    },
    
    # Debt Funds (10 funds)
    'HDFC_SHORTTERM': {
        'name': 'HDFC Short Term Debt Fund',
        'category': 'Debt',
        'nav': 45.67,
        'return_1y': 7.2,
        'return_3y': 6.8,
        'return_5y': 7.1,
        'expense_ratio': 0.45,
        'rating': 4.3,
        'aum': 18900,
        'fund_house': 'HDFC Mutual Fund',
        'min_sip': 1000
    },
    'SBI_SHORTTERM': {
        'name': 'SBI Short Term Debt Fund',
        'category': 'Debt',
        'nav': 38.94,
        'return_1y': 6.9,
        'return_3y': 6.5,
        'return_5y': 6.8,
        'expense_ratio': 0.52,
        'rating': 4.1,
        'aum': 14200,
        'fund_house': 'SBI Mutual Fund',
        'min_sip': 500
    },
    'ICICI_SHORTTERM': {
        'name': 'ICICI Prudential Short Term Fund',
        'category': 'Debt',
        'nav': 56.78,
        'return_1y': 7.1,
        'return_3y': 6.7,
        'return_5y': 7.0,
        'expense_ratio': 0.48,
        'rating': 4.2,
        'aum': 16700,
        'fund_house': 'ICICI Prudential MF',
        'min_sip': 1000
    },
    'AXIS_SHORTTERM': {
        'name': 'Axis Short Term Fund',
        'category': 'Debt',
        'nav': 42.34,
        'return_1y': 7.0,
        'return_3y': 6.6,
        'return_5y': 6.9,
        'expense_ratio': 0.49,
        'rating': 4.0,
        'aum': 9800,
        'fund_house': 'Axis Mutual Fund',
        'min_sip': 500
    },
    'KOTAK_BOND': {
        'name': 'Kotak Bond Fund',
        'category': 'Debt',
        'nav': 67.89,
        'return_1y': 7.4,
        'return_3y': 7.0,
        'return_5y': 7.3,
        'expense_ratio': 0.44,
        'rating': 4.4,
        'aum': 12400,
        'fund_house': 'Kotak Mutual Fund',
        'min_sip': 1000
    },
    'UTI_BOND': {
        'name': 'UTI Bond Fund',
        'category': 'Debt',
        'nav': 34.56,
        'return_1y': 6.8,
        'return_3y': 6.4,
        'return_5y': 6.7,
        'expense_ratio': 0.55,
        'rating': 3.9,
        'aum': 8900,
        'fund_house': 'UTI Mutual Fund',
        'min_sip': 500
    },
    'FRANKLIN_SHORTTERM': {
        'name': 'Franklin India Short Term Income Fund',
        'category': 'Debt',
        'nav': 78.45,
        'return_1y': 7.3,
        'return_3y': 6.9,
        'return_5y': 7.2,
        'expense_ratio': 0.46,
        'rating': 4.2,
        'aum': 11200,
        'fund_house': 'Franklin Templeton MF',
        'min_sip': 1000
    },
    'NIPPON_SHORTTERM': {
        'name': 'Nippon India Short Term Fund',
        'category': 'Debt',
        'nav': 51.23,
        'return_1y': 6.7,
        'return_3y': 6.3,
        'return_5y': 6.6,
        'expense_ratio': 0.53,
        'rating': 3.8,
        'aum': 7600,
        'fund_house': 'Nippon India MF',
        'min_sip': 500
    },
    'MIRAE_BOND': {
        'name': 'Mirae Asset Short Term Fund',
        'category': 'Debt',
        'nav': 89.67,
        'return_1y': 7.5,
        'return_3y': 7.1,
        'return_5y': 7.4,
        'expense_ratio': 0.42,
        'rating': 4.5,
        'aum': 13800,
        'fund_house': 'Mirae Asset MF',
        'min_sip': 1000
    },
    'CANARA_BOND': {
        'name': 'Canara Robeco Short Duration Fund',
        'category': 'Debt',
        'nav': 63.45,
        'return_1y': 6.9,
        'return_3y': 6.5,
        'return_5y': 6.8,
        'expense_ratio': 0.51,
        'rating': 4.0,
        'aum': 6700,
        'fund_house': 'Canara Robeco MF',
        'min_sip': 1000
    },
    
    # Hybrid Funds (8 funds)
    'HDFC_BALANCED': {
        'name': 'HDFC Balanced Advantage Fund',
        'category': 'Hybrid',
        'nav': 123.45,
        'return_1y': 9.8,
        'return_3y': 10.2,
        'return_5y': 9.5,
        'expense_ratio': 0.78,
        'rating': 4.4,
        'aum': 22400,
        'fund_house': 'HDFC Mutual Fund',
        'min_sip': 1000
    },
    'SBI_HYBRID': {
        'name': 'SBI Equity Hybrid Fund',
        'category': 'Hybrid',
        'nav': 89.67,
        'return_1y': 9.2,
        'return_3y': 9.6,
        'return_5y': 8.9,
        'expense_ratio': 0.85,
        'rating': 4.1,
        'aum': 16800,
        'fund_house': 'SBI Mutual Fund',
        'min_sip': 500
    },
    'ICICI_BALANCED': {
        'name': 'ICICI Prudential Balanced Advantage Fund',
        'category': 'Hybrid',
        'nav': 156.78,
        'return_1y': 10.1,
        'return_3y': 10.5,
        'return_5y': 9.8,
        'expense_ratio': 0.82,
        'rating': 4.3,
        'aum': 19200,
        'fund_house': 'ICICI Prudential MF',
        'min_sip': 1000
    },
    'AXIS_HYBRID': {
        'name': 'Axis Hybrid Fund',
        'category': 'Hybrid',
        'nav': 67.34,
        'return_1y': 9.5,
        'return_3y': 9.9,
        'return_5y': 9.2,
        'expense_ratio': 0.79,
        'rating': 4.2,
        'aum': 12600,
        'fund_house': 'Axis Mutual Fund',
        'min_sip': 500
    },
    'KOTAK_BALANCED': {
        'name': 'Kotak Balanced Advantage Fund',
        'category': 'Hybrid',
        'nav': 198.45,
        'return_1y': 10.4,
        'return_3y': 10.8,
        'return_5y': 10.1,
        'expense_ratio': 0.75,
        'rating': 4.5,
        'aum': 24600,
        'fund_house': 'Kotak Mutual Fund',
        'min_sip': 1000
    },
    'UTI_BALANCED': {
        'name': 'UTI Balanced Advantage Fund',
        'category': 'Hybrid',
        'nav': 134.56,
        'return_1y': 9.0,
        'return_3y': 9.4,
        'return_5y': 8.7,
        'expense_ratio': 0.88,
        'rating': 3.9,
        'aum': 8900,
        'fund_house': 'UTI Mutual Fund',
        'min_sip': 500
    },
    'FRANKLIN_BALANCED': {
        'name': 'Franklin India Balanced Fund',
        'category': 'Hybrid',
        'nav': 178.67,
        'return_1y': 9.7,
        'return_3y': 10.1,
        'return_5y': 9.4,
        'expense_ratio': 0.81,
        'rating': 4.0,
        'aum': 11400,
        'fund_house': 'Franklin Templeton MF',
        'min_sip': 1000
    },
    'MIRAE_HYBRID': {
        'name': 'Mirae Asset Hybrid Equity Fund',
        'category': 'Hybrid',
        'nav': 245.89,
        'return_1y': 10.6,
        'return_3y': 11.0,
        'return_5y': 10.3,
        'expense_ratio': 0.73,
        'rating': 4.6,
        'aum': 18700,
        'fund_house': 'Mirae Asset MF',
        'min_sip': 1000
    }
}

# Data Configuration
HISTORICAL_YEARS = 5
UPDATE_FREQUENCY = "15min"  # More frequent updates for dynamic experience
START_DATE = (datetime.now() - timedelta(days=365*HISTORICAL_YEARS)).strftime('%Y-%m-%d')
END_DATE = datetime.now().strftime('%Y-%m-%d')

# Enhanced News Sources (No API Keys Required)
NEWS_SOURCES = {
    'google_finance': 'https://news.google.com/rss/search?q=indian+stock+market&hl=en-IN&gl=IN&ceid=IN:en',
    'google_ipo': 'https://news.google.com/rss/search?q=IPO+india&hl=en-IN&gl=IN&ceid=IN:en',
    'et_market': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
    'et_stocks': 'https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms',
    'moneycontrol_market': 'https://www.moneycontrol.com/rss/marketreports.xml',
    'moneycontrol_results': 'https://www.moneycontrol.com/rss/results.xml',
    'business_standard': 'https://www.business-standard.com/rss/markets-106.rss',
    'livemint_market': 'https://www.livemint.com/rss/markets',
    'financial_express': 'https://www.financialexpress.com/market/rss'
}

# Database Configuration
DATABASE_PATH = "data/sarthak_nivesh_enhanced.db"
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
TEAM_MEMBERS = [
    "Aman Jain",
    "Rohit Fogla", 
    "Vanshita Mehta",
    "Disita Tirthani"
]

# Auto-refresh Configuration
AUTO_REFRESH_INTERVAL = 900  # 15 minutes in seconds
REAL_TIME_UPDATE = True

print(f"✅ Enhanced Configuration loaded for {PROJECT_NAME}")
print(f"📊 Tracking {len(STOCK_SYMBOLS)} stocks across multiple sectors")
print(f"💰 Covering {len(MUTUAL_FUNDS)} mutual funds across all categories")
print(f"👥 Team: {', '.join(TEAM_MEMBERS)}")
print(f"🔄 Auto-refresh enabled: Every {AUTO_REFRESH_INTERVAL//60} minutes")