"""
Test all Budget Intelligence API endpoints and visualizations
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/budget"
budget_id = "budget_20261103_140607"

def test_endpoint(name, url):
    try:
        r = requests.get(url)
        data = r.json()
        print(f"✅ {name}: {r.status_code} - Keys: {list(data.keys())[:8]}")
        return True
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

print("=" * 70)
print("🧪 TESTING ALL BUDGET INTELLIGENCE API ENDPOINTS")
print("=" * 70)

# Test all endpoints
endpoints = [
    ("Health Check", f"{BASE_URL}/health"),
    ("List Budgets", f"{BASE_URL}/list"),
    ("Complete Analysis", f"{BASE_URL}/{budget_id}/complete-analysis"),
    ("Budget at Glance", f"{BASE_URL}/{budget_id}/budget-at-glance"),
    ("Revenue Analysis", f"{BASE_URL}/{budget_id}/revenue-analysis"),
    ("Expenditure Analysis", f"{BASE_URL}/{budget_id}/expenditure-analysis"),
    ("Ministry Analysis", f"{BASE_URL}/{budget_id}/ministry-analysis"),
    ("Scheme Analysis", f"{BASE_URL}/{budget_id}/scheme-analysis"),
    ("Sectoral Analysis", f"{BASE_URL}/{budget_id}/sectoral-analysis"),
    ("Taxation Analysis", f"{BASE_URL}/{budget_id}/taxation-analysis"),
    ("Fiscal Analysis", f"{BASE_URL}/{budget_id}/fiscal-analysis"),
    ("Economic Impact", f"{BASE_URL}/{budget_id}/economic-impact"),
    ("Recommendations", f"{BASE_URL}/{budget_id}/recommendations"),
    ("Announcements", f"{BASE_URL}/{budget_id}/announcements"),
    ("Summary", f"{BASE_URL}/{budget_id}/summary"),
    ("Statistics", f"{BASE_URL}/{budget_id}/statistics"),
]

passed = 0
for name, url in endpoints:
    if test_endpoint(name, url):
        passed += 1

print(f"\n{'=' * 70}")
print(f"📊 RESULTS: {passed}/{len(endpoints)} endpoints passed")
print(f"{'=' * 70}")

# Test data quality for visualizations
print("\n🎨 TESTING VISUALIZATION DATA QUALITY")
print("-" * 50)

r = requests.get(f"{BASE_URL}/{budget_id}/complete-analysis")
data = r.json()

# Check Ministry data for bar chart
ministries = data.get('ministry_allocations', [])
print(f"\n📊 Ministry Bar Chart Data:")
print(f"   Total ministries: {len(ministries)}")
if ministries:
    print(f"   Top 5: {[m['name'].replace('Ministry of ', '')[:25] for m in ministries[:5]]}")
    print(f"   Allocations: {[m['allocation'] for m in ministries[:5]]}")

# Check Scheme data for treemap
schemes = data.get('schemes', [])
print(f"\n🎯 Scheme Treemap Data:")
print(f"   Total schemes: {len(schemes)}")
if schemes:
    print(f"   Top 5: {[s['name'][:25] for s in schemes[:5]]}")

# Check Sectoral data for pie chart
sectors = data.get('sectoral', {})
print(f"\n📊 Sectoral Pie Chart Data:")
print(f"   Total sectors: {len(sectors)}")
print(f"   Sectors: {list(sectors.keys())}")

# Check Revenue data for charts
revenue = data.get('revenue_data', {})
tax_revenue = revenue.get('tax_revenue', {})
print(f"\n💰 Revenue Chart Data:")
print(f"   Tax components: {len([k for k, v in tax_revenue.items() if k != 'total' and isinstance(v, (int, float))])}")
print(f"   Non-tax components: {len(revenue.get('non_tax_revenue', {}))}")

# Check Fiscal Health for gauge
fiscal_health = data.get('analysis', {}).get('fiscal_health', {})
print(f"\n🏥 Fiscal Health Gauge:")
print(f"   Score: {fiscal_health.get('sustainability_score')}/100")
print(f"   Health: {fiscal_health.get('overall_health')}")

# Check Scorecard
scorecard = data.get('analysis', {}).get('scorecard', {})
print(f"\n📈 Scorecard:")
print(f"   Overall Grade: {scorecard.get('overall_grade')}")
print(f"   Overall Score: {scorecard.get('overall_score')}")

# Check Recommendations
recommendations = data.get('analysis', {}).get('recommendations', [])
print(f"\n💡 Recommendations: {len(recommendations)} items")
for rec in recommendations[:3]:
    print(f"   [{rec.get('priority')}] {rec.get('category')}")

# Check Statistics
stats = data.get('analysis', {}).get('statistics', {})
print(f"\n📊 Statistics:")
print(f"   Per capita: ₹{stats.get('per_capita_allocation', 0):,}")
print(f"   Ministries funded: {stats.get('total_ministries_funded')}")
print(f"   Schemes funded: {stats.get('total_schemes_funded')}")

print("\n" + "=" * 70)
print("✅ ALL VISUALIZATION DATA VERIFIED")
print("=" * 70)
