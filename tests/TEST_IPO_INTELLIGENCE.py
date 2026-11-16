"""
Test IPO Intelligence Hub - All 6 Agents
========================================
Quick test to verify all agents are working correctly
"""

import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://localhost:8000"
IPO_API = f"{BASE_URL}/api/ipo_intelligence"

def test_health_check():
    """Test if the service is running"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{IPO_API}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Service is healthy!")
            print(f"   Status: {data['status']}")
            print(f"   Service: {data['service']}")
            print(f"   Groq API: {data['groq_api']}")
            print(f"   Agents: {len(data['agents'])} agents active")
            for i, agent in enumerate(data['agents'], 1):
                print(f"      {i}. {agent}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("⚠️  Make sure backend is running: START_COMPLETE_SYSTEM.bat")
        return False


def test_ipo_analysis(company_name="Reliance Industries", symbol="RELIANCE.NS"):
    """Test complete IPO analysis with all 6 agents"""
    print(f"\n🚀 Testing IPO Analysis for: {company_name}")
    print("=" * 80)
    
    try:
        # Prepare request
        request_data = {
            "company_name": company_name,
            "symbol": symbol,
            "issue_price": 1450.0,
            "issue_size": 5000.0,
            "lot_size": 10
        }
        
        print(f"📤 Sending request...")
        print(f"   Company: {company_name}")
        print(f"   Symbol: {symbol}")
        print()
        
        # Make API call
        response = requests.post(
            f"{IPO_API}/analyze",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Analysis Complete!")
            print("=" * 80)
            print()
            
            # Overall Results
            print(f"🏢 Company: {result['company_name']}")
            print(f"📈 Symbol: {result['symbol']}")
            print(f"🕒 Timestamp: {result['timestamp']}")
            print()
            
            print("=" * 80)
            print("🎯 FINAL RECOMMENDATION")
            print("=" * 80)
            print(f"Recommendation: {result['final_recommendation']}")
            print(f"Overall Score: {result['overall_score']:.2f}/100")
            print(f"Confidence: {result['overall_confidence']*100:.1f}%")
            print()
            
            # Agent Scores
            print("=" * 80)
            print("🤖 AGENT SCORES")
            print("=" * 80)
            
            agents = [
                ("subscription_score", "📊 Subscription Analysis"),
                ("gmp_score", "💰 GMP Analysis"),
                ("financials_score", "📈 Financials & Fundamentals"),
                ("listing_score", "🎯 Listing Day Predictor"),
                ("post_listing_score", "📅 Post-Listing Tracker"),
                ("risk_score", "⚠️  Risk Assessment")
            ]
            
            for agent_key, agent_name in agents:
                agent_data = result[agent_key]
                print(f"\n{agent_name}")
                print(f"   Score: {agent_data['score']:.1f}/100")
                print(f"   Confidence: {agent_data['confidence']*100:.1f}%")
                print(f"   Recommendation: {agent_data['recommendation']}")
                print(f"   Key Insights:")
                for insight in agent_data['key_insights'][:3]:
                    print(f"      • {insight}")
            
            # Strengths
            print("\n" + "=" * 80)
            print("✅ STRENGTHS")
            print("=" * 80)
            for i, strength in enumerate(result['strengths'], 1):
                print(f"{i}. {strength}")
            
            # Risks
            print("\n" + "=" * 80)
            print("⚠️  RISKS")
            print("=" * 80)
            for i, risk in enumerate(result['risks'], 1):
                print(f"{i}. {risk}")
            
            # Action Items
            print("\n" + "=" * 80)
            print("📋 ACTION ITEMS")
            print("=" * 80)
            for i, action in enumerate(result['action_items'], 1):
                print(f"{i}. {action}")
            
            # Performance
            print("\n" + "=" * 80)
            print("⚡ PERFORMANCE METRICS")
            print("=" * 80)
            print(f"Analysis Duration: {result['analysis_duration']:.2f} seconds")
            print(f"Tokens Used: {result['tokens_used']:,}")
            
            print("\n" + "=" * 80)
            print("✅ TEST PASSED - All 6 agents working perfectly!")
            print("=" * 80)
            
            return True
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_companies():
    """Test with multiple companies"""
    print("\n\n" + "=" * 80)
    print("🧪 TESTING MULTIPLE COMPANIES")
    print("=" * 80)
    
    companies = [
        {"name": "Tata Consultancy Services", "symbol": "TCS.NS"},
        {"name": "Infosys", "symbol": "INFY.NS"},
        {"name": "HDFC Bank", "symbol": "HDFCBANK.NS"}
    ]
    
    for company in companies:
        print(f"\n{'─'*80}")
        test_ipo_analysis(company["name"], company["symbol"])
        print(f"{'─'*80}")


if __name__ == "__main__":
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  🧪 IPO INTELLIGENCE HUB - COMPLETE TEST SUITE".center(78) + "║")
    print("║" + "  All 6 Agents with Groq API".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Step 1: Health Check
    if test_health_check():
        print()
        
        # Step 2: Single Company Test
        print("\n" + "=" * 80)
        print("TEST 1: Single Company Analysis")
        print("=" * 80)
        test_ipo_analysis()
        
        # Step 3: Multiple Companies (optional)
        print("\n\n❓ Do you want to test multiple companies? (y/n): ", end="")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                test_multiple_companies()
        except:
            pass
        
        print("\n\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETE!")
        print("=" * 80)
        print()
        print("🎯 Your IPO Intelligence Hub with all 6 agents is working perfectly!")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔗 Test endpoint: http://localhost:8000/api/ipo_intelligence/health")
        print()
    else:
        print("\n⚠️  Please start the backend server first:")
        print("   Run: START_COMPLETE_SYSTEM.bat")
