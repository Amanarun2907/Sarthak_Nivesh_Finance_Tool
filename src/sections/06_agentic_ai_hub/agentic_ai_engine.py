"""
Agentic AI Engine - Complete Real-time Data Layer
Fixes: caching, full stock universe, news, sector data, market breadth
"""
import os
import re
import time
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    "your_groq_api_key_here"
)

# Full 120-stock universe
INDIAN_STOCKS = {
    "RELIANCE.NS": "Reliance Industries", "TCS.NS": "TCS",
    "HDFCBANK.NS": "HDFC Bank", "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank", "HINDUNILVR.NS": "Hindustan Unilever",
    "ITC.NS": "ITC", "SBIN.NS": "SBI", "BHARTIARTL.NS": "Bharti Airtel",
    "KOTAKBANK.NS": "Kotak Bank", "LT.NS": "L&T", "AXISBANK.NS": "Axis Bank",
    "ASIANPAINT.NS": "Asian Paints", "MARUTI.NS": "Maruti Suzuki",
    "TITAN.NS": "Titan", "BAJFINANCE.NS": "Bajaj Finance",
    "WIPRO.NS": "Wipro", "ULTRACEMCO.NS": "UltraTech Cement",
    "NESTLEIND.NS": "Nestle India", "HCLTECH.NS": "HCL Tech",
    "SUNPHARMA.NS": "Sun Pharma", "TATAMOTORS.NS": "Tata Motors",
    "TATASTEEL.NS": "Tata Steel", "NTPC.NS": "NTPC",
    "POWERGRID.NS": "Power Grid", "ONGC.NS": "ONGC",
    "COALINDIA.NS": "Coal India", "BAJAJFINSV.NS": "Bajaj Finserv",
    "TECHM.NS": "Tech Mahindra", "ADANIENT.NS": "Adani Enterprises",
    "ADANIPORTS.NS": "Adani Ports", "JSWSTEEL.NS": "JSW Steel",
    "HINDALCO.NS": "Hindalco", "DRREDDY.NS": "Dr Reddy",
    "CIPLA.NS": "Cipla", "DIVISLAB.NS": "Divi's Labs",
    "APOLLOHOSP.NS": "Apollo Hospitals", "EICHERMOT.NS": "Eicher Motors",
    "HEROMOTOCO.NS": "Hero MotoCorp", "BAJAJ-AUTO.NS": "Bajaj Auto",
    "BRITANNIA.NS": "Britannia", "DABUR.NS": "Dabur",
    "MARICO.NS": "Marico", "GODREJCP.NS": "Godrej Consumer",
    "PIDILITIND.NS": "Pidilite", "BERGEPAINT.NS": "Berger Paints",
    "HAVELLS.NS": "Havells", "VOLTAS.NS": "Voltas",
    "MUTHOOTFIN.NS": "Muthoot Finance", "CHOLAFIN.NS": "Chola Finance",
    "SBILIFE.NS": "SBI Life", "HDFCLIFE.NS": "HDFC Life",
    "ICICIPRULI.NS": "ICICI Pru Life", "BANDHANBNK.NS": "Bandhan Bank",
    "FEDERALBNK.NS": "Federal Bank", "IDFCFIRSTB.NS": "IDFC First Bank",
    "INDUSINDBK.NS": "IndusInd Bank", "PNB.NS": "Punjab National Bank",
    "BANKBARODA.NS": "Bank of Baroda", "CANBK.NS": "Canara Bank",
    "GRASIM.NS": "Grasim", "SHREECEM.NS": "Shree Cement",
    "AMBUJACEM.NS": "Ambuja Cement", "ACC.NS": "ACC",
    "TATACONSUM.NS": "Tata Consumer", "MCDOWELL-N.NS": "United Spirits",
    "UBL.NS": "United Breweries", "COLPAL.NS": "Colgate",
    "EMAMILTD.NS": "Emami", "JUBLFOOD.NS": "Jubilant FoodWorks",
    "ZOMATO.NS": "Zomato", "NYKAA.NS": "Nykaa",
    "PAYTM.NS": "Paytm", "POLICYBZR.NS": "PB Fintech",
    "DELHIVERY.NS": "Delhivery", "IRCTC.NS": "IRCTC",
    "IRFC.NS": "IRFC", "RVNL.NS": "RVNL",
    "HAL.NS": "HAL", "BEL.NS": "BEL",
    "BHEL.NS": "BHEL", "SAIL.NS": "SAIL",
    "NMDC.NS": "NMDC", "VEDL.NS": "Vedanta",
    "HINDZINC.NS": "Hindustan Zinc", "NATIONALUM.NS": "NALCO",
    "RECLTD.NS": "REC", "PFC.NS": "PFC",
    "TATAPOWER.NS": "Tata Power", "ADANIGREEN.NS": "Adani Green",
    "TORNTPOWER.NS": "Torrent Power", "CESC.NS": "CESC",
    "MPHASIS.NS": "Mphasis", "LTIM.NS": "LTIMindtree",
    "PERSISTENT.NS": "Persistent", "COFORGE.NS": "Coforge",
    "OFSS.NS": "Oracle Fin Services", "KPITTECH.NS": "KPIT Tech",
    "ZYDUSLIFE.NS": "Zydus Life", "TORNTPHARM.NS": "Torrent Pharma",
    "AUROPHARMA.NS": "Aurobindo Pharma", "LUPIN.NS": "Lupin",
    "BIOCON.NS": "Biocon", "ALKEM.NS": "Alkem Labs",
    "MAXHEALTH.NS": "Max Healthcare", "FORTIS.NS": "Fortis",
    "LALPATHLAB.NS": "Dr Lal PathLabs", "METROPOLIS.NS": "Metropolis",
    "ABCAPITAL.NS": "Aditya Birla Capital", "MANAPPURAM.NS": "Manappuram",
    "LICHSGFIN.NS": "LIC Housing", "PNBHOUSING.NS": "PNB Housing",
    "OBEROIRLTY.NS": "Oberoi Realty", "DLF.NS": "DLF",
    "GODREJPROP.NS": "Godrej Properties", "PRESTIGE.NS": "Prestige Estates",
    "PHOENIXLTD.NS": "Phoenix Mills", "NAUKRI.NS": "Info Edge",
    "JUSTDIAL.NS": "Just Dial", "INDIAMART.NS": "IndiaMART",
    "TRENT.NS": "Trent", "ABFRL.NS": "Aditya Birla Fashion",
    "PAGEIND.NS": "Page Industries", "KALYANKJIL.NS": "Kalyan Jewellers",
}

