"""
Agentic AI System for Investment Platform
Real-time, Advanced, Accurate Analysis
"""

import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
import yfinance as yf
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
from langchain.tools import Tool
import streamlit as st

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")

# Initialize LLM with correct parameters for langchain-groq
try:
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="mixtral-8x7b-32768"
    )
    print("✅ LLM initialized successfully")
except Exception as e:
    print(f"⚠️ LLM initialization warning: {e}")
    # Create a minimal LLM object for import to work
    llm = None

# ==================== TOOLS FOR AGENTS ====================

def fetch_real_time_stock_data(symbol: str) -> Dict[str, Any]:
    """Fetch real-time stock data"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='30d')
        info = ticker.info
        
        if hist.empty:
            return {"error": "No data available"}
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        
        # Technical indicators
        ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
        ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else ma_20
        
        # RSI
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1]
        
        # Volume
        avg_volume = hist['Volume'].mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume
        
        return {
            'symbol': symbol,
            'current_price': float(current_price),
            'previous_close': float(prev_close),
            'change_percent': float(((current_price - prev_close) / prev_close) * 100),
            'ma_20': float(ma_20),
            'ma_50': float(ma_50),
            'rsi': float(current_rsi),
            'volume_ratio': float(volume_ratio),
            'avg_volume': float(avg_volume),
            'current_volume': float(current_volume),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            '52_week_high': info.get('fiftyTwoWeekHigh', 0),
            '52_week_low': info.get('fiftyTwoWeekLow', 0),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_fii_dii_data() -> Dict[str, Any]:
    """Fetch real-time FII/DII data"""
    try:
        import requests
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.nseindia.com/'
        })
        
        # Get cookies
        session.get('https://www.nseindia.com', timeout=10)
        
        # Fetch FII/DII data
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

def fetch_market_sentiment() -> Dict[str, Any]:
    """Fetch overall market sentiment"""
    try:
        # Fetch NIFTY data
        nifty = yf.Ticker('^NSEI')
        nifty_hist = nifty.history(period='5d')
        
        if not nifty_hist.empty:
            current = nifty_hist['Close'].iloc[-1]
            prev = nifty_hist['Close'].iloc[0]
            change = ((current - prev) / prev) * 100
            
            # Determine sentiment
            if change > 2:
                sentiment = "Very Bullish"
                score = 0.9
            elif change > 0.5:
                sentiment = "Bullish"
                score = 0.7
            elif change > -0.5:
                sentiment = "Neutral"
                score = 0.5
            elif change > -2:
                sentiment = "Bearish"
                score = 0.3
            else:
                sentiment = "Very Bearish"
                score = 0.1
            
            return {
                'sentiment': sentiment,
                'score': score,
                'nifty_change': float(change),
                'nifty_current': float(current),
                'timestamp': datetime.now().isoformat()
            }
        
        return {"error": "Unable to fetch market sentiment"}
    except Exception as e:
        return {"error": str(e)}

def analyze_portfolio_risk(holdings: List[Dict]) -> Dict[str, Any]:
    """Analyze portfolio risk metrics"""
    try:
        if not holdings:
            return {"error": "No holdings provided"}
        
        total_value = sum(h.get('current_value', 0) for h in holdings)
        
        # Calculate diversification
        unique_stocks = len(holdings)
        diversification_score = min(100, (unique_stocks / 20) * 100)
        
        # Calculate concentration
        max_holding = max(h.get('current_value', 0) for h in holdings)
        concentration = (max_holding / total_value * 100) if total_value > 0 else 0
        
        # Risk level
        if concentration > 30:
            risk_level = "High"
        elif concentration > 20:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            'total_value': total_value,
            'num_holdings': unique_stocks,
            'diversification_score': diversification_score,
            'concentration': concentration,
            'risk_level': risk_level,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

# Create Tools
stock_data_tool = Tool(
    name="Real-Time Stock Data",
    func=fetch_real_time_stock_data,
    description="Fetches real-time stock data including price, technical indicators, and fundamentals. Input: stock symbol (e.g., 'RELIANCE.NS')"
)

fii_dii_tool = Tool(
    name="FII/DII Data",
    func=fetch_fii_dii_data,
    description="Fetches real-time Foreign and Domestic Institutional Investor data from NSE"
)

market_sentiment_tool = Tool(
    name="Market Sentiment",
    func=fetch_market_sentiment,
    description="Analyzes overall market sentiment based on NIFTY movement"
)

portfolio_risk_tool = Tool(
    name="Portfolio Risk Analysis",
    func=analyze_portfolio_risk,
    description="Analyzes portfolio risk metrics including diversification and concentration"
)

# ==================== AGENTS ====================

# 1. Stock Analyst Agent
stock_analyst_agent = Agent(
    role='Senior Stock Market Analyst',
    goal='Provide accurate, data-driven stock analysis and recommendations',
    backstory="""You are a highly experienced stock market analyst with 20+ years of experience.
    You specialize in technical and fundamental analysis of Indian stocks.
    You always base your recommendations on real-time data and proven indicators.
    You are known for your accuracy and conservative approach to risk.""",
    tools=[stock_data_tool, market_sentiment_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# 2. Smart Money Tracker Agent
smart_money_agent = Agent(
    role='Institutional Money Flow Analyst',
    goal='Track and analyze institutional investor movements to identify smart money trends',
    backstory="""You are an expert in tracking institutional money flows.
    You understand FII/DII behavior and can predict market movements based on their actions.
    You have a proven track record of identifying accumulation and distribution patterns.
    You always follow the smart money.""",
    tools=[fii_dii_tool, market_sentiment_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# 3. Risk Management Agent
risk_manager_agent = Agent(
    role='Portfolio Risk Manager',
    goal='Ensure portfolio safety through comprehensive risk analysis and management',
    backstory="""You are a certified risk management professional.
    You specialize in portfolio risk assessment and mitigation strategies.
    You prioritize capital preservation while maximizing risk-adjusted returns.
    You are conservative and always err on the side of caution.""",
    tools=[portfolio_risk_tool, stock_data_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

# 4. Market Strategist Agent
market_strategist_agent = Agent(
    role='Chief Market Strategist',
    goal='Develop comprehensive investment strategies based on market conditions',
    backstory="""You are a chief market strategist with deep understanding of market cycles.
    You can synthesize information from multiple sources to create winning strategies.
    You have successfully navigated bull and bear markets.
    You provide clear, actionable investment strategies.""",
    tools=[market_sentiment_tool, fii_dii_tool, stock_data_tool],
    llm=llm,
    verbose=True,
    allow_delegation=True
)

# ==================== AGENTIC WORKFLOWS ====================

class AgenticStockAnalysis:
    """Complete agentic stock analysis workflow"""
    
    def __init__(self):
        self.llm = llm
    
    def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """Run multi-agent stock analysis"""
        
        # Task 1: Technical Analysis
        technical_task = Task(
            description=f"""Analyze {symbol} using real-time data.
            
            Steps:
            1. Fetch current stock data using the Real-Time Stock Data tool
            2. Analyze technical indicators (RSI, Moving Averages, Volume)
            3. Identify support and resistance levels
            4. Determine trend direction
            5. Provide technical score (0-10)
            
            Output Format:
            - Current Price: [price]
            - Technical Score: [0-10]
            - RSI Analysis: [overbought/oversold/neutral]
            - Trend: [bullish/bearish/neutral]
            - Key Levels: [support and resistance]
            - Technical Recommendation: [BUY/SELL/HOLD]
            """,
            agent=stock_analyst_agent,
            expected_output="Detailed technical analysis with clear recommendation"
        )
        
        # Task 2: Smart Money Analysis
        smart_money_task = Task(
            description=f"""Analyze institutional money flow for {symbol}.
            
            Steps:
            1. Fetch FII/DII data using the FII/DII Data tool
            2. Analyze institutional buying/selling patterns
            3. Check market sentiment using Market Sentiment tool
            4. Determine if smart money is accumulating or distributing
            5. Provide institutional score (0-10)
            
            Output Format:
            - FII Net Flow: [value in Cr]
            - DII Net Flow: [value in Cr]
            - Institutional Score: [0-10]
            - Smart Money Signal: [accumulation/distribution/neutral]
            - Market Sentiment: [bullish/bearish/neutral]
            - Institutional Recommendation: [BUY/SELL/HOLD]
            """,
            agent=smart_money_agent,
            expected_output="Institutional money flow analysis with recommendation"
        )
        
        # Task 3: Final Strategy
        strategy_task = Task(
            description=f"""Create final investment strategy for {symbol}.
            
            Based on:
            - Technical analysis from Stock Analyst
            - Institutional flow from Smart Money Tracker
            
            Provide:
            1. Overall Score (0-10)
            2. Final Recommendation: STRONG BUY/BUY/HOLD/SELL/STRONG SELL
            3. Confidence Level: 0-100%
            4. Entry Price Range
            5. Target Price (3 months)
            6. Stop Loss Level
            7. Risk Level: Low/Medium/High
            8. Investment Horizon: Short/Medium/Long term
            9. Key Reasons (top 3)
            10. Key Risks (top 3)
            
            Be specific and actionable.
            """,
            agent=market_strategist_agent,
            expected_output="Comprehensive investment strategy with clear action plan",
            context=[technical_task, smart_money_task]
        )
        
        # Create Crew
        crew = Crew(
            agents=[stock_analyst_agent, smart_money_agent, market_strategist_agent],
            tasks=[technical_task, smart_money_task, strategy_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute
        try:
            result = crew.kickoff()
            return {
                'success': True,
                'symbol': symbol,
                'analysis': str(result),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class AgenticPortfolioManager:
    """Autonomous portfolio management"""
    
    def __init__(self):
        self.llm = llm
    
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict[str, Any]:
        """Run multi-agent portfolio analysis"""
        
        # Task 1: Risk Assessment
        risk_task = Task(
            description=f"""Analyze portfolio risk for holdings: {holdings}
            
            Steps:
            1. Use Portfolio Risk Analysis tool to get risk metrics
            2. Analyze diversification
            3. Check concentration risk
            4. Identify over-exposed positions
            5. Provide risk score (0-10, where 10 is highest risk)
            
            Output Format:
            - Risk Score: [0-10]
            - Risk Level: [Low/Medium/High]
            - Diversification: [Good/Moderate/Poor]
            - Top Risks: [list top 3]
            - Recommended Actions: [specific actions to reduce risk]
            """,
            agent=risk_manager_agent,
            expected_output="Comprehensive risk assessment with actionable recommendations"
        )
        
        # Task 2: Market Alignment
        alignment_task = Task(
            description="""Analyze if portfolio is aligned with current market conditions.
            
            Steps:
            1. Check market sentiment using Market Sentiment tool
            2. Check institutional flow using FII/DII Data tool
            3. Determine if portfolio positioning is appropriate
            4. Suggest rebalancing if needed
            
            Output Format:
            - Market Condition: [bullish/bearish/neutral]
            - Portfolio Alignment: [aligned/misaligned]
            - Rebalancing Needed: [yes/no]
            - Suggested Changes: [specific recommendations]
            """,
            agent=market_strategist_agent,
            expected_output="Portfolio alignment analysis with rebalancing suggestions"
        )
        
        # Task 3: Action Plan
        action_task = Task(
            description="""Create comprehensive portfolio action plan.
            
            Based on:
            - Risk assessment
            - Market alignment analysis
            
            Provide:
            1. Overall Portfolio Health: [Excellent/Good/Fair/Poor]
            2. Immediate Actions: [list with priority]
            3. Short-term Strategy (1-3 months)
            4. Long-term Strategy (6-12 months)
            5. Stocks to Add: [with reasoning]
            6. Stocks to Reduce/Exit: [with reasoning]
            7. Target Allocation: [sector-wise %]
            8. Expected Returns: [realistic estimate]
            9. Risk Mitigation Steps: [specific actions]
            10. Review Schedule: [when to review next]
            """,
            agent=market_strategist_agent,
            expected_output="Detailed action plan for portfolio optimization",
            context=[risk_task, alignment_task]
        )
        
        # Create Crew
        crew = Crew(
            agents=[risk_manager_agent, market_strategist_agent],
            tasks=[risk_task, alignment_task, action_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute
        try:
            result = crew.kickoff()
            return {
                'success': True,
                'analysis': str(result),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

class AgenticMarketIntelligence:
    """Real-time market intelligence"""
    
    def __init__(self):
        self.llm = llm
    
    def get_market_intelligence(self) -> Dict[str, Any]:
        """Get comprehensive market intelligence"""
        
        # Task: Market Analysis
        market_task = Task(
            description="""Provide comprehensive market intelligence report.
            
            Steps:
            1. Check market sentiment using Market Sentiment tool
            2. Analyze FII/DII flow using FII/DII Data tool
            3. Identify market trends
            4. Predict short-term direction
            5. Suggest trading strategy
            
            Output Format:
            - Market Status: [bullish/bearish/neutral]
            - NIFTY Trend: [up/down/sideways]
            - FII Activity: [buying/selling/neutral]
            - DII Activity: [buying/selling/neutral]
            - Market Prediction (1 week): [direction with confidence]
            - Sectors to Watch: [top 3 sectors]
            - Trading Strategy: [specific actionable strategy]
            - Risk Factors: [top 3 risks]
            - Opportunities: [top 3 opportunities]
            """,
            agent=market_strategist_agent,
            expected_output="Comprehensive market intelligence report"
        )
        
        # Create Crew
        crew = Crew(
            agents=[market_strategist_agent],
            tasks=[market_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute
        try:
            result = crew.kickoff()
            return {
                'success': True,
                'intelligence': str(result),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# ==================== EXPORT CLASSES ====================

__all__ = [
    'AgenticStockAnalysis',
    'AgenticPortfolioManager',
    'AgenticMarketIntelligence',
    'llm'
]
