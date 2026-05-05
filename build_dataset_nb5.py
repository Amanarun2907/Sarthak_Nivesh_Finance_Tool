# coding: utf-8
import json
cells=[]

import json

def cc(src, cid):
    return {"cell_type":"code","execution_count":None,"id":cid,"metadata":{},"outputs":[],"source":[src]}
def mc(src, cid):
    return {"cell_type":"markdown","id":cid,"metadata":{},"source":[src]}

# ── PART B: REAL-TIME AGENTIC AI FRAMEWORK DATA ───────────────────────────────
cells.append(mc("""---
# PART B: Real-Time Agentic AI Framework Data Visualizations
## Data Sources Used in the Live Sarthak Nivesh Platform
""", "mB"))

# ── Chart 10: Data Source Architecture ───────────────────────────────────────
cells.append(mc("""## Chart 10 — Data Source Architecture Diagram
**What this shows:** All data sources feeding into the 6 agents and the LLM synthesis layer.
""", "m_c10"))

cells.append(cc("""
# CHART 10: Data Source Architecture
# =====================================
fig, ax = plt.subplots(figsize=(20, 12))
ax.set_xlim(0, 20); ax.set_ylim(0, 12)
ax.axis('off')
fig.patch.set_facecolor('white')
fig.suptitle('Chart 10: Data Source Architecture — Sarthak Nivesh Multi-Agent AI Framework',
             fontsize=14, fontweight='bold', y=0.98)

def draw_box(ax, x, y, w, h, text, color, fontsize=9, text_color='white'):
    rect = plt.Rectangle((x, y), w, h, facecolor=color, edgecolor='white',
                          lw=2, zorder=3, alpha=0.92)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight='bold', color=text_color,
            zorder=4, wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, color='#555555'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8))

# Data Sources (left column)
sources = [
    (0.3, 9.5, 3.5, 1.0, 'Yahoo Finance\nfast_info API\n(Live Prices)', '#1565C0'),
    (0.3, 8.0, 3.5, 1.0, 'Yahoo Finance\nHistorical OHLCV\n(3mo / 1y / 2y)', '#1976D2'),
    (0.3, 6.5, 3.5, 1.0, 'NSE India API\nFII/DII Net Flow\n(Daily)', '#0D47A1'),
    (0.3, 5.0, 3.5, 1.0, 'Google Finance RSS\nMarket Headlines\n(Real-time)', '#2E7D32'),
    (0.3, 3.5, 3.5, 1.0, 'Economic Times RSS\nMarket News\n(Real-time)', '#388E3C'),
    (0.3, 2.0, 3.5, 1.0, 'Groq Cloud API\nLLaMA 3.3 70B\n(LLM Inference)', '#6A1B9A'),
]
for x, y, w, h, text, color in sources:
    draw_box(ax, x, y, w, h, text, color, fontsize=8)

# Agents (middle column)
agents = [
    (7.5, 9.5, 3.5, 1.0, 'Agent 1\nStock Intelligence\nRSI+MACD+MA50', '#1565C0'),
    (7.5, 8.0, 3.5, 1.0, 'Agent 2\nMarket Analysis\nSector Rotation', '#2E7D32'),
    (7.5, 6.5, 3.5, 1.0, 'Agent 3\nSmart Money\nFII/DII Tracker', '#0D47A1'),
    (7.5, 5.0, 3.5, 1.0, 'Agent 4\nNews Sentiment\nVADER NLP', '#AD1457'),
    (7.5, 3.5, 3.5, 1.0, 'Agent 5\nRisk Management\nVaR 95%', '#E65100'),
    (7.5, 2.0, 3.5, 1.0, 'Agent 6\nAdvanced Analytics\nVolume Anomaly', '#00695C'),
]
for x, y, w, h, text, color in agents:
    draw_box(ax, x, y, w, h, text, color, fontsize=8)

# Master Report (right)
draw_box(ax, 14.5, 5.0, 4.5, 2.5,
         'Master Report Agent\nLLaMA 3.3 70B\n(Groq API)\n\nSynthesizes all 6\nagent outputs',
         '#37474F', fontsize=9)

# Output
draw_box(ax, 14.5, 2.0, 4.5, 2.5,
         'Structured Investment\nReport\n\n1. Executive Summary\n2. Opportunities\n3. Risks\n4. Action Plan',
         '#4A148C', fontsize=8)

# Arrows: sources to agents
arrow_map = [
    (3.8, 10.0, 7.5, 10.0),  # Yahoo fast_info -> Agent 1
    (3.8, 10.0, 7.5, 8.5),   # Yahoo fast_info -> Agent 2
    (3.8, 8.5,  7.5, 10.0),  # Yahoo hist -> Agent 1
    (3.8, 8.5,  7.5, 8.5),   # Yahoo hist -> Agent 2
    (3.8, 8.5,  7.5, 4.0),   # Yahoo hist -> Agent 5
    (3.8, 8.5,  7.5, 2.5),   # Yahoo hist -> Agent 6
    (3.8, 7.0,  7.5, 7.0),   # NSE -> Agent 3
    (3.8, 5.5,  7.5, 5.5),   # Google RSS -> Agent 4
    (3.8, 4.0,  7.5, 5.5),   # ET RSS -> Agent 4
    (3.8, 2.5,  7.5, 10.0),  # Groq -> Agent 1 (LLM)
    (3.8, 2.5,  7.5, 8.5),
    (3.8, 2.5,  7.5, 7.0),
    (3.8, 2.5,  7.5, 5.5),
    (3.8, 2.5,  7.5, 4.0),
    (3.8, 2.5,  7.5, 2.5),
]
for x1,y1,x2,y2 in arrow_map:
    draw_arrow(ax, x1, y1, x2, y2, '#AAAAAA')

# Agents to Master
for y in [10.0, 8.5, 7.0, 5.5, 4.0, 2.5]:
    draw_arrow(ax, 11.0, y, 14.5, 6.25, '#555555')

# Master to Output
draw_arrow(ax, 16.75, 5.0, 16.75, 4.5, '#4A148C')

# Labels
ax.text(2.0, 11.2, 'DATA SOURCES', ha='center', fontsize=11, fontweight='bold', color='#333333')
ax.text(9.25, 11.2, 'SPECIALIST AGENTS', ha='center', fontsize=11, fontweight='bold', color='#333333')
ax.text(16.75, 11.2, 'LLM SYNTHESIS', ha='center', fontsize=11, fontweight='bold', color='#333333')

ax.axvline(6.8, color='#CCCCCC', lw=1.5, linestyle='--', alpha=0.7)
ax.axvline(13.8, color='#CCCCCC', lw=1.5, linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('dataset_chart10_architecture.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 10 saved: dataset_chart10_architecture.png")
""", "c_chart10"))

