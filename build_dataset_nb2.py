# coding: utf-8
import json
cells=[]


def cc(src, cid):
    return {"cell_type":"code","execution_count":None,"id":cid,"metadata":{},"outputs":[],"source":[src]}
def mc(src, cid):
    return {"cell_type":"markdown","id":cid,"metadata":{},"source":[src]}

# ── PART A: BACKTESTING DATASET ───────────────────────────────────────────────
cells.append(mc("""---
# PART A: Backtesting Dataset Visualizations
## Yahoo Finance Historical Data — 25 Nifty 50 Stocks (2023-2024)
""", "mA"))

# ── Chart 1: Stock Universe Overview ─────────────────────────────────────────
cells.append(mc("""## Chart 1 — Stock Universe Overview
**What this shows:** The composition of the 25-stock backtesting universe across 8 sectors.
This directly supports Table 1 in the Dataset section of the research paper.
""", "m_c1"))

cells.append(cc("""
# CHART 1: Stock Universe — Sector Distribution
# ================================================
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle('Chart 1: Backtesting Universe — 25 Nifty 50 Stocks Across 8 Sectors',
             fontsize=14, fontweight='bold', y=1.01)

sector_counts = {}
for sector, tickers in SECTOR_MAP.items():
    sector_counts[sector] = len(tickers)

colors = [SECTOR_COLORS[s] for s in sector_counts.keys()]

# Pie chart
ax1 = axes[0]
wedges, texts, autotexts = ax1.pie(
    sector_counts.values(), labels=sector_counts.keys(),
    colors=colors, autopct='%1.0f%%', startangle=90,
    wedgeprops={'edgecolor':'white','linewidth':2},
    textprops={'fontsize':10}
)
for at in autotexts:
    at.set_fontsize(9); at.set_fontweight('bold')
ax1.set_title('Sector Distribution\\n(% of total stocks)', fontsize=12, fontweight='bold')

# Bar chart with stock names
ax2 = axes[1]
sectors = list(sector_counts.keys())
counts  = list(sector_counts.values())
bars = ax2.barh(sectors, counts, color=colors, edgecolor='white', lw=1.5, height=0.6)
ax2.set_xlabel('Number of Stocks', fontsize=11)
ax2.set_title('Stocks per Sector\\n(Exact SECTOR_MAP from agentic.py)', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 7)
for bar, val, sector in zip(bars, counts, sectors):
    tickers = SECTOR_MAP[sector]
    names   = [STOCKS.get(t, t.replace('.NS','')) for t in tickers]
    label   = ', '.join(names)
    ax2.text(val + 0.05, bar.get_y() + bar.get_height()/2,
             f' {val}  [{label}]', va='center', fontsize=8.5, color='#333333')
ax2.set_yticks(range(len(sectors)))
ax2.set_yticklabels(sectors, fontsize=10, fontweight='bold')
ax2.grid(axis='x', alpha=0.4)
ax2.set_axisbelow(True)

plt.tight_layout()
plt.savefig('dataset_chart1_universe.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 1 saved: dataset_chart1_universe.png")
print(f"Total stocks: {sum(sector_counts.values())} | Sectors: {len(sector_counts)}")
""", "c_chart1"))

cells.append(mc("""### Chart 1 Interpretation
- **Banking** has the most stocks (5) — reflects the dominance of financial sector in Nifty 50
- **Telecom** has only 1 stock (Bharti Airtel) — but it was the top performer in 2023-2024
- The 8-sector distribution ensures broad market coverage for backtesting
- This exact sector map is used in Agent 2 (Sector Rotation) and Agent 6 (Volume Analytics)
""", "m_c1e"))

# ── Chart 2: Normalized Price History ────────────────────────────────────────
cells.append(mc("""## Chart 2 — Normalized Price History (All 25 Stocks + NIFTY 50)
**What this shows:** How each stock performed relative to its starting price (normalized to 100).
This reveals the wide dispersion of returns across the universe — a key dataset characteristic.
""", "m_c2"))

