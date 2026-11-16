
# ─── CHART 1: IPO LISTING GAINS ──────────────────────────────────────────────
print("[5a/9] Chart 1 — IPO Listing Gains...")
df_sorted = df.sort_values("ret_list", ascending=True).reset_index(drop=True)
colors_bar = [C["win"] if x > 0 else C["loss"] for x in df_sorted["ret_list"]]

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("IPO Listing Performance — 25 Real NSE/BSE IPOs (2021–2024)",
             fontsize=15, fontweight="bold", y=1.01)

# Left: horizontal bar chart
ax = axes[0]
bars = ax.barh(df_sorted["name"], df_sorted["ret_list"],
               color=colors_bar, edgecolor="white", linewidth=0.5)
ax.axvline(0, color="black", linewidth=1.2, linestyle="--", alpha=0.6)
for bar, val in zip(bars, df_sorted["ret_list"]):
    ax.text(val + (1 if val >= 0 else -1),
            bar.get_y() + bar.get_height()/2,
            f"{val:+.1f}%", va="center", ha="left" if val >= 0 else "right",
            fontsize=8, fontweight="bold",
            color=C["win"] if val > 0 else C["loss"])
ax.set_xlabel("Listing Day Return (%)", fontweight="bold")
ax.set_title("Listing Day Returns (sorted)", fontweight="bold")
win_patch  = mpatches.Patch(color=C["win"],  label=f'Profitable ({(df_sorted.ret_list>0).sum()})')
loss_patch = mpatches.Patch(color=C["loss"], label=f'Loss ({(df_sorted.ret_list<=0).sum()})')
ax.legend(handles=[win_patch, loss_patch], fontsize=9)
ax.set_facecolor("#F8F9FA")
ax.grid(axis="x", alpha=0.3)

# Right: distribution histogram
ax2 = axes[1]
ax2.hist(df_sorted["ret_list"], bins=12, color=C["orch"], edgecolor="white",
         linewidth=0.8, alpha=0.85)
ax2.axvline(df_sorted["ret_list"].mean(), color="red", linewidth=2,
            linestyle="--", label=f'Mean: {df_sorted["ret_list"].mean():.1f}%')
ax2.axvline(0, color="black", linewidth=1.5, linestyle="-", alpha=0.5)
ax2.fill_betweenx([0, ax2.get_ylim()[1] if ax2.get_ylim()[1] > 0 else 10],
                  df_sorted["ret_list"].min(), 0, alpha=0.05, color=C["loss"])
ax2.set_xlabel("Listing Day Return (%)", fontweight="bold")
ax2.set_ylabel("Number of IPOs", fontweight="bold")
ax2.set_title("Return Distribution", fontweight="bold")
ax2.legend(fontsize=9)
ax2.set_facecolor("#F8F9FA")
stats_txt = (f"Mean: {df_sorted.ret_list.mean():.1f}%\n"
             f"Median: {df_sorted.ret_list.median():.1f}%\n"
             f"Std: {df_sorted.ret_list.std():.1f}%\n"
             f"Min: {df_sorted.ret_list.min():.1f}%\n"
             f"Max: {df_sorted.ret_list.max():.1f}%")
ax2.text(0.98, 0.97, stats_txt, transform=ax2.transAxes,
         va="top", ha="right", fontsize=9,
         bbox=dict(boxstyle="round,pad=0.4", facecolor="white", alpha=0.8))

plt.tight_layout()
p1 = os.path.join(OUT, "bt_chart1_listing_gains.png")
plt.savefig(p1, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p1}")

# ─── CHART 2: 30/60/90-DAY PERFORMANCE ───────────────────────────────────────
print("[5b/9] Chart 2 — Multi-Horizon Performance...")
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("IPO Post-Listing Returns: 30-Day | 60-Day | 90-Day",
             fontsize=15, fontweight="bold", y=1.01)

horizons = [("ret_30d","30-Day Returns"), ("ret_60d","60-Day Returns"), ("ret_90d","90-Day Returns")]
for ax, (col, title) in zip(axes, horizons):
    d_s = df.sort_values(col).reset_index(drop=True)
    cols = [C["win"] if x > 0 else C["loss"] for x in d_s[col]]
    ax.barh(d_s["name"], d_s[col], color=cols, edgecolor="white", linewidth=0.4)
    ax.axvline(0, color="black", linewidth=1.2, linestyle="--", alpha=0.6)
    ax.set_xlabel("Return from Issue Price (%)", fontsize=9, fontweight="bold")
    ax.set_title(title, fontweight="bold")
    ax.tick_params(axis="y", labelsize=7.5)
    ax.set_facecolor("#F8F9FA")
    ax.grid(axis="x", alpha=0.3)
    pos = (d_s[col] > 0).sum()
    ax.text(0.02, 0.99, f"Profitable: {pos}/{len(d_s)}\nAvg: {d_s[col].mean():.1f}%",
            transform=ax.transAxes, va="top", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.9))

plt.tight_layout()
p2 = os.path.join(OUT, "bt_chart2_multihorizon.png")
plt.savefig(p2, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p2}")
