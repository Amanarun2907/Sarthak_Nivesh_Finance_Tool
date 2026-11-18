import sys, time
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "src" / "core"))
sys.path.insert(0, str(root / "src" / "sections" / "06_agentic_ai_hub"))
from ipo_multi_agent_framework import run_ipo_multi_agent_analysis

def cb(step, msg):
    print(f"[{time.strftime('%H:%M:%S')}] Step {step}: {msg}", flush=True)

print("Starting analysis...", flush=True)
t0 = time.time()
res = run_ipo_multi_agent_analysis(
    ipo_name="Jio Platforms Limited",
    symbol="JPL.NS",
    issue_price=1119.0,
    listing_price=1366.0,
    progress_callback=cb
)
print(f"Done in {time.time()-t0:.2f}s! Decision: {res.final_decision}, Score: {res.overall_score}", flush=True)
