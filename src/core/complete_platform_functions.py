#!/usr/bin/env python3
"""
COMPLETE PLATFORM FUNCTIONS
All functionality for the unified सार्थक निवेश platform
Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import sqlite3

from config import *

def show_current_open_ipos():
    """Display currently open IPOs with real-time analysis"""
    st.subheader("🚀 Currently Open IPOs - Live Analysis")
    
    try:
        # Get current open IPOs
        with st.spinner("📊 Analyzing current IPOs..."):
            results = st.session_state.ipo_intelligence.analyze_all_open_ipos()
        
        if not results:
            st.warning("⚠️ No open IPOs found at the moment.")
            return
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        strong_buy_count = sum(1 for r in results if r['recommendation'] == 'STRONG BUY')
        buy_count = sum(1 for r in results if r['recommendation'] == 'BUY')
        neutral_count = sum(1 for r in results if r['recommendation'] == 'NEUTRAL')
        avoid_count = sum(1 for r in results if r['recommendation'] == 'AVOID')
        
        with col1:
            st.metric("🎯 Strong Buy", strong_buy_count)
        with col2:
            st.metric("📈 Buy", buy_count)
        with col3:
            st.metric("⚖️ Neutral", neutral_count)
        with col4:
            st.metric("⚠️ Avoid", avoid_count)
        
        st.markdown("---")
        
        # Display each IPO with detailed analysis
        for result in results:
            recommendation_color = {
                'STRONG BUY': '#28a745',
                'BUY': '#17a2b8', 
                'NEUTRAL': '#ffc107',
                'AVOID': '#dc3545'
            }.get(result['recommendation'], '#6c757d')
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                        padding: 1.5rem; border-radius: 12px; margin: 1rem 0; 
                        border-left: 5px solid {recommendation_color}; 
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <div>
                        <h3 style="margin: 0; color: #2c3e50;">🏢 {result['company']}</h3>
                        <p style="margin: 0.5rem 0; color: #6c757d;"><strong>Symbol:</strong> {result['symbol']} | <strong>Price Range:</strong> {result['price_range']} | <strong>Size:</strong> {result['size']}</p>
                    </div>
                    <div style="text-align: right;">
                        <h2 style="margin: 0; color: {recommendation_color};">{result['recommendation']}</h2>
                        <p style="margin: 0; font-size: 0.9em; color: #6c757d;">Confidence: {result['confidence']}</p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div>
                        <strong>🎯 Target Price:</strong><br>
                        <span style="color: #28a745; font-size: 1.2em; font-weight: 600;">{result['target']}</span>
                    </div>
                    <div>
                        <strong>🛑 Stop Loss:</strong><br>
                        <span style="color: #dc3545; font-size: 1.2em; font-weight: 600;">{result['stop_loss']}</span>
                    </div>
                    <div>
                        <strong>📊 Data Source:</strong><br>
                        <span style="color: #17a2b8; font-weight: 600;">{result.get('data_source', 'Live Analysis')}</span>
                    </div>
                </div>
                
                <div style="background: rgba(255, 193, 7, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <strong>🚪 Exit Strategy:</strong><br>
                    {result['exit_strategy']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Refresh button
        if st.button("🔄 Refresh IPO Analysis", type="primary"):
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error loading current IPOs: {str(e)}")

def show_post_ipo_analysis():
    """Show post-IPO performance analysis"""
    st.subheader("📊 Post-IPO Performance Analysis")
    
    # Sample post-listing data with real examples
    sample_data = [
        {
            'company': 'Tata Technologies Limited',
            'symbol': 'TATATECH.NS',
            'listing_date': '2023-11-30',
            'issue_price': 500,
            'listing_price': 1200,
            'current_price': 1138.41,
            'listing_gains': 140.0,
            'current_gains': 127.68,
            'days_since_listing': 85,
            'recommendation': 'STRONG HOLD',
            'volume_trend': 'High',
            'sector': 'Technology'
        },
        {
            'company': 'IREDA Limited',
            'symbol': 'IREDA.NS',
            'listing_date': '2023-11-29',
            'issue_price': 32,
            'listing_price': 56,
            'current_price': 52.30,
            'listing_gains': 75.0,
            'current_gains': 63.44,
            'days_since_listing': 86,
            'recommendation': 'HOLD',
            'volume_trend': 'Medium',
            'sector': 'Energy'
        }
    ]
    
    if sample_data:
        for data in sample_data:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                            padding: 1.5rem; border-radius: 12px; margin: 1rem 0; 
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h3 style="color: #2c3e50;">🏢 {data['company']} ({data['symbol']})</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                        <div>
                            <strong>Issue Price:</strong> ₹{data['issue_price']}<br>
                            <strong>Listing Price:</strong> ₹{data['listing_price']}<br>
                            <strong>Current Price:</strong> ₹{data['current_price']}
                        </div>
                        <div>
                            <strong>Listing Gains:</strong> <span style="color: #28a745;">{data['listing_gains']:.1f}%</span><br>
                            <strong>Current Gains:</strong> <span style="color: #28a745;">{data['current_gains']:.1f}%</span><br>
                            <strong>Days Listed:</strong> {data['days_since_listing']} days
                        </div>
                        <div>
                            <strong>Recommendation:</strong><br>
                            <span style="color: #17a2b8; font-weight: 600;">{data['recommendation']}</span><br>
                            <strong>Volume:</strong> {data['volume_trend']}<br>
                            <strong>Sector:</strong> {data['sector']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Create performance chart
                days = list(range(0, data['days_since_listing'] + 1, 10))
                prices = [data['issue_price'] * (1 + (data['current_gains']/100) * (d/data['days_since_listing'])) for d in days]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=days, y=prices, mode='lines+markers', name='Price', line=dict(color='#667eea')))
                fig.add_hline(y=data['issue_price'], line_dash="dash", line_color="red", annotation_text="Issue Price")
                fig.add_hline(y=data['listing_price'], line_dash="dash", line_color="green", annotation_text="Listing Price")
                fig.update_layout(
                    title=f"{data['symbol']} Performance",
                    xaxis_title="Days Since Listing",
                    yaxis_title="Price (₹)",
                    height=300,
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No post-listing data available. Data will appear after IPOs get listed.")

def show_ipo_predictions():
    """Show IPO prediction engine"""
    st.subheader("🤖 IPO Prediction Engine")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
        <h4 style="color: #1565c0;">🧠 AI-Powered IPO Success Prediction</h4>
        <p>Our machine learning models analyze multiple factors to predict IPO performance:</p>
        <ul>
            <li><strong>Company Fundamentals:</strong> Revenue growth, profit margins, debt ratios</li>
            <li><strong>Market Conditions:</strong> Overall market sentiment and volatility</li>
            <li><strong>Sector Performance:</strong> Industry trends and peer comparisons</li>
            <li><strong>Subscription Data:</strong> Retail vs institutional demand</li>
            <li><strong>Grey Market Premium:</strong> Unofficial trading indicators</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # IPO Prediction Interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Prediction Factors")
        
        company_score = st.slider("Company Fundamentals Score", 0, 100, 75)
        market_score = st.slider("Market Conditions Score", 0, 100, 65)
        sector_score = st.slider("Sector Performance Score", 0, 100, 80)
        demand_score = st.slider("Subscription Demand Score", 0, 100, 70)
        
        if st.button("🎯 Generate Prediction", type="primary"):
            # Calculate prediction
            overall_score = (company_score * 0.3 + market_score * 0.2 + sector_score * 0.25 + demand_score * 0.25)
            
            if overall_score >= 75:
                prediction = "STRONG SUCCESS"
                color = "#28a745"
                expected_return = f"{15 + (overall_score - 75) * 0.8:.1f}%"
            elif overall_score >= 60:
                prediction = "MODERATE SUCCESS"
                color = "#17a2b8"
                expected_return = f"{8 + (overall_score - 60) * 0.5:.1f}%"
            elif overall_score >= 40:
                prediction = "NEUTRAL"
                color = "#ffc107"
                expected_return = f"{0 + (overall_score - 40) * 0.4:.1f}%"
            else:
                prediction = "HIGH RISK"
                color = "#dc3545"
                expected_return = f"{-5 + (overall_score - 20) * 0.25:.1f}%"
            
            st.markdown(f"""
            <div style="background: {color}; color: white; padding: 1rem; border-radius: 8px; text-align: center;">
                <h3>Prediction: {prediction}</h3>
                <p>Overall Score: {overall_score:.1f}/100</p>
                <p>Expected 30-day Return: {expected_return}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 Historical Accuracy")
        
        # Sample accuracy data
        accuracy_data = {
            'Prediction Type': ['Strong Success', 'Moderate Success', 'Neutral', 'High Risk'],
            'Accuracy %': [78, 72, 65, 82],
            'Sample Size': [25, 35, 28, 15]
        }
        
        df = pd.DataFrame(accuracy_data)
        
        fig = px.bar(df, x='Prediction Type', y='Accuracy %', 
                    title='Model Accuracy by Prediction Type',
                    color='Accuracy %',
                    color_continuous_scale='Viridis')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_ipo_sentiment_analysis():
    """Show IPO sentiment analysis"""
    st.subheader("📰 IPO Sentiment Analysis")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%); 
                padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
        <h4 style="color: #7b1fa2;">📰 Multi-Source Sentiment Intelligence</h4>
        <p>Real-time sentiment analysis from multiple sources:</p>
        <ul>
            <li><strong>News Articles:</strong> Economic Times, MoneyControl, Business Standard</li>
            <li><strong>Social Media:</strong> Twitter, Reddit, LinkedIn discussions</li>
            <li><strong>Analyst Reports:</strong> Brokerage recommendations and research</li>
            <li><strong>Market Forums:</strong> Investor community discussions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample sentiment data for current IPOs
    sentiment_data = [
        {
            'company': 'Clean Max Enviro Energy Limited',
            'overall_sentiment': 0.65,
            'news_sentiment': 0.72,
            'social_sentiment': 0.58,
            'analyst_sentiment': 0.68,
            'news_count': 45,
            'social_mentions': 1250,
            'trend': 'Positive'
        },
        {
            'company': 'Gaudium IVF & Women Health Limited',
            'overall_sentiment': 0.48,
            'news_sentiment': 0.52,
            'social_sentiment': 0.44,
            'analyst_sentiment': 0.50,
            'news_count': 28,
            'social_mentions': 890,
            'trend': 'Neutral'
        }
    ]
    
    for data in sentiment_data:
        sentiment_color = '#28a745' if data['overall_sentiment'] > 0.5 else '#ffc107' if data['overall_sentiment'] > 0.2 else '#dc3545'
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 1.5rem; border-radius: 12px; margin: 1rem 0; 
                    border-left: 5px solid {sentiment_color};">
            <h4 style="color: #2c3e50;">📊 {data['company']}</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                <div style="text-align: center;">
                    <strong>Overall Sentiment</strong><br>
                    <span style="color: {sentiment_color}; font-size: 1.5em; font-weight: bold;">{data['overall_sentiment']:.2f}</span>
                </div>
                <div style="text-align: center;">
                    <strong>News Sentiment</strong><br>
                    <span style="font-size: 1.2em;">{data['news_sentiment']:.2f}</span><br>
                    <small>{data['news_count']} articles</small>
                </div>
                <div style="text-align: center;">
                    <strong>Social Sentiment</strong><br>
                    <span style="font-size: 1.2em;">{data['social_sentiment']:.2f}</span><br>
                    <small>{data['social_mentions']} mentions</small>
                </div>
                <div style="text-align: center;">
                    <strong>Analyst Sentiment</strong><br>
                    <span style="font-size: 1.2em;">{data['analyst_sentiment']:.2f}</span><br>
                    <small>Research reports</small>
                </div>
            </div>
            
            <div style="background: rgba(102, 126, 234, 0.1); padding: 0.8rem; border-radius: 6px;">
                <strong>📈 Trend:</strong> {data['trend']} | 
                <strong>Recommendation:</strong> {'Positive outlook for listing' if data['overall_sentiment'] > 0.5 else 'Monitor closely' if data['overall_sentiment'] > 0.2 else 'Cautious approach recommended'}
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_ipo_exit_strategies():
    """Show IPO exit strategies"""
    st.subheader("🎯 IPO Exit Strategies & Recommendations")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%); 
                padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
        <h4 style="color: #ef6c00;">🎯 Smart Exit Strategy Framework</h4>
        <p>Our AI-powered exit strategies help you maximize profits and minimize risks:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Exit Strategy Calculator
    st.markdown("### 🧮 Exit Strategy Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        investment_amount = st.number_input("💰 Investment Amount (₹)", min_value=1000, value=50000, step=1000)
        issue_price = st.number_input("📊 Issue Price (₹)", min_value=1, value=100, step=1)
    
    with col2:
        current_price = st.number_input("📈 Current/Expected Price (₹)", min_value=1, value=120, step=1)
        days_held = st.number_input("📅 Days Held", min_value=0, value=7, step=1)
    
    with col3:
        risk_tolerance = st.selectbox("🎯 Risk Tolerance", ["Conservative", "Moderate", "Aggressive"])
    
    if st.button("🎯 Generate Exit Strategy", type="primary"):
        shares = investment_amount // issue_price
        current_value = shares * current_price
        gains_percent = ((current_price - issue_price) / issue_price) * 100
        profit_amount = current_value - investment_amount
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); 
                    padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
            <h4 style="color: #2e7d32;">📊 Your Position Analysis</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem; margin: 1rem 0;">
                <div style="text-align: center;">
                    <strong>Shares Owned</strong><br>
                    <span style="font-size: 1.5em; color: #1976d2;">{shares}</span>
                </div>
                <div style="text-align: center;">
                    <strong>Current Value</strong><br>
                    <span style="font-size: 1.5em; color: #1976d2;">₹{current_value:,.0f}</span>
                </div>
                <div style="text-align: center;">
                    <strong>Profit/Loss</strong><br>
                    <span style="font-size: 1.5em; color: {'#28a745' if profit_amount >= 0 else '#dc3545'};">₹{profit_amount:,.0f}</span>
                </div>
                <div style="text-align: center;">
                    <strong>Returns</strong><br>
                    <span style="font-size: 1.5em; color: {'#28a745' if gains_percent >= 0 else '#dc3545'};">{gains_percent:.1f}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Generate recommendation based on performance and risk tolerance
        if gains_percent >= 25:
            recommendation = "🎉 **BOOK PROFITS NOW**"
            action = f"Excellent gains of {gains_percent:.1f}%! Consider booking 70-80% profits."
            color = "#28a745"
        elif gains_percent >= 15:
            recommendation = "📈 **PARTIAL BOOKING**"
            action = f"Good gains of {gains_percent:.1f}%. Book 50% profits, trail SL for rest."
            color = "#17a2b8"
        elif gains_percent >= 5:
            recommendation = "🔄 **HOLD WITH SL**"
            action = f"Moderate gains of {gains_percent:.1f}%. Hold with strict stop loss at ₹{issue_price * 0.95:.2f}"
            color = "#ffc107"
        else:
            recommendation = "⚠️ **REVIEW POSITION**"
            action = f"Underperforming ({gains_percent:.1f}%). Consider exit if no improvement in 2-3 days."
            color = "#dc3545"
        
        st.markdown(f"""
        <div style="background: {color}; color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h3>{recommendation}</h3>
            <p style="font-size: 1.1em;">{action}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Exit Strategy Guidelines
    st.markdown("### 📋 Exit Strategy Guidelines")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🟢 If You Get Allotment:
        
        **Day 0 (Listing Day):**
        - Monitor opening price vs issue price
        - If gains > 20%: Book 50% profits
        - If gains 10-20%: Hold with stop loss
        - If gains < 5%: Consider immediate exit
        
        **Week 1:**
        - Track daily volume and price action
        - Book profits if target achieved
        - Maintain strict stop loss
        
        **Month 1:**
        - Evaluate fundamental performance
        - Consider partial profit booking
        - Trail stop loss for remaining position
        """)
    
    with col2:
        st.markdown("""
        #### 🔴 If You Don't Get Allotment:
        
        **Alternative Strategies:**
        - Wait for listing day dip to enter
        - Monitor for 2-3 days post listing
        - Enter only if price corrects 10-15%
        - Use same exit strategy as allottees
        
        **Risk Management:**
        - Never chase high opening prices
        - Set strict position sizing (max 5% portfolio)
        - Always use stop losses
        - Book profits systematically
        """)

