"""
🧠 AI-Powered "Explain My Loss" — Personal Finance Coach
Author: Aman Jain (B.Tech 2023-27)

Flow:
  1. Reads user's real portfolio from SQLite (portfolio_holdings table)
  2. Fetches today's live price change for every holding via yfinance
  3. Fetches live FII/DII data from NSE API
  4. Fetches live sector performance via yfinance
  5. Fetches live news headlines via Google Finance RSS
  6. Sends ALL of it to Groq Llama-3.3-70B
  7. Returns plain-language explanation + SELL/HOLD recommendation
  8. Renders rich Plotly charts + Hindi/English toggle
"""

import sqlite3
import os
import requests
import feedparser
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re
import warnings
warnings.filterwarnings("ignore")

# ── DB path (same as rest of platform) ───────────────────────────────────────
_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "sarthak_nivesh.db"
)

# ── NSE header (same as smart_money_live) ────────────────────────────────────
_HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

# ── Sector → representative NSE tickers ──────────────────────────────────────
SECTOR_TICKERS = {
    "Banking":  ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
    "IT":       ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
    "Pharma":   ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"],
    "Auto":     ["MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS"],
    "Energy":   ["RELIANCE.NS", "ONGC.NS", "NTPC.NS"],
    "FMCG":     ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS"],
    "Metals":   ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS"],
    "Realty":   ["DLF.NS", "GODREJPROP.NS"],
    "Telecom":  ["BHARTIARTL.NS"],
    "Others":   ["LT.NS", "ULTRACEMCO.NS"],
}


# ═════════════════════════════════════════════════════════════════════════════
# DATA FETCHERS  (100 % real-time, zero dummy data)
# ═════════════════════════════════════════════════════════════════════════════

def _fetch_portfolio_from_db():
    """Read holdings from portfolio_holdings table (created by PortfolioRiskManager)."""
    try:
        conn = sqlite3.connect(_DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM portfolio_holdings WHERE user_id = 'default' ORDER BY created_at DESC",
            conn
        )
        conn.close()
        return df
    except Exception as e:
        print(f"DB read error: {e}")
        return pd.DataFrame()


def _fetch_today_prices(holdings_df):
    """
    For each holding fetch today's open & latest close from yfinance.
    Returns list of dicts with live price data.
    """
    results = []
    for _, row in holdings_df.iterrows():
        symbol = str(row.get("symbol", "")).strip()
        if not symbol:
            continue
        # symbol stored without .NS in portfolio_holdings
        ticker_sym = symbol if symbol.endswith(".NS") else symbol + ".NS"
        try:
            hist = yf.Ticker(ticker_sym).history(period="5d")
            if hist.empty or len(hist) < 2:
                continue
            today_close = float(hist["Close"].iloc[-1])
            prev_close  = float(hist["Close"].iloc[-2])
            today_open  = float(hist["Open"].iloc[-1])
            day_high    = float(hist["High"].iloc[-1])
            day_low     = float(hist["Low"].iloc[-1])
            volume      = float(hist["Volume"].iloc[-1])
            chg_pct     = ((today_close - prev_close) / prev_close) * 100

            buy_price   = float(row.get("buy_price", 0))
            quantity    = float(row.get("quantity", 0))
            invested    = buy_price * quantity
            curr_val    = today_close * quantity
            overall_pnl_pct = ((today_close - buy_price) / buy_price) * 100 if buy_price else 0

            results.append({
                "symbol":        symbol,
                "ticker":        ticker_sym,
                "company_name":  str(row.get("company_name", symbol)),
                "sector":        str(row.get("sector", "Others")),
                "quantity":      quantity,
                "buy_price":     buy_price,
                "today_open":    today_open,
                "prev_close":    prev_close,
                "today_close":   today_close,
                "day_high":      day_high,
                "day_low":       day_low,
                "volume":        volume,
                "today_chg_pct": chg_pct,
                "today_pnl":     (today_close - prev_close) * quantity,
                "invested":      invested,
                "curr_val":      curr_val,
                "overall_pnl_pct": overall_pnl_pct,
            })
        except Exception as e:
            print(f"Price fetch error {symbol}: {e}")
    return results


