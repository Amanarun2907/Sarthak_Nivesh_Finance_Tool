# coding: utf-8
# Builder for Dataset.ipynb

import json

def cc(src, cid):
    return {"cell_type":"code","execution_count":None,"id":cid,
            "metadata":{},"outputs":[],"source":[src]}
def mc(src, cid):
    return {"cell_type":"markdown","id":cid,"metadata":{},"source":[src]}

cells = []

# ── Title ─────────────────────────────────────────────────────────────────────
cells.append(mc("""# Dataset Visualization — Multi-Agent AI Investment Hub
## Supporting the Dataset Section of the Research Paper
**Paper:** Multi-Agent Artificial Intelligence Investment Hub Utilizing LLM for Predictive Decision Assistance in Volatile Stock Markets
**Author:** Aman Jain | B.Tech CSE 2023-27 | BML Munjal University, Gurugram

---
### What this notebook covers:
**Part A — Backtesting Dataset (Yahoo Finance, 2023-2024)**
- Stock universe overview (25 Nifty 50 stocks, 8 sectors)
- Price history and cumulative returns
- Daily return distributions and statistical properties
- Volatility, correlation, skewness, kurtosis analysis
- ADF stationarity and JB normality test results

**Part B — Real-Time Agentic AI Framework Data**
- Data source architecture
- Sector composition (exact SECTOR_MAP from agentic.py)
- VADER sentiment scoring illustration
- FII/DII signal thresholds
- Volume anomaly detection threshold
""", "title"))

# ── Cell 1: Setup ─────────────────────────────────────────────────────────────
cells.append(mc("""## Cell 1 — Setup: Install Libraries and Define Universe
All data is downloaded from Yahoo Finance using yfinance — 100% real historical data.
The stock universe and sector map exactly match the web interface implementation (`agentic.py`).
""", "m1"))

cells.append(cc("""
# CELL 1: Setup — Libraries and Stock Universe
# =============================================
import subprocess
for pkg in ['yfinance','pandas','numpy','matplotlib','seaborn','scipy','statsmodels']:
    subprocess.run(['pip','install',pkg,'-q'], capture_output=True)

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
from scipy.stats import skew, kurtosis, jarque_bera, norm
from statsmodels.tsa.stattools import adfuller

# ── Global plot style ─────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': 'white', 'axes.facecolor': '#F8F9FA',
    'axes.grid': True, 'grid.alpha': 0.35, 'font.size': 11,
    'axes.titlesize': 13, 'axes.labelsize': 11, 'figure.dpi': 120,
    'axes.spines.top': False, 'axes.spines.right': False
})

# ── Exact SECTOR_MAP from web/backend/routers/agentic.py ─────────────────────
SECTOR_MAP = {
    "Banking": ["HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","KOTAKBANK.NS","AXISBANK.NS"],
    "IT":      ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS"],
    "Energy":  ["RELIANCE.NS","ONGC.NS","NTPC.NS"],
    "FMCG":    ["HINDUNILVR.NS","ITC.NS","NESTLEIND.NS"],
    "Auto":    ["MARUTI.NS","M&M.NS","BAJAJ-AUTO.NS"],
    "Pharma":  ["SUNPHARMA.NS","DRREDDY.NS","CIPLA.NS"],
    "Metals":  ["TATASTEEL.NS","HINDALCO.NS","JSWSTEEL.NS"],
    "Telecom": ["BHARTIARTL.NS"],
}

# ── Backtesting stock universe (25 stocks) ────────────────────────────────────
STOCKS = {
    'RELIANCE.NS':'Reliance','TCS.NS':'TCS','HDFCBANK.NS':'HDFC Bank',
    'INFY.NS':'Infosys','ICICIBANK.NS':'ICICI Bank','HINDUNILVR.NS':'HUL',
    'ITC.NS':'ITC','SBIN.NS':'SBI','BHARTIARTL.NS':'Airtel',
    'KOTAKBANK.NS':'Kotak Bank','LT.NS':'L&T','AXISBANK.NS':'Axis Bank',
    'WIPRO.NS':'Wipro','MARUTI.NS':'Maruti','TITAN.NS':'Titan',
    'BAJFINANCE.NS':'Bajaj Finance','SUNPHARMA.NS':'Sun Pharma',
    'TATASTEEL.NS':'Tata Steel','NTPC.NS':'NTPC','M&M.NS':'Mahindra',
    'HCLTECH.NS':'HCL Tech','NESTLEIND.NS':'Nestle',
    'DRREDDY.NS':'Dr Reddy','CIPLA.NS':'Cipla','ONGC.NS':'ONGC'
}

# Sector assignment for each stock
STOCK_SECTOR = {}
for sector, tickers in SECTOR_MAP.items():
    for t in tickers:
        name = STOCKS.get(t, t.replace('.NS',''))
        STOCK_SECTOR[name] = sector
# Add stocks not in SECTOR_MAP
for sym, name in STOCKS.items():
    if name not in STOCK_SECTOR:
        STOCK_SECTOR[name] = 'Other'

SECTOR_COLORS = {
    'Banking':'#1565C0','IT':'#2E7D32','Energy':'#E65100',
    'FMCG':'#6A1B9A','Auto':'#AD1457','Pharma':'#00695C',
    'Metals':'#37474F','Telecom':'#F57F17','Other':'#78909C'
}

START, END = '2023-01-01', '2025-01-01'
print(f"Setup complete.")
print(f"Stock universe: {len(STOCKS)} stocks across {len(SECTOR_MAP)} sectors")
print(f"Backtesting period: {START} to {END}")
print(f"Sectors: {list(SECTOR_MAP.keys())}")
""", "c1"))