cells.append(mc("""### Chart 10 Interpretation
- **Left column (Data Sources):** 6 distinct data sources feed the framework — Yahoo Finance (prices), NSE API (FII/DII), RSS feeds (news), and Groq API (LLM).
- **Middle column (Agents):** Each agent consumes specific data sources. Agent 1 uses Yahoo Finance prices; Agent 3 uses NSE API; Agent 4 uses RSS feeds.
- **Right column (LLM Synthesis):** All 6 agent outputs are synthesized by LLaMA 3.3 70B into a structured investment report.
- The Groq API feeds into all 6 agents (each agent calls the LLM for its narrative analysis).
""", "m_c10e"))

# ── Chart 11: Sector Map Visualization ───────────────────────────────────────
cells.append(mc("""## Chart 11 — Sector Map: Real-Time Framework vs Backtesting Universe
**What this shows:** The exact SECTOR_MAP from agentic.py and how it maps to the backtesting universe.
""", "m_c11"))

cells.append(cc("""
# CHART 11: Sector Map Comparison
# ==================================
fig, axes = plt.subplots(1, 2, figsize=(20, 9))
fig.suptitle('Chart 11: Sector Map — Real-Time Framework (agentic.py) vs Backtesting Universe',
             fontsize=13, fontweight='bold', y=1.01)

# Left: Real-time SECTOR_MAP (from agentic.py)
ax1 = axes[0]
ax1.set_xlim(0, 10); ax1.set_ylim(0, 10); ax1.axis('off')
ax1.set_title('Real-Time Framework\\n(SECTOR_MAP in agentic.py)', fontsize=11, fontweight='bold')

y_pos = 9.5
for sector, tickers in SECTOR_MAP.items():
    color = SECTOR_COLORS.get(sector, '#78909C')
    rect = plt.Rectangle((0.2, y_pos-0.55), 9.6, 0.9, facecolor=color,
                          edgecolor='white', lw=1.5, alpha=0.85)
    ax1.add_patch(rect)
    names = [t.replace('.NS','') for t in tickers]
    ax1.text(0.5, y_pos-0.1, f"{sector}:", fontsize=9, fontweight='bold',
             color='white', va='center')
    ax1.text(2.5, y_pos-0.1, '  |  '.join(names), fontsize=8.5,
             color='white', va='center')
    y_pos -= 1.1

ax1.text(5, 0.3, f"Total: {sum(len(v) for v in SECTOR_MAP.values())} stocks across {len(SECTOR_MAP)} sectors",
         ha='center', fontsize=10, fontweight='bold', color='#333333')

# Right: Backtesting universe with sector assignment
ax2 = axes[1]
ax2.set_xlim(0, 10); ax2.set_ylim(0, 13); ax2.axis('off')
ax2.set_title('Backtesting Universe (25 Stocks)\\nWith Sector Assignment', fontsize=11, fontweight='bold')

y_pos = 12.5
for sector in SECTOR_MAP.keys():
    stocks_in_sector = [name for sym, name in STOCKS.items()
                        if STOCK_SECTOR.get(name) == sector]
    if not stocks_in_sector:
        continue
    color = SECTOR_COLORS.get(sector, '#78909C')
    h = 0.45 * len(stocks_in_sector) + 0.2
    rect = plt.Rectangle((0.2, y_pos - h), 9.6, h, facecolor=color,
                          edgecolor='white', lw=1.5, alpha=0.85)
    ax2.add_patch(rect)
    ax2.text(0.5, y_pos - h/2, f"{sector} ({len(stocks_in_sector)})",
             fontsize=9, fontweight='bold', color='white', va='center')
    ax2.text(3.0, y_pos - h/2, '  |  '.join(stocks_in_sector),
             fontsize=8, color='white', va='center')
    y_pos -= h + 0.15

ax2.text(5, 0.3, f"Total: {len(STOCKS)} stocks | Period: 2023-2024 | 491 trading days",
         ha='center', fontsize=10, fontweight='bold', color='#333333')

plt.tight_layout()
plt.savefig('dataset_chart11_sector_map.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 11 saved: dataset_chart11_sector_map.png")
""", "c_chart11"))

