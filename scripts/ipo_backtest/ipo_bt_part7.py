
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
