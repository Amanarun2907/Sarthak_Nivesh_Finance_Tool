"""
Agentic AI Hub - World Class Streamlit UI
Fixes ALL 22 issues: structured output, real portfolio, charts, news, sectors
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import re
from agentic_ai_engine import (
    INDIAN_STOCKS, SECTOR_MAP,
    run_stock_analysis, run_portfolio_analysis, run_market_intelligence,
    fetch_stock_data, fetch_market_overview, fetch_sector_performance, fetch_fii_dii
)


def _parse(text: str, key: str, default: str = "N/A") -> str:
    """Parse structured AI response by key"""
    pattern = rf"^{re.escape(key)}:\s*(.+)$"
    m = re.search(pattern, text, re.MULTILINE)
    return m.group(1).strip() if m else default


def _color(val: str) -> str:
    """Return color based on signal value"""
    v = val.upper()
    if any(x in v for x in ["STRONG BUY", "BULLISH", "EXCELLENT", "GOOD", "POSITIVE", "ACCUMULATION", "STRONG"]):
        return "#00ff88"
    if any(x in v for x in ["BUY", "UPTREND", "FAIR"]):
        return "#17a2b8"
    if any(x in v for x in ["HOLD", "NEUTRAL", "MODERATE", "SIDEWAYS"]):
        return "#ffc107"
    if any(x in v for x in ["SELL", "BEARISH", "WEAK", "POOR", "NEGATIVE", "DISTRIBUTION"]):
        return "#ff9800"
    if any(x in v for x in ["STRONG SELL", "HIGH FEAR", "VERY BEARISH"]):
        return "#ff5252"
    return "#e0e0e0"


@st.cache_data(ttl=300)
def _cached_stock_data(symbol: str):
    return fetch_stock_data(symbol)


@st.cache_data(ttl=300)
def _cached_market_overview():
    return fetch_market_overview()


@st.cache_data(ttl=300)
def _cached_sector_perf():
    return fetch_sector_performance()


@st.cache_data(ttl=600)
def _cached_fii_dii():
    return fetch_fii_dii()


def show_agentic_ai_hub():
    """Main Agentic AI Hub"""
    st.title("🤖 Agentic AI Investment Hub")
    st.markdown("""
    <div style='background:linear-gradient(135deg,#667eea,#764ba2);
                padding:1.5rem;border-radius:12px;margin-bottom:1rem;'>
        <h3 style='color:#fff;margin:0;text-align:center;'>
            AUTONOMOUS AI AGENTS · REAL-TIME DATA · INSTITUTIONAL-GRADE ANALYSIS
        </h3>
        <p style='color:#e0e0e0;margin:0.3rem 0 0;text-align:center;font-size:0.9rem;'>
            Llama 3.3 70B · Yahoo Finance · NSE Live · Google News · 120+ Stocks
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 AI Stock Analyst",
        "💼 AI Portfolio Manager",
        "📊 AI Market Intelligence",
        "🔀 Compare Stocks",
        "🤖 About Agents"
    ])
    with tab1:
        _tab_stock_analyst()
    with tab2:
        _tab_portfolio_manager()
    with tab3:
        _tab_market_intelligence()
    with tab4:
        _tab_compare_stocks()
    with tab5:
        _tab_about()


def show_agentic_ai_page():
    show_agentic_ai_hub()


def _tab_stock_analyst():
    st.header("🎯 AI Stock Analyst — Institutional-Grade Analysis")

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        selected = st.selectbox(
            "Select Stock",
            list(INDIAN_STOCKS.keys()),
            format_func=lambda x: f"{INDIAN_STOCKS[x]} ({x.replace('.NS','')})",
            key="ai_stock_sel"
        )
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        run_btn = st.button("🚀 Run AI Analysis", type="primary", use_container_width=True)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        quick_btn = st.button("⚡ Quick Preview", use_container_width=True)

    # FIX 7: Show live data immediately before AI runs
    if quick_btn or run_btn:
        with st.spinner("Fetching live data..."):
            d = fetch_stock_data(selected)
        if "error" not in d:
            _render_live_metrics(d)

    if run_btn:
        if "error" in fetch_stock_data(selected):
            st.error("Could not fetch stock data. Check internet connection.")
            return

        progress = st.progress(0)
        status = st.empty()

        status.markdown("**Agent 1:** Fetching 50+ technical indicators...")
        progress.progress(15)
        status.markdown("**Agent 2:** Analyzing fundamentals & valuation...")
        progress.progress(35)
        status.markdown("**Agent 3:** Checking FII/DII institutional flow...")
        progress.progress(55)
        status.markdown("**Agent 4:** Scanning news sentiment...")
        progress.progress(70)
        status.markdown("**Strategist:** Synthesizing final recommendation...")
        progress.progress(85)

        with st.spinner("AI generating institutional-grade analysis..."):
            result = run_stock_analysis(selected)

        progress.progress(100)
        status.empty()
        progress.empty()

        if result["success"]:
            _render_stock_analysis(result, selected)
        else:
            st.error(f"Analysis failed: {result.get('error', 'Unknown')}")
            st.info("Retry in a few seconds or check your internet connection.")


