# सार्थक निवेश - Advanced Stock Analysis Module
# Technical indicators, price predictions, and comprehensive stock analysis
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sqlite3
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import warnings
warnings.filterwarnings('ignore')
from config import *
from sklearn.linear_model import LinearRegression

class AdvancedStockAnalyzer:
    def __init__(self):
        self.alpha_vantage_ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        self.alpha_vantage_ti = TechIndicators(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
        print("✅ Advanced Stock Analyzer initialized")
    
    def calculate_technical_indicators(self, df):
        """Calculate comprehensive technical indicators - REAL DATA"""
        try:
            if df.empty or len(df) < 20:
                print("⚠️ Insufficient data for technical analysis")
                return df
            
            # Ensure we have the required columns
            if 'close' not in df.columns:
                print("❌ Missing 'close' column in data")
                return df
            
            # Sort by date to ensure proper calculation
            df = df.sort_values('date').reset_index(drop=True)
            
            # Simple Moving Averages
            df['sma_5'] = df['close'].rolling(window=5).mean()
            df['sma_10'] = df['close'].rolling(window=10).mean()
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # MACD (Moving Average Convergence Divergence)
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # RSI (Relative Strength Index)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_width'] = df['bb_upper'] - df['bb_lower']
            df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
            
            # Volume indicators
            if 'volume' in df.columns:
                df['volume_sma'] = df['volume'].rolling(window=20).mean()
                df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            # Price change indicators
            df['price_change'] = df['close'].pct_change()
            df['price_change_5d'] = df['close'].pct_change(periods=5)
            df['volatility'] = df['price_change'].rolling(window=20).std()
            
            # Support and Resistance levels
            df['resistance'] = df['high'].rolling(window=20).max()
            df['support'] = df['low'].rolling(window=20).min()
            
            # Trend indicators
            df['trend_5d'] = np.where(df['close'] > df['sma_5'], 1, -1)
            df['trend_20d'] = np.where(df['close'] > df['sma_20'], 1, -1)
            
            print("✅ Technical indicators calculated successfully")
            return df
            
        except Exception as e:
            print(f"❌ Error calculating technical indicators: {str(e)}")
            return df
    
    def get_stock_analysis(self, symbol, days=90):
        """Get comprehensive stock analysis - REAL DATA ONLY"""
        try:
            print(f"📊 Analyzing {symbol} with real market data...")
            
            # Get real data from database
            conn = sqlite3.connect(DATABASE_PATH)
            query = '''
                SELECT * FROM stock_prices 
                WHERE symbol = ? 
                ORDER BY date DESC 
                LIMIT ?
            '''
            df = pd.read_sql_query(query, conn, params=(symbol, days))
            conn.close()
            
            if df.empty:
                print(f"❌ No data found for {symbol}")
                return None
            
            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)
            
            # Get latest values
            latest = df.iloc[0]  # Most recent data
            
            # Calculate analysis metrics
            analysis = {
                'symbol': symbol,
                'company_name': STOCK_SYMBOLS.get(symbol, symbol),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                
                # Current Price Data
                'current_price': round(latest['close'], 2),
                'previous_close': round(df.iloc[1]['close'], 2) if len(df) > 1 else latest['close'],
                'day_change': round(latest['close'] - df.iloc[1]['close'], 2) if len(df) > 1 else 0,
                'day_change_percent': round(((latest['close'] - df.iloc[1]['close']) / df.iloc[1]['close']) * 100, 2) if len(df) > 1 else 0,
                
                # Price Range
                'day_high': round(latest['high'], 2),
                'day_low': round(latest['low'], 2),
                'week_high': round(df['high'].head(7).max(), 2),
                'week_low': round(df['low'].head(7).min(), 2),
                'month_high': round(df['high'].head(30).max(), 2),
                'month_low': round(df['low'].head(30).min(), 2),
                
                # Volume Analysis
                'volume': int(latest['volume']) if 'volume' in latest else 0,
                'avg_volume': int(df['volume'].mean()) if 'volume' in df.columns else 0,
                'volume_ratio': round(latest.get('volume_ratio', 1.0), 2),
                
                # Technical Indicators
                'rsi': round(latest.get('rsi', 50), 2),
                'macd': round(latest.get('macd', 0), 4),
                'macd_signal': round(latest.get('macd_signal', 0), 4),
                'bb_position': round(latest.get('bb_position', 0.5), 3),
                
                # Moving Averages
                'sma_5': round(latest.get('sma_5', latest['close']), 2),
                'sma_20': round(latest.get('sma_20', latest['close']), 2),
                'sma_50': round(latest.get('sma_50', latest['close']), 2),
                
                # Support/Resistance
                'support_level': round(latest.get('support', latest['low']), 2),
                'resistance_level': round(latest.get('resistance', latest['high']), 2),
                
                # Volatility
                'volatility': round(latest.get('volatility', 0) * 100, 2),
                
                # Trend Analysis
                'short_term_trend': 'Bullish' if latest.get('trend_5d', 0) > 0 else 'Bearish',
                'medium_term_trend': 'Bullish' if latest.get('trend_20d', 0) > 0 else 'Bearish',
            }
            
            # Generate trading signals
            analysis['trading_signals'] = self.generate_trading_signals(latest)
            
            # Risk assessment
            analysis['risk_level'] = self.assess_risk_level(df)
            
            print(f"✅ Analysis complete for {symbol}")
            return analysis
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {str(e)}")
            return None
    
    def generate_trading_signals(self, latest_data):
        """Generate real-time trading signals"""
        signals = []
        
        try:
            # RSI Signals
            rsi = latest_data.get('rsi', 50)
            if rsi > 70:
                signals.append({'type': 'SELL', 'reason': f'RSI Overbought ({rsi:.1f})', 'strength': 'Strong'})
            elif rsi < 30:
                signals.append({'type': 'BUY', 'reason': f'RSI Oversold ({rsi:.1f})', 'strength': 'Strong'})
            
            # MACD Signals
            macd = latest_data.get('macd', 0)
            macd_signal = latest_data.get('macd_signal', 0)
            if macd > macd_signal and macd > 0:
                signals.append({'type': 'BUY', 'reason': 'MACD Bullish Crossover', 'strength': 'Medium'})
            elif macd < macd_signal and macd < 0:
                signals.append({'type': 'SELL', 'reason': 'MACD Bearish Crossover', 'strength': 'Medium'})
            
            # Bollinger Bands Signals
            bb_position = latest_data.get('bb_position', 0.5)
            if bb_position > 0.9:
                signals.append({'type': 'SELL', 'reason': 'Price near Upper Bollinger Band', 'strength': 'Medium'})
            elif bb_position < 0.1:
                signals.append({'type': 'BUY', 'reason': 'Price near Lower Bollinger Band', 'strength': 'Medium'})
            
            # Moving Average Signals
            current_price = latest_data.get('close', 0)
            sma_20 = latest_data.get('sma_20', current_price)
            sma_50 = latest_data.get('sma_50', current_price)
            
            if current_price > sma_20 > sma_50:
                signals.append({'type': 'BUY', 'reason': 'Price above key moving averages', 'strength': 'Medium'})
            elif current_price < sma_20 < sma_50:
                signals.append({'type': 'SELL', 'reason': 'Price below key moving averages', 'strength': 'Medium'})
            
            # Volume Signals
            volume_ratio = latest_data.get('volume_ratio', 1.0)
            if volume_ratio > 2.0:
                signals.append({'type': 'WATCH', 'reason': f'High volume activity ({volume_ratio:.1f}x avg)', 'strength': 'Strong'})
            
            return signals
            
        except Exception as e:
            print(f"❌ Error generating signals: {str(e)}")
            return [{'type': 'HOLD', 'reason': 'Analysis incomplete', 'strength': 'Low'}]
    
    def assess_risk_level(self, df):
        """Assess risk level based on volatility and other factors"""
        try:
            if df.empty:
                return 'Unknown'
            
            # Calculate volatility
            volatility = df['price_change'].std() if 'price_change' in df.columns else 0
            
            # Calculate beta (simplified - relative to market)
            # For now, use volatility as proxy
            if volatility > 0.03:  # 3% daily volatility
                return 'High'
            elif volatility > 0.015:  # 1.5% daily volatility
                return 'Medium'
            else:
                return 'Low'
                
        except Exception as e:
            print(f"❌ Error assessing risk: {str(e)}")
            return 'Unknown'
    
    def get_sector_analysis(self):
        """Analyze performance by sector - REAL DATA"""
        try:
            print("📊 Performing sector-wise analysis...")
            
            # Define sectors
            sectors = {
                'Banking': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'AXISBANK.NS'],
                'IT': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS'],
                'Energy': ['RELIANCE.NS', 'NTPC.NS', 'POWERGRID.NS'],
                'FMCG': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS'],
                'Auto': ['MARUTI.NS', 'TATAPOWER.NS'],
                'Pharma': ['SUNPHARMA.NS', 'DRREDDY.NS'],
                'Metals': ['LT.NS', 'TATASTEEL.NS']
            }
            
            sector_performance = {}
            
            conn = sqlite3.connect(DATABASE_PATH)
            
            for sector, stocks in sectors.items():
                sector_data = []
                
                for stock in stocks:
                    # Get latest 2 days data for change calculation
                    query = '''
                        SELECT close, date FROM stock_prices 
                        WHERE symbol = ? 
                        ORDER BY date DESC 
                        LIMIT 2
                    '''
                    stock_df = pd.read_sql_query(query, conn, params=(stock,))
                    
                    if len(stock_df) >= 2:
                        current_price = stock_df.iloc[0]['close']
                        previous_price = stock_df.iloc[1]['close']
                        change_percent = ((current_price - previous_price) / previous_price) * 100
                        sector_data.append(change_percent)
                
                if sector_data:
                    avg_performance = np.mean(sector_data)
                    sector_performance[sector] = {
                        'performance': round(avg_performance, 2),
                        'stocks_count': len(sector_data),
                        'status': 'Positive' if avg_performance > 0 else 'Negative' if avg_performance < 0 else 'Neutral'
                    }
            
            conn.close()
            
            print("✅ Sector analysis completed")
            return sector_performance
            
        except Exception as e:
            print(f"❌ Error in sector analysis: {str(e)}")
            return {}
    
    def get_top_movers(self, limit=10):
        """Get top gainers and losers - REAL DATA"""
        try:
            print("📈 Finding top movers...")
            
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Get latest prices with change calculation
            query = '''
                WITH latest_prices AS (
                    SELECT symbol, close, date,
                           LAG(close) OVER (PARTITION BY symbol ORDER BY date) as prev_close
                    FROM stock_prices
                    WHERE date >= date('now', '-2 days')
                ),
                price_changes AS (
                    SELECT symbol, close, prev_close,
                           ROUND(((close - prev_close) / prev_close) * 100, 2) as change_percent
                    FROM latest_prices
                    WHERE prev_close IS NOT NULL
                )
                SELECT * FROM price_changes
                ORDER BY change_percent DESC
            '''
            
            movers_df = pd.read_sql_query(query, conn)
            conn.close()
            
            if movers_df.empty:
                return {'gainers': [], 'losers': []}
            
            # Get top gainers and losers
            gainers = movers_df.head(limit).to_dict('records')
            losers = movers_df.tail(limit).to_dict('records')
            
            # Add company names
            for mover in gainers + losers:
                mover['company_name'] = STOCK_SYMBOLS.get(mover['symbol'], mover['symbol'])
            
            print(f"✅ Found {len(gainers)} gainers and {len(losers)} losers")
            
            return {
                'gainers': gainers,
                'losers': losers
            }
            
        except Exception as e:
            print(f"❌ Error finding top movers: {str(e)}")
            return {'gainers': [], 'losers': []}
    
    def quick_price_forecast(self, symbol, horizon_days=30):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            df = pd.read_sql_query("""
                SELECT date, close FROM stock_prices
                WHERE symbol = ?
                ORDER BY date ASC
            """, conn, params=(symbol,))
            conn.close()
            if df.empty:
                return None
            df['date'] = pd.to_datetime(df['date'])
            df = df.dropna(subset=['close'])
            df = df.tail(180)
            if len(df) < 20:
                return None
            X = np.arange(len(df)).reshape(-1, 1)
            y = df['close'].values
            model = LinearRegression()
            model.fit(X, y)
            future_X = np.arange(len(df), len(df) + horizon_days).reshape(-1, 1)
            preds = model.predict(future_X)
            last_date = df['date'].iloc[-1]
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon_days, freq='B')
            forecast_df = pd.DataFrame({'date': future_dates[:horizon_days], 'forecast': preds[:len(future_dates)]})
            history = df[['date', 'close']].copy()
            history.columns = ['date', 'actual']
            return {'history': history, 'forecast': forecast_df}
        except Exception:
            return None

# Test the stock analyzer
if __name__ == "__main__":
    print("📊 Testing Advanced Stock Analyzer...")
    
    analyzer = AdvancedStockAnalyzer()
    
    # Test stock analysis
    test_symbol = 'RELIANCE.NS'
    analysis = analyzer.get_stock_analysis(test_symbol)
    
    if analysis:
        print(f"✅ Analysis for {analysis['company_name']}:")
        print(f"   Current Price: ₹{analysis['current_price']}")
        print(f"   Day Change: {analysis['day_change_percent']}%")
        print(f"   RSI: {analysis['rsi']}")
        print(f"   Risk Level: {analysis['risk_level']}")
        print(f"   Signals: {len(analysis['trading_signals'])} generated")
    
    # Test sector analysis
    sectors = analyzer.get_sector_analysis()
    print(f"✅ Sector analysis: {len(sectors)} sectors analyzed")
    
    # Test top movers
    movers = analyzer.get_top_movers(5)
    print(f"✅ Top movers: {len(movers['gainers'])} gainers, {len(movers['losers'])} losers")
    
    print("✅ Stock Analyzer test completed!")
