"""
IPO Multi-Agent Framework - Sarthak Nivesh
Hierarchical Multi-Agentic AI System for IPO Investment & Exit Strategy
Authors: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani
"""
import os, re, time, requests, math
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"
MACRO_TICKERS = {
    "NIFTY50":"^NSEI","SENSEX":"^BSESN","BANKNIFTY":"^NSEBANK",
    "INDIA_VIX":"^INDIAVIX","USD_INR":"INR=X","GOLD":"GC=F",
    "CRUDE_OIL":"CL=F","US_10Y":"^TNX","DOW":"^DJI","NASDAQ":"^IXIC",
}
VADER = SentimentIntensityAnalyzer()

def _sf(v, d=0.0):
    try:
        f = float(v)
        return d if (math.isnan(f) or math.isinf(f)) else f
    except: return d

@dataclass
class AgentResult:
    agent_name: str; score: float; signal: str; confidence: float; summary: str
    details: dict = field(default_factory=dict); error: Optional[str] = None

@dataclass
class OrchestratorResult:
    ipo_name: str; symbol: str; final_decision: str; overall_score: float
    confidence: float; entry_strategy: str; exit_strategy: str
    target_price: float; stop_loss: float; risk_level: str; holding_period: str
    agent_scores: dict; investment_thesis: str; key_risks: list
    key_catalysts: list; monitoring_triggers: list
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class GroqLLM:
    def __init__(self): self.api_key = GROQ_API_KEY; self.url = GROQ_URL
    def ask(self, sys_p: str, usr_p: str, max_tokens: int = 800) -> str:
        if not self.api_key or self.api_key in ("","your_groq_api_key_here"):
            return "LLM_UNAVAILABLE"
        try:
            r = requests.post(self.url,
                headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"},
                json={"model":GROQ_MODEL,
                      "messages":[{"role":"system","content":sys_p},{"role":"user","content":usr_p}],
                      "temperature":0.1,"max_tokens":max_tokens},timeout=90)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"]
            return f"API_ERROR_{r.status_code}"
        except Exception as e: return f"CONNECTION_ERROR:{e}"
    @staticmethod
    def parse(text:str,key:str,default:str="N/A")->str:
        m = re.search(rf"^{re.escape(key)}:\s*(.+)$",text,re.MULTILINE)
        return m.group(1).strip() if m else default

_llm = GroqLLM()

