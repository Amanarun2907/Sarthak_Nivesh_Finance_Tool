
import sys, subprocess, os, warnings, json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats

for p in ['yfinance','pandas','numpy','matplotlib','seaborn',
          'requests','beautifulsoup4','vaderSentiment','textblob','scipy','nbformat']:
    subprocess.run([sys.executable,'-m','pip','install',p,'-q'],capture_output=True)

import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import seaborn as sns
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

warnings.filterwarnings("ignore")
VADER = SentimentIntensityAnalyzer()
OUT   = "research"
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor":"white","axes.facecolor":"#F8F9FA",
    "axes.grid":True,"grid.alpha":0.3,"grid.color":"#CCCCCC",
    "font.family":"DejaVu Sans","font.size":11,
    "axes.titlesize":13,"axes.titleweight":"bold","axes.labelsize":11,
    "figure.dpi":130,"savefig.dpi":150,"savefig.bbox":"tight",
})
C = {"buy":"#00BFFF","strong_buy":"#00C853","hold":"#FF8F00",
     "sell":"#FF4757","strong_sell":"#B71C1C",
     "price":"#00BCD4","macro":"#4CAF50","sentiment":"#FFC107",
     "risk":"#9C27B0","ipo":"#FF5722","orch":"#FFC300",
     "win":"#43A047","loss":"#E53935"}

print("[1/9] Setup complete — all libraries loaded")



# ─── IPO DATASET ─────────────────────────────────────────────────────────────
RAW = [
    ("LIC",             "LICI.NS",       949,  872,   2.95,  2.83,  "2022-05-17"),
    ("Paytm",           "PAYTM.NS",      2150, 1955,  1.89,  2.79,  "2021-11-18"),
    ("Nykaa",           "NYKAA.NS",      1125, 2001,  82.0,  91.2,  "2021-11-10"),
    ("Zomato",          "ZOMATO.NS",     76,   116,   38.25, 51.8,  "2021-07-23"),
    ("Delhivery",       "DELHIVERY.NS",  487,  493,   1.63,  2.22,  "2022-05-24"),
    ("Adani Wilmar",    "AWL.NS",        230,  227,   17.5,  7.62,  "2022-02-08"),
    ("Devyani Intl",    "DEVYANI.NS",    90,   140,   116.7, 144.5, "2021-08-16"),
    ("Policybazaar",    "POLICYBZR.NS",  980,  1150,  16.6,  22.5,  "2021-11-15"),
    ("Paradeep Phos",   "PARADEEP.NS",   42,   50,    107.1, 153.4, "2022-05-12"),
    ("Rainbow Childrn", "RAINBOW.NS",    542,  628,   43.0,  50.2,  "2022-05-10"),
    ("Campus Activwear","CAMPUS.NS",     292,  370,   51.75, 68.5,  "2022-04-28"),
    ("Vedant Fashions", "MANYAVAR.NS",   866,  1008,  66.0,  98.2,  "2022-02-16"),
    ("Medplus Health",  "MEDPLUS.NS",    796,  1008,  52.6,  64.3,  "2021-12-23"),
    ("Go Fashion",      "GOCOLORS.NS",   690,  1035,  135.5, 176.3, "2021-11-30"),
    ("Latent View",     "LATENTVIEW.NS", 197,  512,   326.5, 409.1, "2021-11-23"),
    ("Fino Payments",   "FINOPB.NS",     577,  544,   2.6,   3.4,   "2021-11-12"),
    ("Ethos Ltd",       "ETHOS.NS",      878,  1200,  9.4,   13.5,  "2022-05-30"),
    ("Hyundai India",   "HYUNDAI.NS",    1960, 1934,  17.4,  36.5,  "2024-10-22"),
    ("Bajaj Hsg Fin",   "BAJAJHFL.NS",   70,   150,   67.4,  208.0, "2024-09-16"),
    ("Swiggy",          "SWIGGY.NS",     390,  420,   3.6,   6.0,   "2024-11-13"),
    ("Ola Electric",    "OLAELEC.NS",    76,   76,    4.27,  5.5,   "2024-08-09"),
    ("Firstcry",        "BRAINBEES.NS",  465,  596,   12.2,  18.7,  "2024-08-13"),
    ("Premier Energies","PREMIERENE.NS", 450,  910,   74.1,  120.5, "2024-09-03"),
    ("Waaree Energies", "WAAREEENER.NS", 1503, 2550,  69.5,  199.2, "2024-10-28"),
    ("NTPC Green",      "NTPCGREEN.NS",  108,  111,   2.55,  3.3,   "2024-11-27"),
]
COLS = ["name","symbol","issue","listing","sub","qib","date"]
df0 = pd.DataFrame(RAW, columns=COLS)
df0["ret_list"]     = (df0["listing"] - df0["issue"]) / df0["issue"] * 100
df0["listing_date"] = pd.to_datetime(df0["date"])
print(f"[2/9] Dataset: {len(df0)} IPOs loaded")
print(f"  Avg listing gain : {df0.ret_list.mean():.1f}%")
print(f"  Profitable IPOs  : {(df0.ret_list>0).sum()}/{len(df0)}")
print(f"  Period           : {df0.listing_date.min().date()} to {df0.listing_date.max().date()}")



# ─── FETCH POST-LISTING PRICES ───────────────────────────────────────────────
def get_price(sym, target, window=7):
    """Return closing price closest to target_dt. Returns None if unavailable."""
    try:
        s = (target - timedelta(days=window)).strftime("%Y-%m-%d")
        e = (target + timedelta(days=window)).strftime("%Y-%m-%d")
        t = yf.Ticker(sym)
        h = t.history(start=s, end=e)
        if h.empty:
            return None
        h.index = pd.to_datetime(h.index).tz_localize(None)
        idx = (h.index - pd.Timestamp(target)).abs().argmin()
        return round(float(h["Close"].iloc[idx]), 2)
    except Exception:
        return None

