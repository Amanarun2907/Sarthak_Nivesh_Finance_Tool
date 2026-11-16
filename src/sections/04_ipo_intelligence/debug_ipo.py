import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
})

# Test 1: Chittorgarh subscription status
print("=== TEST 1: Chittorgarh subscription status ===")
url = "https://www.chittorgarh.com/report/ipo_subscription_status_live_data/93/"
r = session.get(url, timeout=15)
r.encoding = r.apparent_encoding or "utf-8"
print(f"Status: {r.status_code}")
soup = BeautifulSoup(r.text, "html.parser")
tables = soup.find_all("table")
print(f"Tables found: {len(tables)}")
for i, t in enumerate(tables[:2]):
    rows = t.find_all("tr")
    print(f"  Table {i}: {len(rows)} rows")
    for row in rows[:3]:
        print(f"    {[td.get_text(strip=True)[:20] for td in row.find_all(['td','th'])]}")

# Test 2: Chittorgarh performance tracker
print("\n=== TEST 2: Chittorgarh performance tracker ===")
url2 = "https://www.chittorgarh.com/report/ipo_performance_tracker/84/"
r2 = session.get(url2, timeout=15)
r2.encoding = r2.apparent_encoding or "utf-8"
print(f"Status: {r2.status_code}")
soup2 = BeautifulSoup(r2.text, "html.parser")
tables2 = soup2.find_all("table")
print(f"Tables found: {len(tables2)}")
for i, t in enumerate(tables2[:2]):
    rows = t.find_all("tr")
    print(f"  Table {i}: {len(rows)} rows")
    for row in rows[:3]:
        print(f"    {[td.get_text(strip=True)[:20] for td in row.find_all(['td','th'])]}")

# Test 3: InvestorGain GMP
print("\n=== TEST 3: InvestorGain GMP ===")
url3 = "https://www.investorgain.com/report/live-ipo-gmp/331/"
r3 = session.get(url3, timeout=15)
r3.encoding = r3.apparent_encoding or "utf-8"
print(f"Status: {r3.status_code}")
soup3 = BeautifulSoup(r3.text, "html.parser")
tables3 = soup3.find_all("table")
print(f"Tables found: {len(tables3)}")
for i, t in enumerate(tables3[:2]):
    rows = t.find_all("tr")
    print(f"  Table {i}: {len(rows)} rows, id={t.get('id','')}, class={t.get('class','')}")
    for row in rows[:3]:
        print(f"    {[td.get_text(strip=True)[:20] for td in row.find_all(['td','th'])]}")
