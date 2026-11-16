
# ─── CHART 9: COMPREHENSIVE SUMMARY DASHBOARD ────────────────────────────────
print("[9b/9] Chart 9 — Summary Dashboard...")

fig = plt.figure(figsize=(20, 14))
fig.patch.set_facecolor("white")
gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.55, wspace=0.4)
fig.suptitle("IPO Multi-Agent Framework — Backtesting Summary Dashboard\n"
             "25 Real NSE/BSE IPOs | 2021–2024 | Groq Llama 3.3 70B",
             fontsize=16, fontweight="bold", y=0.98)

# [0,0] Signal distribution
ax00 = fig.add_subplot(gs[0, 0])
sig_c = df["signal"].value_counts().reindex(sig_order, fill_value=0)
sig_colors_list = [C[s.lower()] for s in sig_order]
ax00.bar(sig_c.index, sig_c.values, color=sig_colors_list, edgecolor="white")
ax00.set_title("Signal Distribution", fontweight="bold", fontsize=11)
ax00.set_ylabel("Count")
ax00.tick_params(axis="x", rotation=20, labelsize=7.5)
ax00.set_facecolor("#F8F9FA")
for i, v in enumerate(sig_c.values):
    ax00.text(i, v + 0.05, str(v), ha="center", va="bottom", fontsize=9)

# [0,1] Return timeline
ax01 = fig.add_subplot(gs[0, 1])
df_t = df.sort_values("date").reset_index(drop=True)
ax01.plot(range(len(df_t)), df_t["ret_list"],  "o-", color=C["price"],
          linewidth=1.5, markersize=4, label="Listing Day")
ax01.plot(range(len(df_t)), df_t["ret_90d"],   "s-", color=C["ipo"],
          linewidth=1.5, markersize=4, label="90-Day")
ax01.axhline(0, color="black", linewidth=1, alpha=0.4)
ax01.fill_between(range(len(df_t)), df_t["ret_90d"], 0,
                  where=df_t["ret_90d"] > 0, alpha=0.12, color=C["win"])
ax01.fill_between(range(len(df_t)), df_t["ret_90d"], 0,
                  where=df_t["ret_90d"] <= 0, alpha=0.12, color=C["loss"])
ax01.set_title("Returns Timeline (Chronological)", fontweight="bold", fontsize=11)
ax01.set_ylabel("Return (%)")
ax01.legend(fontsize=8)
ax01.set_facecolor("#F8F9FA")
ax01.tick_params(axis="x", labelsize=7)
ax01.set_xticks(range(len(df_t)))
ax01.set_xticklabels(df_t["name"].str[:6], rotation=45, ha="right", fontsize=6)

# [0,2-3] KPI summary text box
ax02 = fig.add_subplot(gs[0, 2:])
ax02.axis("off")
buy_ipos_2 = df[df["signal"].isin(["STRONG_BUY","BUY"])]
kpis = [
    ("IPOs Analysed",            f"{len(df)}"),
    ("Avg Listing Gain",         f"{df.ret_list.mean():.1f}%"),
    ("Avg 90-Day Return",        f"{df.ret_90d.mean():.1f}%"),
    ("Framework Accuracy (90d)", f"{df.win_90d.mean()*100:.1f}%"),
    ("BUY Signal Accuracy",      f"{buy_ipos_2.win_90d.mean()*100:.1f}%" if len(buy_ipos_2)>0 else "N/A"),
    ("Best Performer",           f"{df.loc[df.ret_90d.idxmax(),'name']} ({df.ret_90d.max():.0f}%)"),
    ("Worst Performer",          f"{df.loc[df.ret_90d.idxmin(),'name']} ({df.ret_90d.min():.0f}%)"),
    ("Orch Score vs Return (r)", f"{df[['sc_orch','ret_90d']].corr().iloc[0,1]:.3f}"),
]
y_pos = 0.95
for label, val in kpis:
    # Safely determine color from the value
    try:
        # Strip everything after first space or '(' to get a clean number
        clean = val.replace("%","").replace("+","").strip()
        clean = clean.split("(")[0].strip().split(" ")[0]
        num   = float(clean)
        color = C["win"] if num > 0 else C["loss"] if num < 0 else "navy"
    except Exception:
        color = "navy"
    ax02.text(0.05, y_pos, f"• {label}:", transform=ax02.transAxes,
              fontsize=11, va="top", color="#333333", fontweight="bold")
    ax02.text(0.60, y_pos, val, transform=ax02.transAxes,
              fontsize=11, va="top", color=color, fontweight="bold")
    y_pos -= 0.115
ax02.text(0.05, 0.02, "Data: Yahoo Finance (real) | NSE/BSE Official | ipowatch.in",
          transform=ax02.transAxes, fontsize=8, color="grey", style="italic")

# [1,0-1] Listing gain waterfall
ax10 = fig.add_subplot(gs[1, 0:2])
df_wf = df.sort_values("ret_list").reset_index(drop=True)
c_wf  = [C["win"] if x > 0 else C["loss"] for x in df_wf["ret_list"]]
ax10.bar(range(len(df_wf)), df_wf["ret_list"], color=c_wf, edgecolor="white", width=0.7)
ax10.axhline(0, color="black", linewidth=1.2, alpha=0.5)
ax10.axhline(df_wf["ret_list"].mean(), color="navy", linestyle="--",
             linewidth=1.5, alpha=0.7, label=f"Mean: {df_wf['ret_list'].mean():.1f}%")
