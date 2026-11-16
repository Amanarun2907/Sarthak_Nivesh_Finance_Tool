
# ─── CHART 8: RISK METRICS ────────────────────────────────────────────────────
print("[9a/9] Chart 8 — Risk Metrics & Statistical Tests...")

fig, axes = plt.subplots(2, 2, figsize=(16, 11))
fig.suptitle("Risk Metrics, Statistical Validation & Confidence Calibration",
             fontsize=14, fontweight="bold")

# --- Sharpe, Calmar, Max Drawdown per strategy
buy_ipos = df[df["signal"].isin(["STRONG_BUY","BUY"])]
all_ipos = df.copy()

def sharpe(returns, rf=0.065):
    r = returns / 100.0
    excess = r.mean() - rf / 12
    return (excess / r.std() * (12**0.5)) if r.std() > 0 else 0.0

def max_dd(returns):
    cum = (1 + returns/100).cumprod()
    return ((cum - cum.cummax()) / cum.cummax()).min() * 100

ax0 = axes[0][0]
strategies_comp = {
    "Framework\n(BUY signals)": buy_ipos["ret_90d"],
    "Benchmark\n(All IPOs)":    all_ipos["ret_90d"],
}
metrics = {}
for name, rets in strategies_comp.items():
    if len(rets) > 0:
        metrics[name] = {
            "Mean Return (%)":     rets.mean(),
            "Std Dev (%)":         rets.std(),
            "Sharpe Ratio":        sharpe(rets),
            "Win Rate (%)":        (rets > 0).mean() * 100,
            "Max Drawdown (%)":    max_dd(rets.reset_index(drop=True)),
        }

df_metrics = pd.DataFrame(metrics).T
x4 = np.arange(len(df_metrics.columns))
width4 = 0.35
fw_vals_m  = [df_metrics.iloc[0][c] for c in df_metrics.columns]
bh_vals_m  = [df_metrics.iloc[1][c] for c in df_metrics.columns]
ax0.bar(x4 - width4/2, fw_vals_m, width=width4,
        label="Framework", color=C["strong_buy"], edgecolor="white", alpha=0.85)
ax0.bar(x4 + width4/2, bh_vals_m, width=width4,
        label="Benchmark", color=C["sell"], edgecolor="white", alpha=0.85)
ax0.set_xticks(x4)
ax0.set_xticklabels(df_metrics.columns, rotation=20, ha="right", fontsize=8.5)
ax0.set_title("Framework vs Benchmark — Key Metrics", fontweight="bold")
ax0.legend(fontsize=9)
ax0.axhline(0, color="black", linewidth=1, alpha=0.3)
ax0.set_facecolor("#F8F9FA")
for i, (fv, bv) in enumerate(zip(fw_vals_m, bh_vals_m)):
    ax0.text(i - width4/2, fv + 0.3, f"{fv:.1f}", ha="center",
             va="bottom", fontsize=7.5, color=C["strong_buy"])
    ax0.text(i + width4/2, bv + 0.3, f"{bv:.1f}", ha="center",
             va="bottom", fontsize=7.5, color=C["sell"])

# --- T-test: BUY signal returns vs SELL/HOLD returns
ax1 = axes[0][1]
buy_group  = df[df["signal"].isin(["STRONG_BUY","BUY"])]["ret_90d"].dropna()
sell_group = df[df["signal"].isin(["SELL","STRONG_SELL","HOLD"])]["ret_90d"].dropna()
if len(buy_group) > 1 and len(sell_group) > 1:
    t_stat, p_value = stats.ttest_ind(buy_group, sell_group, equal_var=False)
    ax1.hist(buy_group,  bins=8, alpha=0.75, color=C["strong_buy"],
             label=f"BUY signals  (n={len(buy_group)}, mean={buy_group.mean():.1f}%)",
             edgecolor="white")
    ax1.hist(sell_group, bins=8, alpha=0.75, color=C["loss"],
             label=f"SELL/HOLD    (n={len(sell_group)}, mean={sell_group.mean():.1f}%)",
             edgecolor="white")
    ax1.axvline(buy_group.mean(),  color=C["strong_buy"], linewidth=2,
                linestyle="--", alpha=0.9)
    ax1.axvline(sell_group.mean(), color=C["loss"],        linewidth=2,
                linestyle="--", alpha=0.9)
    sig_str = "SIGNIFICANT" if p_value < 0.05 else "Not significant"
    ax1.text(0.05, 0.96,
             f"Welch t-test\nt = {t_stat:.3f}\np = {p_value:.4f}\n{sig_str} (α=0.05)",
             transform=ax1.transAxes, va="top", fontsize=9,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="lightyellow", alpha=0.9))