print("[3/9] Fetching 30/60/90-day post-listing prices from Yahoo Finance...")
recs = []
for _, row in df0.iterrows():
    ld = row["listing_date"]
    ip, lp = row["issue"], row["listing"]
    # Use wider window for potentially delisted/illiquid stocks
    p30 = get_price(row["symbol"], ld + timedelta(days=30),  window=10)
    p60 = get_price(row["symbol"], ld + timedelta(days=60),  window=10)
    p90 = get_price(row["symbol"], ld + timedelta(days=90),  window=10)
    # If all three fail, fetch the longest available history
    if p30 is None and p60 is None and p90 is None:
        try:
            days_since = (datetime.now() - ld).days
            period = "max" if days_since > 365 else "1y"
            h_all = yf.Ticker(row["symbol"]).history(period=period)
            if not h_all.empty:
                h_all.index = pd.to_datetime(h_all.index).tz_localize(None)
                close_vals = h_all["Close"]
                for days_offset, attr in [(30,"p30"),(60,"p60"),(90,"p90")]:
                    target_ts = pd.Timestamp(ld + timedelta(days=days_offset))
                    if target_ts < pd.Timestamp(datetime.now()):
                        valid = close_vals[close_vals.index <= target_ts + timedelta(days=15)]
                        if not valid.empty:
                            locals()[attr] = round(float(valid.iloc[-1]), 2)
        except Exception:
            pass
    recs.append({
        "name":    row["name"],   "symbol": row["symbol"],
        "issue":   ip,            "listing": lp,
        "sub":     row["sub"],    "qib":     row["qib"],
        "date":    row["date"],
        "p30":  p30 if p30 else lp,
        "p60":  p60 if p60 else (p30 if p30 else lp),
        "p90":  p90 if p90 else (p60 if p60 else (p30 if p30 else lp)),
        "ret_list": round((lp - ip) / ip * 100, 2),
        "ret_30d":  round((p30 - ip) / ip * 100, 2) if p30 else round((lp - ip) / ip * 100, 2),
        "ret_60d":  round((p60 - ip) / ip * 100, 2) if p60 else (round((p30 - ip) / ip * 100, 2) if p30 else round((lp - ip) / ip * 100, 2)),
        "ret_90d":  round((p90 - ip) / ip * 100, 2) if p90 else (round((p60 - ip) / ip * 100, 2) if p60 else (round((p30 - ip) / ip * 100, 2) if p30 else round((lp - ip) / ip * 100, 2))),
    })

df = pd.DataFrame(recs)
print(f"[3/9] Prices fetched for {len(df)} IPOs")
print(f"  Avg 30d return : {df.ret_30d.mean():.1f}%")
print(f"  Avg 60d return : {df.ret_60d.mean():.1f}%")
print(f"  Avg 90d return : {df.ret_90d.mean():.1f}%")
print(f"  Profitable 90d : {(df.ret_90d > 0).sum()}/{len(df)}")
print(df[["name","ret_list","ret_30d","ret_60d","ret_90d"]].round(1).to_string(index=False))



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



# ─── CHART 1: IPO LISTING GAINS ──────────────────────────────────────────────
print("[5a/9] Chart 1 — IPO Listing Gains...")
df_sorted = df.sort_values("ret_list", ascending=True).reset_index(drop=True)
colors_bar = [C["win"] if x > 0 else C["loss"] for x in df_sorted["ret_list"]]

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("IPO Listing Performance — 25 Real NSE/BSE IPOs (2021–2024)",
             fontsize=15, fontweight="bold", y=1.01)

# Left: horizontal bar chart
ax = axes[0]
bars = ax.barh(df_sorted["name"], df_sorted["ret_list"],
               color=colors_bar, edgecolor="white", linewidth=0.5)
ax.axvline(0, color="black", linewidth=1.2, linestyle="--", alpha=0.6)
for bar, val in zip(bars, df_sorted["ret_list"]):
    ax.text(val + (1 if val >= 0 else -1),
            bar.get_y() + bar.get_height()/2,
            f"{val:+.1f}%", va="center", ha="left" if val >= 0 else "right",
            fontsize=8, fontweight="bold",
            color=C["win"] if val > 0 else C["loss"])
ax.set_xlabel("Listing Day Return (%)", fontweight="bold")
ax.set_title("Listing Day Returns (sorted)", fontweight="bold")
win_patch  = mpatches.Patch(color=C["win"],  label=f'Profitable ({(df_sorted.ret_list>0).sum()})')
loss_patch = mpatches.Patch(color=C["loss"], label=f'Loss ({(df_sorted.ret_list<=0).sum()})')
ax.legend(handles=[win_patch, loss_patch], fontsize=9)
ax.set_facecolor("#F8F9FA")
ax.grid(axis="x", alpha=0.3)

# Right: distribution histogram
ax2 = axes[1]
ax2.hist(df_sorted["ret_list"], bins=12, color=C["orch"], edgecolor="white",
         linewidth=0.8, alpha=0.85)
ax2.axvline(df_sorted["ret_list"].mean(), color="red", linewidth=2,
            linestyle="--", label=f'Mean: {df_sorted["ret_list"].mean():.1f}%')
ax2.axvline(0, color="black", linewidth=1.5, linestyle="-", alpha=0.5)
ax2.fill_betweenx([0, ax2.get_ylim()[1] if ax2.get_ylim()[1] > 0 else 10],
                  df_sorted["ret_list"].min(), 0, alpha=0.05, color=C["loss"])
ax2.set_xlabel("Listing Day Return (%)", fontweight="bold")
ax2.set_ylabel("Number of IPOs", fontweight="bold")
ax2.set_title("Return Distribution", fontweight="bold")
ax2.legend(fontsize=9)
ax2.set_facecolor("#F8F9FA")
stats_txt = (f"Mean: {df_sorted.ret_list.mean():.1f}%\n"
             f"Median: {df_sorted.ret_list.median():.1f}%\n"
             f"Std: {df_sorted.ret_list.std():.1f}%\n"
             f"Min: {df_sorted.ret_list.min():.1f}%\n"
             f"Max: {df_sorted.ret_list.max():.1f}%")
ax2.text(0.98, 0.97, stats_txt, transform=ax2.transAxes,
         va="top", ha="right", fontsize=9,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8))

plt.tight_layout()
p1 = os.path.join(OUT, "bt_chart1_listing_gains.png")
plt.savefig(p1, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p1}")

# ─── CHART 2: 30/60/90-DAY PERFORMANCE ───────────────────────────────────────
print("[5b/9] Chart 2 — Multi-Horizon Performance...")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("IPO Post-Listing Returns: 30-Day | 60-Day | 90-Day",
             fontsize=15, fontweight="bold", y=1.01)

horizons = [("ret_30d","30-Day Returns"), ("ret_60d","60-Day Returns"), ("ret_90d","90-Day Returns")]
for ax, (col, title) in zip(axes, horizons):
    d_s = df.sort_values(col).reset_index(drop=True)
    cols = [C["win"] if x > 0 else C["loss"] for x in d_s[col]]
    ax.barh(d_s["name"], d_s[col], color=cols, edgecolor="white", linewidth=0.4)
    ax.axvline(0, color="black", linewidth=1.2, linestyle="--", alpha=0.6)
    ax.set_xlabel("Return from Issue Price (%)", fontsize=9, fontweight="bold")
    ax.set_title(title, fontweight="bold")
    ax.tick_params(axis="y", labelsize=7.5)
    ax.set_facecolor("#F8F9FA")
    ax.grid(axis="x", alpha=0.3)
    pos = (d_s[col] > 0).sum()
    ax.text(0.02, 0.99, f"Profitable: {pos}/{len(d_s)}\nAvg: {d_s[col].mean():.1f}%",
            transform=ax.transAxes, va="top", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.9))

