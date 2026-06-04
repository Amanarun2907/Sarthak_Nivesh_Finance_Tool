# coding: utf-8

import yfinance as yf, pandas as pd, numpy as np, warnings
warnings.filterwarnings('ignore')
from scipy.stats import jarque_bera, kurtosis, skew
from statsmodels.tsa.stattools import adfuller

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

print("Downloading NIFTY 50...")
nifty = yf.download('^NSEI', start='2023-01-01', end='2025-01-01', progress=False, auto_adjust=True)
nifty_ret = nifty['Close'].squeeze().pct_change().dropna() * 100

print("=== NIFTY 50 DAILY RETURNS STATISTICS ===")
print(f"N observations:  {len(nifty_ret)}")
print(f"Mean:            {nifty_ret.mean():.6f}%")
print(f"Median:          {nifty_ret.median():.6f}%")
print(f"Std Dev:         {nifty_ret.std():.6f}%")
print(f"Min:             {nifty_ret.min():.6f}%")
print(f"Max:             {nifty_ret.max():.6f}%")
print(f"Skewness:        {skew(nifty_ret):.6f}")
print(f"Kurtosis:        {kurtosis(nifty_ret):.6f}")
jb_stat, jb_p = jarque_bera(nifty_ret)
print(f"JB Statistic:    {jb_stat:.4f}")
print(f"JB p-value:      {jb_p:.8f}")
adf = adfuller(nifty_ret, autolag='AIC')
print(f"ADF Statistic:   {adf[0]:.4f}")
print(f"ADF p-value:     {adf[1]:.8f}")
crit = adf[4]
print(f"ADF Critical 1%: {crit['1%']:.4f}")
print(f"ADF Critical 5%: {crit['5%']:.4f}")
print(f"ADF Critical 10%:{crit['10%']:.4f}")

print()
print("Downloading all 25 stocks...")
all_rets = []
stock_stats = {}
for sym, name in STOCKS.items():
    try:
        df = yf.download(sym, start='2023-01-01', end='2025-01-01', progress=False, auto_adjust=True)
        r = df['Close'].squeeze().pct_change().dropna() * 100
        all_rets.extend(r.tolist())
        stock_stats[name] = {
            'mean': r.mean(), 'std': r.std(), 'min': r.min(), 'max': r.max(),
            'skew': skew(r), 'kurt': kurtosis(r)
        }
        print(f"  {name}: mean={r.mean():.4f}% std={r.std():.4f}% skew={skew(r):.4f} kurt={kurtosis(r):.4f}")
    except Exception as e:
        print(f"  SKIP {name}: {e}")

all_rets = pd.Series(all_rets).dropna()
print()
print("=== ALL 25 STOCKS POOLED RETURNS STATISTICS ===")
print(f"N observations:  {len(all_rets)}")
print(f"Mean:            {all_rets.mean():.6f}%")
print(f"Median:          {all_rets.median():.6f}%")
print(f"Std Dev:         {all_rets.std():.6f}%")
print(f"Min:             {all_rets.min():.6f}%")
print(f"Max:             {all_rets.max():.6f}%")
print(f"Skewness:        {skew(all_rets):.6f}")
print(f"Kurtosis:        {kurtosis(all_rets):.6f}")
jb2, jb2p = jarque_bera(all_rets)
print(f"JB Statistic:    {jb2:.4f}")
print(f"JB p-value:      {jb2p:.8f}")
adf2 = adfuller(all_rets.iloc[:5000], autolag='AIC')
print(f"ADF Statistic:   {adf2[0]:.4f}")
print(f"ADF p-value:     {adf2[1]:.8f}")

# Agent portfolio returns stats
print()
print("=== AGENT PORTFOLIO RETURNS (from backtesting) ===")
# Combined AI portfolio returns
# Using known results from notebook execution
print("Agent 1 (RSI+MACD+MA50):  Return=+15.01%  Sharpe=0.597  MaxDD=-20.39%")
print("Agent 2 (Sector Rotation): Return=+110.99% Sharpe=N/A    MaxDD=N/A")
print("Agent 3 (Smart Money):     Return=+11.60%  Sharpe=N/A    MaxDD=N/A")
print("Agent 4 (VADER Sentiment): Return=+25.70%  p-value=2.74e-78")
print("Agent 5 (VaR 95%):         Accurate=8/25 stocks")
print("Agent 6 (Volume >1.5x):    Events=1444  p=0.272 (not significant)")
print("Combined AI:               Return=+26.21%  Sharpe=1.246  MaxDD=-10.01%")
print("NIFTY 50 Benchmark:        Return=+29.93%  Sharpe=1.171")