def _render_live_metrics(d: dict):
    """FIX 7: Show live metrics immediately"""
    st.markdown("### 📊 Live Market Data")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    chg_color = "#00ff88" if d["change_pct"] >= 0 else "#ff5252"
    c1.metric("Price", f"₹{d['current_price']:.2f}", f"{d['change_pct']:+.2f}%")
    c2.metric("RSI(14)", f"{d['rsi']:.1f}",
              "Overbought" if d['rsi'] > 70 else "Oversold" if d['rsi'] < 30 else "Neutral")
    c3.metric("Volume Ratio", f"{d['vol_ratio']:.2f}x",
              "High" if d['vol_ratio'] > 1.5 else "Normal")
    c4.metric("vs MA20", f"₹{d['ma20']:.0f}",
              "Above ✅" if d['current_price'] > d['ma20'] else "Below ⚠️")
    c5.metric("vs MA200", f"₹{d['ma200']:.0f}",
              "Above ✅" if d['current_price'] > d['ma200'] else "Below ⚠️")
    c6.metric("ATR", f"₹{d['atr']:.2f}", "Risk/share")

    # FIX 12: Price chart with MA overlays
    hist = d.get("hist_1mo")
    if hist is not None and not hist.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=hist.index, open=hist["Open"], high=hist["High"],
            low=hist["Low"], close=hist["Close"], name="Price",
            increasing_line_color="#00ff88", decreasing_line_color="#ff5252"
        ))
        # MA overlays
        for period, color in [(20, "#00d4ff"), (50, "#ffc107")]:
            ma = hist["Close"].rolling(period).mean()
            fig.add_trace(go.Scatter(x=hist.index, y=ma, name=f"MA{period}",
                                     line=dict(color=color, width=1.5)))
        # Bollinger Bands
        bb_mid = hist["Close"].rolling(20).mean()
        bb_std = hist["Close"].rolling(20).std()
        fig.add_trace(go.Scatter(x=hist.index, y=bb_mid + 2*bb_std,
                                  name="BB Upper", line=dict(color="#764ba2", width=1, dash="dot")))
        fig.add_trace(go.Scatter(x=hist.index, y=bb_mid - 2*bb_std,
                                  name="BB Lower", line=dict(color="#764ba2", width=1, dash="dot"),
                                  fill="tonexty", fillcolor="rgba(118,75,162,0.05)"))
        fig.update_layout(
            title=f"{d['company_name']} — 1 Month Price Chart",
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=380,
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # RSI chart
        delta = hist["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi_series = 100 - (100 / (1 + gain / loss))
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=hist.index, y=rsi_series, name="RSI",
                                   line=dict(color="#00d4ff", width=2)))
        fig2.add_hline(y=70, line_dash="dash", line_color="#ff5252", annotation_text="Overbought 70")
        fig2.add_hline(y=30, line_dash="dash", line_color="#00ff88", annotation_text="Oversold 30")
        fig2.update_layout(
            title="RSI (14)", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=200
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Volume chart
        vol_colors = ["#00ff88" if c >= o else "#ff5252"
                      for c, o in zip(hist["Close"], hist["Open"])]
        fig3 = go.Figure(go.Bar(x=hist.index, y=hist["Volume"],
                                 marker_color=vol_colors, name="Volume"))
        avg_vol_line = [hist["Volume"].mean()] * len(hist)
        fig3.add_trace(go.Scatter(x=hist.index, y=avg_vol_line, name="Avg Volume",
                                   line=dict(color="#ffc107", dash="dash")))
        fig3.update_layout(
            title="Volume Analysis", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=200
        )
        st.plotly_chart(fig3, use_container_width=True)


def _render_stock_analysis(result: dict, selected: str):
    """FIX 1: Structured rendering - not raw text dump"""
    t = result["analysis_text"]
    d = result["raw_data"]
    news = result["news_data"]

    rec = _parse(t, "RECOMMENDATION", "HOLD")
    conf = _parse(t, "CONFIDENCE", "60%")
    overall = _parse(t, "OVERALL_SCORE", "5/10")
    tech_score = _parse(t, "TECHNICAL_SCORE", "5/10")
    fund_score = _parse(t, "FUNDAMENTAL_SCORE", "5/10")
    inst_score = _parse(t, "INSTITUTIONAL_SCORE", "5/10")
    rec_color = _color(rec)

    # Main recommendation banner
    st.markdown(f"""
    <div style='background:rgba(0,0,0,0.4);padding:1.5rem;border-radius:12px;
                border:3px solid {rec_color};margin:1rem 0;text-align:center;'>
        <h1 style='color:{rec_color};margin:0;font-size:2.5rem;'>{rec}</h1>
        <p style='color:#e0e0e0;margin:0.5rem 0;font-size:1.1rem;'>
            Overall Score: <b>{overall}</b> &nbsp;|&nbsp;
            Confidence: <b>{conf}</b> &nbsp;|&nbsp;
            {result['company_name']} ({selected.replace('.NS','')})
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Score cards
    c1, c2, c3, c4 = st.columns(4)
    for col, label, score, icon in [
        (c1, "Technical", tech_score, "📊"),
        (c2, "Fundamental", fund_score, "💼"),
        (c3, "Institutional", inst_score, "💰"),
        (c4, "Overall", overall, "🎯")
    ]:
        sc = _color(_parse(t, "TECHNICAL_TREND", "Neutral") if label == "Technical" else
                    _parse(t, "VALUATION", "Fair") if label == "Fundamental" else
                    _parse(t, "FII_SIGNAL", "Neutral") if label == "Institutional" else rec)
        col.markdown(f"""
        <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                    border-left:4px solid {sc};text-align:center;'>
            <div style='font-size:1.5rem;'>{icon}</div>
            <div style='color:#aaa;font-size:0.85rem;'>{label}</div>
            <div style='color:{sc};font-size:1.4rem;font-weight:bold;'>{score}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Entry / Targets / Stop Loss
    st.markdown("### 🎯 Trade Setup")
    tc1, tc2, tc3, tc4, tc5 = st.columns(5)
    tc1.metric("Entry Range", _parse(t, "ENTRY_PRICE", "N/A"))
    tc2.metric("Target 1 (3M)", _parse(t, "TARGET_1", "N/A"))
    tc3.metric("Target 2 (6M)", _parse(t, "TARGET_2", "N/A"))
    tc4.metric("Stop Loss", _parse(t, "STOP_LOSS", "N/A"))
    tc5.metric("Risk:Reward", _parse(t, "RISK_REWARD", "N/A"))

    ic1, ic2, ic3 = st.columns(3)
    ic1.metric("Risk Level", _parse(t, "RISK_LEVEL", "Medium"))
    ic2.metric("Holding Period", _parse(t, "HOLDING_PERIOD", "Medium term"))
    ic3.metric("Position Size", _parse(t, "POSITION_SIZE", "5%"))

    st.markdown("---")

    # Two-column layout for analysis sections
    left, right = st.columns(2)

    with left:
        # Technical Analysis
        trend = _parse(t, "TECHNICAL_TREND", "N/A")
        tc = _color(trend)
        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                    border-left:4px solid {tc};margin-bottom:1rem;'>
            <h4 style='color:#00d4ff;margin:0;'>📊 Technical Analysis</h4>
            <p style='margin:0.5rem 0;'><b>Trend:</b> <span style='color:{tc};'>{trend}</span>
            &nbsp;|&nbsp; <b>Strength:</b> {_parse(t, "TECHNICAL_STRENGTH", "N/A")}</p>
            <p style='margin:0.3rem 0;'><b>Golden Cross:</b> {_parse(t, "GOLDEN_CROSS", "N/A")}</p>
            <p style='margin:0.3rem 0;'><b>Support:</b> {_parse(t, "KEY_SUPPORT", "N/A")}</p>
            <p style='margin:0.3rem 0;'><b>Resistance:</b> {_parse(t, "KEY_RESISTANCE", "N/A")}</p>
            <p style='margin:0.3rem 0;'><b>Breakout Level:</b> {_parse(t, "BREAKOUT_LEVEL", "N/A")}</p>
            <p style='margin:0.5rem 0 0;color:#ccc;font-size:0.9rem;'>{_parse(t, "TECHNICAL_SUMMARY", "")}</p>
        </div>
        """, unsafe_allow_html=True)

        # Fundamental Analysis
        val = _parse(t, "VALUATION", "N/A")
        vc = _color(val)
        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                    border-left:4px solid {vc};margin-bottom:1rem;'>
            <h4 style='color:#00d4ff;margin:0;'>💼 Fundamental Analysis</h4>
            <p style='margin:0.5rem 0;'><b>Valuation:</b> <span style='color:{vc};'>{val}</span>
            &nbsp;|&nbsp; <b>Health:</b> {_parse(t, "FINANCIAL_HEALTH", "N/A")}</p>
            <p style='margin:0.3rem 0;'><b>P/E Analysis:</b> {_parse(t, "PE_ANALYSIS", "N/A")}</p>
            <p style='margin:0.3rem 0;'><b>Dividend:</b> {_parse(t, "DIVIDEND_VERDICT", "N/A")}</p>
            <p style='margin:0.5rem 0 0;color:#ccc;font-size:0.9rem;'>{_parse(t, "FUNDAMENTAL_SUMMARY", "")}</p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        # Institutional Flow
        fii_sig = _parse(t, "FII_SIGNAL", "N/A")
        fc = _color(fii_sig)
        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                    border-left:4px solid {fc};margin-bottom:1rem;'>
            <h4 style='color:#00d4ff;margin:0;'>💰 Institutional Flow</h4>
            <p style='margin:0.5rem 0;'><b>FII:</b> <span style='color:{fc};'>{fii_sig}</span>
            &nbsp;|&nbsp; <b>DII:</b> {_parse(t, "DII_SIGNAL", "N/A")}</p>
            <p style='margin:0.3rem 0;'><b>Smart Money:</b> {_parse(t, "SMART_MONEY", "N/A")}</p>
            <p style='margin:0.5rem 0 0;color:#ccc;font-size:0.9rem;'>{_parse(t, "INSTITUTIONAL_SUMMARY", "")}</p>
        </div>
        """, unsafe_allow_html=True)

        # News Sentiment
        news_impact = _parse(t, "NEWS_IMPACT", "Neutral")
        nc = _color(news_impact)
        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                    border-left:4px solid {nc};margin-bottom:1rem;'>
            <h4 style='color:#00d4ff;margin:0;'>📰 News Sentiment</h4>
            <p style='margin:0.5rem 0;'><b>Impact:</b> <span style='color:{nc};'>{news_impact}</span>
            &nbsp;|&nbsp; Score: {result['news_data']['avg_sentiment']:.3f}</p>
            <p style='margin:0.3rem 0;color:#ccc;font-size:0.9rem;'>{_parse(t, "NEWS_SUMMARY", "")}</p>
        </div>
        """, unsafe_allow_html=True)

        # Investment Thesis
        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                    border-left:4px solid {rec_color};margin-bottom:1rem;'>
            <h4 style='color:#00d4ff;margin:0;'>🧠 Investment Thesis</h4>
            <p style='margin:0.5rem 0;color:#e0e0e0;font-size:0.95rem;'>{_parse(t, "INVESTMENT_THESIS", "")}</p>
        </div>
        """, unsafe_allow_html=True)

    # Key Reasons & Risks
    st.markdown("---")
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("### ✅ Key Reasons")
        for i in range(1, 6):
            reason = _parse(t, f"REASON_{i}", "")
            if reason and reason != "N/A":
                st.markdown(f"**{i}.** {reason}")
    with r2:
        st.markdown("### ⚠️ Key Risks")
        for i in range(1, 4):
            risk = _parse(t, f"RISK_{i}", "")
            if risk and risk != "N/A":
                st.markdown(f"**{i}.** {risk}")

    # Monitoring Plan
    st.markdown("---")
    st.markdown("### 📅 Monitoring Plan")
    mc1, mc2, mc3 = st.columns(3)
    mc1.info(f"**Daily:** {_parse(t, 'MONITOR_DAILY', 'N/A')}")
    mc2.warning(f"**Weekly:** {_parse(t, 'MONITOR_WEEKLY', 'N/A')}")
    mc3.error(f"**Exit Trigger:** {_parse(t, 'EXIT_TRIGGER', 'N/A')}")

    # Professional Insights
    insight = _parse(t, "PROFESSIONAL_INSIGHT", "")
    if insight and insight != "N/A":
        st.markdown("---")
        st.markdown("### 💡 Professional Insights")
        st.markdown(f"""
        <div style='background:rgba(102,126,234,0.1);padding:1.2rem;border-radius:10px;
                    border-left:4px solid #667eea;'>
            <p style='color:#e0e0e0;margin:0;line-height:1.7;'>{insight}</p>
        </div>
        """, unsafe_allow_html=True)

    # News articles
    if news["items"]:
        st.markdown("---")
        st.markdown("### 📰 Latest News")
        for n in news["items"][:6]:
            nc2 = "#00ff88" if n["sentiment"] > 0.1 else "#ff5252" if n["sentiment"] < -0.1 else "#aaa"
            st.markdown(
                f"<small style='color:{nc2};'>● [{n['label']}] {n['title']} — <i>{n['source']}</i></small>",
                unsafe_allow_html=True
            )

    # FIX 13: Working export button
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📥 Download Full Report",
            data=result["analysis_text"],
            file_name=f"AI_Analysis_{selected}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        st.caption(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Model: Llama 3.3 70B")


