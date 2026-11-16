"""
Enhanced Quick Actions for AI Investment Assistant
Real, Dynamic, and Insightful implementations
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]
    except:
        return 50

def calculate_sip_returns(monthly_sip, annual_return, years):
    """Calculate SIP future value"""
    months = years * 12
    monthly_rate = (annual_return / 100) / 12
    
    if monthly_rate > 0:
        future_value = monthly_sip * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
    else:
        future_value = monthly_sip * months
    
    return future_value

def handle_quick_action_enhanced(action, INDIAN_STOCKS, get_stock_data, get_realtime_mutual_funds, 
                                 get_realtime_news, GROQ_AI_AVAILABLE, GROQ_API_KEY, GroqAIAnalyzer,
                                 get_nifty_data_robust, REALTIME_NEWS_AVAILABLE):
    """Enhanced quick action handler with real data"""
    
    if action == 'analyze_stock':
        st.markdown("### 📊 Comprehensive Stock Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            stock_symbol = st.selectbox(
                "Select Stock",
                list(INDIAN_STOCKS.keys()),
                format_func=lambda x: f"{INDIAN_STOCKS[x]} ({x.replace('.NS', '')})"
            )
        
        with col2:
            period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"])
        
        if st.button("🚀 Analyze", type="primary", use_container_width=True):
            with st.spinner("Analyzing..."):
                stock_data = get_stock_data(stock_symbol, period)
                
                if not stock_data.empty:
                    current = stock_data['Close'].iloc[-1]
                    prev = stock_data['Close'].iloc[0]
                    change = ((current - prev) / prev) * 100
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Price", f"₹{current:.2f}", f"{change:+.2f}%")
                    with col2:
                        st.metric("High", f"₹{stock_data['High'].max():.2f}")
                    with col3:
                        st.metric("Low", f"₹{stock_data['Low'].min():.2f}")
                    with col4:
                        vol = stock_data['Close'].pct_change().std() * np.sqrt(252) * 100
                        st.metric("Volatility", f"{vol:.2f}%")
                    
                    # Chart
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=stock_data.index,
                        open=stock_data['Open'],
                        high=stock_data['High'],
                        low=stock_data['Low'],
                        close=stock_data['Close']
                    ))
                    fig.update_layout(
                        title=f"{INDIAN_STOCKS[stock_symbol]} Price",
                        height=400,
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # AI Analysis
                    if GROQ_AI_AVAILABLE:
                        rsi = calculate_rsi(stock_data['Close'])
                        sma20 = stock_data['Close'].rolling(20).mean().iloc[-1]
                        
                        prompt = f"""Analyze {INDIAN_STOCKS[stock_symbol]}:
Price: ₹{current:.2f} ({change:+.2f}%)
RSI: {rsi:.2f}
SMA20: ₹{sma20:.2f}

Provide: Assessment, Signals, Recommendation, Target, Stop Loss"""
                        
                        analyzer = GroqAIAnalyzer(GROQ_API_KEY)
                        response = analyzer._call_groq(prompt)
                        
                        if response:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(0,255,136,0.1)); 
                                        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #00d4ff;'>
                                {response}
                            </div>
                            """, unsafe_allow_html=True)
    
    elif action == 'best_sip':
        st.markdown("### 💰 Best SIP Recommendations")
        
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Monthly SIP (₹)", 500, 100000, 5000, 500)
        with col2:
            risk = st.selectbox("Risk", ["Conservative", "Moderate", "Aggressive"])
        
        if st.button("Get Recommendations", type="primary", use_container_width=True):
            with st.spinner("Analyzing funds..."):
                funds, total = get_realtime_mutual_funds()
                
                if funds:
                    st.success(f"✅ Analyzed {total} funds")
                    
                    categories = ['Debt', 'Hybrid'] if risk == "Conservative" else ['Large Cap', 'Hybrid'] if risk == "Moderate" else ['Mid Cap', 'Small Cap']
                    
                    for cat in categories[:2]:
                        if cat in funds and funds[cat]:
                            fund = sorted(funds[cat], key=lambda x: x.get('return_3y', 0), reverse=True)[0]
                            
                            with st.expander(f"{fund['name'][:50]}... - ⭐{fund['rating']}/5"):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("NAV", f"₹{fund['nav']:.2f}")
                                with col2:
                                    st.metric("3Y Return", f"{fund.get('return_3y', 0):.2f}%")
                                with col3:
                                    st.metric("Min SIP", f"₹{fund['min_sip']}")
                                
                                # Projection
                                future = calculate_sip_returns(amount, fund.get('return_3y', 12), 10)
                                invested = amount * 120
                                st.metric("10Y Value", f"₹{future:,.0f}", f"Gain: ₹{future-invested:,.0f}")
    
    elif action == 'portfolio_review':
        st.markdown("### 🎯 Portfolio Review")
        
        portfolio = st.text_area("Enter holdings (one per line)", 
                                 placeholder="HDFC Bank - 40%\nTCS - 30%\nAxis Fund - 20%\nGold - 10%",
                                 height=120)
        
        if st.button("Review", type="primary", use_container_width=True):
            if portfolio and GROQ_AI_AVAILABLE:
                with st.spinner("Analyzing..."):
                    prompt = f"""Review portfolio:
{portfolio}

Provide: Diversification Score (1-10), Strengths, Weaknesses, Recommendations"""
                    
                    analyzer = GroqAIAnalyzer(GROQ_API_KEY)
                    response = analyzer._call_groq(prompt)
                    
                    if response:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, rgba(255,193,7,0.1), rgba(255,152,0,0.1)); 
                                    padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ffc107;'>
                            {response}
                        </div>
                        """, unsafe_allow_html=True)
    
    elif action == 'market_outlook':
        st.markdown("### 📈 Market Outlook")
        
        timeframe = st.selectbox("Timeframe", ["This Week", "This Month", "This Quarter"])
        
        if st.button("Generate", type="primary", use_container_width=True):
            with st.spinner("Analyzing market..."):
                nifty = get_nifty_data_robust()
                
                if not nifty.empty:
                    current = nifty['Close'].iloc[-1]
                    prev = nifty['Close'].iloc[-2]
                    change = ((current - prev) / prev) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("NIFTY", f"{current:.2f}", f"{change:+.2f}%")
                    with col2:
                        sentiment = "Bullish 🟢" if change > 0 else "Bearish 🔴"
                        st.metric("Sentiment", sentiment)
                    with col3:
                        vol = nifty['Close'].pct_change().std() * 100
                        st.metric("Volatility", f"{vol:.2f}%")
                    
                    if GROQ_AI_AVAILABLE:
                        prompt = f"""Market outlook for {timeframe.lower()}:
NIFTY: {current:.2f} ({change:+.2f}%)

Provide: Direction, Key Factors, Sectors to Watch, Strategy"""
                        
                        analyzer = GroqAIAnalyzer(GROQ_API_KEY)
                        response = analyzer._call_groq(prompt)
                        
                        if response:
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, rgba(255,82,82,0.1), rgba(255,23,68,0.1)); 
                                        padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ff5252;'>
                                {response}
                            </div>
                            """, unsafe_allow_html=True)
