# सार्थक निवेश - AI Investment Assistant (Phase 5)
# Advanced Conversational AI for Investment Guidance
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sqlite3
import requests
import json
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import warnings
warnings.filterwarnings('ignore')
from config import *

class AIInvestmentAssistant:
    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.setup_ai_database()
        self.investment_knowledge_base = self.load_investment_knowledge()
        print("🤖 AI Investment Assistant initialized")
    
    def setup_ai_database(self):
        """Setup AI assistant database tables"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # User conversation history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    user_query TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    query_type TEXT,
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User investment profile
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    age INTEGER,
                    risk_tolerance TEXT,
                    investment_experience TEXT,
                    monthly_income REAL,
                    investment_goals TEXT,
                    time_horizon TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # AI recommendations tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    recommendation_type TEXT NOT NULL,
                    recommendation_text TEXT NOT NULL,
                    confidence_score REAL,
                    reasoning TEXT,
                    follow_up_date DATE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ AI Assistant database setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up AI database: {str(e)}")
    
    def load_investment_knowledge(self):
        """Load comprehensive investment knowledge base"""
        return {
            'stock_analysis': {
                'keywords': ['stock', 'share', 'equity', 'company', 'buy', 'sell', 'hold', 'price', 'valuation'],
                'responses': {
                    'general': "I can help you analyze stocks using real-time data, technical indicators, and market sentiment.",
                    'buy_advice': "For buying stocks, I consider current price, technical indicators, sentiment analysis, and your risk profile.",
                    'sell_advice': "For selling decisions, I analyze profit/loss, market conditions, and your investment goals."
                }
            },
            'mutual_funds': {
                'keywords': ['mutual fund', 'mf', 'sip', 'systematic', 'nav', 'expense ratio', 'fund manager'],
                'responses': {
                    'general': "I can recommend mutual funds based on your risk profile, investment horizon, and financial goals.",
                    'sip_advice': "SIP is great for rupee cost averaging. I'll suggest funds based on your age and risk tolerance.",
                    'fund_selection': "I consider fund performance, expense ratio, fund manager track record, and AUM size."
                }
            },
            'ipo_analysis': {
                'keywords': ['ipo', 'initial public offering', 'listing', 'subscription', 'allotment'],
                'responses': {
                    'general': "I provide unique IPO analysis including post-listing performance prediction and hold/exit recommendations.",
                    'subscription_advice': "I analyze IPO fundamentals, subscription levels, and market conditions for subscription advice.",
                    'post_listing': "My unique feature tracks IPO performance for 30/60/90 days and suggests optimal exit strategies."
                }
            },
            'risk_management': {
                'keywords': ['risk', 'portfolio', 'diversification', 'allocation', 'volatility', 'beta'],
                'responses': {
                    'general': "I help optimize your portfolio risk through diversification analysis and asset allocation.",
                    'portfolio_advice': "I calculate risk metrics like Sharpe ratio, beta, and VaR for comprehensive risk assessment.",
                    'diversification': "Proper diversification across sectors and asset classes reduces portfolio risk significantly."
                }
            },
            'market_analysis': {
                'keywords': ['market', 'nifty', 'sensex', 'trend', 'bull', 'bear', 'correction'],
                'responses': {
                    'general': "I analyze market trends using technical indicators, sentiment analysis, and economic factors.",
                    'trend_analysis': "Current market trends are analyzed using moving averages, RSI, and market sentiment scores.",
                    'market_timing': "While timing the market is difficult, I can help identify good entry and exit points."
                }
            },
            'tax_planning': {
                'keywords': ['tax', 'elss', '80c', 'ltcg', 'stcg', 'tax saving'],
                'responses': {
                    'general': "I can suggest tax-efficient investment strategies including ELSS funds and tax-saving instruments.",
                    'elss_advice': "ELSS funds offer tax benefits under 80C with potential for good returns over 3+ years.",
                    'tax_optimization': "I help structure your investments to minimize tax liability while maximizing returns."
                }
            }
        }
    
    def process_user_query(self, user_query, user_id="default_user"):
        """Process user query and generate intelligent response"""
        try:
            print(f"🤖 Processing query: {user_query}")
            
            # Clean and analyze query
            query_lower = user_query.lower().strip()
            query_type = self.classify_query(query_lower)
            
            # Generate response based on query type
            if query_type == 'stock_analysis':
                response = self.handle_stock_query(query_lower, user_query)
            elif query_type == 'mutual_funds':
                response = self.handle_mutual_fund_query(query_lower, user_query)
            elif query_type == 'ipo_analysis':
                response = self.handle_ipo_query(query_lower, user_query)
            elif query_type == 'risk_management':
                response = self.handle_risk_query(query_lower, user_query)
            elif query_type == 'market_analysis':
                response = self.handle_market_query(query_lower, user_query)
            elif query_type == 'tax_planning':
                response = self.handle_tax_query(query_lower, user_query)
            elif query_type == 'general_advice':
                response = self.handle_general_query(query_lower, user_query)
            else:
                response = self.handle_unknown_query(user_query)
            
            # Calculate confidence score
            confidence_score = self.calculate_response_confidence(query_type, user_query)
            
            # Store conversation
            self.store_conversation(user_id, user_query, response['text'], query_type, confidence_score)
            
            return {
                'response': response['text'],
                'query_type': query_type,
                'confidence': confidence_score,
                'suggestions': response.get('suggestions', []),
                'data': response.get('data', {})
            }
            
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            return {
                'response': "I apologize, but I encountered an error processing your query. Please try rephrasing your question.",
                'query_type': 'error',
                'confidence': 0.0,
                'suggestions': [],
                'data': {}
            }
    
    def classify_query(self, query_lower):
        """Classify user query into appropriate category"""
        try:
            # Check for specific stock mentions
            indian_stocks = ['reliance', 'tcs', 'hdfc', 'infosys', 'icici', 'sbi', 'bharti', 'itc', 'kotak', 'axis']
            if any(stock in query_lower for stock in indian_stocks):
                return 'stock_analysis'
            
            # Check for query type based on keywords
            for category, info in self.investment_knowledge_base.items():
                if any(keyword in query_lower for keyword in info['keywords']):
                    return category
            
            # Check for general investment advice keywords
            general_keywords = ['invest', 'money', 'save', 'return', 'profit', 'loss', 'advice', 'help', 'suggest']
            if any(keyword in query_lower for keyword in general_keywords):
                return 'general_advice'
            
            return 'unknown'
            
        except Exception as e:
            print(f"❌ Error classifying query: {str(e)}")
            return 'unknown'
    
    def handle_stock_query(self, query_lower, original_query):
        """Handle stock-related queries with real data"""
        try:
            # Extract stock name from query
            stock_symbol = self.extract_stock_symbol(query_lower)
            
            if stock_symbol:
                # Get real stock data
                stock_data = self.get_real_stock_data(stock_symbol)
                
                if stock_data:
                    # Generate comprehensive stock advice
                    advice = self.generate_stock_advice(stock_data, query_lower)
                    
                    return {
                        'text': advice,
                        'suggestions': [
                            f"Get detailed technical analysis for {stock_symbol}",
                            f"Check risk assessment for {stock_symbol}",
                            f"Compare {stock_symbol} with sector peers",
                            "Set price alerts for this stock"
                        ],
                        'data': stock_data
                    }
                else:
                    return {
                        'text': f"I couldn't fetch current data for {stock_symbol}. Please check the stock symbol or try again later.",
                        'suggestions': ["Try asking about other stocks", "Check market overview", "Get sector analysis"]
                    }
            else:
                return {
                    'text': "I can help you analyze specific stocks. Please mention a stock name like 'HDFC Bank', 'Reliance', or 'TCS' for detailed analysis.",
                    'suggestions': ["Ask about HDFC Bank", "Ask about Reliance Industries", "Ask about TCS", "Get market overview"]
                }
                
        except Exception as e:
            print(f"❌ Error handling stock query: {str(e)}")
            return {
                'text': "I encountered an error analyzing the stock. Please try again with a specific stock name.",
                'suggestions': []
            }
    
    def extract_stock_symbol(self, query_lower):
        """Extract stock symbol from user query"""
        stock_mapping = {
            'reliance': 'RELIANCE.NS',
            'tcs': 'TCS.NS',
            'hdfc bank': 'HDFCBANK.NS',
            'hdfc': 'HDFCBANK.NS',
            'infosys': 'INFY.NS',
            'icici bank': 'ICICIBANK.NS',
            'icici': 'ICICIBANK.NS',
            'sbi': 'SBIN.NS',
            'state bank': 'SBIN.NS',
            'bharti airtel': 'BHARTIARTL.NS',
            'airtel': 'BHARTIARTL.NS',
            'itc': 'ITC.NS',
            'kotak': 'KOTAKBANK.NS',
            'axis bank': 'AXISBANK.NS',
            'axis': 'AXISBANK.NS',
            'maruti': 'MARUTI.NS',
            'sun pharma': 'SUNPHARMA.NS',
            'ntpc': 'NTPC.NS'
        }
        
        for name, symbol in stock_mapping.items():
            if name in query_lower:
                return symbol
        
        return None
    
    def get_real_stock_data(self, symbol):
        """Get real-time stock data for analysis"""
        try:
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="1y")
            info = ticker.info
            
            if hist_data.empty:
                return None
            
            current_price = hist_data['Close'].iloc[-1]
            prev_close = hist_data['Close'].iloc[-2] if len(hist_data) > 1 else current_price
            change_percent = ((current_price - prev_close) / prev_close) * 100
            
            # Calculate technical indicators
            prices = hist_data['Close']
            ma_20 = prices.rolling(window=20).mean().iloc[-1]
            ma_50 = prices.rolling(window=50).mean().iloc[-1]
            
            # RSI calculation
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'change_percent': change_percent,
                'ma_20': ma_20,
                'ma_50': ma_50,
                'rsi': current_rsi,
                'volume': hist_data['Volume'].iloc[-1],
                'high_52w': hist_data['High'].max(),
                'low_52w': hist_data['Low'].min(),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A')
            }
            
        except Exception as e:
            print(f"❌ Error getting stock data: {str(e)}")
            return None
    
    def generate_stock_advice(self, stock_data, query_lower):
        """Generate comprehensive stock investment advice"""
        try:
            symbol = stock_data['symbol'].replace('.NS', '')
            current_price = stock_data['current_price']
            change_percent = stock_data['change_percent']
            rsi = stock_data['rsi']
            ma_20 = stock_data['ma_20']
            ma_50 = stock_data['ma_50']
            
            # Generate advice based on technical analysis
            advice_parts = []
            
            # Current status
            advice_parts.append(f"📊 **{symbol} Analysis:**")
            advice_parts.append(f"Current Price: ₹{current_price:.2f} ({change_percent:+.2f}%)")
            
            # Technical analysis
            if current_price > ma_20 > ma_50:
                trend = "bullish uptrend"
                trend_advice = "The stock is in a strong uptrend. Good for buying on dips."
            elif current_price < ma_20 < ma_50:
                trend = "bearish downtrend"
                trend_advice = "The stock is in a downtrend. Wait for reversal signals before buying."
            else:
                trend = "sideways movement"
                trend_advice = "The stock is moving sideways. Wait for a clear breakout."
            
            advice_parts.append(f"📈 **Trend Analysis:** {trend_advice}")
            
            # RSI analysis
            if rsi > 70:
                rsi_advice = f"RSI is {rsi:.1f} (Overbought). Consider waiting for a pullback before buying."
            elif rsi < 30:
                rsi_advice = f"RSI is {rsi:.1f} (Oversold). Good buying opportunity if fundamentals are strong."
            else:
                rsi_advice = f"RSI is {rsi:.1f} (Neutral). Technical indicators are balanced."
            
            advice_parts.append(f"📊 **RSI Analysis:** {rsi_advice}")
            
            # Investment recommendation
            if 'buy' in query_lower or 'purchase' in query_lower:
                if current_price > ma_20 and rsi < 70:
                    recommendation = "✅ **Recommendation: BUY** - Technical indicators support buying at current levels."
                elif rsi > 70:
                    recommendation = "⚠️ **Recommendation: WAIT** - Stock appears overbought. Wait for a better entry point."
                else:
                    recommendation = "🔍 **Recommendation: RESEARCH** - Check fundamentals before making a decision."
            elif 'sell' in query_lower:
                if current_price < ma_20 or rsi > 70:
                    recommendation = "💰 **Recommendation: CONSIDER SELLING** - Technical indicators suggest profit booking."
                else:
                    recommendation = "📈 **Recommendation: HOLD** - No immediate selling pressure from technical indicators."
            else:
                # General analysis
                score = 0
                if current_price > ma_20: score += 2
                if current_price > ma_50: score += 2
                if 30 < rsi < 70: score += 2
                if change_percent > 0: score += 1
                
                if score >= 6:
                    recommendation = "🚀 **Overall: BULLISH** - Multiple positive technical indicators."
                elif score >= 4:
                    recommendation = "📊 **Overall: NEUTRAL** - Mixed technical signals."
                else:
                    recommendation = "📉 **Overall: BEARISH** - Technical indicators suggest caution."
            
            advice_parts.append(recommendation)
            
            # Risk factors
            advice_parts.append("⚠️ **Risk Factors:**")
            advice_parts.append("• Market volatility can affect short-term performance")
            advice_parts.append("• Consider your risk tolerance and investment horizon")
            advice_parts.append("• Diversify your portfolio across multiple stocks")
            
            # Additional suggestions
            advice_parts.append("💡 **Suggestions:**")
            advice_parts.append("• Set stop-loss at 8-10% below your buying price")
            advice_parts.append("• Monitor quarterly results and management commentary")
            advice_parts.append("• Consider SIP approach for regular investments")
            
            return "\n".join(advice_parts)
            
        except Exception as e:
            print(f"❌ Error generating stock advice: {str(e)}")
            return "I encountered an error generating stock advice. Please try again."
    
    def handle_mutual_fund_query(self, query_lower, original_query):
        """Handle mutual fund and SIP related queries"""
        try:
            if 'sip' in query_lower or 'systematic' in query_lower:
                return {
                    'text': """💰 **SIP Investment Guidance:**

