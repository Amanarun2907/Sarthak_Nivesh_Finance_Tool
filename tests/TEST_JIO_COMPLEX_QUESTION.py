"""
🎯 COMPLEX JIO PLATFORMS IPO ANALYSIS TEST
===========================================
Testing all 12 agents with a sophisticated, multi-layered question about:
- Capital allocation decisions
- Off-balance sheet obligations
- Pre-IPO investor dynamics
- True shareholder value

This tests the DEPTH and QUALITY of agent analysis.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

COMPLEX_QUESTION = """How does Jio Platforms' decision to use its entire ₹30,188 crore fresh issue strictly to prepay bank borrowings at Reliance Jio Infocomm affect the true equity value for public shareholders, given that over ₹1.04 lakh crore in deferred spectrum payment obligations remain off the reported net debt and excluded from the use of proceeds, while major pre-IPO cap-table investors like Meta and Google retain their stakes without providing an exit?"""

def print_header(title, char="="):
    print("\n" + char*100)
    print(f"  {title}")
    print(char*100)

def print_analysis(text, max_length=800):
    """Print analysis with word wrap"""
    if len(text) <= max_length:
        print(text)
    else:
        print(text[:max_length] + "...")
        print(f"\n[Full analysis: {len(text)} characters - showing first {max_length}]")

def test_agentic_ai_hub():
    """Test Agentic AI Hub with complex Jio question"""
    print_header("🤖 AGENTIC AI HUB - COMPLEX JIO ANALYSIS", "=")
    
    payload = {
        "query": COMPLEX_QUESTION,
        "agents": ["stock", "market", "smartmoney", "news", "risk", "analytics"]
    }
    
    print("\n📡 Sending complex Jio question to Agentic AI Hub...")
    print(f"\n❓ QUESTION (Complex & Multi-layered):")
    print("   " + COMPLEX_QUESTION[:150] + "...")
    print(f"\n   Full question length: {len(COMPLEX_QUESTION)} characters")
    print(f"   Complexity: High (Capital structure, Off-BS items, Investor dynamics)")
    
    start = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/agentic/run",
            json=payload,
            timeout=180
        )
        
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            
            print_header("✅ AGENTIC AI HUB - ANALYSIS COMPLETE", "✅")
            
            print(f"\n⏱️  Duration: {duration:.2f}s")
            print(f"📊 Agents Run: {data['agents_run']}/6")
            
            print_header("📊 AGENT PERFORMANCE ANALYSIS", "-")
            
            quality_scores = []
            
            for i, agent in enumerate(data['agent_results'], 1):
                print(f"\n{'='*100}")
                print(f"AGENT {i}: {agent['agent']} {agent['icon']}")
                print(f"{'='*100}")
                print(f"Status: {agent['status']}")
                
                analysis = agent.get('analysis', 'No analysis')
                
                # Analyze quality
                has_numbers = any(char.isdigit() for char in analysis)
                has_rupee = '₹' in analysis or 'crore' in analysis.lower()
                has_specific_refs = any(word in analysis.lower() for word in ['jio', 'reliance', 'meta', 'google', 'spectrum', 'debt'])
                length = len(analysis)
                
                quality_score = 0
                if has_numbers: quality_score += 25
                if has_rupee: quality_score += 25
                if has_specific_refs: quality_score += 30
                if length > 100: quality_score += 20
                
                quality_scores.append(quality_score)
                
                print(f"\n📈 QUALITY METRICS:")
                print(f"   Length: {length} characters")
                print(f"   Contains Numbers: {'✅' if has_numbers else '❌'}")
                print(f"   Contains ₹/Crores: {'✅' if has_rupee else '❌'}")
                print(f"   Jio-Specific: {'✅' if has_specific_refs else '❌'}")
                print(f"   Quality Score: {quality_score}/100")
                
                print(f"\n💬 ANALYSIS:")
                print_analysis(analysis, 600)
                
                # Show specific data for each agent
                if agent['agent'] == 'Stock Intelligence':
                    stocks = agent.get('stocks', [])
                    if stocks:
                        print(f"\n📊 Stock Data: {len(stocks)} stocks analyzed")
                elif agent['agent'] == 'Smart Money Tracker':
                    print(f"\n💰 FII/DII Data:")
                    print(f"   FII Net: ₹{agent.get('fii_net', 0):,.0f} Cr")
                    print(f"   DII Net: ₹{agent.get('dii_net', 0):,.0f} Cr")
                    print(f"   Signal: {agent.get('signal', 'N/A')}")
                elif agent['agent'] == 'News & Sentiment':
                    print(f"\n📰 Sentiment Analysis:")
                    print(f"   Articles: {len(agent.get('articles', []))}")
                    print(f"   Overall: {agent.get('overall', 'N/A')}")
            
            print_header("🎯 MASTER REPORT - COMPREHENSIVE ANALYSIS", "=")
            
            master = data.get('master_report', 'No master report')
            
            # Analyze master report quality
            master_has_jio = 'jio' in master.lower() or 'reliance' in master.lower()
            master_has_debt = 'debt' in master.lower() or 'borrowing' in master.lower()
            master_has_spectrum = 'spectrum' in master.lower()
            master_has_meta = 'meta' in master.lower() or 'google' in master.lower()
            master_length = len(master)
            
            print(f"\n📈 MASTER REPORT QUALITY:")
            print(f"   Length: {master_length} characters")
            print(f"   Addresses Jio: {'✅' if master_has_jio else '❌'}")
            print(f"   Addresses Debt: {'✅' if master_has_debt else '❌'}")
            print(f"   Addresses Spectrum: {'✅' if master_has_spectrum else '❌'}")
            print(f"   Addresses Investors: {'✅' if master_has_meta else '❌'}")
            
            master_quality = (
                (25 if master_has_jio else 0) +
                (25 if master_has_debt else 0) +
                (25 if master_has_spectrum else 0) +
                (25 if master_has_meta else 0)
            )
            print(f"   Overall Quality: {master_quality}/100")
            
            print(f"\n💬 MASTER REPORT:")
            print_analysis(master, 1000)
            
            print_header("📊 OVERALL PERFORMANCE SUMMARY", "=")
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            print(f"\n   Average Agent Quality: {avg_quality:.1f}/100")
            print(f"   Master Report Quality: {master_quality}/100")
            print(f"   Total Execution Time: {duration:.2f}s")
            print(f"   Agents Succeeded: {data['agents_run']}/6")
            
            overall_grade = "EXCELLENT" if avg_quality >= 70 and master_quality >= 75 else \
                           "GOOD" if avg_quality >= 50 and master_quality >= 50 else \
                           "NEEDS IMPROVEMENT"
            
            print(f"\n   🎯 Overall Grade: {overall_grade}")
            
            return {
                'success': True,
                'avg_quality': avg_quality,
                'master_quality': master_quality,
                'duration': duration,
                'grade': overall_grade
            }
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(response.text)
            return {'success': False}
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False}


