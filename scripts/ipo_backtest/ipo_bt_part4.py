
# ─── AGENT SIGNAL GENERATION ─────────────────────────────────────────────────
def agent_price(issue, listing, sub):
    """Price Movement Agent — exact logic from PriceMovementAgent._rule_score"""
    score = 50.0
    lg = (listing - issue) / issue * 100
    if   lg > 50:   score += 12
    elif lg > 25:   score += 8
    elif lg > 10:   score += 5
    elif lg < -10:  score -= 12
    elif lg < 0:    score -= 6
    if   sub > 50:  score += 8
    elif sub > 20:  score += 5
    elif sub > 5:   score += 2
    elif sub < 2:   score -= 6
    return round(max(0.0, min(100.0, score)), 1)

def agent_macro(date_str):
    """Macroeconomic Agent — NIFTY 1-week trend around listing date"""
    try:
        ld = datetime.strptime(date_str, "%Y-%m-%d")
        s  = (ld - timedelta(days=7)).strftime("%Y-%m-%d")
        e  = (ld + timedelta(days=2)).strftime("%Y-%m-%d")
        h  = yf.Ticker("^NSEI").history(start=s, end=e)
        if h.empty or len(h) < 2:
            return 50.0
        chg = (h["Close"].iloc[-1] - h["Close"].iloc[0]) / h["Close"].iloc[0] * 100
        score = 50.0
        if   chg > 3:   score += 15
        elif chg > 1:   score += 8
        elif chg > 0:   score += 3
        elif chg < -3:  score -= 15
        elif chg < -1:  score -= 8
        else:           score -= 3
        return round(max(0.0, min(100.0, score)), 1)
    except Exception:
        return 50.0

def agent_sentiment(name):
    """Sentiment Agent — Google News RSS + VADER + TextBlob"""
    try:
        from bs4 import BeautifulSoup
        q   = name.replace(" ", "+") + "+IPO+India"
        url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
        r   = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return 50.0
        soup   = BeautifulSoup(r.content, "xml")
        titles = [t.title.text for t in soup.find_all("item")[:8] if t.title]
        if not titles:
            return 50.0
        scores = []
        for t in titles:
            vs = VADER.polarity_scores(t)["compound"]
            try:    tb = TextBlob(t).sentiment.polarity
            except: tb = 0.0
            tl  = t.lower()
            pos = sum(1 for k in ["gain","profit","surge","rally","oversubscribed","bullish","listing"] if k in tl)
            neg = sum(1 for k in ["loss","crash","below","bearish","fraud","fall","weak"] if k in tl)
            kw  = (pos - neg) / max(pos + neg, 1)
            scores.append(vs * 0.4 + tb * 0.3 + kw * 0.3)
        avg = sum(scores) / len(scores)
        return round(max(0.0, min(100.0, 50.0 + avg * 50.0)), 1)
    except Exception:
        return 50.0

def agent_risk(issue, listing, sub):
    """Risk Agent — listing risk, subscription confidence"""
    score = 50.0
    lg    = (listing - issue) / issue * 100
    if   lg > 30:   score += 15
    elif lg > 10:   score += 8
    elif lg > 0:    score += 3
    elif lg < -15:  score -= 20
    elif lg < -5:   score -= 12
    else:           score -= 6
    if   sub > 100: score += 10
    elif sub > 50:  score += 6
    elif sub > 10:  score += 3
    elif sub < 2:   score -= 8
    return round(max(0.0, min(100.0, score)), 1)

def agent_ipo(issue, listing, sub, qib):
    """IPO Intelligence Agent — GMP proxy, QIB endorsement, subscription"""
    score = 50.0
    lg    = (listing - issue) / issue * 100
    if   lg > 50:   score += 12
    elif lg > 25:   score += 8
    elif lg > 10:   score += 5
    elif lg < -10:  score -= 12
    elif lg < 0:    score -= 6
    if   qib > 100: score += 12
    elif qib > 50:  score += 8
    elif qib > 20:  score += 4
    elif qib < 5:   score -= 8
    elif qib < 2:   score -= 12
    if   sub > 50:  score += 5
    elif sub > 20:  score += 3
    elif sub < 2:   score -= 5
    return round(max(0.0, min(100.0, score)), 1)

def orchestrator(ps, ms, ss, rs, is_):
    """Orchestrator — weighted: Price(20)+Macro(15)+Sent(20)+Risk(20)+IPO(25)"""
    return round(ps*0.20 + ms*0.15 + ss*0.20 + rs*0.20 + is_*0.25, 1)

def to_signal(score):
    if   score >= 80: return "STRONG_BUY"
    elif score >= 65: return "BUY"
    elif score >= 45: return "HOLD"
    elif score >= 30: return "SELL"
    else:             return "STRONG_SELL"

def to_decision(score):
    if   score >= 80: return "INVEST"
    elif score >= 65: return "PARTIAL_INVEST"
    elif score >= 45: return "HOLD"
    elif score >= 30: return "EXIT"
    else:             return "STRONG_EXIT"

print("[4/9] Computing agent signals for all 25 IPOs...")
for i, row in df.iterrows():
    ps  = agent_price(row["issue"], row["listing"], row["sub"])
    ms  = agent_macro(row["date"])
    ss  = agent_sentiment(row["name"])
    rs  = agent_risk(row["issue"], row["listing"], row["sub"])
    is_ = agent_ipo(row["issue"], row["listing"], row["sub"], row["qib"])
    oc  = orchestrator(ps, ms, ss, rs, is_)
    df.at[i, "sc_price"]  = ps
    df.at[i, "sc_macro"]  = ms
    df.at[i, "sc_sent"]   = ss
    df.at[i, "sc_risk"]   = rs
    df.at[i, "sc_ipo"]    = is_
    df.at[i, "sc_orch"]   = oc
    df.at[i, "signal"]    = to_signal(oc)
    df.at[i, "decision"]  = to_decision(oc)
    df.at[i, "win_90d"]   = 1 if row["ret_90d"] > 0 else 0

AGENT_COLS = ["sc_price","sc_macro","sc_sent","sc_risk","sc_ipo","sc_orch"]
for c in AGENT_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce")

print("[4/9] Agent signals computed")
print("Signal distribution:")
print(df["signal"].value_counts().to_string())
print(f"Avg Orchestrator score : {df.sc_orch.mean():.1f}/100")
print(f"Overall accuracy (90d) : {df.win_90d.mean()*100:.1f}%")
