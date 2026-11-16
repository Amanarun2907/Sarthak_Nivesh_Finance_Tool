"""
Real-Time Data Fetcher for IPO Intelligence
============================================
Fetches live news, sentiment, and regulatory filings from free sources.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import feedparser
import re
from typing import List, Dict, Optional
import time


class RealTimeDataFetcher:
    """Fetches real-time IPO data from free sources."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.news_cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def fetch_live_news(self, company_name: str, symbol: str) -> List[Dict]:
        """
        Fetch live news from multiple free sources.
        Sources: Google News RSS, Economic Times RSS, MoneyControl RSS
        """
        cache_key = f"{company_name}_{symbol}"
        now = time.time()
        
        # Check cache
        if cache_key in self.news_cache:
            cached_data, cached_time = self.news_cache[cache_key]
            if now - cached_time < self.cache_duration:
                return cached_data
        
        all_news = []
        
        # 1. Google News RSS
        try:
            import urllib.parse
            query = urllib.parse.quote(f"{company_name} IPO")
            google_feed = feedparser.parse(
                f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            )
            for entry in google_feed.entries[:10]:
                all_news.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', ''),
                    'source': 'Google News',
                    'snippet': entry.get('summary', '')[:200]
                })
        except Exception as e:
            print(f"Google News fetch error: {e}")
        
        # 2. Economic Times RSS
        try:
            et_feed = feedparser.parse(
                "https://economictimes.indiatimes.com/markets/ipos/fpo/rssfeeds/12968048.cms"
            )
            for entry in et_feed.entries[:10]:
                if company_name.lower() in entry.title.lower() or symbol.lower() in entry.title.lower():
                    all_news.append({
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.get('published', ''),
                        'source': 'Economic Times',
                        'snippet': entry.get('summary', '')[:200]
                    })
        except Exception as e:
            print(f"Economic Times fetch error: {e}")
        
        # 3. MoneyControl web scraping (IPO section)
        try:
            mc_url = "https://www.moneycontrol.com/ipo/ipo-snapshot"
            response = requests.get(mc_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = soup.find_all('div', class_='article', limit=5)
                for article in articles:
                    title_tag = article.find('a')
                    if title_tag and (company_name.lower() in title_tag.text.lower() or 
                                     symbol.lower() in title_tag.text.lower()):
                        all_news.append({
                            'title': title_tag.text.strip(),
                            'link': title_tag.get('href', ''),
                            'published': datetime.now().isoformat(),
                            'source': 'MoneyControl',
                            'snippet': ''
                        })
        except Exception as e:
            print(f"MoneyControl scraping error: {e}")
        
        # Cache results
        self.news_cache[cache_key] = (all_news, now)
        
        return all_news
    
    def fetch_social_sentiment(self, company_name: str, symbol: str) -> Dict:
        """
        Fetch social media sentiment from free sources.
        Sources: Reddit (via JSON API), Twitter alternative feeds
        """
        sentiment_data = {
            'overall_score': 0.0,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'total_mentions': 0,
            'sources': []
        }
        
        # 1. Reddit JSON API (no auth required)
        try:
            import urllib.parse
            subreddits = ['IndianStockMarket', 'IndiaInvestments', 'StockMarket', 'investing', 'stocks']
            
            # URL encode company name for search
            encoded_name = urllib.parse.quote(company_name)
            
            for subreddit in subreddits:
                # Try multiple search queries to increase hit rate
                search_queries = [
                    f"{encoded_name}+IPO",
                    f"{encoded_name}",
                    symbol if symbol else ""
                ]
                
                for query in search_queries:
                    if not query:
                        continue
                        
                    # Use Reddit JSON API with proper headers
                    url = f"https://www.reddit.com/r/{subreddit}/search.json"
                    params = {
                        'q': query,
                        'limit': 25,
                        'sort': 'new',
                        't': 'month'  # Last month
                    }
                    
                    # Add User-Agent to avoid rate limiting
                    reddit_headers = self.headers.copy()
                    reddit_headers['User-Agent'] = 'Mozilla/5.0 (IPO Analytics Bot 1.0)'
                    
                    response = requests.get(url, headers=reddit_headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        posts = data.get('data', {}).get('children', [])
                        
                        for post in posts:
                            post_data = post.get('data', {})
                            title = post_data.get('title', '').lower()
                            selftext = post_data.get('selftext', '').lower()
                            
                            # Simple sentiment analysis
                            positive_words = ['bullish', 'buy', 'good', 'strong', 'profit', 'gain', 'success', 'subscribe', 'listing gains', 'oversubscribed']
                            negative_words = ['bearish', 'avoid', 'weak', 'loss', 'risk', 'overpriced', 'fail', 'skip', 'poor', 'expensive']
                            
                            text = f"{title} {selftext}"
                            pos_count = sum(1 for word in positive_words if word in text)
                            neg_count = sum(1 for word in negative_words if word in text)
                            
                            if pos_count > neg_count:
                                sentiment_data['positive_count'] += 1
                            elif neg_count > pos_count:
                                sentiment_data['negative_count'] += 1
                            else:
                                sentiment_data['neutral_count'] += 1
                            
                            sentiment_data['total_mentions'] += 1
                        
                        if len(posts) > 0:
                            sentiment_data['sources'].append({
                                'name': f'Reddit r/{subreddit}',
                                'mentions': len(posts)
                            })
                            break  # Got results, move to next subreddit
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.5)
        except Exception as e:
            print(f"Reddit sentiment fetch error: {e}")
        
        # 2. Calculate overall sentiment score (-1 to +1)
        if sentiment_data['total_mentions'] > 0:
            sentiment_data['overall_score'] = (
                (sentiment_data['positive_count'] - sentiment_data['negative_count']) / 
                sentiment_data['total_mentions']
            )
        else:
            # No mentions found - add informative message
            sentiment_data['message'] = f"No recent social media discussions found for {company_name}. This could indicate low retail interest or limited social media presence."
        
        return sentiment_data
    
    def fetch_regulatory_filings(self, company_name: str) -> List[Dict]:
        """
        Fetch regulatory filings from SEBI/BSE/NSE websites.
        Free access to IPO prospectus links and announcements.
        """
        filings = []
        
        # 1. NSE IPO page scraping
        try:
            nse_url = "https://www.nseindia.com/market-data/forthcoming-issues-ipo"
            response = requests.get(nse_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse IPO table for relevant filings
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if cells and company_name.lower() in ' '.join([c.text for c in cells]).lower():
                            filings.append({
                                'type': 'IPO Listing',
                                'source': 'NSE',
                                'date': datetime.now().isoformat(),
                                'description': 'IPO filing found on NSE'
                            })
        except Exception as e:
            print(f"NSE filing fetch error: {e}")
        
        # 2. BSE Announcements
        try:
            bse_url = "https://www.bseindia.com/markets/PublicIssues/IPOIssues_new.aspx"
            response = requests.get(bse_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse announcements
                links = soup.find_all('a', href=True)
                for link in links:
                    if company_name.lower() in link.text.lower():
                        filings.append({
                            'type': 'Company Announcement',
                            'source': 'BSE',
                            'date': datetime.now().isoformat(),
                            'description': link.text.strip(),
                            'link': link['href']
                        })
        except Exception as e:
            print(f"BSE filing fetch error: {e}")
        
        # 3. IPO Watch (free IPO data aggregator)
        try:
            ipowatch_url = "https://www.ipowatch.in/p/ipo-grey-market-premium-latest-ipo-gmp.html"
            response = requests.get(ipowatch_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        if company_name.lower() in row.text.lower():
                            filings.append({
                                'type': 'GMP Update',
                                'source': 'IPO Watch',
                                'date': datetime.now().isoformat(),
                                'description': 'Grey Market Premium data available'
                            })
        except Exception as e:
            print(f"IPO Watch fetch error: {e}")
        
        return filings
    
    def fetch_current_price(self, symbol: str) -> Optional[float]:
        """
        Fetch current stock price from Yahoo Finance (free, no API key).
        """
        try:
            # Yahoo Finance quote URL
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {'interval': '1d', 'range': '1d'}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                chart = data.get('chart', {})
                result = chart.get('result', [])
                if result:
                    meta = result[0].get('meta', {})
                    current_price = meta.get('regularMarketPrice')
                    return float(current_price) if current_price else None
        except Exception as e:
            print(f"Price fetch error for {symbol}: {e}")
        
        return None
    
    def fetch_market_data(self, symbol: str) -> Dict:
        """
        Fetch comprehensive market data for the symbol.
        """
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {'interval': '1d', 'range': '1mo'}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                chart = data.get('chart', {})
                result = chart.get('result', [])
                
                if result:
                    meta = result[0].get('meta', {})
                    indicators = result[0].get('indicators', {}).get('quote', [{}])[0]
                    
                    return {
                        'current_price': meta.get('regularMarketPrice'),
                        'previous_close': meta.get('previousClose'),
                        'day_high': meta.get('regularMarketDayHigh'),
                        'day_low': meta.get('regularMarketDayLow'),
                        'volume': meta.get('regularMarketVolume'),
                        'market_cap': meta.get('marketCap'),
                        'fifty_day_avg': meta.get('fiftyDayAverage'),
                        'two_hundred_day_avg': meta.get('twoHundredDayAverage'),
                        'high_52_week': indicators.get('high', [None])[-1] if indicators.get('high') else None,
                        'low_52_week': indicators.get('low', [None])[-1] if indicators.get('low') else None,
                    }
        except Exception as e:
            print(f"Market data fetch error for {symbol}: {e}")
        
        return {}


# Singleton instance
_fetcher_instance = None

def get_real_time_fetcher() -> RealTimeDataFetcher:
    """Get or create singleton instance of RealTimeDataFetcher."""
    global _fetcher_instance
    if _fetcher_instance is None:
        _fetcher_instance = RealTimeDataFetcher()
    return _fetcher_instance