class PriceMovementAgent:
    NAME = "Price Movement Agent"
    def __init__(self,llm): self.llm=llm
    def _fetch(self,symbol):
        try:
            t=yf.Ticker(symbol); h1=t.history(period="1mo"); h3=t.history(period="3mo"); inf=t.info
            if h1.empty: return {"error":"No data"}
            c=h1["Close"]; hi=h1["High"]; lo=h1["Low"]; v=h1["Volume"]
            cur=float(c.iloc[-1]); prev=float(c.iloc[-2]) if len(c)>1 else cur
            ma20=float(c.rolling(20).mean().iloc[-1]) if len(c)>=20 else cur
            ma50=float(h3["Close"].rolling(50).mean().iloc[-1]) if len(h3)>=50 else cur
            ema12=float(c.ewm(span=12).mean().iloc[-1]); ema26=float(c.ewm(span=26).mean().iloc[-1])
            macd=ema12-ema26; macd_sig=float(c.ewm(span=9).mean().iloc[-1])
            delta=c.diff(); gain=delta.where(delta>0,0.0).rolling(14).mean()
            loss=(-delta.where(delta<0,0.0)).rolling(14).mean()
            rsi=_sf((100-100/(1+gain/loss)).iloc[-1],50.0)
            bb_mid=float(c.rolling(20).mean().iloc[-1]); bb_std=_sf(c.rolling(20).std().iloc[-1])
            bb_up=bb_mid+2*bb_std; bb_lo=bb_mid-2*bb_std
            avg_vol=_sf(v.mean()); cur_vol=_sf(v.iloc[-1])
            vol_ratio=cur_vol/avg_vol if avg_vol>0 else 1.0
            hl=hi-lo; hc=abs(hi-c.shift()); lc=abs(lo-c.shift())
            atr=_sf(pd.concat([hl,hc,lc],axis=1).max(axis=1).rolling(14).mean().iloc[-1])
            r1=_sf(hi.nlargest(3).iloc[0]); s1=_sf(lo.nsmallest(3).iloc[0])
            mom1d=((cur-prev)/prev)*100 if prev else 0.0
            mom1m=((cur-float(c.iloc[0]))/float(c.iloc[0]))*100 if c.iloc[0] else 0.0
            mom3m=((cur-float(h3["Close"].iloc[0]))/float(h3["Close"].iloc[0]))*100 if len(h3)>0 else 0.0
            w52h=inf.get("fiftyTwoWeekHigh",cur); w52l=inf.get("fiftyTwoWeekLow",cur)
            return dict(symbol=symbol,current_price=cur,prev_close=prev,change_pct=mom1d,
                        ma20=ma20,ma50=ma50,ema12=ema12,ema26=ema26,macd=macd,
                        macd_signal=macd_sig,macd_hist=macd-macd_sig,rsi=rsi,
                        bb_upper=bb_up,bb_mid=bb_mid,bb_lower=bb_lo,
                        vol_ratio=vol_ratio,avg_vol=avg_vol,cur_vol=cur_vol,atr=atr,
                        r1=r1,s1=s1,mom_1d=mom1d,mom_1m=mom1m,mom_3m=mom3m,
                        w52h=w52h,w52l=w52l,
                        pct_from_52h=((cur-w52h)/w52h)*100 if w52h else 0.0,
                        beta=inf.get("beta",0.0),
                        volatility=_sf(c.pct_change().std()*(252**0.5)*100))
        except Exception as e: return {"error":str(e)}
    def _rule_score(self,d):
        score=50.0; signals=[]; cur=d["current_price"]
        if cur>d["ma20"]:  score+=6; signals.append("Above MA20")
        else:              score-=5; signals.append("Below MA20")
        if cur>d["ma50"]:  score+=5; signals.append("Above MA50")
        else:              score-=4; signals.append("Below MA50")
        rsi=d["rsi"]
        if rsi<30:         score+=8; signals.append(f"RSI {rsi:.1f} oversold")
        elif rsi<45:       score+=3; signals.append(f"RSI {rsi:.1f} mild oversold")
        elif rsi>75:       score-=8; signals.append(f"RSI {rsi:.1f} overbought")
        elif rsi>60:       score-=2; signals.append(f"RSI {rsi:.1f} near overbought")
        else:              score+=1; signals.append(f"RSI {rsi:.1f} neutral")
        if d["macd_hist"]>0: score+=6; signals.append("MACD bullish")
        else:              score-=4; signals.append("MACD bearish")
        vr=d["vol_ratio"]
        if vr>2.0:         score+=8; signals.append(f"Vol {vr:.1f}x strong")
        elif vr>1.5:       score+=4; signals.append(f"Vol {vr:.1f}x above avg")
        elif vr<0.5:       score-=4; signals.append(f"Vol {vr:.1f}x low")
        if d["mom_1m"]>10: score+=6; signals.append(f"1M mom +{d['mom_1m']:.1f}%")
        elif d["mom_1m"]>0:score+=2; signals.append(f"1M mom +{d['mom_1m']:.1f}%")
        elif d["mom_1m"]<-15:score-=8;signals.append(f"1M mom {d['mom_1m']:.1f}%")
        else:              score-=3; signals.append(f"1M mom {d['mom_1m']:.1f}%")
        return max(0.0,min(100.0,score)),signals
    def run(self,symbol,ipo_name):
        d=self._fetch(symbol)
        if "error" in d:
            return AgentResult(self.NAME,50.0,"HOLD",30.0,f"No price data: {d['error']}",error=d["error"])
        rule_score,signals=self._rule_score(d)
        sp="You are a specialist IPO technical analyst. Be precise and data-driven."
        up=f"""IPO: {ipo_name} ({symbol})
Price: Rs{d['current_price']:.2f} ({d['change_pct']:+.2f}%) | RSI: {d['rsi']:.1f} | MACD hist: {d['macd_hist']:.3f}
MA20: Rs{d['ma20']:.2f} | MA50: Rs{d['ma50']:.2f} | Vol: {d['vol_ratio']:.2f}x
ATR: Rs{d['atr']:.2f} | 1M mom: {d['mom_1m']:+.2f}% | Support: Rs{d['s1']:.2f} | Resist: Rs{d['r1']:.2f}
BB: Rs{d['bb_lower']:.2f}-Rs{d['bb_upper']:.2f} | Volatility: {d['volatility']:.1f}%
Rule score: {rule_score:.1f}/100 | Key signals: {' | '.join(signals[:4])}

Respond in EXACTLY this format:
PRICE_SCORE: [0-100]
PRICE_SIGNAL: [STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL]
PRICE_CONFIDENCE: [0-100]
TREND_DIRECTION: [Uptrend/Downtrend/Sideways]
TREND_STRENGTH: [Strong/Moderate/Weak]
KEY_SUPPORT: [Rs value]
KEY_RESISTANCE: [Rs value]
MOMENTUM_STATUS: [Accelerating/Decelerating/Flat]
VOLUME_VERDICT: [Accumulation/Distribution/Neutral]
PRICE_SUMMARY: [2 precise sentences with specific price levels and indicator values]"""
        llm_text=self.llm.ask(sp,up,max_tokens=500)
        try:    ls=float(self.llm.parse(llm_text,"PRICE_SCORE",str(rule_score)))
        except: ls=rule_score
        try:    lc=float(self.llm.parse(llm_text,"PRICE_CONFIDENCE","60"))
        except: lc=60.0
        return AgentResult(self.NAME,round(rule_score*0.4+ls*0.6,1),
            self.llm.parse(llm_text,"PRICE_SIGNAL","HOLD"),round(lc,1),
            self.llm.parse(llm_text,"PRICE_SUMMARY","; ".join(signals[:3])),
            dict(price_data=d,rule_signals=signals,rule_score=rule_score,
                 trend_direction=self.llm.parse(llm_text,"TREND_DIRECTION","Sideways"),
                 trend_strength=self.llm.parse(llm_text,"TREND_STRENGTH","Moderate"),
                 key_support=self.llm.parse(llm_text,"KEY_SUPPORT",f"Rs{d['s1']:.2f}"),
                 key_resistance=self.llm.parse(llm_text,"KEY_RESISTANCE",f"Rs{d['r1']:.2f}"),
                 momentum_status=self.llm.parse(llm_text,"MOMENTUM_STATUS","Flat"),
                 volume_verdict=self.llm.parse(llm_text,"VOLUME_VERDICT","Neutral"),llm_raw=llm_text))