cells.append(cc("""
# CHART 2: Normalized Price History
# ====================================
fig, axes = plt.subplots(2, 1, figsize=(18, 14))
fig.suptitle('Chart 2: Normalized Price History — All 25 Stocks + NIFTY 50 (2023-2024)\\n'
             '(Base = 100 on January 2, 2023)',
             fontsize=14, fontweight='bold', y=1.01)

# Top: All stocks colored by sector
ax1 = axes[0]
norm_px = close_px / close_px.iloc[0] * 100
norm_nifty = nifty_close / nifty_close.iloc[0] * 100

for col in norm_px.columns:
    sector = STOCK_SECTOR.get(col, 'Other')
    color  = SECTOR_COLORS.get(sector, '#78909C')
    ax1.plot(norm_px.index, norm_px[col], color=color, lw=1.2, alpha=0.65)

# NIFTY 50 benchmark
ax1.plot(norm_nifty.index, norm_nifty.values, color='black', lw=3,
         linestyle='--', label='NIFTY 50 Benchmark', zorder=10)
ax1.axhline(100, color='gray', linestyle=':', lw=1, alpha=0.7)

# Legend for sectors
legend_patches = [mpatches.Patch(color=SECTOR_COLORS[s], label=s) for s in SECTOR_MAP.keys()]
legend_patches.append(mpatches.Patch(color='black', label='NIFTY 50'))
ax1.legend(handles=legend_patches, loc='upper left', fontsize=9, ncol=3,
           framealpha=0.9, title='Sector / Benchmark')
ax1.set_title('All 25 Stocks — Colored by Sector', fontsize=12, fontweight='bold')
ax1.set_ylabel('Normalized Price (Base = 100)', fontsize=11)
ax1.set_xlabel('Date', fontsize=11)
ax1.set_ylim(50, 350)

# Bottom: Top 5 and Bottom 5 performers highlighted
ax2 = axes[1]
final_returns = (norm_px.iloc[-1] - 100).sort_values(ascending=False)
top5    = final_returns.head(5).index.tolist()
bottom5 = final_returns.tail(5).index.tolist()

# Gray background for all others
for col in norm_px.columns:
    if col not in top5 and col not in bottom5:
        ax2.plot(norm_px.index, norm_px[col], color='#CCCCCC', lw=0.8, alpha=0.5)

# Top 5 in green shades
greens = ['#1B5E20','#2E7D32','#388E3C','#43A047','#66BB6A']
for i, col in enumerate(top5):
    ret = final_returns[col]
    ax2.plot(norm_px.index, norm_px[col], color=greens[i], lw=2.5,
             label=f'{col} (+{ret:.1f}%)')

# Bottom 5 in red shades
reds = ['#B71C1C','#C62828','#D32F2F','#E53935','#EF5350']
for i, col in enumerate(bottom5):
    ret = final_returns[col]
    ax2.plot(norm_px.index, norm_px[col], color=reds[i], lw=2.5,
             label=f'{col} ({ret:+.1f}%)')

ax2.plot(norm_nifty.index, norm_nifty.values, color='black', lw=2.5,
         linestyle='--', label=f'NIFTY 50 (+{(norm_nifty.iloc[-1]-100):.1f}%)')
ax2.axhline(100, color='gray', linestyle=':', lw=1, alpha=0.7)
ax2.legend(loc='upper left', fontsize=9, ncol=2, framealpha=0.9,
           title='Top 5 (green) | Bottom 5 (red)')
ax2.set_title('Top 5 and Bottom 5 Performers vs NIFTY 50 Benchmark', fontsize=12, fontweight='bold')
ax2.set_ylabel('Normalized Price (Base = 100)', fontsize=11)
ax2.set_xlabel('Date', fontsize=11)

plt.tight_layout()
plt.savefig('dataset_chart2_prices.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart 2 saved: dataset_chart2_prices.png")
print("Top 5 performers:", top5)
print("Bottom 5 performers:", bottom5)
print(f"NIFTY 50 return: {norm_nifty.iloc[-1]-100:.2f}%")
""", "c_chart2"))

cells.append(mc("""### Chart 2 Interpretation
- **Top chart:** All 25 stocks colored by sector. The wide spread (50 to 350) shows the high return dispersion in the dataset.
- **Bottom chart:** Top 5 performers (green) vs Bottom 5 (red) vs NIFTY 50 (black dashed).
- Telecom (Airtel) is typically the top performer — validating Agent 2's sector rotation results.
- The dataset captures both strong outperformers and underperformers, making it a rigorous test environment.
""", "m_c2e"))

# ── Chart 3: NIFTY 50 Return Distribution ────────────────────────────────────
cells.append(mc("""## Chart 3 — NIFTY 50 Daily Return Distribution
**What this shows:** The statistical properties of NIFTY 50 daily returns — fat tails, negative skewness,
and non-normality. This directly supports Tables 2 and the JB/ADF test results in the paper.
""", "m_c3"))