**What is SIP?**
Systematic Investment Plan (SIP) allows you to invest a fixed amount regularly in mutual funds.

**Benefits of SIP:**
• Rupee Cost Averaging - Buy more units when prices are low
• Disciplined investing approach
• Power of compounding over time
• Reduces impact of market volatility

**SIP Recommendations:**
• **Age 20-30:** 70-80% Equity funds, 20-30% Debt funds
• **Age 30-40:** 60-70% Equity funds, 30-40% Debt funds  
• **Age 40-50:** 50-60% Equity funds, 40-50% Debt funds

**Best SIP Amount:**
Start with at least ₹1,000 per month. Increase by 10-15% annually.

**Recommended Fund Types:**
• Large Cap funds for stability
• Mid Cap funds for growth (if risk tolerance is high)
• ELSS funds for tax saving
• Debt funds for stability

Would you like me to create a personalized SIP portfolio for you?""",
                    'suggestions': [
                        "Create personalized SIP portfolio",
                        "Compare mutual funds",
                        "Calculate SIP returns",
                        "Tax-saving ELSS funds"
                    ]
                }
            
            elif 'elss' in query_lower or 'tax' in query_lower:
                return {
                    'text': """💸 **ELSS Tax-Saving Funds:**

**What is ELSS?**
Equity Linked Savings Scheme - Mutual funds that offer tax deduction under Section 80C.