def _fetch_fii_dii():
    """Fetch today's FII/DII from NSE API (same logic as smart_money_live)."""
    def _n(v):
        try:
            v = str(v).replace(",", "").replace("(", "-").replace(")","").strip()
            m = re.findall(r"-?\d+\.?\d*", v)
            return float(m[0]) if m else 0.0
        except Exception:
            return 0.0

    try:
        sess = requests.Session()
        sess.headers.update(_HDR)
        r = sess.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=15)
        if r.status_code == 200:
            data = r.json()
            fii = next((x for x in data if "FII" in x.get("category","").upper()), None)
            dii = next((x for x in data if "DII" in x.get("category","").upper()), None)
            if fii or dii:
                fii_net = _n((fii or {}).get("netValue", 0))
                dii_net = _n((dii or {}).get("netValue", 0))
                fii_buy = _n((fii or {}).get("buyValue", 0))
                fii_sell= _n((fii or {}).get("sellValue",0))
                date    = (fii or dii or {}).get("date", datetime.now().strftime("%d-%b-%Y"))
                return {"fii_net": fii_net, "dii_net": dii_net,
                        "fii_buy": fii_buy, "fii_sell": fii_sell,
                        "date": date, "source": "NSE Live"}
    except Exception as e:
        print(f"FII/DII fetch error: {e}")
    return {"fii_net": None, "dii_net": None, "source": "Unavailable"}