cells.append(cc("""
# CHART 3: NIFTY 50 Return Distribution
# ========================================
nifty_ret_pct = nifty_ret * 100

fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.suptitle('Chart 3: NIFTY 50 Daily Return Distribution — Statistical Properties (2023-2024)',
             fontsize=13, fontweight='bold', y=1.01)

# Chart 3a: Histogram with normal overlay
ax1 = axes[0]
n, bins, patches = ax1.hist(nifty_ret_pct, bins=50, density=True,
                             color='#1565C0', alpha=0.75, edgecolor='white', lw=0.5,
                             label='Actual Returns')
mu, sigma = nifty_ret_pct.mean(), nifty_ret_pct.std()
x = np.linspace(nifty_ret_pct.min(), nifty_ret_pct.max(), 300)
ax1.plot(x, norm.pdf(x, mu, sigma), color='#E65100', lw=2.5, linestyle='--',
         label=f'Normal Dist (mu={mu:.3f}%, sigma={sigma:.3f}%)')
ax1.axvline(mu, color='green', lw=2, linestyle='-', label=f'Mean: {mu:.4f}%')
ax1.axvline(nifty_ret_pct.median(), color='purple', lw=2, linestyle='-.',
            label=f'Median: {nifty_ret_pct.median():.4f}%')
ax1.set_title('Return Distribution vs Normal\\n(Fat tails visible)', fontsize=11, fontweight='bold')
ax1.set_xlabel('Daily Return (%)', fontsize=10)
ax1.set_ylabel('Probability Density', fontsize=10)
ax1.legend(fontsize=8.5)

# Annotate key stats
stats_text = (f"N = {len(nifty_ret_pct)}\n"
              f"Mean = {mu:.4f}%\n"
              f"Std = {sigma:.4f}%\n"
              f"Min = {nifty_ret_pct.min():.3f}%\n"
              f"Max = {nifty_ret_pct.max():.3f}%\n"
              f"Skew = {skew(nifty_ret_pct):.4f}\n"
              f"Kurt = {kurtosis(nifty_ret_pct):.4f}")
ax1.text(0.97, 0.97, stats_text, transform=ax1.transAxes,
         fontsize=8, va='top', ha='right',
         bbox=dict(boxstyle='round', facecolor='#E3F2FD', alpha=0.8))

# Chart 3b: QQ Plot
ax2 = axes[1]
from scipy.stats import probplot
(osm, osr), (slope, intercept, r) = probplot(nifty_ret_pct, dist='norm')
ax2.scatter(osm, osr, color='#1565C0', s=8, alpha=0.6, label='Actual quantiles')
ax2.plot(osm, slope*np.array(osm)+intercept, color='#E65100', lw=2,
         linestyle='--', label='Normal reference line')
ax2.set_title('Q-Q Plot vs Normal Distribution\\n(Deviation = fat tails)', fontsize=11, fontweight='bold')
ax2.set_xlabel('Theoretical Quantiles (Normal)', fontsize=10)
ax2.set_ylabel('Sample Quantiles (NIFTY 50 Returns)', fontsize=10)
ax2.legend(fontsize=9)
ax2.text(0.05, 0.95, f'R² = {r**2:.4f}', transform=ax2.transAxes,
         fontsize=10, va='top', color='#E65100', fontweight='bold')

# Chart 3c: Rolling statistics
ax3 = axes[2]
roll30_mean = nifty_ret_pct.rolling(30).mean()
roll30_std  = nifty_ret_pct.rolling(30).std()
ax3.plot(nifty_ret_pct.index, roll30_mean, color='#2E7D32', lw=2,
         label='30-day Rolling Mean')
ax3.fill_between(nifty_ret_pct.index,
                 roll30_mean - roll30_std,
                 roll30_mean + roll30_std,
                 alpha=0.25, color='#1565C0', label='±1 Std Dev Band')
ax3.axhline(0, color='gray', linestyle=':', lw=1)
ax3.set_title('30-Day Rolling Mean & Volatility Band\\n(Market regime changes visible)', fontsize=11, fontweight='bold')
ax3.set_xlabel('Date', fontsize=10)
ax3.set_ylabel('Daily Return (%)', fontsize=10)
ax3.legend(fontsize=9)

plt.tight_layout()
plt.savefig('dataset_chart3_distribution.png', dpi=150, bbox_inches='tight')
plt.show()

jb_stat, jb_p = jarque_bera(nifty_ret_pct)
adf_result = adfuller(nifty_ret_pct, autolag='AIC')
print("=== NIFTY 50 Statistical Tests ===")
print(f"Jarque-Bera Statistic: {jb_stat:.4f}  |  p-value: {jb_p:.2e}  |  Normal? {'NO' if jb_p < 0.05 else 'YES'}")
print(f"ADF Statistic:         {adf_result[0]:.4f}  |  p-value: {adf_result[1]:.2e}  |  Stationary? {'YES' if adf_result[1] < 0.05 else 'NO'}")
print(f"Skewness: {skew(nifty_ret_pct):.4f}  |  Excess Kurtosis: {kurtosis(nifty_ret_pct):.4f}")
""", "c_chart3"))

cells.append(mc("""### Chart 3 Interpretation
- **Left (Histogram):** The actual return distribution (blue) has much taller peaks and fatter tails than the normal distribution (orange dashed). This confirms the JB test result (JB = 1553, p < 0.0001).
- **Middle (Q-Q Plot):** Points deviate from the normal reference line at both extremes — confirming fat tails. The S-shaped deviation is the signature of leptokurtosis (excess kurtosis = 8.57).
- **Right (Rolling Stats):** The 30-day rolling mean fluctuates around zero, confirming stationarity. The volatility band widens during market stress periods (October 2024 correction).
""", "m_c3e"))

with open('nb_dataset_part2.json','w',encoding='utf-8') as f:
    json.dump(cells, f)
print(f"Part 2: {len(cells)} cells")
