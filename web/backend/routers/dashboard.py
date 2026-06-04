"""Dashboard router — live NIFTY, SENSEX, gainers, losers, market breadth.
Uses yfinance fast_info for real-time prices (not delayed daily close).
"""
from fastapi import APIRouter
import yfinance as yf
import math
from datetime import datetime

router = APIRouter()

INDIAN_STOCKS = {
    "HDFCBANK.NS":  "HDFC Bank",
    "ICICIBANK.NS": "ICICI Bank",
    "KOTAKBANK.NS": "Kotak Bank",
    "SBIN.NS":      "State Bank",
    "AXISBANK.NS":  "Axis Bank",
    "TCS.NS":       "TCS",
    "INFY.NS":      "Infosys",
    "WIPRO.NS":     "Wipro",
    "HCLTECH.NS":   "HCL Tech",
    "RELIANCE.NS":  "Reliance",
    "HINDUNILVR.NS":"HUL",
    "ITC.NS":       "ITC",
    "MARUTI.NS":    "Maruti",
    "M&M.NS":       "Mahindra",
    "SUNPHARMA.NS": "Sun Pharma",
    "DRREDDY.NS":   "Dr Reddy",
    "BAJFINANCE.NS":"Bajaj Finance",
    "LT.NS":        "L&T",
    "BHARTIARTL.NS":"Airtel",
    "TITAN.NS":     "Titan",
}


def _safe(v, default=0.0):
    try:
        f = float(v)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except Exception:
        return default


def _live_price(ticker_obj):
    """Get live price using fast_info (real-time), fallback to daily close."""
    try:
        p = ticker_obj.fast_info.last_price
        if p and not math.isnan(float(p)):
            return float(p)
    except Exception:
        pass
    try:
        h = ticker_obj.history(period="5d")
        closes = h["Close"].dropna()
        if not closes.empty:
            return float(closes.iloc[-1])
    except Exception:
        pass
    return None


def _prev_close(ticker_obj):
    """Get previous day's close using fast_info."""
    try:
        p = ticker_obj.fast_info.previous_close
        if p and not math.isnan(float(p)):
            return float(p)
    except Exception:
        pass
    try:
        h = ticker_obj.history(period="5d")
        closes = h["Close"].dropna()
        if len(closes) >= 2:
            return float(closes.iloc[-2])
    except Exception:
        pass
    return None


def _index(symbol):
    try:
        t     = yf.Ticker(symbol)
        price = _live_price(t)
        prev  = _prev_close(t)
        if price is None or prev is None or prev == 0:
            return None
        chg_pts = price - prev
        chg_pct = (chg_pts / prev) * 100
        return {
            "value":      round(price, 2),
            "change_pct": round(_safe(chg_pct), 2),
            "change_pts": round(_safe(chg_pts), 2),
        }
    except Exception:
        return None


@router.get("/indices")
def get_indices():
    nifty  = _index("^NSEI")
    sensex = _index("^BSESN")
    return {
        "nifty":  nifty  or {"value": 0, "change_pct": 0, "change_pts": 0},
        "sensex": sensex or {"value": 0, "change_pct": 0, "change_pts": 0},
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/movers")
def get_movers():
    gainers, losers = [], []
    for sym, name in INDIAN_STOCKS.items():
        try:
            t     = yf.Ticker(sym)
            price = _live_price(t)
            prev  = _prev_close(t)
            if price is None or prev is None or prev == 0:
                continue
            chg = _safe((price - prev) / prev * 100)
            item = {
                "symbol":     sym.replace(".NS", ""),
                "name":       name,
                "price":      round(price, 2),
                "change_pct": round(chg, 2),
            }
            if chg > 0:
                gainers.append(item)
            else:
                losers.append(item)
        except Exception:
            continue
    gainers = sorted(gainers, key=lambda x: x["change_pct"], reverse=True)[:5]
    losers  = sorted(losers,  key=lambda x: x["change_pct"])[:5]
    return {"gainers": gainers, "losers": losers, "timestamp": datetime.now().isoformat()}


@router.get("/breadth")
def get_breadth():
    advancing = declining = unchanged = 0
    for sym in INDIAN_STOCKS:
        try:
            t     = yf.Ticker(sym)
            price = _live_price(t)
            prev  = _prev_close(t)
            if price is None or prev is None or prev == 0:
                continue
            chg = (price - prev) / prev * 100
            if chg > 0.05:    advancing += 1
            elif chg < -0.05: declining += 1
            else:              unchanged += 1
        except Exception:
            continue
    total = advancing + declining + unchanged or 1
    return {
        "advancing": advancing, "declining": declining, "unchanged": unchanged,
        "total":     total,
        "ad_ratio":  round(advancing / max(declining, 1), 2),
        "strength":  round(advancing / total * 100, 1),
    }

@router.get("/overview")
def get_overview():
    """Combined overview endpoint for dashboard."""
    nifty  = _index("^NSEI")
    sensex = _index("^BSESN")
    
    # Get top gainers and losers
    gainers, losers = [], []
    for sym, name in list(INDIAN_STOCKS.items())[:10]:
        try:
            t     = yf.Ticker(sym)
            price = _live_price(t)
            prev  = _prev_close(t)
            if price is None or prev is None or prev == 0:
                continue
            chg = _safe((price - prev) / prev * 100)
            item = {
                "symbol":     sym.replace(".NS", ""),
                "name":       name,
                "price":      round(price, 2),
                "change_pct": round(chg, 2),
            }
            if chg > 0:
                gainers.append(item)
            else:
                losers.append(item)
        except Exception:
            continue
    
    gainers = sorted(gainers, key=lambda x: x["change_pct"], reverse=True)[:3]
    losers  = sorted(losers,  key=lambda x: x["change_pct"])[:3]
    
    # Market breadth
    advancing = declining = unchanged = 0
    for sym in INDIAN_STOCKS:
        try:
            t     = yf.Ticker(sym)
            price = _live_price(t)
            prev  = _prev_close(t)
            if price is None or prev is None or prev == 0:
                continue
            chg = (price - prev) / prev * 100
            if chg > 0.05:    advancing += 1
            elif chg < -0.05: declining += 1
            else:              unchanged += 1
        except Exception:
            continue
    
    total = advancing + declining + unchanged or 1
    
    return {
        "indices": {
            "nifty":  nifty  or {"value": 0, "change_pct": 0, "change_pts": 0},
            "sensex": sensex or {"value": 0, "change_pct": 0, "change_pts": 0},
        },
        "movers": {
            "gainers": gainers,
            "losers": losers,
        },
        "breadth": {
            "advancing": advancing,
            "declining": declining,
            "unchanged": unchanged,
            "total": total,
            "ad_ratio": round(advancing / max(declining, 1), 2),
            "strength": round(advancing / total * 100, 1),
        },
        "timestamp": datetime.now().isoformat(),
    }