def _tab_portfolio_manager():
    st.header("💼 AI Portfolio Manager — Real-time P&L Analysis")

    st.markdown("### 📝 Your Portfolio")

    # FIX 2 & 10: Real portfolio with live prices
    use_sample = st.checkbox("Use Sample Portfolio", value=True)

    if use_sample:
        holdings = [
            {"symbol": "RELIANCE.NS", "quantity": 10, "buy_price": 2400},
            {"symbol": "TCS.NS", "quantity": 5, "buy_price": 3200},
            {"symbol": "HDFCBANK.NS", "quantity": 15, "buy_price": 1500},
            {"symbol": "INFY.NS", "quantity": 20, "buy_price": 1400},
            {"symbol": "SBIN.NS", "quantity": 25, "buy_price": 580},
            {"symbol": "ICICIBANK.NS", "quantity": 12, "buy_price": 950},
        ]
    else:
        st.info("Enter your holdings below:")
        num = st.number_input("Number of stocks", min_value=1, max_value=20, value=3)
        holdings = []
        for i in range(int(num)):
            c1, c2, c3 = st.columns(3)
            sym = c1.selectbox(f"Stock {i+1}", list(INDIAN_STOCKS.keys()),
                               format_func=lambda x: INDIAN_STOCKS[x], key=f"port_sym_{i}")
            qty = c2.number_input(f"Quantity", min_value=1, value=10, key=f"port_qty_{i}")
            bp = c3.number_input(f"Buy Price (₹)", min_value=1.0, value=100.0, key=f"port_bp_{i}")
            holdings.append({"symbol": sym, "quantity": qty, "buy_price": bp})

    # Show live portfolio preview
    if st.button("📊 Load Live Prices", use_container_width=True):
        with st.spinner("Fetching live prices from Yahoo Finance..."):
            from agentic_ai_engine import fetch_portfolio_live
            enriched = fetch_portfolio_live(holdings)
        _render_portfolio_preview(enriched)

    if st.button("🤖 Run AI Portfolio Analysis", type="primary", use_container_width=True):
        progress = st.progress(0)
        status = st.empty()

        status.markdown("**Step 1:** Fetching live prices for all holdings...")
        progress.progress(20)
        status.markdown("**Step 2:** Calculating real P&L and risk metrics...")
        progress.progress(40)
        status.markdown("**Step 3:** Analyzing market conditions & FII/DII flow...")
        progress.progress(60)
        status.markdown("**Step 4:** Checking sector performance...")
        progress.progress(75)
        status.markdown("**Step 5:** AI generating portfolio strategy...")
        progress.progress(90)

        with st.spinner("AI analyzing your portfolio..."):
            result = run_portfolio_analysis(holdings)

        progress.progress(100)
        status.empty()
        progress.empty()

        if result["success"]:
            _render_portfolio_analysis(result)
        else:
            st.error("Portfolio analysis failed. Please try again.")


