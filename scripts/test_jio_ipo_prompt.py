"""
Jio IPO Prompt Comprehensive Test Script
Tests all 4 sections implemented via CrewAI and ADK:
1. IPO Multi-Agent Framework
2. Agentic AI Hub
3. Enhanced IPO Analysis
4. Agent Control Tower
"""
import requests
import json
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"

JIO_PROMPT = (
    "How does Jio Platforms' decision to use its entire ₹30,188 crore fresh issue strictly to prepay bank borrowings "
    "at Reliance Jio Infocomm affect the true equity value for public shareholders, given that over ₹1.04 lakh crore "
    "in deferred spectrum payment obligations remain off the reported net debt and excluded from the use of proceeds, "
    "while major pre-IPO cap-table investors like Meta and Google retain their stakes without providing an exit?"
)

def test_all():
    print("=" * 80)
    print("🚀 TESTING SARTHAK NIVESH CREWAI + ADK FRAMEWORKS WITH JIO IPO PROMPT")
    print("=" * 80)

    # 1. IPO Multi-Agent Framework
    print("\n[1/4] Testing IPO Multi-Agent (CrewAI + ADK 6-Agent Framework)...")
    payload_ipo = {
        "ipo_name": f"Jio Platforms - {JIO_PROMPT[:150]}...",
        "symbol": "RELIANCE.NS",
        "issue_price": 750.0,
        "listing_price": 840.0,
        "current_price": 840.0,
        "sub_total": 42.5,
        "sub_qib": 86.0,
        "sub_retail": 14.2,
        "listing_date_str": "2025-06-20"
    }
    t0 = time.time()
    try:
        r1 = requests.post(f"{BASE_URL}/api/ipo_multiagent/analyze", json=payload_ipo, timeout=240)
        dur1 = round(time.time() - t0, 2)
        print(f"Status: {r1.status_code} in {dur1}s")
        if r1.status_code == 200:
            res1 = r1.json()
            print(f"  • Final Decision: {res1.get('final_decision')}")
            print(f"  • Overall Score:  {res1.get('overall_score')}/100")
            print(f"  • Confidence:     {res1.get('confidence')}%")
            print(f"  • Risk Level:     {res1.get('risk_level')}")
            print(f"  • Target Price:   ₹{res1.get('target_price')}")
            print(f"  • Stop Loss:      ₹{res1.get('stop_loss')}")
            print(f"  • Investment Thesis: {res1.get('investment_thesis')[:300]}...")
            print("  • Agent Scores Breakdown:")
            for a_name, a_info in res1.get('agent_scores', {}).items():
                if isinstance(a_info, dict):
                    print(f"    - {a_name} ({a_info.get('framework', 'AI')}): {a_info.get('score')}/100 [{a_info.get('signal')}]")
        else:
            print(f"Error {r1.status_code}: {r1.text[:200]}")
    except Exception as e:
        print(f"Failed: {e}")

    # 2. Agentic AI Hub
    print("\n[2/4] Testing Agentic AI Hub (CrewAI Stock/Market/SmartMoney/News + ADK Risk/Analytics)...")
    payload_hub = {
        "query": JIO_PROMPT,
        "agents": ["stock", "market", "smartmoney", "news", "risk", "analytics"]
    }
    t0 = time.time()
    try:
        r2 = requests.post(f"{BASE_URL}/api/agentic/run", json=payload_hub, timeout=240)
        dur2 = round(time.time() - t0, 2)
        print(f"Status: {r2.status_code} in {dur2}s")
        if r2.status_code == 200:
            res2 = r2.json()
            print(f"  • Agents Run: {res2.get('agents_run')}")
            print(f"  • Framework:  {res2.get('framework')}")
            print(f"  • Master Report Preview:\n{res2.get('master_report')[:400]}...\n")
        else:
            print(f"Error {r2.status_code}: {r2.text[:200]}")
    except Exception as e:
        print(f"Failed: {e}")

    # 3. Enhanced IPO Analysis
    print("\n[3/4] Testing Enhanced IPO Intelligence (Dynamic Exit Engine + Explainability + Control Tower)...")
    payload_enh = {
        "ipo_name": "Jio Platforms Limited (RJIL)",
        "symbol": "RELIANCE.NS",
        "entry_price": 750.0,
        "position_size": 200,
        "risk_profile": "moderate"
    }
    t0 = time.time()
    try:
        r3 = requests.post(f"{BASE_URL}/api/ipo_enhanced/analyze/comprehensive", json=payload_enh, timeout=240)
        dur3 = round(time.time() - t0, 2)
        print(f"Status: {r3.status_code} in {dur3}s")
        if r3.status_code == 200:
            res3 = r3.json()
            print(f"  • Task ID: {res3.get('task_id')}")
            r_inner = res3.get('result', {})
            print(f"  • Overall Multi-Agent Score: {r_inner.get('overall_score')}")
            print(f"  • Exit Action: {r_inner.get('exit_strategy', {}).get('recommended_action')}")
            print(f"  • Exit Price Target: ₹{r_inner.get('exit_strategy', {}).get('target_price')}")
        else:
            print(f"Error {r3.status_code}: {r3.text[:200]}")
    except Exception as e:
        print(f"Failed: {e}")

    # 4. Agent Control Tower
    print("\n[4/4] Testing Agent Control Tower (Real-time telemetry, agents, tasks)...")
    try:
        r4 = requests.get(f"{BASE_URL}/api/control_tower/dashboard")
        print(f"Status: {r4.status_code}")
        if r4.status_code == 200:
            dash = r4.json()
            print(f"  • System Status:        {dash.get('system_status')}")
            print(f"  • Active Tasks:         {dash.get('active_tasks_count')}")
            print(f"  • Total Completed Tasks:{dash.get('completed_tasks_count')}")
            print(f"  • Total Agent Calls:    {dash.get('total_agent_calls')}")
            print(f"  • Total Cost USD:       ${dash.get('total_cost_usd')}")
            print(f"  • Monitored Agents:     {len(dash.get('agents', {}))} registered agents")
            for ag_name, ag_data in list(dash.get('agents', {}).items())[:6]:
                print(f"    - {ag_name}: status={ag_data.get('status')}, calls={ag_data.get('api_calls_made')}, health={ag_data.get('health_score')}%")
    except Exception as e:
        print(f"Failed: {e}")

    print("\n" + "=" * 80)
    print("✅ COMPREHENSIVE JIO IPO MULTI-AGENT TESTING COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    test_all()