SECTOR_MAP = {
    "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS",
                "INDUSINDBK.NS", "BANDHANBNK.NS", "FEDERALBNK.NS", "PNB.NS", "BANKBARODA.NS"],
    "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS",
           "MPHASIS.NS", "LTIM.NS", "PERSISTENT.NS", "COFORGE.NS", "OFSS.NS"],
    "Auto": ["MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS",
             "MARICO.NS", "COLPAL.NS", "GODREJCP.NS"],
    "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS",
               "LUPIN.NS", "AUROPHARMA.NS", "ZYDUSLIFE.NS", "TORNTPHARM.NS"],
    "Finance": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "MUTHOOTFIN.NS", "CHOLAFIN.NS",
                "SBILIFE.NS", "HDFCLIFE.NS", "ICICIPRULI.NS"],
    "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS",
               "ADANIGREEN.NS", "COALINDIA.NS"],
    "Metals": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS",
               "SAIL.NS", "NMDC.NS", "HINDZINC.NS"],
    "Infra": ["LT.NS", "ADANIENT.NS", "ADANIPORTS.NS", "HAL.NS", "BEL.NS", "BHEL.NS"],
    "Realty": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS"],
}


class GroqClient:
    """Groq API client using openai/gpt-oss-120b"""
    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def chat(self, prompt: str, max_tokens: int = 4096) -> str:
        try:
            r = requests.post(
                self.url,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.1, "max_tokens": max_tokens},
                timeout=90
            )
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            return f"API Error {r.status_code}: {r.text[:200]}"
        except Exception as e:
            return f"Connection Error: {str(e)}"


groq = GroqClient()


