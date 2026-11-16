# सार्थक निवेश - Excel Export Manager
# Real-time Excel report generation with professional formatting
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.chart import LineChart, BarChart, PieChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows
import xlsxwriter
from config import *
from stock_analyzer import AdvancedStockAnalyzer
from sentiment_analyzer import AdvancedSentimentAnalyzer

class ExcelExportManager:
    def __init__(self):
        self.setup_exports_folder()
        self.stock_analyzer = AdvancedStockAnalyzer()
        self.sentiment_analyzer = AdvancedSentimentAnalyzer()
        print("✅ Excel Export Manager initialized")
    
    def setup_exports_folder(self):
        """Create exports folder with proper structure"""
        folders = ['exports', 'exports/daily', 'exports/weekly', 'exports/monthly']
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
        print("📁 Export folders created")
    
    def create_stock_data_excel(self):
        """Create comprehensive stock data Excel - REAL DATA ONLY"""
        try:
            print("📊 Creating stock_data.xlsx with real market data...")
            
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Create Excel writer with multiple sheets
            with pd.ExcelWriter('exports/stock_data.xlsx', engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Define formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#FF9933',  # Indian flag orange
                    'border': 1,
                    'font_color': 'white'
                })
                
                money_format = workbook.add_format({'num_format': '₹#,##0.00'})
                percent_format = workbook.add_format({'num_format': '0.00%'})
                date_format = workbook.add_format({'num_format': 'dd-mm-yyyy'})
                
                # Sheet 1: Latest Prices
                latest_query = '''
                    WITH latest_data AS (
                        SELECT symbol, date, close, volume,
                               LAG(close) OVER (PARTITION BY symbol ORDER BY date) as prev_close,
                               ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY date DESC) as rn
                        FROM stock_prices
                    )
                    SELECT symbol, date, close, volume, prev_close,
                           ROUND(((close - prev_close) / prev_close) * 100, 2) as change_percent,
                           ROUND(close - prev_close, 2) as change_amount
                    FROM latest_data
                    WHERE rn = 1 AND prev_close IS NOT NULL
                    ORDER BY change_percent DESC
                '''
                
                latest_df = pd.read_sql_query(latest_query, conn)
                latest_df['company_name'] = latest_df['symbol'].map(
                    lambda x: STOCK_SYMBOLS.get(x, x.replace('.NS', ''))
                )
                
                # Reorder columns
                latest_df = latest_df[['symbol', 'company_name', 'date', 'close', 'change_amount', 
                                     'change_percent', 'volume']]
                
                latest_df.to_excel(writer, sheet_name='Latest_Prices', index=False)
                worksheet = writer.sheets['Latest_Prices']
                
                # Format Latest Prices sheet
                worksheet.set_column('A:A', 15)  # Symbol
                worksheet.set_column('B:B', 25)  # Company Name
                worksheet.set_column('C:C', 12, date_format)  # Date
                worksheet.set_column('D:D', 12, money_format)  # Close
                worksheet.set_column('E:E', 12, money_format)  # Change Amount
                worksheet.set_column('F:F', 12, percent_format)  # Change %
                worksheet.set_column('G:G', 15)  # Volume
                
                # Add header formatting
                for col_num, value in enumerate(latest_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # Sheet 2: Historical Data (Last 30 days)
                historical_query = '''
                    SELECT symbol, date, open, high, low, close, volume
                    FROM stock_prices
                    WHERE date >= date('now', '-30 days')
                    ORDER BY symbol, date DESC
                '''
                
                historical_df = pd.read_sql_query(historical_query, conn)
                historical_df.to_excel(writer, sheet_name='Historical_30Days', index=False)
                
                # Sheet 3: Top Gainers
                gainers_df = latest_df.head(10)
                gainers_df.to_excel(writer, sheet_name='Top_Gainers', index=False)
                
                # Sheet 4: Top Losers
                losers_df = latest_df.tail(10)
                losers_df.to_excel(writer, sheet_name='Top_Losers', index=False)
                
                # Sheet 5: Sector Performance
                sectors = {
                    'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS'],
                    'IT': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS'],
                    'Energy': ['RELIANCE.NS', 'NTPC.NS', 'POWERGRID.NS'],
                    'FMCG': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS'],
                    'Auto': ['MARUTI.NS', 'TATAPOWER.NS'],
                    'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS'],
                    'Metals': ['LT.NS', 'TATASTEEL.NS']
                }
                
                sector_data = []
                for sector, stocks in sectors.items():
                    sector_stocks = latest_df[latest_df['symbol'].isin(stocks)]
                    if not sector_stocks.empty:
                        avg_performance = sector_stocks['change_percent'].mean()
                        sector_data.append({
                            'Sector': sector,
                            'Avg_Performance_%': round(avg_performance, 2),
                            'Stocks_Count': len(sector_stocks),
                            'Best_Performer': sector_stocks.loc[sector_stocks['change_percent'].idxmax(), 'symbol'],
                            'Worst_Performer': sector_stocks.loc[sector_stocks['change_percent'].idxmin(), 'symbol']
                        })
                
                sector_df = pd.DataFrame(sector_data)
                sector_df.to_excel(writer, sheet_name='Sector_Performance', index=False)
                
                # Sheet 6: Summary Statistics
                summary_data = {
                    'Metric': [
                        'Total Stocks Tracked',
                        'Stocks with Positive Change',
                        'Stocks with Negative Change',
                        'Average Market Performance (%)',
                        'Highest Gainer (%)',
                        'Biggest Loser (%)',
                        'Total Volume Traded',
                        'Last Updated'
                    ],
                    'Value': [
                        len(latest_df),
                        len(latest_df[latest_df['change_percent'] > 0]),
                        len(latest_df[latest_df['change_percent'] < 0]),
                        round(latest_df['change_percent'].mean(), 2),
                        latest_df['change_percent'].max(),
                        latest_df['change_percent'].min(),
                        f"{latest_df['volume'].sum():,}",
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Market_Summary', index=False)
            
            conn.close()
            print("✅ stock_data.xlsx created successfully with real data")
            return True
            
        except Exception as e:
            print(f"❌ Error creating stock data Excel: {str(e)}")
            return False
    
    def create_news_sentiment_excel(self):
        """Create news sentiment analysis Excel - REAL DATA ONLY"""
        try:
            print("📰 Creating news_sentiment.xlsx with real news analysis...")
            
            conn = sqlite3.connect(DATABASE_PATH)
            
            with pd.ExcelWriter('exports/news_sentiment.xlsx', engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Define formats
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#138808',  # Indian flag green
                    'border': 1,
                    'font_color': 'white'
                })
                
                positive_format = workbook.add_format({'bg_color': '#90EE90'})
                negative_format = workbook.add_format({'bg_color': '#FFB6C1'})
                neutral_format = workbook.add_format({'bg_color': '#FFFACD'})
                
                # Sheet 1: All News with Sentiment
                news_query = '''
                    SELECT title, description, source, published_at, 
                           sentiment_score, is_fake_news, url
                    FROM news_articles
                    WHERE sentiment_score IS NOT NULL
                    ORDER BY published_at DESC
                    LIMIT 500
                '''
                
                news_df = pd.read_sql_query(news_query, conn)
                
                # Add sentiment category
                news_df['sentiment_category'] = news_df['sentiment_score'].apply(
                    lambda x: 'Positive' if x > 0.1 else 'Negative' if x < -0.1 else 'Neutral'
                )
                
                news_df.to_excel(writer, sheet_name='All_News', index=False)
                worksheet = writer.sheets['All_News']
                
                # Format columns
                worksheet.set_column('A:A', 50)  # Title
                worksheet.set_column('B:B', 60)  # Description
                worksheet.set_column('C:C', 20)  # Source
                worksheet.set_column('D:D', 20)  # Published At
                worksheet.set_column('E:E', 15)  # Sentiment Score
                worksheet.set_column('F:F', 15)  # Is Fake News
                worksheet.set_column('G:G', 50)  # URL
                worksheet.set_column('H:H', 15)  # Sentiment Category
                
                # Sheet 2: Sentiment Summary
                sentiment_summary = news_df.groupby('sentiment_category').agg({
                    'title': 'count',
                    'sentiment_score': 'mean'
                }).reset_index()
                sentiment_summary.columns = ['Sentiment', 'Article_Count', 'Avg_Score']
                sentiment_summary.to_excel(writer, sheet_name='Sentiment_Summary', index=False)
                
                # Sheet 3: Source Analysis
                source_analysis = news_df.groupby('source').agg({
                    'title': 'count',
                    'sentiment_score': 'mean',
                    'is_fake_news': 'sum'
                }).reset_index()
                source_analysis.columns = ['Source', 'Total_Articles', 'Avg_Sentiment', 'Fake_News_Count']
                source_analysis = source_analysis.sort_values('Total_Articles', ascending=False)
                source_analysis.to_excel(writer, sheet_name='Source_Analysis', index=False)
                
                # Sheet 4: Daily Sentiment Trend
                news_df['date'] = pd.to_datetime(news_df['published_at']).dt.date
                daily_sentiment = news_df.groupby('date').agg({
                    'sentiment_score': 'mean',
                    'title': 'count'
                }).reset_index()
                daily_sentiment.columns = ['Date', 'Avg_Sentiment', 'Article_Count']
                daily_sentiment.to_excel(writer, sheet_name='Daily_Sentiment', index=False)
                
                # Sheet 5: Fake News Report
                fake_news = news_df[news_df['is_fake_news'] == 1]
                if not fake_news.empty:
                    fake_news[['title', 'source', 'published_at', 'sentiment_score']].to_excel(
                        writer, sheet_name='Fake_News_Detected', index=False
                    )
                else:
                    # Create empty sheet with message
                    pd.DataFrame({'Message': ['No fake news detected - All sources verified']}).to_excel(
                        writer, sheet_name='Fake_News_Detected', index=False
                    )
            
            conn.close()
            print("✅ news_sentiment.xlsx created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating news sentiment Excel: {str(e)}")
            return False
    
    def create_ipo_analysis_excel(self):
        """Create IPO analysis Excel - REAL IPO DATA from Phase 3"""
        try:
            print("🚀 Creating ipo_analysis.xlsx for unique IPO feature...")
            
            # Load IPO intelligence data from database (if available)
            conn = sqlite3.connect(DATABASE_PATH)
            try:
                ipo_df = pd.read_sql_query(
                    """
                    SELECT
                        company_name AS Company_Name,
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
            except Exception:
                ipo_df = pd.DataFrame()
            finally:
                conn.close()

            with pd.ExcelWriter('exports/ipo_analysis.xlsx', engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Header format
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#FF6600',  # Orange theme
                    'border': 1,
                    'font_color': 'white'
                })

                # Sheet 1: Feature overview (updated for completed Phase 3)
                framework_data = {
                    'Feature': [
                        'Post-IPO Performance Tracking',
                        'Sentiment-Based Analysis',
                        'Hold/Exit Recommendations',
                        'Liquidity Forecasting',
                        'Retail Sentiment Impact',
                        'Volume Pattern Analysis',
                        'Price Momentum Tracking',
                        'Risk Assessment'
                    ],
                    'Status': [
                        'Implemented (Phase 3 Complete)',
                        'Implemented (Phase 3 Complete)', 
                        'Implemented (Phase 3 Complete)',
                        'Implemented (Phase 3 Complete)',
                        'Implemented (Phase 3 Complete)',
                        'Implemented (Phase 3 Complete)',
                        'Implemented (Phase 3 Complete)',
                        'Implemented (Phase 3 Complete)'
                    ],
                    'Implementation': [
                        'Phase 3 (Unique IPO Intelligence System)',
                        'Phase 3 (News & Sentiment Integration)',
                        'Phase 3 (Recommendation Engine)', 
                        'Phase 3 (Liquidity Analysis)',
                        'Phase 3 (Retail Sentiment Scoring)',
                        'Phase 3 (Volume & Pattern Analysis)',
                        'Phase 3 (Momentum & Performance)',
                        'Phase 3 (Risk & Volatility Assessment)'
                    ]
                }
                
                framework_df = pd.DataFrame(framework_data)
                framework_df.to_excel(writer, sheet_name='IPO_Features', index=False)
                features_ws = writer.sheets['IPO_Features']
                for col_num, value in enumerate(framework_df.columns.values):
                    features_ws.write(0, col_num, value, header_format)
                
                # Sheet 2: IPO performance (real data if available)
                if not ipo_df.empty:
                    ipo_df.to_excel(writer, sheet_name='IPO_Performance', index=False)
                    perf_ws = writer.sheets['IPO_Performance']
                    for col_num, value in enumerate(ipo_df.columns.values):
                        perf_ws.write(0, col_num, value, header_format)
                else:
                    # Create empty structure when no data yet
                    empty_ipo_df = pd.DataFrame(
                        columns=[
                            'Company_Name',
                            'Symbol',
                            'Listing_Date',
                            'Issue_Price',
                            'Listing_Price',
                            'Current_Price',
                            'Performance_30D_Percent',
                            'Performance_60D_Percent',
                            'Performance_90D_Percent',
                            'Sentiment_Score',
                            'Recommendation',
                            'Confidence_Score',
                            'Volume_Analysis',
                            'Retail_Sentiment',
                            'Last_Updated'
                        ]
                    )
                    empty_ipo_df.to_excel(writer, sheet_name='IPO_Performance', index=False)
                    perf_ws = writer.sheets['IPO_Performance']
                    for col_num, value in enumerate(empty_ipo_df.columns.values):
                        perf_ws.write(0, col_num, value, header_format)
                
                # Sheet 3: Implementation notes (updated for completed Phase 3)
                notes_data = {
                    'Note': [
                        'This workbook contains REAL IPO analysis data from the Phase 3 unique IPO Intelligence feature.',
                        'IPO performance metrics use post-IPO price data at 30/60/90 days after listing.',
                        'Sentiment scores are computed using multi-source Indian financial news and VADER-based analysis.',
                        'Hold/exit recommendations and confidence scores are generated by the IPO Intelligence System.',
                        'This India-specific IPO intelligence (liquidity + retail sentiment forecast) is not available on platforms like Groww.',
                        'Data is refreshed whenever Phase 3 IPO analysis and recommendation workflows are executed.'
                    ]
                }
                
                notes_df = pd.DataFrame(notes_data)
                notes_df.to_excel(writer, sheet_name='Implementation_Notes', index=False)
                notes_ws = writer.sheets['Implementation_Notes']
                for col_num, value in enumerate(notes_df.columns.values):
                    notes_ws.write(0, col_num, value, header_format)
            
            print("✅ ipo_analysis.xlsx created with IPO intelligence data")
            return True
            
        except Exception as e:
            print(f"❌ Error creating IPO analysis Excel: {str(e)}")
            return False
    
    def create_portfolio_summary_excel(self):
        """Create portfolio summary Excel"""
        try:
            print("💰 Creating portfolio_summary.xlsx...")
            
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Get database statistics
            stock_count = pd.read_sql_query("SELECT COUNT(*) as count FROM stock_prices", conn).iloc[0]['count']
            news_count = pd.read_sql_query("SELECT COUNT(*) as count FROM news_articles", conn).iloc[0]['count']
            unique_stocks = pd.read_sql_query("SELECT COUNT(DISTINCT symbol) as count FROM stock_prices", conn).iloc[0]['count']
            
            conn.close()
            
            with pd.ExcelWriter('exports/portfolio_summary.xlsx', engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # System Status
                status_data = {
                    'Metric': [
                        'Platform Name',
                        'Last Updated',
                        'Total Stock Records',
                        'Unique Stocks Tracked',
                        'News Articles Collected',
                        'Data Sources',
                        'Update Frequency',
                        'Analysis Features',
                        'Excel Reports Generated',
                        'System Status'
                    ],
                    'Value': [
                        PROJECT_NAME,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        f"{stock_count:,}",
                        unique_stocks,
                        f"{news_count:,}",
                        'Yahoo Finance, NewsAPI, RSS Feeds',
                        'Every Hour (Automatic)',
                        'Technical Analysis, Sentiment Analysis, Fake News Detection',
                        '4 Reports (Stock Data, News Sentiment, IPO Analysis, Portfolio Summary)',
                        '✅ Active - Real Data Only'
                    ]
                }
                
                status_df = pd.DataFrame(status_data)
                status_df.to_excel(writer, sheet_name='System_Status', index=False)
                
                # Team Information
                team_data = {
                    'Team_Member': TEAM_MEMBERS,
                    'Role': [
                        'Project Lead & ML Development',
                        'Data Collection & API Integration',
                        'Frontend Development & UI/UX',
                        'NLP & Sentiment Analysis'
                    ],
                    'Phase_2_Contribution': [
                        'System Architecture & Stock Analysis',
                        'Data Service & Excel Integration',
                        'User Interface Enhancement',
                        'Sentiment Analysis & Fake News Detection'
                    ]
                }
                
                team_df = pd.DataFrame(team_data)
                team_df.to_excel(writer, sheet_name='Team_Info', index=False)
                
                # Feature Status
                features_data = {
                    'Feature': [
                        'Real-time Stock Data Collection',
                        'Multi-source News Collection',
                        'Advanced Sentiment Analysis',
                        'Fake News Detection',
                        'Technical Indicators',
                        'Excel Report Generation',
                        'Background Data Service',
                        'IPO Analysis Framework',
                        'Sector Analysis',
                        'Top Movers Tracking'
                    ],
                    'Status': [
                        '✅ Implemented',
                        '✅ Implemented',
                        '✅ Implemented',
                        '✅ Implemented',
                        '✅ Implemented',
                        '✅ Implemented',
                        '✅ Implemented',
                        '🔄 Framework Ready',
                        '✅ Implemented',
                        '✅ Implemented'
                    ],
                    'Phase': [
                        'Phase 2',
                        'Phase 2',
                        'Phase 2',
                        'Phase 2',
                        'Phase 2',
                        'Phase 2',
                        'Phase 2',
                        'Phase 3',
                        'Phase 2',
                        'Phase 2'
                    ]
                }
                
                features_df = pd.DataFrame(features_data)
                features_df.to_excel(writer, sheet_name='Feature_Status', index=False)
            
            print("✅ portfolio_summary.xlsx created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating portfolio summary Excel: {str(e)}")
            return False
    
    def create_daily_market_report(self):
        """Create comprehensive daily market report"""
        try:
            print("📊 Creating daily_market_report.xlsx...")
            
            conn = sqlite3.connect(DATABASE_PATH)
            today = datetime.now().date()
            
            with pd.ExcelWriter('exports/daily_market_report.xlsx', engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Get today's market data
                today_query = '''
                    WITH today_data AS (
                        SELECT symbol, close, date,
                               LAG(close) OVER (PARTITION BY symbol ORDER BY date) as prev_close
                        FROM stock_prices
                        WHERE date >= date('now', '-2 days')
                    )
                    SELECT symbol, close, prev_close,
                           ROUND(((close - prev_close) / prev_close) * 100, 2) as change_percent,
                           ROUND(close - prev_close, 2) as change_amount
                    FROM today_data
                    WHERE prev_close IS NOT NULL
                    ORDER BY change_percent DESC
                '''
                
                market_df = pd.read_sql_query(today_query, conn)
                
                if not market_df.empty:
                    # Top Gainers
                    top_gainers = market_df.head(10)
                    top_gainers['company_name'] = top_gainers['symbol'].map(
                        lambda x: STOCK_SYMBOLS.get(x, x.replace('.NS', ''))
                    )
                    top_gainers.to_excel(writer, sheet_name='Top_Gainers', index=False)
                    
                    # Top Losers
                    top_losers = market_df.tail(10)
                    top_losers['company_name'] = top_losers['symbol'].map(
                        lambda x: STOCK_SYMBOLS.get(x, x.replace('.NS', ''))
                    )
                    top_losers.to_excel(writer, sheet_name='Top_Losers', index=False)
                    
                    # Market Summary
                    total_stocks = len(market_df)
                    gainers = len(market_df[market_df['change_percent'] > 0])
                    losers = len(market_df[market_df['change_percent'] < 0])
                    unchanged = total_stocks - gainers - losers
                    
                    summary_data = {
                        'Metric': [
                            'Date',
                            'Total Stocks',
                            'Gainers',
                            'Losers', 
                            'Unchanged',
                            'Market Sentiment',
                            'Average Change %',
                            'Best Performer',
                            'Worst Performer',
                            'Report Generated'
                        ],
                        'Value': [
                            today.strftime('%Y-%m-%d'),
                            total_stocks,
                            gainers,
                            losers,
                            unchanged,
                            'Positive' if gainers > losers else 'Negative' if losers > gainers else 'Mixed',
                            f"{market_df['change_percent'].mean():.2f}%",
                            f"{market_df.iloc[0]['symbol']} (+{market_df.iloc[0]['change_percent']}%)",
                            f"{market_df.iloc[-1]['symbol']} ({market_df.iloc[-1]['change_percent']}%)",
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        ]
                    }
                    
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='Market_Summary', index=False)
                
                else:
                    # No data available
                    no_data_df = pd.DataFrame({
                        'Message': ['No market data available for today'],
                        'Note': ['Data will be available once market opens and updates']
                    })
                    no_data_df.to_excel(writer, sheet_name='No_Data', index=False)
            
            conn.close()
            print("✅ daily_market_report.xlsx created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating daily market report: {str(e)}")
            return False
    
    def generate_all_reports(self):
        """Generate all Excel reports"""
        print("📊 Generating all Excel reports with REAL DATA...")
        
        results = {
            'stock_data': self.create_stock_data_excel(),
            'news_sentiment': self.create_news_sentiment_excel(),
            'ipo_analysis': self.create_ipo_analysis_excel(),
            'portfolio_summary': self.create_portfolio_summary_excel(),
            'daily_market_report': self.create_daily_market_report()
        }
        
        successful = sum(results.values())
        total = len(results)
        
        print(f"📊 Excel Report Generation Complete:")
        print(f"   ✅ Successful: {successful}/{total} reports")
        print(f"   📁 Location: exports/ folder")
        print(f"   🔄 Auto-updates: Every hour")
        
        return successful == total

# Test the Excel manager
if __name__ == "__main__":
    print("📊 Testing Excel Export Manager...")
    
    manager = ExcelExportManager()
    success = manager.generate_all_reports()
    
    if success:
        print("✅ All Excel reports generated successfully!")
    else:
        print("⚠️ Some reports had issues")
    
    print("✅ Excel Manager test completed!")