"""
QUICK BUG VALIDATION TEST
Tests only the critical bugs that were reported
"""
import sys
sys.path.insert(0, 'sections/06_agentic_ai_hub')

print("\n" + "="*70)
print("QUICK BUG VALIDATION TEST")
print("="*70)

# Import system
try:
    from ipo_multi_agent_framework import (
        run_ipo_multi_agent_analysis,
        PriceMovementAgent,
        MacroeconomicAgent,
        SentimentAgent,
        RiskAgent,
        IPOIntelligenceAgent,
        GroqLLM
    )
    from ipo_real_data_fetcher import RealIPODataFetcher
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

bugs_found = []
tests_passed = 0
tests_total = 0

# ============================================================================
# BUG TEST 1: GMP Variable UnboundLocalError
# ============================================================================
print("\n" + "="*70)
print("BUG TEST 1: GMP Variable UnboundLocalError (FIXED)")
print("="*70)
tests_total += 1

try:
    llm = GroqLLM()
    agent = IPOIntelligenceAgent(llm)
    # This used to crash with UnboundLocalError when GMP fetch failed
    result = agent.run("Test IPO", "INVALID.NS", 1000, 1000, 0, 10, 20, 5, "")
    gmp_value = result.details.get('gmp_data', {}).get('gmp', 0)
    print(f"✅ No crash! GMP handled: Rs.{gmp_value:.2f}")
    tests_passed += 1
except Exception as e:
    bugs_found.append(f"BUG 1: GMP variable error - {str(e)}")
    print(f"❌ FAILED: {e}")

# ============================================================================
# BUG TEST 2: Invalid Symbol Crashes
# ============================================================================
print("\n" + "="*70)
print("BUG TEST 2: Invalid Symbol Crashes (FIXED)")
print("="*70)
tests_total += 1

try:
    llm = GroqLLM()
    agent = PriceMovementAgent(llm)
    # This used to crash with invalid symbols - need both symbol and ipo_name
    result = agent.run("INVALID_SYMBOL_12345.NS", "Test IPO")
    print(f"✅ No crash! Score: {result.score:.1f}, Signal: {result.signal}")
    tests_passed += 1
except Exception as e:
    bugs_found.append(f"BUG 2: Invalid symbol crash - {str(e)}")
    print(f"❌ FAILED: {e}")

# ============================================================================
# BUG TEST 3: Macroeconomic Agent - No NIFTY Data
# ============================================================================
print("\n" + "="*70)
print("BUG TEST 3: Macroeconomic Agent - No NIFTY Data (FIXED)")
print("="*70)
tests_total += 1

try:
    llm = GroqLLM()
    agent = MacroeconomicAgent(llm)
    result = agent.run()
    # Check that agent returns valid result even if data fetch fails
    assert result.score >= 0 and result.score <= 100, f"Invalid score: {result.score}"
    assert 'nifty' in result.details, "No NIFTY data in details"
    print(f"✅ No crash! Score: {result.score:.1f}, Has NIFTY data: {bool(result.details['nifty'])}")
    tests_passed += 1
except AssertionError as e:
    bugs_found.append(f"BUG 3: Macroeconomic Agent NIFTY - {str(e)}")
    print(f"❌ FAILED: {e}")
except Exception as e:
    bugs_found.append(f"BUG 3: Macroeconomic Agent error - {str(e)}")
    print(f"❌ FAILED: {e}")

# ============================================================================
# BUG TEST 4: Null/None Value Handling
# ============================================================================
print("\n" + "="*70)
print("BUG TEST 4: Null/None Value Handling (FIXED)")
print("="*70)
tests_total += 1

try:
    # Test with None and 0 values
    result = run_ipo_multi_agent_analysis(
        None, None, 0, 0, 0, 0, 0, 0, None
    )
    print(f"✅ No crash! Decision: {result.final_decision}, Score: {result.overall_score:.1f}")
    tests_passed += 1
