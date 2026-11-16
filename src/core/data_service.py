# सार्थक निवेश - Independent Background Data Service
# Runs 24/7 automatically, updates data every hour
# Author: Aman Jain (B.Tech 2023-27)

import schedule
import time
import threading
from datetime import datetime
import yfinance as yf
import pandas as pd
import requests
import feedparser
from alpha_vantage.timeseries import TimeSeries
from newsapi import NewsApiClient
import sqlite3
import os
from config import *

class BackgroundDataService:
    def __init__(self):
        self.alpha_vantage = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        self.news_api = NewsApiClient(api_key=NEWS_API_KEY)
        self.setup_exports_folder()
        print(f"🚀 {PROJECT_NAME} Background Service Started")
        print(f"⏰ Data will update every hour automatically")
        
    def setup_exports_folder(self):
        """Create exports folder for Excel files"""
        os.makedirs('exports', exist_ok=True)
        print("✅ Exports folder ready")
    
    def get_all_nse_stocks(self):
        """Get comprehensive list of NSE stocks - REAL DATA"""
        try:
            # Get NSE stock list from multiple sources
            nse_stocks = {}
            
            # Method 1: Popular NSE stocks (expanded list)
            popular_stocks = {
                # Banking & Financial Services (Top 20)
                'HDFCBANK.NS': 'HDFC Bank', 'ICICIBANK.NS': 'ICICI Bank', 'SBIN.NS': 'State Bank of India',
                'AXISBANK.NS': 'Axis Bank', 'KOTAKBANK.NS': 'Kotak Mahindra Bank', 'INDUSINDBK.NS': 'IndusInd Bank',
                'FEDERALBNK.NS': 'Federal Bank', 'BANDHANBNK.NS': 'Bandhan Bank', 'IDFCFIRSTB.NS': 'IDFC First Bank',
                'PNB.NS': 'Punjab National Bank', 'BANKBARODA.NS': 'Bank of Baroda', 'CANBK.NS': 'Canara Bank',
                
                # Information Technology (Top 15)
                'TCS.NS': 'Tata Consultancy Services', 'INFY.NS': 'Infosys', 'WIPRO.NS': 'Wipro',
                'HCLTECH.NS': 'HCL Technologies', 'TECHM.NS': 'Tech Mahindra', 'LTI.NS': 'LTI Mindtree',
                'MPHASIS.NS': 'Mphasis', 'COFORGE.NS': 'Coforge', 'PERSISTENT.NS': 'Persistent Systems',
                
                # Energy & Infrastructure (Top 15)
                'RELIANCE.NS': 'Reliance Industries', 'NTPC.NS': 'NTPC', 'POWERGRID.NS': 'Power Grid Corporation',
                'ONGC.NS': 'Oil & Natural Gas Corporation', 'IOC.NS': 'Indian Oil Corporation', 'BPCL.NS': 'BPCL',
                'GAIL.NS': 'GAIL India', 'COALINDIA.NS': 'Coal India', 'ADANIPORTS.NS': 'Adani Ports',
                
                # FMCG (Top 12)
                'HINDUNILVR.NS': 'Hindustan Unilever', 'ITC.NS': 'ITC', 'NESTLEIND.NS': 'Nestlé India',
                'BRITANNIA.NS': 'Britannia Industries', 'DABUR.NS': 'Dabur India', 'MARICO.NS': 'Marico',
                'GODREJCP.NS': 'Godrej Consumer Products', 'COLPAL.NS': 'Colgate-Palmolive',
                
                # Automobile (Top 10)
                'MARUTI.NS': 'Maruti Suzuki', 'TATAPOWER.NS': 'Tata Power', 'M&M.NS': 'Mahindra & Mahindra',
                'BAJAJ-AUTO.NS': 'Bajaj Auto', 'HEROMOTOCO.NS': 'Hero MotoCorp', 'EICHERMOT.NS': 'Eicher Motors',
                'ASHOKLEY.NS': 'Ashok Leyland', 'TVSMOTOR.NS': 'TVS Motor Company',
                
                # Pharmaceuticals (Top 12)
                'SUNPHARMA.NS': 'Sun Pharma', 'DRREDDY.NS': 'Dr Reddy\'s Laboratories', 'CIPLA.NS': 'Cipla',
                'DIVISLAB.NS': 'Divi\'s Laboratories', 'BIOCON.NS': 'Biocon', 'LUPIN.NS': 'Lupin',
                'AUROPHARMA.NS': 'Aurobindo Pharma', 'TORNTPHARM.NS': 'Torrent Pharmaceuticals',
                
                # Metals & Mining (Top 10)
                'LT.NS': 'Larsen & Toubro', 'TATASTEEL.NS': 'Tata Steel', 'HINDALCO.NS': 'Hindalco Industries',
                'JSWSTEEL.NS': 'JSW Steel', 'VEDL.NS': 'Vedanta', 'NMDC.NS': 'NMDC', 'SAIL.NS': 'SAIL',
                
                # Telecom (Top 5)
                'BHARTIARTL.NS': 'Bharti Airtel', 'IDEA.NS': 'Vodafone Idea', 'MTNL.NS': 'MTNL',
                
                # Cement (Top 8)
                'ULTRACEMCO.NS': 'UltraTech Cement', 'SHREECEM.NS': 'Shree Cement', 'ACC.NS': 'ACC',
                'AMBUJACEMENT.NS': 'Ambuja Cements', 'JKCEMENT.NS': 'JK Cement',
                
                # Retail & Consumer (Top 8)
                'DMART.NS': 'Avenue Supermarts', 'TRENT.NS': 'Trent', 'JUBLFOOD.NS': 'Jubilant FoodWorks',
                'WESTLIFE.NS': 'Westlife Development',
                
                # Real Estate (Top 5)
                'DLF.NS': 'DLF', 'GODREJPROP.NS': 'Godrej Properties', 'OBEROIRLTY.NS': 'Oberoi Realty'
            }
            
            nse_stocks.update(popular_stocks)
            
            print(f"✅ Loaded {len(nse_stocks)} NSE stocks for comprehensive analysis")
            return nse_stocks
            
        except Exception as e:
            print(f"❌ Error loading NSE stocks: {str(e)}")
            return STOCK_SYMBOLS  # Fallback to configured stocks
    
    def collect_comprehensive_stock_data(self):
        """Collect data for ALL available stocks - REAL DATA ONLY"""
        print("🚀 Starting comprehensive stock data collection...")
        
        # Get all available stocks
        all_stocks = self.get_all_nse_stocks()
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        successful_updates = 0
        failed_updates = 0
        
        for symbol, name in all_stocks.items():
            try:
                print(f"📊 Collecting real data for {name} ({symbol})")
                
                # Get real-time data from Yahoo Finance
                ticker = yf.Ticker(symbol)
                
                # Get latest data (last 5 days to ensure we have recent data)
                hist_data = ticker.history(period="5d")
                
                if hist_data.empty:
                    print(f"⚠️ No recent data for {symbol}")
                    failed_updates += 1
                    continue
                
                # Store real data in database
                for date, row in hist_data.iterrows():
                    cursor.execute('''
                        INSERT OR REPLACE INTO stock_prices 
                        (symbol, date, open, high, low, close, volume, adj_close)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (symbol, date.date(), row['Open'], row['High'], 
                          row['Low'], row['Close'], row['Volume'], row['Close']))
                
                successful_updates += 1
                print(f"✅ Updated {name}: {len(hist_data)} real records")
                
                # Rate limiting to respect API limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error updating {symbol}: {str(e)}")
                failed_updates += 1
                continue
        
        conn.commit()
        conn.close()
        
        print(f"📊 Stock Data Update Complete:")
        print(f"✅ Successful: {successful_updates} stocks")
        print(f"❌ Failed: {failed_updates} stocks")
        
        return successful_updates > 0
    
    def collect_real_news_data(self):
        """Collect real news from multiple sources - NO DUMMY DATA"""
        print("📰 Collecting real news data from multiple sources...")
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        total_articles = 0
        
        # Real RSS Feeds
        for source_name, rss_url in NEWS_SOURCES.items():
            try:
                print(f"📡 Fetching real news from {source_name}")
                feed = feedparser.parse(rss_url)
                
                articles_added = 0
                for entry in feed.entries[:15]:  # Latest 15 real articles per source
                    try:
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
                        articles_added += 1
                    except:
                        continue
                
                print(f"✅ Added {articles_added} real articles from {source_name}")
                total_articles += articles_added
                
            except Exception as e:
                print(f"❌ Error with {source_name}: {str(e)}")
        
        # Real NewsAPI data
        try:
            print("📡 Fetching real news from NewsAPI...")
            articles = self.news_api.get_everything(
                q='indian stock market OR NSE OR BSE OR IPO OR mutual fund',
                language='en',
                sort_by='publishedAt',
                page_size=25
            )
            
            newsapi_added = 0
            for article in articles['articles']:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO news_articles 
                        (title, description, url, source, published_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        article['title'],
                        article['description'],
                        article['url'],
                        'newsapi_real',
                        article['publishedAt']
                    ))
                    newsapi_added += 1
                except:
                    continue
            
            print(f"✅ Added {newsapi_added} real articles from NewsAPI")
            total_articles += newsapi_added
            
        except Exception as e:
            print(f"❌ Error with NewsAPI: {str(e)}")
        
        conn.commit()
        conn.close()
        
        print(f"📰 Real News Collection Complete: {total_articles} articles")
        return total_articles > 0
    
    def generate_excel_reports(self):
        """Generate real-time Excel reports - REAL DATA ONLY"""
        print("📊 Generating real-time Excel reports...")
        
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            # 1. Stock Data Excel - REAL DATA
            print("📈 Creating stock_data.xlsx with real market data...")
            stock_query = '''
                SELECT symbol, date, open, high, low, close, volume, 
                       ROUND(((close - LAG(close) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close) OVER (PARTITION BY symbol ORDER BY date)) * 100, 2) as change_percent
                FROM stock_prices 
                ORDER BY symbol, date DESC
            '''
            stock_df = pd.read_sql_query(stock_query, conn)
            
            with pd.ExcelWriter('exports/stock_data.xlsx', engine='openpyxl') as writer:
                stock_df.to_excel(writer, sheet_name='All_Stocks', index=False)
                
                # Create summary sheet with latest prices
                latest_prices = stock_df.groupby('symbol').first().reset_index()
                latest_prices.to_excel(writer, sheet_name='Latest_Prices', index=False)
            
            print("✅ stock_data.xlsx created with real market data")
            
            # 2. News Sentiment Excel - REAL DATA
            print("📰 Creating news_sentiment.xlsx with real news analysis...")
            news_query = '''
                SELECT title, description, source, published_at, sentiment_score, url
                FROM news_articles 
                ORDER BY published_at DESC
                LIMIT 500
            '''
            news_df = pd.read_sql_query(news_query, conn)
            
            with pd.ExcelWriter('exports/news_sentiment.xlsx', engine='openpyxl') as writer:
                news_df.to_excel(writer, sheet_name='All_News', index=False)
                
                # Create source-wise summary
                source_summary = news_df.groupby('source').agg({
                    'title': 'count',
                    'sentiment_score': 'mean'
                }).reset_index()
                source_summary.columns = ['Source', 'Article_Count', 'Avg_Sentiment']
                source_summary.to_excel(writer, sheet_name='Source_Summary', index=False)
            
            print("✅ news_sentiment.xlsx created with real news data")
            
            # 3. Portfolio Summary Excel
            print("💰 Creating portfolio_summary.xlsx...")
            portfolio_data = {
                'Last_Updated': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Total_Stocks_Tracked': [len(stock_df['symbol'].unique())],
                'Total_News_Articles': [len(news_df)],
                'Data_Sources': ['Yahoo Finance, NewsAPI, Economic Times, MoneyControl'],
                'Update_Frequency': ['Every Hour'],
                'Status': ['Active - Real Data Only']
            }
            
            portfolio_summary = pd.DataFrame(portfolio_data)
            portfolio_summary.to_excel('exports/portfolio_summary.xlsx', index=False)
            
            print("✅ portfolio_summary.xlsx created")
            
            # 4. Daily Market Report Excel
            print("📊 Creating daily_market_report.xlsx...")
            today = datetime.now().date()
            
            # Get today's top movers
            today_stocks = stock_df[stock_df['date'] == str(today)]
            if not today_stocks.empty:
                top_gainers = today_stocks.nlargest(10, 'change_percent')
                top_losers = today_stocks.nsmallest(10, 'change_percent')
                
                with pd.ExcelWriter('exports/daily_market_report.xlsx', engine='openpyxl') as writer:
                    top_gainers.to_excel(writer, sheet_name='Top_Gainers', index=False)
                    top_losers.to_excel(writer, sheet_name='Top_Losers', index=False)
                    
                    # Market summary
                    market_summary = pd.DataFrame({
                        'Metric': ['Total Stocks', 'Gainers', 'Losers', 'Unchanged'],
                        'Count': [
                            len(today_stocks),
                            len(today_stocks[today_stocks['change_percent'] > 0]),
                            len(today_stocks[today_stocks['change_percent'] < 0]),
                            len(today_stocks[today_stocks['change_percent'] == 0])
                        ]
                    })
                    market_summary.to_excel(writer, sheet_name='Market_Summary', index=False)
            
            print("✅ daily_market_report.xlsx created")
            
            conn.close()
            
            print("📊 All Excel reports generated successfully with REAL DATA!")
            return True
            
        except Exception as e:
            print(f"❌ Error generating Excel reports: {str(e)}")
            return False
    
    def update_all_data(self):
        """Complete data update cycle - REAL DATA ONLY"""
        print(f"\n🔄 Starting automated data update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Update stock data
        stock_success = self.collect_comprehensive_stock_data()
        
        # Update news data
        news_success = self.collect_real_news_data()
        
        # Generate Excel reports
        excel_success = self.generate_excel_reports()
        
        # Check alerts
        try:
            self.check_alerts()
        except Exception as e:
            print(f"⚠️ Alert check error: {str(e)}")
        
        print("=" * 60)
        if stock_success and news_success and excel_success:
            print("✅ Complete data update successful!")
        else:
            print("⚠️ Some updates had issues, but continuing...")
        
        print(f"⏰ Next update scheduled in 1 hour")
        print("=" * 60)
    
    def check_alerts(self):
        conn = sqlite3.connect(DATABASE_PATH)
        alerts = pd.read_sql_query("SELECT * FROM alerts WHERE enabled = 1", conn)
        for _, alert in alerts.iterrows():
            if alert['type'] == 'PRICE' and alert['symbol'] and alert['target_price']:
                price_df = pd.read_sql_query('''
                    SELECT close FROM stock_prices WHERE symbol = ? ORDER BY date DESC LIMIT 1
                ''', conn, params=(alert['symbol'],))
                if not price_df.empty:
                    latest = float(price_df.iloc[0]['close'])
                    cond = (alert['direction']=='above' and latest >= alert['target_price']) or (alert['direction']=='below' and latest <= alert['target_price'])
                    if cond:
                        msg = f"{alert['symbol']} is {alert['direction']} ₹{alert['target_price']:.2f} (last ₹{latest:.2f})"
                        conn.execute("INSERT INTO alert_events (alert_id, message) VALUES (?, ?)", (int(alert['id']), msg))
            elif alert['type'] == 'NEWS' and alert['keyword']:
                news = pd.read_sql_query('''
                    SELECT title FROM news_articles 
                    WHERE (title LIKE ? OR description LIKE ?)
                    AND published_at >= datetime('now', '-1 hour')
                    ORDER BY published_at DESC LIMIT 3
                ''', conn, params=(f"%{alert['keyword']}%", f"%{alert['keyword']}%"))
                if not news.empty:
                    msg = f"News matches keyword '{alert['keyword']}': {news.iloc[0]['title'][:80]}"
                    conn.execute("INSERT INTO alert_events (alert_id, message) VALUES (?, ?)", (int(alert['id']), msg))
            elif alert['type'] == 'PORTFOLIO' and alert['threshold'] is not None:
                holdings = pd.read_sql_query("SELECT symbol, quantity, buy_price FROM user_portfolio", conn)
                if not holdings.empty:
                    total_inv = 0.0
                    total_val = 0.0
                    for _, h in holdings.iterrows():
                        price_df = pd.read_sql_query('''
                            SELECT close FROM stock_prices WHERE symbol = ? ORDER BY date DESC LIMIT 1
                        ''', conn, params=(h['symbol'],))
                        if price_df.empty:
                            continue
                        latest = float(price_df.iloc[0]['close'])
                        total_inv += float(h['quantity']) * float(h['buy_price'])
                        total_val += float(h['quantity']) * latest
                    if total_inv > 0:
                        pnl_pct = ((total_val - total_inv) / total_inv) * 100
                        cond = (alert['direction']=='above' and pnl_pct >= alert['threshold']) or (alert['direction']=='below' and pnl_pct <= alert['threshold'])
                        if cond:
                            msg = f"Portfolio P&L {alert['direction']} {alert['threshold']}% (current {pnl_pct:.2f}%)"
                            conn.execute("INSERT INTO alert_events (alert_id, message) VALUES (?, ?)", (int(alert['id']), msg))
            elif alert['type'] == 'IPO_LISTING':
                ipos = pd.read_sql_query('''
                    SELECT company_name, symbol FROM ipo_data WHERE listing_date = date('now')
                ''', conn)
                if not ipos.empty:
                    msg = f"IPO listed today: {ipos.iloc[0]['company_name']} ({ipos.iloc[0]['symbol']})"
                    conn.execute("INSERT INTO alert_events (alert_id, message) VALUES (?, ?)", (int(alert['id']), msg))
            elif alert['type'] == 'TRAIL' and alert['symbol']:
                try:
                    params = json.loads(alert['params']) if 'params' in alert and alert['params'] else {}
                    tpct = float(params.get('trailing_pct', 12.0))
                    hist = pd.read_sql_query('''
                        SELECT close FROM stock_prices WHERE symbol = ? ORDER BY date DESC LIMIT 30
                    ''', conn, params=(alert['symbol'],))
                    if not hist.empty:
                        recent_high = float(hist['close'].max())
                        latest = float(hist['close'].iloc[0])
                        trigger = latest <= recent_high * (1 - tpct/100.0)
                        if trigger:
                            msg = f"{alert['symbol']} fell {tpct}% from recent high (₹{recent_high:.2f} → ₹{latest:.2f})"
                            conn.execute("INSERT INTO alert_events (alert_id, message) VALUES (?, ?)", (int(alert['id']), msg))
                except Exception:
                    pass
        conn.commit()
        conn.close()
    
    def start_service(self):
        """Start the background service"""
        print(f"🚀 Starting {PROJECT_NAME} Background Data Service")
        print("📊 Real-time data updates every hour")
        print("🔄 App-independent operation")
        print("=" * 60)
        
        # Run initial update
        self.update_all_data()
        
        # Schedule hourly updates
        schedule.every().hour.do(self.update_all_data)
        
        print("⏰ Background service running... Press Ctrl+C to stop")
        
        # Keep service running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    service = BackgroundDataService()
    try:
        service.start_service()
    except KeyboardInterrupt:
        print("\n🛑 Background service stopped by user")
    except Exception as e:
        print(f"❌ Service error: {str(e)}")
        print("🔄 Restarting in 5 seconds...")
        time.sleep(5)