**Key Benefits:**
• Tax deduction up to ₹1.5 lakh under Section 80C
• Potential for higher returns than traditional tax-saving options
• Only 3-year lock-in period (shortest among 80C options)
• Professional fund management

**ELSS vs Other 80C Options:**
• PPF: 15-year lock-in, 7-8% returns
• NSC: 5-year lock-in, 6-7% returns
• ELSS: 3-year lock-in, 12-15% potential returns

**Investment Strategy:**
• Invest ₹12,500 monthly to maximize ₹1.5L annual limit
• Choose funds with consistent 3-year performance
• Consider large-cap ELSS for lower risk

**Top ELSS Categories:**
• Large Cap ELSS for stability
• Multi-cap ELSS for balanced approach
• Flexi-cap ELSS for growth potential

Would you like specific ELSS fund recommendations?""",
                    'suggestions': [
                        "Get ELSS fund recommendations",
                        "Calculate tax savings",
                        "Compare ELSS vs PPF",
                        "ELSS SIP calculator"
                    ]
                }
            
            else:
                return {
                    'text': """📊 **Mutual Fund Investment Guide:**

**Types of Mutual Funds:**

**Equity Funds (Higher Risk, Higher Returns):**
• Large Cap: Invest in top 100 companies (Stable)
• Mid Cap: Invest in mid-sized companies (Growth potential)
• Small Cap: Invest in smaller companies (High risk/reward)