plt.tight_layout()
p2 = os.path.join(OUT, "bt_chart2_multihorizon.png")
plt.savefig(p2, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p2}")



# ─── CHART 3: AGENT SCORES RADAR / HEATMAP ───────────────────────────────────
print("[6a/9] Chart 3 — Agent Scores Heatmap...")

score_cols  = ["sc_price","sc_macro","sc_sent","sc_risk","sc_ipo","sc_orch"]
agent_names = ["Price\nMovement","Macro-\neconomic","Sentiment","Risk","IPO\nIntelligence","Orchestrator"]

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Agent Score Analysis — All 25 IPOs", fontsize=15, fontweight="bold")

# Left: heatmap
heat_data = df[score_cols].rename(columns=dict(zip(score_cols, agent_names)))
sns.heatmap(heat_data.set_index(df["name"]),
            ax=axes[0], cmap="RdYlGn", vmin=0, vmax=100,
            annot=True, fmt=".0f", annot_kws={"size":7},
            linewidths=0.5, cbar_kws={"label":"Score (0-100)"})
axes[0].set_title("Agent Scores per IPO (0-100)", fontweight="bold")
axes[0].set_xlabel("Agent", fontweight="bold")
axes[0].tick_params(axis="x", rotation=0, labelsize=8)
axes[0].tick_params(axis="y", labelsize=7.5)

# Right: avg agent scores comparison
avg_scores = df[score_cols].mean()
colors_ag  = [C["price"],C["macro"],C["sentiment"],C["risk"],C["ipo"],C["orch"]]
bars = axes[1].bar(agent_names, avg_scores.values, color=colors_ag,
                   edgecolor="white", linewidth=0.8, width=0.6)
axes[1].axhline(50, color="grey", linestyle="--", linewidth=1.2, alpha=0.7, label="Neutral (50)")
axes[1].axhline(65, color="green", linestyle=":", linewidth=1.5, alpha=0.7, label="BUY threshold (65)")
for bar, val in zip(bars, avg_scores.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
axes[1].set_ylim(0, 100)
axes[1].set_ylabel("Average Score", fontweight="bold")
axes[1].set_title("Average Score per Agent (all 25 IPOs)", fontweight="bold")
axes[1].legend(fontsize=9)
axes[1].set_facecolor("#F8F9FA")

plt.tight_layout()
p3 = os.path.join(OUT, "bt_chart3_agent_scores.png")
plt.savefig(p3, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p3}")

# ─── CHART 4: SIGNAL ACCURACY ─────────────────────────────────────────────────
print("[6b/9] Chart 4 — Signal Accuracy vs Actual Outcomes...")
sig_order = ["STRONG_BUY","BUY","HOLD","SELL","STRONG_SELL"]
sig_colors = [C["strong_buy"],C["buy"],C["hold"],C["sell"],C["strong_sell"]]

accuracy_data = {}
for sig in sig_order:
    sub_df = df[df["signal"] == sig]
    if len(sub_df) > 0:
        acc = sub_df["win_90d"].mean() * 100
        cnt = len(sub_df)
        accuracy_data[sig] = {"accuracy": acc, "count": cnt}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Signal Accuracy Analysis — Framework vs Benchmark", fontsize=15, fontweight="bold")

# Left: accuracy per signal
sigs_present = [s for s in sig_order if s in accuracy_data]
accs  = [accuracy_data[s]["accuracy"] for s in sigs_present]
cnts  = [accuracy_data[s]["count"]    for s in sigs_present]
scols = [C[s.lower()] for s in sigs_present]
bars  = axes[0].bar(sigs_present, accs, color=scols, edgecolor="white", width=0.6)
axes[0].axhline(50, color="grey", linestyle="--", alpha=0.6, linewidth=1.2, label="Random (50%)")
axes[0].axhline(df["win_90d"].mean()*100, color="navy", linestyle="-.",
                linewidth=1.5, alpha=0.7,
                label=f'Overall ({df["win_90d"].mean()*100:.0f}%)')
for bar, val, cnt in zip(bars, accs, cnts):
    axes[0].text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 1,
                 f"{val:.0f}%\n(n={cnt})", ha="center", va="bottom", fontsize=9)
axes[0].set_ylim(0, 110)
axes[0].set_ylabel("90-Day Win Rate (%)", fontweight="bold")
axes[0].set_title("Accuracy by Signal Type", fontweight="bold")
axes[0].legend(fontsize=8)
axes[0].tick_params(axis="x", rotation=15)
axes[0].set_facecolor("#F8F9FA")

# Middle: score vs 90d return scatter
sc2 = axes[1]
sc2.scatter(df["sc_orch"], df["ret_90d"],
            c=[C["win"] if w else C["loss"] for w in df["win_90d"]],
            s=80, alpha=0.8, edgecolors="white", linewidth=0.5)
if len(df) > 2:
    z   = np.polyfit(df["sc_orch"], df["ret_90d"], 1)
    p   = np.poly1d(z)
    xs  = np.linspace(df["sc_orch"].min(), df["sc_orch"].max(), 100)
    sc2.plot(xs, p(xs), color="navy", linewidth=2, linestyle="--", label="Trend line")
    r, pv = stats.pearsonr(df["sc_orch"], df["ret_90d"])
    sc2.text(0.05, 0.93, f"Pearson r = {r:.3f}\np-value  = {pv:.4f}",
             transform=sc2.transAxes, fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.9))
sc2.axhline(0, color="black", linewidth=1, linestyle="-", alpha=0.4)
sc2.axvline(65, color="green", linewidth=1.2, linestyle=":", alpha=0.6, label="BUY threshold (65)")
sc2.set_xlabel("Orchestrator Score (0-100)", fontweight="bold")
sc2.set_ylabel("Actual 90-Day Return (%)", fontweight="bold")
sc2.set_title("Score vs Actual Return (Correlation)", fontweight="bold")
sc2.legend(fontsize=8)
for _, row in df.iterrows():
    sc2.annotate(row["name"][:8], (row["sc_orch"], row["ret_90d"]),
                 textcoords="offset points", xytext=(3,3), fontsize=6.5, alpha=0.7)
sc2.set_facecolor("#F8F9FA")

# Right: decision distribution pie
dec_counts = df["decision"].value_counts()
dec_colors_map = {"INVEST":C["strong_buy"],"PARTIAL_INVEST":C["buy"],
                  "HOLD":C["hold"],"EXIT":C["sell"],"STRONG_EXIT":C["strong_sell"]}
