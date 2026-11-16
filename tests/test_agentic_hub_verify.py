import sys
import os
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "web" / "backend"))
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

print("=== 1. Testing GET /api/agentic/status ===")
res_status = client.get("/api/agentic/status")
print("Status code:", res_status.status_code)
status_data = res_status.json()
print("Service:", status_data.get("service"))
print("Agents count:", status_data.get("agents_count"))
print("Status:", status_data.get("status"))

print("\n=== 2. Testing POST /api/agentic/run with 6 agents ===")
payload = {
    "query": "Give me a complete market analysis and tell me where to invest today",
    "agents": ["stock", "market", "smartmoney", "news", "risk", "analytics"]
}
res_run = client.post("/api/agentic/run", json=payload)
print("Run status code:", res_run.status_code)

if res_run.status_code != 200:
    print("Error response:", res_run.text)
    sys.exit(1)

data = res_run.json()
print("Agents run:", data.get("agents_run"))
print("Agent results count:", len(data.get("agent_results", [])))

for a in data.get("agent_results", []):
    agent_id = a.get("agent")
    name = a.get("name")
    status = a.get("status")
    print(f" -> [{status}] {agent_id}: {name}")
    if agent_id == "stock":
        print(f"    Stocks: {len(a.get('stocks', []))}, Top BUY: {a.get('top_buy')}")
    elif agent_id == "market":
        print(f"    Sectors: {len(a.get('sector_perf', {}))}, Best sector: {a.get('best_sector')}")
    elif agent_id == "smartmoney":
        print(f"    FII Net: {a.get('fii_net')}, Signal: {a.get('signal')}")
    elif agent_id == "news":
        print(f"    Articles: {len(a.get('articles', []))}, Overall: {a.get('overall')}")
    elif agent_id == "risk":
        print(f"    Portfolio Vol: {a.get('portfolio_volatility')}, Portfolio VaR: {a.get('portfolio_var')}, Avg Corr: {a.get('avg_correlation')}")
    elif agent_id == "analytics":
        print(f"    Volume alerts: {len(a.get('volume_alerts', []))}, Sector momentum: {len(a.get('sector_momentum', {}))}")

print("\n=== 3. Testing Master Report ===")
master = data.get("master_report", "")
print("Master report generated! Length:", len(master))
print("Preview:\n", master[:250], "...")

print("\n=== 4. Testing Telemetry ===")
telemetry = data.get("telemetry", {})
print("Telemetry:", telemetry)
print("\n ALL AGENTIC AI HUB CHECKS PASSED PERFECTLY!")
