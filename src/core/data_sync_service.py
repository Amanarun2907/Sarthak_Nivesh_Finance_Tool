"""
Data Synchronization Service
Automatically syncs real-time data to database
Author: Aman Jain (B.Tech 2023-27)
"""

import sys
import os

# Ensure section folders are on the path when running this file standalone
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _sub in [
    os.path.join(_ROOT, "sections", "07_portfolio_risk"),
    os.path.join(_ROOT, "sections", "10_advanced_analytics"),
    os.path.join(_ROOT, "core"),
]:
    if _sub not in sys.path:
        sys.path.insert(0, _sub)

from database_manager import SarthakNiveshDB
from advanced_analytics_realtime import (
    get_realtime_market_data,
    get_sector_performance,
    get_volume_analysis
)
from datetime import datetime
import schedule
import time

class DataSyncService:
    """Service to sync real-time data to database"""
    
    def __init__(self):
        self.db = SarthakNiveshDB()
        print("✅ Data Sync Service initialized")
    
    def sync_all_data(self):
        """Sync all real-time data to database"""
        print(f"\n🔄 Starting data sync at {datetime.now().strftime('%H:%M:%S')}")
        
        try:
            # 1. Sync Stock Data
            print("📊 Syncing stock data...")
            stock_data = get_realtime_market_data()
            if stock_data:
                self.db.insert_stock_data(stock_data)
            
            # 2. Sync Sector Performance
            print("📈 Syncing sector performance...")
            sector_data = get_sector_performance()
            if sector_data:
                self.db.insert_sector_performance(sector_data)
            
            # 3. Sync Volume Analysis
            print("📊 Syncing volume analysis...")
            volume_data = get_volume_analysis()
            if volume_data:
                self.db.insert_volume_analysis(volume_data)
            
            # 4. Calculate and sync market breadth
            if stock_data:
                print("⚡ Syncing market breadth...")
                total = len(stock_data)
                advancing = sum(1 for d in stock_data.values() if d['change_pct'] > 0)
                declining = sum(1 for d in stock_data.values() if d['change_pct'] < 0)
                unchanged = total - advancing - declining
                ad_ratio = advancing / declining if declining > 0 else advancing
                
                breadth_data = {
                    'total': total,
                    'advancing': advancing,
                    'declining': declining,
                    'unchanged': unchanged,
                    'ad_ratio': ad_ratio,
                    'sentiment': 'Bullish' if ad_ratio > 1.5 else 'Bearish' if ad_ratio < 0.67 else 'Neutral',
                    'strength': (advancing / total) * 100
                }
                self.db.insert_market_breadth(breadth_data)
            
            print(f"✅ Data sync completed at {datetime.now().strftime('%H:%M:%S')}\n")
            
        except Exception as e:
            print(f"❌ Error during sync: {str(e)}")
    
    def start_scheduled_sync(self, interval_minutes=30):
        """Start scheduled data synchronization"""
        print(f"🚀 Starting scheduled sync every {interval_minutes} minutes...")
        
        # Initial sync
        self.sync_all_data()
        
        # Schedule periodic syncs
        schedule.every(interval_minutes).minutes.do(self.sync_all_data)
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def manual_sync():
    """Manually trigger data sync"""
    service = DataSyncService()
    service.sync_all_data()
    
    # Show stats
    print("\n📊 Database Statistics:")
    stats = service.db.get_database_stats()
    for table, count in stats.items():
        print(f"   {table}: {count} records")

if __name__ == "__main__":
    print("=" * 70)
    print("🗄️ SARTHAK NIVESH - DATA SYNC SERVICE")
    print("=" * 70)
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        # Run scheduled sync
        service = DataSyncService()
        service.start_scheduled_sync(interval_minutes=30)
    else:
        # Run manual sync
        manual_sync()
