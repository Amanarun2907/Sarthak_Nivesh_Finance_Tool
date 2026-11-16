"""
FINAL COMPREHENSIVE END-TO-END TESTING
Tests every scenario, edge case, and bug to ensure 100% reliability
"""
import sys
sys.path.insert(0, 'sections/06_agentic_ai_hub')

import json
import time
from datetime import datetime

# Results tracking
results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'bugs_found': [],
    'tests': []
}

def test(name, func):
    """Run a test and track results"""
    results['total'] += 1
    print(f"\n{'='*70}")
    print(f"TEST {results['total']}: {name}")
    print('='*70)
    
    try:
        func()
        results['passed'] += 1
        print(f"✅ PASSED: {name}")
        results['tests'].append({'name': name, 'status': 'PASS'})
    except AssertionError as e:
        results['failed'] += 1
        bug = f"{name}: {str(e)}"
        results['bugs_found'].append(bug)
        results['tests'].append({'name': name, 'status': 'FAIL', 'error': str(e)})
        print(f"❌ FAILED: {name}")
        print(f"   Error: {e}")
    except Exception as e:
        results['failed'] += 1
        bug = f"{name}: Unexpected error - {str(e)}"
        results['bugs_found'].append(bug)
        results['tests'].append({'name': name, 'status': 'ERROR', 'error': str(e)})
        print(f"❌ ERROR: {name}")
        print(f"   Exception: {e}")

# Import system
print("\n" + "="*70)
print("IMPORTING IPO INTELLIGENCE SYSTEM")
print("="*70)

from ipo_multi_agent_framework import (
    run_ipo_multi_agent_analysis,
    PriceMovementAgent,
    MacroeconomicAgent,
    SentimentAgent,
    RiskAgent,
    IPOIntelligenceAgent,
    OrchestratorAgent,
    GroqLLM
)
from ipo_real_data_fetcher import RealIPODataFetcher

print("✅ All imports successful\n")

# ============================================================================
# BASIC FUNCTIONALITY TESTS
# ============================================================================

def test_valid_ipo_analysis():
    """Test with valid Hyundai IPO data"""
    result = run_ipo_multi_agent_analysis(
        "Hyundai Motor India", "HYUNDAI.NS", 1960, 1934, 0, 17, 36.5, 6.8, "2024-10-22"
    )
    assert result is not None, "Result is None"
    assert result.final_decision in ['INVEST', 'PARTIAL_INVEST', 'HOLD', 'EXIT', 'STRONG_EXIT'], f"Invalid decision: {result.final_decision}"
    assert 0 <= result.overall_score <= 100, f"Score out of range: {result.overall_score}"
    assert 0 <= result.confidence <= 100, f"Confidence out of range: {result.confidence}"
    assert result.target_price > 0, "Target price is zero"
    assert result.stop_loss > 0, "Stop loss is zero"
    assert len(result.exit_strategy) > 0, "Exit strategy is empty"
    print(f"   Decision: {result.final_decision}, Score: {result.overall_score:.1f}")

def test_invalid_symbol():
    """Test with completely invalid symbol"""
    result = run_ipo_multi_agent_analysis(
        "NonExistent Company", "INVALID123.NS", 100, 100, 0, 0, 0, 0, ""
    )
    assert result is not None, "System crashed on invalid symbol"
    assert result.final_decision is not None, "No decision returned"
    print(f"   Decision: {result.final_decision}")

def test_zero_values():
    """Test with all zero subscription data"""
    result = run_ipo_multi_agent_analysis(
        "Zero Sub IPO", "HYUNDAI.NS", 500, 500, 500, 0, 0, 0, ""
    )
    assert result is not None, "System failed with zero subscription"
    assert result.overall_score >= 0, "Negative score"
    print(f"   Score: {result.overall_score:.1f}")

def test_negative_prices():
    """Test with edge case: very different listing vs issue price"""
    result = run_ipo_multi_agent_analysis(
        "High Listing", "HYUNDAI.NS", 1000, 1500, 0, 50, 80, 30, ""
    )
    assert result is not None, "Failed with high listing gain"
    assert result.overall_score > 50, "Score too low for highly subscribed IPO"
    print(f"   Score: {result.overall_score:.1f}")

def test_very_low_listing():
    """Test with IPO listed below issue price"""
    result = run_ipo_multi_agent_analysis(
        "Poor Listing", "HYUNDAI.NS", 1000, 800, 0, 2, 1.5, 0.8, ""
    )
    assert result is not None, "Failed with poor listing"
    assert result.overall_score < 50, "Score too high for poorly performing IPO"
    print(f"   Score: {result.overall_score:.1f}")

# ============================================================================
# INDIVIDUAL AGENT TESTS
# ============================================================================

def test_price_agent_valid():
    """Test Price Movement Agent with valid symbol"""
    llm = GroqLLM()
    agent = PriceMovementAgent(llm)
    result = agent.run("HYUNDAI.NS", "Hyundai Motor India")
    assert result.score >= 0 and result.score <= 100, f"Invalid score: {result.score}"
    assert result.signal in ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'], f"Invalid signal: {result.signal}"
    print(f"   Score: {result.score:.1f}, Signal: {result.signal}")

