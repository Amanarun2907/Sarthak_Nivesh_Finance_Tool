"""
Advanced Analytics Module - Real-time Data
Professional Market Intelligence with Live Data
AUTO-SAVES TO DATABASE
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import database manager for auto-save
try:
    from database_manager import SarthakNiveshDB
    DB_AVAILABLE = True
    db = SarthakNiveshDB()
except ImportError:
    DB_AVAILABLE = False
    db = None

def get_realtime_market_data():
    """Fetch real-time market data for Indian stocks"""
    try:
        # Top Indian stocks
        symbols = {
            'RELIANCE.NS': 'Reliance',
            'TCS.NS': 'TCS',
            'HDFCBANK.NS': 'HDFC Bank',
            'INFY.NS': 'Infosys',
            'ICICIBANK.NS': 'ICICI Bank',
            'HINDUNILVR.NS': 'HUL',
            'ITC.NS': 'ITC',
            'SBIN.NS': 'SBI',
            'BHARTIARTL.NS': 'Airtel',
            'KOTAKBANK.NS': 'Kotak Bank',
            'LT.NS': 'L&T',
            'AXISBANK.NS': 'Axis Bank',
            'WIPRO.NS': 'Wipro',
            'MARUTI.NS': 'Maruti',
            'TITAN.NS': 'Titan'
        }
        
        data = {}
        for symbol, name in symbols.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='5d')
                info = ticker.info
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change = current_price - prev_price
                    change_pct = (change / prev_price) * 100
                    volume = hist['Volume'].iloc[-1]
                    
                    data[name] = {
                        'symbol': symbol,
                        'price': current_price,
                        'change': change,
                        'change_pct': change_pct,
                        'volume': volume,
                        'market_cap': info.get('marketCap', 0),
                        'sector': info.get('sector', 'Unknown')
                    }
            except:
                continue
        
        return data
    except Exception as e:
        st.error(f"Error fetching market data: {str(e)}")
        return {}

def get_sector_performance():
    """Calculate real-time sector performance"""
    try:
        sector_stocks = {
            'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
            'IT': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS'],
            'Auto': ['MARUTI.NS', 'TATAMOTORS.NS', 'M&M.NS', 'BAJAJ-AUTO.NS'],
            'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS'],
            'FMCG': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS'],
            'Energy': ['RELIANCE.NS', 'ONGC.NS', 'BPCL.NS', 'IOC.NS'],
            'Telecom': ['BHARTIARTL.NS', 'IDEA.NS'],
            'Metals': ['TATASTEEL.NS', 'HINDALCO.NS', 'JSWSTEEL.NS']
        }
        
        sector_performance = {}
        
        for sector, stocks in sector_stocks.items():
            sector_changes = []
            for stock in stocks:
                try:
                    ticker = yf.Ticker(stock)
                    hist = ticker.history(period='2d')
                    if len(hist) >= 2:
                        change_pct = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                        sector_changes.append(change_pct)
                except:
                    continue
            
            if sector_changes:
                sector_performance[sector] = np.mean(sector_changes)
        
        return sector_performance
    except:
        return {}

def get_correlation_matrix(symbols, period='1mo'):
    """Calculate correlation matrix for stocks"""
    try:
        data = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if not hist.empty:
                data[symbol.replace('.NS', '')] = hist['Close']
        
        df = pd.DataFrame(data)
        correlation = df.corr()
        return correlation
    except:
        return pd.DataFrame()

def get_volume_analysis():
    """Get real-time volume analysis"""
    try:
        stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 
                  'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'HINDUNILVR.NS', 'KOTAKBANK.NS']
        
        volume_data = []
        
        for stock in stocks:
            try:
                ticker = yf.Ticker(stock)
                hist = ticker.history(period='5d')
                
                if len(hist) >= 2:
                    current_volume = hist['Volume'].iloc[-1]
                    avg_volume = hist['Volume'].mean()
                    volume_ratio = current_volume / avg_volume
                    
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    price_change = ((current_price - prev_price) / prev_price) * 100
                    
                    volume_data.append({
                        'Stock': stock.replace('.NS', ''),
                        'Volume': f"{current_volume/1e6:.2f}M",
                        'Avg Volume': f"{avg_volume/1e6:.2f}M",
                        'Volume Ratio': f"{volume_ratio:.2f}x",
                        'Price Change': f"{price_change:+.2f}%",
                        'Alert': 'High' if volume_ratio > 1.5 else 'Normal'
                    })
            except:
                continue
        
        return sorted(volume_data, key=lambda x: float(x['Volume Ratio'].replace('x', '')), reverse=True)[:10]
    except:
        return []

def show_advanced_analytics_realtime():
    """Advanced Analytics Page with Real-time Data"""
    
    st.header("📈 Advanced Market Analytics - Real-time")
    
    # Real-time status indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.success("🟢 Live Data | Updated: " + datetime.now().strftime("%H:%M:%S"))
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    with col3:
        auto_refresh = st.checkbox("Auto-refresh (30s)")
    
    if auto_refresh:
        st.markdown("""
        <meta http-equiv="refresh" content="30">
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tab structure for different analytics
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔥 Market Heat Map",
        "🔗 Correlation Analysis", 
        "📊 Volume Intelligence",
        "📈 Momentum Tracker",
        "🎯 Sector Rotation",
        "⚡ Market Breadth"
    ])
    
    # TAB 1: Market Heat Map
    with tab1:
        st.subheader("🔥 Real-time Sector Performance Heat Map")
        
        with st.spinner("Fetching real-time sector data..."):
            sector_performance = get_sector_performance()
            
            # AUTO-SAVE to database
            if sector_performance and DB_AVAILABLE:
                try:
                    db.insert_sector_performance(sector_performance)
                    st.success("✅ Data saved to database", icon="💾")
                except Exception as e:
                    st.warning(f"⚠️ Could not save to database: {str(e)}")
        
        if sector_performance:
            sectors = list(sector_performance.keys())
            performance = list(sector_performance.values())
            
            # Create heat map
            fig = go.Figure(data=go.Heatmap(
                z=[performance],
                x=sectors,
                y=['Today'],
                colorscale=[
                    [0, '#ff5252'],
                    [0.5, '#ffc107'],
                    [1, '#00ff88']
                ],
                text=[[f"{p:.2f}%" for p in performance]],
                texttemplate='%{text}',
                textfont={"size": 16, "color": "white"},
                colorbar=dict(title="Returns %")
            ))
            
            fig.update_layout(
                title="Sector Performance Heat Map (Real-time)",
                height=250,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(side='bottom')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sector insights
            best_sector = max(sector_performance, key=sector_performance.get)
            worst_sector = min(sector_performance, key=sector_performance.get)
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🚀 Best Performer: **{best_sector}** ({sector_performance[best_sector]:+.2f}%)")
            with col2:
                st.error(f"📉 Worst Performer: **{worst_sector}** ({sector_performance[worst_sector]:+.2f}%)")
        else:
            st.warning("Unable to fetch sector data. Please try again.")
    
    # TAB 2: Correlation Analysis
    with tab2:
        st.subheader("🔗 Stock Correlation Matrix - Real-time")
        
        period = st.selectbox("Analysis Period", ["1mo", "3mo", "6mo", "1y"], index=1)
        
        with st.spinner("Calculating correlations..."):
            symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS', 
                      'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS']
            correlation = get_correlation_matrix(symbols, period)
        
        if not correlation.empty:
            fig = go.Figure(data=go.Heatmap(
                z=correlation.values,
                x=correlation.columns,
                y=correlation.columns,
                colorscale='RdBu',
                zmid=0,
                text=correlation.values,
                texttemplate='%{text:.2f}',
                textfont={"size": 10},
                colorbar=dict(title="Correlation")
            ))
            
            fig.update_layout(
                title=f"Stock Correlation Matrix ({period})",
                height=600,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.info("💡 **Insight:** Correlation ranges from -1 (inverse) to +1 (perfect correlation). Use this to diversify your portfolio.")
        else:
            st.warning("Unable to calculate correlations. Please try again.")
    
    # TAB 3: Volume Intelligence
    with tab3:
        st.subheader("📊 Volume Intelligence - Unusual Activity Detection")
        
        with st.spinner("Analyzing volume patterns..."):
            volume_data = get_volume_analysis()
            
            # AUTO-SAVE to database
            if volume_data and DB_AVAILABLE:
                try:
                    db.insert_volume_analysis(volume_data)
                    st.success("✅ Volume data saved to database", icon="💾")
                except Exception as e:
                    st.warning(f"⚠️ Could not save volume data: {str(e)}")
        
        if volume_data:
            df = pd.DataFrame(volume_data)
            
            # Display table with color coding
            st.dataframe(
                df.style.map(
                    lambda x: 'background-color: #ff5252' if x == 'High' else '',
                    subset=['Alert']
                ),
                use_container_width=True,
                height=400
            )
            
            # Volume chart
            stocks = [d['Stock'] for d in volume_data[:5]]
            volumes = [float(d['Volume'].replace('M', '')) for d in volume_data[:5]]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=stocks,
                    y=volumes,
                    marker_color=['#ff5252' if d['Alert'] == 'High' else '#00d4ff' for d in volume_data[:5]],
                    text=[f"{v:.2f}M" for v in volumes],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title="Top 5 Stocks by Volume",
                xaxis_title="Stock",
                yaxis_title="Volume (Millions)",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            high_volume_count = sum(1 for d in volume_data if d['Alert'] == 'High')
            st.warning(f"⚠️ **{high_volume_count}** stocks showing unusual volume activity!")
        else:
            st.warning("Unable to fetch volume data. Please try again.")
    
    # TAB 4: Momentum Tracker
    with tab4:
        st.subheader("📈 Momentum Tracker - Real-time Price Action")
        
        with st.spinner("Fetching momentum data..."):
            market_data = get_realtime_market_data()
            
            # AUTO-SAVE to database
            if market_data and DB_AVAILABLE:
                try:
                    db.insert_stock_data(market_data)
                    st.success("✅ Stock data saved to database", icon="💾")
                except Exception as e:
                    st.warning(f"⚠️ Could not save stock data: {str(e)}")
        
        if market_data:
            # Sort by change percentage
            sorted_stocks = sorted(market_data.items(), key=lambda x: x[1]['change_pct'], reverse=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🚀 Top Gainers")
                for name, data in sorted_stocks[:5]:
                    html = f"""
                    <div style='background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 212, 255, 0.2) 100%);
                                padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 5px solid #00ff88;'>
                        <strong style='font-size: 1.1rem;'>{name}</strong><br>
                        <span style='font-size: 1.3rem; color: #00ff88;'>₹{data['price']:.2f}</span>
                        <span style='color: #00ff88; margin-left: 1rem;'>+{data['change_pct']:.2f}%</span>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📉 Top Losers")
                for name, data in sorted_stocks[-5:]:
                    html = f"""
                    <div style='background: linear-gradient(135deg, rgba(255, 82, 82, 0.2) 0%, rgba(255, 165, 0, 0.2) 100%);
                                padding: 1rem; border-radius: 10px; margin: 0.5rem 0; border-left: 5px solid #ff5252;'>
                        <strong style='font-size: 1.1rem;'>{name}</strong><br>
                        <span style='font-size: 1.3rem; color: #ff5252;'>₹{data['price']:.2f}</span>
                        <span style='color: #ff5252; margin-left: 1rem;'>{data['change_pct']:.2f}%</span>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
            
            # Momentum chart
            names = [name for name, _ in sorted_stocks]
            changes = [data['change_pct'] for _, data in sorted_stocks]
            colors = ['#00ff88' if c > 0 else '#ff5252' for c in changes]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=names,
                    y=changes,
                    marker_color=colors,
                    text=[f"{c:+.2f}%" for c in changes],
                    textposition='outside'
                )
            ])
            
            fig.update_layout(
                title="Market Momentum - All Stocks",
                xaxis_title="Stock",
                yaxis_title="Change %",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Unable to fetch market data. Please try again.")
    
    # TAB 5: Sector Rotation
    with tab5:
        st.subheader("🎯 Sector Rotation Analysis")
        
        with st.spinner("Analyzing sector rotation..."):
            sector_performance = get_sector_performance()
        
        if sector_performance:
            # Sector rotation chart
            sectors = list(sector_performance.keys())
            performance = list(sector_performance.values())
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=performance,
                theta=sectors,
                fill='toself',
                name='Today',
                line_color='#00d4ff',
                fillcolor='rgba(0, 212, 255, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[-3, 3]
                    )
                ),
                title="Sector Rotation Radar",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sector recommendations
            st.markdown("### 💡 Sector Insights")
            
            strong_sectors = [s for s, p in sector_performance.items() if p > 1]
            weak_sectors = [s for s, p in sector_performance.items() if p < -1]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if strong_sectors:
                    st.success("**🟢 Strong Sectors (Outperforming)**")
                    for sector in strong_sectors:
                        st.write(f"• {sector}: {sector_performance[sector]:+.2f}%")
                else:
                    st.info("No sectors showing strong outperformance")
            
            with col2:
                if weak_sectors:
                    st.error("**🔴 Weak Sectors (Underperforming)**")
                    for sector in weak_sectors:
                        st.write(f"• {sector}: {sector_performance[sector]:+.2f}%")
                else:
                    st.info("No sectors showing significant weakness")
        else:
            st.warning("Unable to fetch sector data. Please try again.")
    
    # TAB 6: Market Breadth
    with tab6:
        st.subheader("⚡ Market Breadth Analysis")
        
        with st.spinner("Calculating market breadth..."):
            market_data = get_realtime_market_data()
        
        if market_data:
            # Calculate breadth metrics
            total_stocks = len(market_data)
            advancing = sum(1 for data in market_data.values() if data['change_pct'] > 0)
            declining = sum(1 for data in market_data.values() if data['change_pct'] < 0)
            unchanged = total_stocks - advancing - declining
            
            advance_decline_ratio = advancing / declining if declining > 0 else advancing
            breadth_strength = (advancing / total_stocks) * 100
            sentiment = 'Bullish' if advance_decline_ratio > 1.5 else 'Bearish' if advance_decline_ratio < 0.67 else 'Neutral'
            
            # AUTO-SAVE to database
            if DB_AVAILABLE:
                try:
                    breadth_data = {
                        'total': total_stocks,
                        'advancing': advancing,
                        'declining': declining,
                        'unchanged': unchanged,
                        'ad_ratio': advance_decline_ratio,
                        'sentiment': sentiment,
                        'strength': breadth_strength
                    }
                    db.insert_market_breadth(breadth_data)
                    st.success("✅ Market breadth saved to database", icon="💾")
                except Exception as e:
                    st.warning(f"⚠️ Could not save market breadth: {str(e)}")
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Advancing", advancing, f"{(advancing/total_stocks)*100:.1f}%")
            
            with col2:
                st.metric("Declining", declining, f"{(declining/total_stocks)*100:.1f}%")
            
            with col3:
                st.metric("Unchanged", unchanged)
            
            with col4:
                st.metric("A/D Ratio", f"{advance_decline_ratio:.2f}")
            
            # Breadth visualization
            fig = go.Figure(data=[
                go.Pie(
                    labels=['Advancing', 'Declining', 'Unchanged'],
                    values=[advancing, declining, unchanged],
                    marker=dict(colors=['#00ff88', '#ff5252', '#ffc107']),
                    hole=0.4,
                    textinfo='label+percent',
                    textfont=dict(size=14)
                )
            ])
            
            fig.update_layout(
                title="Market Breadth Distribution",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Market sentiment
            if advance_decline_ratio > 1.5:
                st.success("🟢 **Market Sentiment: BULLISH** - Strong buying pressure across the market")
            elif advance_decline_ratio < 0.67:
                st.error("🔴 **Market Sentiment: BEARISH** - Widespread selling pressure")
            else:
                st.warning("🟡 **Market Sentiment: NEUTRAL** - Mixed market conditions")
            
            # Breadth strength gauge (already calculated above)
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=breadth_strength,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Market Breadth Strength", 'font': {'size': 24}},
                delta={'reference': 50, 'increasing': {'color': "#00ff88"}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "#00d4ff"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 2,
                    'bordercolor': "white",
                    'steps': [
                        {'range': [0, 33], 'color': 'rgba(255, 82, 82, 0.3)'},
                        {'range': [33, 67], 'color': 'rgba(255, 193, 7, 0.3)'},
                        {'range': [67, 100], 'color': 'rgba(0, 255, 136, 0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': "white", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                font={'color': "white", 'family': "Arial"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Unable to fetch market data. Please try again.")

if __name__ == "__main__":
    st.set_page_config(page_title="Advanced Analytics", layout="wide")
    show_advanced_analytics_realtime()
