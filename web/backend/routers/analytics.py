"""Advanced Analytics router — uses fast_info for live prices."""
from fastapi import APIRouter
import yfinance as yf
import numpy as np
import pandas as pd
import math
from datetime import datetime

router = APIRouter()

SECTOR_STOCKS = {
    "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"],
    "IT":      ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS"],
    "Auto":    ["MARUTI.NS","M&M.NS","BAJAJ-AUTO.NS"],
    "Pharma":  ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS","DIVISLAB.NS"],
    "FMCG":    ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS","BRITANNIA.NS"],
    "Energy":  ["RELIANCE.NS","ONGC.NS","BPCL.NS","IOC.NS"],
    "Telecom": ["BHARTIARTL.NS"],
    "Metals":  ["TATASTEEL.NS","HINDALCO.NS","JSWSTEEL.NS"],
}

CORR_STOCKS = {
    "RELIANCE":   "RELIANCE.NS",
    "TCS":        "TCS.NS",
    "HDFCBANK":   "HDFCBANK.NS",
    "INFY":       "INFY.NS",
    "ICICIBANK":  "ICICIBANK.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "ITC":        "ITC.NS",
    "SBIN":       "SBIN.NS",
}


def _live_chg(sym: str):
    """Return % change using fast_info live price vs previous close."""
    try:
        t     = yf.Ticker(sym)
        price = float(t.fast_info.last_price)
        prev  = float(t.fast_info.previous_close)
        if math.isnan(price) or math.isnan(prev) or prev == 0:
            raise ValueError("nan")
        return (price - prev) / prev * 100
    except Exception:
        pass
    # Fallback: daily history
    try:
        h = yf.Ticker(sym).history(period="5d")
        c = h["Close"].dropna()
        if len(c) >= 2:
            return float((c.iloc[-1] - c.iloc[-2]) / c.iloc[-2] * 100)
    except Exception:
        pass
    return None


@router.get("/sector_heatmap")
def sector_heatmap():
    result = {}
    for sector, tickers in SECTOR_STOCKS.items():
        changes = []
        for sym in tickers:
            chg = _live_chg(sym)
            if chg is not None and not math.isnan(chg):
                changes.append(chg)
        if changes:
            result[sector] = round(float(np.mean(changes)), 2)
    return {"sectors": result, "timestamp": datetime.now().isoformat()}


@router.get("/correlation")
def correlation(period: str = "3mo"):
    data = {}
    for name, sym in CORR_STOCKS.items():
        try:
            hist = yf.Ticker(sym).history(period=period)
            if not hist.empty:
                closes = hist["Close"].dropna()
                if len(closes) > 5:
                    data[name] = closes.pct_change().dropna()
        except Exception:
            pass
    if len(data) < 2:
        # Fallback to 3mo if 1mo has insufficient data
        for name, sym in CORR_STOCKS.items():
            if name in data:
                continue
            try:
                hist = yf.Ticker(sym).history(period="3mo")
                if not hist.empty:
                    closes = hist["Close"].dropna()
                    if len(closes) > 5:
                        data[name] = closes.pct_change().dropna()
            except Exception:
                pass
    if len(data) < 2:
        return {"error": "Insufficient data", "stocks": [], "matrix": []}
    df   = pd.DataFrame(data).dropna()
    if df.empty or len(df) < 2:
        return {"error": "Insufficient data", "stocks": [], "matrix": []}
    corr = df.corr().round(3)
    matrix = [[0.0 if (math.isnan(v) or math.isinf(v)) else v for v in row]
              for row in corr.values.tolist()]
    return {
        "stocks":    corr.columns.tolist(),
        "matrix":    matrix,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/volume_analysis")
def volume_analysis():
    result = []
    for name, sym in CORR_STOCKS.items():
        try:
            t     = yf.Ticker(sym)
            price = float(t.fast_info.last_price)
            prev  = float(t.fast_info.previous_close)
            hist  = t.history(period="5d")
            vols  = hist["Volume"].dropna()
            if vols.empty or prev == 0:
                continue
            cv  = float(vols.iloc[-1])
            av  = float(vols.mean())
            chg = (price - prev) / prev * 100 if prev > 0 else 0
            result.append({
                "symbol":       name,
                "current_vol":  int(cv),
                "avg_vol":      int(av),
                "vol_ratio":    round(cv / av, 2) if av > 0 else 1.0,
                "price_change": round(chg, 2),
                "alert":        "High" if cv / av > 1.5 else "Normal",
            })
        except Exception:
            continue
    return sorted(result, key=lambda x: x["vol_ratio"], reverse=True)


@router.get("/market_breadth")
def market_breadth():
    all_stocks = [s for tickers in SECTOR_STOCKS.values() for s in tickers]
    adv = dec = unch = 0
    for sym in all_stocks:
        chg = _live_chg(sym)
        if chg is None:
            continue
        if chg > 0.05:    adv  += 1
        elif chg < -0.05: dec  += 1
        else:              unch += 1
    total = adv + dec + unch or 1
    ratio = adv / total
    return {
        "advancing": adv, "declining": dec, "unchanged": unch, "total": total,
        "ad_ratio":  round(adv / max(dec, 1), 2),
        "strength":  round(ratio * 100, 1),
        "sentiment": "Bullish" if ratio > 0.6 else "Bearish" if ratio < 0.4 else "Neutral",
    }

# Alias endpoints for frontend compatibility
@router.get("/breadth_gauge")
def breadth_gauge():
    """Alias for market_breadth endpoint."""
    return market_breadth()

@router.get("/volume_intelligence")
def volume_intelligence():
    """Alias for volume_analysis endpoint."""
    return volume_analysis()
