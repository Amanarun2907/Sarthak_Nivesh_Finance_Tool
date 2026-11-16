"""
Fix agent2_backtest.png:
- X-axis: clean 'Mon-YY' labels instead of full ISO timestamps
- Y-axis: proper sector labels, no overlap
- Heatmap: larger figure, better font sizes, rotated x labels
- Cell annotations: readable size
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.rcParams.update({
    'figure.facecolor': 'white',
    'axes.facecolor': '#F8F9FA',
    'axes.grid': True,
    'grid.alpha': 0.4,
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.dpi': 120
})

STOCKS = {
    'RELIANCE.NS':'Reliance','TCS.NS':'TCS','HDFCBANK.NS':'HDFC Bank',
    'INFY.NS':'Infosys','ICICIBANK.NS':'ICICI Bank','HINDUNILVR.NS':'HUL',
    'ITC.NS':'ITC','SBIN.NS':'SBI','BHARTIARTL.NS':'Airtel',
    'KOTAKBANK.NS':'Kotak Bank','LT.NS':'L&T','AXISBANK.NS':'Axis Bank',
    'WIPRO.NS':'Wipro','MARUTI.NS':'Maruti','TITAN.NS':'Titan',
    'BAJFINANCE.NS':'Bajaj Finance','SUNPHARMA.NS':'Sun Pharma',
    'TATASTEEL.NS':'Tata Steel','NTPC.NS':'NTPC','M&M.NS':'Mahindra',
    'HCLTECH.NS':'HCL Tech','ULTRACEMCO.NS':'UltraTech',
    'NESTLEIND.NS':'Nestle','DRREDDY.NS':'Dr Reddy','CIPLA.NS':'Cipla'
}
START, END, NIFTY_SYM = '2023-01-01', '2025-01-01', '^NSEI'

print("Downloading data...")
all_data = {}
for sym, name in STOCKS.items():
    try:
        df = yf.download(sym, start=START, end=END, progress=False, auto_adjust=True)
        if len(df) > 200:
            all_data[sym] = df
    except:
        pass

nifty_df = yf.download(NIFTY_SYM, start=START, end=END, progress=False, auto_adjust=True)
nifty_close = nifty_df['Close'].squeeze()
nifty_close.index = pd.to_datetime(nifty_close.index)

close_prices = pd.DataFrame({STOCKS[s]: all_data[s]['Close'].squeeze() for s in all_data})
close_prices.index = pd.to_datetime(close_prices.index)
close_prices = close_prices.dropna(how='all')

# ── Sector Rotation logic ──────────────────────────────────────────────────────
SECTOR_MAP = {
    'Banking':  ['HDFC Bank','ICICI Bank','SBI','Kotak Bank','Axis Bank'],
    'IT':       ['TCS','Infosys','Wipro','HCL Tech'],
    'Energy':   ['Reliance','NTPC'],
    'FMCG':     ['HUL','ITC','Nestle'],
    'Auto':     ['Maruti','Mahindra'],
    'Pharma':   ['Sun Pharma','Dr Reddy','Cipla'],
    'Metals':   ['Tata Steel'],
    'Telecom':  ['Airtel'],
}

sector_monthly = {}
for sector, stocks_list in SECTOR_MAP.items():
    valid = [s for s in stocks_list if s in close_prices.columns]
    if not valid:
        continue
    sector_prices = close_prices[valid].mean(axis=1)
    sector_monthly[sector] = sector_prices.resample('ME').last().pct_change()

sector_df = pd.DataFrame(sector_monthly).dropna()

rotation_returns = []
for i in range(1, len(sector_df)):
    best_sector = sector_df.iloc[i-1].idxmax()
    this_ret = sector_df.iloc[i][best_sector]
    rotation_returns.append({'date': sector_df.index[i], 'return': this_ret, 'sector': best_sector})

rot_df = pd.DataFrame(rotation_returns).set_index('date')
rot_df['cumulative'] = (1 + rot_df['return']).cumprod()

nifty_monthly = nifty_close.resample('ME').last().pct_change().dropna()
nifty_monthly_cum = (1 + nifty_monthly).cumprod()

agent2_return = (rot_df['cumulative'].iloc[-1] - 1) * 100
nifty_m_return = (nifty_monthly_cum.iloc[-1] - 1) * 100

print(f'Agent 2 Return: {agent2_return:.2f}%')
print(f'NIFTY Return:   {nifty_m_return:.2f}%')

# ── Build clean month labels for heatmap ──────────────────────────────────────
# Format: Jan-23, Feb-23, ...
month_labels = [d.strftime('%b-%y') for d in sector_df.index]

# ── Figure: wider layout, heatmap gets more space ─────────────────────────────
fig = plt.figure(figsize=(24, 7))
fig.suptitle(
    'Agent 2: Market Analysis — Sector Rotation Strategy vs NIFTY 50 (2023–2025)',
    fontsize=14, fontweight='bold', y=1.01
)

# Use GridSpec so heatmap gets ~50% width
from matplotlib.gridspec import GridSpec
gs = GridSpec(1, 3, figure=fig, width_ratios=[1, 0.7, 1.5], wspace=0.35)

# ── Chart 1: Cumulative returns ────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0])
ax1.plot(rot_df.index, rot_df['cumulative'], color='#1565C0', lw=2.5, label='Sector Rotation')
ax1.plot(nifty_monthly_cum.index, nifty_monthly_cum.values, color='#E65100', lw=2,
         linestyle='--', label='NIFTY 50')
ax1.axhline(1.0, color='gray', linestyle=':', lw=1)
ax1.fill_between(rot_df.index, rot_df['cumulative'], 1, alpha=0.12, color='#1565C0')
ax1.set_title('Cumulative Returns\nSector Rotation vs NIFTY')
ax1.set_xlabel('Date')
ax1.set_ylabel('Portfolio Value (x)')
ax1.legend(fontsize=10)
# Annotate final values
ax1.annotate(f'{agent2_return:.1f}%', xy=(rot_df.index[-1], rot_df["cumulative"].iloc[-1]),
             xytext=(-60, 8), textcoords='offset points', fontsize=10,
             color='#1565C0', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#1565C0'))
ax1.annotate(f'{nifty_m_return:.1f}%', xy=(nifty_monthly_cum.index[-1], nifty_monthly_cum.iloc[-1]),
             xytext=(-60, -18), textcoords='offset points', fontsize=10,
             color='#E65100', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='#E65100'))

# ── Chart 2: Sector selection frequency ───────────────────────────────────────
ax2 = fig.add_subplot(gs[1])
sc = rot_df['sector'].value_counts()
colors_bar = ['#1565C0','#2E7D32','#E65100','#6A1B9A','#00695C','#AD1457','#37474F','#F57F17']
bars = ax2.bar(sc.index, sc.values, color=colors_bar[:len(sc)], edgecolor='white', lw=1.5)
ax2.set_title('Sector Selection\nFrequency (months)')
ax2.set_xlabel('Sector')
ax2.set_ylabel('Times Selected')
ax2.tick_params(axis='x', rotation=45)
for bar, val in zip(bars, sc.values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(val),
             ha='center', fontsize=10, fontweight='bold')

# ── Chart 3: Heatmap — FIXED ──────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[2])

# Build heatmap data with clean string column labels
heatmap_data = (sector_df * 100).copy()
heatmap_data.index = month_labels          # clean 'Jan-23' labels on columns
heatmap_data = heatmap_data.T              # sectors on Y, months on X

sns.heatmap(
    heatmap_data,
    cmap='RdYlGn',
    center=0,
    ax=ax3,
    cbar_kws={'label': 'Monthly Return %', 'shrink': 0.85},
    linewidths=0.4,
    linecolor='white',
    annot=True,
    fmt='.1f',
    annot_kws={'size': 7.5, 'weight': 'bold'}
)

ax3.set_title('Sector Monthly Returns Heatmap (%)\nGreen = Up, Red = Down', fontsize=12)
ax3.set_xlabel('Month', fontsize=11)
ax3.set_ylabel('Sector', fontsize=11)

# X-axis: rotate labels so they don't overlap
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45, ha='right', fontsize=8.5)
# Y-axis: horizontal, readable
ax3.set_yticklabels(ax3.get_yticklabels(), rotation=0, fontsize=10)

plt.savefig('research/agent2_backtest.png', dpi=150, bbox_inches='tight')
plt.savefig('agent2_backtest.png', dpi=150, bbox_inches='tight')
print("Saved: research/agent2_backtest.png and agent2_backtest.png")
plt.show()