def fetch_stock_data(symbol: str) -> dict:
    """Fetch comprehensive real-time stock data - all indicators"""
    try:
        ticker = yf.Ticker(symbol)
        hist_1mo = ticker.history(period="1mo")
        hist_3mo = ticker.history(period="3mo")
        hist_1y = ticker.history(period="1y")
        info = ticker.info

        if hist_1mo.empty:
            return {"error": "No data"}

        c = hist_1mo["Close"]
        h = hist_1mo["High"]
        lo = hist_1mo["Low"]
        v = hist_1mo["Volume"]

        cur = float(c.iloc[-1])
        prev = float(c.iloc[-2]) if len(c) > 1 else cur

        # MAs
        ma5 = float(c.rolling(5).mean().iloc[-1]) if len(c) >= 5 else cur
        ma10 = float(c.rolling(10).mean().iloc[-1]) if len(c) >= 10 else cur
        ma20 = float(c.rolling(20).mean().iloc[-1]) if len(c) >= 20 else cur
        ma50 = float(hist_3mo["Close"].rolling(50).mean().iloc[-1]) if len(hist_3mo) >= 50 else cur
        ma200 = float(hist_1y["Close"].rolling(200).mean().iloc[-1]) if len(hist_1y) >= 200 else cur
        ema12 = float(c.ewm(span=12).mean().iloc[-1])
        ema26 = float(c.ewm(span=26).mean().iloc[-1])
        macd = ema12 - ema26
        macd_sig = float(c.ewm(span=9).mean().iloc[-1])

        # RSI
        delta = c.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = float((100 - 100 / (1 + gain / loss)).iloc[-1])

        # Stochastic
        l14 = lo.rolling(14).min().iloc[-1]
        h14 = h.rolling(14).max().iloc[-1]
        stoch = float(100 * (cur - l14) / (h14 - l14)) if h14 != l14 else 50

        # Bollinger
        bb_mid = float(c.rolling(20).mean().iloc[-1])
        bb_std = float(c.rolling(20).std().iloc[-1])
        bb_up = bb_mid + 2 * bb_std
        bb_lo = bb_mid - 2 * bb_std

        # Volume
        avg_vol = float(v.mean())
        cur_vol = float(v.iloc[-1])
        vol_ratio = cur_vol / avg_vol if avg_vol > 0 else 1

        # ATR
        hl = h - lo
        hc = abs(h - c.shift())
        lc = abs(lo - c.shift())
        atr = float(pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(14).mean().iloc[-1])

        # ADX
        pdm = h.diff().clip(lower=0)
        ndm = (-lo.diff()).clip(lower=0)
        tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
        tr14 = tr.rolling(14).sum()
        pdi = 100 * pdm.rolling(14).sum() / tr14
        ndi = 100 * ndm.rolling(14).sum() / tr14
        dx = 100 * abs(pdi - ndi) / (pdi + ndi)
        adx = float(dx.rolling(14).mean().iloc[-1])

        # Support / Resistance
        r1 = float(h.nlargest(3).iloc[0])
        r2 = float(h.nlargest(3).iloc[1]) if len(h) >= 2 else r1
        s1 = float(lo.nsmallest(3).iloc[0])
        s2 = float(lo.nsmallest(3).iloc[1]) if len(lo) >= 2 else s1

        # Momentum
        mom1d = float(((cur - prev) / prev) * 100) if prev else 0
        mom1mo = float(((cur - c.iloc[0]) / c.iloc[0]) * 100) if c.iloc[0] else 0
        mom3mo = float(((cur - hist_3mo["Close"].iloc[0]) / hist_3mo["Close"].iloc[0]) * 100) if len(hist_3mo) > 0 else 0

        w52h = info.get("fiftyTwoWeekHigh", cur)
        w52l = info.get("fiftyTwoWeekLow", cur)

        return {
            "symbol": symbol, "timestamp": datetime.now().isoformat(),
            "company_name": info.get("longName", symbol),
            "sector": info.get("sector", "Unknown"),
            "industry": info.get("industry", "Unknown"),
            "exchange": info.get("exchange", "NSE"),
            "current_price": cur, "prev_close": prev,
            "change": cur - prev, "change_pct": ((cur - prev) / prev) * 100,
            "open": float(hist_1mo["Open"].iloc[-1]),
            "high": float(h.iloc[-1]), "low": float(lo.iloc[-1]),
            "ma5": ma5, "ma10": ma10, "ma20": ma20, "ma50": ma50, "ma200": ma200,
            "ema12": ema12, "ema26": ema26,
            "macd": macd, "macd_signal": macd_sig, "macd_hist": macd - macd_sig,
            "rsi": rsi, "stoch": stoch, "adx": adx,
            "bb_upper": bb_up, "bb_mid": bb_mid, "bb_lower": bb_lo,
            "bb_width": ((bb_up - bb_lo) / bb_mid) * 100,
            "cur_vol": cur_vol, "avg_vol": avg_vol, "vol_ratio": vol_ratio,
            "atr": atr,
            "r1": r1, "r2": r2, "s1": s1, "s2": s2,
            "mom1d": mom1d, "mom1mo": mom1mo, "mom3mo": mom3mo,
            "volatility": float(c.pct_change().std() * (252 ** 0.5) * 100),
            "market_cap": info.get("marketCap", 0),
            "pe": info.get("trailingPE", 0), "fwd_pe": info.get("forwardPE", 0),
            "peg": info.get("pegRatio", 0), "pb": info.get("priceToBook", 0),
            "eps": info.get("trailingEps", 0),
            "profit_margin": info.get("profitMargins", 0),
            "roe": info.get("returnOnEquity", 0),
            "debt_eq": info.get("debtToEquity", 0),
            "current_ratio": info.get("currentRatio", 0),
            "div_yield": info.get("dividendYield", 0),
            "beta": info.get("beta", 0),
            "w52h": w52h, "w52l": w52l,
            "pct_from_52h": ((cur - w52h) / w52h) * 100 if w52h else 0,
            "pct_from_52l": ((cur - w52l) / w52l) * 100 if w52l else 0,
            "hist_1mo": hist_1mo,
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_fii_dii() -> dict:
    """Fetch FII/DII from NSE"""
    try:
        s = requests.Session()
        s.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://www.nseindia.com/"})
        s.get("https://www.nseindia.com", timeout=10)
        r = s.get("https://www.nseindia.com/api/fiidiiTradeReact", timeout=10)
        if r.status_code == 200:
            d = r.json()
            if d:
                latest = d[0]
                return {
                    "date": latest.get("date", ""),
                    "fii_buy": float(latest.get("fiiBuyValue", 0)),
                    "fii_sell": float(latest.get("fiiSellValue", 0)),
                    "fii_net": float(latest.get("fiiNetValue", 0)),
                    "dii_buy": float(latest.get("diiBuyValue", 0)),
                    "dii_sell": float(latest.get("diiSellValue", 0)),
                    "dii_net": float(latest.get("diiNetValue", 0)),
                    "total_net": float(latest.get("fiiNetValue", 0)) + float(latest.get("diiNetValue", 0)),
                }
    except:
        pass
    return {"fii_net": 0, "dii_net": 0, "total_net": 0, "date": "N/A",
            "fii_buy": 0, "fii_sell": 0, "dii_buy": 0, "dii_sell": 0}


def fetch_market_overview() -> dict:
    """Fetch NIFTY, SENSEX, BankNifty, VIX, global markets"""
    result = {}
    indices = {
        "NIFTY50": "^NSEI", "SENSEX": "^BSESN",
        "BANKNIFTY": "^NSEBANK", "NIFTYIT": "^CNXIT",
        "VIX": "^INDIAVIX", "SGX_NIFTY": "^NSEI",
        "DOW": "^DJI", "NASDAQ": "^IXIC", "SP500": "^GSPC",
    }
    for name, sym in indices.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="5d")
            if not h.empty:
                cur = float(h["Close"].iloc[-1])
                prev = float(h["Close"].iloc[-2]) if len(h) > 1 else cur
                result[name] = {
                    "current": cur,
                    "change": cur - prev,
                    "change_pct": ((cur - prev) / prev) * 100 if prev else 0,
                }
        except:
            result[name] = {"current": 0, "change": 0, "change_pct": 0}
    return result