pie_colors = [dec_colors_map.get(d, "grey") for d in dec_counts.index]
wedges, texts, autotexts = axes[2].pie(
    dec_counts.values, labels=dec_counts.index, colors=pie_colors,
    autopct="%1.0f%%", startangle=90, pctdistance=0.75,
    wedgeprops=dict(edgecolor="white", linewidth=1.5))
for at in autotexts: at.set_fontsize(9); at.set_fontweight("bold")
axes[2].set_title("Decision Distribution (Orchestrator)", fontweight="bold")

plt.tight_layout()
p4 = os.path.join(OUT, "bt_chart4_accuracy.png")
plt.savefig(p4, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p4}")



# ─── CHART 5: PORTFOLIO SIMULATION ───────────────────────────────────────────
print("[7/9] Chart 5 — Portfolio Simulation...")

INITIAL_CAPITAL = 100000  # Rs 1,00,000

def simulate_portfolio(df, strategy, label):
    """Simulate strategy: 'buy_buy_signals' or 'buy_all' (benchmark)."""
    capital    = INITIAL_CAPITAL
    trades     = []
    alloc_per  = INITIAL_CAPITAL / len(df)

    for _, row in df.iterrows():
        if strategy == "framework":
            if row["signal"] not in ("STRONG_BUY", "BUY"):
                trades.append({"name": row["name"], "ret": 0.0, "active": False})
                continue
        # Invest alloc_per in this IPO
        ret_90   = row["ret_90d"] / 100.0
        pnl      = alloc_per * ret_90
        trades.append({"name": row["name"], "ret": ret_90 * 100, "pnl": pnl, "active": True})

    active_trades = [t for t in trades if t.get("active", True)]
    if not active_trades:
        return pd.DataFrame(trades), 0, 0

    # Cumulative portfolio value over time (sort by date)
    df_sorted = df.sort_values("date").reset_index(drop=True)
    portfolio_value = [INITIAL_CAPITAL]
    running = INITIAL_CAPITAL

    for _, row in df_sorted.iterrows():
        if strategy == "framework" and row["signal"] not in ("STRONG_BUY", "BUY"):
            continue
        invested = alloc_per
        gain     = invested * (row["ret_90d"] / 100.0)
        running += gain
        portfolio_value.append(running)

    total_return = (running - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100
    return pd.DataFrame(trades), total_return, portfolio_value

_, fw_ret, fw_vals   = simulate_portfolio(df, "framework",  "Framework (BUY signals only)")
_, bh_ret, bh_vals   = simulate_portfolio(df, "benchmark",  "Buy-and-Hold All IPOs")

# Individual IPO QIB-based strategy
qib_df = df[df["qib"] > 20].copy()
qib_ret = qib_df["ret_90d"].mean()

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("Portfolio Backtesting — Framework vs Benchmark Strategies\n"
             "Initial Capital: ₹1,00,000 | Horizon: 90-Day Post-Listing",
             fontsize=14, fontweight="bold")

# Top-left: portfolio growth comparison
ax0 = axes[0][0]
strategies = {
    "Framework\n(BUY/STRONG_BUY)": (fw_vals, C["strong_buy"]),
    "Buy-All\n(Benchmark)":         (bh_vals, C["sell"]),
}
for label, (vals, color) in strategies.items():
    xs = range(len(vals))
    ax0.plot(xs, vals, color=color, linewidth=2.5, marker="o", markersize=4, label=label)
ax0.axhline(INITIAL_CAPITAL, color="grey", linestyle="--", linewidth=1, alpha=0.6,
            label="Initial Capital")
ax0.set_xlabel("Number of IPOs Traded", fontweight="bold")
ax0.set_ylabel("Portfolio Value (₹)", fontweight="bold")
ax0.set_title("Portfolio Growth: Framework vs Benchmark", fontweight="bold")
ax0.legend(fontsize=9)
ax0.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
ax0.set_facecolor("#F8F9FA")

# Annotate final values
for label, (vals, color) in strategies.items():
    ax0.annotate(f"₹{vals[-1]:,.0f}",
                 xy=(len(vals)-1, vals[-1]),
                 xytext=(-40, 10), textcoords="offset points",
                 fontsize=9, fontweight="bold", color=color,
                 arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

# Top-right: return per IPO comparison
ax1 = axes[0][1]
x_idx  = np.arange(len(df))
width  = 0.38
bars_fw = ax1.bar(x_idx - width/2, df.sort_values("date").ret_90d,
                  width=width, color=[C["win"] if r > 0 else C["loss"]
                                      for r in df.sort_values("date").ret_90d],
                  alpha=0.8, label="Actual 90d Return", edgecolor="white")
ax1.axhline(0, color="black", linewidth=1, linestyle="-", alpha=0.4)
ax1.set_xticks(x_idx)
ax1.set_xticklabels(df.sort_values("date").name.str[:8], rotation=45, ha="right", fontsize=7)
ax1.set_ylabel("Return from Issue Price (%)", fontweight="bold")
ax1.set_title("Individual IPO 90-Day Returns", fontweight="bold")
ax1.legend(fontsize=9)
ax1.set_facecolor("#F8F9FA")
ax1.axhline(df.ret_90d.mean(), color="navy", linestyle="--", linewidth=1.5,
            alpha=0.7, label=f"Avg: {df.ret_90d.mean():.1f}%")

# Bottom-left: strategy comparison bar
ax2 = axes[1][0]
strat_labels  = ["Framework\n(BUY signals)", "Buy-All\n(Benchmark)", "QIB>20x\nFilter"]
strat_returns = [fw_ret, bh_ret, qib_ret]
strat_colors  = [C["strong_buy"], C["sell"], C["orch"]]
bars_s = ax2.bar(strat_labels, strat_returns, color=strat_colors,
                 edgecolor="white", width=0.5)
ax2.axhline(0, color="black", linewidth=1.2, linestyle="-", alpha=0.4)
for bar, val in zip(bars_s, strat_returns):
    ax2.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + (0.5 if val >= 0 else -2),
             f"{val:+.1f}%", ha="center", va="bottom",
             fontsize=12, fontweight="bold",
             color=C["win"] if val > 0 else C["loss"])
ax2.set_ylabel("Total 90-Day Portfolio Return (%)", fontweight="bold")
ax2.set_title("Strategy Return Comparison", fontweight="bold")
ax2.set_facecolor("#F8F9FA")

# Bottom-right: win/loss distribution per signal
ax3 = axes[1][1]
sig_grp = df.groupby("signal")["win_90d"].agg(["sum","count"]).reset_index()
sig_grp["loss"] = sig_grp["count"] - sig_grp["sum"]
sig_grp = sig_grp[sig_grp["signal"].isin(sig_order)]
x3 = np.arange(len(sig_grp))
ax3.bar(x3, sig_grp["sum"],  label="Win", color=C["win"],  edgecolor="white", width=0.5)
ax3.bar(x3, sig_grp["loss"], label="Loss", color=C["loss"], edgecolor="white",
        bottom=sig_grp["sum"], width=0.5)
ax3.set_xticks(x3)
ax3.set_xticklabels(sig_grp["signal"], rotation=15, fontsize=9)
ax3.set_ylabel("Number of IPOs", fontweight="bold")
ax3.set_title("Win/Loss Count per Signal Type", fontweight="bold")
ax3.legend(fontsize=9)
ax3.set_facecolor("#F8F9FA")
for i, (_, r) in enumerate(sig_grp.iterrows()):
    rate = r["sum"]/r["count"]*100 if r["count"] > 0 else 0
    ax3.text(i, r["count"]+0.1, f"{rate:.0f}%", ha="center", va="bottom",
             fontsize=9, fontweight="bold", color="navy")

plt.tight_layout()
p5 = os.path.join(OUT, "bt_chart5_portfolio.png")
plt.savefig(p5, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p5}")



# ─── CHART 6: AGENT-WISE ACCURACY ─────────────────────────────────────────────
print("[8a/9] Chart 6 — Agent-Wise Accuracy & Correlation...")

fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle("Agent-Wise Predictive Accuracy — Score vs 90-Day Outcome",
             fontsize=15, fontweight="bold")

agent_cfg = [
    ("sc_price",  "Price Movement Agent",   C["price"]),
    ("sc_macro",  "Macroeconomic Agent",     C["macro"]),
    ("sc_sent",   "Sentiment Agent",         C["sentiment"]),
    ("sc_risk",   "Risk Agent",              C["risk"]),
    ("sc_ipo",    "IPO Intelligence Agent",  C["ipo"]),
    ("sc_orch",   "Orchestrator (Combined)", C["orch"]),
]
correlations = {}
for ax, (col, title, color) in zip(axes.flat, agent_cfg):
    win_scores  = df[df["win_90d"] == 1][col].dropna()
    loss_scores = df[df["win_90d"] == 0][col].dropna()

    ax.scatter(df[col], df["ret_90d"],
               c=[C["win"] if w else C["loss"] for w in df["win_90d"]],
               s=70, alpha=0.85, edgecolors="white", linewidth=0.5, zorder=3)

    # Trend line
    valid = df[[col, "ret_90d"]].dropna()
    if len(valid) > 2:
        z = np.polyfit(valid[col], valid["ret_90d"], 1)
        p = np.poly1d(z)
        xs = np.linspace(valid[col].min(), valid[col].max(), 100)
        ax.plot(xs, p(xs), color=color, linewidth=2, linestyle="--", alpha=0.9)
        r, pv = stats.pearsonr(valid[col], valid["ret_90d"])
        correlations[title] = r
        # accuracy: fraction where score>50 AND win
        high_score = df[df[col] > 50]
        acc = high_score["win_90d"].mean() * 100 if len(high_score) > 0 else 0
        info = f"r={r:.3f} | p={pv:.3f}\nAcc (score>50): {acc:.0f}%"
        ax.text(0.04, 0.96, info, transform=ax.transAxes,
                va="top", fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))

    ax.axhline(0, color="black", linewidth=1, linestyle="-", alpha=0.3)
    ax.axvline(50, color="grey", linewidth=1, linestyle="--", alpha=0.4)
    ax.set_xlabel(f"{title} Score", fontsize=9, fontweight="bold")
    ax.set_ylabel("90-Day Return (%)", fontsize=9, fontweight="bold")
    ax.set_title(title, fontweight="bold", color=color, fontsize=11)
    ax.set_facecolor("#F8F9FA")

    # Annotate IPO names
    for _, row in df.iterrows():
        ax.annotate(row["name"][:7],
                    (row[col], row["ret_90d"]),
                    textcoords="offset points", xytext=(3, 2),
                    fontsize=5.5, alpha=0.65)

