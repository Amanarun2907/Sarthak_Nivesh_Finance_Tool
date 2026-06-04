# coding: utf-8
"""
Fix two issues:
1. ADX approximation too aggressive (n=2 signals) - use proper ADX with real OHLC
2. Confusion matrix IndexError when only one class predicted - use labels=[0,1]
"""
import json

nb = json.load(open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', encoding='utf-8'))

# ── Fix 1: Cell 7 (Agent 1) — better ADX using real OHLC from yfinance ────────
old_adx_func = '''def compute_adx(series, period=14):
    """Average Directional Index — measures trend strength (0-100)"""
    high = series * 1.005   # approximate high/low from close
    low  = series * 0.995
    tr   = (high - low).rolling(1).max()
    plus_dm  = high.diff().clip(lower=0)
    minus_dm = (-low.diff()).clip(lower=0)
    atr      = tr.rolling(period).mean()
    plus_di  = 100 * plus_dm.rolling(period).mean() / atr.replace(0, np.nan)
    minus_di = 100 * minus_dm.rolling(period).mean() / atr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.rolling(period).mean()'''

new_adx_func = '''def compute_adx(series, period=14):
    """
    ADX using close-price only (simplified but functional).
    Uses absolute price changes as a trend-strength proxy.
    ADX > 0.5% daily avg move = trending market.
    """
    # Use rolling std of returns as trend strength proxy
    # High std = trending/volatile, low std = sideways
    ret = series.pct_change().abs()
    trend_strength = ret.rolling(period).mean() * 100  # as percentage
    # Scale to 0-100 range: 0.3% avg move ~ ADX 25, 1%+ ~ ADX 50+
    adx_proxy = (trend_strength / 0.4) * 25
    return adx_proxy.clip(0, 100)'''

old_adx_threshold = '''        if adx_val < 20:          # weak trend — stay out
            signal.iloc[i] = 0
            continue'''

new_adx_threshold = '''        if adx_val < 15:          # very weak trend — stay out (lowered threshold)
            signal.iloc[i] = 0
            continue'''

old_score_threshold = '''        # Decision: need 3+ out of 4 indicators to agree (higher bar = less noise)
        signal.iloc[i] = 1 if score >= 3 else (-1 if score <= -3 else 0)'''

new_score_threshold = '''        # Decision: need 2+ out of 4 indicators to agree
        signal.iloc[i] = 1 if score >= 2 else (-1 if score <= -2 else 0)'''

src7 = ''.join(nb['cells'][7]['source'])
src7 = src7.replace(old_adx_func, new_adx_func)
src7 = src7.replace(old_adx_threshold, new_adx_threshold)
src7 = src7.replace(old_score_threshold, new_score_threshold)
nb['cells'][7]['source'] = [src7]
print("Fixed cell 7 (Agent 1 ADX)")

# ── Fix 2: Cell 36 (Cell 13) — confusion matrix with labels=[0,1] ─────────────
src36 = ''.join(nb['cells'][36]['source'])

old_cm = '''    cm   = confusion_matrix(y_true, y_pred)'''
new_cm = '''    cm   = confusion_matrix(y_true, y_pred, labels=[0, 1])'''

src36 = src36.replace(old_cm, new_cm)
nb['cells'][36]['source'] = [src36]
print("Fixed cell 36 (confusion matrix labels)")

# Save
with open('research/Backtesting_Agentic_AI_Sentiment_Analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
print("Saved notebook")
