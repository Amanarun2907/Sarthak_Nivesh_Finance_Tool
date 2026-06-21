"""
END-TO-END TESTING - IPO Intelligence System
Tests every functionality, feature, and data source
"""
import sys
sys.path.insert(0, 'sections/06_agentic_ai_hub')

import json
import time
from datetime import datetime

# Test results storage
test_results = {
    'total_tests': 0,
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'tests': []
}

def log_test(name, status, message, details=None):
    """Log test result"""
    test_results['total_tests'] += 1
    if status == 'PASS':
        test_results['passed'] += 1
        icon = '✅'
    elif status == 'FAIL':
        test_results['failed'] += 1
        icon = '❌'
    else:
        test_results['warnings'] += 1
        icon = '⚠️'
    
    test_results['tests'].append({
        'name': name,
        'status': status,
        'message': message,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })
    
    print(f"{icon} {name}: {message}")
    if details:
        print(f"   Details: {details}")

def print_section(title):
    """Print section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

# ============================================================================
# TEST 1: Import Tests
# ============================================================================
print_section("TEST 1: MODULE IMPORTS")

try:
    from ipo_real_data_fetcher import RealIPODataFetcher
    log_test("Import RealIPODataFetcher", "PASS", "Module imported successfully")
except Exception as e:
    log_test("Import RealIPODataFetcher", "FAIL", f"Import failed: {e}")
    sys.exit(1)

try:
    from ipo_multi_agent_framework import (
        PriceMovementAgent,
        MacroeconomicAgent,
        SentimentAgent,
        RiskAgent,
        IPOIntelligenceAgent,
        OrchestratorAgent,
        run_ipo_multi_agent_analysis
    )
    log_test("Import Multi-Agent Framework", "PASS", "All agents imported")
except Exception as e:
    log_test("Import Multi-Agent Framework", "FAIL", f"Import failed: {e}")
    sys.exit(1)

# ============================================================================
# TEST 2: Real Data Fetcher Tests
# ============================================================================
print_section("TEST 2: REAL DATA FETCHER")

fetcher = RealIPODataFetcher()

# Test 2.1: IPO Calendar Fetch
print("\n--- Test 2.1: IPO Calendar Fetch ---")
try:
    calendar = fetcher.fetch_ipo_calendar()
    if len(calendar) > 0:
        log_test("Fetch IPO Calendar", "PASS", f"Found {len(calendar)} IPOs", 
                 f"First IPO: {calendar[0]['name']}")
    else:
        log_test("Fetch IPO Calendar", "WARN", "No IPOs found (APIs may be down)")
except Exception as e:
    log_test("Fetch IPO Calendar", "FAIL", f"Error: {e}")

# Test 2.2: Subscription Data Fetch
print("\n--- Test 2.2: Subscription Data Fetch ---")
try:
    # Test with a recent IPO
    test_ipo = "Swiggy"
    sub_data = fetcher.fetch_ipo_subscription_data(test_ipo)
    if sub_data['total'] > 0:
        log_test("Fetch Subscription Data", "PASS", 
                 f"Total: {sub_data['total']:.1f}x, QIB: {sub_data['qib']:.1f}x",
                 f"Source: {sub_data['source']}")
    else:
        log_test("Fetch Subscription Data", "WARN", 
                 "No subscription data (IPO may not be open)")
except Exception as e:
    log_test("Fetch Subscription Data", "FAIL", f"Error: {e}")

# Test 2.3: Grey Market Premium Fetch
print("\n--- Test 2.3: Grey Market Premium Fetch ---")
try:
    test_ipo = "Swiggy"
    gmp = fetcher.fetch_grey_market_premium(test_ipo)
    if gmp != 0:
        log_test("Fetch GMP", "PASS", f"GMP: Rs.{gmp:.2f}")
    else:
        log_test("Fetch GMP", "WARN", "No GMP data available")
except Exception as e:
    log_test("Fetch GMP", "FAIL", f"Error: {e}")

# Test 2.4: Allotment Status Fetch
print("\n--- Test 2.4: Allotment Status Fetch ---")
try:
    test_ipo = "Hyundai Motor India"
    allotment = fetcher.fetch_ipo_allotment_status(test_ipo)
    log_test("Fetch Allotment Status", "PASS", 
             f"Finalized: {allotment['finalized']}")
except Exception as e:
    log_test("Fetch Allotment Status", "FAIL", f"Error: {e}")

# Test 2.5: Complete IPO Data Fetch (LISTED IPO)
print("\n--- Test 2.5: Complete Data Fetch - LISTED IPO ---")
try:
    test_ipo = "Hyundai Motor India"
    test_symbol = "HYUNDAI.NS"
    complete_data = fetcher.get_complete_ipo_data(test_ipo, test_symbol)
    
    if complete_data['data_quality'] >= 20:
        log_test("Complete Data - Listed IPO", "PASS", 
                 f"Data Quality: {complete_data['data_quality']}/100",
                 f"Current: Rs.{complete_data['current_price']:.2f}, Listing: Rs.{complete_data['listing_price']:.2f}")
    else:
        log_test("Complete Data - Listed IPO", "WARN", 
                 f"Low data quality: {complete_data['data_quality']}/100")
except Exception as e:
    log_test("Complete Data - Listed IPO", "FAIL", f"Error: {e}")

# Test 2.6: Smart IPO Search
print("\n--- Test 2.6: Smart IPO Search ---")
try:
    search_term = "Hyundai"
    match = fetcher.search_ipo_by_name(search_term)
    if match:
        log_test("Smart IPO Search", "PASS", 
                 f"Found: {match['name']}, Confidence: {match['match_confidence']}%")
    else:
        log_test("Smart IPO Search", "WARN", "No matches found")
except Exception as e:
    log_test("Smart IPO Search", "FAIL", f"Error: {e}")

# ============================================================================
# TEST 3: Individual Agent Tests
# ============================================================================
print_section("TEST 3: INDIVIDUAL AGENT TESTS")

from ipo_multi_agent_framework import GroqLLM

llm = GroqLLM()

# Test 3.1: Price Movement Agent
print("\n--- Test 3.1: Price Movement Agent ---")
try:
    price_agent = PriceMovementAgent(llm)
    result = price_agent.run("HYUNDAI.NS", "Hyundai Motor India")
    
    if result.score >= 0 and result.score <= 100:
        log_test("Price Movement Agent", "PASS", 
                 f"Score: {result.score:.1f}, Signal: {result.signal}",
                 f"Summary: {result.summary[:100]}")
    else:
        log_test("Price Movement Agent", "FAIL", "Invalid score range")
except Exception as e:
    log_test("Price Movement Agent", "FAIL", f"Error: {e}")

# Test 3.2: Macroeconomic Agent
print("\n--- Test 3.2: Macroeconomic Agent ---")
try:
    macro_agent = MacroeconomicAgent(llm)
    result = macro_agent.run()
    
    if result.score >= 0 and result.score <= 100:
        log_test("Macroeconomic Agent", "PASS", 
                 f"Score: {result.score:.1f}, Signal: {result.signal}",
                 f"Summary: {result.summary[:100]}")
    else:
        log_test("Macroeconomic Agent", "FAIL", "Invalid score range")
except Exception as e:
    log_test("Macroeconomic Agent", "FAIL", f"Error: {e}")

# Test 3.3: Sentiment Agent
print("\n--- Test 3.3: Sentiment Agent ---")
try:
    sentiment_agent = SentimentAgent(llm)
    result = sentiment_agent.run("Hyundai Motor India")
    
    if result.score >= 0 and result.score <= 100:
        articles_count = len(result.details.get('articles', []))
        log_test("Sentiment Agent", "PASS", 
                 f"Score: {result.score:.1f}, Articles: {articles_count}",
                 f"Summary: {result.summary[:100]}")
    else:
        log_test("Sentiment Agent", "FAIL", "Invalid score range")
except Exception as e:
    log_test("Sentiment Agent", "FAIL", f"Error: {e}")

# Test 3.4: Risk Agent
print("\n--- Test 3.4: Risk Agent ---")
try:
    risk_agent = RiskAgent(llm)
    result = risk_agent.run("HYUNDAI.NS", "Hyundai Motor India", 1960.0)
    
    if result.score >= 0 and result.score <= 100:
        sharpe = result.details['metrics'].get('sharpe_ratio', 0)
        volatility = result.details['metrics'].get('annual_vol', 0)
        log_test("Risk Agent", "PASS", 
                 f"Score: {result.score:.1f}, Sharpe: {sharpe:.2f}",
                 f"Volatility: {volatility:.1f}%")
    else:
        log_test("Risk Agent", "FAIL", "Invalid score range")
except Exception as e:
    log_test("Risk Agent", "FAIL", f"Error: {e}")

# Test 3.5: IPO Intelligence Agent (with Real Data)
print("\n--- Test 3.5: IPO Intelligence Agent ---")
try:
    ipo_intel_agent = IPOIntelligenceAgent(llm)
    result = ipo_intel_agent.run(
        "Hyundai Motor India",
        "HYUNDAI.NS",
        1960.0,  # issue price
        1913.0,  # current price
        1934.0,  # listing price
        17.0,    # sub_total
        36.5,    # sub_qib
        6.8,     # sub_retail
        "2024-10-22"
    )
    
    if result.score >= 0 and result.score <= 100:
        real_data_used = result.details.get('real_data_used', False)
        gmp = result.details.get('gmp', 0)
        log_test("IPO Intelligence Agent", "PASS", 
                 f"Score: {result.score:.1f}, Real Data: {real_data_used}",
                 f"GMP: Rs.{gmp:.2f}, Summary: {result.summary[:80]}")
    else:
        log_test("IPO Intelligence Agent", "FAIL", "Invalid score range")
except Exception as e:
    log_test("IPO Intelligence Agent", "FAIL", f"Error: {e}")

# ============================================================================
# TEST 4: Orchestrator Agent (Full Integration)
# ============================================================================
print_section("TEST 4: ORCHESTRATOR - FULL INTEGRATION TEST")

print("\n--- Test 4.1: Full Analysis - Listed IPO ---")
try:
    progress_log = []
    def progress_callback(step, message):
        progress_log.append(f"{step}%: {message}")
        print(f"  Progress: {step}% - {message}")
    
    result = run_ipo_multi_agent_analysis(
        ipo_name="Hyundai Motor India",
        symbol="HYUNDAI.NS",
        issue_price=1960.0,
        listing_price=1934.0,
        current_price=0.0,  # Auto-fetch
        sub_total=17.0,
        sub_qib=36.5,
        sub_retail=6.8,
        listing_date_str="2024-10-22",
        progress_callback=progress_callback
    )
    
    # Validate result
    checks = {
        'Final Decision': result.final_decision in ['INVEST', 'PARTIAL_INVEST', 'HOLD', 'EXIT', 'STRONG_EXIT'],
        'Overall Score': 0 <= result.overall_score <= 100,
        'Confidence': 0 <= result.confidence <= 100,
        'Exit Strategy': len(result.exit_strategy) > 0,
        'Target Price': result.target_price > 0,
        'Stop Loss': result.stop_loss > 0,
        'Investment Thesis': len(result.investment_thesis) > 0,
        'Agent Scores': len(result.agent_scores) == 5
    }
    
    all_passed = all(checks.values())
    
    if all_passed:
        log_test("Full Integration Test", "PASS", 
                 f"Decision: {result.final_decision}, Score: {result.overall_score:.1f}",
                 f"Confidence: {result.confidence:.1f}%, Target: Rs.{result.target_price:.2f}")
        
        print(f"\n   📊 DETAILED RESULTS:")
        print(f"      Final Decision: {result.final_decision}")
        print(f"      Overall Score: {result.overall_score:.1f}/100")
        print(f"      Confidence: {result.confidence:.1f}%")
        print(f"      Target Price: Rs.{result.target_price:.2f}")
        print(f"      Stop Loss: Rs.{result.stop_loss:.2f}")
        print(f"      Risk Level: {result.risk_level}")
        print(f"      Holding Period: {result.holding_period}")
        print(f"\n   📋 EXIT STRATEGY:")
        print(f"      {result.exit_strategy}")
        print(f"\n   🎯 AGENT SCORES:")
        for agent, data in result.agent_scores.items():
            print(f"      {agent}: {data['score']:.1f} ({data['signal']})")
    else:
        failed_checks = [k for k, v in checks.items() if not v]
        log_test("Full Integration Test", "FAIL", 
                 f"Failed checks: {', '.join(failed_checks)}")
        
except Exception as e:
    log_test("Full Integration Test", "FAIL", f"Error: {e}")
    import traceback
    print(f"\n   Traceback:\n{traceback.format_exc()}")

# ============================================================================
# TEST 5: API Endpoint Testing
# ============================================================================
print_section("TEST 5: API ENDPOINT TESTING")

import requests

print("\n--- Test 5.1: Backend API Status ---")
try:
    response = requests.get("http://localhost:8000/api/ipo_multiagent/status", timeout=5)
    if response.status_code == 200:
        data = response.json()
        log_test("API Status Endpoint", "PASS", 
                 f"Status: {data.get('status', 'unknown')}",
                 f"Agents: {data.get('agents', 0)}, Model: {data.get('model', 'unknown')}")
    else:
        log_test("API Status Endpoint", "FAIL", f"Status code: {response.status_code}")
except Exception as e:
    log_test("API Status Endpoint", "WARN", f"Backend not running: {e}")

print("\n--- Test 5.2: Backend API Analysis ---")
try:
    payload = {
        "ipo_name": "Hyundai Motor India",
        "symbol": "HYUNDAI.NS",
        "issue_price": 1960,
        "listing_price": 1934,
        "current_price": 0,
        "sub_total": 17,
        "sub_qib": 36.5,
        "sub_retail": 6.8,
        "listing_date_str": "2024-10-22"
    }
    
    response = requests.post(
        "http://localhost:8000/api/ipo_multiagent/analyze",
        json=payload,
        timeout=120
    )
    
    if response.status_code == 200:
        data = response.json()
        log_test("API Analysis Endpoint", "PASS", 
                 f"Decision: {data.get('final_decision', 'N/A')}",
                 f"Score: {data.get('overall_score', 0):.1f}, Confidence: {data.get('confidence', 0):.1f}%")
    else:
        log_test("API Analysis Endpoint", "FAIL", 
                 f"Status code: {response.status_code}")
except Exception as e:
    log_test("API Analysis Endpoint", "WARN", f"Backend not running or timeout: {e}")

# ============================================================================
# TEST 6: Edge Cases and Error Handling
# ============================================================================
print_section("TEST 6: EDGE CASES & ERROR HANDLING")

print("\n--- Test 6.1: Invalid Symbol ---")
try:
    result = run_ipo_multi_agent_analysis(
        ipo_name="NonExistent IPO",
        symbol="INVALID.NS",
        issue_price=100,
        listing_price=100,
        current_price=0,
        sub_total=0,
        sub_qib=0,
        sub_retail=0,
        listing_date_str=""
    )
    log_test("Invalid Symbol Handling", "PASS", 
             "System handled invalid symbol gracefully",
             f"Decision: {result.final_decision}")
except Exception as e:
    log_test("Invalid Symbol Handling", "FAIL", f"System crashed: {e}")

print("\n--- Test 6.2: Zero Subscription Data ---")
try:
    result = run_ipo_multi_agent_analysis(
        ipo_name="Test IPO",
        symbol="HYUNDAI.NS",
        issue_price=100,
        listing_price=100,
        current_price=100,
        sub_total=0,
        sub_qib=0,
        sub_retail=0,
        listing_date_str=""
    )
    log_test("Zero Subscription Handling", "PASS", 
             "System handled zero subscription data",
             f"Decision: {result.final_decision}")
except Exception as e:
    log_test("Zero Subscription Handling", "FAIL", f"System crashed: {e}")

print("\n--- Test 6.3: Upcoming IPO (No Listing Data) ---")
try:
    result = run_ipo_multi_agent_analysis(
        ipo_name="Upcoming IPO Test",
        symbol="UPCOMING.NS",
        issue_price=500,
        listing_price=0,  # Not listed yet
        current_price=0,
        sub_total=25,
        sub_qib=40,
        sub_retail=15,
        listing_date_str=""
    )
    log_test("Upcoming IPO Handling", "PASS", 
             "System handled upcoming IPO scenario",
             f"Decision: {result.final_decision}")
except Exception as e:
    log_test("Upcoming IPO Handling", "FAIL", f"System crashed: {e}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print_section("TEST SUMMARY")

print(f"Total Tests: {test_results['total_tests']}")
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
print(f"⚠️  Warnings: {test_results['warnings']}")
print(f"\nSuccess Rate: {(test_results['passed']/test_results['total_tests']*100):.1f}%")

# Save results to file
with open('ipo_intelligence_test_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)

print(f"\n📄 Detailed results saved to: ipo_intelligence_test_results.json")

# Exit code based on results
if test_results['failed'] > 0:
    print("\n⚠️  SOME TESTS FAILED - Review results above")
    sys.exit(1)
else:
    print("\n✅ ALL CRITICAL TESTS PASSED")
    sys.exit(0)