ax1.set_xlabel("90-Day Return (%)", fontweight="bold")
ax1.set_ylabel("Number of IPOs", fontweight="bold")
ax1.set_title("Distribution: BUY Signals vs SELL/HOLD\n(Welch's t-test)", fontweight="bold")
ax1.legend(fontsize=8)
ax1.set_facecolor("#F8F9FA")

# --- Agent score correlation heatmap
ax2 = axes[1][0]
corr_cols = ["sc_price","sc_macro","sc_sent","sc_risk","sc_ipo","sc_orch","ret_90d"]
corr_matrix = df[corr_cols].corr()
corr_labels = ["Price\nAgent","Macro\nAgent","Sentiment\nAgent","Risk\nAgent",
               "IPO\nAgent","Orchestrator","90d\nReturn"]
mask = np.zeros_like(corr_matrix, dtype=bool)
np.fill_diagonal(mask, True)
sns.heatmap(corr_matrix, ax=ax2, cmap="RdYlGn", vmin=-1, vmax=1,
            annot=True, fmt=".2f", annot_kws={"size":8.5},
            xticklabels=corr_labels, yticklabels=corr_labels,
            linewidths=0.5, cbar_kws={"label":"Pearson r"},
            mask=mask if not mask.all() else None)
ax2.set_title("Agent Score Correlation Matrix\n(Pearson r, includes 90-Day Return)",
              fontweight="bold")
ax2.tick_params(axis="x", rotation=0, labelsize=8)
ax2.tick_params(axis="y", rotation=0, labelsize=8)

# --- Confidence calibration: score deciles vs actual win rate
ax3 = axes[1][1]
df["score_decile"] = pd.qcut(df["sc_orch"], q=5,
                              labels=["0-20","20-40","40-60","60-80","80-100"],
                              duplicates="drop")
cal = df.groupby("score_decile", observed=True)["win_90d"].agg(["mean","count"]).reset_index()
cal["win_rate"] = cal["mean"] * 100
bar_cols = [C["win"] if w >= 50 else C["loss"] for w in cal["win_rate"]]
ax3.bar(cal["score_decile"].astype(str), cal["win_rate"],
        color=bar_cols, edgecolor="white", width=0.6, alpha=0.85)
ax3.axhline(50, color="grey", linestyle="--", linewidth=1.5, alpha=0.7,
            label="Random (50%)")
ax3.set_xlabel("Orchestrator Score Quintile", fontweight="bold")
ax3.set_ylabel("Actual Win Rate (%)", fontweight="bold")
ax3.set_title("Confidence Calibration\n(Higher Score → Higher Win Rate?)",
              fontweight="bold")
ax3.set_ylim(0, 115)
ax3.legend(fontsize=9)
ax3.set_facecolor("#F8F9FA")
for i, (_, r) in enumerate(cal.iterrows()):
    ax3.text(i, r["win_rate"] + 1.5, f"{r['win_rate']:.0f}%\n(n={int(r['count'])})",
             ha="center", va="bottom", fontsize=9, fontweight="bold",
             color=C["win"] if r["win_rate"] >= 50 else C["loss"])

plt.tight_layout()
p8 = os.path.join(OUT, "bt_chart8_risk_stats.png")
plt.savefig(p8, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p8}")