plt.tight_layout()
p6 = os.path.join(OUT, "bt_chart6_agent_accuracy.png")
plt.savefig(p6, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p6}")

# ─── CHART 7: SUBSCRIPTION vs RETURNS ─────────────────────────────────────────
print("[8b/9] Chart 7 — Subscription & QIB vs Returns...")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Subscription Data vs Post-Listing Returns",
             fontsize=14, fontweight="bold")

# QIB vs 90d return
ax0 = axes[0]
ax0.scatter(df["qib"], df["ret_90d"],
            c=[C["win"] if w else C["loss"] for w in df["win_90d"]],
            s=80, alpha=0.85, edgecolors="white", linewidth=0.5)
if len(df) > 2:
    z = np.polyfit(df["qib"], df["ret_90d"], 1)
    p = np.poly1d(z)
    xs = np.linspace(df["qib"].min(), df["qib"].max(), 100)
    ax0.plot(xs, p(xs), color="navy", linewidth=2, linestyle="--", alpha=0.8)
    r, pv = stats.pearsonr(df["qib"], df["ret_90d"])
    ax0.text(0.04, 0.96, f"r={r:.3f} | p={pv:.3f}", transform=ax0.transAxes,
             va="top", fontsize=9,
             bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.85))
ax0.axhline(0, color="black", linewidth=1, alpha=0.4)
ax0.set_xlabel("QIB Subscription (×)", fontweight="bold")
ax0.set_ylabel("90-Day Return (%)", fontweight="bold")
ax0.set_title("QIB Subscription vs 90-Day Return", fontweight="bold")
ax0.set_facecolor("#F8F9FA")
for _, row in df.iterrows():
    ax0.annotate(row["name"][:8], (row["qib"], row["ret_90d"]),
                 textcoords="offset points", xytext=(3, 2), fontsize=6.5, alpha=0.7)

# Total sub vs listing return
ax1 = axes[1]
ax1.scatter(df["sub"], df["ret_list"],
            c=[C["win"] if w > 0 else C["loss"] for w in df["ret_list"]],
            s=80, alpha=0.85, edgecolors="white", linewidth=0.5)
if len(df) > 2:
    z2  = np.polyfit(df["sub"], df["ret_list"], 1)
    p2  = np.poly1d(z2)
    xs2 = np.linspace(df["sub"].min(), df["sub"].max(), 100)
    ax1.plot(xs2, p2(xs2), color="purple", linewidth=2, linestyle="--", alpha=0.8)
    r2, pv2 = stats.pearsonr(df["sub"], df["ret_list"])
    ax1.text(0.04, 0.96, f"r={r2:.3f} | p={pv2:.3f}", transform=ax1.transAxes,
             va="top", fontsize=9,
             bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.85))
