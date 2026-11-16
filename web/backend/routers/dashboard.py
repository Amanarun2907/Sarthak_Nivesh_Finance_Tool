"""
Dashboard Router — Sarthak Nivesh (Production Grade)
===================================================
Real-time NIFTY, SENSEX, Market Movers, and Breadth Analytics.
All figures are computed from live Yahoo Finance quotes of the tracked
NIFTY-universe. 60-second in-memory caching; stale cache is served when
the network is down instead of fabricated numbers.
"""

from fastapi import APIRouter
import yfinance as yf
import math
import time
from datetime import datetime
from agentic_runtime import is_network_available

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
    "TECHM.NS":     "Tech Mahindra",
    "RELIANCE.NS":  "Reliance",
    "HINDUNILVR.NS":"HUL",
    "ITC.NS":       "ITC",
    "MARUTI.NS":    "Maruti",
    "M&M.NS":       "Mahindra",
    "SUNPHARMA.NS": "Sun Pharma",
    "DRREDDY.NS":   "Dr Reddy",
    "CIPLA.NS":     "Cipla",
    "BAJFINANCE.NS":"Bajaj Finance",
    "BAJAJAUTO.NS": "Bajaj Auto",
    "LT.NS":        "L&T",
    "BHARTIARTL.NS":"Airtel",
    "TITAN.NS":     "Titan",
    "ASIANPAINT.NS":"Asian Paints",
    "ULTRACEMCO.NS":"UltraTech",
    "NESTLEIND.NS": "Nestle",
    "TATAMOTORS.NS":"Tata Motors",
    "TATASTEEL.NS": "Tata Steel",
    "JSWSTEEL.NS":  "JSW Steel",
    "HINDALCO.NS":  "Hindalco",
    "COALINDIA.NS": "Coal India",
    "ONGC.NS":      "ONGC",
    "NTPC.NS":      "NTPC",
    "POWERGRID.NS": "Power Grid",
    "ADANIENT.NS":  "Adani Ent",
    "ADANIPORTS.NS":"Adani Ports",
    "EICHERMOT.NS": "Eicher",
    "HEROMOTOCO.NS":"Hero Moto",
    "BRITANNIA.NS": "Britannia",
    "APOLLOHOSP.NS":"Apollo Hosp",
    "INDUSINDBK.NS":"IndusInd",
    "SBILIFE.NS":   "SBI Life",
    "HDFCLIFE.NS":  "HDFC Life",
    "BHARATFORG.NS":"Bharat Forge",
    "DMART.NS":     "D-Mart",
    "PIDILITIND.NS":"Pidilite",
    "HAVELLS.NS":   "Havells",
    "ZOMATO.NS":    "Zomato",
    "IRCTC.NS":     "IRCTC",
    "PAYTM.NS":     "Paytm",
    "NYKAA.NS":     "Nykaa",
}

TTL = 60.0
_CACHE = {
    "snap": None,        # full universe snapshot: {sym: {price, change_pct}}
    "snap_ts": 0.0,
    "indices": None,
    "indices_ts": 0.0,
}


def _safe(v, default=0.0):
    try:
        f = float(v)
        return default if (math.isnan(f) or math.isinf(f)) else f
    except Exception:
        return default


def _live_price(ticker_obj):
    try:
        p = ticker_obj.fast_info.last_price
        if p and not math.isnan(float(p)) and float(p) > 0:
            return float(p)
    except Exception:
        pass
    return None


def _prev_close(ticker_obj):
    try:
        p = ticker_obj.fast_info.previous_close
        if p and not math.isnan(float(p)) and float(p) > 0:
            return float(p)
    except Exception:
        pass
    return None


def _index(symbol: str):
    if not is_network_available():
        return {"value": 0.0, "change_pct": 0.0, "change_pts": 0.0, "live": False}
    try:
        t = yf.Ticker(symbol)
        price = _live_price(t)
        prev = _prev_close(t)
        if price and prev and prev > 0:
            chg_pts = price - prev
            chg_pct = (chg_pts / prev) * 100.0
            return {
                "value": round(price, 2),
                "change_pct": round(_safe(chg_pct), 2),
                "change_pts": round(_safe(chg_pts), 2),
                "live": True,
            }
    except Exception:
        pass
    return {"value": 0.0, "change_pct": 0.0, "change_pts": 0.0, "live": False}