class MacroeconomicAgent:
    NAME = "Macroeconomic Agent"
    def __init__(self,llm): self.llm=llm
    def _fetch(self):
        idx={}
        for name,sym in MACRO_TICKERS.items():
            try:
                h=yf.Ticker(sym).history(period="5d")
                if not h.empty:
                    cur=float(h["Close"].iloc[-1]); prev=float(h["Close"].iloc[-2]) if len(h)>1 else cur
                    idx[name]={"current":round(cur,2),"change_pct":round(((cur-prev)/prev)*100,2) if prev else 0.0}
                else: idx[name]={"current":0,"change_pct":0.0}
            except: idx[name]={"current":0,"change_pct":0.0}
        fii={"fii_net":0.0,"dii_net":0.0,"date":"N/A"}
        try:
            s=requests.Session(); s.headers.update({"User-Agent":"Mozilla/5.0","Referer":"https://www.nseindia.com/"})
            s.get("https://www.nseindia.com",timeout=8)
            r=s.get("https://www.nseindia.com/api/fiidiiTradeReact",timeout=8)
            if r.status_code==200:
                data=r.json(); dm={}
                for rec in data:
                    dt=rec.get("date",""); cat=rec.get("category",""); net=_sf(rec.get("netValue",0))
                    if dt not in dm: dm[dt]={"fii_net":0.0,"dii_net":0.0}
                    if "FII" in cat or "FPI" in cat: dm[dt]["fii_net"]+=net
                    elif "DII" in cat: dm[dt]["dii_net"]+=net
                if dm:
                    ld=list(dm.keys())[0]
                    fii={"fii_net":round(dm[ld]["fii_net"],2),"dii_net":round(dm[ld]["dii_net"],2),"date":ld}
        except: pass
        return {"indices":idx,"fii_dii":fii}
    def _rule_score(self,macro):
        idx=macro["indices"]; fii=macro["fii_dii"]; score=50.0; signals=[]
        nc=idx.get("NIFTY50",{}).get("change_pct",0.0)
        if nc>1.5:   score+=8;  signals.append(f"NIFTY strong +{nc:.2f}%")
        elif nc>0:   score+=3;  signals.append(f"NIFTY positive +{nc:.2f}%")
        elif nc<-1.5:score-=8;  signals.append(f"NIFTY weak {nc:.2f}%")
        else:        score-=3;  signals.append(f"NIFTY mildly negative {nc:.2f}%")
        vix=idx.get("INDIA_VIX",{}).get("current",15.0)
        if vix<13:   score+=6;  signals.append(f"VIX {vix:.1f} low fear")
        elif vix<18: score+=2;  signals.append(f"VIX {vix:.1f} moderate")
        elif vix<25: score-=5;  signals.append(f"VIX {vix:.1f} elevated fear")
        else:        score-=10; signals.append(f"VIX {vix:.1f} HIGH FEAR")
        fn=fii.get("fii_net",0.0)
        if fn>1500:  score+=8;  signals.append(f"FII buying Rs{fn:.0f}Cr")
        elif fn>0:   score+=3;  signals.append(f"FII mild buying Rs{fn:.0f}Cr")
        elif fn<-2000:score-=8; signals.append(f"FII selling Rs{abs(fn):.0f}Cr")
        else:        score-=3;  signals.append(f"FII mild selling")
        dn=fii.get("dii_net",0.0)
        if dn>1000:  score+=5;  signals.append(f"DII buying Rs{dn:.0f}Cr")
        elif dn<-1000:score-=4; signals.append(f"DII selling Rs{abs(dn):.0f}Cr")
        dc=idx.get("DOW",{}).get("change_pct",0.0)
        if dc>1.0:   score+=4;  signals.append(f"Dow +{dc:.2f}%")
        elif dc<-1.0:score-=4;  signals.append(f"Dow {dc:.2f}%")
        return max(0.0,min(100.0,score)),signals
    def run(self):
        macro=self._fetch(); rule_score,signals=self._rule_score(macro)
        idx=macro["indices"]; fii=macro["fii_dii"]
        sp="You are a senior macro analyst for Indian capital markets. Be specific with numbers."
        up=f"""MACRO SNAPSHOT for IPO suitability:
NIFTY50: {idx.get('NIFTY50',{}).get('current',0):.0f} ({idx.get('NIFTY50',{}).get('change_pct',0):+.2f}%)
SENSEX: {idx.get('SENSEX',{}).get('current',0):.0f} | INDIA VIX: {idx.get('INDIA_VIX',{}).get('current',0):.2f}
USD/INR: {idx.get('USD_INR',{}).get('current',0):.2f} ({idx.get('USD_INR',{}).get('change_pct',0):+.2f}%)
Crude Oil: {idx.get('CRUDE_OIL',{}).get('current',0):.2f} ({idx.get('CRUDE_OIL',{}).get('change_pct',0):+.2f}%)
Gold: {idx.get('GOLD',{}).get('current',0):.2f} | US 10Y Yield: {idx.get('US_10Y',{}).get('current',0):.2f}%
Dow Jones: {idx.get('DOW',{}).get('current',0):.0f} ({idx.get('DOW',{}).get('change_pct',0):+.2f}%)
NASDAQ: {idx.get('NASDAQ',{}).get('current',0):.0f} ({idx.get('NASDAQ',{}).get('change_pct',0):+.2f}%)
FII Net: Rs{fii.get('fii_net',0):,.0f}Cr | DII Net: Rs{fii.get('dii_net',0):,.0f}Cr ({fii.get('date','N/A')})
Rule score: {rule_score:.1f}/100 | Signals: {' | '.join(signals[:4])}

Respond in EXACTLY this format:
MACRO_SCORE: [0-100]
MACRO_SIGNAL: [STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL]
MACRO_CONFIDENCE: [0-100]
MARKET_REGIME: [Bull/Bear/Sideways]
FII_VERDICT: [Accumulating/Distributing/Neutral]
VIX_RISK: [Low/Medium/High/Very_High]
LIQUIDITY_CONDITION: [Ample/Moderate/Tight]
MACRO_SUMMARY: [3 sentences on macro conditions for IPO investing today with specific data points]"""
        lt=self.llm.ask(sp,up,max_tokens=500)
        try:    ls=float(self.llm.parse(lt,"MACRO_SCORE",str(rule_score)))
        except: ls=rule_score
        try:    lc=float(self.llm.parse(lt,"MACRO_CONFIDENCE","65"))
        except: lc=65.0
        return AgentResult(self.NAME,round(rule_score*0.35+ls*0.65,1),
            self.llm.parse(lt,"MACRO_SIGNAL","HOLD"),round(lc,1),
            self.llm.parse(lt,"MACRO_SUMMARY","; ".join(signals[:3])),
            dict(macro_data=macro,rule_signals=signals,rule_score=rule_score,
                 market_regime=self.llm.parse(lt,"MARKET_REGIME","Sideways"),
                 fii_verdict=self.llm.parse(lt,"FII_VERDICT","Neutral"),
                 vix_risk=self.llm.parse(lt,"VIX_RISK","Medium"),
                 liquidity=self.llm.parse(lt,"LIQUIDITY_CONDITION","Moderate"),
                 nifty=idx.get("NIFTY50",{}),vix=idx.get("INDIA_VIX",{}),
                 fii_dii=fii,llm_raw=lt))

