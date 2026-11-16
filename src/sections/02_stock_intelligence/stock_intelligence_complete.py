# COMPLETE STOCK INTELLIGENCE FUNCTION - COPY THIS TO REPLACE OLD ONE
# Replace lines 2228-2426 in main_ultimate_final.py with this entire function

def show_stock_intelligence():
    st.header("📊 Real-time Stock Intelligence - 50+ Stocks")
    
    # Create tabs for different analysis views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Technical Analysis", 
        "📊 Fundamental Data", 
        "📰 News & Sentiment",
        "🔮 Price Prediction",
        "⚖️ Compare Stocks"
    ])
    
    # Stock Selection (common for all tabs)
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_stock = st.selectbox(
            "Select Stock for Deep Analysis",
            list(INDIAN_STOCKS.keys()),
            format_func=lambda x: f"{INDIAN_STOCKS[x]} ({x.replace('.NS', '')})"
        )
    
    with col2:
        period = st.selectbox("Analysis Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])
    
    with col3:
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.success("✅ Refreshed!")
    
    # Fetch and display data
    data = get_stock_data(selected_stock, period)
    
    if not data.empty:
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price) * 100
        
        # Get real-time stock info
        ticker = yf.Ticker(selected_stock)
        info = ticker.info

        
        # Key Metrics Dashboard (Enhanced with real data) - OUTSIDE TABS
        st.markdown("### 📊 Live Market Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("Current Price", f"₹{current_price:.2f}", f"{change_pct:+.2f}%")
        with col2:
            high_52w = info.get('fiftyTwoWeekHigh', data['High'].max())
            st.metric("52W High", f"₹{high_52w:.2f}")
        with col3:
            low_52w = info.get('fiftyTwoWeekLow', data['Low'].min())
            st.metric("52W Low", f"₹{low_52w:.2f}")
        with col4:
            market_cap = info.get('marketCap', 0) / 1e9
            st.metric("Market Cap", f"₹{market_cap:.2f}B" if market_cap > 0 else "N/A")
        with col5:
            pe_ratio = info.get('trailingPE', 0)
            st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
        with col6:
            div_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            st.metric("Div Yield", f"{div_yield:.2f}%")
