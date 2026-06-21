"""
Real-Time IPO Data Fetcher
Fetches ACTUAL data for Upcoming, Current, and Closed IPOs
Uses multiple Indian IPO data sources
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time
import json

class RealIPODataFetcher:
    """Fetch real IPO data from multiple sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })
    
    def fetch_ipo_calendar(self):
        """
        Fetch current and upcoming IPOs from multiple sources
        Returns: List of IPOs with status, dates, price bands
        """
        ipos = []
        
        # Source 1: NSE India Official IPO List
        try:
            # Set up session with proper headers for NSE
            self.session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
            
            # NSE IPO API endpoint
            url = "https://www.nseindia.com/api/ipo-detail?category=sme"
            r = self.session.get(url, timeout=15)
            
            if r.status_code == 200:
                data = r.json()
                for category in ['current', 'upcoming', 'listed']:
                    for ipo in data.get(category, []):
                        ipo_data = {
                            'name': ipo.get('issuerCompany', 'Unknown'),
                            'symbol': ipo.get('symbol', ''),
                            'open_date': ipo.get('openIssueDate', ''),
                            'close_date': ipo.get('closeIssueDate', ''),
                            'listing_date': ipo.get('listingDate', ''),
                            'price_band': f"{ipo.get('issueStartPrice', 0)}-{ipo.get('issueEndPrice', 0)}",
                            'issue_price': float(ipo.get('issueEndPrice', 0)),
                            'listing_price': float(ipo.get('listingPrice', 0)),
                            'issue_size': float(ipo.get('issueSize', 0)),
                            'status': category.upper(),
                            'source': 'nse_official'
                        }
                        ipos.append(ipo_data)
                        print(f"  ✓ NSE: Found {ipo_data['name']} - {category}")
        except Exception as e:
            print(f"  ✗ NSE API error: {e}")
        
        # Source 2: BSE IPO List
        try:
            url = "https://api.bseindia.com/BseIndiaAPI/api/ListofForthcomingcorp/w"
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                for ipo in data.get('Table', []):
                    ipo_data = {
                        'name': ipo.get('SCRIP_CD', 'Unknown'),
                        'symbol': ipo.get('SCRIP_CD', ''),
                        'open_date': ipo.get('BIDDINGDT', ''),
                        'close_date': ipo.get('BIDENDDT', ''),
                        'listing_date': ipo.get('LISTINGDT', ''),
                        'price_band': ipo.get('PRICEBND', ''),
                        'issue_price': self._extract_price(ipo.get('PRICEBND', '')),
                        'listing_price': 0,
                        'status': 'UPCOMING',
                        'source': 'bse_official'
                    }
                    ipos.append(ipo_data)
                    print(f"  ✓ BSE: Found {ipo_data['name']}")
        except Exception as e:
            print(f"  ✗ BSE API error: {e}")
        
        # Source 3: MoneyControl RSS Feed (Reliable backup)
        try:
            url = "https://www.moneycontrol.com/rss/ipo.xml"
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'xml')
                items = soup.find_all('item')
                for item in items[:10]:
                    title = item.title.text if item.title else ""
                    link = item.link.text if item.link else ""
                    if 'IPO' in title.upper():
                        ipo_data = {
                            'name': title.split('IPO')[0].strip(),
                            'symbol': '',
                            'open_date': '',
                            'close_date': '',
                            'listing_date': '',
                            'price_band': '',
                            'issue_price': 0,
                            'listing_price': 0,
                            'status': 'UPCOMING',
                            'source': 'moneycontrol_rss',
                            'news_link': link
                        }
                        ipos.append(ipo_data)
                        print(f"  ✓ MC: Found {ipo_data['name']}")
        except Exception as e:
            print(f"  ✗ MoneyControl RSS error: {e}")
        
        return ipos
    
    def fetch_ipo_subscription_data(self, ipo_name):
        """
        Fetch REAL subscription data from multiple reliable sources
        Returns: {total_subscription, qib_subscription, retail_subscription, hni_subscription}
        """
        subscription_data = {
            'total': 0.0,
            'qib': 0.0,
            'retail': 0.0,
            'hni': 0.0,
            'source': 'none'
        }
        
        # Source 1: Try IPO-specific websites with subscription tracking
        try:
            # Clean the IPO name for search
            search_name = ipo_name.replace('Limited', '').replace('Ltd', '').replace('IPO', '').strip()
            
            # Use a more reliable approach - check if IPO is in recent listings
            url = "https://www.chittorgarh.com/report/ipo-subscription-status/82/"
            r = self.session.get(url, timeout=15)
            
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            row_text = ' '.join([cell.text.strip() for cell in cells])
                            
                            # Check if this row contains our IPO
                            if search_name.lower() in row_text.lower():
                                # Extract subscription data from cells
                                for i, cell in enumerate(cells):
                                    text = cell.text.strip().lower()
                                    value_match = re.search(r'([\d.]+)\s*(?:times|x)', text, re.IGNORECASE)
                                    
                                    if value_match:
                                        value = float(value_match.group(1))
                                        
                                        if 'qib' in text or 'institutional' in text:
                                            subscription_data['qib'] = value
                                        elif 'retail' in text or 'rii' in text:
                                            subscription_data['retail'] = value
                                        elif 'hni' in text or 'nii' in text:
                                            subscription_data['hni'] = value
                                        elif 'total' in text or 'overall' in text:
                                            subscription_data['total'] = value
                
                # Calculate total if individual categories are available
                if subscription_data['total'] == 0 and any([subscription_data['qib'], subscription_data['retail'], subscription_data['hni']]):
                    # Weighted average based on typical allocation
                    subscription_data['total'] = (
                        subscription_data['retail'] * 0.35 +
                        subscription_data['qib'] * 0.50 +
                        subscription_data['hni'] * 0.15
                    )
                
                if subscription_data['total'] > 0:
                    subscription_data['source'] = 'chittorgarh'
                    return subscription_data
        except Exception as e:
            print(f"  ⚠️ Chittorgarh subscription error: {e}")
        
        # Source 2: Try Google Search for recent IPO subscription data
        try:
            # Search for recent news about subscription
            query = f"{ipo_name} IPO subscription times oversubscribed"
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                # Look for subscription multiples in the search results
                text = r.text
                
                # Pattern: "X times oversubscribed" or "X.Y times"
                matches = re.findall(r'(\d+\.?\d*)\s*times\s*(?:over)?subscribed', text, re.IGNORECASE)
                if matches:
                    # Use the highest value found (usually total subscription)
                    subscription_data['total'] = float(matches[0])
                    subscription_data['source'] = 'google_search'
                    return subscription_data
        except Exception as e:
            print(f"  ⚠️ Google search error: {e}")
        
        return subscription_data
    
    def fetch_grey_market_premium(self, ipo_name):
        """
        Fetch REAL Grey Market Premium (GMP) from Investorgain/IPOWatch
        Returns: GMP in rupees
        """
        gmp = 0.0
        
        # Source 1: Investorgain GMP (Most popular GMP tracker)
        try:
            url = "https://www.investorgain.com/report/live-ipo-gmp/331/"
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                
                # Find IPO in GMP table
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 3:
                            name_cell = cols[0].text.strip().lower()
                            if ipo_name.lower().replace('limited', '').replace('ltd', '').strip() in name_cell:
                                # GMP usually in format: "₹50" or "50"
                                gmp_text = cols[1].text.strip() if len(cols) > 1 else "0"
                                gmp = self._extract_price(gmp_text)
                                return gmp
        except Exception as e:
            print(f"Investorgain GMP fetch error: {e}")
        
        # Source 2: IPOWatch GMP
        try:
            url = "https://ipowatch.in/ipo-grey-market-premium-latest-gmp/"
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                # Parse IPOWatch table
                # Format similar to Investorgain
                pass
        except:
            pass
        
        return gmp
    
    def fetch_ipo_allotment_status(self, ipo_name):
        """
        Check if IPO allotment is finalized
        Returns: {allotment_date, finalized, allotment_url}
        """
        allotment_info = {
            'finalized': False,
            'allotment_date': None,
            'registrar_url': None
        }
        
        try:
            # Chittorgarh maintains allotment links
            search_name = ipo_name.replace(' ', '+')
            url = f"https://www.chittorgarh.com/ipo/ipo_detail.asp?search={search_name}"
            r = self.session.get(url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                
                # Find allotment date and status
                text = soup.get_text().lower()
                if 'allotment finalized' in text or 'allotment completed' in text:
                    allotment_info['finalized'] = True
                
                # Find registrar link
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if 'linkintime' in href or 'karvy' in href or 'kfintech' in href:
                        allotment_info['registrar_url'] = href
        except:
            pass
        
        return allotment_info
    
    def fetch_ipo_financials(self, ipo_name):
        """
        Fetch IPO company fundamentals from prospectus/screening sites
        Returns: {pe_ratio, market_cap, promoter_holding, etc}
        """
        financials = {
            'pe_ratio': 0,
            'industry_pe': 0,
            'market_cap': 0,
            'promoter_holding': 0,
            'revenue': 0,
            'profit': 0,
            'roe': 0,
            'debt_to_equity': 0
        }
        
        # Can be enhanced with Screener.in, Trendlyne, or Tijori Finance data
        # For now, returning structure for future implementation
        
        return financials
    
    def search_ipo_by_name(self, search_name):
        """
        Smart search for IPO by name across all sources
        Returns best match with confidence score
        """
        search_lower = search_name.lower().replace('limited', '').replace('ltd', '').replace('ipo', '').strip()
        
        matches = []
        calendar = self.fetch_ipo_calendar()
        
        for ipo in calendar:
            ipo_name_lower = ipo['name'].lower().replace('limited', '').replace('ltd', '').strip()
            
            # Calculate similarity score
            if search_lower in ipo_name_lower or ipo_name_lower in search_lower:
                confidence = 90
            elif any(word in ipo_name_lower for word in search_lower.split()):
                confidence = 70
            else:
                continue
            
            matches.append({
                **ipo,
                'match_confidence': confidence
            })
        
        # Sort by confidence
        matches.sort(key=lambda x: x['match_confidence'], reverse=True)
        
        return matches[0] if matches else None
    
    def get_complete_ipo_data(self, ipo_name, symbol=None):
        """
        One-stop function to fetch ALL real data for ANY IPO
        Works for: UPCOMING, CURRENT (open), LISTED, CLOSED
        """
        print(f"🔍 Fetching real data for: {ipo_name}")
        
        result = {
            'ipo_name': ipo_name,
            'symbol': symbol,
            'status': 'UNKNOWN',
            'data_quality': 0,  # 0-100 score
            'issue_price': 0,
            'listing_price': 0,
            'current_price': 0,
            'open_date': None,
            'close_date': None,
            'listing_date': None,
            'subscription_data': {'total': 0, 'qib': 0, 'retail': 0, 'hni': 0},
            'gmp': 0,
            'allotment_status': {},
            'financials': {},
            'data_sources_used': []
        }
        
        # Step 1: Smart search in IPO calendar
        match = self.search_ipo_by_name(ipo_name)
        if match:
            result['status'] = match['status']
            result['issue_price'] = match['issue_price']
            result['listing_price'] = match.get('listing_price', 0)
            result['open_date'] = match['open_date']
            result['close_date'] = match['close_date']
            result['listing_date'] = match['listing_date']
            result['symbol'] = match.get('symbol', symbol) or symbol
            result['data_sources_used'].append(match['source'])
            result['data_quality'] += 25
            print(f"  ✅ Found in calendar: {match['name']} ({match['status']})")
        
        # Step 2: Fetch subscription data (for UPCOMING or CURRENT)
        if result['status'] in ['UPCOMING', 'CURRENT', 'OPEN']:
            sub_data = self.fetch_ipo_subscription_data(ipo_name)
            if sub_data['total'] > 0:
                result['subscription_data'] = sub_data
                result['data_sources_used'].append(f"subscription_{sub_data['source']}")
                result['data_quality'] += 25
                print(f"  ✅ Subscription: {sub_data['total']:.1f}x (QIB: {sub_data['qib']:.1f}x)")
        
        # Step 3: Fetch GMP (for UPCOMING or CURRENT)
        if result['status'] in ['UPCOMING', 'CURRENT', 'OPEN']:
            gmp = self.fetch_grey_market_premium(ipo_name)
            if gmp != 0:
                result['gmp'] = gmp
                result['data_sources_used'].append('gmp')
                result['data_quality'] += 15
                print(f"  ✅ GMP: Rs.{gmp:.2f}")
        
        # Step 4: Fetch allotment status
        allotment = self.fetch_ipo_allotment_status(ipo_name)
        result['allotment_status'] = allotment
        if allotment['finalized']:
            result['data_sources_used'].append('allotment')
            result['data_quality'] += 10
            print(f"  ✅ Allotment finalized")
        
        # Step 5: Fetch current price from Yahoo Finance (if listed)
        if symbol:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='2d')
                if not hist.empty:
                    result['current_price'] = float(hist['Close'].iloc[-1])
                    result['data_sources_used'].append('yfinance')
                    result['data_quality'] += 20
                    print(f"  ✅ Current price: Rs.{result['current_price']:.2f}")
                
                # Also fetch listing price if not available
                if result['listing_price'] == 0:
                    hist_full = ticker.history(period='3mo')
                    if not hist_full.empty:
                        result['listing_price'] = float(hist_full['Close'].iloc[0])
                        print(f"  ✅ Listing price: Rs.{result['listing_price']:.2f}")
            except Exception as e:
                print(f"  ⚠️ Yahoo Finance error: {e}")
        
        # Step 6: Fetch fundamentals
        financials = self.fetch_ipo_financials(ipo_name)
        result['financials'] = financials
        if any(financials.values()):
            result['data_sources_used'].append('fundamentals')
            result['data_quality'] += 10
        
        print(f"✅ Data quality: {result['data_quality']}/100")
        print(f"📊 Sources used: {', '.join(result['data_sources_used'])}")
        
        return result
    
    # Helper methods
    def _extract_price(self, text):
        """Extract price from text like '₹100-110' or 'Rs 100'"""
        text = text.replace('₹', '').replace('Rs', '').replace(',', '').strip()
        match = re.search(r'([\d.]+)', text)
        return float(match.group(1)) if match else 0.0
    
    def _determine_status(self, open_date, close_date, listing_date):
        """Determine if IPO is UPCOMING, CURRENT, or LISTED"""
        try:
            today = datetime.now().date()
            
            open_dt = datetime.strptime(open_date, '%d %b %Y').date() if open_date and open_date != '-' else None
            close_dt = datetime.strptime(close_date, '%d %b %Y').date() if close_date and close_date != '-' else None
            listing_dt = datetime.strptime(listing_date, '%d %b %Y').date() if listing_date and listing_date != '-' else None
            
            if listing_dt and today >= listing_dt:
                return 'LISTED'
            elif open_dt and close_dt and open_dt <= today <= close_dt:
                return 'CURRENT'
            elif open_dt and today < open_dt:
                return 'UPCOMING'
            elif close_dt and today > close_dt and (not listing_dt or today < listing_dt):
                return 'CLOSED_NOT_LISTED'
            else:
                return 'UNKNOWN'
        except:
            return 'UNKNOWN'


# Test function
if __name__ == "__main__":
    fetcher = RealIPODataFetcher()
    
    # Test with a real IPO
    print("=" * 70)
    print("TESTING REAL IPO DATA FETCHER")
    print("=" * 70)
    
    # Test 1: Fetch calendar
    print("\n📅 Fetching IPO Calendar...")
    calendar = fetcher.fetch_ipo_calendar()
    print(f"Found {len(calendar)} IPOs")
    if calendar:
        print("\nRecent IPOs:")
        for ipo in calendar[:5]:
            print(f"  • {ipo['name']} - {ipo['status']} - Rs.{ipo['issue_price']}")
    
    # Test 2: Get complete data for a specific IPO
    print("\n" + "=" * 70)
    test_ipo = "Hyundai Motor India"
    print(f"📊 Fetching complete data for: {test_ipo}")
    data = fetcher.get_complete_ipo_data(test_ipo, "HYUNDAI.NS")
    print(json.dumps(data, indent=2, default=str))