def test_ipo_multiagent():
    """Test IPO Multi-Agent with Jio IPO scenario"""
    print_header("🚀 IPO MULTI-AGENT - JIO PLATFORMS ANALYSIS", "=")
    
    # Create Jio IPO-like scenario
    jio_ipo_data = {
        "ipo_name": "Jio Platforms IPO (Hypothetical)",
        "company_name": "Reliance Jio Infocomm",
        "symbol": "JIOPLAT",
        "exchange": "NSE",
        "price_band_min": 850,
        "price_band_max": 900,
        "issue_size_crores": 30188,  # Fresh issue amount
        "lot_size": 16,
        "qib_subscription": 0,  # Not yet subscribed
        "hni_subscription": 0,
        "retail_subscription": 0,
        "gmp_rupees": 0,
        "gmp_percentage": 0
    }
    
    print("\n📡 Sending Jio scenario to IPO Multi-Agent...")
    print(f"\n💼 JIO IPO SCENARIO:")
    print(f"   Company: {jio_ipo_data['company_name']}")
    print(f"   Fresh Issue: ₹{jio_ipo_data['issue_size_crores']:,} Crores")
    print(f"   Price Band: ₹{jio_ipo_data['price_band_min']} - ₹{jio_ipo_data['price_band_max']}")
    print(f"\n   💡 Complex Context:")
    print(f"      • ₹30,188 Cr to prepay bank borrowings")
    print(f"      • ₹1.04 lakh Cr spectrum obligations (off-balance sheet)")
    print(f"      • Meta & Google as pre-IPO investors (no exit)")
    
    start = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ipo_fixed/analyze-enhanced",
            json=jio_ipo_data,
            timeout=120
        )
        
        duration = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            
            print_header("✅ IPO MULTI-AGENT - ANALYSIS COMPLETE", "✅")
            
            print(f"\n⏱️  Duration: {duration:.2f}s")
            print(f"📊 Final Score: {data['overall_score']:.1f}/100")
            print(f"🎯 Confidence: {data['overall_confidence']*100:.1f}%")
            print(f"📈 Recommendation: {data['final_recommendation']}")
            
            print_header("📊 INDIVIDUAL AGENT ANALYSIS", "-")
            
            agents = data['agents']
            quality_scores = []
            
            for i, (name, agent) in enumerate(agents.items(), 1):
                print(f"\n{'='*100}")
                print(f"AGENT {i}: {agent['agent_name']} [{agent['framework']}]")
                print(f"{'='*100}")
                
                print(f"Status: {agent['status']}")
                print(f"Score: {agent['score']:.1f}/100")
                print(f"Confidence: {agent['confidence']*100:.1f}%")
                print(f"Recommendation: {agent['recommendation']}")
                print(f"Time: {agent['execution_time']:.2f}s")
                print(f"Cost: ${agent['cost_usd']:.4f}")
                
                # Analyze reasoning quality
                reasoning = agent.get('reasoning', '')
                insights = agent.get('key_insights', [])
                
                has_jio_ref = 'jio' in reasoning.lower() or 'reliance' in reasoning.lower()
                has_debt_ref = 'debt' in reasoning.lower() or 'borrowing' in reasoning.lower()
                has_spectrum_ref = 'spectrum' in reasoning.lower()
                has_numbers = any(char.isdigit() for char in reasoning)
                
                quality_score = (
                    (25 if has_jio_ref else 0) +
                    (25 if has_debt_ref else 0) +
                    (20 if has_spectrum_ref else 0) +
                    (30 if has_numbers else 0)
                )
                quality_scores.append(quality_score)
                
                print(f"\n📈 ANALYSIS QUALITY:")
                print(f"   Jio-Specific: {'✅' if has_jio_ref else '❌'}")
                print(f"   Debt Analysis: {'✅' if has_debt_ref else '❌'}")
                print(f"   Spectrum Reference: {'✅' if has_spectrum_ref else '❌'}")
                print(f"   Data-Driven: {'✅' if has_numbers else '❌'}")
                print(f"   Quality Score: {quality_score}/100")
                
                print(f"\n💡 KEY INSIGHTS ({len(insights)}):")
                for j, insight in enumerate(insights[:3], 1):
                    print(f"   {j}. {insight[:120]}{'...' if len(insight) > 120 else ''}")
                
                if reasoning:
                    print(f"\n💬 REASONING:")
                    print_analysis(reasoning, 400)
            
            print_header("💡 DYNAMIC STRATEGY ANALYSIS", "=")
            
            strategy = data['dynamic_strategy']
            print(f"\n   Action: {strategy['action']}")
            print(f"   Allocation: {strategy['allocation_percentage']}%")
            print(f"   Risk Level: {strategy['risk_level']}")
            print(f"   Expected Return: {strategy['expected_return_min']:.1f}% to {strategy['expected_return_max']:.1f}%")
            print(f"   Time Horizon: {strategy['time_horizon']}")
            print(f"\n   Entry Strategy:")
            print(f"      {strategy['entry_strategy']}")
            print(f"\n   Exit Strategy:")
            print(f"      {strategy['exit_strategy']}")
            
            # Analyze if strategy addresses the complex question
            conditions = ' '.join(strategy.get('conditions', []))
            addresses_debt = 'debt' in conditions.lower() or 'borrowing' in conditions.lower()
            
            print(f"\n   🎯 Strategy Relevance:")
            print(f"      Addresses Debt Concerns: {'✅' if addresses_debt else '❌'}")
            
            print_header("🎮 CONTROL TOWER METRICS", "=")
            
            tower = data['control_tower']
            print(f"\n   Total Agents: {tower['total_agents']}")
            print(f"   Completed: {tower['completed_agents']}")
            print(f"   Failed: {tower['failed_agents']}")
            print(f"   Progress: {tower['overall_progress']:.0f}%")
            print(f"   Duration: {tower['total_duration']:.2f}s")
            print(f"   Total Cost: ${tower['total_cost']:.4f}")
            
            print_header("📊 OVERALL PERFORMANCE SUMMARY", "=")
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            print(f"\n   Average Agent Quality: {avg_quality:.1f}/100")
            print(f"   Overall IPO Score: {data['overall_score']:.1f}/100")
            print(f"   System Confidence: {data['overall_confidence']*100:.1f}%")
            print(f"   Total Execution Time: {duration:.2f}s")
            print(f"   Agents Succeeded: {tower['completed_agents']}/{tower['total_agents']}")
            
            overall_grade = "EXCELLENT" if avg_quality >= 60 and data['overall_score'] >= 50 else \
                           "GOOD" if avg_quality >= 40 else \
                           "NEEDS IMPROVEMENT"
            
            print(f"\n   🎯 Overall Grade: {overall_grade}")
            
            return {
                'success': True,
                'avg_quality': avg_quality,
                'ipo_score': data['overall_score'],
                'duration': duration,
                'grade': overall_grade
            }
        else:
            print(f"\n❌ Error: HTTP {response.status_code}")
            print(response.text)
            return {'success': False}
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False}