ax1.axhline(0, color="black", linewidth=1, alpha=0.4)
ax1.set_xlabel("Total Subscription (×)", fontweight="bold")
ax1.set_ylabel("Listing Day Return (%)", fontweight="bold")
ax1.set_title("Total Subscription vs Listing-Day Return", fontweight="bold")
ax1.set_facecolor("#F8F9FA")

# Return buckets by subscription range
ax2 = axes[2]
bins = [0, 5, 20, 50, 200, 500]
labels_b = ["<5x","5-20x","20-50x","50-200x",">200x"]
df["sub_bucket"] = pd.cut(df["sub"], bins=bins, labels=labels_b)
bucket_ret = df.groupby("sub_bucket", observed=True)["ret_90d"].agg(["mean","std","count"])
x_pos = np.arange(len(bucket_ret))
cols_b = [C["strong_buy"] if m > 0 else C["loss"] for m in bucket_ret["mean"]]
ax2.bar(x_pos, bucket_ret["mean"], color=cols_b, edgecolor="white",
        width=0.6, alpha=0.85)
ax2.errorbar(x_pos, bucket_ret["mean"], yerr=bucket_ret["std"],
             fmt="none", ecolor="black", capsize=4, linewidth=1.2)
ax2.axhline(0, color="black", linewidth=1, linestyle="-", alpha=0.4)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(labels_b, fontsize=10)
ax2.set_ylabel("Avg 90-Day Return (%)", fontweight="bold")
ax2.set_title("Avg 90-Day Return by Subscription Band", fontweight="bold")
ax2.set_facecolor("#F8F9FA")
for i, (_, r) in enumerate(bucket_ret.iterrows()):
    ax2.text(i, r["mean"] + 1, f"n={int(r['count'])}", ha="center",
             va="bottom", fontsize=9, color="navy")

plt.tight_layout()
p7 = os.path.join(OUT, "bt_chart7_subscription.png")
plt.savefig(p7, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p7}")



# ─── CHART 8: RISK METRICS ────────────────────────────────────────────────────
print("[9a/9] Chart 8 — Risk Metrics & Statistical Tests...")

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle("Risk Metrics, Statistical Validation & Confidence Calibration",
             fontsize=14, fontweight="bold")

# --- Sharpe, Calmar, Max Drawdown per strategy
buy_ipos = df[df["signal"].isin(["STRONG_BUY","BUY"])]
all_ipos = df.copy()

def sharpe(returns, rf=0.065):
    r = returns / 100.0
    excess = r.mean() - rf / 12
    return (excess / r.std() * (12**0.5)) if r.std() > 0 else 0.0

def max_dd(returns):
    cum = (1 + returns/100).cumprod()
    return ((cum - cum.cummax()) / cum.cummax()).min() * 100

ax0 = axes[0][0]
strategies_comp = {
    "Framework\n(BUY signals)": buy_ipos["ret_90d"],
    "Benchmark\n(All IPOs)":    all_ipos["ret_90d"],
}
metrics = {}
for name, rets in strategies_comp.items():
    if len(rets) > 0:
        metrics[name] = {
            "Mean Return (%)":     rets.mean(),
            "Std Dev (%)":         rets.std(),
            "Sharpe Ratio":        sharpe(rets),
            "Win Rate (%)":        (rets > 0).mean() * 100,
            "Max Drawdown (%)":    max_dd(rets.reset_index(drop=True)),
        }

df_metrics = pd.DataFrame(metrics).T
x4 = np.arange(len(df_metrics.columns))
width4 = 0.35
fw_vals_m  = [df_metrics.iloc[0][c] for c in df_metrics.columns]
bh_vals_m  = [df_metrics.iloc[1][c] for c in df_metrics.columns]
ax0.bar(x4 - width4/2, fw_vals_m, width=width4,
        label="Framework", color=C["strong_buy"], edgecolor="white", alpha=0.85)
ax0.bar(x4 + width4/2, bh_vals_m, width=width4,
        label="Benchmark", color=C["sell"], edgecolor="white", alpha=0.85)
ax0.set_xticks(x4)
ax0.set_xticklabels(df_metrics.columns, rotation=20, ha="right", fontsize=8.5)
ax0.set_title("Framework vs Benchmark — Key Metrics", fontweight="bold")
ax0.legend(fontsize=9)
ax0.axhline(0, color="black", linewidth=1, alpha=0.3)
ax0.set_facecolor("#F8F9FA")
for i, (fv, bv) in enumerate(zip(fw_vals_m, bh_vals_m)):
    ax0.text(i - width4/2, fv + 0.3, f"{fv:.1f}", ha="center",
             va="bottom", fontsize=7.5, color=C["strong_buy"])
    ax0.text(i + width4/2, bv + 0.3, f"{bv:.1f}", ha="center",
             va="bottom", fontsize=7.5, color=C["sell"])

