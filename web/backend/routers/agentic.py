"""
Agentic AI Hub — Multi-Agent Investment Intelligence
Uses fast_info for live prices. No TATAMOTORS.NS. Full NaN protection.
"""
from fastapi import APIRouter, Body
import os, requests, yfinance as yf, feedparser, re, math
import numpy as np, pandas as pd
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

router = APIRouter()
_vader = SentimentIntensityAnalyzer()

_HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html, */*",
    "Referer": "https://www.nseindia.com/",
}

# ── Stock universe (TATAMOTORS removed — Yahoo Finance broken) ────────────────
WATCHLIST = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS",
    "LT.NS","AXISBANK.NS","WIPRO.NS","MARUTI.NS","TITAN.NS",
    "BAJFINANCE.NS","SUNPHARMA.NS","TATASTEEL.NS","NTPC.NS","M&M.NS",
]
SECTOR_MAP = {
    "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"],
    "IT":      ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS"],
    "Energy":  ["RELIANCE.NS","ONGC.NS","NTPC.NS"],
    "FMCG":    ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS"],
    "Auto":    ["MARUTI.NS","M&M.NS","BAJAJ-AUTO.NS"],
    "Pharma":  ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"],
    "Metals":  ["TATASTEEL.NS","HINDALCO.NS","JSWSTEEL.NS"],
    "Telecom": ["BHARTIARTL.NS"],
}


def _sf(v, default=0.0):
    """Safe float — returns default for NaN/Inf/None."""
    try:
        f = float(v)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except Exception:
        return default


def _live(sym: str):
    """Get live price and prev close via fast_info."""
    try:
        t     = yf.Ticker(sym)
        price = _sf(t.fast_info.last_price)
        prev  = _sf(t.fast_info.previous_close)
        if price > 0 and prev > 0:
            return price, prev
    except Exception:
        pass
    try:
        h = yf.Ticker(sym).history(period="5d")
        c = h["Close"].dropna()
        if len(c) >= 2:
            return _sf(c.iloc[-1]), _sf(c.iloc[-2])
    except Exception:
        pass
    return None, None


# ── Groq helper ───────────────────────────────────────────────────────────────

def _groq(prompt: str, system: str, max_tokens: int = 600) -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return "⚠️ Add GROQ_API_KEY to .env for AI analysis."
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}"},
            json={"model": "llama-3.3-70b-versatile", "temperature": 0.55,
                  "max_tokens": max_tokens,
                  "messages": [{"role": "system", "content": system},
                                {"role": "user",   "content": prompt}]},
            timeout=40,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
        return f"Groq error {r.status_code}"
    except Exception as e:
        return f"Groq call failed: {e}"


# ── Agent 1: Stock Intelligence ───────────────────────────────────────────────

def agent_stock_intelligence(query: str) -> dict:
    results = []
    for sym in WATCHLIST[:15]:
        try:
            price, prev = _live(sym)
            if price is None or prev is None or prev == 0:
                continue
            chg = (price - prev) / prev * 100
            # RSI from 3mo history
            hist  = yf.Ticker(sym).history(period="3mo")
            close = hist["Close"].dropna()
            rsi   = 50.0
            macd_sig = "HOLD"
            if len(close) >= 20:
                delta = close.diff()
                gain  = delta.clip(lower=0).rolling(14).mean()
                loss  = (-delta.clip(upper=0)).rolling(14).mean()
                rs    = gain / loss.replace(0, np.nan)
                rsi_s = 100 - (100 / (1 + rs))
                rsi   = _sf(rsi_s.dropna().iloc[-1], 50.0)
                ema12 = close.ewm(span=12).mean()
                ema26 = close.ewm(span=26).mean()
                macd  = ema12 - ema26
                sig   = macd.ewm(span=9).mean()
                if _sf(macd.iloc[-1]) > _sf(sig.iloc[-1]):
                    macd_sig = "BUY"
                else:
                    macd_sig = "SELL"
            score = 0
            if rsi < 40: score += 1
            if rsi > 60: score -= 1
            if macd_sig == "BUY": score += 1
            else: score -= 1
            if len(close) >= 50 and price > _sf(close.rolling(50).mean().iloc[-1]):
                score += 1
            else:
                score -= 1
            signal = "BUY" if score >= 2 else "SELL" if score <= -2 else "HOLD"
            results.append({
                "symbol":      sym.replace(".NS", ""),
                "price":       round(price, 2),
                "change_pct":  round(chg, 2),
                "rsi":         round(rsi, 1),
                "macd_signal": macd_sig,
                "signal":      signal,
            })
        except Exception:
            continue

    top_buy  = [r for r in results if r["signal"] == "BUY"][:3]
    top_sell = [r for r in results if r["signal"] == "SELL"][:3]
    data_txt = "\n".join([
        f"  {r['symbol']}: ₹{r['price']} | {r['change_pct']:+.2f}% | RSI {r['rsi']} | {r['signal']}"
        for r in results
    ])
    analysis = _groq(
        f"User query: {query}\n\nLive stock data (fast_info prices):\n{data_txt}\n\n"
        "Provide a sharp 3-4 sentence stock analysis. Name specific stocks with BUY/SELL signals. "
        "Mention RSI levels and what they mean for the investor.",
        "You are a stock market analyst. Be concise, specific, and data-driven.",
        max_tokens=280,
    )
    return {
        "agent":    "Stock Intelligence",
        "icon":     "📊",
        "stocks":   results,
        "top_buy":  top_buy,
        "top_sell": top_sell,
        "analysis": analysis,
        "status":   "complete",
    }


# ── Agent 2: Market Analysis ──────────────────────────────────────────────────

def agent_market_analysis(query: str) -> dict:
    indices = {}
    for name, sym in [("NIFTY 50", "^NSEI"), ("SENSEX", "^BSESN")]:
        price, prev = _live(sym)
        if price and prev and prev > 0:
            indices[name] = {
                "value":      round(price, 2),
                "change_pct": round((price - prev) / prev * 100, 2),
            }

    sector_perf = {}
    for sector, tickers in SECTOR_MAP.items():
        changes = []
        for t in tickers:
            p, pv = _live(t)
            if p and pv and pv > 0:
                changes.append((p - pv) / pv * 100)
        if changes:
            sector_perf[sector] = round(float(np.mean(changes)), 2)

    best  = max(sector_perf, key=sector_perf.get) if sector_perf else "N/A"
    worst = min(sector_perf, key=sector_perf.get) if sector_perf else "N/A"

    idx_txt = "\n".join([f"  {k}: {v['value']:,.0f} ({v['change_pct']:+.2f}%)"
                         for k, v in indices.items()])
    sec_txt = "\n".join([f"  {k}: {v:+.2f}%"
                         for k, v in sorted(sector_perf.items(), key=lambda x: x[1], reverse=True)])
    analysis = _groq(
        f"User query: {query}\n\nLive market data:\n{idx_txt}\n\nSector performance:\n{sec_txt}\n\n"
        "Provide a 3-4 sentence market analysis. Comment on index direction, "
        "best and worst sectors, and overall market mood.",
        "You are a market analyst. Be concise and specific.",
        max_tokens=280,
    )
    return {
        "agent":        "Market Analysis",
        "icon":         "📈",
        "indices":      indices,
        "sector_perf":  sector_perf,
        "best_sector":  best,
        "worst_sector": worst,
        "analysis":     analysis,
        "status":       "complete",
    }


# ── Agent 3: Smart Money ──────────────────────────────────────────────────────

def agent_smart_money(query: str) -> dict:
    def _n(v):
        try:
            m = re.findall(r"-?\d+\.?\d*", str(v).replace(",", ""))
            return float(m[0]) if m else 0.0
        except Exception:
            return 0.0

    fii_net = dii_net = None
    date_str = source = ""
    try:
        sess = requests.Session()
        sess.headers.update(_HDR)
        r = sess.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=15)
        if r.status_code == 200:
            data = r.json()
            fii  = next((x for x in data if "FII" in x.get("category", "").upper()), None)
            dii  = next((x for x in data if "DII" in x.get("category", "").upper()), None)
            if fii or dii:
                fii_net  = _n((fii or {}).get("netValue", 0))
                dii_net  = _n((dii or {}).get("netValue", 0))
                date_str = (fii or dii or {}).get("date", "")
                source   = "NSE Live"
    except Exception as e:
        print(f"FII/DII error: {e}")

    signal = "NEUTRAL"
    if fii_net is not None and dii_net is not None:
        if fii_net > 1000 and dii_net > 1000:    signal = "STRONG BUY"
        elif fii_net > 0 and dii_net > 0:         signal = "BUY"
        elif fii_net < -1000 and dii_net < -1000: signal = "STRONG SELL"
        elif fii_net < 0 and dii_net < 0:         signal = "SELL"

    data_txt = (f"FII Net: ₹{fii_net:+,.0f} Cr | DII Net: ₹{dii_net:+,.0f} Cr | Date: {date_str}"
                if fii_net is not None else "FII/DII data unavailable")
    analysis = _groq(
        f"User query: {query}\n\nInstitutional flow (NSE live):\n{data_txt}\n\n"
        "Provide a 2-3 sentence analysis of what institutions are doing "
        "and what it means for retail investors today.",
        "You are an institutional flow analyst. Be direct and specific.",
        max_tokens=220,
    )
    return {
        "agent":    "Smart Money Tracker",
        "icon":     "🏦",
        "fii_net":  fii_net,
        "dii_net":  dii_net,
        "date":     date_str,
        "source":   source,
        "signal":   signal,
        "analysis": analysis,
        "status":   "complete",
    }


# ── Agent 4: News & Sentiment ─────────────────────────────────────────────────

def agent_news_sentiment(query: str) -> dict:
    articles = []
    feeds = [
        ("https://news.google.com/rss/search?q=indian+stock+market+NSE+BSE&hl=en-IN&gl=IN&ceid=IN:en",
         "Google Finance"),
        ("https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
         "Economic Times"),
    ]
    for url, src in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                title = entry.get("title", "")
                if not title:
                    continue
                score = _vader.polarity_scores(title)["compound"]
                articles.append({
                    "title":     title,
                    "source":    src,
                    "sentiment": "Positive" if score > 0.05 else "Negative" if score < -0.05 else "Neutral",
                    "score":     round(score, 3),
                })
        except Exception:
            pass

    pos = sum(1 for a in articles if a["sentiment"] == "Positive")
    neg = sum(1 for a in articles if a["sentiment"] == "Negative")
    avg = round(float(np.mean([a["score"] for a in articles])), 3) if articles else 0
    overall = "Positive" if avg > 0.05 else "Negative" if avg < -0.05 else "Neutral"

    headlines = "\n".join([f"  [{a['sentiment']}] {a['title'][:70]}" for a in articles[:8]])
    analysis  = _groq(
        f"User query: {query}\n\nLatest market headlines:\n{headlines}\n\n"
        f"Overall sentiment: {overall} (score: {avg})\n\n"
        "Provide a 3-4 sentence news sentiment analysis. What are the key themes? "
        "How does the news sentiment affect investment decisions today?",
        "You are a financial news analyst. Be concise and actionable.",
        max_tokens=280,
    )
    return {
        "agent":    "News & Sentiment",
        "icon":     "📰",
        "articles": articles[:10],
        "positive": pos,
        "negative": neg,
        "neutral":  len(articles) - pos - neg,
        "avg_score":avg,
        "overall":  overall,
        "analysis": analysis,
        "status":   "complete",
    }


# ── Agent 5: Risk Management ──────────────────────────────────────────────────

def agent_risk_management(query: str) -> dict:
    returns_data = {}
    for sym in WATCHLIST[:10]:
        try:
            hist = yf.Ticker(sym).history(period="1y")
            c    = hist["Close"].dropna()
            if len(c) > 50:
                returns_data[sym.replace(".NS", "")] = c.pct_change().dropna()
        except Exception:
            pass

    risk_metrics = {}
    port_vol = port_var = avg_corr = 0.0

    if returns_data:
        df = pd.DataFrame(returns_data).dropna()
        for col in df.columns:
            vol = _sf(df[col].std() * np.sqrt(252) * 100)
            var = _sf(np.percentile(df[col], 5) * 100)
            risk_metrics[col] = {"volatility": round(vol, 2), "var_95": round(var, 2)}

        if len(df.columns) > 1:
            port_ret = df.mean(axis=1)
            port_vol = _sf(port_ret.std() * np.sqrt(252) * 100)
            port_var = _sf(np.percentile(port_ret, 5) * 100)
            corr     = df.corr().values
            upper    = corr[np.triu_indices_from(corr, k=1)]
            avg_corr = _sf(float(np.mean(upper[~np.isnan(upper)])))

    risk_txt = "\n".join([
        f"  {sym}: Volatility {m['volatility']}% | VaR(95%) {m['var_95']}%"
        for sym, m in list(risk_metrics.items())[:8]
    ])
    analysis = _groq(
        f"User query: {query}\n\nRisk metrics:\n{risk_txt}\n"
        f"Portfolio volatility: {port_vol:.1f}% | VaR(95%): {port_var:.2f}% | "
        f"Avg correlation: {avg_corr:.2f}\n\n"
        "Provide a 3-4 sentence risk assessment. Which stocks are most/least risky? "
        "What does the correlation level mean for diversification?",
        "You are a risk management expert. Be specific and actionable.",
        max_tokens=280,
    )
    return {
        "agent":                "Risk Management",
        "icon":                 "🛡️",
        "risk_metrics":         risk_metrics,
        "portfolio_volatility": round(port_vol, 2),
        "portfolio_var":        round(port_var, 2),
        "avg_correlation":      round(avg_corr, 3),
        "analysis":             analysis,
        "status":               "complete",
    }


# ── Agent 6: Advanced Analytics ───────────────────────────────────────────────

def agent_advanced_analytics(query: str) -> dict:
    volume_alerts = []
    for sym in WATCHLIST[:15]:
        try:
            hist  = yf.Ticker(sym).history(period="10d")
            vols  = hist["Volume"].dropna()
            close = hist["Close"].dropna()
            if len(vols) >= 5 and len(close) >= 2:
                cv  = _sf(vols.iloc[-1])
                av  = _sf(vols.mean())
                vr  = cv / av if av > 0 else 1.0
                p, pv = _live(sym)
                chg = (p - pv) / pv * 100 if p and pv and pv > 0 else 0
                if vr > 1.5:
                    volume_alerts.append({
                        "symbol":       sym.replace(".NS", ""),
                        "volume_ratio": round(vr, 2),
                        "price_change": round(chg, 2),
                        "signal":       "Bullish Breakout" if chg > 0 else "Bearish Breakdown",
                    })
        except Exception:
            pass

    sector_momentum = {}
    for sector, tickers in SECTOR_MAP.items():
        week_chg, month_chg = [], []
        for t in tickers:
            try:
                hist  = yf.Ticker(t).history(period="1mo")
                close = hist["Close"].dropna()
                if len(close) >= 5:
                    week_chg.append(_sf((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100))
                if len(close) >= 20:
                    month_chg.append(_sf((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100))
            except Exception:
                pass
        if week_chg:
            sector_momentum[sector] = {
                "week":  round(float(np.mean(week_chg)), 2),
                "month": round(float(np.mean(month_chg)), 2) if month_chg else 0.0,
            }

    alerts_txt = "\n".join([
        f"  {a['symbol']}: {a['volume_ratio']}x volume | {a['price_change']:+.2f}% | {a['signal']}"
        for a in volume_alerts[:6]
    ]) or "  No unusual volume detected"
    momentum_txt = "\n".join([
        f"  {s}: 1W {v['week']:+.2f}% | 1M {v['month']:+.2f}%"
        for s, v in sorted(sector_momentum.items(), key=lambda x: x[1]["week"], reverse=True)
    ])
    analysis = _groq(
        f"User query: {query}\n\nVolume anomalies:\n{alerts_txt}\n\nSector momentum:\n{momentum_txt}\n\n"
        "Provide a 3-4 sentence advanced analytics insight. Which sectors show rotation? "
        "What do the volume anomalies suggest for tomorrow?",
        "You are an advanced market analytics expert. Be specific and actionable.",
        max_tokens=280,
    )
    return {
        "agent":            "Advanced Analytics",
        "icon":             "📈",
        "volume_alerts":    volume_alerts,
        "sector_momentum":  sector_momentum,
        "analysis":         analysis,
        "status":           "complete",
    }


# ── Master Report Agent ───────────────────────────────────────────────────────

def agent_master_report(query: str, agent_results: list) -> str:
    summaries = "\n\n".join([
        f"=== {r['agent']} ===\n{r.get('analysis', 'No analysis')}"
        for r in agent_results
    ])
    prompt = f"""
You are the Master Investment Advisor. You have received reports from {len(agent_results)} specialist agents.
Synthesise them into a comprehensive investment report for this query: "{query}"

Agent Reports:
{summaries}

Write a structured investment report with these EXACT sections:

**1. EXECUTIVE SUMMARY** (2-3 sentences — overall market verdict right now)

**2. TOP 3 INVESTMENT OPPORTUNITIES** (specific stocks/sectors with exact reasoning from the data)

**3. KEY RISKS TO WATCH** (3 specific risks from the agent data above)

**4. SMART MONEY SIGNAL** (what FII/DII are doing and what retail investors should do)

**5. RECOMMENDED ACTION PLAN** (3 concrete, specific steps the investor should take today)

**6. CONFIDENCE LEVEL** (High/Medium/Low with one sentence reason based on data quality)

Be specific, cite actual numbers from the agent reports. Use ₹ for amounts. Under 400 words.
""".strip()
    return _groq(
        prompt,
        "You are a senior investment advisor synthesising multi-agent research. "
        "Be authoritative, cite specific numbers, and give actionable advice.",
        max_tokens=750,
    )


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post("/run")
def run_agents(data: dict = Body(...)):
    query          = data.get("query", "Give me a complete market analysis and investment recommendation")
    agents_to_run  = data.get("agents", ["stock", "market", "smartmoney", "news", "risk", "analytics"])

    agent_map = {
        "stock":      agent_stock_intelligence,
        "market":     agent_market_analysis,
        "smartmoney": agent_smart_money,
        "news":       agent_news_sentiment,
        "risk":       agent_risk_management,
        "analytics":  agent_advanced_analytics,
    }

    results = []
    for agent_id in agents_to_run:
        if agent_id not in agent_map:
            continue
        try:
            result = agent_map[agent_id](query)
            # Sanitize any NaN/Inf floats before returning
            results.append(_sanitize_dict(result))
        except Exception as e:
            results.append({
                "agent":    agent_id,
                "icon":     "⚠️",
                "analysis": f"Agent error: {str(e)[:100]}",
                "status":   "error",
            })

    master = agent_master_report(query, results)

    return {
        "query":         query,
        "agent_results": results,
        "master_report": master,
        "timestamp":     datetime.now().isoformat(),
        "agents_run":    len(results),
    }

# Alias endpoints for compatibility
@router.post("/report")
def run_report(data: dict = Body(...)):
    """Alias for /run endpoint - generates multi-agent report."""
    return run_agents(data)

@router.get("/status")
def get_status():
    """Health check for agentic AI system."""
    return {
        "status": "online",
        "service": "Agentic AI Hub",
        "agents": 6,
        "available_agents": ["stock", "market", "smartmoney", "news", "risk", "analytics"],
        "model": "Groq Llama 3.3 70B",
        "timestamp": datetime.now().isoformat()
    }


def _sanitize_dict(obj):
    """Recursively replace NaN/Inf with 0 in any dict/list."""
    if isinstance(obj, float):
        return 0.0 if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {k: _sanitize_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_dict(v) for v in obj]
    return obj