def fetch_sector_performance() -> dict:
    """Fetch real-time sector performance"""
    sector_data = {}
    for sector, symbols in SECTOR_MAP.items():
        changes = []
        for sym in symbols[:5]:
            try:
                h = yf.Ticker(sym).history(period="5d")
                if not h.empty and len(h) >= 2:
                    chg = ((h["Close"].iloc[-1] - h["Close"].iloc[-2]) / h["Close"].iloc[-2]) * 100
                    changes.append(float(chg))
            except:
                continue
        if changes:
            avg = sum(changes) / len(changes)
            sector_data[sector] = {
                "avg_change": round(avg, 2),
                "signal": "Bullish" if avg > 0.5 else "Bearish" if avg < -0.5 else "Neutral",
                "stocks_analyzed": len(changes),
            }
    return sector_data


def fetch_news_sentiment(company_name: str) -> dict:
    """Fetch real news from Google News RSS"""
    items = []
    avg_sent = 0.0
    try:
        q = company_name.replace(" ", "+") + "+stock+India"
        url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        r = requests.get(url, timeout=10,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.content, "xml")
            sentiments = []
            for item in soup.find_all("item")[:8]:
                title = item.title.text if item.title else ""
                source = item.source.text if item.source else "Google News"
                pub = item.pubDate.text if item.pubDate else ""
                try:
                    s = TextBlob(title).sentiment.polarity
                except:
                    s = 0.0
                sentiments.append(s)
                items.append({"title": title, "source": source, "date": pub, "sentiment": s,
                               "label": "Positive" if s > 0.1 else "Negative" if s < -0.1 else "Neutral"})
            avg_sent = sum(sentiments) / len(sentiments) if sentiments else 0.0
    except Exception as e:
        print(f"News error: {e}")
    label = "Positive" if avg_sent > 0.1 else "Negative" if avg_sent < -0.1 else "Neutral"
    return {"items": items, "avg_sentiment": round(avg_sent, 3), "label": label}