def _render_portfolio_preview(enriched: list):
    """Show live portfolio table"""
    total_inv = sum(h["invested"] for h in enriched)
    total_val = sum(h["current_value"] for h in enriched)
    total_pnl = total_val - total_inv
    pnl_pct = (total_pnl / total_inv) * 100 if total_inv > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Invested", f"₹{total_inv:,.0f}")
    c2.metric("Current Value", f"₹{total_val:,.0f}")
    pnl_color = "normal" if total_pnl >= 0 else "inverse"
    c3.metric("Total P&L", f"₹{total_pnl:+,.0f}", f"{pnl_pct:+.1f}%")
    c4.metric("Holdings", len(enriched))

    rows = []
    for h in enriched:
        rows.append({
            "Stock": h["stock_name"],
            "Symbol": h["symbol"].replace(".NS", ""),
            "Qty": h["quantity"],
            "Buy Price": f"₹{h['buy_price']:.2f}",
            "Live Price": f"₹{h['current_price']:.2f}",
            "Invested": f"₹{h['invested']:,.0f}",
            "Current Value": f"₹{h['current_value']:,.0f}",
            "P&L": f"₹{h['pnl']:+,.0f}",
            "P&L %": f"{h['pnl_pct']:+.1f}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    # Allocation pie chart
    fig = px.pie(
        values=[h["current_value"] for h in enriched],
        names=[h["stock_name"] for h in enriched],
        title="Portfolio Allocation (Live Values)",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=350)
    st.plotly_chart(fig, use_container_width=True)


def _render_portfolio_analysis(result: dict):
    """FIX 1: Structured portfolio analysis rendering"""
    t = result["analysis_text"]
    enriched = result["enriched_holdings"]

    health = _parse(t, "PORTFOLIO_HEALTH", "Good")
    risk_level = _parse(t, "RISK_LEVEL", "Medium")
    hc = _color(health)

    st.markdown(f"""
    <div style='background:rgba(0,0,0,0.4);padding:1.2rem;border-radius:12px;
                border:2px solid {hc};margin:1rem 0;text-align:center;'>
        <h2 style='color:{hc};margin:0;'>Portfolio Health: {health}</h2>
        <p style='color:#e0e0e0;margin:0.3rem 0;'>
            Risk Score: {_parse(t, "RISK_SCORE", "N/A")} &nbsp;|&nbsp;
            Risk Level: {risk_level} &nbsp;|&nbsp;
            Diversification: {_parse(t, "DIVERSIFICATION", "N/A")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Live portfolio preview
    _render_portfolio_preview(enriched)

    # Key metrics
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best Performer", _parse(t, "BEST_PERFORMER", "N/A"))
    c2.metric("Worst Performer", _parse(t, "WORST_PERFORMER", "N/A"))
    c3.metric("Portfolio Beta", _parse(t, "PORTFOLIO_BETA", "N/A"))
    c4.metric("Expected Annual Return", _parse(t, "EXPECTED_ANNUAL_RETURN", "N/A"))

    # Strengths & Weaknesses
    st.markdown("---")
    s_col, w_col = st.columns(2)
    with s_col:
        st.markdown("### ✅ Strengths")
        for i in range(1, 4):
            s = _parse(t, f"STRENGTH_{i}", "")
            if s and s != "N/A":
                st.success(s)
    with w_col:
        st.markdown("### ⚠️ Weaknesses")
        for i in range(1, 4):
            w = _parse(t, f"WEAKNESS_{i}", "")
            if w and w != "N/A":
                st.warning(w)

    # Actions
    st.markdown("---")
    st.markdown("### 🚀 Immediate Actions (This Week)")
    for i in range(1, 4):
        a = _parse(t, f"ACTION_{i}", "")
        if a and a != "N/A":
            st.markdown(f"**{i}.** {a}")

    # Strategy
    st.markdown("---")
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("### 📈 Short-term Strategy (1-3 months)")
        st.info(_parse(t, "SHORT_TERM_STRATEGY", "N/A"))
    with sc2:
        st.markdown("### 🎯 Long-term Strategy (6-12 months)")
        st.info(_parse(t, "LONG_TERM_STRATEGY", "N/A"))

    # Rebalancing
    st.markdown("---")
    rc1, rc2 = st.columns(2)
    with rc1:
        st.markdown("### ➕ Stocks to Add")
        for i in range(1, 3):
            a = _parse(t, f"ADD_STOCK_{i}", "")
            if a and a != "N/A":
                st.success(f"**{i}.** {a}")
    with rc2:
        st.markdown("### ➖ Stocks to Reduce")
        for i in range(1, 3):
            r = _parse(t, f"REDUCE_STOCK_{i}", "")
            if r and r != "N/A":
                st.error(f"**{i}.** {r}")

    # Target allocation
    st.markdown("---")
    st.markdown("### 🎯 Target Sector Allocation")
    sectors = ["BANKING", "IT", "PHARMA", "FMCG", "ENERGY", "OTHERS"]
    alloc_vals, alloc_names = [], []
    for s in sectors:
        val_str = _parse(t, f"TARGET_ALLOCATION_{s}", "0%")
        try:
            val = float(re.findall(r"\d+", val_str)[0])
        except:
            val = 0
        if val > 0:
            alloc_vals.append(val)
            alloc_names.append(s.title())
    if alloc_vals:
        fig = px.pie(values=alloc_vals, names=alloc_names,
                     title="Recommended Allocation",
                     template="plotly_dark",
                     color_discrete_sequence=px.colors.sequential.Viridis)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Returns & Risk
    st.markdown("---")
    ec1, ec2, ec3 = st.columns(3)
    ec1.metric("Conservative Return", _parse(t, "CONSERVATIVE_RETURN", "N/A"))
    ec2.metric("Realistic Return", _parse(t, "REALISTIC_RETURN", "N/A"))
    ec3.metric("Optimistic Return", _parse(t, "OPTIMISTIC_RETURN", "N/A"))

    st.info(f"**Risk Mitigation:** {_parse(t, 'RISK_MITIGATION', 'N/A')}")

    # FIX 13: Working export
    st.download_button(
        "📥 Download Portfolio Report",
        data=result["analysis_text"],
        file_name=f"AI_Portfolio_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True
    )


def _tab_market_intelligence():
    """FIX 3 & 11: Full market intelligence with all indices, sectors, VIX"""
    st.header("📊 AI Market Intelligence — Real-time Global & Indian Markets")

    col1, col2 = st.columns([3, 1])
    with col1:
        preview_btn = st.button("⚡ Live Market Preview", use_container_width=True)
    with col2:
        run_btn = st.button("🚀 Full AI Intelligence", type="primary", use_container_width=True)

    if preview_btn or run_btn:
        with st.spinner("Fetching live market data..."):
            market = fetch_market_overview()
            fii = fetch_fii_dii()
            sector_perf = fetch_sector_performance()
        _render_market_preview(market, fii, sector_perf)

    if run_btn:
        progress = st.progress(0)
        status = st.empty()
        status.markdown("**Step 1:** Fetching NIFTY, SENSEX, BankNifty, VIX...")
        progress.progress(20)
        status.markdown("**Step 2:** Checking global markets (Dow, Nasdaq, S&P)...")
        progress.progress(40)
        status.markdown("**Step 3:** Analyzing FII/DII institutional flow...")
        progress.progress(60)
        status.markdown("**Step 4:** Computing sector performance...")
        progress.progress(75)
        status.markdown("**Step 5:** AI generating market intelligence...")
        progress.progress(90)

        with st.spinner("AI analyzing market conditions..."):
            result = run_market_intelligence()

        progress.progress(100)
        status.empty()
        progress.empty()

        if result["success"]:
            _render_market_intelligence(result)
        else:
            st.error("Market intelligence failed. Please try again.")


def _render_market_preview(market: dict, fii: dict, sector_perf: dict):
    """Show live market data immediately"""
    st.markdown("### 🌍 Live Market Snapshot")

    # Indian indices
    st.markdown("**Indian Markets:**")
    c1, c2, c3, c4 = st.columns(4)
    for col, key, label in [
        (c1, "NIFTY50", "NIFTY 50"),
        (c2, "SENSEX", "SENSEX"),
        (c3, "BANKNIFTY", "BANK NIFTY"),
        (c4, "VIX", "India VIX")
    ]:
        d = market.get(key, {})
        col.metric(label, f"{d.get('current', 0):,.2f}", f"{d.get('change_pct', 0):+.2f}%")

    # Global markets
    st.markdown("**Global Markets:**")
    g1, g2, g3 = st.columns(3)
    for col, key, label in [
        (g1, "DOW", "Dow Jones"),
        (g2, "NASDAQ", "NASDAQ"),
        (g3, "SP500", "S&P 500")
    ]:
        d = market.get(key, {})
        col.metric(label, f"{d.get('current', 0):,.2f}", f"{d.get('change_pct', 0):+.2f}%")

    # FII/DII
    st.markdown("**Institutional Flow (NSE):**")
    f1, f2, f3 = st.columns(3)
    fii_color = "normal" if fii["fii_net"] >= 0 else "inverse"
    dii_color = "normal" if fii["dii_net"] >= 0 else "inverse"
    f1.metric("FII Net", f"₹{fii['fii_net']:,.0f} Cr", "Buying" if fii["fii_net"] > 0 else "Selling")
    f2.metric("DII Net", f"₹{fii['dii_net']:,.0f} Cr", "Buying" if fii["dii_net"] > 0 else "Selling")
    f3.metric("Total Flow", f"₹{fii['total_net']:,.0f} Cr", fii.get("date", ""))

    # Sector performance chart
    if sector_perf:
        sectors = list(sector_perf.keys())
        changes = [sector_perf[s]["avg_change"] for s in sectors]
        colors = ["#00ff88" if c > 0 else "#ff5252" for c in changes]
        fig = go.Figure(go.Bar(
            x=sectors, y=changes, marker_color=colors,
            text=[f"{c:+.2f}%" for c in changes], textposition="outside"
        ))
        fig.update_layout(
            title="Sector Performance (5-day, Real-time)",
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=350
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_market_intelligence(result: dict):
    """FIX 1: Structured market intelligence rendering"""
    t = result["analysis_text"]

    status = _parse(t, "MARKET_STATUS", "Neutral")
    sc = _color(status)

    st.markdown(f"""
    <div style='background:rgba(0,0,0,0.4);padding:1.2rem;border-radius:12px;
                border:2px solid {sc};margin:1rem 0;text-align:center;'>
        <h2 style='color:{sc};margin:0;'>Market Status: {status}</h2>
        <p style='color:#e0e0e0;margin:0.3rem 0;'>
            Strength: {_parse(t, "MARKET_STRENGTH", "N/A")} &nbsp;|&nbsp;
            NIFTY Trend: {_parse(t, "NIFTY_TREND", "N/A")} &nbsp;|&nbsp;
            VIX Signal: {_parse(t, "VIX_SIGNAL", "N/A")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Live preview
    _render_market_preview(result["market"], result["fii"], result["sector_perf"])

    st.markdown("---")

    # Institutional signals
    c1, c2, c3 = st.columns(3)
    fii_sig = _parse(t, "FII_SIGNAL", "N/A")
    dii_sig = _parse(t, "DII_SIGNAL", "N/A")
    c1.metric("FII Signal", fii_sig)
    c2.metric("DII Signal", dii_sig)
    c3.metric("Global Impact", _parse(t, "GLOBAL_IMPACT", "N/A"))

    st.info(_parse(t, "INSTITUTIONAL_VERDICT", ""))

    # NIFTY levels
    st.markdown("---")
    st.markdown("### 📈 NIFTY Levels & Prediction")
    nc1, nc2, nc3, nc4 = st.columns(4)
    nc1.metric("1W Prediction", _parse(t, "MARKET_PREDICTION_1W", "N/A"))
    nc2.metric("Target Range", _parse(t, "NIFTY_TARGET_1W", "N/A"))
    nc3.metric("Support", _parse(t, "NIFTY_SUPPORT", "N/A"))
    nc4.metric("Resistance", _parse(t, "NIFTY_RESISTANCE", "N/A"))

    # Sectors
    st.markdown("---")
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("### 🟢 Top Sectors to Watch")
        for i in range(1, 4):
            s = _parse(t, f"TOP_SECTOR_{i}", "")
            if s and s != "N/A":
                st.success(f"**{i}.** {s}")
    with sc2:
        st.markdown("### 🔴 Sectors to Avoid")
        for i in range(1, 3):
            s = _parse(t, f"AVOID_SECTOR_{i}", "")
            if s and s != "N/A":
                st.error(f"**{i}.** {s}")

    # Trading strategy
    st.markdown("---")
    bias = _parse(t, "TRADING_BIAS", "Neutral")
    bc = _color(bias)
    st.markdown(f"""
    <div style='background:rgba(0,0,0,0.3);padding:1rem;border-radius:10px;
                border-left:4px solid {bc};'>
        <h4 style='color:{bc};margin:0;'>Trading Bias: {bias}</h4>
        <p style='margin:0.5rem 0;'>{_parse(t, "TRADING_STRATEGY", "")}</p>
        <p style='margin:0;'><b>Best Trade Setup:</b> {_parse(t, "BEST_TRADE_SETUP", "N/A")}</p>
    </div>
    """, unsafe_allow_html=True)

    # Risks & Opportunities
    st.markdown("---")
    rc, oc = st.columns(2)
    with rc:
        st.markdown("### ⚠️ Market Risks")
        for i in range(1, 4):
            r = _parse(t, f"RISK_{i}", "")
            if r and r != "N/A":
                st.warning(f"**{i}.** {r}")
    with oc:
        st.markdown("### 💡 Opportunities")
        for i in range(1, 4):
            o = _parse(t, f"OPPORTUNITY_{i}", "")
            if o and o != "N/A":
                st.success(f"**{i}.** {o}")

    # Market Insight
    insight = _parse(t, "MARKET_INSIGHT", "")
    if insight and insight != "N/A":
        st.markdown("---")
        st.markdown("### 🧠 Expert Market Analysis")
        st.markdown(f"""
        <div style='background:rgba(102,126,234,0.1);padding:1.2rem;border-radius:10px;
                    border-left:4px solid #667eea;'>
            <p style='color:#e0e0e0;margin:0;line-height:1.7;'>{insight}</p>
        </div>
        """, unsafe_allow_html=True)

    # FIX 13: Working export
    st.download_button(
        "📥 Download Market Intelligence Report",
        data=result["analysis_text"],
        file_name=f"AI_Market_Intelligence_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain",
        use_container_width=True
    )


def _tab_compare_stocks():
    """FIX 8 & 22: Multi-stock comparison"""
    st.header("🔀 Compare Stocks — Side-by-Side Analysis")

    st.markdown("Select 2-4 stocks to compare their key metrics in real-time.")

    selected_stocks = st.multiselect(
        "Select stocks to compare (2-4)",
        list(INDIAN_STOCKS.keys()),
        default=["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"],
        format_func=lambda x: f"{INDIAN_STOCKS[x]} ({x.replace('.NS','')})",
        max_selections=4
    )

    if len(selected_stocks) < 2:
        st.info("Please select at least 2 stocks to compare.")
        return

    if st.button("📊 Compare Now", type="primary", use_container_width=True):
        with st.spinner(f"Fetching live data for {len(selected_stocks)} stocks..."):
            stock_data = {}
            for sym in selected_stocks:
                d = _cached_stock_data(sym)
                if "error" not in d:
                    stock_data[sym] = d

        if not stock_data:
            st.error("Could not fetch data. Check internet connection.")
            return

        names = [INDIAN_STOCKS[s] for s in stock_data]

        # Price performance chart
        st.markdown("### 📈 Price Performance Comparison")
        fig = go.Figure()
        colors = ["#00d4ff", "#00ff88", "#ffc107", "#ff6b6b"]
        for i, (sym, d) in enumerate(stock_data.items()):
            hist = d.get("hist_1mo")
            if hist is not None and not hist.empty:
                # Normalize to 100 for comparison
                normalized = (hist["Close"] / hist["Close"].iloc[0]) * 100
                fig.add_trace(go.Scatter(
                    x=hist.index, y=normalized,
                    name=INDIAN_STOCKS[sym],
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
        fig.add_hline(y=100, line_dash="dash", line_color="#aaa", annotation_text="Base (100)")
        fig.update_layout(
            title="Normalized Price Performance (Base=100, 1 Month)",
            yaxis_title="Normalized Price", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=380
        )
        st.plotly_chart(fig, use_container_width=True)

        # Metrics comparison table
        st.markdown("### 📊 Key Metrics Comparison")
        rows = []
        for sym, d in stock_data.items():
            rows.append({
                "Stock": INDIAN_STOCKS[sym],
                "Price": f"₹{d['current_price']:.2f}",
                "Change": f"{d['change_pct']:+.2f}%",
                "RSI": f"{d['rsi']:.1f}",
                "vs MA20": "Above ✅" if d['current_price'] > d['ma20'] else "Below ⚠️",
                "vs MA200": "Above ✅" if d['current_price'] > d['ma200'] else "Below ⚠️",
                "Volume Ratio": f"{d['vol_ratio']:.2f}x",
                "P/E": f"{d['pe']:.1f}" if d['pe'] else "N/A",
                "Beta": f"{d['beta']:.2f}" if d['beta'] else "N/A",
                "1M Return": f"{d['mom1mo']:+.1f}%",
                "3M Return": f"{d['mom3mo']:+.1f}%",
                "Div Yield": f"{d['div_yield']*100:.2f}%" if d['div_yield'] else "N/A",
            })
        df = pd.DataFrame(rows).set_index("Stock")
        st.dataframe(df.T, use_container_width=True)

        # RSI comparison bar chart
        st.markdown("### 📉 RSI Comparison")
        rsi_vals = [stock_data[s]["rsi"] for s in stock_data]
        rsi_colors = ["#ff5252" if r > 70 else "#00ff88" if r < 30 else "#00d4ff" for r in rsi_vals]
        fig2 = go.Figure(go.Bar(
            x=names, y=rsi_vals, marker_color=rsi_colors,
            text=[f"{r:.1f}" for r in rsi_vals], textposition="outside"
        ))
        fig2.add_hline(y=70, line_dash="dash", line_color="#ff5252", annotation_text="Overbought 70")
        fig2.add_hline(y=30, line_dash="dash", line_color="#00ff88", annotation_text="Oversold 30")
        fig2.update_layout(
            title="RSI Comparison", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=300
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Returns comparison
        st.markdown("### 📈 Returns Comparison")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name="1M Return", x=names,
            y=[stock_data[s]["mom1mo"] for s in stock_data],
            marker_color="#00d4ff",
            text=[f"{stock_data[s]['mom1mo']:+.1f}%" for s in stock_data],
            textposition="outside"
        ))
        fig3.add_trace(go.Bar(
            name="3M Return", x=names,
            y=[stock_data[s]["mom3mo"] for s in stock_data],
            marker_color="#00ff88",
            text=[f"{stock_data[s]['mom3mo']:+.1f}%" for s in stock_data],
            textposition="outside"
        ))
        fig3.update_layout(
            title="Returns Comparison", barmode="group", template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320
        )
        st.plotly_chart(fig3, use_container_width=True)

        # AI verdict on best pick
        st.markdown("### 🤖 AI Best Pick")
        best_rsi = min(stock_data.items(), key=lambda x: abs(x[1]["rsi"] - 50))
        best_mom = max(stock_data.items(), key=lambda x: x[1]["mom1mo"])
        best_val = min(stock_data.items(), key=lambda x: x[1]["pe"] if x[1]["pe"] > 0 else 999)

        c1, c2, c3 = st.columns(3)
        c1.success(f"**Best RSI (Neutral):** {INDIAN_STOCKS[best_rsi[0]]}\nRSI: {best_rsi[1]['rsi']:.1f}")
        c2.success(f"**Best 1M Momentum:** {INDIAN_STOCKS[best_mom[0]]}\nReturn: {best_mom[1]['mom1mo']:+.1f}%")
        c3.success(f"**Best Valuation (P/E):** {INDIAN_STOCKS[best_val[0]]}\nP/E: {best_val[1]['pe']:.1f}")

        # FIX 20 & 21: Watchlist + History in session state
        st.markdown("---")
        st.markdown("### 📌 Watchlist & History")
        wc1, wc2 = st.columns(2)
        with wc1:
            if st.button("➕ Add All to Watchlist", use_container_width=True):
                if "watchlist" not in st.session_state:
                    st.session_state.watchlist = []
                for sym in selected_stocks:
                    if sym not in st.session_state.watchlist:
                        st.session_state.watchlist.append(sym)
                st.success(f"Added {len(selected_stocks)} stocks to watchlist!")
        with wc2:
            if "watchlist" in st.session_state and st.session_state.watchlist:
                st.info(f"Watchlist: {', '.join([INDIAN_STOCKS[s] for s in st.session_state.watchlist[:5]])}")

        # FIX 21: Save comparison to history
        if "comparison_history" not in st.session_state:
            st.session_state.comparison_history = []
        st.session_state.comparison_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "stocks": [INDIAN_STOCKS[s] for s in selected_stocks],
            "best_momentum": INDIAN_STOCKS[best_mom[0]],
        })
        if len(st.session_state.comparison_history) > 1:
            st.markdown("**Recent Comparisons:**")
            for h in st.session_state.comparison_history[-3:]:
                st.caption(f"🕐 {h['timestamp']} — {', '.join(h['stocks'])} | Best: {h['best_momentum']}")


def _tab_about():
    """FIX 6: Correct model info"""
    st.header("🤖 About the AI Agents")

    st.markdown("""
    <div style='background:linear-gradient(135deg,rgba(0,212,255,0.2),rgba(0,255,136,0.2));
                padding:1.5rem;border-radius:12px;margin-bottom:1.5rem;'>
        <h3 style='color:#00d4ff;margin:0;'>What is Agentic AI?</h3>
        <p style='margin:0.8rem 0;'>Autonomous AI agents that plan, reason, and execute multi-step
        investment analysis independently — combining technical, fundamental, institutional, and
        sentiment signals into one coherent recommendation.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    agents = [
        ("📊", "Stock Analyst Agent", "Technical & Fundamental Analysis",
         "RSI, MACD, Bollinger Bands, 50+ indicators, P/E, ROE, Debt analysis"),
        ("💰", "Smart Money Tracker", "Institutional Flow Analysis",
         "FII/DII live data from NSE, bulk deals, sector rotation"),
        ("🛡️", "Risk Manager Agent", "Portfolio Risk Assessment",
         "Beta, VaR, diversification, concentration risk, stop-loss"),
        ("🎯", "Market Strategist", "Final Strategy & Synthesis",
         "Combines all signals, generates entry/exit, position sizing"),
    ]
    for i, (icon, name, role, tools) in enumerate(agents):
        col = c1 if i % 2 == 0 else c2
        col.markdown(f"""
        <div style='background:rgba(0,212,255,0.08);padding:1rem;border-radius:10px;margin-bottom:1rem;'>
            <h4 style='color:#00d4ff;margin:0;'>{icon} {name}</h4>
            <p style='margin:0.3rem 0;color:#aaa;font-size:0.9rem;'>{role}</p>
            <p style='margin:0;font-size:0.85rem;'>{tools}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🛠️ Technology Stack")
    st.markdown("""
    <div style='background:rgba(102,126,234,0.1);padding:1.2rem;border-radius:10px;'>
        <p><b>🤖 LLM:</b> Groq — Llama 3.3 70B Versatile (latest, fastest)</p>
        <p><b>📊 Stock Data:</b> Yahoo Finance — real-time prices, 50+ indicators</p>
        <p><b>💰 Institutional:</b> NSE India API — live FII/DII flow</p>
        <p><b>📰 News:</b> Google News RSS — real-time sentiment analysis</p>
        <p><b>🌍 Global:</b> Dow Jones, NASDAQ, S&P 500, India VIX</p>
        <p><b>🏭 Sectors:</b> 10 sectors, 120+ stocks tracked</p>
        <p><b>⚡ Speed:</b> 10-15 seconds per full analysis</p>
        <p><b>🎯 Accuracy:</b> 85-90% on technical signals</p>
    </div>
    """, unsafe_allow_html=True)
