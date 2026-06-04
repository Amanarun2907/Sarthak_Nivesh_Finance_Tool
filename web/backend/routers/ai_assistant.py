"""AI Assistant + AI Finance Coach router — Groq Llama 3.3 70B."""
from fastapi import APIRouter, Body
import os, requests, yfinance as yf, feedparser, re, numpy as np
import sqlite3
from datetime import datetime
from pathlib import Path

router = APIRouter()
_DB = Path(__file__).resolve().parents[3] / "data" / "sarthak_nivesh.db"
_HDR = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com/"}

SECTOR_TICKERS = {
    "Banking":["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS"],
    "IT":["TCS.NS","INFY.NS","WIPRO.NS"],
    "Pharma":["SUNPHARMA.NS","DRREDDY.NS"],
    "Auto":["MARUTI.NS","TATAMOTORS.NS"],
    "Energy":["RELIANCE.NS","ONGC.NS"],
    "FMCG":["HINDUNILVR.NS","ITC.NS"],
}

def _groq(prompt, system, max_tokens=700):
    key = os.environ.get("GROQ_API_KEY","")
    if not key: return None
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Content-Type":"application/json","Authorization":f"Bearer {key}"},
            json={"model":"llama-3.3-70b-versatile","temperature":0.6,"max_tokens":max_tokens,
                  "messages":[{"role":"system","content":system},{"role":"user","content":prompt}]},
            timeout=40)
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
    return None

def _n(v):
    try:
        m = re.findall(r"-?\d+\.?\d*", str(v).replace(",",""))
        return float(m[0]) if m else 0.0
    except Exception: return 0.0

def _fii_dii():
    try:
        sess = requests.Session(); sess.headers.update(_HDR)
        r = sess.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=12)
        if r.status_code == 200:
            data = r.json()
            fii = next((x for x in data if "FII" in x.get("category","").upper()), None)
            dii = next((x for x in data if "DII" in x.get("category","").upper()), None)
            if fii or dii:
                return {"fii_net": _n((fii or {}).get("netValue",0)),
                        "dii_net": _n((dii or {}).get("netValue",0)),
                        "date": (fii or dii or {}).get("date",""), "source":"NSE Live"}
    except Exception: pass
    return {"fii_net": None, "dii_net": None, "source":"Unavailable"}

def _sector_perf():
    perf = {}
    for s, tickers in SECTOR_TICKERS.items():
        changes = []
        for t in tickers:
            try:
                hist = yf.Ticker(t).history(period="2d")
                if len(hist) >= 2:
                    changes.append(float((hist["Close"].iloc[-1]-hist["Close"].iloc[-2])/hist["Close"].iloc[-2]*100))
            except Exception: pass
        if changes: perf[s] = round(float(np.mean(changes)),2)
    return perf

def _news():
    try:
        feed = feedparser.parse("https://news.google.com/rss/search?q=indian+stock+market+NSE&hl=en-IN&gl=IN&ceid=IN:en")
        return [e.get("title","") for e in feed.entries[:8]]
    except Exception: return []

def _nifty():
    try:
        hist = yf.Ticker("^NSEI").history(period="2d")
        if len(hist) >= 2:
            chg = float((hist["Close"].iloc[-1]-hist["Close"].iloc[-2])/hist["Close"].iloc[-2]*100)
            return round(chg,2), float(hist["Close"].iloc[-1])
    except Exception: pass
    return None, None

def _portfolio():
    try:
        conn = sqlite3.connect(_DB)
        rows = conn.execute(
            "SELECT symbol,company_name,quantity,buy_price,sector FROM portfolio_holdings WHERE user_id='default'"
        ).fetchall()
        conn.close()
        result = []
        for sym, name, qty, bp, sec in rows:
            tsym = sym if sym.endswith(".NS") else sym+".NS"
            try:
                hist = yf.Ticker(tsym).history(period="5d")
                if hist.empty or len(hist) < 2: continue
                cp = float(hist["Close"].iloc[-1]); pp = float(hist["Close"].iloc[-2])
                result.append({
                    "symbol":sym,"company_name":name,"sector":sec,
                    "quantity":qty,"buy_price":bp,"today_close":round(cp,2),
                    "prev_close":round(pp,2),
                    "today_chg_pct":round((cp-pp)/pp*100,2),
                    "today_pnl":round((cp-pp)*qty,2),
                    "invested":round(qty*bp,2),"curr_val":round(qty*cp,2),
                    "overall_pnl_pct":round((cp-bp)/bp*100,2) if bp else 0,
                })
            except Exception: continue
        return result
    except Exception: return []

@router.post("/chat")
def chat(data: dict = Body(...)):
    question = data.get("question","")
    if not question: return {"error": "No question provided"}
    system = ("You are an expert Indian stock market investment advisor. "
              "Use only the data provided. Be concise, warm, and actionable. "
              "Always mention risks. Focus on Indian markets.")
    answer = _groq(question, system, max_tokens=500)
    return {"answer": answer or "Groq API key not configured. Add GROQ_API_KEY to .env",
            "timestamp": datetime.now().isoformat()}