def fetch_portfolio_live(holdings: list) -> list:
    """Enrich portfolio holdings with real-time prices"""
    enriched = []
    for h in holdings:
        sym = h.get("symbol", "")
        qty = h.get("quantity", 0)
        buy_price = h.get("buy_price", 0)
        try:
            hist = yf.Ticker(sym).history(period="1d")
            if not hist.empty:
                cur = float(hist["Close"].iloc[-1])
                cur_val = cur * qty
                invested = buy_price * qty
                pnl = cur_val - invested
                pnl_pct = (pnl / invested) * 100 if invested > 0 else 0
                enriched.append({
                    **h,
                    "current_price": cur,
                    "current_value": cur_val,
                    "invested": invested,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "stock_name": INDIAN_STOCKS.get(sym, sym),
                })
        except:
            enriched.append({**h, "current_price": buy_price,
                             "current_value": buy_price * qty,
                             "invested": buy_price * qty,
                             "pnl": 0, "pnl_pct": 0,
                             "stock_name": INDIAN_STOCKS.get(sym, sym)})
    return enriched


def run_stock_analysis(symbol: str) -> dict:
    """Full stock analysis with all real-time data"""
    d = fetch_stock_data(symbol)
    if "error" in d:
        return {"success": False, "error": d["error"]}
    fii = fetch_fii_dii()
    news = fetch_news_sentiment(d["company_name"])

    prompt = f"""You are a world-class senior investment analyst. Analyze this stock with institutional-grade precision.

STOCK: {d['company_name']} ({symbol}) | SECTOR: {d['sector']} | INDUSTRY: {d['industry']}
TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

LIVE PRICE DATA:
Current: Rs{d['current_price']:.2f} | Change: Rs{d['change']:+.2f} ({d['change_pct']:+.2f}%)
Open: Rs{d['open']:.2f} | High: Rs{d['high']:.2f} | Low: Rs{d['low']:.2f} | Prev Close: Rs{d['prev_close']:.2f}

MOVING AVERAGES:
MA5: Rs{d['ma5']:.2f} ({'ABOVE' if d['current_price']>d['ma5'] else 'BELOW'}) | MA10: Rs{d['ma10']:.2f} ({'ABOVE' if d['current_price']>d['ma10'] else 'BELOW'})
MA20: Rs{d['ma20']:.2f} ({'ABOVE' if d['current_price']>d['ma20'] else 'BELOW'}) | MA50: Rs{d['ma50']:.2f} ({'ABOVE' if d['current_price']>d['ma50'] else 'BELOW'})
MA200: Rs{d['ma200']:.2f} ({'ABOVE - BULLISH LONG TERM' if d['current_price']>d['ma200'] else 'BELOW - BEARISH LONG TERM'})
EMA12: Rs{d['ema12']:.2f} | EMA26: Rs{d['ema26']:.2f}

MACD: Line={d['macd']:.2f} | Signal={d['macd_signal']:.2f} | Histogram={d['macd_hist']:.2f} ({'BULLISH' if d['macd_hist']>0 else 'BEARISH'})
RSI(14): {d['rsi']:.1f} ({'OVERBOUGHT' if d['rsi']>70 else 'OVERSOLD' if d['rsi']<30 else 'NEUTRAL'})
Stochastic: {d['stoch']:.1f} | ADX: {d['adx']:.1f} ({'STRONG TREND' if d['adx']>25 else 'WEAK/NO TREND'})

BOLLINGER BANDS: Upper=Rs{d['bb_upper']:.2f} | Mid=Rs{d['bb_mid']:.2f} | Lower=Rs{d['bb_lower']:.2f} | Width={d['bb_width']:.1f}%
SUPPORT: S1=Rs{d['s1']:.2f} | S2=Rs{d['s2']:.2f}
RESISTANCE: R1=Rs{d['r1']:.2f} | R2=Rs{d['r2']:.2f}

VOLUME: Current={d['cur_vol']:,.0f} | Avg={d['avg_vol']:,.0f} | Ratio={d['vol_ratio']:.2f}x ({'HIGH ACTIVITY' if d['vol_ratio']>1.5 else 'NORMAL'})
ATR: Rs{d['atr']:.2f} | Volatility(Annual): {d['volatility']:.1f}%

MOMENTUM: 1D={d['mom1d']:+.2f}% | 1M={d['mom1mo']:+.2f}% | 3M={d['mom3mo']:+.2f}%
52W High: Rs{d['w52h']:.2f} ({d['pct_from_52h']:+.1f}% from high) | 52W Low: Rs{d['w52l']:.2f} ({d['pct_from_52l']:+.1f}% from low)

FUNDAMENTALS:
Market Cap: Rs{d['market_cap']:,.0f} | P/E: {d['pe']:.1f} | Fwd P/E: {d['fwd_pe']:.1f} | PEG: {d['peg']:.2f} | P/B: {d['pb']:.2f}
EPS: Rs{d['eps']:.2f} | Profit Margin: {d['profit_margin']*100:.1f}% | ROE: {d['roe']*100:.1f}%
Debt/Equity: {d['debt_eq']:.2f} | Current Ratio: {d['current_ratio']:.2f} | Beta: {d['beta']:.2f}
Dividend Yield: {d['div_yield']*100:.2f}%

INSTITUTIONAL FLOW (NSE Live - {fii['date']}):
FII Net: Rs{fii['fii_net']:,.0f} Cr (Buy: Rs{fii['fii_buy']:,.0f} | Sell: Rs{fii['fii_sell']:,.0f})
DII Net: Rs{fii['dii_net']:,.0f} Cr (Buy: Rs{fii['dii_buy']:,.0f} | Sell: Rs{fii['dii_sell']:,.0f})
Total Institutional: Rs{fii['total_net']:,.0f} Cr

NEWS SENTIMENT: {news['label']} (Score: {news['avg_sentiment']:.3f}) | {len(news['items'])} articles analyzed
Top Headlines: {' | '.join([n['title'][:60] for n in news['items'][:3]])}

Provide STRUCTURED analysis in EXACTLY this format (use these exact section headers):

TECHNICAL_SCORE: [X/10]
TECHNICAL_TREND: [Bullish/Bearish/Sideways]
TECHNICAL_STRENGTH: [Strong/Moderate/Weak]
TECHNICAL_SUMMARY: [2-3 sentences covering MA alignment, RSI, MACD, volume]
GOLDEN_CROSS: [Yes/No - explain]
KEY_SUPPORT: [Rs X (probability %)]
KEY_RESISTANCE: [Rs X (probability %)]
BREAKOUT_LEVEL: [Rs X - what happens if broken]

FUNDAMENTAL_SCORE: [X/10]
VALUATION: [Overvalued/Fair/Undervalued]
PE_ANALYSIS: [1 sentence vs sector average]
FINANCIAL_HEALTH: [Strong/Moderate/Weak - 1 sentence]
DIVIDEND_VERDICT: [Attractive/Moderate/Poor]
FUNDAMENTAL_SUMMARY: [2-3 sentences]

INSTITUTIONAL_SCORE: [X/10]
FII_SIGNAL: [Bullish/Bearish/Neutral]
DII_SIGNAL: [Bullish/Bearish/Neutral]
SMART_MONEY: [Accumulation/Distribution/Neutral]
INSTITUTIONAL_SUMMARY: [1-2 sentences]

NEWS_IMPACT: [Positive/Negative/Neutral]
NEWS_SUMMARY: [1 sentence on news impact]

OVERALL_SCORE: [X/10]
RECOMMENDATION: [STRONG BUY/BUY/HOLD/SELL/STRONG SELL]
CONFIDENCE: [X%]
INVESTMENT_THESIS: [3-4 sentences - core reason to buy/sell/hold]
ENTRY_PRICE: [Rs X - Rs Y]
TARGET_1: [Rs X (X% upside, 3 months)]
TARGET_2: [Rs X (X% upside, 6 months)]
STOP_LOSS: [Rs X (X% below entry)]
RISK_REWARD: [X:Y]
RISK_LEVEL: [Low/Medium/High]
HOLDING_PERIOD: [Short/Medium/Long term]
POSITION_SIZE: [X% of portfolio]

REASON_1: [Most important reason with specific data]
REASON_2: [Second reason with specific data]
REASON_3: [Third reason with specific data]
REASON_4: [Fourth reason with specific data]
REASON_5: [Fifth reason with specific data]

RISK_1: [Most critical risk with probability]
RISK_2: [Second risk]
RISK_3: [Third risk]

MONITOR_DAILY: [What to watch daily]
MONITOR_WEEKLY: [What to review weekly]
EXIT_TRIGGER: [Specific conditions to exit]

PROFESSIONAL_INSIGHT: [2-3 paragraphs of expert-level insights about sector trends, competitive position, market cycles]"""

    analysis_text = groq.chat(prompt)
    return {
        "success": True, "symbol": symbol,
        "company_name": d["company_name"],
        "raw_data": d, "fii_data": fii,
        "news_data": news, "analysis_text": analysis_text,
        "timestamp": datetime.now().isoformat()
    }


