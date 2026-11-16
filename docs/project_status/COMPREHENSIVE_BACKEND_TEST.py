"""
COMPREHENSIVE BACKEND API TESTING
Tests all 12 API routers with real data
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"
results = {"passed": 0, "failed": 0, "tests": []}

def test_endpoint(name, url, method="GET", data=None):
    """Test an API endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        else:
            response = requests.post(url, json=data, timeout=10)
        
        status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
        results["passed" if response.status_code == 200 else "failed"] += 1
        
        test_info = {
            "name": name,
            "status": status,
            "status_code": response.status_code,
            "response_size": len(response.text) if response.text else 0
        }
        results["tests"].append(test_info)
        
        print(f"{status} | {name}")
        if response.status_code == 200 and len(response.text) < 500:
            print(f"  Response: {response.json()}")
        
        return response
    except Exception as e:
        print(f"❌ ERROR | {name}: {str(e)}")
        results["failed"] += 1
        results["tests"].append({"name": name, "status": "❌ ERROR", "error": str(e)})
        return None

print("=" * 80)
print("🧪 COMPREHENSIVE BACKEND API TESTING")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Base URL: {BASE_URL}\n")

# ─── 1. ROOT & HEALTH CHECKS ────────────────────────────────────────────────
print("\n📍 1. BASIC ENDPOINTS")
print("-" * 80)
test_endpoint("Root Endpoint", "http://localhost:8000/")
test_endpoint("Health Check", "http://localhost:8000/health")

# ─── 2. DASHBOARD ───────────────────────────────────────────────────────────
print("\n📊 2. DASHBOARD ENDPOINTS")
print("-" * 80)
test_endpoint("Market Overview", f"{BASE_URL}/dashboard/overview")
test_endpoint("Top Gainers", f"{BASE_URL}/dashboard/gainers")
test_endpoint("Top Losers", f"{BASE_URL}/dashboard/losers")
test_endpoint("Market Breadth", f"{BASE_URL}/dashboard/breadth")

# ─── 3. STOCKS ──────────────────────────────────────────────────────────────
print("\n📈 3. STOCK INTELLIGENCE ENDPOINTS")
print("-" * 80)
test_endpoint("Stock List", f"{BASE_URL}/stocks/list")
test_endpoint("Stock Price - RELIANCE", f"{BASE_URL}/stocks/RELIANCE.NS/price")
test_endpoint("Stock OHLCV - TCS", f"{BASE_URL}/stocks/TCS.NS/ohlcv")
test_endpoint("Stock Technicals - HDFCBANK", f"{BASE_URL}/stocks/HDFCBANK.NS/technicals")
test_endpoint("Stock Fundamentals - INFY", f"{BASE_URL}/stocks/INFY.NS/fundamentals")
test_endpoint("Stock Signal - SBIN", f"{BASE_URL}/stocks/SBIN.NS/signal")

# ─── 4. MUTUAL FUNDS ────────────────────────────────────────────────────────
print("\n💰 4. MUTUAL FUNDS ENDPOINTS")
print("-" * 80)
test_endpoint("MF Categories", f"{BASE_URL}/mf/categories")
test_endpoint("MF List (Equity)", f"{BASE_URL}/mf/list?category=Equity")
test_endpoint("MF Details", f"{BASE_URL}/mf/119551/details")  # Sample scheme code
test_endpoint("MF NAV History", f"{BASE_URL}/mf/119551/nav")

# ─── 5. SIP GOALS ───────────────────────────────────────────────────────────
print("\n🎯 5. SIP GOAL PLANNER ENDPOINTS")
print("-" * 80)
test_endpoint("SIP Calculator", f"{BASE_URL}/sip/calculate", "POST", {
    "monthly_amount": 5000,
    "years": 10,
    "expected_return": 12
})
test_endpoint("Goal Calculator", f"{BASE_URL}/sip/goal_calculator", "POST", {
    "target_amount": 1000000,
    "years": 10,
    "inflation_rate": 6
})
test_endpoint("SIP Recommendations", f"{BASE_URL}/sip/recommendations?risk_profile=moderate")