class SentimentAgent:
    NAME = "Sentiment Agent"
    def __init__(self,llm): self.llm=llm
    def _fetch_news(self,ipo_name):
        articles=[]
        for q in [f"{ipo_name} IPO India",f"{ipo_name} stock listing NSE"]:
            try:
                url=f"https://news.google.com/rss/search?q={q.replace(' ','+')}"\
                    f"&hl=en-IN&gl=IN&ceid=IN:en"
                r=requests.get(url,timeout=10,headers={"User-Agent":"Mozilla/5.0"})
                if r.status_code==200:
                    from bs4 import BeautifulSoup
                    soup=BeautifulSoup(r.content,"xml")
                    for item in soup.find_all("item")[:6]:
                        title=item.title.text if item.title else ""
                        source=item.source.text if item.source else "Google News"
                        if title: articles.append({"title":title,"source":source})
            except: continue
        seen=set(); unique=[]
        for a in articles:
            if a["title"] not in seen: seen.add(a["title"]); unique.append(a)
        return unique[:10]
    def _score(self,title):
        vs=VADER.polarity_scores(title)["compound"]
        try: tb=TextBlob(title).sentiment.polarity
        except: tb=0.0
        tl=title.lower()
        pos=["profit","growth","bullish","rally","surge","gain","oversubscribed","listing gain","buy","upgrade","strong"]
        neg=["loss","decline","bearish","crash","fall","weak","sell","downgrade","fraud","below issue price","investigation"]
        pc=sum(1 for k in pos if k in tl); nc=sum(1 for k in neg if k in tl)
        kw=(pc-nc)/max(pc+nc,1)
        return round(vs*0.4+tb*0.3+kw*0.3,3)
    def run(self,ipo_name):
        articles=self._fetch_news(ipo_name)
        scored=[{"title":a["title"],"source":a["source"],"score":self._score(a["title"])} for a in articles]
        avg=sum(s["score"] for s in scored)/len(scored) if scored else 0.0
        pos_c=sum(1 for s in scored if s["score"]>0.1)
        neg_c=sum(1 for s in scored if s["score"]<-0.1)
        rule_score=min(100.0,max(0.0,50.0+avg*50.0))
        headlines="\n".join([f"  [{'POS' if s['score']>0.1 else 'NEG' if s['score']<-0.1 else 'NEU'}] {s['title'][:80]}" for s in scored[:7]])
        sp="You are a financial news sentiment analyst. Analyse IPO-related news precisely."
        up=f"""SENTIMENT ANALYSIS: {ipo_name}
Articles analysed: {len(scored)} | Avg score: {avg:.3f} (-1 to +1)
Positive: {pos_c} | Negative: {neg_c} | Neutral: {len(scored)-pos_c-neg_c}
Recent headlines:
{headlines if headlines else "  No news found — treating as neutral."}
Rule score: {rule_score:.1f}/100

Respond in EXACTLY this format:
SENTIMENT_SCORE: [0-100]
SENTIMENT_SIGNAL: [STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL]
SENTIMENT_CONFIDENCE: [0-100]
INVESTOR_MOOD: [Euphoric/Positive/Neutral/Fearful/Panic]
MEDIA_COVERAGE: [High/Medium/Low]
FAKE_NEWS_RISK: [Low/Medium/High]
SENTIMENT_SUMMARY: [3 sentences on investor sentiment and media narrative for this IPO]"""
        lt=self.llm.ask(sp,up,max_tokens=500)
        try:    ls=float(self.llm.parse(lt,"SENTIMENT_SCORE",str(rule_score)))
        except: ls=rule_score
        try:    lc=float(self.llm.parse(lt,"SENTIMENT_CONFIDENCE","60"))
        except: lc=60.0
        return AgentResult(self.NAME,round(rule_score*0.35+ls*0.65,1),
            self.llm.parse(lt,"SENTIMENT_SIGNAL","HOLD"),round(lc,1),
            self.llm.parse(lt,"SENTIMENT_SUMMARY",f"Avg {avg:.3f} from {len(scored)} articles"),
            dict(articles=scored,avg_score=round(avg,3),pos_count=pos_c,neg_count=neg_c,
                 investor_mood=self.llm.parse(lt,"INVESTOR_MOOD","Neutral"),
                 media_coverage=self.llm.parse(lt,"MEDIA_COVERAGE","Low"),
                 fake_news_risk=self.llm.parse(lt,"FAKE_NEWS_RISK","Low"),llm_raw=lt))