**Debt Funds (Lower Risk, Stable Returns):**
• Ultra Short Duration: 3-6 months investment horizon
• Short Duration: 1-3 years investment horizon
• Medium Duration: 3-4 years investment horizon

**Hybrid Funds (Balanced Approach):**
• Conservative: 10-25% equity, rest debt
• Balanced: 65-80% equity, rest debt
• Aggressive: 65-80% equity, rest debt

**How to Choose:**
1. Define your investment goal
2. Assess your risk tolerance
3. Decide investment horizon
4. Check fund performance and expense ratio
5. Consider fund manager track record

**Key Metrics to Check:**
• 3-year and 5-year returns
• Expense ratio (lower is better)
• AUM size (larger is generally better)
• Fund manager experience

Would you like help choosing funds based on your profile?""",
                    'suggestions': [
                        "Get personalized fund recommendations",
                        "Compare fund performance",
                        "Calculate mutual fund returns",
                        "Learn about SIP investing"
                    ]
                }
            
        except Exception as e:
            print(f"❌ Error handling mutual fund query: {str(e)}")
            return {
                'text': "I encountered an error with mutual fund analysis. Please try asking about specific fund types or SIP planning.",
                'suggestions': []
            }
    
    def handle_ipo_query(self, query_lower, original_query):
        """Handle IPO-related queries with unique insights"""
        return {
            'text': """🚀 **IPO Investment Intelligence (Our Unique Feature):**

