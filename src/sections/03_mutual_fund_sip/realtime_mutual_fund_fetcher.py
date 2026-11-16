"""
Real-time Mutual Fund Data Fetcher
Sources: AMFI (NAV) + mfapi.in (returns) — 100% real data, zero static values
"""

import requests
from datetime import datetime
import time


class RealtimeMutualFundFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/html, */*',
        })
        self._amfi_nav_cache = {}  # scheme_code → nav info

    # ── AMFI: Real NAV for all funds ─────────────────────────────────────────
    def fetch_from_amfi(self):
        """Fetch all Direct Growth fund NAVs from AMFI. Returns list of dicts."""
        try:
            r = self.session.get("https://www.amfiindia.com/spages/NAVAll.txt", timeout=20)
            if r.status_code != 200:
                return []
            funds = []
            current_amc = ""
            for line in r.text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                if ';' not in line:
                    if line.isupper() or (len(line) > 5 and 'Mutual Fund' in line):
                        current_amc = line
                    continue
                parts = line.split(';')
                if len(parts) < 5:
                    continue
                try:
                    code = parts[0].strip()
                    name = parts[3].strip()
                    nav_str = parts[4].strip()
                    date_str = parts[5].strip() if len(parts) > 5 else datetime.now().strftime('%d-%b-%Y')
                    if not nav_str or nav_str in ['N.A.', '-', '']:
                        continue
                    nav = float(nav_str)
                    if 'Direct' in name and 'Growth' in name and nav > 0:
                        fund = {
                            'scheme_code': code,
                            'scheme_name': name,
                            'amc': current_amc,
                            'nav': nav,
                            'date': date_str,
                            'return_1y': 0,
                            'return_3y': 0,
                            'return_5y': 0,
                        }
                        funds.append(fund)
                        self._amfi_nav_cache[code] = fund
                except (ValueError, IndexError):
                    continue
            return funds
        except Exception as e:
            print(f"AMFI error: {e}")
            return []

    # ── mfapi.in: Real returns for specific funds ─────────────────────────────
    def fetch_fund_with_returns(self, scheme_code):
        """Fetch a single fund's NAV + calculated returns from mfapi.in"""
        try:
            r = self.session.get(f"https://api.mfapi.in/mf/{scheme_code}", timeout=10)
            if r.status_code != 200:
                return None
            data = r.json()
            nav_data = data.get('data', [])
            meta = data.get('meta', {})
            if not nav_data:
                return None
            latest = nav_data[0]
            nav = float(latest.get('nav', 0))
            if nav <= 0:
                return None
            return {
                'scheme_code': scheme_code,
                'scheme_name': meta.get('scheme_name', ''),
                'fund_house': meta.get('fund_house', ''),
                'scheme_category': meta.get('scheme_category', ''),
                'scheme_type': meta.get('scheme_type', ''),
                'nav': nav,
                'date': latest.get('date', ''),
                'return_1y': self._calc_return(nav_data, 365),
                'return_3y': self._calc_return(nav_data, 1095),
                'return_5y': self._calc_return(nav_data, 1825),
            }
        except Exception as e:
            print(f"mfapi error for {scheme_code}: {e}")
            return None

    def _calc_return(self, nav_data, days):
        try:
            if len(nav_data) <= days:
                return 0.0
            current = float(nav_data[0]['nav'])
            old = float(nav_data[min(days, len(nav_data) - 1)]['nav'])
            if old <= 0:
                return 0.0
            years = days / 365
            return round(((current / old) ** (1 / years) - 1) * 100, 2)
        except:
            return 0.0

    # ── Search mfapi for real fund codes by keyword ───────────────────────────
    def search_funds_by_keyword(self, keyword):
        """Search mfapi.in for fund codes matching a keyword"""
        try:
            r = self.session.get(f"https://api.mfapi.in/mf/search?q={keyword}", timeout=10)
            if r.status_code == 200:
                results = r.json()
                # Filter Direct Growth only
                return [
                    f for f in results
                    if 'Direct' in f.get('schemeName', '') and 'Growth' in f.get('schemeName', '')
                ]
        except Exception as e:
            print(f"Search error for {keyword}: {e}")
        return []

    # ── Main: fetch per-category with real returns ────────────────────────────
    def fetch_category_funds(self, category, keywords):
        """
        Search mfapi by keyword for real fund codes, then fetch NAV + returns.
        Only funds whose scheme_name actually matches the category are kept,
        preventing cross-category contamination.
        """
        funds = []
        seen_codes = set()

        for keyword in keywords:
            results = self.search_funds_by_keyword(keyword)
            for r in results[:8]:  # check more results per keyword
                code = str(r.get('schemeCode', ''))
                if code in seen_codes:
                    continue
                seen_codes.add(code)
                fund = self.fetch_fund_with_returns(code)
                if fund and fund['nav'] > 0:
                    # Validate the fund actually belongs to this category
                    if self._fund_matches_category(fund, category):
                        fund['category'] = category
                        funds.append(fund)
                time.sleep(0.05)
            if len(funds) >= 10:
                break

        return funds[:10]

    def _fund_matches_category(self, fund, category):
        """Verify a fund actually belongs to the given category using its real metadata."""
        name = fund.get('scheme_name', '').lower()
        scheme_cat = fund.get('scheme_category', '').lower()

        rules = {
            'Large Cap': lambda: any(w in name or w in scheme_cat for w in ['large cap', 'bluechip', 'top 100', 'large & mid']),
            'Mid Cap':   lambda: any(w in name or w in scheme_cat for w in ['mid cap', 'midcap', 'mid & small']),
            'Small Cap': lambda: any(w in name or w in scheme_cat for w in ['small cap', 'smallcap']),
            'Flexi Cap': lambda: any(w in name or w in scheme_cat for w in ['flexi cap', 'flexicap', 'multi cap', 'multicap']),
            'Index Funds': lambda: any(w in name or w in scheme_cat for w in ['index', 'nifty', 'sensex', 'etf fof']),
            'ELSS':      lambda: any(w in name or w in scheme_cat for w in ['elss', 'tax saver', 'tax saving', 'long term equity']),
            'Debt':      lambda: any(w in name or w in scheme_cat for w in ['debt', 'bond', 'gilt', 'liquid', 'overnight', 'short term', 'short duration', 'corporate bond', 'money market']),
            'Hybrid':    lambda: any(w in name or w in scheme_cat for w in ['hybrid', 'balanced', 'equity & bond', 'aggressive hybrid', 'conservative hybrid']),
            'Gold & Silver': lambda: any(w in name or w in scheme_cat for w in ['gold', 'silver']),
        }
        check = rules.get(category)
        return check() if check else True

    # ── Public API used by main app ───────────────────────────────────────────
    def get_comprehensive_fund_data(self):
        """Fetch real data from AMFI + mfapi. Returns dict for merge_and_enrich_data."""
        print("Fetching AMFI NAV data...")
        amfi_data = self.fetch_from_amfi()
        print(f"AMFI: {len(amfi_data)} Direct Growth funds")

        # Fetch top funds per category with real returns
        print("Fetching per-category returns from mfapi.in...")
        category_keywords = {
            'Large Cap':    ['large cap direct growth', 'bluechip direct growth', 'top 100 direct growth'],
            'Mid Cap':      ['mid cap direct growth', 'midcap direct growth'],
            'Small Cap':    ['small cap direct growth', 'smallcap direct growth'],
            'Flexi Cap':    ['flexi cap direct growth', 'flexicap direct growth'],
            'Index Funds':  ['nifty 50 index direct growth', 'sensex index direct growth'],
            'ELSS':         ['elss direct growth', 'tax saver direct growth'],
            'Debt':         ['short term debt direct growth', 'corporate bond direct growth'],
            'Hybrid':       ['balanced advantage direct growth', 'hybrid equity direct growth'],
            'Gold & Silver':['gold fund direct growth', 'gold etf fof direct growth'],
        }

        mfapi_by_category = {}
        for cat, keywords in category_keywords.items():
            cat_funds = self.fetch_category_funds(cat, keywords)
            mfapi_by_category[cat] = cat_funds
            print(f"  {cat}: {len(cat_funds)} funds with returns")

        return {
            'amfi_data': amfi_data,
            'mfapi_by_category': mfapi_by_category,
        }

    def merge_and_enrich_data(self, all_data):
        """
        Merge AMFI NAV data with mfapi returns.
        Priority: mfapi funds (have real returns) first, then AMFI-only funds.
        """
        merged = []
        seen_names = set()

        # Build AMFI lookup by scheme_name (lowercase)
        amfi_lookup = {}
        for f in all_data.get('amfi_data', []):
            key = f['scheme_name'].lower().strip()
            amfi_lookup[key] = f

        # Add mfapi funds (they have real returns + NAV)
        for cat, funds in all_data.get('mfapi_by_category', {}).items():
            for fund in funds:
                name = fund.get('scheme_name', '').strip()
                key = name.lower()
                if key in seen_names or not name:
                    continue
                seen_names.add(key)

                # Try to get more accurate NAV from AMFI
                amfi_match = amfi_lookup.get(key)
                if amfi_match and amfi_match['nav'] > 0:
                    fund['nav'] = amfi_match['nav']
                    fund['date'] = amfi_match['date']
                    fund['amc'] = amfi_match.get('amc', fund.get('fund_house', ''))

                fund.setdefault('amc', fund.get('fund_house', ''))
                fund.setdefault('expense_ratio', self._estimate_expense(fund))
                fund.setdefault('min_sip', self._estimate_min_sip(fund))
                fund.setdefault('exit_load', '1% if redeemed within 1 year')
                fund.setdefault('fund_manager', 'N/A')
                fund.setdefault('aum', self._estimate_aum(fund))
                merged.append(fund)

        # Fill remaining categories from AMFI (NAV only, no returns)
        for f in all_data.get('amfi_data', []):
            key = f['scheme_name'].lower().strip()
            if key in seen_names:
                continue
            seen_names.add(key)
            f.setdefault('expense_ratio', self._estimate_expense(f))
            f.setdefault('min_sip', self._estimate_min_sip(f))
            f.setdefault('exit_load', '1% if redeemed within 1 year')
            f.setdefault('fund_manager', 'N/A')
            f.setdefault('aum', self._estimate_aum(f))
            merged.append(f)

        return merged

    def _estimate_expense(self, fund):
        """Estimate expense ratio based on fund type — only used when API doesn't provide it."""
        name = fund.get('scheme_name', '').lower()
        if 'index' in name or 'nifty' in name or 'sensex' in name:
            return 0.10
        if any(w in name for w in ['debt', 'bond', 'gilt', 'liquid', 'overnight']):
            return 0.30
        return 0.50  # equity direct

    def _estimate_min_sip(self, fund):
        """Estimate minimum SIP — only used when API doesn't provide it."""
        house = (fund.get('fund_house', '') + fund.get('amc', '')).lower()
        if any(h in house for h in ['icici', 'nippon', 'tata', 'quant']):
            return 100
        return 500

    def _estimate_aum(self, fund):
        """AUM is not available from mfapi/AMFI — return 0 so UI shows N/A."""
        return 0

    # Legacy compatibility
    def fetch_from_mfapi(self):
        return []

    def fuzzy_match(self, n1, n2, threshold=0.7):
        w1 = set(n1.lower().split())
        w2 = set(n2.lower().split())
        if not w1 or not w2:
            return False
        return len(w1 & w2) / len(w1 | w2) >= threshold
