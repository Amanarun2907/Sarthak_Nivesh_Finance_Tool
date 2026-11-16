"""
Database Manager for Sarthak Nivesh Platform
Stores all real-time data in organized tables
"""

import sqlite3
import pandas as pd
from datetime import datetime
import json

class SarthakNiveshDB:
    """Professional Database Manager for Investment Platform"""
    
    def __init__(self, db_path='data/sarthak_nivesh.db'):
        self.db_path = db_path
        self.create_tables()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Create all necessary tables with proper structure"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table 1: Stock Market Data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            current_price REAL,
            previous_price REAL,
            price_change REAL,
            price_change_pct REAL,
            volume INTEGER,
            market_cap REAL,
            sector TEXT,
            day_high REAL,
            day_low REAL,
            week_52_high REAL,
            week_52_low REAL
        )
        ''')
        
        # Table 2: Sector Performance
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sector_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sector_name TEXT NOT NULL,
            performance_pct REAL,
            stocks_count INTEGER,
            avg_volume REAL,
            market_sentiment TEXT
        )
        ''')
        
        # Table 3: Mutual Fund Data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mutual_funds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            scheme_code TEXT,
            fund_name TEXT NOT NULL,
            category TEXT,
            nav REAL,
            return_1y REAL,
            return_3y REAL,
            return_5y REAL,
            aum REAL,
            expense_ratio REAL,
            risk_level TEXT,
            rating INTEGER
        )
        ''')
        
        # Table 4: IPO Data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ipo_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            company_name TEXT NOT NULL,
            issue_price REAL,
            listing_price REAL,
            current_price REAL,
            listing_gain_pct REAL,
            current_gain_pct REAL,
            issue_size REAL,
            subscription_times REAL,
            listing_date DATE,
            sector TEXT,
            recommendation TEXT
        )
        ''')
        
        # Table 5: Portfolio Holdings
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT DEFAULT 'default_user',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            quantity INTEGER,
            avg_buy_price REAL,
            current_price REAL,
            invested_amount REAL,
            current_value REAL,
            profit_loss REAL,
            profit_loss_pct REAL
        )
        ''')
        
        # Table 6: Market Indices
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_indices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            index_name TEXT NOT NULL,
            index_value REAL,
            change_points REAL,
            change_pct REAL,
            day_high REAL,
            day_low REAL,
            volume REAL
        )
        ''')
        
        # Table 7: News & Sentiment
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            news_title TEXT NOT NULL,
            news_summary TEXT,
            source TEXT,
            category TEXT,
            sentiment_score REAL,
            sentiment_label TEXT,
            related_stocks TEXT,
            url TEXT
        )
        ''')
        
        # Table 8: Volume Analysis
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS volume_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            symbol TEXT NOT NULL,
            stock_name TEXT NOT NULL,
            current_volume INTEGER,
            avg_volume INTEGER,
            volume_ratio REAL,
            price_change_pct REAL,
            alert_level TEXT
        )
        ''')
        
        # Table 9: Correlation Data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS correlation_matrix (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            stock1 TEXT NOT NULL,
            stock2 TEXT NOT NULL,
            correlation_value REAL,
            period TEXT
        )
        ''')
        
        # Table 10: Market Breadth
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_breadth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            total_stocks INTEGER,
            advancing INTEGER,
            declining INTEGER,
            unchanged INTEGER,
            advance_decline_ratio REAL,
            market_sentiment TEXT,
            breadth_strength REAL
        )
        ''')
        
        # Table 11: User Activity Log
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT DEFAULT 'default_user',
            activity_type TEXT,
            activity_details TEXT,
            page_visited TEXT
        )
        ''')
        
        # Table 12: AI Recommendations
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            recommendation_type TEXT,
            symbol TEXT,
            recommendation TEXT,
            confidence_score REAL,
            reasoning TEXT,
            target_price REAL,
            stop_loss REAL
        )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ All database tables created successfully!")
    
    # ==================== INSERT METHODS ====================
    
    def insert_stock_data(self, stock_data):
        """Insert real-time stock data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for stock_name, data in stock_data.items():
            cursor.execute('''
            INSERT INTO stock_data (symbol, stock_name, current_price, previous_price, 
                                   price_change, price_change_pct, volume, market_cap, sector)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('symbol', ''),
                stock_name,
                data.get('price', 0),
                data.get('price', 0) - data.get('change', 0),
                data.get('change', 0),
                data.get('change_pct', 0),
                data.get('volume', 0),
                data.get('market_cap', 0),
                data.get('sector', 'Unknown')
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ Inserted {len(stock_data)} stock records")
    
    def insert_sector_performance(self, sector_data):
        """Insert sector performance data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for sector, performance in sector_data.items():
            sentiment = 'Bullish' if performance > 1 else 'Bearish' if performance < -1 else 'Neutral'
            
            cursor.execute('''
            INSERT INTO sector_performance (sector_name, performance_pct, market_sentiment)
            VALUES (?, ?, ?)
            ''', (sector, performance, sentiment))
        
        conn.commit()
        conn.close()
        print(f"✅ Inserted {len(sector_data)} sector records")
    
    def insert_mutual_fund_data(self, fund_data):
        """Insert mutual fund data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        count = 0
        for category, funds in fund_data.items():
            for fund in funds:
                cursor.execute('''
                INSERT INTO mutual_funds (scheme_code, fund_name, category, nav, 
                                         return_1y, return_3y, return_5y, expense_ratio, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fund.get('scheme_code', ''),
                    fund.get('name', ''),
                    category,
                    fund.get('nav', 0),
                    fund.get('return_1y', 0),
                    fund.get('return_3y', 0),
                    fund.get('return_5y', 0),
                    fund.get('expense_ratio', 0),
                    fund.get('risk', 'Medium')
                ))
                count += 1
        
        conn.commit()
        conn.close()
        print(f"✅ Inserted {count} mutual fund records")
    
    def insert_ipo_data(self, ipo_data):
        """Insert IPO data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO ipo_data (company_name, issue_price, listing_price, current_price,
                             listing_gain_pct, current_gain_pct, issue_size, listing_date,
                             sector, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ipo_data.get('company_name', ''),
            ipo_data.get('issue_price', 0),
            ipo_data.get('listing_price', 0),
            ipo_data.get('current_price', 0),
            ipo_data.get('listing_gain_pct', 0),
            ipo_data.get('current_gain_pct', 0),
            ipo_data.get('issue_size', 0),
            ipo_data.get('listing_date', ''),
            ipo_data.get('sector', ''),
            ipo_data.get('recommendation', '')
        ))
        
        conn.commit()
        conn.close()
        print("✅ Inserted IPO data")
    
    def insert_volume_analysis(self, volume_data):
        """Insert volume analysis data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for data in volume_data:
            cursor.execute('''
            INSERT INTO volume_analysis (symbol, stock_name, current_volume, avg_volume,
                                        volume_ratio, price_change_pct, alert_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('Stock', ''),
                data.get('Stock', ''),
                float(data.get('Volume', '0M').replace('M', '')) * 1e6,
                float(data.get('Avg Volume', '0M').replace('M', '')) * 1e6,
                float(data.get('Volume Ratio', '0x').replace('x', '')),
                float(data.get('Price Change', '0%').replace('%', '')),
                data.get('Alert', 'Normal')
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ Inserted {len(volume_data)} volume analysis records")
    
    def insert_market_breadth(self, breadth_data):
        """Insert market breadth data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO market_breadth (total_stocks, advancing, declining, unchanged,
                                   advance_decline_ratio, market_sentiment, breadth_strength)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            breadth_data.get('total', 0),
            breadth_data.get('advancing', 0),
            breadth_data.get('declining', 0),
            breadth_data.get('unchanged', 0),
            breadth_data.get('ad_ratio', 0),
            breadth_data.get('sentiment', 'Neutral'),
            breadth_data.get('strength', 50)
        ))
        
        conn.commit()
        conn.close()
        print("✅ Inserted market breadth data")
    
    def insert_news_sentiment(self, news_data):
        """Insert news and sentiment data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for news in news_data:
            cursor.execute('''
            INSERT INTO news_sentiment (news_title, news_summary, source, category,
                                       sentiment_score, sentiment_label, related_stocks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                news.get('title', ''),
                news.get('summary', ''),
                news.get('source', ''),
                news.get('category', ''),
                news.get('sentiment_analysis', {}).get('score', 0),
                news.get('sentiment_analysis', {}).get('label', 'Neutral'),
                json.dumps(news.get('related_stocks', []))
            ))
        
        conn.commit()
        conn.close()
        print(f"✅ Inserted {len(news_data)} news records")
    
    def insert_portfolio_holding(self, holding_data):
        """Insert portfolio holding"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO portfolio_holdings (symbol, stock_name, quantity, avg_buy_price,
                                       current_price, invested_amount, current_value,
                                       profit_loss, profit_loss_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            holding_data.get('symbol', ''),
            holding_data.get('name', ''),
            holding_data.get('quantity', 0),
            holding_data.get('avg_price', 0),
            holding_data.get('current_price', 0),
            holding_data.get('invested', 0),
            holding_data.get('current_value', 0),
            holding_data.get('profit_loss', 0),
            holding_data.get('profit_loss_pct', 0)
        ))
        
        conn.commit()
        conn.close()
        print("✅ Inserted portfolio holding")
    
    def log_user_activity(self, activity_type, details, page):
        """Log user activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO user_activity (activity_type, activity_details, page_visited)
        VALUES (?, ?, ?)
        ''', (activity_type, details, page))
        
        conn.commit()
        conn.close()
    
    # ==================== QUERY METHODS ====================
    
    def get_latest_stock_data(self, limit=50):
        """Get latest stock data"""
        conn = self.get_connection()
        df = pd.read_sql_query(f'''
        SELECT * FROM stock_data 
        ORDER BY timestamp DESC 
        LIMIT {limit}
        ''', conn)
        conn.close()
        return df
    
    def get_sector_performance_history(self, sector_name, days=30):
        """Get sector performance history"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
        SELECT * FROM sector_performance 
        WHERE sector_name = ? 
        AND timestamp >= datetime('now', '-' || ? || ' days')
        ORDER BY timestamp DESC
        ''', conn, params=(sector_name, days))
        conn.close()
        return df
    
    def get_portfolio_summary(self):
        """Get portfolio summary"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
        SELECT * FROM portfolio_holdings 
        ORDER BY timestamp DESC
        ''', conn)
        conn.close()
        return df
    
    def get_market_breadth_trend(self, days=7):
        """Get market breadth trend"""
        conn = self.get_connection()
        df = pd.read_sql_query('''
        SELECT * FROM market_breadth 
        WHERE timestamp >= datetime('now', '-' || ? || ' days')
        ORDER BY timestamp DESC
        ''', conn, params=(days,))
        conn.close()
        return df
    
    def get_database_stats(self):
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        tables = ['stock_data', 'sector_performance', 'mutual_funds', 'ipo_data',
                 'portfolio_holdings', 'market_indices', 'news_sentiment',
                 'volume_analysis', 'market_breadth', 'user_activity']
        
        for table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            stats[table] = count
        
        conn.close()
        return stats
    
    def cleanup_old_data(self, days=90):
        """Clean up data older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        tables = ['stock_data', 'sector_performance', 'volume_analysis', 'market_breadth']
        
        for table in tables:
            cursor.execute(f'''
            DELETE FROM {table} 
            WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
        
        conn.commit()
        deleted = cursor.rowcount
        conn.close()
        print(f"✅ Cleaned up {deleted} old records")
        return deleted

# Initialize database
if __name__ == "__main__":
    print("🗄️ Initializing Sarthak Nivesh Database...")
    db = SarthakNiveshDB()
    print("\n📊 Database Statistics:")
    stats = db.get_database_stats()
    for table, count in stats.items():
        print(f"   {table}: {count} records")
    print("\n✅ Database ready!")
