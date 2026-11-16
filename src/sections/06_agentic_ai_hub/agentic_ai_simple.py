"""
Simplified Agentic AI System - Compatible Version
Works with current library versions
"""

import os
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
import yfinance as yf
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")

# Simple Groq API client
class SimpleGroqClient:
    """Simple Groq API client without complex dependencies"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def chat(self, prompt: str) -> str:
        """Send chat request to Groq"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "openai/gpt-oss-120b",  # Updated model
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 4096
            }
            
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"Error: {response.status_code} - {response.text}"
        
        except Exception as e:
            return f"Error: {str(e)}"

# Initialize client
groq_client = SimpleGroqClient(GROQ_API_KEY)

# ==================== DATA FETCHING FUNCTIONS ====================

def fetch_stock_data(symbol: str) -> Dict[str, Any]:
    """Fetch comprehensive real-time stock data with all indicators"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get multiple timeframes for better analysis
        hist_1d = ticker.history(period='1d', interval='5m')  # Intraday
        hist_5d = ticker.history(period='5d')  # Short term
        hist_1mo = ticker.history(period='1mo')  # Medium term
        hist_3mo = ticker.history(period='3mo')  # Long term
        hist_1y = ticker.history(period='1y')  # Yearly
        
        info = ticker.info
        
        if hist_1mo.empty:
            return {"error": "No data available"}
        
        # Current price data
        current_price = hist_1mo['Close'].iloc[-1]
        prev_close = hist_1mo['Close'].iloc[-2] if len(hist_1mo) > 1 else current_price
        open_price = hist_1mo['Open'].iloc[-1]
        high_price = hist_1mo['High'].iloc[-1]
        low_price = hist_1mo['Low'].iloc[-1]
        
        # Calculate comprehensive technical indicators
        close_prices = hist_1mo['Close']
        
        # Moving Averages (multiple periods)
        ma_5 = close_prices.rolling(window=5).mean().iloc[-1] if len(close_prices) >= 5 else current_price
        ma_10 = close_prices.rolling(window=10).mean().iloc[-1] if len(close_prices) >= 10 else current_price
        ma_20 = close_prices.rolling(window=20).mean().iloc[-1] if len(close_prices) >= 20 else current_price
        ma_50 = hist_3mo['Close'].rolling(window=50).mean().iloc[-1] if len(hist_3mo) >= 50 else current_price
        ma_200 = hist_1y['Close'].rolling(window=200).mean().iloc[-1] if len(hist_1y) >= 200 else current_price
        
        # Exponential Moving Averages
        ema_12 = close_prices.ewm(span=12).mean().iloc[-1]
        ema_26 = close_prices.ewm(span=26).mean().iloc[-1]
        
        # MACD
        macd_line = ema_12 - ema_26
        signal_line = close_prices.ewm(span=9).mean().iloc[-1]
        macd_histogram = macd_line - signal_line
        
        # RSI (14-period)
        delta = close_prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Stochastic Oscillator
        low_14 = hist_1mo['Low'].rolling(window=14).min()
        high_14 = hist_1mo['High'].rolling(window=14).max()
        stoch_k = 100 * ((current_price - low_14.iloc[-1]) / (high_14.iloc[-1] - low_14.iloc[-1]))
        
        # Bollinger Bands
        bb_middle = close_prices.rolling(window=20).mean().iloc[-1]
        bb_std = close_prices.rolling(window=20).std().iloc[-1]
        bb_upper = bb_middle + (2 * bb_std)
        bb_lower = bb_middle - (2 * bb_std)
        bb_width = ((bb_upper - bb_lower) / bb_middle) * 100
        
        # Volume Analysis
        avg_volume_10d = hist_1mo['Volume'].rolling(window=10).mean().iloc[-1]
        avg_volume_30d = hist_1mo['Volume'].mean()
        current_volume = hist_1mo['Volume'].iloc[-1]
        volume_ratio_10d = current_volume / avg_volume_10d if avg_volume_10d > 0 else 1
        volume_ratio_30d = current_volume / avg_volume_30d if avg_volume_30d > 0 else 1
        
        # Price momentum
        momentum_1d = ((current_price - hist_1mo['Close'].iloc[-2]) / hist_1mo['Close'].iloc[-2]) * 100 if len(hist_1mo) > 1 else 0
        momentum_5d = ((current_price - hist_5d['Close'].iloc[0]) / hist_5d['Close'].iloc[0]) * 100 if len(hist_5d) > 0 else 0
        momentum_1mo = ((current_price - hist_1mo['Close'].iloc[0]) / hist_1mo['Close'].iloc[0]) * 100
        momentum_3mo = ((current_price - hist_3mo['Close'].iloc[0]) / hist_3mo['Close'].iloc[0]) * 100 if len(hist_3mo) > 0 else 0
        
        # Volatility (Standard Deviation)
        volatility_10d = close_prices.rolling(window=10).std().iloc[-1]
        volatility_30d = close_prices.std()
        
        # Average True Range (ATR) for volatility
        high_low = hist_1mo['High'] - hist_1mo['Low']
        high_close = abs(hist_1mo['High'] - hist_1mo['Close'].shift())
        low_close = abs(hist_1mo['Low'] - hist_1mo['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean().iloc[-1]
        
        # Support and Resistance levels
        recent_highs = hist_1mo['High'].nlargest(3)
        recent_lows = hist_1mo['Low'].nsmallest(3)
        resistance_1 = recent_highs.iloc[0]
        resistance_2 = recent_highs.iloc[1] if len(recent_highs) > 1 else resistance_1
        support_1 = recent_lows.iloc[0]
        support_2 = recent_lows.iloc[1] if len(recent_lows) > 1 else support_1
        
        # Price position analysis
        price_vs_52w_high = ((current_price - info.get('fiftyTwoWeekHigh', current_price)) / info.get('fiftyTwoWeekHigh', current_price)) * 100
        price_vs_52w_low = ((current_price - info.get('fiftyTwoWeekLow', current_price)) / info.get('fiftyTwoWeekLow', current_price)) * 100
        
        # Trend strength
        adx_period = 14
        plus_dm = hist_1mo['High'].diff()
        minus_dm = -hist_1mo['Low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        tr_smooth = true_range.rolling(window=adx_period).sum()
        plus_di = 100 * (plus_dm.rolling(window=adx_period).sum() / tr_smooth)
        minus_di = 100 * (minus_dm.rolling(window=adx_period).sum() / tr_smooth)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=adx_period).mean().iloc[-1]
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            
            # Price data
            'current_price': float(current_price),
            'open_price': float(open_price),
            'high_price': float(high_price),
            'low_price': float(low_price),
            'previous_close': float(prev_close),
            'change': float(current_price - prev_close),
            'change_percent': float(((current_price - prev_close) / prev_close) * 100),
            
            # Moving Averages
            'ma_5': float(ma_5),
            'ma_10': float(ma_10),
            'ma_20': float(ma_20),
            'ma_50': float(ma_50),
            'ma_200': float(ma_200),
            'ema_12': float(ema_12),
            'ema_26': float(ema_26),
            
            # MACD
            'macd_line': float(macd_line),
            'macd_signal': float(signal_line),
            'macd_histogram': float(macd_histogram),
            
            # Oscillators
            'rsi': float(current_rsi),
            'stochastic': float(stoch_k),
            
            # Bollinger Bands
            'bb_upper': float(bb_upper),
            'bb_middle': float(bb_middle),
            'bb_lower': float(bb_lower),
            'bb_width': float(bb_width),
            
            # Volume
            'current_volume': float(current_volume),
            'avg_volume_10d': float(avg_volume_10d),
            'avg_volume_30d': float(avg_volume_30d),
            'volume_ratio_10d': float(volume_ratio_10d),
            'volume_ratio_30d': float(volume_ratio_30d),
            
            # Momentum
            'momentum_1d': float(momentum_1d),
            'momentum_5d': float(momentum_5d),
            'momentum_1mo': float(momentum_1mo),
            'momentum_3mo': float(momentum_3mo),
            
            # Volatility
            'volatility_10d': float(volatility_10d),
            'volatility_30d': float(volatility_30d),
            'atr': float(atr),
            'adx': float(adx),
            
            # Support/Resistance
            'resistance_1': float(resistance_1),
            'resistance_2': float(resistance_2),
            'support_1': float(support_1),
            'support_2': float(support_2),
            
            # Fundamentals
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'forward_pe': info.get('forwardPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'price_to_book': info.get('priceToBook', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'dividend_rate': info.get('dividendRate', 0),
            'beta': info.get('beta', 0),
            'eps': info.get('trailingEps', 0),
            'revenue': info.get('totalRevenue', 0),
            'profit_margin': info.get('profitMargins', 0),
            'operating_margin': info.get('operatingMargins', 0),
            'roe': info.get('returnOnEquity', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'current_ratio': info.get('currentRatio', 0),
            'book_value': info.get('bookValue', 0),
            '52_week_high': info.get('fiftyTwoWeekHigh', 0),
            '52_week_low': info.get('fiftyTwoWeekLow', 0),
            'price_vs_52w_high': float(price_vs_52w_high),
            'price_vs_52w_low': float(price_vs_52w_low),
            
            # Additional info
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown'),
            'company_name': info.get('longName', symbol),
            'currency': info.get('currency', 'INR'),
            'exchange': info.get('exchange', 'NSE')
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_fii_dii_data() -> Dict[str, Any]:
    """Fetch FII/DII data from NSE"""
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.nseindia.com/'
        })
        
        session.get('https://www.nseindia.com', timeout=10)
        url = 'https://www.nseindia.com/api/fiidiiTradeReact'
        response = session.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                latest = data[0]
                return {
                    'date': latest.get('date', ''),
                    'fii_buy': float(latest.get('fiiBuyValue', 0)),
                    'fii_sell': float(latest.get('fiiSellValue', 0)),
                    'fii_net': float(latest.get('fiiNetValue', 0)),
                    'dii_buy': float(latest.get('diiBuyValue', 0)),
                    'dii_sell': float(latest.get('diiSellValue', 0)),
                    'dii_net': float(latest.get('diiNetValue', 0)),
                    'total_net': float(latest.get('fiiNetValue', 0)) + float(latest.get('diiNetValue', 0)),
                    'timestamp': datetime.now().isoformat()
                }
        
        return {"error": "Unable to fetch FII/DII data"}
    except Exception as e:
        return {"error": str(e)}

# ==================== AGENTIC ANALYSIS CLASSES ====================

class SimpleAgenticStockAnalysis:
    """Simplified agentic stock analysis"""
    
    def __init__(self):
        self.client = groq_client
    
    def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """Analyze stock using comprehensive AI with real-time data"""
        
        # Fetch comprehensive data
        stock_data = fetch_stock_data(symbol)
        fii_dii_data = fetch_fii_dii_data()
        
        if 'error' in stock_data:
            return {'success': False, 'error': stock_data['error']}
        
        # Create world-class comprehensive prompt
        prompt = f"""You are a world-class senior investment analyst with 25+ years of experience. Provide an institutional-grade analysis of this stock with extreme detail and accuracy.

