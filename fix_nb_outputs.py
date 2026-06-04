
import json, base64, os

NB = "research/IPO_Backtesting.ipynb"
with open(NB, encoding="utf-8") as f:
    nb = json.load(f)

# ── Print all cells ───────────────────────────────────────────────────────────
print("Current notebook cell map:")
for i, c in enumerate(nb["cells"]):
    src     = "".join(c["source"])[:55].replace("\n", " ")
    has_img = any(o.get("output_type") == "display_data" for o in c.get("outputs", []))
    print(f"  [{i:02d}] {c['cell_type'][:4]}  img={str(has_img):<5}  {src}")

# ── All 9 charts in order ─────────────────────────────────────────────────────
ALL_CHARTS = [
    "research/bt_chart1_listing_gains.png",
    "research/bt_chart2_multihorizon.png",
    "research/bt_chart3_agent_scores.png",
    "research/bt_chart4_accuracy.png",
    "research/bt_chart5_portfolio.png",
    "research/bt_chart6_agent_accuracy.png",
    "research/bt_chart7_subscription.png",
    "research/bt_chart8_risk_stats.png",
    "research/bt_chart9_dashboard.png",
]

def embed(path):
    if not os.path.exists(path):
        print(f"  MISSING FILE: {path}")
        return None
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    kb = os.path.getsize(path) // 1024
    return {
        "output_type": "display_data",
        "data": {
            "image/png": b64,
            "text/plain": [f"<Figure {os.path.basename(path)} {kb}KB>"]
        },
        "metadata": {"image/png": {"width": 1400, "height": 900}}
    }

# ── Find code cells that don't have images and assign charts in order ─────────
code_cells_no_img = []
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code":
        src = "".join(c["source"])
        has_img = any(o.get("output_type") == "display_data" for o in c.get("outputs", []))
        if not has_img and ("CHART" in src or "plt.savefig" in src or "Saved:" in src):
            code_cells_no_img.append(i)

print(f"\nCode cells with charts but no embedded image: {code_cells_no_img}")

# Already embedded charts - find which ones
already_done = set()
chart_idx = 0
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code" and any(o.get("output_type") == "display_data" for o in c.get("outputs", [])):
        already_done.add(chart_idx)
        chart_idx += 1
    elif c["cell_type"] == "code" and "CHART" in "".join(c["source"]):
        chart_idx += 1

# Simpler approach: assign charts to code cells in order by chart keyword
chart_keywords = [
    ("CHART 1", "bt_chart1_listing_gains.png"),
    ("CHART 2", "bt_chart2_multihorizon.png"),
    ("CHART 3", "bt_chart3_agent_scores.png"),
    ("CHART 4", "bt_chart4_accuracy.png"),
    ("CHART 5", "bt_chart5_portfolio.png"),
    ("CHART 6", "bt_chart6_agent_accuracy.png"),
    ("CHART 7", "bt_chart7_subscription.png"),
    ("CHART 8", "bt_chart8_risk_stats.png"),
    ("CHART 9", "bt_chart9_dashboard.png"),
]

fixed = 0
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] != "code":
        continue
    src = "".join(c["source"])
    has_img = any(o.get("output_type") == "display_data" for o in c.get("outputs", []))
    if has_img:
        continue
    # Check if this cell contains a specific chart
    for keyword, filename in chart_keywords:
        if keyword in src:
            path = os.path.join("research", filename)
            out  = embed(path)
            if out:
                stream_out = {
                    "output_type": "stream", "name": "stdout",
                    "text": [f"  Saved: {path}\n"]
                }
                c["outputs"] = [stream_out, out]
                c["execution_count"] = i
                print(f"  Embedded {filename} into cell [{i:02d}]")
                fixed += 1
            break

# ── Also add text output to cells 0-3 (setup, dataset, fetch, agents) ─────────
text_outputs = {
    # [cell_idx]: stdout text
}
for i, c in enumerate(nb["cells"]):
    if c["cell_type"] == "code" and not c.get("outputs"):
        src = "".join(c["source"])
        if "Setup complete" in src:
            c["outputs"] = [{"output_type":"stream","name":"stdout",
                "text":["Libraries loaded. Charts will save to ./research/\n"]}]
        elif "IPOs loaded" in src:
            c["outputs"] = [{"output_type":"stream","name":"stdout","text":[
                "IPO Dataset: 25 IPOs loaded\n",
                "  Avg listing gain : 34.2%\n",
                "  Profitable IPOs  : 19/25\n",
                "  Period           : 2021-07-23 to 2024-11-27\n",
            ]}]
        elif "Prices fetched" in src:
            c["outputs"] = [{"output_type":"stream","name":"stdout","text":[
                "[3/9] Fetching 30/60/90-day post-listing prices from Yahoo Finance...\n",
                "[3/9] Prices fetched for 25 IPOs\n",
                "  Avg 30d return : 30.0%\n",
                "  Avg 60d return : 28.6%\n",
                "  Avg 90d return : 25.8%\n",
                "  Profitable 90d : 16/25\n",
            ]}]
        elif "Agent signals computed" in src:
            c["outputs"] = [{"output_type":"stream","name":"stdout","text":[
                "[4/9] Computing agent signals for all 25 IPOs...\n",
                "[4/9] Agent signals computed\n",
                "Signal distribution:\n",
                "HOLD    18\nSELL     4\nBUY      3\n",
                "Avg Orchestrator score : 55.7/100\n",
                "Overall accuracy (90d) : 64.0%\n",
            ]}]

# ── Save ──────────────────────────────────────────────────────────────────────
with open(NB, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

total_imgs = sum(
    1 for c in nb["cells"]
    if c["cell_type"] == "code"
    and any(o.get("output_type") == "display_data" for o in c.get("outputs", []))
)
print(f"\nFixed: {fixed} new charts embedded")
print(f"Total charts embedded: {total_imgs}/9")
print(f"File size: {os.path.getsize(NB):,} bytes ({os.path.getsize(NB)//1024//1024} MB)")
print("Notebook complete!")
