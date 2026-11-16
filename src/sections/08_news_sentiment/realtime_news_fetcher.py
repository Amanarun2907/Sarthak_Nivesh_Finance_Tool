"""
Real-time News & Sentiment Fetcher
Fetches live financial news from multiple sources with sentiment analysis
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
from textblob import TextBlob
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import time

class RealtimeNewsFetcher:
    """Fetch real-time financial news with sentiment analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.vader = SentimentIntensityAnalyzer()
    
    def fetch_from_moneycontrol_rss(self):
        """Fetch news from Moneycontrol RSS feeds"""
        try:
            print("📰 Fetching from Moneycontrol RSS...")
            
            rss_feeds = [
                'https://www.moneycontrol.com/rss/latestnews.xml',
                'https://www.moneycontrol.com/rss/marketreports.xml',
                'https://www.moneycontrol.com/rss/marketoutlook.xml'
            ]
            
            news_items = []
            
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:10]:  # Get top 10 from each feed
                        # Get published date with fallback
                        pub_date = entry.get('published', '')
                        if not pub_date:
                            pub_date = entry.get('updated', datetime.now().strftime('%a, %d %b %Y %H:%M:%S'))
                        
                        news_items.append({
                            'title': entry.title,
                            'link': entry.link,
                            'published': pub_date,
                            'published_parsed': entry.get('published_parsed', None),
                            'summary': entry.get('summary', entry.title),
                            'source': 'MoneyControl',
                            'category': self.categorize_news(entry.title)
                        })
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"Error fetching feed {feed_url}: {e}")
                    continue
            
            print(f"✅ Fetched {len(news_items)} news from Moneycontrol")
            return news_items
            
        except Exception as e:
            print(f"❌ Moneycontrol RSS fetch error: {e}")
        
        return []
    
    def fetch_from_economic_times_rss(self):
        """Fetch news from Economic Times RSS"""
        try:
            print("📰 Fetching from Economic Times RSS...")
            
            rss_feeds = [
                'https://economictimes.indiatimes.com/rssfeedstopstories.cms',
                'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
                'https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms'
            ]
            
            news_items = []
            
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:10]:
                        # Get published date with fallback
                        pub_date = entry.get('published', '')
                        if not pub_date:
                            pub_date = entry.get('updated', datetime.now().strftime('%a, %d %b %Y %H:%M:%S'))
                        
                        news_items.append({
                            'title': entry.title,
                            'link': entry.link,
                            'published': pub_date,
                            'published_parsed': entry.get('published_parsed', None),
                            'summary': entry.get('description', entry.title),
                            'source': 'Economic Times',
                            'category': self.categorize_news(entry.title)
                        })
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error fetching feed {feed_url}: {e}")
                    continue
            
            print(f"✅ Fetched {len(news_items)} news from Economic Times")
            return news_items
            
        except Exception as e:
            print(f"❌ Economic Times RSS fetch error: {e}")
        
        return []
    
    def fetch_from_business_standard_rss(self):
        """Fetch news from Business Standard RSS"""
        try:
            print("📰 Fetching from Business Standard RSS...")
            
            feed_url = 'https://www.business-standard.com/rss/home_page_top_stories.rss'
            
            news_items = []
            
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:15]:
                    # Get published date with fallback
                    pub_date = entry.get('published', '')
                    if not pub_date:
                        pub_date = entry.get('updated', datetime.now().strftime('%a, %d %b %Y %H:%M:%S'))
                    
                    news_items.append({
                        'title': entry.title,
                        'link': entry.link,
                        'published': pub_date,
                        'published_parsed': entry.get('published_parsed', None),
                        'summary': entry.get('summary', entry.title),
                        'source': 'Business Standard',
                        'category': self.categorize_news(entry.title)
                    })
                
            except Exception as e:
                print(f"Error fetching Business Standard: {e}")
            
            print(f"✅ Fetched {len(news_items)} news from Business Standard")
            return news_items
            
        except Exception as e:
            print(f"❌ Business Standard RSS fetch error: {e}")
        
        return []
    
    def categorize_news(self, title):
        """Categorize news based on title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['breaking', 'alert', 'urgent', 'flash']):
            return 'Breaking'
        elif any(word in title_lower for word in ['analysis', 'outlook', 'view', 'opinion']):
            return 'Analysis'
        elif any(word in title_lower for word in ['result', 'earnings', 'profit', 'loss', 'revenue']):
            return 'Earnings'
        elif any(word in title_lower for word in ['ipo', 'listing', 'issue']):
            return 'IPO'
        elif any(word in title_lower for word in ['rbi', 'sebi', 'policy', 'regulation']):
            return 'Regulatory'
        elif any(word in title_lower for word in ['merger', 'acquisition', 'deal']):
            return 'M&A'
        else:
            return 'General'
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using both TextBlob and VADER"""
        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_score = blob.sentiment.polarity
        
        # VADER sentiment
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # Combined score (average)
        combined_score = (textblob_score + vader_compound) / 2
        
        # Classify sentiment
        if combined_score > 0.2:
            sentiment = 'Positive'
            emoji = '🟢'
        elif combined_score < -0.2:
            sentiment = 'Negative'
            emoji = '🔴'
        else:
            sentiment = 'Neutral'
            emoji = '🟡'
        
        return {
            'score': combined_score,
            'sentiment': sentiment,
            'emoji': emoji,
            'textblob': textblob_score,
            'vader': vader_compound,
            'confidence': abs(combined_score)
        }
    
    def extract_stock_mentions(self, text):
        """Extract stock/company mentions from text"""
        # Common Indian company names and stock symbols
        companies = {
            'reliance': 'RELIANCE.NS',
            'tcs': 'TCS.NS',
            'infosys': 'INFY.NS',
            'hdfc': 'HDFCBANK.NS',
            'icici': 'ICICIBANK.NS',
            'sbi': 'SBIN.NS',
            'wipro': 'WIPRO.NS',
            'bharti': 'BHARTIARTL.NS',
            'itc': 'ITC.NS',
            'maruti': 'MARUTI.NS',
            'tata': 'TATAMOTORS.NS',
            'adani': 'ADANIPORTS.NS',
            'bajaj': 'BAJFINANCE.NS',
            'axis': 'AXISBANK.NS',
            'kotak': 'KOTAKBANK.NS'
        }
        
        text_lower = text.lower()
        mentioned_stocks = []
        
        for company, symbol in companies.items():
            if company in text_lower:
                mentioned_stocks.append(symbol)
        
        return mentioned_stocks
    
    def calculate_news_impact_score(self, news_item):
        """Calculate impact score based on sentiment, source credibility, and recency"""
        sentiment_score = abs(news_item.get('sentiment_analysis', {}).get('score', 0))
        
        # Source credibility weights
        source_weights = {
            'Economic Times': 1.0,
            'MoneyControl': 0.95,
            'Business Standard': 0.9,
            'LiveMint': 0.85,
            'default': 0.7
        }
        
        source_weight = source_weights.get(news_item.get('source', ''), source_weights['default'])
        
        # Recency weight (newer = higher impact)
        try:
            pub_date = datetime.strptime(news_item.get('published', ''), '%a, %d %b %Y %H:%M:%S')
            hours_old = (datetime.now() - pub_date).total_seconds() / 3600
            recency_weight = max(0.5, 1 - (hours_old / 48))  # Decay over 48 hours
        except:
            recency_weight = 0.7
        
        # Category weight
        category_weights = {
            'Breaking': 1.0,
            'Earnings': 0.9,
            'Regulatory': 0.85,
            'M&A': 0.8,
            'Analysis': 0.6,
            'General': 0.5
        }
        
        category_weight = category_weights.get(news_item.get('category', 'General'), 0.5)
        
        # Calculate final impact score (0-100)
        impact_score = (sentiment_score * 40 + source_weight * 30 + recency_weight * 20 + category_weight * 10)
        
        return round(impact_score, 2)
    
    def get_trending_topics(self, news_items):
        """Extract trending topics from news"""
        # Common financial keywords
        keywords = {}
        
        for news in news_items:
            text = (news.get('title', '') + ' ' + news.get('summary', '')).lower()
            
            # Extract important words (excluding common words)
            words = re.findall(r'\b[a-z]{4,}\b', text)
            
            for word in words:
                if word not in ['that', 'this', 'with', 'from', 'have', 'been', 'will', 'said', 'says']:
                    keywords[word] = keywords.get(word, 0) + 1
        
        # Get top 10 trending topics
        trending = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [{'topic': topic, 'count': count} for topic, count in trending]
    
    def get_comprehensive_news(self):
        """Get comprehensive news from all sources with analysis"""
        print("🚀 Starting comprehensive news fetch...")
        
        all_news = []
        
        # Fetch from all sources
        all_news.extend(self.fetch_from_moneycontrol_rss())
        all_news.extend(self.fetch_from_economic_times_rss())
        all_news.extend(self.fetch_from_business_standard_rss())
        
        # Analyze sentiment for each news item
        for news in all_news:
            text = news['title'] + ' ' + news.get('summary', '')
            news['sentiment_analysis'] = self.analyze_sentiment(text)
            news['stock_mentions'] = self.extract_stock_mentions(text)
            news['impact_score'] = self.calculate_news_impact_score(news)
            news['time_ago'] = self.calculate_time_ago(news.get('published', ''))
        
        # Sort by impact score
        all_news = sorted(all_news, key=lambda x: x.get('impact_score', 0), reverse=True)
        
        print(f"✅ Total news fetched and analyzed: {len(all_news)}")
        
        return all_news
    
    def calculate_time_ago(self, published_str):
        """Calculate time ago from published date"""
        try:
            pub_date = datetime.strptime(published_str, '%a, %d %b %Y %H:%M:%S')
            diff = datetime.now() - pub_date
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds >= 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds >= 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        except:
            return "Recently"
    
    def get_sector_sentiment(self, news_items):
        """Calculate sector-wise sentiment from news"""
        sectors = {
            'Banking': ['bank', 'hdfc', 'icici', 'sbi', 'axis', 'kotak', 'finance'],
            'IT': ['tcs', 'infosys', 'wipro', 'tech', 'software', 'it sector'],
            'Pharma': ['pharma', 'drug', 'medicine', 'healthcare', 'hospital'],
            'Auto': ['auto', 'car', 'maruti', 'tata motors', 'vehicle'],
            'FMCG': ['fmcg', 'consumer', 'itc', 'hindustan unilever', 'nestle'],
            'Energy': ['oil', 'gas', 'energy', 'power', 'reliance', 'ongc']
        }
        
        sector_sentiments = {}
        
        for sector, keywords in sectors.items():
            sector_news = []
            
            for news in news_items:
                text = (news.get('title', '') + ' ' + news.get('summary', '')).lower()
                
                if any(keyword in text for keyword in keywords):
                    sector_news.append(news.get('sentiment_analysis', {}).get('score', 0))
            
            if sector_news:
                avg_sentiment = sum(sector_news) / len(sector_news)
                sector_sentiments[sector] = {
                    'score': round(avg_sentiment, 3),
                    'count': len(sector_news)
                }
            else:
                sector_sentiments[sector] = {'score': 0, 'count': 0}
        
        return sector_sentiments