**What Makes Our IPO Analysis Special:**
Unlike Groww or other platforms, we provide:

**1. Post-IPO Performance Tracking:**
• Track performance for 30, 60, and 90 days after listing
• Analyze if you should hold or exit after listing
• Predict liquidity and trading volumes

**2. Retail Sentiment Impact Analysis:**
• How retail investor mood affects IPO pricing
• Social media buzz and news sentiment analysis
• Predict if IPO will sustain gains or fall

**3. Hold/Exit Recommendations:**
• Specific advice: HOLD, PARTIAL EXIT, or FULL EXIT
• Target prices and stop-loss levels
• Confidence scores for recommendations

**IPO Investment Strategy:**
• **Before Listing:** Check fundamentals, subscription levels, market conditions
• **Listing Day:** Don't get carried away by initial euphoria
• **Post-Listing:** Use our unique tracking for exit decisions

**Key IPO Metrics We Analyze:**
• Subscription levels (higher = better demand)
• Price band vs peer comparison
• Promoter holding and lock-in period
• Use of funds and business model
• Market conditions and sector performance

**Our Recommendation Process:**
1. Analyze company fundamentals
2. Check market sentiment and conditions
3. Evaluate subscription demand
4. Provide subscription advice with reasoning
5. Track post-listing performance
6. Give hold/exit recommendations

Would you like analysis of any specific IPO?""",
            'suggestions': [
                "Analyze current IPO opportunities",
                "Get post-IPO performance tracking",
                "Learn IPO evaluation criteria",
                "Check IPO market sentiment"
            ]
        }
    
    def handle_risk_query(self, query_lower, original_query):
        """Handle risk management and portfolio queries"""
        return {
            'text': """🛡️ **Risk Management & Portfolio Optimization:**

**Understanding Investment Risk:**

**Types of Risk:**
• **Market Risk:** Overall market movements (Beta measures this)
• **Company Risk:** Specific to individual companies
• **Sector Risk:** Industry-specific risks
• **Liquidity Risk:** Difficulty in buying/selling
• **Inflation Risk:** Purchasing power erosion

**Risk Assessment Metrics:**
• **Beta:** Measures stock volatility vs market (>1 = more volatile)
• **Standard Deviation:** Measures price volatility
• **Sharpe Ratio:** Risk-adjusted returns (higher = better)
• **VaR (Value at Risk):** Maximum expected loss

**Portfolio Diversification Rules:**
• **Sector Diversification:** Max 25% in any single sector
• **Stock Concentration:** Max 10% in any single stock
• **Asset Classes:** Mix equity, debt, gold, real estate
• **Geographic:** Consider international exposure

**Risk Management Strategies:**
1. **Asset Allocation:** Age-based equity allocation (100 - Age)
2. **Stop Loss:** Set 8-10% stop loss for individual stocks
3. **Position Sizing:** Don't put all money in one investment
4. **Regular Review:** Rebalance portfolio quarterly
5. **Emergency Fund:** Keep 6 months expenses in liquid funds

