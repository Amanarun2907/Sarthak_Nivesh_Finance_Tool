# coding: utf-8
import json, ast

nb = json.load(open('research/Dataset.ipynb', encoding='utf-8'))

# Build cell 37 source using list concatenation to avoid newline issues
lines = [
    "",
    "# CHART 10: Data Source Architecture Diagram",
    "# =============================================",
    "import matplotlib.patches as mpatches",
    "",
    "fig, ax = plt.subplots(figsize=(20, 11))",
    "ax.set_xlim(0, 20); ax.set_ylim(0, 12)",
    "ax.axis('off')",
    "fig.patch.set_facecolor('white')",
    "fig.suptitle('Chart 10: Data Source Architecture - Sarthak Nivesh Multi-Agent AI Framework',",
    "             fontsize=14, fontweight='bold', y=0.98)",
    "",
    "def box(ax, x, y, w, h, txt, fc, tc='white', fs=9):",
    "    r = plt.Rectangle((x,y), w, h, facecolor=fc, edgecolor='white', lw=2, zorder=3, alpha=0.92)",
    "    ax.add_patch(r)",
    "    ax.text(x+w/2, y+h/2, txt, ha='center', va='center', fontsize=fs,",
    "            fontweight='bold', color=tc, zorder=4)",
    "",
    "def arr(ax, x1, y1, x2, y2):",
    "    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),",
    "                arrowprops=dict(arrowstyle='->', color='#888888', lw=1.5))",
    "",
    "# Data Sources",
    "box(ax, 0.3, 9.5, 3.5, 1.0, 'Yahoo Finance fast_info API (Live Prices)', '#1565C0', fs=8)",
    "box(ax, 0.3, 8.0, 3.5, 1.0, 'Yahoo Finance Historical OHLCV (3mo/1y/2y)', '#1976D2', fs=8)",
    "box(ax, 0.3, 6.5, 3.5, 1.0, 'NSE India API - FII/DII Net Flow (Daily)', '#0D47A1', fs=8)",
    "box(ax, 0.3, 5.0, 3.5, 1.0, 'Google Finance RSS - Market Headlines', '#2E7D32', fs=8)",
    "box(ax, 0.3, 3.5, 3.5, 1.0, 'Economic Times RSS - Market News', '#388E3C', fs=8)",
    "box(ax, 0.3, 2.0, 3.5, 1.0, 'Groq Cloud API - LLaMA 3.3 70B (LLM)', '#6A1B9A', fs=8)",
    "",
    "# Agents",
    "box(ax, 7.5, 9.5, 3.5, 1.0, 'Agent 1: Stock Intelligence (RSI+MACD+MA50)', '#1565C0', fs=8)",
    "box(ax, 7.5, 8.0, 3.5, 1.0, 'Agent 2: Market Analysis (Sector Rotation)', '#2E7D32', fs=8)",
    "box(ax, 7.5, 6.5, 3.5, 1.0, 'Agent 3: Smart Money (FII/DII Tracker)', '#0D47A1', fs=8)",
    "box(ax, 7.5, 5.0, 3.5, 1.0, 'Agent 4: News Sentiment (VADER NLP)', '#AD1457', fs=8)",
    "box(ax, 7.5, 3.5, 3.5, 1.0, 'Agent 5: Risk Management (VaR 95%)', '#E65100', fs=8)",
    "box(ax, 7.5, 2.0, 3.5, 1.0, 'Agent 6: Advanced Analytics (Volume)', '#00695C', fs=8)",
    "",
    "# Master + Output",
    "box(ax, 14.5, 5.0, 4.5, 2.5, 'Master Report Agent\\nLLaMA 3.3 70B (Groq)\\nSynthesizes all 6 agents', '#37474F', fs=9)",
    "box(ax, 14.5, 2.0, 4.5, 2.5, 'Structured Investment Report\\n1. Executive Summary\\n2. Opportunities\\n3. Risks + Action Plan', '#4A148C', fs=8)",
    "",
    "# Arrows sources -> agents",
    "arrow_pairs = [",
    "    (3.8,10.0,7.5,10.0),(3.8,10.0,7.5,8.5),(3.8,8.5,7.5,10.0),",
    "    (3.8,8.5,7.5,8.5),(3.8,8.5,7.5,4.0),(3.8,8.5,7.5,2.5),",
    "    (3.8,7.0,7.5,7.0),(3.8,5.5,7.5,5.5),(3.8,4.0,7.5,5.5),",
    "    (3.8,2.5,7.5,10.0),(3.8,2.5,7.5,8.5),(3.8,2.5,7.5,7.0),",
    "    (3.8,2.5,7.5,5.5),(3.8,2.5,7.5,4.0),(3.8,2.5,7.5,2.5),",
    "]",
    "for x1,y1,x2,y2 in arrow_pairs:",
    "    arr(ax, x1, y1, x2, y2)",
    "",
    "for y in [10.0, 8.5, 7.0, 5.5, 4.0, 2.5]:",
    "    arr(ax, 11.0, y, 14.5, 6.25)",
    "arr(ax, 16.75, 5.0, 16.75, 4.5)",
    "",
    "ax.text(2.0, 11.2, 'DATA SOURCES', ha='center', fontsize=11, fontweight='bold', color='#333333')",
    "ax.text(9.25, 11.2, 'SPECIALIST AGENTS', ha='center', fontsize=11, fontweight='bold', color='#333333')",
    "ax.text(16.75, 11.2, 'LLM SYNTHESIS', ha='center', fontsize=11, fontweight='bold', color='#333333')",
    "ax.axvline(6.8, color='#CCCCCC', lw=1.5, linestyle='--', alpha=0.7)",
    "ax.axvline(13.8, color='#CCCCCC', lw=1.5, linestyle='--', alpha=0.7)",
    "",
    "plt.tight_layout()",
    "plt.savefig('dataset_chart10_architecture.png', dpi=150, bbox_inches='tight')",
    "plt.show()",
    "print('Chart 10 saved: dataset_chart10_architecture.png')",
]

src37 = '\n'.join(lines)
ast.parse(src37)
print('Cell 37 syntax OK')
nb['cells'][37]['source'] = [src37]
nb['cells'][37]['outputs'] = []
nb['cells'][37]['execution_count'] = None
with open('research/Dataset.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print('Saved')