# Test the fetcher
if __name__ == "__main__":
    print("🚀 Testing Real-time News Fetcher...")
    
    fetcher = RealtimeNewsFetcher()
    
    # Test comprehensive news fetch
    print("\n1️⃣ Testing Comprehensive News Fetch...")
    news = fetcher.get_comprehensive_news()
    
    if news:
        print(f"\n✅ Sample News with Analysis:")
        sample = news[0]
        print(f"  Title: {sample['title']}")
        print(f"  Source: {sample['source']}")
        print(f"  Category: {sample['category']}")
        print(f"  Sentiment: {sample['sentiment_analysis']['sentiment']} {sample['sentiment_analysis']['emoji']}")
        print(f"  Score: {sample['sentiment_analysis']['score']:.3f}")
        print(f"  Impact Score: {sample['impact_score']}")
        print(f"  Time: {sample['time_ago']}")
        if sample['stock_mentions']:
            print(f"  Stocks Mentioned: {', '.join(sample['stock_mentions'])}")
    
    # Test trending topics
    print("\n2️⃣ Testing Trending Topics...")
    trending = fetcher.get_trending_topics(news)
    print("✅ Top Trending Topics:")
    for topic in trending[:5]:
        print(f"  {topic['topic']}: {topic['count']} mentions")
    
    # Test sector sentiment
    print("\n3️⃣ Testing Sector Sentiment...")
    sector_sentiment = fetcher.get_sector_sentiment(news)
    print("✅ Sector Sentiment:")
    for sector, data in sector_sentiment.items():
        emoji = '🟢' if data['score'] > 0.1 else '🔴' if data['score'] < -0.1 else '🟡'
        print(f"  {sector}: {data['score']:.3f} {emoji} ({data['count']} news)")
    
    print("\n✅ Real-time News Fetcher test completed!")
