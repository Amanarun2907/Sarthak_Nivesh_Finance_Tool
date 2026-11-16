import requests
from bs4 import BeautifulSoup
import json

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
})

# Test IPO data from ipowatch.in
print("=== ipowatch.in ===")
try:
    r = session.get("https://ipowatch.in/ipo-grey-market-premium-latest-ipo-gmp/", timeout=15)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Status: {r.status_code}, Tables: {len(tables)}")
    for t in tables[:1]:
        rows = t.find_all("tr")
        print(f"Rows: {len(rows)}")
        for row in rows[:5]:
            cells = [td.get_text(strip=True)[:25] for td in row.find_all(["td","th"])]
            if cells: print(f"  {cells}")
except Exception as e:
    print(f"Error: {e}")

# Test IPO data from ipomonitor.in
print("\n=== ipomonitor.in ===")
try:
    r = session.get("https://www.ipomonitor.in/pages/ipo-subscription-status.html", timeout=15)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table")
    print(f"Status: {r.status_code}, Tables: {len(tables)}")
    for t in tables[:1]:
        rows = t.find_all("tr")
        print(f"Rows: {len(rows)}")
        for row in rows[:5]:
            cells = [td.get_text(strip=True)[:25] for td in row.find_all(["td","th"])]
            if cells: print(f"  {cells}")
except Exception as e:
    print(f"Error: {e}")

# Test IPO data from NSE direct page
print("\n=== NSE IPO page ===")
try:
    nse = requests.Session()
    nse.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    })
    nse.get("https://www.nseindia.com", timeout=10)
    import time; time.sleep(1)
    r = nse.get("https://www.nseindia.com/api/ipo-current-allotment", timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print(r.text[:300])
    # Try different NSE endpoints
    for ep in ["allotment", "ipo", "ipo-allotment", "ipo-subscription"]:
        r2 = nse.get(f"https://www.nseindia.com/api/{ep}", timeout=8)
        print(f"  /api/{ep}: {r2.status_code}")
except Exception as e:
    print(f"Error: {e}")

# Test BSE IPO API
print("\n=== BSE IPO API ===")
try:
    bse = requests.Session()
    bse.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.bseindia.com/"
    })
    endpoints = [
        "https://api.bseindia.com/BseIndiaAPI/api/IPOIssues/w?type=current",
        "https://api.bseindia.com/BseIndiaAPI/api/IPOIssues/w?type=upcoming",
        "https://api.bseindia.com/BseIndiaAPI/api/IPOIssues/w?type=recent",
    ]
    for url in endpoints:
        r = bse.get(url, timeout=10)
        print(f"  {url.split('type=')[1]}: {r.status_code} | {r.text[:200]}")
except Exception as e:
    print(f"BSE Error: {e}")