STOCK: {stock_data.get('company_name', symbol)} ({symbol})
SECTOR: {stock_data['sector']} | INDUSTRY: {stock_data['industry']}
EXCHANGE: {stock_data['exchange']} | CURRENCY: {stock_data['currency']}

═══════════════════════════════════════════════════════════════
REAL-TIME PRICE DATA (Live as of {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
═══════════════════════════════════════════════════════════════
Current Price: ₹{stock_data['current_price']:.2f}
Open: ₹{stock_data['open_price']:.2f} | High: ₹{stock_data['high_price']:.2f} | Low: ₹{stock_data['low_price']:.2f}
Previous Close: ₹{stock_data['previous_close']:.2f}
Change: ₹{stock_data['change']:+.2f} ({stock_data['change_percent']:+.2f}%)

═══════════════════════════════════════════════════════════════
COMPREHENSIVE TECHNICAL ANALYSIS
═══════════════════════════════════════════════════════════════

MOVING AVERAGES:
• 5-day MA: ₹{stock_data['ma_5']:.2f} | Price is {'ABOVE' if stock_data['current_price'] > stock_data['ma_5'] else 'BELOW'} (Signal: {'Bullish' if stock_data['current_price'] > stock_data['ma_5'] else 'Bearish'})
• 10-day MA: ₹{stock_data['ma_10']:.2f} | Price is {'ABOVE' if stock_data['current_price'] > stock_data['ma_10'] else 'BELOW'}
• 20-day MA: ₹{stock_data['ma_20']:.2f} | Price is {'ABOVE' if stock_data['current_price'] > stock_data['ma_20'] else 'BELOW'}
• 50-day MA: ₹{stock_data['ma_50']:.2f} | Price is {'ABOVE' if stock_data['current_price'] > stock_data['ma_50'] else 'BELOW'}
• 200-day MA: ₹{stock_data['ma_200']:.2f} | Price is {'ABOVE' if stock_data['current_price'] > stock_data['ma_200'] else 'BELOW'}
• EMA 12: ₹{stock_data['ema_12']:.2f} | EMA 26: ₹{stock_data['ema_26']:.2f}

MACD ANALYSIS:
• MACD Line: {stock_data['macd_line']:.2f}
• Signal Line: {stock_data['macd_signal']:.2f}
• Histogram: {stock_data['macd_histogram']:.2f}
• Signal: {'BULLISH CROSSOVER' if stock_data['macd_histogram'] > 0 else 'BEARISH CROSSOVER'}

MOMENTUM OSCILLATORS:
• RSI (14): {stock_data['rsi']:.2f} - {'OVERBOUGHT (>70)' if stock_data['rsi'] > 70 else 'OVERSOLD (<30)' if stock_data['rsi'] < 30 else 'NEUTRAL (30-70)'}
• Stochastic: {stock_data['stochastic']:.2f}
• ADX (Trend Strength): {stock_data['adx']:.2f} - {'STRONG TREND' if stock_data['adx'] > 25 else 'WEAK TREND'}

BOLLINGER BANDS:
• Upper Band: ₹{stock_data['bb_upper']:.2f}
• Middle Band: ₹{stock_data['bb_middle']:.2f}
• Lower Band: ₹{stock_data['bb_lower']:.2f}
• Band Width: {stock_data['bb_width']:.2f}% - {'HIGH VOLATILITY' if stock_data['bb_width'] > 10 else 'LOW VOLATILITY'}
• Price Position: {'Near Upper Band (Overbought)' if stock_data['current_price'] > stock_data['bb_middle'] else 'Near Lower Band (Oversold)'}

SUPPORT & RESISTANCE LEVELS:
• Resistance 1: ₹{stock_data['resistance_1']:.2f} (Distance: {((stock_data['resistance_1'] - stock_data['current_price']) / stock_data['current_price'] * 100):+.2f}%)
• Resistance 2: ₹{stock_data['resistance_2']:.2f}
• Support 1: ₹{stock_data['support_1']:.2f} (Distance: {((stock_data['support_1'] - stock_data['current_price']) / stock_data['current_price'] * 100):+.2f}%)
• Support 2: ₹{stock_data['support_2']:.2f}

VOLUME ANALYSIS:
• Current Volume: {stock_data['current_volume']:,.0f}
• 10-day Avg: {stock_data['avg_volume_10d']:,.0f} | Ratio: {stock_data['volume_ratio_10d']:.2f}x
• 30-day Avg: {stock_data['avg_volume_30d']:,.0f} | Ratio: {stock_data['volume_ratio_30d']:.2f}x
• Volume Signal: {'EXTREMELY HIGH (>2x)' if stock_data['volume_ratio_30d'] > 2 else 'HIGH (1.5-2x)' if stock_data['volume_ratio_30d'] > 1.5 else 'NORMAL'}

MOMENTUM & VOLATILITY:
• 1-Day Momentum: {stock_data['momentum_1d']:+.2f}%
• 5-Day Momentum: {stock_data['momentum_5d']:+.2f}%
• 1-Month Momentum: {stock_data['momentum_1mo']:+.2f}%
• 3-Month Momentum: {stock_data['momentum_3mo']:+.2f}%
• ATR (Volatility): ₹{stock_data['atr']:.2f}
• 10-day Volatility: {stock_data['volatility_10d']:.2f}
• 30-day Volatility: {stock_data['volatility_30d']:.2f}

═══════════════════════════════════════════════════════════════
FUNDAMENTAL ANALYSIS
═══════════════════════════════════════════════════════════════

VALUATION METRICS:
• Market Cap: ₹{stock_data['market_cap']:,.0f} Cr
• P/E Ratio: {stock_data['pe_ratio']:.2f} | Forward P/E: {stock_data['forward_pe']:.2f}
• PEG Ratio: {stock_data['peg_ratio']:.2f}
• Price/Book: {stock_data['price_to_book']:.2f}
• Beta: {stock_data['beta']:.2f} ({'More Volatile than Market' if stock_data['beta'] > 1 else 'Less Volatile than Market'})

PROFITABILITY:
• EPS: ₹{stock_data['eps']:.2f}
• Profit Margin: {stock_data['profit_margin']*100:.2f}%
• Operating Margin: {stock_data['operating_margin']*100:.2f}%
• ROE: {stock_data['roe']*100:.2f}%

FINANCIAL HEALTH:
• Debt/Equity: {stock_data['debt_to_equity']:.2f}
• Current Ratio: {stock_data['current_ratio']:.2f}
• Book Value: ₹{stock_data['book_value']:.2f}

DIVIDEND:
• Dividend Yield: {stock_data['dividend_yield']*100:.2f}%
• Dividend Rate: ₹{stock_data['dividend_rate']:.2f}

52-WEEK RANGE:
• 52W High: ₹{stock_data['52_week_high']:.2f} (Current is {stock_data['price_vs_52w_high']:+.2f}% from high)
• 52W Low: ₹{stock_data['52_week_low']:.2f} (Current is {stock_data['price_vs_52w_low']:+.2f}% from low)

═══════════════════════════════════════════════════════════════
INSTITUTIONAL MONEY FLOW (Real-time from NSE)
═══════════════════════════════════════════════════════════════
Date: {fii_dii_data.get('date', 'N/A')}
• FII Net: ₹{fii_dii_data.get('fii_net', 0):,.0f} Cr (Buy: ₹{fii_dii_data.get('fii_buy', 0):,.0f} Cr | Sell: ₹{fii_dii_data.get('fii_sell', 0):,.0f} Cr)
• DII Net: ₹{fii_dii_data.get('dii_net', 0):,.0f} Cr (Buy: ₹{fii_dii_data.get('dii_buy', 0):,.0f} Cr | Sell: ₹{fii_dii_data.get('dii_sell', 0):,.0f} Cr)
• Total Institutional Flow: ₹{fii_dii_data.get('total_net', 0):,.0f} Cr

═══════════════════════════════════════════════════════════════
PROVIDE WORLD-CLASS INSTITUTIONAL-GRADE ANALYSIS
═══════════════════════════════════════════════════════════════

Based on ALL the above real-time data, provide an extremely detailed analysis in this EXACT format:

═══════════════════════════════════════════════════════════════
📊 COMPREHENSIVE TECHNICAL ANALYSIS
═══════════════════════════════════════════════════════════════

Technical Score: [X/10] (Explain scoring methodology)

Trend Analysis:
• Primary Trend: [Bullish/Bearish/Sideways] - Explain using MA alignment
• Trend Strength: [Strong/Moderate/Weak] - Based on ADX
• Trend Duration: [Short-term/Medium-term/Long-term]

Moving Average Analysis:
• Short-term (5/10 MA): [Detailed interpretation]
• Medium-term (20/50 MA): [Detailed interpretation]
• Long-term (200 MA): [Detailed interpretation]
• Golden/Death Cross: [Any recent crossovers?]

Momentum Analysis:
• RSI Interpretation: [Detailed analysis with overbought/oversold zones]
• MACD Signal: [Bullish/Bearish with histogram analysis]
• Stochastic: [Detailed interpretation]
• Momentum Sustainability: [Can current momentum continue?]

Volume Analysis:
• Volume Confirmation: [Is price move confirmed by volume?]
• Accumulation/Distribution: [Are institutions accumulating or distributing?]
• Volume Breakout: [Any volume breakouts detected?]

Volatility Analysis:
• Current Volatility: [High/Medium/Low]
• Bollinger Band Position: [Squeeze/Expansion]
• ATR Analysis: [Risk per share]

Support & Resistance:
• Key Support Levels: [List with probability of holding]
• Key Resistance Levels: [List with probability of breaking]
• Breakout/Breakdown Zones: [Critical levels to watch]

═══════════════════════════════════════════════════════════════
💼 FUNDAMENTAL ANALYSIS
═══════════════════════════════════════════════════════════════

Fundamental Score: [X/10] (Explain scoring)

Valuation Assessment:
• P/E Analysis: [Overvalued/Fairly Valued/Undervalued compared to sector]
• PEG Ratio: [Growth vs valuation analysis]
• Price/Book: [Asset backing analysis]
• Overall Valuation: [Detailed conclusion]

Profitability Analysis:
• Margin Analysis: [Profit margins vs industry]
• ROE Analysis: [Return on equity assessment]
• Earnings Quality: [Sustainable or one-time gains?]

Financial Health:
• Debt Analysis: [Debt levels comfortable or concerning?]
• Liquidity: [Can company meet short-term obligations?]
• Cash Flow: [Operating cash flow strength]

Dividend Analysis:
• Dividend Sustainability: [Can company maintain dividends?]
• Dividend Growth: [Historical dividend growth]
• Yield Attractiveness: [Compared to alternatives]

═══════════════════════════════════════════════════════════════
💰 INSTITUTIONAL MONEY FLOW ANALYSIS
═══════════════════════════════════════════════════════════════

Institutional Score: [X/10]

FII Activity Analysis:
• FII Sentiment: [Bullish/Bearish/Neutral]
• FII Flow Trend: [Consistent buying/selling or erratic?]
• FII Impact: [How will this affect stock price?]

DII Activity Analysis:
• DII Sentiment: [Bullish/Bearish/Neutral]
• DII vs FII: [Are they aligned or diverging?]
• Domestic Support: [Strong/Moderate/Weak]

Smart Money Signal:
• Overall Institutional Signal: [Accumulation/Distribution/Neutral]
• Confidence Level: [High/Medium/Low]
• Expected Impact: [Short-term and long-term]

═══════════════════════════════════════════════════════════════
🎯 FINAL RECOMMENDATION
═══════════════════════════════════════════════════════════════

Overall Score: [X/10] (Technical: X + Fundamental: X + Institutional: X)

RECOMMENDATION: [STRONG BUY / BUY / HOLD / SELL / STRONG SELL]

Confidence Level: [X%] (Explain why this confidence level)

Investment Thesis:
[3-4 sentences explaining the core investment thesis]

Entry Strategy:
• Ideal Entry Price: ₹[X] - ₹[Y]
• Current Price Assessment: [Good entry/Wait for pullback/Overextended]
• Entry Timing: [Immediate/Wait for dip/Wait for breakout]

Price Targets:
• Conservative Target (3 months): ₹[X] ([Y]% upside)
• Realistic Target (3 months): ₹[X] ([Y]% upside)
• Optimistic Target (6 months): ₹[X] ([Y]% upside)

Stop Loss Strategy:
• Initial Stop Loss: ₹[X] ([Y]% below entry)
• Trailing Stop Loss: [Strategy]
• Risk/Reward Ratio: [X:Y]

Risk Assessment:
• Risk Level: [Low/Medium/High]
• Risk Factors: [List specific risks]
• Risk Mitigation: [How to manage risks]

Investment Horizon:
• Recommended Holding Period: [Short-term (1-3 months) / Medium-term (3-6 months) / Long-term (6-12 months)]
• Rationale: [Why this timeframe?]

Position Sizing:
• Recommended Allocation: [X% of portfolio]
• Maximum Allocation: [Y% of portfolio]
• Rationale: [Based on risk level]

═══════════════════════════════════════════════════════════════
✅ KEY REASONS TO BUY/HOLD/SELL (Top 5)
═══════════════════════════════════════════════════════════════
1. [Most important reason with data]
2. [Second reason with data]
3. [Third reason with data]
4. [Fourth reason with data]
5. [Fifth reason with data]

═══════════════════════════════════════════════════════════════
⚠️ KEY RISKS TO WATCH (Top 5)
═══════════════════════════════════════════════════════════════
1. [Most critical risk with probability]
2. [Second risk with probability]
3. [Third risk with probability]
4. [Fourth risk with probability]
5. [Fifth risk with probability]

═══════════════════════════════════════════════════════════════
📅 MONITORING PLAN
═══════════════════════════════════════════════════════════════
• Daily: [What to monitor daily]
• Weekly: [What to review weekly]
• Monthly: [What to assess monthly]
• Exit Triggers: [When to exit the position]

═══════════════════════════════════════════════════════════════
💡 PROFESSIONAL INSIGHTS
═══════════════════════════════════════════════════════════════
[Provide 2-3 paragraphs of professional insights that only an experienced analyst would know. Include sector trends, competitive positioning, market cycles, and any unique factors affecting this stock.]

═══════════════════════════════════════════════════════════════

Be extremely detailed, data-driven, and professional. Use all the real-time data provided. This analysis should be worthy of a top-tier investment bank."""

        # Get AI analysis
        analysis = self.client.chat(prompt)
        
        return {
            'success': True,
            'symbol': symbol,
            'company_name': stock_data.get('company_name', symbol),
            'analysis': analysis,
            'raw_data': stock_data,
            'timestamp': datetime.now().isoformat()
        }

class SimpleAgenticPortfolioManager:
    """Simplified portfolio management"""
    
    def __init__(self):
        self.client = groq_client
    
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Analyze portfolio"""
        
        # Calculate portfolio metrics
        total_value = sum(h.get('current_value', 0) for h in holdings)
        num_holdings = len(holdings)
        
        # Create prompt
        prompt = f"""You are a portfolio risk manager. Analyze this portfolio and provide recommendations.

Portfolio Summary:
- Total Value: ₹{total_value:,.0f}
- Number of Holdings: {num_holdings}
- Holdings: {holdings}

Provide analysis in this exact format:

RISK ASSESSMENT:
- Risk Score: [0-10, where 10 is highest risk]
- Risk Level: [Low/Medium/High]
- Diversification: [Good/Moderate/Poor with explanation]
- Concentration Risk: [Analysis of top holdings]

PORTFOLIO HEALTH:
- Overall Health: [Excellent/Good/Fair/Poor]
- Strengths: [List top 3]
- Weaknesses: [List top 3]

IMMEDIATE ACTIONS (This Week):
1. [Action 1 with reasoning]
2. [Action 2 with reasoning]
3. [Action 3 with reasoning]

SHORT-TERM STRATEGY (1-3 months):
1. [Strategy 1]
2. [Strategy 2]
3. [Strategy 3]

LONG-TERM STRATEGY (6-12 months):
1. [Strategy 1]
2. [Strategy 2]
3. [Strategy 3]

REBALANCING RECOMMENDATIONS:
- Stocks to Add: [List with reasoning]
- Stocks to Reduce: [List with reasoning]
- Target Allocation: [Sector-wise %]

EXPECTED RETURNS:
- Conservative Estimate: [X%]
- Realistic Estimate: [Y%]
- Optimistic Estimate: [Z%]

Be specific and actionable."""

        # Get AI analysis
        analysis = self.client.chat(prompt)
        
        return {
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }

class SimpleAgenticMarketIntelligence:
    """Simplified market intelligence"""
    
    def __init__(self):
        self.client = groq_client
    
    def get_market_intelligence(self) -> Dict[str, Any]:
        """Get market intelligence"""
        
        # Fetch market data
        fii_dii_data = fetch_fii_dii_data()
        
        # Get NIFTY data
        nifty = yf.Ticker('^NSEI')
        nifty_hist = nifty.history(period='5d')
        
        if not nifty_hist.empty:
            current = nifty_hist['Close'].iloc[-1]
            prev = nifty_hist['Close'].iloc[0]
            change = ((current - prev) / prev) * 100
        else:
            current = 0
            change = 0
        
        # Create prompt
        prompt = f"""You are a chief market strategist. Provide comprehensive market intelligence.

Market Data:
- NIFTY Current: {current:.2f}
- NIFTY Change (5 days): {change:+.2f}%
- FII Net Flow: ₹{fii_dii_data.get('fii_net', 0):,.0f} Cr
- DII Net Flow: ₹{fii_dii_data.get('dii_net', 0):,.0f} Cr
- Total Institutional Flow: ₹{fii_dii_data.get('total_net', 0):,.0f} Cr

Provide intelligence in this exact format:

MARKET STATUS:
- Overall Status: [Bullish/Bearish/Neutral]
- NIFTY Trend: [Upward/Downward/Sideways]
- Market Strength: [Strong/Moderate/Weak]

INSTITUTIONAL ACTIVITY:
- FII Activity: [Buying/Selling/Neutral with amount]
- DII Activity: [Buying/Selling/Neutral with amount]
- Net Institutional Flow: [Positive/Negative with interpretation]

MARKET PREDICTION (1 Week):
- Direction: [Upward/Downward/Sideways]
- Confidence: [0-100%]
- Expected Range: [X - Y]
- Key Levels: [Support and Resistance]

SECTORS TO WATCH:
1. [Sector 1 with reasoning]
2. [Sector 2 with reasoning]
3. [Sector 3 with reasoning]

TRADING STRATEGY:
- Bias: [Bullish/Bearish/Neutral]
- Approach: [Buy on dips/Sell on rallies/Stay cautious]
- Focus: [Large-cap/Mid-cap/Small-cap]
- Stop-loss Level: [NIFTY level]

RISK FACTORS (Top 3):
1. [Risk 1]
2. [Risk 2]
3. [Risk 3]

OPPORTUNITIES (Top 3):
1. [Opportunity 1]
2. [Opportunity 2]
3. [Opportunity 3]

Be specific and actionable."""

        # Get AI analysis
        intelligence = self.client.chat(prompt)
        
        return {
            'success': True,
            'intelligence': intelligence,
            'timestamp': datetime.now().isoformat()
        }

# Export classes
__all__ = [
    'SimpleAgenticStockAnalysis',
    'SimpleAgenticPortfolioManager',
    'SimpleAgenticMarketIntelligence'
]

print("✅ Simplified Agentic AI System loaded successfully")