class RiskAgent:
    NAME = "Risk Agent"; RF = 0.065
    def __init__(self,llm): self.llm=llm
    def _metrics(self,symbol,issue_price):
        try:
            hist=yf.Ticker(symbol).history(period="3mo")
            if hist.empty or len(hist)<5: return {"error":"Insufficient data"}
            close=hist["Close"]; returns=close.pct_change().dropna(); cur=float(close.iloc[-1])
            dv=_sf(returns.std()); av=dv*(252**0.5)*100; dr=_sf(returns.mean())
            sharpe=_sf((dr-(self.RF/252))/dv*(252**0.5)) if dv>0 else 0.0
            var95=_sf(np.percentile(returns,5)); var99=_sf(np.percentile(returns,1))
            cvar95=_sf(returns[returns<=var95].mean()) if len(returns[returns<=var95])>0 else var95
            cum=(1+returns).cumprod(); maxdd=_sf(((cum-cum.cummax())/cum.cummax()).min())*100
            hl=hist["High"]-hist["Low"]; hc=abs(hist["High"]-close.shift()); lc=abs(hist["Low"]-close.shift())
            atr=_sf(pd.concat([hl,hc,lc],axis=1).max(axis=1).rolling(14).mean().iloc[-1])
            stop_p=round(cur-2.0*atr,2); stop_pct=round(((stop_p-cur)/cur)*100,2)
            lg=((cur-issue_price)/issue_price)*100 if issue_price>0 else 0.0
            rc=50.0
            if av>50: rc+=25
            elif av>35: rc+=15
            elif av>20: rc+=5
            else: rc-=10
            if abs(maxdd)>30: rc+=15
            elif abs(maxdd)>20: rc+=8
            elif abs(maxdd)>10: rc+=3
            if sharpe<0: rc+=10
            elif sharpe>1.5: rc-=10
            elif sharpe>1.0: rc-=5
            invest_score=max(0.0,min(100.0,100.0-rc))
            risk_level="VERY_HIGH" if rc>80 else "HIGH" if rc>65 else "MEDIUM" if rc>45 else "LOW"
            return dict(current_price=cur,issue_price=issue_price,listing_gain=round(lg,2),
                        annual_vol=round(av,2),sharpe_ratio=round(sharpe,3),
                        var_95_pct=round(var95*100,3),var_99_pct=round(var99*100,3),
                        cvar_95_pct=round(cvar95*100,3),max_drawdown=round(maxdd,2),
                        atr=round(atr,2),stop_loss_price=stop_p,stop_loss_pct=stop_pct,
                        risk_level=risk_level,risk_composite=round(rc,1),invest_score=round(invest_score,1))
        except Exception as e: return {"error":str(e)}
    def run(self,symbol,ipo_name,issue_price):
        m=self._metrics(symbol,issue_price)
        if "error" in m:
            return AgentResult(self.NAME,50.0,"HOLD",30.0,f"Risk metrics unavailable: {m['error']}",error=m["error"])
        sp="You are a quantitative risk manager. Be specific with numbers and percentages."
        up=f"""RISK ASSESSMENT: {ipo_name} ({symbol})
Issue Price: Rs{issue_price:.2f} | Current: Rs{m['current_price']:.2f} | Listing gain: {m['listing_gain']:+.2f}%
Annual Volatility: {m['annual_vol']:.2f}% | Sharpe Ratio: {m['sharpe_ratio']:.3f}
VaR(95%,1-day): {m['var_95_pct']:.3f}% | VaR(99%,1-day): {m['var_99_pct']:.3f}%
CVaR(95%): {m['cvar_95_pct']:.3f}% | Max Drawdown: {m['max_drawdown']:.2f}%
ATR(14): Rs{m['atr']:.2f} | Suggested Stop-Loss: Rs{m['stop_loss_price']:.2f} ({m['stop_loss_pct']:+.2f}%)
Risk Level: {m['risk_level']} | Invest Score: {m['invest_score']:.1f}/100

Respond in EXACTLY this format:
RISK_SCORE: [0-100 where 100=lowest risk]
RISK_SIGNAL: [STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL]
RISK_CONFIDENCE: [0-100]
RISK_RATING: [LOW/MEDIUM/HIGH/VERY_HIGH]
RECOMMENDED_STOP_LOSS: [Rs value]
POSITION_SIZE_ADVICE: [X% of portfolio]
RISK_REWARD_RATIO: [X:Y]
RISK_SUMMARY: [3 sentences on risk-reward profile for retail IPO investor with specific numbers]"""
        lt=self.llm.ask(sp,up,max_tokens=500)
        try:    ls=float(self.llm.parse(lt,"RISK_SCORE",str(m["invest_score"])))
        except: ls=m["invest_score"]
        try:    lc=float(self.llm.parse(lt,"RISK_CONFIDENCE","70"))
        except: lc=70.0
        return AgentResult(self.NAME,round(m["invest_score"]*0.4+ls*0.6,1),
            self.llm.parse(lt,"RISK_SIGNAL","HOLD"),round(lc,1),
            self.llm.parse(lt,"RISK_SUMMARY",f"Risk {m['risk_level']}, drawdown {m['max_drawdown']:.1f}%"),
            dict(metrics=m,risk_rating=self.llm.parse(lt,"RISK_RATING",m["risk_level"]),
                 stop_loss=self.llm.parse(lt,"RECOMMENDED_STOP_LOSS",f"Rs{m['stop_loss_price']:.2f}"),
                 position_size=self.llm.parse(lt,"POSITION_SIZE_ADVICE","5%"),
                 risk_reward=self.llm.parse(lt,"RISK_REWARD_RATIO","N/A"),llm_raw=lt))