# ─── 6. IPO ─────────────────────────────────────────────────────────────────
print("\n🚀 6. IPO INTELLIGENCE ENDPOINTS")
print("-" * 80)
test_endpoint("Live IPOs", f"{BASE_URL}/ipo/live")
test_endpoint("IPO Details", f"{BASE_URL}/ipo/latest/details")
test_endpoint("IPO Analysis", f"{BASE_URL}/ipo/latest/analysis")
test_endpoint("IPO Exit Strategy", f"{BASE_URL}/ipo/latest/exit_strategy")

# ─── 7. SMART MONEY ─────────────────────────────────────────────────────────
print("\n💸 7. SMART MONEY TRACKER ENDPOINTS")
print("-" * 80)
test_endpoint("FII/DII Data", f"{BASE_URL}/smartmoney/fii_dii")
test_endpoint("Bulk Deals", f"{BASE_URL}/smartmoney/bulk_deals")
test_endpoint("Block Deals", f"{BASE_URL}/smartmoney/block_deals")
test_endpoint("Sector Flow", f"{BASE_URL}/smartmoney/sector_flow")

# ─── 8. PORTFOLIO ───────────────────────────────────────────────────────────
print("\n📊 8. PORTFOLIO ENDPOINTS")
print("-" * 80)
test_endpoint("Portfolio Summary", f"{BASE_URL}/portfolio/summary")
test_endpoint("Portfolio Risk", f"{BASE_URL}/portfolio/risk")
test_endpoint("Add Holding", f"{BASE_URL}/portfolio/holdings", "POST", {
    "symbol": "RELIANCE.NS",
    "quantity": 10,
    "buy_price": 2500,
    "buy_date": "2024-01-01"
})

# ─── 9. NEWS & SENTIMENT ────────────────────────────────────────────────────
print("\n📰 9. NEWS & SENTIMENT ENDPOINTS")
print("-" * 80)
test_endpoint("Latest News", f"{BASE_URL}/news/latest")
test_endpoint("News Sentiment", f"{BASE_URL}/news/sentiment")
test_endpoint("Market Mood", f"{BASE_URL}/news/market_mood")
test_endpoint("Sector Sentiment", f"{BASE_URL}/news/sector_sentiment")

# ─── 10. AI ASSISTANT ───────────────────────────────────────────────────────
print("\n🤖 10. AI ASSISTANT ENDPOINTS")
print("-" * 80)
test_endpoint("AI Chat", f"{BASE_URL}/ai/chat", "POST", {
    "query": "What is the current market condition?"
})
test_endpoint("Quick Actions", f"{BASE_URL}/ai/quick_actions")

# ─── 11. ANALYTICS ──────────────────────────────────────────────────────────
print("\n📊 11. ADVANCED ANALYTICS ENDPOINTS")
print("-" * 80)
test_endpoint("Sector Heatmap", f"{BASE_URL}/analytics/sector_heatmap")
test_endpoint("Correlation Matrix", f"{BASE_URL}/analytics/correlation")
test_endpoint("Volume Analysis", f"{BASE_URL}/analytics/volume_intelligence")
test_endpoint("Market Breadth Gauge", f"{BASE_URL}/analytics/breadth_gauge")

# ─── 12. AGENTIC AI ─────────────────────────────────────────────────────────
print("\n🧠 12. AGENTIC AI HUB ENDPOINTS")
print("-" * 80)
test_endpoint("Agent Report", f"{BASE_URL}/agentic/report", "POST", {
    "query": "Analyze current market and give investment recommendations"
})
test_endpoint("Agent Status", f"{BASE_URL}/agentic/status")

# ─── 13. IPO MULTI-AGENT ────────────────────────────────────────────────────
print("\n🎯 13. IPO MULTI-AGENT ENDPOINTS")
print("-" * 80)
test_endpoint("IPO Multi-Agent Analysis", f"{BASE_URL}/ipo_multiagent/analyze")

# ─── RESULTS SUMMARY ────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("📊 TEST RESULTS SUMMARY")
print("=" * 80)
print(f"✅ Passed: {results['passed']}")
print(f"❌ Failed: {results['failed']}")
print(f"📈 Success Rate: {results['passed']/(results['passed']+results['failed'])*100:.1f}%")
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Save detailed results
with open("backend_test_results.json", "w") as f:
    json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: backend_test_results.json")

print("\n" + "=" * 80)
