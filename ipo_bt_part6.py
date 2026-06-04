
# ─── CHART 3: AGENT SCORES RADAR / HEATMAP ───────────────────────────────────
print("[6a/9] Chart 3 — Agent Scores Heatmap...")

score_cols  = ["sc_price","sc_macro","sc_sent","sc_risk","sc_ipo","sc_orch"]
agent_names = ["Price\nMovement","Macro-\neconomic","Sentiment","Risk","IPO\nIntelligence","Orchestrator"]

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Agent Score Analysis — All 25 IPOs", fontsize=15, fontweight="bold")

# Left: heatmap
heat_data = df[score_cols].rename(columns=dict(zip(score_cols, agent_names)))
sns.heatmap(heat_data.set_index(df["name"]),
            ax=axes[0], cmap="RdYlGn", vmin=0, vmax=100,
            annot=True, fmt=".0f", annot_kws={"size":7},
            linewidths=0.5, cbar_kws={"label":"Score (0-100)"})
axes[0].set_title("Agent Scores per IPO (0-100)", fontweight="bold")
axes[0].set_xlabel("Agent", fontweight="bold")
axes[0].tick_params(axis="x", rotation=0, labelsize=8)
axes[0].tick_params(axis="y", labelsize=7.5)

# Right: avg agent scores comparison
avg_scores = df[score_cols].mean()
colors_ag  = [C["price"],C["macro"],C["sentiment"],C["risk"],C["ipo"],C["orch"]]
bars = axes[1].bar(agent_names, avg_scores.values, color=colors_ag,
                   edgecolor="white", linewidth=0.8, width=0.6)
axes[1].axhline(50, color="grey", linestyle="--", linewidth=1.2, alpha=0.7, label="Neutral (50)")
axes[1].axhline(65, color="green", linestyle=":", linewidth=1.5, alpha=0.7, label="BUY threshold (65)")
for bar, val in zip(bars, avg_scores.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{val:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
axes[1].set_ylim(0, 100)
axes[1].set_ylabel("Average Score", fontweight="bold")
axes[1].set_title("Average Score per Agent (all 25 IPOs)", fontweight="bold")
axes[1].legend(fontsize=9)
axes[1].set_facecolor("#F8F9FA")

plt.tight_layout()
p3 = os.path.join(OUT, "bt_chart3_agent_scores.png")
plt.savefig(p3, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p3}")

# ─── CHART 4: SIGNAL ACCURACY ─────────────────────────────────────────────────
print("[6b/9] Chart 4 — Signal Accuracy vs Actual Outcomes...")
sig_order = ["STRONG_BUY","BUY","HOLD","SELL","STRONG_SELL"]
sig_colors = [C["strong_buy"],C["buy"],C["hold"],C["sell"],C["strong_sell"]]

accuracy_data = {}
for sig in sig_order:
    sub_df = df[df["signal"] == sig]
    if len(sub_df) > 0:
        acc = sub_df["win_90d"].mean() * 100
        cnt = len(sub_df)
        accuracy_data[sig] = {"accuracy": acc, "count": cnt}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Signal Accuracy Analysis — Framework vs Benchmark", fontsize=15, fontweight="bold")

# Left: accuracy per signal
sigs_present = [s for s in sig_order if s in accuracy_data]
accs  = [accuracy_data[s]["accuracy"] for s in sigs_present]
cnts  = [accuracy_data[s]["count"]    for s in sigs_present]
scols = [C[s.lower()] for s in sigs_present]
bars  = axes[0].bar(sigs_present, accs, color=scols, edgecolor="white", width=0.6)
axes[0].axhline(50, color="grey", linestyle="--", alpha=0.6, linewidth=1.2, label="Random (50%)")
axes[0].axhline(df["win_90d"].mean()*100, color="navy", linestyle="-.",
                linewidth=1.5, alpha=0.7,
                label=f'Overall ({df["win_90d"].mean()*100:.0f}%)')
for bar, val, cnt in zip(bars, accs, cnts):
    axes[0].text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 1,
                 f"{val:.0f}%\n(n={cnt})", ha="center", va="bottom", fontsize=9)
axes[0].set_ylim(0, 110)
axes[0].set_ylabel("90-Day Win Rate (%)", fontweight="bold")
axes[0].set_title("Accuracy by Signal Type", fontweight="bold")
axes[0].legend(fontsize=8)
axes[0].tick_params(axis="x", rotation=15)
axes[0].set_facecolor("#F8F9FA")

# Middle: score vs 90d return scatter
sc2 = axes[1]
sc2.scatter(df["sc_orch"], df["ret_90d"],
            c=[C["win"] if w else C["loss"] for w in df["win_90d"]],
            s=80, alpha=0.8, edgecolors="white", linewidth=0.5)
if len(df) > 2:
    z   = np.polyfit(df["sc_orch"], df["ret_90d"], 1)
    p   = np.poly1d(z)
    xs  = np.linspace(df["sc_orch"].min(), df["sc_orch"].max(), 100)
    sc2.plot(xs, p(xs), color="navy", linewidth=2, linestyle="--", label="Trend line")
    r, pv = stats.pearsonr(df["sc_orch"], df["ret_90d"])
    sc2.text(0.05, 0.93, f"Pearson r = {r:.3f}\np-value  = {pv:.4f}",
             transform=sc2.transAxes, fontsize=9,
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.9))
sc2.axhline(0, color="black", linewidth=1, linestyle="-", alpha=0.4)
sc2.axvline(65, color="green", linewidth=1.2, linestyle=":", alpha=0.6, label="BUY threshold (65)")
sc2.set_xlabel("Orchestrator Score (0-100)", fontweight="bold")
sc2.set_ylabel("Actual 90-Day Return (%)", fontweight="bold")
sc2.set_title("Score vs Actual Return (Correlation)", fontweight="bold")
sc2.legend(fontsize=8)
for _, row in df.iterrows():
    sc2.annotate(row["name"][:8], (row["sc_orch"], row["ret_90d"]),
                 textcoords="offset points", xytext=(3,3), fontsize=6.5, alpha=0.7)
sc2.set_facecolor("#F8F9FA")

# Right: decision distribution pie
dec_counts = df["decision"].value_counts()
dec_colors_map = {"INVEST":C["strong_buy"],"PARTIAL_INVEST":C["buy"],
                  "HOLD":C["hold"],"EXIT":C["sell"],"STRONG_EXIT":C["strong_sell"]}
pie_colors = [dec_colors_map.get(d, "grey") for d in dec_counts.index]
wedges, texts, autotexts = axes[2].pie(
    dec_counts.values, labels=dec_counts.index, colors=pie_colors,
    autopct="%1.0f%%", startangle=90, pctdistance=0.75,
    wedgeprops=dict(edgecolor="white", linewidth=1.5))
for at in autotexts: at.set_fontsize(9); at.set_fontweight("bold")
axes[2].set_title("Decision Distribution (Orchestrator)", fontweight="bold")

plt.tight_layout()
p4 = os.path.join(OUT, "bt_chart4_accuracy.png")
plt.savefig(p4, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p4}")