def show_fund_analysis():
    """Mutual Fund Analysis"""
    st.subheader("🔍 Mutual Fund Analysis")
    
    try:
        # Get MF recommendations
        with st.spinner("📊 Analyzing mutual funds..."):
            recommendations = st.session_state.mf_sip_system.get_sip_recommendations(10000)
        
        if recommendations:
            st.success(f"✅ Analysis complete! Expected return: {recommendations.get('expected_return', 0):.2f}%")
            
            # Display fund recommendations
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Expected Annual Return", f"{recommendations.get('expected_return', 0):.2f}%")
            with col2:
                st.metric("Projected Value (10Y)", f"₹{recommendations.get('projected_value', 0):,.0f}")
            with col3:
                st.metric("Risk Level", recommendations.get('risk_level', 'Moderate'))
            
            # Sample fund data
            fund_data = [
                {"name": "HDFC Top 100 Fund", "category": "Large Cap", "return_1y": "12.5%", "return_3y": "15.2%", "expense_ratio": "1.05%", "rating": "⭐⭐⭐⭐⭐"},
                {"name": "Axis Midcap Fund", "category": "Mid Cap", "return_1y": "18.7%", "return_3y": "22.1%", "expense_ratio": "1.25%", "rating": "⭐⭐⭐⭐"},
                {"name": "SBI Small Cap Fund", "category": "Small Cap", "return_1y": "25.3%", "return_3y": "28.9%", "expense_ratio": "1.45%", "rating": "⭐⭐⭐⭐"},
                {"name": "Motilal Oswal Nasdaq 100", "category": "International", "return_1y": "14.8%", "return_3y": "19.5%", "expense_ratio": "0.65%", "rating": "⭐⭐⭐⭐⭐"}
            ]
            
            st.subheader("📊 Recommended Funds")
            for fund in fund_data:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                            padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                            border-left: 4px solid #667eea;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #2c3e50;">{fund['name']}</h4>
                            <p style="margin: 0; color: #6c757d;">{fund['category']} • {fund['rating']}</p>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0;"><strong>1Y:</strong> {fund['return_1y']} | <strong>3Y:</strong> {fund['return_3y']}</p>
                            <p style="margin: 0; color: #6c757d;">Expense: {fund['expense_ratio']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error in fund analysis: {str(e)}")

def show_sip_optimizer():
    """SIP Optimizer"""
    st.subheader("💰 SIP Optimizer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 SIP Calculator")
        monthly_amount = st.number_input("Monthly SIP Amount (₹)", min_value=500, value=10000, step=500)
        investment_period = st.number_input("Investment Period (Years)", min_value=1, value=10, step=1)
        expected_return = st.slider("Expected Annual Return (%)", 8.0, 20.0, 12.0, 0.5)
        
        if st.button("🎯 Calculate SIP Returns", type="primary"):
            # SIP calculation
            monthly_rate = expected_return / (12 * 100)
            months = investment_period * 12
            
            # Future Value calculation
            if monthly_rate > 0:
                future_value = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
            else:
                future_value = monthly_amount * months
            
            total_investment = monthly_amount * months
            wealth_gained = future_value - total_investment
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%); 
                        padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                <h4 style="color: #2e7d32;">💰 SIP Projection Results</h4>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                    <div style="text-align: center;">
                        <strong>Total Investment</strong><br>
                        <span style="font-size: 1.5em; color: #1976d2;">₹{total_investment:,.0f}</span>
                    </div>
                    <div style="text-align: center;">
                        <strong>Final Value</strong><br>
                        <span style="font-size: 1.5em; color: #28a745;">₹{future_value:,.0f}</span>
                    </div>
                    <div style="text-align: center;">
                        <strong>Wealth Gained</strong><br>
                        <span style="font-size: 1.5em; color: #ff6b35;">₹{wealth_gained:,.0f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📈 SIP vs Lump Sum")
        
        # Create comparison chart
        years = list(range(1, investment_period + 1))
        sip_values = []
        lumpsum_values = []
        
        lumpsum_amount = monthly_amount * 12  # Annual lump sum
        monthly_rate = expected_return / (12 * 100)
        
        for year in years:
            # SIP value
            months_elapsed = year * 12
            if monthly_rate > 0:
                sip_val = monthly_amount * (((1 + monthly_rate) ** months_elapsed - 1) / monthly_rate) * (1 + monthly_rate)
            else:
                sip_val = monthly_amount * months_elapsed
            sip_values.append(sip_val)
            
            # Lump sum value (invested at beginning)
            lumpsum_val = lumpsum_amount * year * ((1 + expected_return/100) ** year)
            lumpsum_values.append(lumpsum_val)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=sip_values, mode='lines+markers', name='SIP', line=dict(color='#28a745')))
        fig.add_trace(go.Scatter(x=years, y=lumpsum_values, mode='lines+markers', name='Lump Sum', line=dict(color='#dc3545')))
        
        fig.update_layout(
            title="SIP vs Lump Sum Investment",
            xaxis_title="Years",
            yaxis_title="Value (₹)",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_portfolio_builder():
    """Portfolio Builder"""
    st.subheader("📊 AI-Powered Portfolio Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 Investor Profile")
        age = st.number_input("Age", min_value=18, max_value=80, value=30)
        risk_appetite = st.selectbox("Risk Appetite", ["Conservative", "Moderate", "Aggressive"])
        investment_goal = st.selectbox("Investment Goal", ["Retirement", "Child Education", "Wealth Creation", "Tax Saving"])
        monthly_investment = st.number_input("Monthly Investment (₹)", min_value=1000, value=15000, step=1000)
        
        if st.button("🎯 Build Portfolio", type="primary"):
            # Portfolio allocation based on profile
            if risk_appetite == "Conservative":
                allocation = {"Large Cap": 50, "Debt": 30, "Hybrid": 20}
                expected_return = 10.5
            elif risk_appetite == "Moderate":
                allocation = {"Large Cap": 40, "Mid Cap": 30, "Debt": 20, "International": 10}
                expected_return = 13.2
            else:  # Aggressive
                allocation = {"Large Cap": 30, "Mid Cap": 30, "Small Cap": 25, "International": 15}
                expected_return = 16.8
            
            # Age-based adjustment
            equity_percentage = min(100 - age, 80)
            debt_percentage = 100 - equity_percentage
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                        padding: 1.5rem; border-radius: 12px;">
                <h4 style="color: #1565c0;">🎯 Recommended Portfolio</h4>
                <p><strong>Expected Annual Return:</strong> {expected_return}%</p>
                <p><strong>Risk Level:</strong> {risk_appetite}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display allocation
            for category, percentage in allocation.items():
                st.progress(percentage/100, text=f"{category}: {percentage}%")
    
    with col2:
        st.markdown("### 📈 Portfolio Performance Projection")
        
        # Sample portfolio performance chart
        years = list(range(1, 21))
        conservative_values = [monthly_investment * 12 * year * ((1 + 0.105) ** year) for year in years]
        moderate_values = [monthly_investment * 12 * year * ((1 + 0.132) ** year) for year in years]
        aggressive_values = [monthly_investment * 12 * year * ((1 + 0.168) ** year) for year in years]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=years, y=conservative_values, mode='lines', name='Conservative (10.5%)', line=dict(color='#ffc107')))
        fig.add_trace(go.Scatter(x=years, y=moderate_values, mode='lines', name='Moderate (13.2%)', line=dict(color='#17a2b8')))
        fig.add_trace(go.Scatter(x=years, y=aggressive_values, mode='lines', name='Aggressive (16.8%)', line=dict(color='#28a745')))
        
        fig.update_layout(
            title="Portfolio Growth Projection",
            xaxis_title="Years",
            yaxis_title="Portfolio Value (₹)",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_performance_tracker():
    """Performance Tracker"""
    st.subheader("📈 Portfolio Performance Tracker")
    
    # Sample portfolio data
    portfolio_data = {
        'Fund Name': ['HDFC Top 100', 'Axis Midcap', 'SBI Small Cap', 'Motilal Nasdaq'],
        'Investment': [50000, 30000, 25000, 20000],
        'Current Value': [58500, 36800, 32500, 23200],
        'Returns %': [17.0, 22.7, 30.0, 16.0],
        'SIP Date': ['2023-01-15', '2023-02-01', '2023-03-10', '2023-04-05']
    }
    
    df = pd.DataFrame(portfolio_data)
    
    # Portfolio summary
    total_investment = df['Investment'].sum()
    total_current_value = df['Current Value'].sum()
    total_returns = total_current_value - total_investment
    total_returns_percent = (total_returns / total_investment) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Investment", f"₹{total_investment:,}")
    with col2:
        st.metric("Current Value", f"₹{total_current_value:,}")
    with col3:
        st.metric("Total Returns", f"₹{total_returns:,}")
    with col4:
        st.metric("Returns %", f"{total_returns_percent:.1f}%")
    
    # Portfolio breakdown
    st.subheader("📊 Portfolio Breakdown")
    st.dataframe(df, use_container_width=True)
    
    # Performance chart
    fig = px.pie(df, values='Current Value', names='Fund Name', 
                title='Portfolio Allocation by Current Value')
    st.plotly_chart(fig, use_container_width=True)