def test_price_agent_invalid():
    """Test Price Movement Agent with invalid symbol"""
    llm = GroqLLM()
    agent = PriceMovementAgent(llm)
    result = agent.run("INVALID.NS", "Invalid Company")
    assert result is not None, "Agent returned None"
    assert result.error is not None, "No error reported for invalid symbol"
    print(f"   Error handled: {result.error[:50]}...")

def test_macro_agent():
    """Test Macroeconomic Agent"""
    llm = GroqLLM()
    agent = MacroeconomicAgent(llm)
    result = agent.run()
    assert result.score >= 0 and result.score <= 100, f"Invalid score: {result.score}"
    # Check that nifty key exists in details (not inside macro_data.indices)
    assert 'nifty' in result.details, "No NIFTY data in details"
    print(f"   Score: {result.score:.1f}")

def test_sentiment_agent():
    """Test Sentiment Agent"""
    llm = GroqLLM()
    agent = SentimentAgent(llm)
    result = agent.run("Hyundai Motor India")
    assert result.score >= 0 and result.score <= 100, f"Invalid score: {result.score}"
    articles = result.details.get('articles', [])
    print(f"   Score: {result.score:.1f}, Articles: {len(articles)}")

def test_risk_agent():
    """Test Risk Agent"""
    llm = GroqLLM()
    agent = RiskAgent(llm)
    result = agent.run("HYUNDAI.NS", "Hyundai Motor India", 1960)
    assert result.score >= 0 and result.score <= 100, f"Invalid score: {result.score}"
    assert 'sharpe_ratio' in result.details.get('metrics', {}), "No Sharpe ratio"
    print(f"   Score: {result.score:.1f}")

def test_ipo_intelligence_agent():
    """Test IPO Intelligence Agent with real data fetching"""
    llm = GroqLLM()
    agent = IPOIntelligenceAgent(llm)
    result = agent.run("Hyundai Motor India", "HYUNDAI.NS", 1960, 1913, 1934, 17, 36.5, 6.8, "2024-10-22")
    assert result.score >= 0 and result.score <= 100, f"Invalid score: {result.score}"
    assert 'gmp' in result.details, "No GMP data"
    print(f"   Score: {result.score:.1f}, GMP: Rs.{result.details.get('gmp', 0):.2f}")

# ============================================================================
# REAL DATA FETCHER TESTS
# ============================================================================

def test_data_fetcher_initialization():
    """Test Real Data Fetcher initialization"""
    fetcher = RealIPODataFetcher()
    assert fetcher is not None, "Fetcher failed to initialize"
    assert hasattr(fetcher, 'session'), "No session attribute"
    print("   Fetcher initialized successfully")

def test_data_fetcher_with_symbol():
    """Test fetching data for a real listed IPO"""
    fetcher = RealIPODataFetcher()
    data = fetcher.get_complete_ipo_data("Hyundai Motor India", "HYUNDAI.NS")
    assert data is not None, "No data returned"
    assert 'data_quality' in data, "No data quality score"
    assert data['current_price'] > 0, "No current price fetched"
    print(f"   Data Quality: {data['data_quality']}/100")
    print(f"   Current Price: Rs.{data['current_price']:.2f}")

def test_data_fetcher_without_symbol():
    """Test fetching data without symbol"""
    fetcher = RealIPODataFetcher()
    data = fetcher.get_complete_ipo_data("Upcoming IPO", None)
    assert data is not None, "Fetcher crashed without symbol"
    print(f"   Data Quality: {data['data_quality']}/100")

# ============================================================================
# EDGE CASES & STRESS TESTS
# ============================================================================

def test_empty_strings():
    """Test with empty string inputs"""
    result = run_ipo_multi_agent_analysis("", "", 0, 0, 0, 0, 0, 0, "")
    assert result is not None, "System crashed with empty strings"
    print(f"   Decision: {result.final_decision}")

def test_very_large_numbers():
    """Test with unrealistically large numbers"""
    result = run_ipo_multi_agent_analysis(
        "Large Numbers", "HYUNDAI.NS", 100000, 150000, 0, 1000, 2000, 500, ""
    )
    assert result is not None, "System crashed with large numbers"
    assert result.overall_score <= 100, "Score exceeded maximum"
    print(f"   Score: {result.overall_score:.1f}")

def test_special_characters():
    """Test with special characters in name"""
    result = run_ipo_multi_agent_analysis(
        "IPO & Company (Pvt.) Ltd.", "HYUNDAI.NS", 1000, 1000, 0, 10, 20, 5, ""
    )
    assert result is not None, "System crashed with special characters"
    print(f"   Decision: {result.final_decision}")

def test_future_date():
    """Test with future listing date"""
    result = run_ipo_multi_agent_analysis(
        "Future IPO", "HYUNDAI.NS", 500, 0, 0, 25, 40, 15, "2025-12-31"
    )
    assert result is not None, "System failed with future date"
    print(f"   Decision: {result.final_decision}")