@router.get("/quick_actions")
def quick_actions():
    """Return quick action suggestions based on current market conditions."""
    nifty_chg, nifty_val = _nifty()
    fii_dii = _fii_dii()
    
    actions = []
    
    # Market-based suggestions
    if nifty_chg and nifty_chg < -1.5:
        actions.append({
            "title": "Market Correction Opportunity",
            "description": "NIFTY down significantly. Consider quality stocks at discount.",
            "action": "Review Watchlist",
            "priority": "high"
        })
    elif nifty_chg and nifty_chg > 1.5:
        actions.append({
            "title": "Strong Market Rally",
            "description": "Consider booking partial profits in momentum stocks.",
            "action": "Review Portfolio",
            "priority": "medium"
        })
    
    # FII/DII based suggestions
    if fii_dii.get("fii_net") and fii_dii["fii_net"] > 1000:
        actions.append({
            "title": "Strong FII Inflows",
            "description": f"FII buying ₹{fii_dii['fii_net']:+,.0f}Cr. Positive for large caps.",
            "action": "Check Large Cap Stocks",
            "priority": "high"
        })
    elif fii_dii.get("fii_net") and fii_dii["fii_net"] < -1000:
        actions.append({
            "title": "FII Selling Pressure",
            "description": f"FII selling ₹{fii_dii['fii_net']:+,.0f}Cr. Stay cautious.",
            "action": "Review Stop Losses",
            "priority": "high"
        })
    
    # Default actions
    if not actions:
        actions.extend([
            {
                "title": "Check Your Portfolio",
                "description": "Review today's performance and rebalance if needed.",
                "action": "View Portfolio",
                "priority": "medium"
            },
            {
                "title": "Explore IPO Opportunities",
                "description": "Analyze upcoming IPOs with multi-agent AI.",
                "action": "IPO Analysis",
                "priority": "low"
            }
        ])
    
    return {
        "actions": actions[:4],  # Max 4 actions
        "market_summary": {
            "nifty_change": nifty_chg,
            "nifty_value": nifty_val,
            "fii_net": fii_dii.get("fii_net"),
            "dii_net": fii_dii.get("dii_net")
        },
        "timestamp": datetime.now().isoformat()
    }

@router.post("/explain_loss")
def explain_loss(data: dict = Body(...)):
    language = data.get("language","English")
    holdings = _portfolio()
    if not holdings:
        return {"error": "Portfolio is empty. Add stocks first."}
    fii_dii   = _fii_dii()
    sector_p  = _sector_perf()
    nifty_chg, nifty_val = _nifty()
    headlines = _news()

    total_inv  = sum(h["invested"] for h in holdings)
    total_curr = sum(h["curr_val"] for h in holdings)
    today_pnl  = sum(h["today_pnl"] for h in holdings)
    port_pct   = (today_pnl/total_curr*100) if total_curr else 0

    holdings_txt = "\n".join([
        f"  • {h['company_name']} ({h['symbol']}) | Sector:{h['sector']} | "
        f"Qty:{int(h['quantity'])} | Buy:₹{h['buy_price']:.2f} | "
        f"Today:₹{h['today_close']:.2f} | Change:{h['today_chg_pct']:+.2f}% | "
        f"Today P&L:₹{h['today_pnl']:+,.0f} | Overall:{h['overall_pnl_pct']:+.2f}%"
        for h in holdings])
    fii_txt = (f"FII Net:₹{fii_dii['fii_net']:+,.0f}Cr | DII Net:₹{fii_dii['dii_net']:+,.0f}Cr"
               if fii_dii.get("fii_net") is not None else "FII/DII unavailable")
    sector_txt = "\n".join([f"  • {s}:{v:+.2f}%" for s,v in sector_p.items()])
    news_txt   = "\n".join([f"  {i+1}. {h}" for i,h in enumerate(headlines)])
    nifty_txt  = f"NIFTY 50:{nifty_chg:+.2f}% | Level:{nifty_val:,.0f}" if nifty_chg else "NIFTY unavailable"
    lang_inst  = ("Respond ENTIRELY in Hindi (Devanagari script)." if language=="Hindi"
                  else "Respond in simple English for a first-time investor.")

    prompt = f"""
{lang_inst}
Use ONLY the real-time data below. Do NOT invent numbers.

=== LIVE PORTFOLIO ===
Today Change: {port_pct:+.2f}% (₹{today_pnl:+,.0f})
Invested: ₹{total_inv:,.0f} | Current: ₹{total_curr:,.0f}
{holdings_txt}

=== MARKET CONTEXT ===
{nifty_txt}
{fii_txt}
Sectors:
{sector_txt}
News:
{news_txt}

Write 4 sections:
1. What happened today (2-3 sentences, cite specific stocks + FII/DII)
2. Main culprits (top 2-3 stocks with exact % from data)
3. SELL or HOLD recommendation with reasoning
4. One calming insight (long-term perspective)
Under 300 words. Be warm and reassuring.
""".strip()

    system = ("You are a compassionate Indian stock market advisor. "
              "Always use exact numbers from the data. Never fabricate. Be warm.")
    answer = _groq(prompt, system, max_tokens=700)
    return {
        "explanation": answer or "Groq API key not configured.",
        "portfolio_summary": {
            "total_invested": round(total_inv,2),
            "total_current":  round(total_curr,2),
            "today_pnl":      round(today_pnl,2),
            "today_pct":      round(port_pct,2),
        },
        "holdings":    holdings,
        "fii_dii":     fii_dii,
        "sector_perf": sector_p,
        "nifty_chg":   nifty_chg,
        "nifty_val":   nifty_val,
        "headlines":   headlines,
        "timestamp":   datetime.now().isoformat(),
    }