class IPOIntelligenceAgent:
    NAME = "IPO Intelligence Agent"
    def __init__(self,llm): self.llm=llm
    def _rule_score(self,issue_price,current_price,listing_price,sub_total,sub_qib,gmp,days):
        score=50.0; signals=[]
        if issue_price>0:
            lg=((listing_price-issue_price)/issue_price)*100
            cg=((current_price-issue_price)/issue_price)*100
            if lg>50:    score+=12; signals.append(f"Exceptional listing +{lg:.1f}%")
            elif lg>25:  score+=8;  signals.append(f"Strong listing +{lg:.1f}%")
            elif lg>10:  score+=4;  signals.append(f"Good listing +{lg:.1f}%")
            elif lg<-10: score-=10; signals.append(f"Below issue price {lg:.1f}%")
            elif lg<0:   score-=5;  signals.append(f"Marginal listing loss {lg:.1f}%")
            if cg>lg+5:  score+=5;  signals.append("Sustained above listing")
            elif cg<lg-10:score-=5; signals.append("Price eroded post-listing")
        if gmp>0 and issue_price>0:
            gp=(gmp/issue_price)*100
            if gp>30:   score+=10; signals.append(f"GMP {gp:.1f}% strong")
            elif gp>15: score+=6;  signals.append(f"GMP {gp:.1f}% positive")
            elif gp>0:  score+=2;  signals.append(f"GMP {gp:.1f}% mild")
        elif gmp<0 and issue_price>0:
            gp=(gmp/issue_price)*100; score-=8; signals.append(f"Negative GMP {gp:.1f}%")
        if sub_total>100:  score+=10; signals.append(f"Mega subscribed {sub_total:.0f}x")
        elif sub_total>50: score+=7;  signals.append(f"Highly subscribed {sub_total:.0f}x")
        elif sub_total>20: score+=4;  signals.append(f"Well subscribed {sub_total:.0f}x")
        elif 0<sub_total<2:score-=8;  signals.append(f"Under-subscribed {sub_total:.1f}x")
        if sub_qib>50:   score+=8; signals.append(f"QIB {sub_qib:.0f}x institutional")
        elif sub_qib>20: score+=4; signals.append(f"QIB {sub_qib:.0f}x moderate")
        elif 0<sub_qib<2:score-=6; signals.append(f"QIB {sub_qib:.1f}x low")
        if days>=90:   signals.append("90-day milestone reached")
        elif days>=60: signals.append("60-day milestone")
        elif days>=30: signals.append("30-day checkpoint")
        return max(0.0,min(100.0,score)),signals
    def run(self,ipo_name,symbol,issue_price,current_price,listing_price,
            sub_total=0.0,sub_qib=0.0,sub_retail=0.0,listing_date_str=""):
        days=0
        if listing_date_str:
            try: days=(datetime.now()-datetime.strptime(listing_date_str,"%Y-%m-%d")).days
            except: days=0
        rule_score,signals=self._rule_score(issue_price,current_price,listing_price,sub_total,sub_qib,0,days)
        lg=((listing_price-issue_price)/issue_price)*100 if issue_price>0 else 0.0
        cg=((current_price-issue_price)/issue_price)*100 if issue_price>0 else 0.0
        sp="You are India's leading IPO analyst. Provide highly specific, actionable hold/exit advice."
        up=f"""IPO INTELLIGENCE: {ipo_name} ({symbol})
Issue Price: Rs{issue_price:.2f} | Listing Price: Rs{listing_price:.2f} (Listing Gain: {lg:+.2f}%)
Current Price: Rs{current_price:.2f} (From Issue: {cg:+.2f}%) | Days since listing: {days}
Total Subscription: {sub_total:.1f}x | QIB: {sub_qib:.1f}x | Retail: {sub_retail:.1f}x
30-day milestone: {"PENDING" if days<30 else f"{cg:+.1f}% from issue"}
60-day milestone: {"PENDING" if days<60 else f"{cg:+.1f}% from issue"}
90-day milestone: {"PENDING" if days<90 else f"{cg:+.1f}% from issue"}
Rule score: {rule_score:.1f}/100 | Key signals: {' | '.join(signals[:4])}

Respond in EXACTLY this format:
IPO_SCORE: [0-100]
IPO_SIGNAL: [STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL]
IPO_CONFIDENCE: [0-100]
HOLD_OR_EXIT: [STRONG_HOLD/HOLD/PARTIAL_EXIT/EXIT/STRONG_EXIT]
HOLD_EXIT_REASON: [2 specific sentences with price levels]
TARGET_PRICE_30D: [Rs value]
TARGET_PRICE_90D: [Rs value]
STOP_LOSS_PRICE: [Rs value]
IDEAL_HOLDING_PERIOD: [X months]
LISTING_ASSESSMENT: [Outstanding/Good/Fair/Disappointing/Very_Disappointing]
IPO_SUMMARY: [3 sentences on IPO intelligence verdict with specific numbers]"""
        lt=self.llm.ask(sp,up,max_tokens=600)
        try:    ls=float(self.llm.parse(lt,"IPO_SCORE",str(rule_score)))
        except: ls=rule_score
        try:    lc=float(self.llm.parse(lt,"IPO_CONFIDENCE","65"))
        except: lc=65.0
        return AgentResult(self.NAME,round(rule_score*0.35+ls*0.65,1),
            self.llm.parse(lt,"IPO_SIGNAL","HOLD"),round(lc,1),
            self.llm.parse(lt,"IPO_SUMMARY",f"IPO gain {cg:+.1f}%, sub {sub_total:.0f}x"),
            dict(issue_price=issue_price,listing_price=listing_price,current_price=current_price,
                 listing_gain=round(lg,2),current_gain=round(cg,2),
                 sub_total=sub_total,sub_qib=sub_qib,days_since_listing=days,rule_signals=signals,
                 hold_or_exit=self.llm.parse(lt,"HOLD_OR_EXIT","HOLD"),
                 hold_exit_reason=self.llm.parse(lt,"HOLD_EXIT_REASON",""),
                 target_30d=self.llm.parse(lt,"TARGET_PRICE_30D",f"Rs{current_price*1.1:.2f}"),
                 target_90d=self.llm.parse(lt,"TARGET_PRICE_90D",f"Rs{current_price*1.2:.2f}"),
                 stop_loss=self.llm.parse(lt,"STOP_LOSS_PRICE",f"Rs{current_price*0.9:.2f}"),
                 holding_period=self.llm.parse(lt,"IDEAL_HOLDING_PERIOD","3-6 months"),
                 listing_assessment=self.llm.parse(lt,"LISTING_ASSESSMENT","Fair"),llm_raw=lt))

