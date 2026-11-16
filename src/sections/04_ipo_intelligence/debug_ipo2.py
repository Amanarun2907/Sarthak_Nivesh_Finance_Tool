import requests
from bs4 import BeautifulSoup
import json

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.chittorgarh.com/",
    "X-Requested-With": "XMLHttpRequest"
})

# Test Chittorgarh API endpoints
print("=== Chittorgarh API Tests ===")
urls = [
    "https://www.chittorgarh.com/api/ipo/list/",
    "https://www.chittorgarh.com/api/ipo/open/",
    "https://www.chittorgarh.com/api/ipo/upcoming/",
    "https://www.chittorgarh.com/api/ipo/recent/",
    "https://www.chittorgarh.com/api/ipo/performance/",
]
for url in urls:
    try:
        r = session.get(url, timeout=10)
        print(f"{url}: {r.status_code} | {r.text[:100]}")
    except Exception as e:
        print(f"{url}: ERROR {e}")

# Test InvestorGain API
print("\n=== InvestorGain API Tests ===")
ig_urls = [
    "https://www.investorgain.com/api/ipo/gmp/",
    "https://www.investorgain.com/api/live-ipo-gmp/",
]
for url in ig_urls:
    try:
        r = session.get(url, timeout=10)
        print(f"{url}: {r.status_code} | {r.text[:100]}")
    except Exception as e:
        print(f"{url}: ERROR {e}")

# Test NSE IPO APIs
print("\n=== NSE IPO API Tests ===")
nse_session = requests.Session()
nse_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/"
})
nse_session.get("https://www.nseindia.com", timeout=10)
import time; time.sleep(1)

nse_urls = [
    "https://www.nseindia.com/api/ipo-current-allotment",
    "https://www.nseindia.com/api/ipo-upcoming-issues",
    "https://www.nseindia.com/api/ipo-past-issues",
    "https://www.nseindia.com/api/ipo-subscription-status",
    "https://www.nseindia.com/api/ipo-current-issues",
]
for url in nse_urls:
    try:
        r = nse_session.get(url, timeout=10)
        print(f"{url.split('/')[-1]}: {r.status_code} | {r.text[:150]}")
    except Exception as e:
        print(f"{url.split('/')[-1]}: ERROR {e}")