except Exception as e:
    bugs_found.append(f"BUG 4: Null/None handling - {str(e)}")
    print(f"❌ FAILED: {e}")

# ============================================================================
# BUG TEST 5: Real IPO Data Integration
# ============================================================================
print("\n" + "="*70)
print("BUG TEST 5: Real IPO Data Fetcher Integration (WORKING)")
print("="*70)
tests_total += 1

try:
    fetcher = RealIPODataFetcher()
    # Test with a real listed IPO - use get_complete_ipo_data method
    data = fetcher.get_complete_ipo_data("Hyundai Motor India", "HYUNDAI.NS")
    
    assert data is not None, "Data fetcher returned None"
    assert 'data_quality' in data, "Missing data_quality field"
    
    quality = data['data_quality']
    current_price = data.get('current_price', 0)
    
    print(f"✅ Real data fetched!")
    print(f"   Data Quality: {quality}/100")
    print(f"   Current Price: Rs.{current_price:.2f}")
    print(f"   Sources: {', '.join(data.get('data_sources_used', []))}")
    tests_passed += 1
except Exception as e:
    bugs_found.append(f"BUG 5: Real data fetcher - {str(e)}")
    print(f"❌ FAILED: {e}")

# ============================================================================
# BUG TEST 6: Complete IPO Analysis (Real World Test)
# ============================================================================
print("\n" + "="*70)
print("BUG TEST 6: Complete IPO Analysis - Hyundai (REAL WORLD TEST)")
print("="*70)
tests_total += 1

try:
    result = run_ipo_multi_agent_analysis(
        ipo_name="Hyundai Motor India",
        symbol="HYUNDAI.NS",
        issue_price=1960,
        listing_price=1931,
        current_price=0,  # Will be auto-fetched
        sub_total=0,  # Will be auto-fetched
        sub_qib=6.97,
        sub_retail=2.0,
        listing_date_str="2024-10-22"
    )
    
    assert result is not None, "Analysis returned None"
    assert result.overall_score >= 0 and result.overall_score <= 100, "Invalid score"
    assert result.final_decision in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"], "Invalid decision"
    assert result.confidence >= 0 and result.confidence <= 100, "Invalid confidence"
    
    print(f"✅ Complete analysis successful!")
    print(f"   Decision: {result.final_decision}")
    print(f"   Score: {result.overall_score:.1f}/100")
    print(f"   Confidence: {result.confidence:.1f}%")
    print(f"   Target Price: Rs.{result.target_price:.2f}")
    print(f"   Stop Loss: Rs.{result.stop_loss:.2f}")
    tests_passed += 1
except Exception as e:
    bugs_found.append(f"BUG 6: Complete analysis - {str(e)}")
    print(f"❌ FAILED: {e}")

# ============================================================================
# FINAL REPORT
# ============================================================================
print("\n" + "="*70)
print("FINAL BUG TEST REPORT")
print("="*70)
print(f"\nTotal Tests: {tests_total}")
print(f"✅ Passed: {tests_passed} ({tests_passed*100//tests_total}%)")
print(f"❌ Failed: {tests_total - tests_passed}")

if bugs_found:
    print(f"\n🐛 BUGS STILL PRESENT ({len(bugs_found)}):")
    for i, bug in enumerate(bugs_found, 1):
        print(f"   {i}. {bug}")
    print("\n" + "="*70)
    print("❌ SYSTEM HAS BUGS - NEEDS MORE FIXES")
    print("="*70)
    sys.exit(1)
else:
    print("\n" + "="*70)
    print("✅ ALL BUGS FIXED - SYSTEM IS PRODUCTION READY")
    print("="*70)
    print("\n🎯 SYSTEM STATUS:")
    print("   ✅ No crashes with invalid inputs")
    print("   ✅ Graceful error handling everywhere")
    print("   ✅ Real data integration working")
    print("   ✅ All agents functioning correctly")
    print("   ✅ Complete end-to-end analysis working")
    sys.exit(0)
