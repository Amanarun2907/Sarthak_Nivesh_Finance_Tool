"""
🎯 ENHANCED SMART MONEY TRACKER - More Comprehensive Analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
import json
import warnings
warnings.filterwarnings('ignore')

# Indian Stocks Database
INDIAN_STOCKS = {
    'HDFCBANK.NS': 'HDFC Bank', 'ICICIBANK.NS': 'ICICI Bank', 'KOTAKBANK.NS': 'Kotak Bank',
    'SBIN.NS': 'State Bank', 'AXISBANK.NS': 'Axis Bank', 'INDUSINDBK.NS': 'IndusInd Bank',
    'BAJFINANCE.NS': 'Bajaj Finance', 'BAJAJFINSV.NS': 'Bajaj Finserv',
    'TCS.NS': 'TCS', 'INFY.NS': 'Infosys', 'WIPRO.NS': 'Wipro',
    'HCLTECH.NS': 'HCL Tech', 'TECHM.NS': 'Tech Mahindra',
    'HINDUNILVR.NS': 'Hindustan Unilever', 'ITC.NS': 'ITC', 'NESTLEIND.NS': 'Nestle',
    'BRITANNIA.NS': 'Britannia', 'DABUR.NS': 'Dabur', 'MARICO.NS': 'Marico',
    'MARUTI.NS': 'Maruti Suzuki', 'TATAMOTORS.NS': 'Tata Motors', 'M&M.NS': 'M&M',
    'BAJAJ-AUTO.NS': 'Bajaj Auto', 'EICHERMOT.NS': 'Eicher Motors',
    'SUNPHARMA.NS': 'Sun Pharma', 'DRREDDY.NS': 'Dr Reddy', 'CIPLA.NS': 'Cipla',
    'DIVISLAB.NS': 'Divi Labs', 'BIOCON.NS': 'Biocon', 'APOLLOHOSP.NS': 'Apollo Hospitals',
    'RELIANCE.NS': 'Reliance', 'ONGC.NS': 'ONGC', 'POWERGRID.NS': 'Power Grid',
    'NTPC.NS': 'NTPC', 'ADANIGREEN.NS': 'Adani Green', 'TATASTEEL.NS': 'Tata Steel',
    'HINDALCO.NS': 'Hindalco', 'JSWSTEEL.NS': 'JSW Steel', 'COALINDIA.NS': 'Coal India',
    'BHARTIARTL.NS': 'Bharti Airtel', 'ULTRACEMCO.NS': 'UltraTech',
    'ASIANPAINT.NS': 'Asian Paints', 'TITAN.NS': 'Titan', 'ADANIPORTS.NS': 'Adani Ports', 'LT.NS': 'L&T'
}

class EnhancedSmartMoneyTracker:
    """Enhanced Smart Money Tracker with better data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.nse_cookies = None
    
    def get_nse_cookies(self):
        """Get NSE cookies for API access"""
        try:
            response = self.session.get('https://www.nseindia.com', timeout=10)
            self.nse_cookies = response.cookies
            return True
        except:
            return False    
    de
f fetch_comprehensive_bulk_deals(self):
        """Fetch bulk deals from multiple sources"""
        
        # Try NSE API first
        bulk_deals = self.fetch_nse_bulk_deals()
        
        # If no data, try web scraping
        if bulk_deals.empty:
            bulk_deals = self.scrape_bulk_deals_multiple_sources()
        
        # If still no data, create informative display
        if bulk_deals.empty:
            return self.create_bulk_deals_info()
        
        return bulk_deals
    
    def fetch_nse_bulk_deals(self):
        """Fetch from NSE API"""
        try:
            if not self.nse_cookies:
                self.get_nse_cookies()
            
            url = "https://www.nseindia.com/api/snapshot-capital-market-largedeal"
            response = self.session.get(url, cookies=self.nse_cookies, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('data') and len(data['data']) > 0:
                    bulk_deals = []
                    
                    for deal in data['data']:
                        bulk_deals.append({
                            'date': deal.get('date', datetime.now().strftime('%d-%b-%Y')),
                            'symbol': deal.get('symbol', ''),
                            'company': deal.get('companyName', ''),
                            'client_name': deal.get('clientName', ''),
                            'deal_type': deal.get('dealType', ''),
                            'quantity': int(deal.get('quantity', 0)),
                            'price': float(deal.get('price', 0)),
                            'value': float(deal.get('value', 0)),
                        })
                    
                    return pd.DataFrame(bulk_deals)
        
        except Exception as e:
            print(f"NSE Bulk API failed: {e}")
        
        return pd.DataFrame()
    
    def scrape_bulk_deals_multiple_sources(self):
        """Try multiple sources for bulk deals"""
        
        sources = [
            'https://www.moneycontrol.com/stocks/marketstats/bulk_deals/index.php',
            'https://www.screener.in/company/bulk-deals/',
        ]
        
        for source in sources:
            try:
                response = self.session.get(source, timeout=10)
                if response.status_code == 200:
                    # Parse based on source
                    if 'moneycontrol' in source:
                        return self.parse_moneycontrol_bulk_deals(response.content)
                    elif 'screener' in source:
                        return self.parse_screener_bulk_deals(response.content)
            except:
                continue
        
        return pd.DataFrame()
    
    def create_bulk_deals_info(self):
        """Create informative display when no bulk deals"""
        
        # Get recent stock movements to show which stocks had unusual activity
        unusual_activity = self.detect_unusual_volume_activity()
        
        return unusual_activity
    
    def detect_unusual_volume_activity(self):
        """Detect stocks with unusual volume (potential bulk activity)"""
        
        unusual_stocks = []
        
        # Check top 20 stocks for unusual volume
        top_stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
                     'HINDUNILVR.NS', 'ITC.NS', 'BAJFINANCE.NS', 'KOTAKBANK.NS', 'SBIN.NS',
                     'BHARTIARTL.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'AXISBANK.NS', 'LT.NS',
                     'SUNPHARMA.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS']
        
        for symbol in top_stocks:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='5d')
                
                if not hist.empty and len(hist) >= 2:
                    current_volume = hist['Volume'].iloc[-1]
                    avg_volume = hist['Volume'].mean()
                    
                    # If volume is 2x higher than average
                    if current_volume > avg_volume * 2:
                        price_change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                        
                        unusual_stocks.append({
                            'company': INDIAN_STOCKS.get(symbol, symbol.replace('.NS', '')),
                            'symbol': symbol.replace('.NS', ''),
                            'volume_ratio': current_volume / avg_volume,
                            'price_change': price_change,
                            'current_price': hist['Close'].iloc[-1],
                            'volume': current_volume,
                            'status': 'High Volume Activity'
                        })
            except:
                continue
        
        return pd.DataFrame(unusual_stocks)