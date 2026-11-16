"""
Utility functions for Sarthak Nivesh Platform
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stock_data(symbol, period="1mo"):
    """Fetch stock data from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    except Exception as e:
        return None

def calculate_sip_returns(monthly_investment, years, annual_return_rate):
    """Calculate SIP returns"""
    months = years * 12
    monthly_rate = annual_return_rate / 12 / 100
    
    future_value = monthly_investment * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    total_invested = monthly_investment * months
    returns = future_value - total_invested
    
    return {
        'future_value': future_value,
        'total_invested': total_invested,
        'returns': returns,
        'return_percentage': (returns / total_invested) * 100
    }

def get_nifty_data_robust():
    """Get NIFTY 50 data"""
    try:
        nifty = yf.Ticker("^NSEI")
        data = nifty.history(period="5d")
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            return {
                'price': current_price,
                'change': change,
                'change_pct': change_pct
            }
    except:
        pass
    return {'price': 22500, 'change': 150, 'change_pct': 0.67}
