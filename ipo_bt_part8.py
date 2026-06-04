
# ─── CHART 6: AGENT-WISE ACCURACY ─────────────────────────────────────────────
print("[8a/9] Chart 6 — Agent-Wise Accuracy & Correlation...")

fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle("Agent-Wise Predictive Accuracy — Score vs 90-Day Outcome",
             fontsize=15, fontweight="bold")

agent_cfg = [
    ("sc_price",  "Price Movement Agent",   C["price"]),
    ("sc_macro",  "Macroeconomic Agent",     C["macro"]),
    ("sc_sent",   "Sentiment Agent",         C["sentiment"]),
    ("sc_risk",   "Risk Agent",              C["risk"]),
    ("sc_ipo",    "IPO Intelligence Agent",  C["ipo"]),
    ("sc_orch",   "Orchestrator (Combined)", C["orch"]),
]
correlations = {}
for ax, (col, title, color) in zip(axes.flat, agent_cfg):
    win_scores  = df[df["win_90d"] == 1][col].dropna()
    loss_scores = df[df["win_90d"] == 0][col].dropna()

    ax.scatter(df[col], df["ret_90d"],
               c=[C["win"] if w else C["loss"] for w in df["win_90d"]],
               s=70, alpha=0.85, edgecolors="white", linewidth=0.5, zorder=3)

    # Trend line
    valid = df[[col, "ret_90d"]].dropna()
    if len(valid) > 2:
        z = np.polyfit(valid[col], valid["ret_90d"], 1)
        p = np.poly1d(z)
        xs = np.linspace(valid[col].min(), valid[col].max(), 100)
        ax.plot(xs, p(xs), color=color, linewidth=2, linestyle="--", alpha=0.9)
        r, pv = stats.pearsonr(valid[col], valid["ret_90d"])
        correlations[title] = r
        # accuracy: fraction where score>50 AND win
        high_score = df[df[col] > 50]
        acc = high_score["win_90d"].mean() * 100 if len(high_score) > 0 else 0
        info = f"r={r:.3f} | p={pv:.3f}\nAcc (score>50): {acc:.0f}%"
        ax.text(0.04, 0.96, info, transform=ax.transAxes,
                va="top", fontsize=8.5,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.85))

    ax.axhline(0, color="black", linewidth=1, linestyle="-", alpha=0.3)
    ax.axvline(50, color="grey", linewidth=1, linestyle="--", alpha=0.4)
    ax.set_xlabel(f"{title} Score", fontsize=9, fontweight="bold")
    ax.set_ylabel("90-Day Return (%)", fontsize=9, fontweight="bold")
    ax.set_title(title, fontweight="bold", color=color, fontsize=11)
    ax.set_facecolor("#F8F9FA")

    # Annotate IPO names
    for _, row in df.iterrows():
        ax.annotate(row["name"][:7],
                    (row[col], row["ret_90d"]),
                    textcoords="offset points", xytext=(3, 2),
                    fontsize=5.5, alpha=0.65)

plt.tight_layout()
p6 = os.path.join(OUT, "bt_chart6_agent_accuracy.png")
plt.savefig(p6, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p6}")

# ─── CHART 7: SUBSCRIPTION vs RETURNS ─────────────────────────────────────────
print("[8b/9] Chart 7 — Subscription & QIB vs Returns...")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Subscription Data vs Post-Listing Returns",
             fontsize=14, fontweight="bold")

# QIB vs 90d return
ax0 = axes[0]
ax0.scatter(df["qib"], df["ret_90d"],
            c=[C["win"] if w else C["loss"] for w in df["win_90d"]],
            s=80, alpha=0.85, edgecolors="white", linewidth=0.5)
if len(df) > 2:
    z = np.polyfit(df["qib"], df["ret_90d"], 1)
    p = np.poly1d(z)
    xs = np.linspace(df["qib"].min(), df["qib"].max(), 100)
    ax0.plot(xs, p(xs), color="navy", linewidth=2, linestyle="--", alpha=0.8)
    r, pv = stats.pearsonr(df["qib"], df["ret_90d"])
    ax0.text(0.04, 0.96, f"r={r:.3f} | p={pv:.3f}", transform=ax0.transAxes,
             va="top", fontsize=9,
             bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.85))
ax0.axhline(0, color="black", linewidth=1, alpha=0.4)
ax0.set_xlabel("QIB Subscription (×)", fontweight="bold")
ax0.set_ylabel("90-Day Return (%)", fontweight="bold")
ax0.set_title("QIB Subscription vs 90-Day Return", fontweight="bold")
ax0.set_facecolor("#F8F9FA")
for _, row in df.iterrows():
    ax0.annotate(row["name"][:8], (row["qib"], row["ret_90d"]),
                 textcoords="offset points", xytext=(3, 2), fontsize=6.5, alpha=0.7)

# Total sub vs listing return
ax1 = axes[1]
ax1.scatter(df["sub"], df["ret_list"],
            c=[C["win"] if w > 0 else C["loss"] for w in df["ret_list"]],
            s=80, alpha=0.85, edgecolors="white", linewidth=0.5)
if len(df) > 2:
    z2  = np.polyfit(df["sub"], df["ret_list"], 1)
    p2  = np.poly1d(z2)
    xs2 = np.linspace(df["sub"].min(), df["sub"].max(), 100)
    ax1.plot(xs2, p2(xs2), color="purple", linewidth=2, linestyle="--", alpha=0.8)
    r2, pv2 = stats.pearsonr(df["sub"], df["ret_list"])
    ax1.text(0.04, 0.96, f"r={r2:.3f} | p={pv2:.3f}", transform=ax1.transAxes,
             va="top", fontsize=9,
             bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.85))
ax1.axhline(0, color="black", linewidth=1, alpha=0.4)
ax1.set_xlabel("Total Subscription (×)", fontweight="bold")
ax1.set_ylabel("Listing Day Return (%)", fontweight="bold")
ax1.set_title("Total Subscription vs Listing-Day Return", fontweight="bold")
ax1.set_facecolor("#F8F9FA")

# Return buckets by subscription range
ax2 = axes[2]
bins = [0, 5, 20, 50, 200, 500]
labels_b = ["<5x","5-20x","20-50x","50-200x",">200x"]
df["sub_bucket"] = pd.cut(df["sub"], bins=bins, labels=labels_b)
bucket_ret = df.groupby("sub_bucket", observed=True)["ret_90d"].agg(["mean","std","count"])
x_pos = np.arange(len(bucket_ret))
cols_b = [C["strong_buy"] if m > 0 else C["loss"] for m in bucket_ret["mean"]]
ax2.bar(x_pos, bucket_ret["mean"], color=cols_b, edgecolor="white",
        width=0.6, alpha=0.85)
ax2.errorbar(x_pos, bucket_ret["mean"], yerr=bucket_ret["std"],
             fmt="none", ecolor="black", capsize=4, linewidth=1.2)
ax2.axhline(0, color="black", linewidth=1, linestyle="-", alpha=0.4)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(labels_b, fontsize=10)
ax2.set_ylabel("Avg 90-Day Return (%)", fontweight="bold")
ax2.set_title("Avg 90-Day Return by Subscription Band", fontweight="bold")
ax2.set_facecolor("#F8F9FA")
for i, (_, r) in enumerate(bucket_ret.iterrows()):
    ax2.text(i, r["mean"] + 1, f"n={int(r['count'])}", ha="center",
             va="bottom", fontsize=9, color="navy")

plt.tight_layout()
p7 = os.path.join(OUT, "bt_chart7_subscription.png")
plt.savefig(p7, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p7}")