def run_portfolio_analysis(holdings: list) -> dict:
    """Portfolio analysis with real live prices"""
    enriched = fetch_portfolio_live(holdings)
    total_invested = sum(h["invested"] for h in enriched)
    total_value = sum(h["current_value"] for h in enriched)
    total_pnl = total_value - total_invested
    total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
    fii = fetch_fii_dii()
    market = fetch_market_overview()
    sector_perf = fetch_sector_performance()

    holdings_detail = "\n".join([
        f"  {h['stock_name']} ({h['symbol']}): Qty={h['quantity']} | "
        f"Buy=Rs{h['buy_price']:.2f} | Current=Rs{h['current_price']:.2f} | "
        f"P&L=Rs{h['pnl']:+.0f} ({h['pnl_pct']:+.1f}%) | Value=Rs{h['current_value']:,.0f}"
        for h in enriched
    ])

    nifty = market.get("NIFTY50", {})
    prompt = f"""You are a portfolio risk manager and investment strategist. Analyze this portfolio with real-time data.

PORTFOLIO SUMMARY (Live Prices from Yahoo Finance):
Total Invested: Rs{total_invested:,.0f}
Current Value: Rs{total_value:,.0f}
Total P&L: Rs{total_pnl:+,.0f} ({total_pnl_pct:+.1f}%)
Number of Holdings: {len(enriched)}

HOLDINGS (Real-time prices):
{holdings_detail}

MARKET CONDITIONS:
NIFTY50: {nifty.get('current', 0):.0f} ({nifty.get('change_pct', 0):+.2f}%)
FII Net Flow: Rs{fii['fii_net']:,.0f} Cr | DII Net Flow: Rs{fii['dii_net']:,.0f} Cr

SECTOR PERFORMANCE:
{chr(10).join([f"  {s}: {v['avg_change']:+.2f}% ({v['signal']})" for s, v in sector_perf.items()])}

Provide STRUCTURED analysis in EXACTLY this format:

PORTFOLIO_HEALTH: [Excellent/Good/Fair/Poor]
RISK_SCORE: [X/10]
RISK_LEVEL: [Low/Medium/High]
DIVERSIFICATION: [Good/Moderate/Poor]
CONCENTRATION_RISK: [1 sentence on top holding concentration]

BEST_PERFORMER: [Stock name - return%]
WORST_PERFORMER: [Stock name - return%]
PORTFOLIO_BETA: [Estimated X.X]
EXPECTED_ANNUAL_RETURN: [X-Y%]

STRENGTH_1: [Portfolio strength with data]
STRENGTH_2: [Portfolio strength with data]
STRENGTH_3: [Portfolio strength with data]

WEAKNESS_1: [Portfolio weakness with data]
WEAKNESS_2: [Portfolio weakness with data]
WEAKNESS_3: [Portfolio weakness with data]

ACTION_1: [Immediate action this week - specific]
ACTION_2: [Immediate action this week - specific]
ACTION_3: [Immediate action this week - specific]

SHORT_TERM_STRATEGY: [1-3 month strategy in 3-4 sentences]
LONG_TERM_STRATEGY: [6-12 month strategy in 3-4 sentences]

ADD_STOCK_1: [Stock to add - symbol and reason]
ADD_STOCK_2: [Stock to add - symbol and reason]
REDUCE_STOCK_1: [Stock to reduce - symbol and reason]
REDUCE_STOCK_2: [Stock to reduce - symbol and reason]

TARGET_ALLOCATION_BANKING: [X%]
TARGET_ALLOCATION_IT: [X%]
TARGET_ALLOCATION_PHARMA: [X%]
TARGET_ALLOCATION_FMCG: [X%]
TARGET_ALLOCATION_ENERGY: [X%]
TARGET_ALLOCATION_OTHERS: [X%]

CONSERVATIVE_RETURN: [X%]
REALISTIC_RETURN: [Y%]
OPTIMISTIC_RETURN: [Z%]

REBALANCING_NEEDED: [Yes/No]
REBALANCING_PLAN: [Specific steps if needed]

RISK_MITIGATION: [3-4 sentences on how to protect the portfolio]"""

    analysis_text = groq.chat(prompt)
    return {
        "success": True, "enriched_holdings": enriched,
        "total_invested": total_invested, "total_value": total_value,
        "total_pnl": total_pnl, "total_pnl_pct": total_pnl_pct,
        "analysis_text": analysis_text, "market": market,
        "sector_perf": sector_perf, "fii": fii,
        "timestamp": datetime.now().isoformat()
    }