class OrchestratorAgent:
    WEIGHTS={"Price Movement Agent":0.20,"Macroeconomic Agent":0.15,"Sentiment Agent":0.20,"Risk Agent":0.20,"IPO Intelligence Agent":0.25}
    def __init__(self):
        self.llm=_llm; self.price_ag=PriceMovementAgent(self.llm); self.macro_ag=MacroeconomicAgent(self.llm)
        self.sent_ag=SentimentAgent(self.llm); self.risk_ag=RiskAgent(self.llm); self.ipo_ag=IPOIntelligenceAgent(self.llm)
    def _weighted_score(self,res):
        return round(sum((res[n].score if n in res and res[n].error is None else 50.0)*w for n,w in self.WEIGHTS.items()),2)
    @staticmethod
    def _decision(score):
        if score>=80: return "INVEST"
        if score>=65: return "PARTIAL_INVEST"
        if score>=45: return "HOLD"
        if score>=30: return "EXIT"
        return "STRONG_EXIT"
    def run(self,ipo_name,symbol,issue_price,listing_price,current_price=0.0,
            sub_total=0.0,sub_qib=0.0,sub_retail=0.0,listing_date_str="",progress_callback=None):
        def _p(s,m):
            if progress_callback: progress_callback(s,m)
        if current_price<=0:
            try:
                h=yf.Ticker(symbol).history(period="2d")
                current_price=float(h["Close"].iloc[-1]) if not h.empty else (listing_price or issue_price)
            except: current_price=listing_price or issue_price
        res={}
        _p(10,"Agent 1/5 — Price Movement Agent: RSI, MACD, Bollinger Bands...")
        res["Price Movement Agent"]=self.price_ag.run(symbol,ipo_name); time.sleep(0.3)
        _p(25,"Agent 2/5 — Macroeconomic Agent: NIFTY, VIX, FII/DII, global markets...")
        res["Macroeconomic Agent"]=self.macro_ag.run(); time.sleep(0.3)
        _p(45,"Agent 3/5 — Sentiment Agent: Google News RSS, VADER, TextBlob...")
        res["Sentiment Agent"]=self.sent_ag.run(ipo_name); time.sleep(0.3)
        _p(62,"Agent 4/5 — Risk Agent: VaR, CVaR, Sharpe ratio, drawdown...")
        res["Risk Agent"]=self.risk_ag.run(symbol,ipo_name,issue_price); time.sleep(0.3)
        _p(80,"Agent 5/5 — IPO Intelligence: GMP, subscription, milestones...")
        res["IPO Intelligence Agent"]=self.ipo_ag.run(ipo_name,symbol,issue_price,current_price,listing_price,sub_total,sub_qib,sub_retail,listing_date_str); time.sleep(0.3)
        overall=self._weighted_score(res); prelim=self._decision(overall)
        _p(90,"Orchestrator Agent synthesising all 5 reports into final strategy...")
        summaries="\n".join([f"  {n} (score {r.score:.1f}/100, signal {r.signal}, conf {r.confidence:.0f}%): {r.summary[:120]}" for n,r in res.items()])
        ipo_d=res.get("IPO Intelligence Agent"); risk_d=res.get("Risk Agent")
        sl_raw=ipo_d.details.get("stop_loss",f"Rs{current_price*0.9:.2f}") if ipo_d else f"Rs{current_price*0.9:.2f}"
        t90_raw=ipo_d.details.get("target_90d",f"Rs{current_price*1.2:.2f}") if ipo_d else f"Rs{current_price*1.2:.2f}"
        rl_raw=risk_d.details.get("risk_rating","MEDIUM") if risk_d else "MEDIUM"
        sp="You are a Chief Investment Officer synthesising 5 specialist AI agent reports. Be highly specific and actionable."
        up=f"""ORCHESTRATOR SYNTHESIS — IPO: {ipo_name} ({symbol})
Issue: Rs{issue_price:.2f} | Listing: Rs{listing_price:.2f} ({((listing_price-issue_price)/issue_price*100) if issue_price>0 else 0:+.1f}%)
Current: Rs{current_price:.2f} | Subscription: {sub_total:.0f}x total | QIB: {sub_qib:.0f}x
WEIGHTED COMPOSITE SCORE: {overall:.1f}/100 | PRELIMINARY DECISION: {prelim}
Agent weights: Price(20%) + Macro(15%) + Sentiment(20%) + Risk(20%) + IPO_Intel(25%)

AGENT REPORTS:
{summaries}

Synthesise into a final comprehensive strategy. Respond in EXACTLY this format:
FINAL_DECISION: [INVEST/PARTIAL_INVEST/HOLD/EXIT/STRONG_EXIT]
OVERALL_SCORE: [0-100]
FINAL_CONFIDENCE: [0-100]
ENTRY_STRATEGY: [3 sentences: specific price ranges, position sizing, entry conditions]
EXIT_STRATEGY: [3 sentences: specific targets, stop-loss levels, trailing strategy]
TARGET_PRICE: [Rs value for 3-6 month target]
STOP_LOSS: [Rs value - hard stop-loss]
RISK_LEVEL: [LOW/MEDIUM/HIGH/VERY_HIGH]
HOLDING_PERIOD: [specific duration]
INVESTMENT_THESIS: [5 sentences integrating all 5 agent signals with specific data points]
RISK_1: [Specific risk with probability and mitigation strategy]
RISK_2: [Specific risk with probability and mitigation strategy]
RISK_3: [Specific risk with probability and mitigation strategy]
CATALYST_1: [Specific upside catalyst with timeframe]
CATALYST_2: [Specific upside catalyst with timeframe]
MONITOR_1: [Specific price/event trigger requiring position review]
MONITOR_2: [Specific price/event trigger requiring position review]
MONITOR_3: [Specific price/event trigger requiring position review]"""
        lt=self.llm.ask(sp,up,max_tokens=1500)
        def _f(raw,default):
            try: nums=re.findall(r"[\d.]+",raw.replace(",","")); return float(nums[0]) if nums else default
            except: return default
        _p(100,"Multi-agent IPO analysis complete!")
        return OrchestratorResult(
            ipo_name=ipo_name,symbol=symbol,
            final_decision=self.llm.parse(lt,"FINAL_DECISION",prelim),
            overall_score=round(_f(self.llm.parse(lt,"OVERALL_SCORE",str(overall)),overall),1),
            confidence=round(_f(self.llm.parse(lt,"FINAL_CONFIDENCE","70"),70.0),1),
            entry_strategy=self.llm.parse(lt,"ENTRY_STRATEGY","N/A"),
            exit_strategy=self.llm.parse(lt,"EXIT_STRATEGY","N/A"),
            target_price=round(_f(self.llm.parse(lt,"TARGET_PRICE",t90_raw),current_price*1.15),2),
            stop_loss=round(_f(self.llm.parse(lt,"STOP_LOSS",sl_raw),current_price*0.90),2),
            risk_level=self.llm.parse(lt,"RISK_LEVEL",rl_raw),
            holding_period=self.llm.parse(lt,"HOLDING_PERIOD","3-6 months"),
            agent_scores={n:{"score":r.score,"signal":r.signal,"confidence":r.confidence,"summary":r.summary} for n,r in res.items()},
            investment_thesis=self.llm.parse(lt,"INVESTMENT_THESIS","N/A"),
            key_risks=[self.llm.parse(lt,f"RISK_{i}","") for i in range(1,4) if self.llm.parse(lt,f"RISK_{i}","") not in ("","N/A")],
            key_catalysts=[self.llm.parse(lt,f"CATALYST_{i}","") for i in range(1,3) if self.llm.parse(lt,f"CATALYST_{i}","") not in ("","N/A")],
            monitoring_triggers=[self.llm.parse(lt,f"MONITOR_{i}","") for i in range(1,4) if self.llm.parse(lt,f"MONITOR_{i}","") not in ("","N/A")])

def run_ipo_multi_agent_analysis(ipo_name,symbol,issue_price,listing_price,
    current_price=0.0,sub_total=0.0,sub_qib=0.0,sub_retail=0.0,
    listing_date_str="",progress_callback=None):
    return OrchestratorAgent().run(ipo_name=ipo_name,symbol=symbol,
        issue_price=issue_price,listing_price=listing_price,current_price=current_price,
        sub_total=sub_total,sub_qib=sub_qib,sub_retail=sub_retail,
        listing_date_str=listing_date_str,progress_callback=progress_callback)

__all__=["run_ipo_multi_agent_analysis","OrchestratorAgent","OrchestratorResult",
         "AgentResult","PriceMovementAgent","MacroeconomicAgent","SentimentAgent",
         "RiskAgent","IPOIntelligenceAgent","GroqLLM","_llm"]