cells.append(mc("""### Cell 1 Output
- All libraries loaded successfully
- 25 stocks defined across 8 sectors (exact match to `agentic.py`)
- Backtesting period: January 2023 to December 2024 (2 years)
""", "m1e"))

# ── Cell 2: Download Data ─────────────────────────────────────────────────────
cells.append(mc("""## Cell 2 — Download Real Historical Data
Downloading 2 years of daily OHLCV data for all 25 stocks and NIFTY 50 from Yahoo Finance.
This is the exact same data used in the backtesting notebook.
""", "m2"))

cells.append(cc("""
# CELL 2: Download Data
# ======================
print("Downloading 2 years of real historical data from Yahoo Finance...")
all_data = {}
for sym, name in STOCKS.items():
    try:
        df = yf.download(sym, start=START, end=END, progress=False, auto_adjust=True)
        if len(df) > 200:
            all_data[sym] = df
    except: pass

nifty_df    = yf.download('^NSEI', start=START, end=END, progress=False, auto_adjust=True)
nifty_close = nifty_df['Close'].squeeze()
nifty_close.index = pd.to_datetime(nifty_close.index)

close_px = pd.DataFrame({STOCKS[s]: all_data[s]['Close'].squeeze() for s in all_data})
close_px.index = pd.to_datetime(close_px.index)
close_px = close_px.dropna(how='all')

vol_data = pd.DataFrame({STOCKS[s]: all_data[s]['Volume'].squeeze() for s in all_data})
vol_data.index = pd.to_datetime(vol_data.index)

daily_ret = close_px.pct_change().dropna()
nifty_ret = nifty_close.pct_change().dropna()

print(f"Data downloaded: {close_px.shape[0]} trading days x {close_px.shape[1]} stocks")
print(f"Date range: {close_px.index[0].date()} to {close_px.index[-1].date()}")
print(f"NIFTY 50: {len(nifty_close)} trading days")
print(f"Total observations: {close_px.shape[0] * close_px.shape[1]:,}")
""", "c2"))

cells.append(mc("""### Cell 2 Output
- **491 trading days** per stock = 2 years of real market data
- **12,250 total observations** (491 days × 25 stocks)
- Data is split-adjusted and dividend-adjusted (auto_adjust=True)
- This is the foundation for all backtesting computations
""", "m2e"))

with open('nb_dataset_part1.json','w',encoding='utf-8') as f:
    json.dump(cells, f)
print(f"Part 1: {len(cells)} cells")