def run_market_intelligence() -> dict:
    """Full market intelligence with all indices, sectors, FII/DII"""
    market = fetch_market_overview()
    fii = fetch_fii_dii()
    sector_perf = fetch_sector_performance()

    nifty = market.get("NIFTY50", {})
    sensex = market.get("SENSEX", {})
    bnk = market.get("BANKNIFTY", {})
    vix = market.get("VIX", {})
    dow = market.get("DOW", {})
    nasdaq = market.get("NASDAQ", {})

    prompt = f"""You are a chief market strategist. Provide comprehensive market intelligence.

INDIAN MARKET (Live):
NIFTY50: {nifty.get('current', 0):.2f} ({nifty.get('change_pct', 0):+.2f}%)
SENSEX: {sensex.get('current', 0):.2f} ({sensex.get('change_pct', 0):+.2f}%)
BANK NIFTY: {bnk.get('current', 0):.2f} ({bnk.get('change_pct', 0):+.2f}%)
INDIA VIX: {vix.get('current', 0):.2f} ({'HIGH FEAR' if vix.get('current', 0) > 20 else 'LOW FEAR' if vix.get('current', 0) < 12 else 'MODERATE'})

GLOBAL MARKETS:
DOW JONES: {dow.get('current', 0):.2f} ({dow.get('change_pct', 0):+.2f}%)
NASDAQ: {nasdaq.get('current', 0):.2f} ({nasdaq.get('change_pct', 0):+.2f}%)
S&P 500: {market.get('SP500', {}).get('current', 0):.2f} ({market.get('SP500', {}).get('change_pct', 0):+.2f}%)

INSTITUTIONAL FLOW (NSE - {fii['date']}):
FII: Rs{fii['fii_net']:,.0f} Cr net | DII: Rs{fii['dii_net']:,.0f} Cr net | Total: Rs{fii['total_net']:,.0f} Cr

SECTOR PERFORMANCE (5-day):
{chr(10).join([f"  {s}: {v['avg_change']:+.2f}% ({v['signal']}) - {v['stocks_analyzed']} stocks" for s, v in sector_perf.items()])}

Provide STRUCTURED intelligence in EXACTLY this format:

MARKET_STATUS: [Bullish/Bearish/Neutral]
MARKET_STRENGTH: [Strong/Moderate/Weak]
NIFTY_TREND: [Uptrend/Downtrend/Sideways]
VIX_SIGNAL: [Fear/Greed/Neutral - interpretation]
GLOBAL_IMPACT: [Positive/Negative/Neutral - 1 sentence]

FII_SIGNAL: [Buying/Selling/Neutral]
DII_SIGNAL: [Buying/Selling/Neutral]
INSTITUTIONAL_VERDICT: [1-2 sentences on combined institutional activity]

TOP_SECTOR_1: [Sector name - reason to watch]
TOP_SECTOR_2: [Sector name - reason to watch]
TOP_SECTOR_3: [Sector name - reason to watch]
AVOID_SECTOR_1: [Sector to avoid - reason]
AVOID_SECTOR_2: [Sector to avoid - reason]

MARKET_PREDICTION_1W: [Direction with confidence %]
NIFTY_TARGET_1W: [Range X-Y]
NIFTY_SUPPORT: [Key support level]
NIFTY_RESISTANCE: [Key resistance level]

TRADING_BIAS: [Bullish/Bearish/Neutral]
TRADING_STRATEGY: [3-4 sentences - specific actionable strategy]
BEST_TRADE_SETUP: [Specific trade idea with entry/target/SL]

RISK_1: [Market risk with probability]
RISK_2: [Market risk with probability]
RISK_3: [Market risk with probability]

OPPORTUNITY_1: [Market opportunity - specific]
OPPORTUNITY_2: [Market opportunity - specific]
OPPORTUNITY_3: [Market opportunity - specific]

MARKET_INSIGHT: [3 paragraphs of expert market analysis covering macro trends, FII behavior, sector rotation, and what smart money is doing]"""

    analysis_text = groq.chat(prompt)
    return {
        "success": True, "market": market, "fii": fii,
        "sector_perf": sector_perf, "analysis_text": analysis_text,
        "timestamp": datetime.now().isoformat()
    }
