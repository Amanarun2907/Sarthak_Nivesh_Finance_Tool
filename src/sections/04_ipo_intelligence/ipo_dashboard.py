#!/usr/bin/env python3
"""
REAL-TIME IPO INTELLIGENCE DASHBOARD
Interactive Dashboard for Currently Open IPOs and Exit Strategies
Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3

from config import *
from realtime_ipo_intelligence import RealTimeIPOIntelligence

# Page configuration
st.set_page_config(
    page_title="🚀 Real-Time IPO Intelligence | सार्थक निवेश",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for IPO Dashboard
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .ipo-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .strong-buy {
        border-left-color: #28a745 !important;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }
    
    .buy {
        border-left-color: #17a2b8 !important;
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
    }
    
    .neutral {
        border-left-color: #ffc107 !important;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    }
    
    .avoid {
        border-left-color: #dc3545 !important;
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        border-top: 3px solid #667eea;
    }
    
    .exit-strategy {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff6b6b;
    }
    
    .gmp-positive {
        color: #28a745;
        font-weight: 600;
    }
    
    .gmp-negative {
        color: #dc3545;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Real-Time IPO Intelligence Dashboard</h1>
        <h3>सार्थक निवेश - Currently Open IPOs & Exit Strategies</h3>
        <p>✨ Live Analysis • Grey Market Premium • AI-Powered Recommendations ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize IPO Intelligence System
    if 'ipo_intel' not in st.session_state:
        with st.spinner("🚀 Initializing Real-Time IPO Intelligence..."):
            st.session_state.ipo_intel = RealTimeIPOIntelligence()
    
    # Sidebar
    st.sidebar.markdown("### 🎯 IPO Intelligence Controls")
    
    # Auto-refresh option
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (30s)", value=False)
    if auto_refresh:
        st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh IPO Data", type="primary"):
        st.session_state.ipo_intel.analyze_all_open_ipos()
        st.success("✅ IPO data refreshed!")
        st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 Currently Open IPOs", 
        "📊 Post-Listing Tracker", 
        "📈 Market Analysis", 
        "🎯 Exit Strategies"
    ])
    
    with tab1:
        show_open_ipos()
    
    with tab2:
        show_post_listing_tracker()
    
    with tab3:
        show_market_analysis()
    
    with tab4:
        show_exit_strategies()

def show_open_ipos():
    """Display currently open IPOs with recommendations"""
    st.header("🚀 Currently Open IPOs - Live Analysis")
    
    # Get fresh data
    with st.spinner("📊 Analyzing current IPOs..."):
        results = st.session_state.ipo_intel.analyze_all_open_ipos()
    
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
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #28a745;">🎯 {strong_buy_count}</h3>
            <p>Strong Buy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #17a2b8;">📈 {buy_count}</h3>
            <p>Buy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ffc107;">⚖️ {neutral_count}</h3>
            <p>Neutral</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #dc3545;">⚠️ {avoid_count}</h3>
            <p>Avoid</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display each IPO
    for result in results:
        recommendation_class = result['recommendation'].lower().replace(' ', '-')
        
        st.markdown(f"""
        <div class="ipo-card {recommendation_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3>🏢 {result['company']}</h3>
                    <p><strong>Symbol:</strong> {result['symbol']} | <strong>Price Range:</strong> {result['price_range']} | <strong>Size:</strong> {result['size']}</p>
                </div>
                <div style="text-align: right;">
                    <h2 style="margin: 0; color: {'#28a745' if result['recommendation'] == 'STRONG BUY' else '#17a2b8' if result['recommendation'] == 'BUY' else '#ffc107' if result['recommendation'] == 'NEUTRAL' else '#dc3545'};">
                        {result['recommendation']}
                    </h2>
                    <p style="margin: 0; font-size: 0.9em;">Confidence: {result['confidence']}</p>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                <div>
                    <strong>🎯 Target Price:</strong><br>
                    <span style="color: #28a745; font-size: 1.2em; font-weight: 600;">{result['target']}</span>
                </div>
                <div>
                    <strong>🛑 Stop Loss:</strong><br>
                    <span style="color: #dc3545; font-size: 1.2em; font-weight: 600;">{result['stop_loss']}</span>
                </div>
                <div>
                    <strong>📊 Grey Market Premium:</strong><br>
                    <span class="{'gmp-positive' if float(result['gmp'].replace('%', '')) > 0 else 'gmp-negative'}">{result['gmp']}</span>
                </div>
            </div>
            
            <div class="exit-strategy" style="margin-top: 1rem;">
                <strong>🚪 Exit Strategy:</strong><br>
                {result['exit_strategy']}
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_post_listing_tracker():
    """Show post-listing performance tracking"""
    st.header("📊 Post-Listing Performance Tracker")
    
    # Sample post-listing data (in real implementation, this would come from database)
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
            'recommendation': 'STRONG HOLD'
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
            'recommendation': 'HOLD'
        }
    ]
    
    if sample_data:
        for data in sample_data:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="ipo-card">
                    <h3>🏢 {data['company']} ({data['symbol']})</h3>
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
                            <span style="color: #17a2b8; font-weight: 600;">{data['recommendation']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Create a simple performance chart
                days = list(range(0, data['days_since_listing'] + 1, 10))
                # Simulate price movement (in real implementation, use actual data)
                prices = [data['issue_price'] * (1 + (data['current_gains']/100) * (d/data['days_since_listing'])) for d in days]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=days, y=prices, mode='lines+markers', name='Price'))
                fig.add_hline(y=data['issue_price'], line_dash="dash", line_color="red", annotation_text="Issue Price")
                fig.update_layout(
                    title=f"{data['symbol']} Performance",
                    xaxis_title="Days Since Listing",
                    yaxis_title="Price (₹)",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 No post-listing data available. Data will appear after IPOs get listed.")

def show_market_analysis():
    """Show market analysis and trends"""
    st.header("📈 IPO Market Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Sector-wise IPO Performance")
        
        # Sample sector data
        sector_data = {
            'Sector': ['Healthcare', 'Renewable Energy', 'Technology', 'Textiles', 'Gas Distribution', 'Jewellery'],
            'Avg_Returns': [25.5, 35.2, 28.7, 12.3, 18.9, 15.6],
            'Success_Rate': [78, 85, 82, 65, 70, 68]
        }
        
        df = pd.DataFrame(sector_data)
        
        fig = px.bar(df, x='Sector', y='Avg_Returns', 
                    title='Average IPO Returns by Sector (%)',
                    color='Avg_Returns',
                    color_continuous_scale='Viridis')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 IPO Success Rate Trends")
        
        fig = px.scatter(df, x='Success_Rate', y='Avg_Returns', 
                        size='Avg_Returns', color='Sector',
                        title='Success Rate vs Average Returns',
                        labels={'Success_Rate': 'Success Rate (%)', 'Avg_Returns': 'Average Returns (%)'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Market insights
    st.subheader("🧠 Market Insights")
    
    insights = [
        "🚀 Renewable Energy sector showing strongest performance with 35.2% average returns",
        "💡 Technology IPOs maintain consistent 82% success rate",
        "⚠️ Textile sector underperforming with only 12.3% average returns",
        "📈 Healthcare sector emerging as investor favorite with 78% success rate",
        "🎯 Current market favors ESG-focused companies and tech innovations"
    ]
    
    for insight in insights:
        st.info(insight)

def show_exit_strategies():
    """Show detailed exit strategies and recommendations"""
    st.header("🎯 Personalized Exit Strategies")
    
    st.markdown("""
    ### 📋 How to Use Exit Strategies:
    
    **For Currently Open IPOs:**
    1. 🎯 **Apply for IPO** based on our recommendation
    2. 📊 **Monitor Grey Market Premium** for early indicators
    3. 🚀 **Follow listing day strategy** based on opening price
    4. 📈 **Execute exit plan** according to our timeline
    
    **Post-Allotment Action Plan:**
    """)
    
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
    
    # Interactive exit strategy calculator
    st.markdown("---")
    st.subheader("🧮 Exit Strategy Calculator")
    
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
        ### 📊 Your Position Analysis:
        
        **Investment Details:**
        - Shares Owned: {shares}
        - Current Value: ₹{current_value:,.2f}
        - Profit/Loss: ₹{profit_amount:,.2f} ({gains_percent:.1f}%)
        
        **Recommended Action:**
        """)
        
        if gains_percent >= 25:
            st.success(f"🎉 **BOOK PROFITS NOW**: Excellent gains of {gains_percent:.1f}%! Consider booking 70-80% profits.")
        elif gains_percent >= 15:
            st.info(f"📈 **PARTIAL BOOKING**: Good gains of {gains_percent:.1f}%. Book 50% profits, trail SL for rest.")
        elif gains_percent >= 5:
            st.warning(f"🔄 **HOLD WITH SL**: Moderate gains of {gains_percent:.1f}%. Hold with strict stop loss at ₹{issue_price * 0.95:.2f}")
        else:
            st.error(f"⚠️ **REVIEW POSITION**: Underperforming ({gains_percent:.1f}%). Consider exit if no improvement in 2-3 days.")

if __name__ == "__main__":
    main()