def _fetch_sector_performance():
    """Fetch live sector % change using representative stocks."""
    perf = {}
    for sector, tickers in SECTOR_TICKERS.items():
        changes = []
        for t in tickers:
            try:
                hist = yf.Ticker(t).history(period="2d")
                if len(hist) >= 2:
                    chg = ((hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
                           / hist["Close"].iloc[-2]) * 100
                    changes.append(chg)
            except Exception:
                pass
        if changes:
            perf[sector] = round(float(np.mean(changes)), 2)
    return perf


def _fetch_nifty_today():
    """Fetch NIFTY 50 today's change %."""
    try:
        hist = yf.Ticker("^NSEI").history(period="2d")
        if len(hist) >= 2:
            chg = ((hist["Close"].iloc[-1] - hist["Close"].iloc[-2])
                   / hist["Close"].iloc[-2]) * 100
            return round(float(chg), 2), float(hist["Close"].iloc[-1])
    except Exception:
        pass
    return None, None


def _fetch_news_headlines(max_items=8):
    """Fetch latest Indian market news from Google Finance RSS."""
    headlines = []
    try:
        feed = feedparser.parse(
            "https://news.google.com/rss/search?q=indian+stock+market+NSE+BSE&hl=en-IN&gl=IN&ceid=IN:en"
        )
        for entry in feed.entries[:max_items]:
            headlines.append(entry.get("title", ""))
    except Exception as e:
        print(f"News fetch error: {e}")
    return headlines


# ═════════════════════════════════════════════════════════════════════════════
# GROQ AI EXPLAINER
# ═════════════════════════════════════════════════════════════════════════════

def _build_groq_prompt(price_data, fii_dii, sector_perf, nifty_chg,
                        nifty_val, headlines, language="English"):
    """Build a rich, data-packed prompt for Groq."""

    # Portfolio summary
    total_invested = sum(p["invested"] for p in price_data)
    total_curr     = sum(p["curr_val"] for p in price_data)
    total_today_pnl= sum(p["today_pnl"] for p in price_data)
    port_today_pct = (total_today_pnl / total_curr * 100) if total_curr else 0

    holdings_lines = "\n".join([
        f"  • {p['company_name']} ({p['symbol']}) | Sector: {p['sector']} | "
        f"Qty: {int(p['quantity'])} | Buy: ₹{p['buy_price']:.2f} | "
        f"Today Close: ₹{p['today_close']:.2f} | "
        f"Today Change: {p['today_chg_pct']:+.2f}% | "
        f"Today P&L: ₹{p['today_pnl']:+,.0f} | "
        f"Overall P&L: {p['overall_pnl_pct']:+.2f}%"
        for p in price_data
    ])

    # FII/DII
    fii_line = "FII/DII data unavailable"
    if fii_dii.get("fii_net") is not None:
        fii_line = (
            f"FII Net: ₹{fii_dii['fii_net']:+,.0f} Cr | "
            f"DII Net: ₹{fii_dii['dii_net']:+,.0f} Cr "
            f"(Date: {fii_dii.get('date','today')})"
        )

    # Sector
    sector_lines = "\n".join([
        f"  • {s}: {v:+.2f}%" for s, v in sorted(sector_perf.items(), key=lambda x: x[1])
    ]) if sector_perf else "  Sector data unavailable"

    # News
    news_lines = "\n".join([f"  {i+1}. {h}" for i, h in enumerate(headlines)]) or "  No headlines available"

    # Nifty
    nifty_line = (f"NIFTY 50: {nifty_chg:+.2f}% | Level: {nifty_val:,.0f}"
                  if nifty_chg is not None else "NIFTY data unavailable")

    lang_instruction = (
        "Respond ENTIRELY in Hindi (Devanagari script). Use simple language a common Indian investor understands."
        if language == "Hindi" else
        "Respond in simple English. Avoid jargon. Write as if explaining to a first-time investor."
    )

    prompt = f"""
You are a compassionate, expert Indian stock market advisor. A retail investor is worried because their portfolio moved today.
Use ONLY the real-time data provided below. Do NOT make up any numbers.

{lang_instruction}

=== LIVE PORTFOLIO DATA (today) ===
Portfolio Today Change: {port_today_pct:+.2f}%  (₹{total_today_pnl:+,.0f})
Total Invested: ₹{total_invested:,.0f} | Current Value: ₹{total_curr:,.0f}

Holdings:
{holdings_lines}

=== LIVE MARKET CONTEXT ===
{nifty_line}
Institutional Flow: {fii_line}

Sector Performance Today:
{sector_lines}

Latest Market News:
{news_lines}

=== YOUR TASK ===
Write a warm, clear explanation with these 4 sections:

1. **What happened today** — In 2-3 sentences, explain why the portfolio moved the way it did today, citing specific stocks, sectors, and the FII/DII data above.

2. **The main culprits** — List the top 2-3 stocks dragging the portfolio down (or up) with their exact % change from the data above.

3. **Should I SELL or HOLD?** — Give a clear recommendation with reasoning. Consider overall P&L, market context, and whether this is a temporary move or a structural problem.

4. **One calming insight** — One sentence that puts today's move in perspective (e.g., long-term return, market cycle context).

Keep total response under 300 words. Be warm and reassuring, not alarming.
"""
    return prompt.strip()


def _call_groq(prompt, api_key):
    """Direct Groq API call — no dependency on other modules."""
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": "openai/gpt-oss-120b",
                "temperature": 0.6,
                "max_tokens": 700,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a compassionate, expert Indian stock market advisor. "
                            "Always use the exact numbers provided. Never fabricate data. "
                            "Be warm, clear, and reassuring."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=40,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        print(f"Groq error {r.status_code}: {r.text[:200]}")
        return None
    except Exception as e:
        print(f"Groq call error: {e}")
        return None


# ═════════════════════════════════════════════════════════════════════════════
# CHARTS
# ═════════════════════════════════════════════════════════════════════════════

def _chart_today_pnl(price_data):
    """Horizontal bar — today's ₹ P&L per stock."""
    df = pd.DataFrame(price_data).sort_values("today_pnl")
    colors = ["#ff5252" if v < 0 else "#00ff88" for v in df["today_pnl"]]
    fig = go.Figure(go.Bar(
        x=df["today_pnl"],
        y=df["company_name"],
        orientation="h",
        marker_color=colors,
        text=[f"₹{v:+,.0f}" for v in df["today_pnl"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Today's P&L per Stock (₹)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=max(300, len(df) * 45),
        xaxis_title="₹ P&L Today",
        margin=dict(l=10, r=60, t=50, b=30),
    )
    fig.add_vline(x=0, line_dash="dash", line_color="#555")
    return fig


def _chart_today_pct(price_data):
    """Bar chart — today's % change per stock vs NIFTY."""
    df = pd.DataFrame(price_data).sort_values("today_chg_pct")
    colors = ["#ff5252" if v < 0 else "#00ff88" for v in df["today_chg_pct"]]
    fig = go.Figure(go.Bar(
        x=df["company_name"],
        y=df["today_chg_pct"],
        marker_color=colors,
        text=[f"{v:+.2f}%" for v in df["today_chg_pct"]],
        textposition="outside",
    ))
    fig.update_layout(
        title="Today's % Change per Stock",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        yaxis_title="% Change",
        xaxis_tickangle=-30,
        margin=dict(l=10, r=10, t=50, b=80),
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#555")
    return fig


def _chart_sector_heatmap(sector_perf):
    """Sector performance heatmap."""
    if not sector_perf:
        return None
    sectors = list(sector_perf.keys())
    values  = list(sector_perf.values())
    fig = go.Figure(go.Bar(
        x=sectors,
        y=values,
        marker_color=["#ff5252" if v < 0 else "#00ff88" for v in values],
        text=[f"{v:+.2f}%" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title="Live Sector Performance Today (%)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=380,
        yaxis_title="% Change",
        xaxis_tickangle=-20,
        margin=dict(l=10, r=10, t=50, b=60),
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#555")
    return fig


def _chart_portfolio_allocation(price_data):
    """Donut chart — current portfolio allocation by stock."""
    df = pd.DataFrame(price_data)
    fig = go.Figure(go.Pie(
        labels=df["company_name"],
        values=df["curr_val"],
        hole=0.45,
        textinfo="label+percent",
        marker=dict(line=dict(color="#1a1a2e", width=2)),
    ))
    fig.update_layout(
        title="Portfolio Allocation (Current Value)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def _chart_overall_pnl(price_data):
    """Scatter — overall P&L % (since buy) per stock, sized by invested amount."""
    df = pd.DataFrame(price_data)
    colors = ["#ff5252" if v < 0 else "#00ff88" for v in df["overall_pnl_pct"]]
    fig = go.Figure(go.Scatter(
        x=df["company_name"],
        y=df["overall_pnl_pct"],
        mode="markers+text",
        marker=dict(
            size=[max(12, min(50, abs(v) * 2 + 12)) for v in df["overall_pnl_pct"]],
            color=colors,
            line=dict(color="#ffffff", width=1),
        ),
        text=[f"{v:+.1f}%" for v in df["overall_pnl_pct"]],
        textposition="top center",
    ))
    fig.update_layout(
        title="Overall P&L % Since Buy (bubble size = magnitude)",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=420,
        yaxis_title="Overall P&L %",
        xaxis_tickangle=-20,
        margin=dict(l=10, r=10, t=50, b=80),
    )
    fig.add_hline(y=0, line_dash="dash", line_color="#555")
    return fig


def _chart_fii_dii_gauge(fii_dii):
    """Gauge showing FII net flow sentiment."""
    fii_net = fii_dii.get("fii_net")
    if fii_net is None:
        return None
    clamp = max(-5000, min(5000, fii_net))
    color = "#00ff88" if fii_net >= 0 else "#ff5252"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=fii_net,
        delta={"reference": 0, "increasing": {"color": "#00ff88"}, "decreasing": {"color": "#ff5252"}},
        number={"suffix": " Cr", "font": {"color": color}},
        title={"text": "FII Net Flow Today (₹ Cr)", "font": {"color": "#00d4ff"}},
        gauge={
            "axis": {"range": [-5000, 5000], "tickcolor": "#ffffff"},
            "bar": {"color": color},
            "bgcolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [-5000, -1000], "color": "rgba(255,82,82,0.25)"},
                {"range": [-1000, 1000],  "color": "rgba(255,193,7,0.15)"},
                {"range": [1000, 5000],   "color": "rgba(0,255,136,0.25)"},
            ],
            "threshold": {"line": {"color": "#ffffff", "width": 3}, "value": clamp},
        },
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        height=300,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


# ═════════════════════════════════════════════════════════════════════════════
# MAIN STREAMLIT PAGE
# ═════════════════════════════════════════════════════════════════════════════

def show_explain_my_loss():
    """Full Streamlit page for the AI Loss Explainer feature."""
    import streamlit as st

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#1a1a2e,#0f3460);
                padding:2rem;border-radius:16px;border:1px solid #00d4ff;
                margin-bottom:1.5rem;'>
        <h1 style='color:#00d4ff;margin:0;text-align:center;'>
            🧠 AI Finance Coach — Explain My Portfolio
        </h1>
        <p style='color:#e0e0e0;margin:0.6rem 0 0 0;text-align:center;font-size:1.05rem;'>
            Real-time AI analysis of why your portfolio moved today —
            with live NSE data, FII/DII flows, sector performance & news
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Language toggle ───────────────────────────────────────────────────────
    col_lang, col_refresh = st.columns([3, 1])
    with col_lang:
        language = st.radio(
            "🌐 Response Language",
            ["English", "Hindi"],
            horizontal=True,
            help="Choose the language for the AI explanation"
        )
    with col_refresh:
        if st.button("🔄 Refresh All Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.caption(f"🕐 Data as of: {datetime.now().strftime('%d %b %Y  %H:%M:%S IST')}")
    st.markdown("---")

    # ── Check portfolio ───────────────────────────────────────────────────────
    holdings_raw = _fetch_portfolio_from_db()

    if holdings_raw.empty:
        st.warning(
            "⚠️ Your portfolio is empty. "
            "Go to **🛡️ Portfolio & Risk Management → Add Holdings** first, "
            "then come back here for your AI explanation."
        )
        st.info(
            "💡 Once you add stocks, this page will:\n"
            "- Fetch today's live prices for every holding\n"
            "- Pull real FII/DII data from NSE\n"
            "- Analyse sector performance\n"
            "- Read latest market news\n"
            "- Ask Groq Llama 3.3 to explain everything in plain language"
        )
        return

    # ── Fetch all live data ───────────────────────────────────────────────────
    with st.spinner("📡 Fetching live prices for your holdings..."):
        price_data = _fetch_today_prices(holdings_raw)

    if not price_data:
        st.error(
            "❌ Could not fetch live prices. "
            "Check your internet connection or try again after market hours."
        )
        return

    with st.spinner("📡 Fetching FII/DII data from NSE..."):
        fii_dii = _fetch_fii_dii()

    with st.spinner("📡 Fetching live sector performance..."):
        sector_perf = _fetch_sector_performance()

    with st.spinner("📡 Fetching NIFTY 50..."):
        nifty_chg, nifty_val = _fetch_nifty_today()

    with st.spinner("📡 Fetching latest market news..."):
        headlines = _fetch_news_headlines()

    # ── Portfolio summary KPIs ────────────────────────────────────────────────
    total_invested  = sum(p["invested"]   for p in price_data)
    total_curr      = sum(p["curr_val"]   for p in price_data)
    total_today_pnl = sum(p["today_pnl"] for p in price_data)
    port_today_pct  = (total_today_pnl / total_curr * 100) if total_curr else 0
    overall_pnl     = total_curr - total_invested
    overall_pnl_pct = (overall_pnl / total_invested * 100) if total_invested else 0

    pnl_color_today   = "#00ff88" if total_today_pnl >= 0 else "#ff5252"
    pnl_color_overall = "#00ff88" if overall_pnl >= 0 else "#ff5252"
    nifty_color       = "#00ff88" if (nifty_chg or 0) >= 0 else "#ff5252"

    st.markdown("### 📊 Live Portfolio Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)

    def _kpi(col, label, value, sub, color):
        col.markdown(
            f"<div style='background:rgba(0,212,255,0.07);padding:1rem;"
            f"border-radius:12px;border-left:4px solid {color};text-align:center;'>"
            f"<p style='color:#aaa;margin:0;font-size:0.8rem;'>{label}</p>"
            f"<h3 style='color:{color};margin:0.3rem 0;'>{value}</h3>"
            f"<p style='color:#ccc;margin:0;font-size:0.75rem;'>{sub}</p></div>",
            unsafe_allow_html=True
        )

    _kpi(c1, "Today's P&L",    f"₹{total_today_pnl:+,.0f}", f"{port_today_pct:+.2f}%", pnl_color_today)
    _kpi(c2, "Overall P&L",    f"₹{overall_pnl:+,.0f}",     f"{overall_pnl_pct:+.2f}%", pnl_color_overall)
    _kpi(c3, "Current Value",  f"₹{total_curr:,.0f}",        f"Invested ₹{total_invested:,.0f}", "#00d4ff")
    _kpi(c4, "NIFTY 50",
         f"{nifty_chg:+.2f}%" if nifty_chg is not None else "N/A",
         f"{nifty_val:,.0f}" if nifty_val else "",
         nifty_color)
    fii_net = fii_dii.get("fii_net")
    _kpi(c5, "FII Net Flow",
         f"₹{fii_net:+,.0f} Cr" if fii_net is not None else "N/A",
         fii_dii.get("date", ""),
         "#00ff88" if (fii_net or 0) >= 0 else "#ff5252")

    st.markdown("---")

    # ── Charts row 1 ─────────────────────────────────────────────────────────
    st.markdown("### 📈 Visual Breakdown")
    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(_chart_today_pnl(price_data), use_container_width=True)
    with ch2:
        st.plotly_chart(_chart_today_pct(price_data), use_container_width=True)

    # ── Charts row 2 ─────────────────────────────────────────────────────────
    ch3, ch4 = st.columns(2)
    with ch3:
        st.plotly_chart(_chart_portfolio_allocation(price_data), use_container_width=True)
    with ch4:
        st.plotly_chart(_chart_overall_pnl(price_data), use_container_width=True)

    # ── Charts row 3 ─────────────────────────────────────────────────────────
    ch5, ch6 = st.columns(2)
    with ch5:
        sector_fig = _chart_sector_heatmap(sector_perf)
        if sector_fig:
            st.plotly_chart(sector_fig, use_container_width=True)
        else:
            st.info("Sector data unavailable right now.")
    with ch6:
        fii_fig = _chart_fii_dii_gauge(fii_dii)
        if fii_fig:
            st.plotly_chart(fii_fig, use_container_width=True)
        else:
            st.info("FII/DII data unavailable right now.")

    st.markdown("---")

    # ── Holdings detail table ─────────────────────────────────────────────────
    with st.expander("📋 Full Holdings Detail (Live Prices)", expanded=False):
        df_display = pd.DataFrame(price_data)[[
            "company_name", "sector", "quantity", "buy_price",
            "prev_close", "today_close", "today_chg_pct",
            "today_pnl", "overall_pnl_pct", "curr_val"
        ]].rename(columns={
            "company_name":   "Stock",
            "sector":         "Sector",
            "quantity":       "Qty",
            "buy_price":      "Buy ₹",
            "prev_close":     "Prev Close ₹",
            "today_close":    "Today ₹",
            "today_chg_pct":  "Today %",
            "today_pnl":      "Today P&L ₹",
            "overall_pnl_pct":"Overall %",
            "curr_val":       "Curr Value ₹",
        })
        # Round for display
        for col in ["Buy ₹", "Prev Close ₹", "Today ₹"]:
            df_display[col] = df_display[col].round(2)
        for col in ["Today %", "Overall %"]:
            df_display[col] = df_display[col].round(2)
        for col in ["Today P&L ₹", "Curr Value ₹"]:
            df_display[col] = df_display[col].round(0).astype(int)

        st.dataframe(df_display, use_container_width=True, height=300)

    # ── News headlines ────────────────────────────────────────────────────────
    with st.expander("📰 Live Market News Used for Analysis", expanded=False):
        if headlines:
            for i, h in enumerate(headlines, 1):
                st.markdown(f"**{i}.** {h}")
        else:
            st.info("No headlines fetched.")

    st.markdown("---")

    # ── AI Explanation ────────────────────────────────────────────────────────
    st.markdown("### 🧠 AI Explanation")

    groq_key = os.environ.get("GROQ_API_KEY", "")

    if not groq_key:
        st.error(
            "❌ GROQ_API_KEY not found in your .env file. "
            "Add it to get the AI explanation. "
            "Get a free key at https://console.groq.com"
        )
        return

    explain_btn = st.button(
        f"🤖 Explain My Portfolio in {language}",
        type="primary",
        use_container_width=True,
    )

    if explain_btn:
        with st.spinner(f"🧠 Groq Llama 3.3 is analysing your portfolio in {language}..."):
            prompt = _build_groq_prompt(
                price_data, fii_dii, sector_perf,
                nifty_chg, nifty_val, headlines, language
            )
            explanation = _call_groq(prompt, groq_key)

        if explanation:
            # Determine overall sentiment for card colour
            card_color = "#ff5252" if total_today_pnl < 0 else "#00ff88"
            emoji = "📉" if total_today_pnl < 0 else "📈"

            st.markdown(
                f"<div style='background:rgba(0,0,0,0.35);padding:2rem;"
                f"border-radius:16px;border-left:6px solid {card_color};"
                f"margin-top:1rem;'>"
                f"<h3 style='color:{card_color};margin:0 0 1rem 0;'>"
                f"{emoji} AI Analysis — {datetime.now().strftime('%d %b %Y %H:%M')}</h3>"
                f"<div style='color:#f0f0f0;line-height:1.8;white-space:pre-wrap;'>"
                f"{explanation}</div></div>",
                unsafe_allow_html=True
            )

            # ── Sell / Hold signal card ───────────────────────────────────────
            sell_keywords = ["sell", "exit", "बेचें", "निकलें"]
            hold_keywords = ["hold", "stay", "रखें", "बने रहें", "घबराएं नहीं"]
            exp_lower = explanation.lower()
            if any(k in exp_lower for k in sell_keywords):
                signal, sig_col, sig_emoji = "CONSIDER SELLING", "#ff5252", "🔴"
            elif any(k in exp_lower for k in hold_keywords):
                signal, sig_col, sig_emoji = "HOLD YOUR POSITION", "#00ff88", "🟢"
            else:
                signal, sig_col, sig_emoji = "REVIEW CAREFULLY", "#ffc107", "🟡"

            st.markdown(
                f"<div style='background:rgba(0,0,0,0.3);padding:1.5rem;"
                f"border-radius:12px;border:2px solid {sig_col};"
                f"text-align:center;margin-top:1.5rem;'>"
                f"<h2 style='color:{sig_col};margin:0;'>{sig_emoji} {signal}</h2>"
                f"<p style='color:#ccc;margin:0.5rem 0 0 0;'>"
                f"Based on today's live data + AI analysis</p></div>",
                unsafe_allow_html=True
            )
        else:
            st.error(
                "❌ Groq API did not return a response. "
                "Check your API key or try again in a moment."
            )
    else:
        st.info(
            f"👆 Click the button above to get your AI explanation in {language}. "
            "All analysis uses 100% real-time data — no dummy numbers."
        )