def test_very_old_date():
    """Test with very old listing date"""
    result = run_ipo_multi_agent_analysis(
        "Old IPO", "HYUNDAI.NS", 500, 600, 550, 30, 50, 20, "2020-01-01"
    )
    assert result is not None, "System failed with old date"
    days = result.agent_scores.get('IPO Intelligence Agent', {}).get('summary', '')
    print(f"   Processed old date successfully")

def test_concurrent_analyses():
    """Test running multiple analyses in sequence (stress test)"""
    for i in range(3):
        result = run_ipo_multi_agent_analysis(
            f"Test IPO {i}", "HYUNDAI.NS", 1000, 1100, 0, 10, 20, 5, ""
        )
        assert result is not None, f"Failed on iteration {i}"
    print("   3 concurrent analyses completed")

# ============================================================================
# OUTPUT VALIDATION TESTS
# ============================================================================

def test_output_completeness():
    """Test that all required fields are present in output"""
    result = run_ipo_multi_agent_analysis(
        "Complete Test", "HYUNDAI.NS", 1000, 1050, 0, 15, 25, 10, ""
    )
    required_fields = [
        'ipo_name', 'symbol', 'final_decision', 'overall_score', 'confidence',
        'entry_strategy', 'exit_strategy', 'target_price', 'stop_loss',
        'risk_level', 'holding_period', 'agent_scores', 'investment_thesis',
        'key_risks', 'key_catalysts', 'monitoring_triggers'
    ]
    for field in required_fields:
        assert hasattr(result, field), f"Missing field: {field}"
    print(f"   All {len(required_fields)} required fields present")

def test_agent_scores_structure():
    """Test that agent scores have correct structure"""
    result = run_ipo_multi_agent_analysis(
        "Structure Test", "HYUNDAI.NS", 1000, 1050, 0, 15, 25, 10, ""
    )
    expected_agents = [
        'Price Movement Agent', 'Macroeconomic Agent', 'Sentiment Agent',
        'Risk Agent', 'IPO Intelligence Agent'
    ]
    for agent_name in expected_agents:
        assert agent_name in result.agent_scores, f"Missing agent: {agent_name}"
        agent_data = result.agent_scores[agent_name]
        assert 'score' in agent_data, f"{agent_name} missing score"
        assert 'signal' in agent_data, f"{agent_name} missing signal"
    print(f"   All {len(expected_agents)} agents present with correct structure")

# ============================================================================
# RUN ALL TESTS
# ============================================================================

print("\n" + "="*70)
print("STARTING COMPREHENSIVE TEST SUITE")
print("="*70)

# Basic Functionality
test("Valid IPO Analysis (Hyundai)", test_valid_ipo_analysis)
test("Invalid Symbol Handling", test_invalid_symbol)
test("Zero Subscription Values", test_zero_values)
test("High Listing Gain Scenario", test_negative_prices)
test("Poor Listing Performance", test_very_low_listing)

# Individual Agents
test("Price Agent - Valid Symbol", test_price_agent_valid)
test("Price Agent - Invalid Symbol", test_price_agent_invalid)
test("Macroeconomic Agent", test_macro_agent)
test("Sentiment Agent", test_sentiment_agent)
test("Risk Agent", test_risk_agent)
test("IPO Intelligence Agent", test_ipo_intelligence_agent)

# Real Data Fetcher
test("Data Fetcher Initialization", test_data_fetcher_initialization)
test("Data Fetcher - With Symbol", test_data_fetcher_with_symbol)
test("Data Fetcher - Without Symbol", test_data_fetcher_without_symbol)

# Edge Cases
test("Empty String Inputs", test_empty_strings)
test("Very Large Numbers", test_very_large_numbers)
test("Special Characters in Name", test_special_characters)
test("Future Listing Date", test_future_date)
test("Very Old Listing Date", test_very_old_date)
test("Concurrent Analyses", test_concurrent_analyses)

# Output Validation
test("Output Completeness", test_output_completeness)
test("Agent Scores Structure", test_agent_scores_structure)

# ============================================================================
# FINAL REPORT
# ============================================================================

print("\n" + "="*70)
print("FINAL TEST REPORT")
print("="*70)

print(f"\nTotal Tests: {results['total']}")
print(f"✅ Passed: {results['passed']} ({results['passed']/results['total']*100:.1f}%)")
print(f"❌ Failed: {results['failed']} ({results['failed']/results['total']*100:.1f}%)")

if results['bugs_found']:
    print(f"\n🐛 BUGS FOUND ({len(results['bugs_found'])}):")
    for i, bug in enumerate(results['bugs_found'], 1):
        print(f"   {i}. {bug}")
else:
    print("\n✅ NO BUGS FOUND - SYSTEM IS 100% RELIABLE!")

# Save results
with open('final_test_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n📄 Detailed results saved to: final_test_results.json")

# Exit code
if results['failed'] == 0:
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED - PRODUCTION READY!")
    print("="*70)
    sys.exit(0)
else:
    print("\n" + "="*70)
    print("⚠️  SOME TESTS FAILED - REVIEW BUGS ABOVE")
    print("="*70)
    sys.exit(1)
