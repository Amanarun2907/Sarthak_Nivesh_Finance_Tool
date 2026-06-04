
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
