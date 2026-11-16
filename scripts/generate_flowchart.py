"""
Agentic AI Flowchart - Clean rebuild with proper text fitting
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── Canvas ────────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 24, 42
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")
fig.patch.set_facecolor("#FAFAFA")
ax.set_facecolor("#FAFAFA")

# ── Palette ───────────────────────────────────────────────────────────────────
PAL = {
    "user":   ("#0D47A1", "#E3F2FD"),
    "router": ("#4A148C", "#F3E5F5"),
    "agent":  ("#BF360C", "#FBE9E7"),
    "data":   ("#004D40", "#E0F2F1"),
    "groq":   ("#880E4F", "#FCE4EC"),
    "master": ("#1A237E", "#E8EAF6"),
    "output": ("#1B5E20", "#E8F5E9"),
    "arrow":  "#37474F",
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def rect(cx, cy, w, h, text, pkey, fs=12, bold=False, wrap=True):
    """Draw a rounded rectangle with text guaranteed inside."""
    border, fill = PAL[pkey]
    patch = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.15",
        linewidth=2.2, edgecolor=border, facecolor=fill, zorder=3
    )
    ax.add_patch(patch)
    ax.text(cx, cy, text,
            ha="center", va="center",
            fontsize=fs, fontweight="bold" if bold else "normal",
            color="#111111", zorder=4,
            multialignment="center",
            linespacing=1.45)

def diamond(cx, cy, w, h, text, fs=12):
    pts = [(cx, cy+h/2), (cx+w/2, cy), (cx, cy-h/2), (cx-w/2, cy)]
    poly = plt.Polygon(pts, closed=True, linewidth=2.2,
                       edgecolor="#4A148C", facecolor="#F3E5F5", zorder=3)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center",
            fontsize=fs, fontweight="bold", color="#111111",
            zorder=4, multialignment="center")

def arr(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=PAL["arrow"],
                                lw=2.0, mutation_scale=22), zorder=2)

def section_label(cx, cy, text):
    ax.text(cx, cy, text, ha="center", va="center",
            fontsize=13, fontweight="bold", color="#4A148C")

# ─────────────────────────────────────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────────────────────────────────────
ax.text(12, 41.3, "Agentic AI Investment Hub  --  Complete Pipeline",
        ha="center", va="center", fontsize=22, fontweight="bold", color="#1A237E")
ax.text(12, 40.7, "Sarthak Nivesh  |  Aman Jain  |  B.Tech 2023-27",
        ha="center", va="center", fontsize=13, color="#546E7A")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1 -- USER INPUT
# ─────────────────────────────────────────────────────────────────────────────
rect(12, 39.8, 12, 1.1,
     "STEP 1:  USER  --  Types an Investment Query\n"
     "Example:  'Which stocks should I buy today?'",
     "user", fs=13, bold=True)
arr(12, 39.25, 12, 38.45)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2 -- QUERY ROUTER
# ─────────────────────────────────────────────────────────────────────────────
rect(12, 38.0, 14, 0.9,
     "STEP 2:  QUERY ROUTER  (FastAPI  /api/agentic/run)\n"
     "Receives query  |  Selects agents  |  Starts pipeline",
     "router", fs=12, bold=True)
arr(12, 37.55, 12, 36.85)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3 -- 6 AGENTS
# ─────────────────────────────────────────────────────────────────────────────
section_label(12, 36.6, "STEP 3:  6 SPECIALIST AGENTS RUN IN PARALLEL")

AGENTS = [
    ("STOCK INTELLIGENCE\nAGENT",
     "- Fetches live prices (fast_info)\n- Computes RSI, MACD, Bollinger\n- BUY / HOLD / SELL signals\n- Covers 15 NSE stocks",
     4.5, 35.1),
    ("MARKET ANALYSIS\nAGENT",
     "- NIFTY 50 & SENSEX live price\n- Sector performance heatmap\n- Best & worst sectors today\n- Market mood assessment",
     12.0, 35.1),
    ("SMART MONEY\nAGENT",
     "- NSE official API (live)\n- FII & DII net flows today\n- STRONG BUY / SELL signal\n- Institutional activity",
     19.5, 35.1),
    ("NEWS & SENTIMENT\nAGENT",
     "- Live RSS feeds (ET, Google)\n- VADER sentiment scoring\n- Positive / Negative / Neutral\n- Market mood from headlines",
     4.5, 31.8),
    ("RISK MANAGEMENT\nAGENT",
     "- 1-year volatility per stock\n- VaR at 95% confidence\n- Portfolio correlation matrix\n- Risk: Low / Medium / High",
     12.0, 31.8),
    ("ADVANCED ANALYTICS\nAGENT",
     "- Unusual volume detection\n- Sector rotation signals\n- 1-week & 1-month momentum\n- Breakout / Breakdown alerts",
     19.5, 31.8),
]

for title, desc, cx, cy in AGENTS:
    rect(cx, cy, 6.5, 2.5, title + "\n\n" + desc, "agent", fs=10.5)
    arr(12, 36.35, cx, cy + 1.25)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4 -- DATA SOURCES
# ─────────────────────────────────────────────────────────────────────────────
section_label(12, 30.35, "STEP 4:  LIVE DATA SOURCES  (All Real-Time, Zero Dummy Data)")

SOURCES = [
    ("Yahoo Finance\nfast_info API\nLive stock prices", 3.0),
    ("NSE India\nOfficial API\nFII / DII flows", 7.5),
    ("AMFI NAV File\n+ mfapi.in\nMF returns", 12.0),
    ("Google Finance\n+ ET RSS Feeds\nLive news", 16.5),
    ("1-Year History\nPrice Data\nRisk metrics", 21.0),
]
for text, cx in SOURCES:
    rect(cx, 29.5, 3.8, 1.3, text, "data", fs=10.5)

for _, _, acx, acy in AGENTS:
    arr(acx, acy - 1.25, acx, 30.2)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5 -- GROQ AI
# ─────────────────────────────────────────────────────────────────────────────
arr(12, 28.85, 12, 28.1)
rect(12, 27.65, 16, 0.9,
     "STEP 5:  GROQ LLAMA 3.3 70B  --  AI Analysis for Each Agent\n"
     "Live data packed into structured prompt  -->  Expert analysis generated per domain",
     "groq", fs=12, bold=True)
arr(12, 27.2, 12, 26.45)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6 -- AGENT REPORTS
# ─────────────────────────────────────────────────────────────────────────────
rect(12, 26.0, 16, 0.9,
     "STEP 6:  6 AGENT REPORTS COLLECTED\n"
     "Each report contains:  Live data  +  AI analysis  +  Status (complete / error)",
     "router", fs=12, bold=True)
arr(12, 25.55, 12, 24.8)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7 -- MASTER REPORT AGENT
# ─────────────────────────────────────────────────────────────────────────────
rect(12, 24.35, 16, 0.9,
     "STEP 7:  MASTER REPORT AGENT  --  Groq Llama 3.3 70B\n"
     "Reads all 6 agent reports  -->  Synthesises into one complete investment report",
     "master", fs=12, bold=True)
arr(12, 23.9, 12, 23.15)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 8 -- REPORT SECTIONS
# ─────────────────────────────────────────────────────────────────────────────
section_label(12, 22.9, "STEP 8:  MASTER REPORT  --  6 STRUCTURED SECTIONS")

SECTIONS = [
    ("1. EXECUTIVE\nSUMMARY\nOverall market verdict\nin 2-3 sentences",       4.0, 21.5),
    ("2. TOP 3\nOPPORTUNITIES\nSpecific stocks/sectors\nwith reasoning",       9.5, 21.5),
    ("3. KEY RISKS\nTO WATCH\n3 specific risks\nfrom live data",              15.0, 21.5),
    ("4. SMART MONEY\nSIGNAL\nFII/DII interpretation\nfor retail investors",  20.5, 21.5),
    ("5. ACTION PLAN\n3 concrete steps\nto take today\nbased on data",         7.0, 19.0),
    ("6. CONFIDENCE\nLEVEL\nHigh / Medium / Low\nwith reasoning",             17.0, 19.0),
]
for text, cx, cy in SECTIONS:
    rect(cx, cy, 4.8, 1.9, text, "master", fs=10.5)
    arr(12, 22.65, cx, cy + 0.95)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 9 -- CHARTS
# ─────────────────────────────────────────────────────────────────────────────
arr(12, 18.05, 12, 17.3)
rect(12, 16.85, 16, 0.9,
     "STEP 9:  INTERACTIVE CHARTS  (Plotly.js in React)\n"
     "Stock % change  |  RSI scatter  |  Sector heatmap  |  Sentiment pie  |  Volatility  |  FII gauge",
     "data", fs=12, bold=True)
arr(12, 16.4, 12, 15.65)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 10 -- FINAL OUTPUT
# ─────────────────────────────────────────────────────────────────────────────
rect(12, 15.2, 16, 0.9,
     "STEP 10:  FINAL OUTPUT  --  React Dashboard\n"
     "Agent status cards  |  7 interactive charts  |  Complete Master Investment Report",
     "output", fs=12, bold=True)
arr(12, 14.75, 12, 14.0)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 11 -- DECISION
# ─────────────────────────────────────────────────────────────────────────────
diamond(12, 13.4, 9, 1.1,
        "User Reviews Report\nand Makes Investment Decision", fs=12)

arr(8.0, 13.4, 5.0, 12.1)
arr(12.0, 12.85, 12.0, 12.1)
arr(16.0, 13.4, 19.0, 12.1)

rect(5.0, 11.55, 5.5, 1.0,
     "BUY\nInvest in recommended\nstocks or sectors", "output", fs=11)
rect(12.0, 11.55, 5.5, 1.0,
     "HOLD\nMonitor portfolio\nwith stop loss set", "data", fs=11)
rect(19.0, 11.55, 5.5, 1.0,
     "ASK AGAIN\nRefine query and\nrun agents again", "router", fs=11)

# ─────────────────────────────────────────────────────────────────────────────
# TIMING
# ─────────────────────────────────────────────────────────────────────────────
rect(12, 10.4, 16, 0.8,
     "Total Pipeline Time:  60 to 120 seconds  |  All data is 100% Real-Time  |  Zero Dummy Data",
     "data", fs=12, bold=True)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 12 -- CONFIDENCE SCORES  (Real scores from live data)
# ─────────────────────────────────────────────────────────────────────────────
# Section header box
rect(12, 9.55, 20, 0.75,
     "STEP 12:  REAL-TIME CONFIDENCE SCORES  (Computed from Live Data Quality)",
     "master", fs=13, bold=True)

# Individual agent scores
AGENT_SCORES = [
    ("Stock Intelligence Agent",  100.0, "15 / 15 stocks returned live price via fast_info"),
    ("Market Analysis Agent",     100.0, "NIFTY 50 and SENSEX both confirmed live"),
    ("Smart Money Agent",          95.0, "NSE FII/DII API live  (5% deducted for occasional downtime)"),
    ("News Sentiment Agent",      100.0, "Both RSS feeds returning fresh articles"),
    ("Risk Management Agent",     100.0, "8 / 8 stocks have full 1-year historical data"),
    ("Advanced Analytics Agent",  100.0, "8 / 8 stocks have valid volume data"),
]

ROW_H   = 0.82
START_Y = 8.9
BAR_X   = 7.5
BAR_W   = 8.0
LABEL_X = 1.2
PCT_X   = 16.0
NOTE_X  = 16.8

for i, (name, score, note) in enumerate(AGENT_SCORES):
    y = START_Y - i * ROW_H

    # Agent name label
    ax.text(LABEL_X, y, name + ":", fontsize=11, fontweight="bold",
            va="center", ha="left", color="#1A1A1A")

    # Background bar
    bg = FancyBboxPatch((BAR_X, y - 0.22), BAR_W, 0.44,
                        boxstyle="round,pad=0.03",
                        linewidth=1.2, edgecolor="#BDBDBD", facecolor="#E0E0E0", zorder=3)
    ax.add_patch(bg)

    # Filled bar
    fill_color = "#2E7D32" if score >= 100 else "#388E3C" if score >= 90 else "#F57F17"
    fill_w = BAR_W * score / 100
    fill = FancyBboxPatch((BAR_X, y - 0.22), fill_w, 0.44,
                          boxstyle="round,pad=0.03",
                          linewidth=0, facecolor=fill_color, zorder=4)
    ax.add_patch(fill)

    # Score % text inside bar
    ax.text(BAR_X + fill_w/2, y, f"{score:.0f}%",
            fontsize=11, fontweight="bold", va="center", ha="center",
            color="white", zorder=5)

    # Note text
    ax.text(NOTE_X, y, note, fontsize=10, va="center", ha="left",
            color="#37474F")

# Separator line
ax.plot([1.0, 23.0], [3.95, 3.95], color="#BDBDBD", linewidth=1.2, zorder=2)

# Overall score box
overall_rect = FancyBboxPatch((2.5, 3.1), 19.0, 0.75,
                               boxstyle="round,pad=0.12",
                               linewidth=3, edgecolor="#1B5E20", facecolor="#C8E6C9", zorder=3)
ax.add_patch(overall_rect)
ax.text(12, 3.47,
        "OVERALL AGENTIC AI CONFIDENCE SCORE:   99.0%   --   HIGH CONFIDENCE",
        ha="center", va="center", fontsize=15, fontweight="bold",
        color="#1B5E20", zorder=4)

# Score explanation
rect(12, 2.55, 20, 0.75,
     "How score is calculated:  (Data availability x Weight)  --  "
     "Stock 25% + Market 20% + Smart Money 20% + News 10% + Risk 15% + Analytics 10%",
     "data", fs=11)

# Disclaimer
ax.text(12, 1.85,
        "IMPORTANT:  Confidence score measures data availability and quality, NOT prediction accuracy.",
        ha="center", va="center", fontsize=11, fontweight="bold", color="#B71C1C")
ax.text(12, 1.45,
        "AI recommendations are for educational purposes only.  Always consult a SEBI-registered advisor before investing.",
        ha="center", va="center", fontsize=10.5, color="#546E7A", style="italic")

# Footer
ax.text(12, 0.75,
        "Sarthak Nivesh  --  Agentic AI Investment Hub  |  Aman Jain, B.Tech 2023-27  |  "
        "Data Sources:  NSE  |  Yahoo Finance  |  AMFI  |  Google Finance RSS",
        ha="center", va="center", fontsize=11, color="#546E7A", style="italic")

# ─────────────────────────────────────────────────────────────────────────────
# LEGEND  (bottom left, clean)
# ─────────────────────────────────────────────────────────────────────────────
LEGEND = [
    (PAL["user"][0],   PAL["user"][1],   "User / Output"),
    (PAL["router"][0], PAL["router"][1], "System / Router"),
    (PAL["agent"][0],  PAL["agent"][1],  "AI Agent"),
    (PAL["data"][0],   PAL["data"][1],   "Data Source"),
    (PAL["groq"][0],   PAL["groq"][1],   "Groq AI (LLM)"),
    (PAL["master"][0], PAL["master"][1], "Master Report"),
]
ax.text(1.2, 0.35, "LEGEND:", fontsize=11, fontweight="bold", color="#1A1A1A")
for i, (border, fill, label) in enumerate(LEGEND):
    bx = 1.2 + i * 3.7
    by = 0.05
    p = FancyBboxPatch((bx, by), 1.0, 0.22,
                       boxstyle="round,pad=0.04",
                       linewidth=1.8, edgecolor=border, facecolor=fill, zorder=3)
    ax.add_patch(p)
    ax.text(bx + 1.1, by + 0.11, label, fontsize=9.5, va="center",
            color="#1A1A1A", ha="left")

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0.3)
plt.savefig("Agentic_AI.jpg", dpi=160, bbox_inches="tight",
            facecolor="#FAFAFA", format="jpg")
plt.close()
print("Saved: Agentic_AI.jpg")