**Our Risk Analysis:**
• Calculate portfolio risk score (0-100)
• Identify concentration risks
• Suggest optimal asset allocation
• Provide rebalancing recommendations

**Risk Tolerance Assessment:**
• **Conservative:** 30-40% equity, 60-70% debt
• **Moderate:** 50-70% equity, 30-50% debt
• **Aggressive:** 70-90% equity, 10-30% debt

Would you like a risk assessment of your current portfolio?""",
            'suggestions': [
                "Assess my portfolio risk",
                "Get diversification recommendations",
                "Calculate optimal asset allocation",
                "Learn about stop-loss strategies"
            ]
        }
    
    def handle_market_query(self, query_lower, original_query):
        """Handle market analysis and trend queries"""
        try:
            # Get real market data
            nifty_data = self.get_market_index_data('^NSEI')
            
            market_status = "neutral"
            if nifty_data and nifty_data['change_percent'] > 1:
                market_status = "bullish"
            elif nifty_data and nifty_data['change_percent'] < -1:
                market_status = "bearish"
            
            market_advice = f"""📈 **Market Analysis & Trends:**

**Current Market Status:**
• NIFTY 50: {nifty_data['current_level']:.2f} ({nifty_data['change_percent']:+.2f}%)
• Market Trend: {market_status.upper()}
• RSI Level: {nifty_data['rsi']:.1f}

**Technical Analysis:**
• **Moving Averages:** {"Bullish" if nifty_data['current_level'] > nifty_data['ma_50'] else "Bearish"} (Price vs 50-day MA)
• **Momentum:** {"Positive" if nifty_data['rsi'] > 50 else "Negative"} (RSI-based)
• **Volatility:** {"High" if abs(nifty_data['change_percent']) > 2 else "Moderate"}

**Market Sentiment Factors:**
• Global market trends and FII flows
• Domestic economic indicators
• Corporate earnings and results
• Government policies and announcements
• Geopolitical events and crude oil prices

**Investment Strategy Based on Market:**
• **Bull Market:** Focus on growth stocks, momentum investing
• **Bear Market:** Defensive stocks, value investing, SIP approach
• **Sideways Market:** Sector rotation, dividend-paying stocks

**Market Timing Tips:**
• Don't try to time the market perfectly
• Use SIP for regular investments
• Buy quality stocks during market corrections
• Maintain long-term perspective

**Current Recommendations:**
{"• Good time for fresh investments" if market_status == "bearish" else "• Be cautious, consider profit booking" if market_status == "bullish" else "• Continue regular SIP investments"}
• Focus on fundamentally strong companies
• Maintain diversified portfolio
• Keep some cash for opportunities

Would you like sector-wise market analysis?""" if nifty_data else """📈 **Market Analysis:**

I'm currently updating market data. Here's general market guidance:

**Market Investment Principles:**
• Markets are cyclical - ups and downs are normal
• Long-term investing beats short-term trading
• Diversification reduces risk
• Regular SIP investments work in all market conditions

**Market Indicators to Watch:**
• NIFTY 50 and SENSEX levels and trends
• FII/DII buying and selling patterns
• Global market movements (US, Europe, Asia)
• Economic indicators (GDP, inflation, interest rates)

Would you like me to get current market data for detailed analysis?"""
            
            return {
                'text': market_advice,
                'suggestions': [
                    "Get sector-wise analysis",
                    "Check FII/DII activity",
                    "Analyze market volatility",
                    "Get investment strategy for current market"
                ],
                'data': nifty_data if nifty_data else {}
            }
            
        except Exception as e:
            print(f"❌ Error handling market query: {str(e)}")
            return {
                'text': "I encountered an error getting market data. Please try again for current market analysis.",
                'suggestions': []
            }
    
    def get_market_index_data(self, index_symbol):
        """Get real market index data"""
        try:
            ticker = yf.Ticker(index_symbol)
            hist_data = ticker.history(period="6mo")
            
            if hist_data.empty:
                return None
            
            current_level = hist_data['Close'].iloc[-1]
            prev_close = hist_data['Close'].iloc[-2] if len(hist_data) > 1 else current_level
            change_percent = ((current_level - prev_close) / prev_close) * 100
            
            # Calculate technical indicators
            prices = hist_data['Close']
            ma_20 = prices.rolling(window=20).mean().iloc[-1]
            ma_50 = prices.rolling(window=50).mean().iloc[-1]
            
            # RSI calculation
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            return {
                'current_level': current_level,
                'change_percent': change_percent,
                'ma_20': ma_20,
                'ma_50': ma_50,
                'rsi': current_rsi,
                'volume': hist_data['Volume'].iloc[-1]
            }
            
        except Exception as e:
            print(f"❌ Error getting market data: {str(e)}")
            return None
    
    def handle_tax_query(self, query_lower, original_query):
        """Handle tax planning queries"""
        return {
            'text': """💸 **Tax-Efficient Investment Planning:**