# --- T-test: BUY signal returns vs SELL/HOLD returns
ax1 = axes[0][1]
buy_group  = df[df["signal"].isin(["STRONG_BUY","BUY"])]["ret_90d"].dropna()
sell_group = df[df["signal"].isin(["SELL","STRONG_SELL","HOLD"])]["ret_90d"].dropna()
if len(buy_group) > 1 and len(sell_group) > 1:
    t_stat, p_value = stats.ttest_ind(buy_group, sell_group, equal_var=False)
    ax1.hist(buy_group,  bins=8, alpha=0.75, color=C["strong_buy"],
             label=f"BUY signals  (n={len(buy_group)}, mean={buy_group.mean():.1f}%)",
             edgecolor="white")
    ax1.hist(sell_group, bins=8, alpha=0.75, color=C["loss"],
             label=f"SELL/HOLD    (n={len(sell_group)}, mean={sell_group.mean():.1f}%)",
             edgecolor="white")
    ax1.axvline(buy_group.mean(),  color=C["strong_buy"], linewidth=2,
                linestyle="--", alpha=0.9)
    ax1.axvline(sell_group.mean(), color=C["loss"],        linewidth=2,
                linestyle="--", alpha=0.9)
    sig_str = "SIGNIFICANT" if p_value < 0.05 else "Not significant"
    ax1.text(0.05, 0.96,
             f"Welch t-test\nt = {t_stat:.3f}\np = {p_value:.4f}\n{sig_str} (α=0.05)",
             transform=ax1.transAxes, va="top", fontsize=9,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", alpha=0.9))
ax1.set_xlabel("90-Day Return (%)", fontweight="bold")
ax1.set_ylabel("Number of IPOs", fontweight="bold")
ax1.set_title("Distribution: BUY Signals vs SELL/HOLD\n(Welch's t-test)", fontweight="bold")
ax1.legend(fontsize=8)
ax1.set_facecolor("#F8F9FA")

# --- Agent score correlation heatmap
ax2 = axes[1][0]
corr_cols = ["sc_price","sc_macro","sc_sent","sc_risk","sc_ipo","sc_orch","ret_90d"]
corr_matrix = df[corr_cols].corr()
corr_labels = ["Price\nAgent","Macro\nAgent","Sentiment\nAgent","Risk\nAgent",
               "IPO\nAgent","Orchestrator","90d\nReturn"]
mask = np.zeros_like(corr_matrix, dtype=bool)
np.fill_diagonal(mask, True)
sns.heatmap(corr_matrix, ax=ax2, cmap="RdYlGn", vmin=-1, vmax=1,
            annot=True, fmt=".2f", annot_kws={"size":8.5},
            xticklabels=corr_labels, yticklabels=corr_labels,
            linewidths=0.5, cbar_kws={"label":"Pearson r"},
            mask=mask if not mask.all() else None)
ax2.set_title("Agent Score Correlation Matrix\n(Pearson r, includes 90-Day Return)",
              fontweight="bold")
ax2.tick_params(axis="x", rotation=0, labelsize=8)
ax2.tick_params(axis="y", rotation=0, labelsize=8)

# --- Confidence calibration: score deciles vs actual win rate
ax3 = axes[1][1]
df["score_decile"] = pd.qcut(df["sc_orch"], q=5,
                              labels=["0-20","20-40","40-60","60-80","80-100"],
                              duplicates="drop")
cal = df.groupby("score_decile", observed=True)["win_90d"].agg(["mean","count"]).reset_index()
cal["win_rate"] = cal["mean"] * 100
bar_cols = [C["win"] if w >= 50 else C["loss"] for w in cal["win_rate"]]
ax3.bar(cal["score_decile"].astype(str), cal["win_rate"],
        color=bar_cols, edgecolor="white", width=0.6, alpha=0.85)
ax3.axhline(50, color="grey", linestyle="--", linewidth=1.5, alpha=0.7,
            label="Random (50%)")
ax3.set_xlabel("Orchestrator Score Quintile", fontweight="bold")
ax3.set_ylabel("Actual Win Rate (%)", fontweight="bold")
ax3.set_title("Confidence Calibration\n(Higher Score → Higher Win Rate?)",
              fontweight="bold")
ax3.set_ylim(0, 115)
ax3.legend(fontsize=9)
ax3.set_facecolor("#F8F9FA")
for i, (_, r) in enumerate(cal.iterrows()):
    ax3.text(i, r["win_rate"] + 1.5, f"{r['win_rate']:.0f}%\n(n={int(r['count'])})",
             ha="center", va="bottom", fontsize=9, fontweight="bold",
             color=C["win"] if r["win_rate"] >= 50 else C["loss"])

plt.tight_layout()
p8 = os.path.join(OUT, "bt_chart8_risk_stats.png")
plt.savefig(p8, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p8}")



# ─── CHART 9: COMPREHENSIVE SUMMARY DASHBOARD ────────────────────────────────
print("[9b/9] Chart 9 — Summary Dashboard...")

fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor("white")
gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.55, wspace=0.4)
fig.suptitle("IPO Multi-Agent Framework — Backtesting Summary Dashboard\n"
             "25 Real NSE/BSE IPOs | 2021–2024 | Groq Llama 3.3 70B",
             fontsize=16, fontweight="bold", y=0.98)

# [0,0] Signal distribution
ax00 = fig.add_subplot(gs[0, 0])
sig_c = df["signal"].value_counts().reindex(sig_order, fill_value=0)
sig_colors_list = [C[s.lower()] for s in sig_order]
ax00.bar(sig_c.index, sig_c.values, color=sig_colors_list, edgecolor="white")
ax00.set_title("Signal Distribution", fontweight="bold", fontsize=11)
ax00.set_ylabel("Count")
ax00.tick_params(axis="x", rotation=20, labelsize=7.5)
ax00.set_facecolor("#F8F9FA")
for i, v in enumerate(sig_c.values):
    ax00.text(i, v + 0.05, str(v), ha="center", va="bottom", fontsize=9)

# [0,1] Return timeline
ax01 = fig.add_subplot(gs[0, 1])
df_t = df.sort_values("date").reset_index(drop=True)
ax01.plot(range(len(df_t)), df_t["ret_list"],  "o-", color=C["price"],
          linewidth=1.5, markersize=4, label="Listing Day")
ax01.plot(range(len(df_t)), df_t["ret_90d"],   "s-", color=C["ipo"],
          linewidth=1.5, markersize=4, label="90-Day")
ax01.axhline(0, color="black", linewidth=1, alpha=0.4)
ax01.fill_between(range(len(df_t)), df_t["ret_90d"], 0,
                  where=df_t["ret_90d"] > 0, alpha=0.12, color=C["win"])
ax01.fill_between(range(len(df_t)), df_t["ret_90d"], 0,
                  where=df_t["ret_90d"] <= 0, alpha=0.12, color=C["loss"])
ax01.set_title("Returns Timeline (Chronological)", fontweight="bold", fontsize=11)
ax01.set_ylabel("Return (%)")
ax01.legend(fontsize=8)
ax01.set_facecolor("#F8F9FA")
ax01.tick_params(axis="x", labelsize=7)
ax01.set_xticks(range(len(df_t)))
ax01.set_xticklabels(df_t["name"].str[:6], rotation=45, ha="right", fontsize=6)

# [0,2-3] KPI summary text box
ax02 = fig.add_subplot(gs[0, 2:])
ax02.axis("off")
buy_ipos_2 = df[df["signal"].isin(["STRONG_BUY","BUY"])]
kpis = [
    ("IPOs Analysed",            f"{len(df)}"),
    ("Avg Listing Gain",         f"{df.ret_list.mean():.1f}%"),
    ("Avg 90-Day Return",        f"{df.ret_90d.mean():.1f}%"),
    ("Framework Accuracy (90d)", f"{df.win_90d.mean()*100:.1f}%"),
    ("BUY Signal Accuracy",      f"{buy_ipos_2.win_90d.mean()*100:.1f}%" if len(buy_ipos_2)>0 else "N/A"),
    ("Best Performer",           f"{df.loc[df.ret_90d.idxmax(),'name']} ({df.ret_90d.max():.0f}%)"),
    ("Worst Performer",          f"{df.loc[df.ret_90d.idxmin(),'name']} ({df.ret_90d.min():.0f}%)"),
    ("Orch Score vs Return (r)", f"{df[['sc_orch','ret_90d']].corr().iloc[0,1]:.3f}"),
]
y_pos = 0.95
for label, val in kpis:
    # Safely determine color from the value
    try:
        # Strip everything after first space or '(' to get a clean number
        clean = val.replace("%","").replace("+","").strip()
        clean = clean.split("(")[0].strip().split(" ")[0]
        num   = float(clean)
        color = C["win"] if num > 0 else C["loss"] if num < 0 else "navy"
    except Exception:
        color = "navy"
    ax02.text(0.05, y_pos, f"• {label}:", transform=ax02.transAxes,
              fontsize=11, va="top", color="#333333", fontweight="bold")
    ax02.text(0.60, y_pos, val, transform=ax02.transAxes,
              fontsize=11, va="top", color=color, fontweight="bold")
    y_pos -= 0.115