def _fetch_universe_snapshot():
    """One bulk download for the whole tracked universe.

    Returns {symbol: {"price": float, "change_pct": float}} computed from the
    last two daily closes (works on trading days, weekends and holidays).
    """
    tickers = list(INDIAN_STOCKS.keys())
    try:
        df = yf.download(
            tickers=tickers,
            period="5d",
            interval="1d",
            group_by="ticker",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
    except Exception:
        return {}

    snap = {}
    for sym in tickers:
        try:
            sub = df[sym] if sym in df.columns.get_level_values(0) else None
            if sub is None:
                continue
            closes = sub["Close"].dropna()
            if len(closes) < 2:
                continue
            prev = float(closes.iloc[-2])
            last = float(closes.iloc[-1])
            if prev <= 0 or last <= 0:
                continue
            snap[sym] = {
                "price": round(last, 2),
                "change_pct": round(_safe((last - prev) / prev * 100.0), 2),
            }
        except Exception:
            continue
    return snap


def _get_snapshot(force=False):
    now = time.time()
    if not force and _CACHE["snap"] and (now - _CACHE["snap_ts"]) < TTL:
        return _CACHE["snap"], True

    if not is_network_available():
        return (_CACHE["snap"] or {}), _CACHE["snap"] is not None

    snap = _fetch_universe_snapshot()
    if snap:
        _CACHE["snap"] = snap
        _CACHE["snap_ts"] = now
        return snap, True
    return (_CACHE["snap"] or {}), False


@router.get("/indices")
def get_indices():
    """Fetch live NIFTY 50 and SENSEX metrics."""
    now = time.time()
    if _CACHE["indices"] and (now - _CACHE["indices_ts"]) < TTL:
        return _CACHE["indices"]

    res = {
        "nifty":  _index("^NSEI"),
        "sensex": _index("^BSESN"),
        "timestamp": datetime.now().isoformat(),
    }
    _CACHE["indices"] = res
    _CACHE["indices_ts"] = now
    return res


@router.get("/movers")
def get_movers():
    """Top 5 gainers and losers across the tracked universe (real data only)."""
    snap, fresh = _get_snapshot()
    items = [
        {
            "symbol": sym.replace(".NS", ""),
            "name": INDIAN_STOCKS[sym],
            "price": v["price"],
            "change_pct": v["change_pct"],
        }
        for sym, v in snap.items()
    ]
    gainers = sorted((i for i in items if i["change_pct"] > 0),
                     key=lambda x: x["change_pct"], reverse=True)[:5]
    losers = sorted((i for i in items if i["change_pct"] < 0),
                    key=lambda x: x["change_pct"])[:5]
    return {
        "gainers": gainers,
        "losers": losers,
        "live": fresh,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/breadth")
def get_breadth():
    """Real market breadth computed from the tracked universe."""
    snap, fresh = _get_snapshot()
    changes = [v["change_pct"] for v in snap.values()]
    advancing = sum(1 for c in changes if c > 0)
    declining = sum(1 for c in changes if c < 0)
    unchanged = sum(1 for c in changes if c == 0)
    total = len(changes)
    return {
        "advancing": advancing,
        "declining": declining,
        "unchanged": unchanged,
        "total": total,
        "ad_ratio": round(advancing / declining, 2) if declining > 0 else round(float(advancing), 2),
        "strength": round((advancing / total) * 100.0, 1) if total > 0 else 0.0,
        "live": fresh,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/overview")
def get_overview():
    """Combined dashboard overview endpoint."""
    indices = get_indices()
    movers = get_movers()
    breadth = get_breadth()
    return {
        "indices": {
            "nifty":  indices["nifty"],
            "sensex": indices["sensex"],
        },
        "movers": movers,
        "breadth": breadth,
        "timestamp": datetime.now().isoformat(),
    }