ax10.set_xticks(range(len(df_wf)))
ax10.set_xticklabels(df_wf["name"], rotation=45, ha="right", fontsize=7)
ax10.set_ylabel("Listing Day Return (%)", fontweight="bold")
ax10.set_title("Listing Day Gains — All 25 IPOs (Sorted)", fontweight="bold", fontsize=11)
ax10.legend(fontsize=9)
ax10.set_facecolor("#F8F9FA")

# [1,2-3] Orchestrator score distribution
ax12 = fig.add_subplot(gs[1, 2:])
bins_o = [0,30,45,65,80,100]
lab_o  = ["STRONG\nSELL","SELL","HOLD","BUY","STRONG\nBUY"]
col_o  = [C["strong_sell"],C["sell"],C["hold"],C["buy"],C["strong_buy"]]
counts_o = pd.cut(df["sc_orch"], bins=bins_o, labels=lab_o).value_counts().reindex(lab_o, fill_value=0)
ax12.bar(lab_o, counts_o.values, color=col_o, edgecolor="white", width=0.6)
ax12.set_ylabel("Number of IPOs", fontweight="bold")
ax12.set_title("Orchestrator Score → Signal Mapping", fontweight="bold", fontsize=11)
ax12.set_facecolor("#F8F9FA")
for i, v in enumerate(counts_o.values):
    ax12.text(i, v + 0.05, str(v), ha="center", va="bottom", fontsize=10, fontweight="bold")
ranges_txt = ["<30","30-45","45-65","65-80",">80"]
for i, rt in enumerate(ranges_txt):
    ax12.text(i, -0.3, rt, ha="center", va="top", fontsize=8, color="grey",
              transform=ax12.get_xaxis_transform())

# [2,0-3] Agent score box plot
ax20 = fig.add_subplot(gs[2, :])
score_data = [df["sc_price"].dropna().values, df["sc_macro"].dropna().values,
              df["sc_sent"].dropna().values,  df["sc_risk"].dropna().values,
              df["sc_ipo"].dropna().values,   df["sc_orch"].dropna().values]
agent_lbls = ["Price\nMovement\n(20%)","Macro-\neconomic\n(15%)",
              "Sentiment\n(20%)","Risk\n(20%)","IPO\nIntelligence\n(25%)","Orchestrator\n(Combined)"]
bp = ax20.boxplot(score_data, labels=agent_lbls, patch_artist=True,
                  boxprops=dict(linewidth=1.5),
                  medianprops=dict(color="navy", linewidth=2),
                  whiskerprops=dict(linewidth=1.2),
                  capprops=dict(linewidth=1.5),
                  flierprops=dict(marker="o", markersize=4, alpha=0.5))
box_colors = [C["price"],C["macro"],C["sentiment"],C["risk"],C["ipo"],C["orch"]]
for patch, color in zip(bp["boxes"], box_colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax20.axhline(50, color="grey", linestyle="--", linewidth=1.5, alpha=0.6, label="Neutral (50)")
ax20.axhline(65, color="green", linestyle=":", linewidth=1.5, alpha=0.6, label="BUY (65)")
ax20.set_ylabel("Agent Score (0-100)", fontweight="bold")
ax20.set_title("Agent Score Distribution — Box Plot (All 25 IPOs)", fontweight="bold")
ax20.legend(fontsize=9)
ax20.set_facecolor("#F8F9FA")
ax20.set_ylim(0, 110)

p9 = os.path.join(OUT, "bt_chart9_dashboard.png")
plt.savefig(p9, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved: {p9}")

# ─── PRINT FINAL SUMMARY ─────────────────────────────────────────────────────
buy_ipos_f = df[df["signal"].isin(["STRONG_BUY","BUY"])]
print("\n" + "="*65)
print("  IPO MULTI-AGENT BACKTESTING — FINAL RESULTS")
print("="*65)
print(f"  Total IPOs analysed     : {len(df)}")
print(f"  Period                  : 2021-07 to 2024-11")
print(f"  Data source             : Yahoo Finance (real)")
print(f"  Avg Listing-day return  : {df.ret_list.mean():.1f}%")
print(f"  Avg 30-day return       : {df.ret_30d.mean():.1f}%")
print(f"  Avg 60-day return       : {df.ret_60d.mean():.1f}%")
print(f"  Avg 90-day return       : {df.ret_90d.mean():.1f}%")
print(f"  Overall accuracy (90d)  : {df.win_90d.mean()*100:.1f}%")
if len(buy_ipos_f) > 0:
    print(f"  BUY signal accuracy     : {buy_ipos_f.win_90d.mean()*100:.1f}%")
    print(f"  BUY signal avg return   : {buy_ipos_f.ret_90d.mean():.1f}%")
corr_r = df[["sc_orch","ret_90d"]].corr().iloc[0,1]
print(f"  Orch score correlation  : r={corr_r:.3f}")
print(f"  Best performing IPO     : {df.loc[df.ret_90d.idxmax(),'name']} (+{df.ret_90d.max():.0f}%)")
print(f"  Worst performing IPO    : {df.loc[df.ret_90d.idxmin(),'name']} ({df.ret_90d.min():.0f}%)")
print("="*65)
print("\nCharts saved:")
for i in range(1, 10):
    fp = os.path.join(OUT, f"bt_chart{i}_*.png")
    import glob
    matches = glob.glob(fp)
    for m in matches:
        print(f"  {m}")
print("\n[DONE] All backtesting complete!")
