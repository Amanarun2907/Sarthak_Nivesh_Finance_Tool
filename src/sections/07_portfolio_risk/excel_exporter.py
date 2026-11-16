# सार्थक निवेश - Excel Exporter (Compatibility Module)
# Simple Excel export functionality for main.py compatibility
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import sqlite3
from datetime import datetime
import os
from config import *

class ExcelExporter:
    def __init__(self):
        os.makedirs('exports', exist_ok=True)
        print("✅ Excel Exporter initialized")
    
    def export_stock_data(self):
        """Export stock data to Excel"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Get latest stock data
            query = '''
                SELECT symbol, date, open, high, low, close, volume
                FROM stock_prices
                ORDER BY symbol, date DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                filename = f"exports/stock_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df.to_excel(filename, index=False)
                return filename
            
            return None
            
        except Exception as e:
            print(f"Error exporting stock data: {str(e)}")
            return None
    
    def export_news_sentiment(self):
        """Export news sentiment to Excel"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            query = '''
                SELECT title, description, source, published_at, sentiment_score, is_fake_news
                FROM news_articles
                ORDER BY published_at DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                filename = f"exports/news_sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df.to_excel(filename, index=False)
                return filename
            
            return None
            
        except Exception as e:
            print(f"Error exporting news sentiment: {str(e)}")
            return None
    
    def export_ipo_analysis(self):
        """Export IPO analysis to Excel"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            try:
                ipo_df = pd.read_sql_query(
                    """
                    SELECT
                        company_name AS Company,
                        symbol AS Symbol,
                        listing_date AS Listing_Date,
                        issue_price AS Issue_Price,
                        listing_price AS Listing_Price,
                        price_day_90 AS Current_Price,
                        performance_30d AS Performance_30D_Percent,
                        performance_60d AS Performance_60D_Percent,
                        performance_90d AS Performance_90D_Percent,
                        overall_sentiment_score AS Sentiment_Score,
                        recommendation AS Recommendation,
                        confidence_score AS Confidence_Score,
                        volume_day_30_avg AS Volume_Analysis,
                        retail_sentiment_score AS Retail_Sentiment,
                        last_updated AS Last_Updated
                    FROM ipo_intelligence
                    ORDER BY listing_date DESC
                    """,
                    conn,
                )
            finally:
                conn.close()

            if ipo_df.empty:
                return None

            filename = f"exports/ipo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            ipo_df.to_excel(filename, index=False)
            return filename
            
        except Exception as e:
            print(f"Error exporting IPO analysis: {str(e)}")
            return None
    
    def export_daily_report(self):
        """Export daily market report"""
        try:
            report_data = pd.DataFrame({
                'Report': ['Daily Market Report'],
                'Generated': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Status': ['Phase 2 Complete']
            })
            
            filename = f"exports/daily_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            report_data.to_excel(filename, index=False)
            return filename
            
        except Exception as e:
            print(f"Error exporting daily report: {str(e)}")
            return None
    
    def export_all_data(self):
        """Export all data to Excel files"""
        exported_files = []
        
        # Export stock data
        stock_file = self.export_stock_data()
        if stock_file:
            exported_files.append(stock_file)
        
        # Export news sentiment
        news_file = self.export_news_sentiment()
        if news_file:
            exported_files.append(news_file)
        
        # Export IPO analysis
        ipo_file = self.export_ipo_analysis()
        if ipo_file:
            exported_files.append(ipo_file)
        
        # Export daily report
        report_file = self.export_daily_report()
        if report_file:
            exported_files.append(report_file)
        
        return exported_files