cells.append(mc("""### Chart 11 Interpretation
- **Left:** The exact SECTOR_MAP used in the live platform (agentic.py). This is what Agent 2 (Sector Rotation) and Agent 6 (Volume Analytics) use for real-time analysis.
- **Right:** The backtesting universe with sector assignments. The backtesting uses the same sector structure but with 25 stocks (some sectors have additional stocks for broader coverage).
- The consistency between the live framework and backtesting universe ensures that backtesting results are directly applicable to the live system.
""", "m_c11e"))

# ── Chart 12: VADER Sentiment Illustration ───────────────────────────────────
cells.append(mc("""## Chart 12 — VADER Sentiment Scoring: How Agent 4 Works
**What this shows:** The VADER compound score distribution and the ±0.05 threshold used in Agent 4.
""", "m_c12"))

cells.append(cc("""
# CHART 12: VADER Sentiment Illustration
# =========================================
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
vader = SentimentIntensityAnalyzer()

# Fetch live headlines
print("Fetching live headlines for VADER illustration...")
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
        for entry in feed.entries[:10]:
            title = entry.get('title','')
            if title:
                score = vader.polarity_scores(title)['compound']
                articles.append({'title': title[:60]+'...', 'score': score, 'source': src,
                                 'sentiment': 'Positive' if score>0.05 else 'Negative' if score<-0.05 else 'Neutral'})
    except: pass

print(f"Fetched {len(articles)} headlines")

fig, axes = plt.subplots(1, 3, figsize=(22, 8))
fig.suptitle('Chart 12: VADER Sentiment Analysis — Agent 4 Data Source and Scoring Method',
             fontsize=13, fontweight='bold', y=1.01)

# Chart 12a: Headline scores bar chart
ax1 = axes[0]
if articles:
    scores = [a['score'] for a in articles]
    titles = [a['title'] for a in articles]
    colors_h = ['#2E7D32' if s>0.05 else '#C62828' if s<-0.05 else '#F57F17' for s in scores]
    ax1.barh(range(len(scores)), scores, color=colors_h, edgecolor='white', lw=0.8)
    ax1.set_yticks(range(len(titles)))
    ax1.set_yticklabels(titles, fontsize=7)
    ax1.axvline(0.05, color='green', lw=2, linestyle='--', label='Positive threshold (+0.05)')
    ax1.axvline(-0.05, color='red', lw=2, linestyle='--', label='Negative threshold (-0.05)')
    ax1.axvline(0, color='black', lw=1)
    ax1.set_xlabel('VADER Compound Score (-1 to +1)', fontsize=10)
    ax1.set_title(f'Live Headlines — VADER Scores\\n({len(articles)} headlines fetched today)', fontsize=11, fontweight='bold')
    ax1.legend(fontsize=8)

# Chart 12b: Sentiment distribution pie
ax2 = axes[1]
if articles:
    pos = sum(1 for a in articles if a['sentiment']=='Positive')
    neg = sum(1 for a in articles if a['sentiment']=='Negative')
    neu = len(articles) - pos - neg
    sizes = [pos, neg, neu]
    labels = [f'Positive\n(score > +0.05)\nn={pos}',
              f'Negative\n(score < -0.05)\nn={neg}',
              f'Neutral\n(-0.05 to +0.05)\nn={neu}']
    colors_pie = ['#2E7D32','#C62828','#F57F17']
    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors_pie,
                                        autopct='%1.1f%%', startangle=90,
                                        wedgeprops={'edgecolor':'white','linewidth':2})
    for at in autotexts: at.set_fontsize(10); at.set_fontweight('bold')
    avg = np.mean([a['score'] for a in articles])
    ax2.set_title(f'Sentiment Distribution\\nAvg VADER Score: {avg:.4f}', fontsize=11, fontweight='bold')

# Chart 12c: VADER score scale explanation
ax3 = axes[2]
ax3.set_xlim(-1.2, 1.2); ax3.set_ylim(0, 10); ax3.axis('off')
ax3.set_title('VADER Compound Score Scale\\n(Agent 4 Classification Logic)', fontsize=11, fontweight='bold')

# Color gradient bar
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list('sentiment', ['#C62828','#FFEB3B','#2E7D32'])
gradient = np.linspace(0, 1, 300).reshape(1, -1)
ax3.imshow(gradient, extent=[-1, 1, 4, 5], aspect='auto', cmap=cmap, zorder=3)
ax3.axvline(-0.05, color='black', lw=2, ymin=0.35, ymax=0.55)
ax3.axvline(0.05, color='black', lw=2, ymin=0.35, ymax=0.55)
ax3.text(-0.55, 5.3, 'NEGATIVE', ha='center', fontsize=12, fontweight='bold', color='#C62828')
ax3.text(0, 5.3, 'NEUTRAL', ha='center', fontsize=11, fontweight='bold', color='#F57F17')
ax3.text(0.55, 5.3, 'POSITIVE', ha='center', fontsize=12, fontweight='bold', color='#2E7D32')
ax3.text(-1.0, 4.5, '-1.0', ha='center', fontsize=10, color='#C62828', fontweight='bold')
ax3.text(-0.05, 4.5, '-0.05', ha='center', fontsize=9, color='black')
ax3.text(0.05, 4.5, '+0.05', ha='center', fontsize=9, color='black')
ax3.text(1.0, 4.5, '+1.0', ha='center', fontsize=10, color='#2E7D32', fontweight='bold')

examples = [
    (-0.8, 7.5, '"Market crashes amid panic selling"', '#C62828'),
    (-0.4, 6.8, '"Stocks decline on weak earnings"', '#E57373'),
    (0.0, 6.1, '"Markets open flat amid uncertainty"', '#F57F17'),
    (0.4, 5.4, '"Nifty rises on strong FII inflows"', '#66BB6A'),
    (0.8, 4.7, '"Record high! Markets surge on GDP beat"', '#2E7D32'),
]
for x, y, text, color in examples:
    ax3.scatter(x, y, color=color, s=80, zorder=5)
    ax3.text(x + 0.05, y, text, fontsize=7.5, va='center', color=color)

ax3.text(0, 3.5, 'Data Sources:', ha='center', fontsize=10, fontweight='bold')
ax3.text(0, 3.0, 'Google Finance RSS + Economic Times RSS', ha='center', fontsize=9, color='#1565C0')
ax3.text(0, 2.5, 'Up to 16 headlines per query (8 per source)', ha='center', fontsize=9)
ax3.text(0, 2.0, 'Threshold: compound > +0.05 = Positive', ha='center', fontsize=9, color='#2E7D32')
ax3.text(0, 1.5, 'Threshold: compound < -0.05 = Negative', ha='center', fontsize=9, color='#C62828')

plt.tight_layout()
plt.savefig('dataset_chart12_vader.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 12 saved: dataset_chart12_vader.png")
""", "c_chart12"))

cells.append(mc("""### Chart 12 Interpretation
- **Left:** Live headlines scored by VADER. Green bars = positive (score > +0.05), red = negative (< -0.05), orange = neutral.
- **Middle:** Pie chart showing today's sentiment distribution — the same output that Agent 4 produces in the live platform.
- **Right:** The VADER compound score scale from -1 (most negative) to +1 (most positive), with the ±0.05 classification thresholds and example headlines at different score levels.
- This directly illustrates the data and methodology described in Section 2.2.3 of the research paper.
""", "m_c12e"))

with open('nb_dataset_part5.json','w',encoding='utf-8') as f:
    json.dump(cells, f)
print(f"Part 5: {len(cells)} cells")