ax02.text(0.05, 0.02, "Data: Yahoo Finance (real) | NSE/BSE Official | ipowatch.in",
          transform=ax02.transAxes, fontsize=8, color="grey", style="italic")

# [1,0-1] Listing gain waterfall
ax10 = fig.add_subplot(gs[1, 0:2])
df_wf = df.sort_values("ret_list").reset_index(drop=True)
c_wf  = [C["win"] if x > 0 else C["loss"] for x in df_wf["ret_list"]]
ax10.bar(range(len(df_wf)), df_wf["ret_list"], color=c_wf, edgecolor="white", width=0.7)
ax10.axhline(0, color="black", linewidth=1.2, alpha=0.5)
ax10.axhline(df_wf["ret_list"].mean(), color="navy", linestyle="--",
             linewidth=1.5, alpha=0.7, label=f"Mean: {df_wf['ret_list'].mean():.1f}%")
ax10.set_xticks(range(len(df_wf)))
ax10.set_xticklabels(df_wf["name"], rotation=45, ha="right", fontsize=7)
ax10.set_ylabel("Listing Day Return (%)", fontweight="bold")
ax10.set_title("Listing Day Gains — All 25 IPOs (Sorted)", fontweight="bold", fontsize=11)
ax10.legend(fontsize=9)
ax10.set_facecolor("#F8F9FA")

# [1,2-3] Orchestrator score distribution
ax12 = fig.add_subplot(gs[1, 2:])
bins_o = [0,30,45,65,80,100]
lab_o  = ["STRONG\nSELL","SELL","HOLD","BUY","STRONG\nBUY"]
col_o  = [C["strong_sell"],C["sell"],C["hold"],C["buy"],C["strong_buy"]]
counts_o = pd.cut(df["sc_orch"], bins=bins_o, labels=lab_o).value_counts().reindex(lab_o, fill_value=0)
ax12.bar(lab_o, counts_o.values, color=col_o, edgecolor="white", width=0.6)
ax12.set_ylabel("Number of IPOs", fontweight="bold")
ax12.set_title("Orchestrator Score → Signal Mapping", fontweight="bold", fontsize=11)
ax12.set_facecolor("#F8F9FA")
for i, v in enumerate(counts_o.values):
    ax12.text(i, v + 0.05, str(v), ha="center", va="bottom", fontsize=10, fontweight="bold")
ranges_txt = ["<30","30-45","45-65","65-80",">80"]
for i, rt in enumerate(ranges_txt):
    ax12.text(i, -0.3, rt, ha="center", va="top", fontsize=8, color="grey",
              transform=ax12.get_xaxis_transform())

# [2,0-3] Agent score box plot
ax20 = fig.add_subplot(gs[2, :])
score_data = [df["sc_price"].dropna().values, df["sc_macro"].dropna().values,
              df["sc_sent"].dropna().values,  df["sc_risk"].dropna().values,
              df["sc_ipo"].dropna().values,   df["sc_orch"].dropna().values]
agent_lbls = ["Price\nMovement\n(20%)","Macro-\neconomic\n(15%)",
              "Sentiment\n(20%)","Risk\n(20%)","IPO\nIntelligence\n(25%)","Orchestrator\n(Combined)"]
bp = ax20.boxplot(score_data, labels=agent_lbls, patch_artist=True,
                  boxprops=dict(linewidth=1.5),
                  medianprops=dict(color="navy", linewidth=2),
                  whiskerprops=dict(linewidth=1.2),
                  capprops=dict(linewidth=1.5),
                  flierprops=dict(marker="o", markersize=4, alpha=0.5))
box_colors = [C["price"],C["macro"],C["sentiment"],C["risk"],C["ipo"],C["orch"]]
for patch, color in zip(bp["boxes"], box_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax20.axhline(50, color="grey", linestyle="--", linewidth=1.5, alpha=0.6, label="Neutral (50)")
ax20.axhline(65, color="green", linestyle=":", linewidth=1.5, alpha=0.6, label="BUY (65)")
ax20.set_ylabel("Agent Score (0-100)", fontweight="bold")
ax20.set_title("Agent Score Distribution — Box Plot (All 25 IPOs)", fontweight="bold")
ax20.legend(fontsize=9)
ax20.set_facecolor("#F8F9FA")
ax20.set_ylim(0, 110)

p9 = os.path.join(OUT, "bt_chart9_dashboard.png")
plt.savefig(p9, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p9}")

# ─── PRINT FINAL SUMMARY ─────────────────────────────────────────────────────
buy_ipos_f = df[df["signal"].isin(["STRONG_BUY","BUY"])]
print("\n" + "="*65)
print("  IPO MULTI-AGENT BACKTESTING — FINAL RESULTS")
print("="*65)
print(f"  Total IPOs analysed     : {len(df)}")
print(f"  Period                  : 2021-07 to 2024-11")
print(f"  Data source             : Yahoo Finance (real)")
print(f"  Avg Listing-day return  : {df.ret_list.mean():.1f}%")
print(f"  Avg 30-day return       : {df.ret_30d.mean():.1f}%")
print(f"  Avg 60-day return       : {df.ret_60d.mean():.1f}%")
print(f"  Avg 90-day return       : {df.ret_90d.mean():.1f}%")
print(f"  Overall accuracy (90d)  : {df.win_90d.mean()*100:.1f}%")
if len(buy_ipos_f) > 0:
    print(f"  BUY signal accuracy     : {buy_ipos_f.win_90d.mean()*100:.1f}%")
    print(f"  BUY signal avg return   : {buy_ipos_f.ret_90d.mean():.1f}%")
corr_r = df[["sc_orch","ret_90d"]].corr().iloc[0,1]
print(f"  Orch score correlation  : r={corr_r:.3f}")
print(f"  Best performing IPO     : {df.loc[df.ret_90d.idxmax(),'name']} (+{df.ret_90d.max():.0f}%)")
print(f"  Worst performing IPO    : {df.loc[df.ret_90d.idxmin(),'name']} ({df.ret_90d.min():.0f}%)")
print("="*65)
print("\nCharts saved:")
for i in range(1, 10):
    fp = os.path.join(OUT, f"bt_chart{i}_*.png")
    import glob
    matches = glob.glob(fp)
    for m in matches:
        print(f"  {m}")
print("\n[DONE] All backtesting complete!")