**Tax-Saving Investment Options (Section 80C):**

**1. ELSS Mutual Funds (Recommended):**
• Deduction: Up to ₹1.5 lakh
• Lock-in: 3 years (shortest)
• Returns: 12-15% potential
• Liquidity: Can sell after 3 years

**2. PPF (Public Provident Fund):**
• Deduction: Up to ₹1.5 lakh
• Lock-in: 15 years
• Returns: 7-8% (tax-free)
• Liquidity: Partial withdrawal after 7 years

**3. NSC (National Savings Certificate):**
• Deduction: Up to ₹1.5 lakh
• Lock-in: 5 years
• Returns: 6-7%
• Liquidity: No premature withdrawal

**Capital Gains Tax:**

**Equity Investments:**
• **STCG (Short Term):** <1 year = 15% tax
• **LTCG (Long Term):** >1 year = 10% tax (above ₹1 lakh gain)

**Debt Investments:**
• **STCG:** <3 years = As per income tax slab
• **LTCG:** >3 years = 20% with indexation

**Tax Optimization Strategies:**
1. **Harvest Losses:** Sell losing investments to offset gains
2. **Hold for Long Term:** Benefit from lower LTCG rates
3. **SIP Approach:** Spread investments across financial years
4. **ELSS for 80C:** Better than traditional options
5. **Debt Funds:** Better than FDs for higher tax brackets

**Tax-Efficient Portfolio:**
• 60-70% Equity (for LTCG benefit)
• 20-30% Debt funds (better than FDs)
• 10% ELSS (for tax saving)

**Annual Tax Planning:**
• Invest ₹1.5L in 80C options by March
• Plan capital gains harvesting in March
• Consider tax-loss harvesting
• Review and rebalance portfolio

Would you like a personalized tax-saving investment plan?""",
            'suggestions': [
                "Create tax-saving investment plan",
                "Compare ELSS vs PPF vs NSC",
                "Calculate capital gains tax",
                "Learn about tax-loss harvesting"
            ]
        }
    
    def handle_general_query(self, query_lower, original_query):
        """Handle general investment advice queries"""
        return {
            'text': """💡 **General Investment Guidance:**

**Investment Fundamentals:**

**1. Start Early:**
• Power of compounding works best over time
• Even ₹1,000 monthly SIP can create significant wealth
• Time in market > Timing the market

**2. Emergency Fund First:**
• Keep 6 months of expenses in liquid funds
• This should be your first financial goal
• Only then start investing in markets

**3. Asset Allocation Strategy:**
• **Age-based Rule:** Equity % = 100 - Your Age
• **Risk-based:** Conservative (30% equity), Moderate (60% equity), Aggressive (80% equity)
• **Goal-based:** Short-term goals (debt), Long-term goals (equity)

**4. Diversification:**
• Don't put all eggs in one basket
• Spread across sectors, asset classes, geographies
• Maximum 10% in any single stock

**5. Regular Review:**
• Review portfolio every 6 months
• Rebalance when allocation drifts >5%
• Stay updated with market trends

**Investment Ladder by Age:**

**Age 20-30:**
• 70-80% Equity, 20-30% Debt
• Focus on growth and wealth creation
• High risk tolerance

**Age 30-40:**
• 60-70% Equity, 30-40% Debt
• Balance growth with stability
• Moderate risk tolerance

**Age 40-50:**
• 50-60% Equity, 40-50% Debt
• Focus on wealth preservation
• Lower risk tolerance

**Age 50+:**
• 30-40% Equity, 60-70% Debt
• Capital preservation priority
• Conservative approach

**Common Investment Mistakes:**
• Trying to time the market
• Putting all money in one investment
• Not having an emergency fund
• Emotional investing (fear and greed)
• Not reviewing and rebalancing

**My Recommendation:**
Start with SIP in diversified equity funds, build emergency fund, and gradually learn about different investment options.

