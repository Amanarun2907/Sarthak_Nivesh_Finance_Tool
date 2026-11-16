# सार्थक निवेश - Data Collection Module
# Handles all data sources: Yahoo Finance, Alpha Vantage, News RSS, Web Scraping

import yfinance as yf
import pandas as pd
import requests
import feedparser
from alpha_vantage.timeseries import TimeSeries
from newsapi import NewsApiClient
import sqlite3
from datetime import datetime, timedelta
import time
from config import *

class DataCollector:
    def __init__(self):
        self.alpha_vantage = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        self.news_api = NewsApiClient(api_key=NEWS_API_KEY)
        self.setup_database()
        
    def setup_database(self):
        """Initialize SQLite database with required tables"""
        import os
        os.makedirs(DATA_FOLDER, exist_ok=True)
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Stock prices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                date DATE,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                adj_close REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # News articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                url TEXT UNIQUE,
                source TEXT,
                published_at TIMESTAMP,
                sentiment_score REAL,
                is_fake_news BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # IPO data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ipo_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                symbol TEXT,
                listing_date DATE,
                issue_price REAL,
                listing_price REAL,
                current_price REAL,
                performance_30d REAL,
                performance_60d REAL,
                performance_90d REAL,
                sentiment_score REAL,
                recommendation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User portfolio table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                buy_price REAL NOT NULL,
                buy_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                symbol TEXT,
                direction TEXT,
                target_price REAL,
                keyword TEXT,
                threshold REAL,
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Alert events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alert_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER,
                event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    def collect_stock_data(self, symbol):
        """Collect historical and current stock data"""
        try:
            # Yahoo Finance data (Primary source - Free & Unlimited)
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(start=START_DATE, end=END_DATE)
            
            if hist_data.empty:
                print(f"❌ No data found for {symbol}")
                return None
                
            # Store in database
            conn = sqlite3.connect(DATABASE_PATH)
            
            for date, row in hist_data.iterrows():
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_prices 
                    (symbol, date, open, high, low, close, volume, adj_close)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (symbol, date.date(), row['Open'], row['High'], 
                      row['Low'], row['Close'], row['Volume'], row['Close']))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Collected data for {symbol}: {len(hist_data)} records")
            return hist_data
            
        except Exception as e:
            print(f"❌ Error collecting data for {symbol}: {str(e)}")
            return None
    
    def collect_all_stocks(self):
        """Collect data for all configured stocks"""
        print(f"🚀 Starting data collection for {len(STOCK_SYMBOLS)} stocks...")
        
        for symbol, name in STOCK_SYMBOLS.items():
            print(f"📊 Collecting data for {name} ({symbol})")
            self.collect_stock_data(symbol)
            time.sleep(1)  # Rate limiting
            
        print("✅ Stock data collection completed!")
    
    def collect_news_data(self):
        """Collect news from RSS feeds and NewsAPI"""
        print("📰 Collecting news data...")
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # RSS Feeds (Free, No limits)
        for source_name, rss_url in NEWS_SOURCES.items():
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:10]:  # Latest 10 articles per source
                    cursor.execute('''
                        INSERT OR IGNORE INTO news_articles 
                        (title, description, url, source, published_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        entry.title,
                        entry.get('description', ''),
                        entry.link,
                        source_name,
                        datetime.now()
                    ))
                
                print(f"✅ Collected news from {source_name}")
                
            except Exception as e:
                print(f"❌ Error collecting from {source_name}: {str(e)}")
        
        # NewsAPI (1000 calls/day limit)
        try:
            # Indian stock market news
            articles = self.news_api.get_everything(
                q='indian stock market OR NSE OR BSE',
                language='en',
                sort_by='publishedAt',
                page_size=20
            )
            
            for article in articles['articles']:
                cursor.execute('''
                    INSERT OR IGNORE INTO news_articles 
                    (title, description, url, source, published_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    article['title'],
                    article['description'],
                    article['url'],
                    'newsapi',
                    article['publishedAt']
                ))
            
            print("✅ Collected news from NewsAPI")
            
        except Exception as e:
            print(f"❌ Error with NewsAPI: {str(e)}")
        
        conn.commit()
        conn.close()
        print("✅ News data collection completed!")
    
    def get_stock_data(self, symbol, days=30):
        """Retrieve stock data from database"""
        conn = sqlite3.connect(DATABASE_PATH)
        
        query = '''
            SELECT * FROM stock_prices 
            WHERE symbol = ? 
            ORDER BY date DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(symbol, days))
        conn.close()
        
        return df
    
    def get_latest_news(self, limit=50):
        """Retrieve latest news from database"""
        conn = sqlite3.connect(DATABASE_PATH)
        
        query = '''
            SELECT * FROM news_articles 
            ORDER BY published_at DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        return df

# Test the data collector
if __name__ == "__main__":
    print("🚀 Testing Data Collector for सार्थक निवेश")
    
    collector = DataCollector()
    
    # Test with one stock first
    print("📊 Testing with RELIANCE stock...")
    data = collector.collect_stock_data('RELIANCE.NS')
    
    if data is not None:
        print(f"✅ Successfully collected {len(data)} records")
        print(data.tail())
    
    # Test news collection
    print("📰 Testing news collection...")
    collector.collect_news_data()
    
    print("✅ Data Collector test completed!")