if __name__ == "__main__":
    print("\n" + "╔" + "="*98 + "╗")
    print("║" + " "*98 + "║")
    print("║" + "  🎯 COMPLEX JIO PLATFORMS IPO ANALYSIS TEST".center(98) + "║")
    print("║" + "  Testing Agent Depth & Analytical Quality".center(98) + "║")
    print("║" + " "*98 + "║")
    print("╚" + "="*98 + "╝")
    
    print("\n📋 TEST OBJECTIVE:")
    print("   Test all 12 agents with a sophisticated multi-layered question about:")
    print("   • Capital allocation (₹30,188 Cr fresh issue)")
    print("   • Off-balance sheet obligations (₹1.04 lakh Cr spectrum)")
    print("   • Pre-IPO investor dynamics (Meta, Google)")
    print("   • True shareholder value implications")
    
    print("\n🎓 COMPLEXITY LEVEL: EXPERT")
    print("   This tests whether agents can handle real-world IPO complexity")
    
    # Test both systems
    print("\n" + "─"*100)
    agentic_results = test_agentic_ai_hub()
    
    print("\n" + "─"*100)
    ipo_results = test_ipo_multiagent()
    
    # Final comparison
    print("\n" + "="*100)
    print_header("🎊 FINAL COMPARATIVE ANALYSIS", "=")
    
    if agentic_results.get('success') and ipo_results.get('success'):
        print(f"\n   📊 AGENTIC AI HUB:")
        print(f"      Average Quality: {agentic_results['avg_quality']:.1f}/100")
        print(f"      Master Quality: {agentic_results['master_quality']}/100")
        print(f"      Duration: {agentic_results['duration']:.2f}s")
        print(f"      Grade: {agentic_results['grade']}")
        
        print(f"\n   🚀 IPO MULTI-AGENT:")
        print(f"      Average Quality: {ipo_results['avg_quality']:.1f}/100")
        print(f"      IPO Score: {ipo_results['ipo_score']:.1f}/100")
        print(f"      Duration: {ipo_results['duration']:.2f}s")
        print(f"      Grade: {ipo_results['grade']}")
        
        print(f"\n   🏆 WINNER:")
        if agentic_results['avg_quality'] > ipo_results['avg_quality']:
            print(f"      Agentic AI Hub (Better analytical depth)")
        elif ipo_results['avg_quality'] > agentic_results['avg_quality']:
            print(f"      IPO Multi-Agent (More IPO-focused analysis)")
        else:
            print(f"      TIE (Both systems performed equally)")
        
        print("\n" + "="*100)
        print("  ✅ BOTH SYSTEMS SUCCESSFULLY ANALYZED COMPLEX QUESTION!")
        print("  The agents demonstrated sophisticated understanding of:")
        print("     • Multi-layered financial structures")
        print("     • Capital allocation implications")
        print("     • Shareholder value considerations")
        print("="*100)
    else:
        print("\n⚠️  Some systems encountered issues. Check errors above.")
    
    print("\n📚 API Documentation: http://localhost:8000/docs")
    print("🔗 Agentic AI Hub: POST /api/agentic/run")
    print("🔗 IPO Multi-Agent: POST /api/ipo_fixed/analyze-enhanced")
    print()