What specific investment goal would you like help with?""",
            'suggestions': [
                "Create investment plan for specific goal",
                "Learn about SIP investing",
                "Get portfolio review",
                "Understand risk assessment"
            ]
        }
    
    def handle_unknown_query(self, original_query):
        """Handle queries that don't fit specific categories"""
        return {
            'text': f"""🤖 **I'm here to help with your investment questions!**

I didn't fully understand your query: "{original_query}"

**I can help you with:**

**📊 Stock Analysis:**
• "Should I buy HDFC Bank stock?"
• "What's the technical analysis of Reliance?"
• "Is TCS a good investment now?"

**💰 Mutual Funds & SIP:**
• "Recommend SIP portfolio for ₹10,000 monthly"
• "Which ELSS fund is best for tax saving?"
• "How to choose mutual funds?"

**🚀 IPO Analysis (Our Unique Feature):**
• "Should I apply for XYZ IPO?"
• "When should I exit after IPO listing?"
• "Analyze recent IPO performance"

**🛡️ Risk Management:**
• "Assess my portfolio risk"
• "How to diversify my investments?"
• "What's optimal asset allocation for my age?"

**📈 Market Analysis:**
• "What's the current market trend?"
• "Is this a good time to invest?"
• "How are different sectors performing?"

**💸 Tax Planning:**
• "Best tax-saving investments"
• "ELSS vs PPF comparison"
• "How to save capital gains tax?"

Please ask me about any of these topics, and I'll provide detailed, personalized advice!""",
            'suggestions': [
                "Ask about stock analysis",
                "Get SIP recommendations",
                "Learn about IPO investing",
                "Check market trends",
                "Get tax-saving advice"
            ]
        }
    
    def calculate_response_confidence(self, query_type, user_query):
        """Calculate confidence score for the response"""
        try:
            base_confidence = {
                'stock_analysis': 0.85,
                'mutual_funds': 0.90,
                'ipo_analysis': 0.95,  # Our unique feature
                'risk_management': 0.88,
                'market_analysis': 0.80,
                'tax_planning': 0.85,
                'general_advice': 0.75,
                'unknown': 0.30
            }
            
            confidence = base_confidence.get(query_type, 0.50)
            
            # Adjust based on query specificity
            if len(user_query.split()) > 5:
                confidence += 0.05  # More specific queries
            
            # Adjust based on keywords
            specific_keywords = ['buy', 'sell', 'invest', 'recommend', 'analysis', 'performance']
            if any(keyword in user_query.lower() for keyword in specific_keywords):
                confidence += 0.05
            
            return min(confidence, 0.95)  # Cap at 95%
            
        except Exception as e:
            print(f"❌ Error calculating confidence: {str(e)}")
            return 0.50
    
    def store_conversation(self, user_id, user_query, ai_response, query_type, confidence_score):
        """Store conversation in database for learning"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ai_conversations 
                (user_id, user_query, ai_response, query_type, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, user_query, ai_response, query_type, confidence_score))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing conversation: {str(e)}")
    
    def get_conversation_history(self, user_id, limit=10):
        """Get user's conversation history"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            query = '''
                SELECT user_query, ai_response, query_type, confidence_score, created_at
                FROM ai_conversations 
                WHERE user_id = ?
                ORDER BY created_at DESC 
                LIMIT ?
            '''
            
            history_df = pd.read_sql_query(query, conn, params=[user_id, limit])
            conn.close()
            
            return history_df.to_dict('records') if not history_df.empty else []
            
        except Exception as e:
            print(f"❌ Error getting conversation history: {str(e)}")
            return []

# Test the AI Investment Assistant
if __name__ == "__main__":
    print("🤖 Testing AI Investment Assistant...")
    
    ai_assistant = AIInvestmentAssistant()
    
    # Test queries
    test_queries = [
        "Should I buy HDFC Bank stock?",
        "Recommend SIP portfolio for ₹15000 monthly",
        "What's the current market trend?",
        "Best ELSS funds for tax saving",
        "Should I apply for upcoming IPO?"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        response = ai_assistant.process_user_query(query)
        print(f"✅ Response Type: {response['query_type']}")
        print(f"📊 Confidence: {response['confidence']:.2%}")
        print(f"💬 Response: {response['response'][:200]}...")
    
    print("\n✅ AI Investment Assistant test completed!")