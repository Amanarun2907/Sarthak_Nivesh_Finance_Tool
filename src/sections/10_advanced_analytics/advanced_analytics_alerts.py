# सार्थक निवेश - Advanced Analytics & Smart Alerts System (Phase 6)
# Comprehensive Market Analytics, Heat Maps, Correlation Analysis & Intelligent Alerts
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Suppress yfinance warnings and errors
import logging
logging.getLogger('yfinance').setLevel(logging.CRITICAL)

import sqlite3
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')
from config import *

class AdvancedAnalyticsSystem:
    def __init__(self):
        self.setup_analytics_database()
        print("📈 Advanced Analytics & Alerts System initialized")
    
    def setup_analytics_database(self):
        """Setup analytics and alerts database tables"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Market analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_date DATE NOT NULL,
                    market_trend TEXT,
                    volatility_index REAL,
                    fear_greed_index REAL,
                    sector_rotation_data TEXT,
                    correlation_matrix TEXT,
                    market_breadth REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Smart alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS smart_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    alert_type TEXT NOT NULL,
                    symbol TEXT,
                    condition_type TEXT NOT NULL,
                    threshold_value REAL,
                    current_value REAL,
                    alert_message TEXT,
                    priority_level TEXT,
                    is_triggered BOOLEAN DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP
                )
            ''')
            
            # Correlation analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS correlation_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_date DATE NOT NULL,
                    symbol_1 TEXT NOT NULL,
                    symbol_2 TEXT NOT NULL,
                    correlation_coefficient REAL,
                    correlation_strength TEXT,
                    time_period TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Market heat map data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_heatmap (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_date DATE NOT NULL,
                    sector TEXT NOT NULL,
                    performance_1d REAL,
                    performance_1w REAL,
                    performance_1m REAL,
                    performance_3m REAL,
                    market_cap_weighted_return REAL,
                    volume_trend TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Advanced Analytics database setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up analytics database: {str(e)}")
    
    def generate_market_heatmap(self):
        """Generate comprehensive market heat map"""
        try:
            print("🔥 Generating market heat map...")
            
            # Define sectors and representative stocks
            sector_stocks = {
                'Banking & Finance': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS'],
                'Information Technology': ['TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS'],
                'Energy & Power': ['RELIANCE.NS', 'NTPC.NS', 'POWERGRID.NS', 'ONGC.NS'],
                'FMCG & Consumer': ['HINDUNILVR.NS', 'ITC.NS', 'NESTLEIND.NS', 'BRITANNIA.NS'],
                'Automobile': ['MARUTI.NS', 'TATAPOWER.NS', 'M&M.NS', 'BAJAJ-AUTO.NS'],
                'Pharmaceuticals': ['SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS'],
                'Metals & Mining': ['TATASTEEL.NS', 'HINDALCO.NS', 'JSWSTEEL.NS', 'VEDL.NS'],
                'Telecom': ['BHARTIARTL.NS', 'IDEA.NS', 'RCOM.NS']
            }
            
            heatmap_data = []
            
            for sector, stocks in sector_stocks.items():
                sector_performance = self.calculate_sector_performance(stocks, sector)
                if sector_performance:
                    heatmap_data.append(sector_performance)
            
            # Create heat map visualization data
            if heatmap_data:
                heatmap_df = pd.DataFrame(heatmap_data)
                
                # Store in database
                self.store_heatmap_data(heatmap_df)
                
                return {
                    'heatmap_data': heatmap_df,
                    'summary': self.generate_heatmap_summary(heatmap_df)
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error generating market heat map: {str(e)}")
            return None
    
    def calculate_sector_performance(self, stocks, sector_name):
        """Calculate sector performance metrics"""
        try:
            sector_returns = {'1d': [], '1w': [], '1m': [], '3m': []}
            sector_volumes = []
            
            for stock in stocks:
                try:
                    ticker = yf.Ticker(stock)
                    hist_data = ticker.history(period="6mo")
                    
                    if not hist_data.empty and len(hist_data) > 90:
                        # Calculate returns for different periods
                        current_price = hist_data['Close'].iloc[-1]
                        
                        # 1-day return
                        if len(hist_data) > 1:
                            price_1d = hist_data['Close'].iloc[-2]
                            return_1d = ((current_price - price_1d) / price_1d) * 100
                            sector_returns['1d'].append(return_1d)
                        
                        # 1-week return
                        if len(hist_data) > 5:
                            price_1w = hist_data['Close'].iloc[-6]
                            return_1w = ((current_price - price_1w) / price_1w) * 100
                            sector_returns['1w'].append(return_1w)
                        
                        # 1-month return
                        if len(hist_data) > 22:
                            price_1m = hist_data['Close'].iloc[-23]
                            return_1m = ((current_price - price_1m) / price_1m) * 100
                            sector_returns['1m'].append(return_1m)
                        
                        # 3-month return
                        if len(hist_data) > 66:
                            price_3m = hist_data['Close'].iloc[-67]
                            return_3m = ((current_price - price_3m) / price_3m) * 100
                            sector_returns['3m'].append(return_3m)
                        
                        # Volume trend
                        current_volume = hist_data['Volume'].iloc[-1]
                        avg_volume = hist_data['Volume'].rolling(window=20).mean().iloc[-1]
                        sector_volumes.append(current_volume / avg_volume)
                
                except Exception as stock_error:
                    # Silently skip problematic stocks to avoid cluttering output
                    continue
            
            # Calculate sector averages
            if any(sector_returns.values()):
                avg_volume_ratio = np.mean(sector_volumes) if sector_volumes else 1.0
                volume_trend = "High" if avg_volume_ratio > 1.2 else "Low" if avg_volume_ratio < 0.8 else "Normal"
                
                return {
                    'sector': sector_name,
                    'performance_1d': np.mean(sector_returns['1d']) if sector_returns['1d'] else 0,
                    'performance_1w': np.mean(sector_returns['1w']) if sector_returns['1w'] else 0,
                    'performance_1m': np.mean(sector_returns['1m']) if sector_returns['1m'] else 0,
                    'performance_3m': np.mean(sector_returns['3m']) if sector_returns['3m'] else 0,
                    'volume_trend': volume_trend,
                    'stocks_analyzed': len([r for r in sector_returns['1d'] if r != 0])
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error calculating sector performance for {sector_name}: {str(e)}")
            return None
    
    def generate_correlation_analysis(self, symbols=None):
        """Generate correlation analysis between stocks/sectors"""
        try:
            print("🔗 Generating correlation analysis...")
            
            if symbols is None:
                # Default major stocks for correlation analysis
                symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS', 
                          'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS']
            
            # Fetch price data for all symbols
            price_data = {}
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist_data = ticker.history(period="1y")
                    
                    if not hist_data.empty:
                        # Calculate daily returns
                        returns = hist_data['Close'].pct_change().dropna()
                        price_data[symbol.replace('.NS', '')] = returns
                
                except Exception as symbol_error:
                    print(f"⚠️ Error processing {symbol}: {str(symbol_error)}")
                    continue
            
            if len(price_data) >= 2:
                # Create returns DataFrame
                returns_df = pd.DataFrame(price_data)
                returns_df = returns_df.dropna()
                
                # Calculate correlation matrix
                correlation_matrix = returns_df.corr()
                
                # Store correlation data
                self.store_correlation_data(correlation_matrix)
                
                # Generate correlation insights
                insights = self.analyze_correlations(correlation_matrix)
                
                return {
                    'correlation_matrix': correlation_matrix,
                    'insights': insights,
                    'heatmap_data': correlation_matrix.values.tolist(),
                    'symbols': list(correlation_matrix.columns)
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error generating correlation analysis: {str(e)}")
            return None
    
    def analyze_correlations(self, correlation_matrix):
        """Analyze correlation patterns and generate insights"""
        try:
            insights = []
            
            # Find highly correlated pairs (>0.7)
            high_correlations = []
            low_correlations = []
            
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    stock1 = correlation_matrix.columns[i]
                    stock2 = correlation_matrix.columns[j]
                    corr_value = correlation_matrix.iloc[i, j]
                    
                    if corr_value > 0.7:
                        high_correlations.append((stock1, stock2, corr_value))
                    elif corr_value < 0.3:
                        low_correlations.append((stock1, stock2, corr_value))
            
            # Generate insights
            if high_correlations:
                insights.append("🔗 **Highly Correlated Stocks (>70%):**")
                for stock1, stock2, corr in sorted(high_correlations, key=lambda x: x[2], reverse=True)[:5]:
                    insights.append(f"• {stock1} & {stock2}: {corr:.2%} correlation")
                insights.append("These stocks tend to move together. Diversify across different correlation groups.")
            
            if low_correlations:
                insights.append("\n🔀 **Low Correlation Pairs (<30%):**")
                for stock1, stock2, corr in sorted(low_correlations, key=lambda x: x[2])[:3]:
                    insights.append(f"• {stock1} & {stock2}: {corr:.2%} correlation")
                insights.append("These stocks provide good diversification benefits.")
            
            # Sector correlation insights
            avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            insights.append(f"\n📊 **Overall Market Correlation:** {avg_correlation:.2%}")
            
            if avg_correlation > 0.6:
                insights.append("High market correlation indicates increased systematic risk. Consider defensive assets.")
            elif avg_correlation < 0.3:
                insights.append("Low market correlation provides good diversification opportunities.")
            else:
                insights.append("Moderate market correlation suggests balanced market conditions.")
            
            return insights
            
        except Exception as e:
            print(f"❌ Error analyzing correlations: {str(e)}")
            return ["Error analyzing correlation patterns"]
    
    def create_smart_alert(self, user_id, alert_config):
        """Create intelligent alert based on user configuration"""
        try:
            print(f"🔔 Creating smart alert for user {user_id}...")
            
            alert_types = {
                'price_target': self.create_price_alert,
                'technical_signal': self.create_technical_alert,
                'news_sentiment': self.create_sentiment_alert,
                'portfolio_risk': self.create_risk_alert,
                'market_volatility': self.create_volatility_alert,
                'ipo_listing': self.create_ipo_alert
            }
            
            alert_type = alert_config.get('type', 'price_target')
            
            if alert_type in alert_types:
                alert_data = alert_types[alert_type](alert_config)
                
                if alert_data:
                    # Store alert in database
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    
                    cursor.execute('''
                        INSERT INTO smart_alerts 
                        (user_id, alert_type, symbol, condition_type, threshold_value, 
                         alert_message, priority_level, is_active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        user_id, alert_type, alert_data.get('symbol', ''),
                        alert_data['condition_type'], alert_data.get('threshold_value', 0),
                        alert_data['message'], alert_data.get('priority', 'Medium'), True
                    ))
                    
                    alert_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    
                    return {
                        'alert_id': alert_id,
                        'status': 'created',
                        'message': f"Smart alert created successfully: {alert_data['message']}"
                    }
            
            return {'status': 'error', 'message': 'Invalid alert type or configuration'}
            
        except Exception as e:
            print(f"❌ Error creating smart alert: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def create_price_alert(self, config):
        """Create price-based alert"""
        try:
            symbol = config.get('symbol', '')
            target_price = config.get('target_price', 0)
            condition = config.get('condition', 'above')  # above/below
            
            if symbol and target_price:
                return {
                    'symbol': symbol,
                    'condition_type': f'price_{condition}',
                    'threshold_value': target_price,
                    'message': f"Alert: {symbol} price {'reaches above' if condition == 'above' else 'falls below'} ₹{target_price}",
                    'priority': 'High'
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating price alert: {str(e)}")
            return None
    
    def create_technical_alert(self, config):
        """Create technical indicator-based alert"""
        try:
            symbol = config.get('symbol', '')
            indicator = config.get('indicator', 'rsi')  # rsi/macd/ma
            condition = config.get('condition', 'overbought')
            
            if symbol and indicator:
                messages = {
                    'rsi_overbought': f"Alert: {symbol} RSI indicates overbought condition (>70)",
                    'rsi_oversold': f"Alert: {symbol} RSI indicates oversold condition (<30)",
                    'macd_bullish': f"Alert: {symbol} MACD shows bullish crossover",
                    'macd_bearish': f"Alert: {symbol} MACD shows bearish crossover",
                    'ma_breakout': f"Alert: {symbol} price breaks above moving average"
                }
                
                alert_key = f"{indicator}_{condition}"
                message = messages.get(alert_key, f"Alert: {symbol} {indicator} {condition}")
                
                return {
                    'symbol': symbol,
                    'condition_type': alert_key,
                    'threshold_value': 0,
                    'message': message,
                    'priority': 'Medium'
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error creating technical alert: {str(e)}")
            return None
    
    def create_sentiment_alert(self, config):
        """Create sentiment-based alert"""
        try:
            symbol = config.get('symbol', 'MARKET')
            sentiment_threshold = config.get('sentiment_threshold', 0.5)
            condition = config.get('condition', 'positive')  # positive/negative
            
            return {
                'symbol': symbol,
                'condition_type': f'sentiment_{condition}',
                'threshold_value': sentiment_threshold,
                'message': f"Alert: {symbol} sentiment turns {'very positive' if condition == 'positive' else 'negative'} (threshold: {sentiment_threshold})",
                'priority': 'Medium'
            }
            
        except Exception as e:
            print(f"❌ Error creating sentiment alert: {str(e)}")
            return None
    
    def create_risk_alert(self, config):
        """Create portfolio risk-based alert"""
        try:
            risk_threshold = config.get('risk_threshold', 80)
            portfolio_id = config.get('portfolio_id', 'default')
            
            return {
                'symbol': portfolio_id,
                'condition_type': 'portfolio_risk_high',
                'threshold_value': risk_threshold,
                'message': f"Alert: Portfolio risk score exceeds {risk_threshold}% - Consider rebalancing",
                'priority': 'High'
            }
            
        except Exception as e:
            print(f"❌ Error creating risk alert: {str(e)}")
            return None
    
    def create_volatility_alert(self, config):
        """Create market volatility alert"""
        try:
            volatility_threshold = config.get('volatility_threshold', 25)
            
            return {
                'symbol': 'MARKET',
                'condition_type': 'market_volatility_high',
                'threshold_value': volatility_threshold,
                'message': f"Alert: Market volatility exceeds {volatility_threshold}% - Exercise caution",
                'priority': 'High'
            }
            
        except Exception as e:
            print(f"❌ Error creating volatility alert: {str(e)}")
            return None
    
    def create_ipo_alert(self, config):
        """Create IPO-related alert"""
        try:
            ipo_type = config.get('ipo_type', 'new_listing')  # new_listing/performance
            
            messages = {
                'new_listing': "Alert: New IPO listing detected - Check our unique IPO analysis",
                'performance': "Alert: IPO performance update available - Check hold/exit recommendations"
            }
            
            return {
                'symbol': 'IPO',
                'condition_type': f'ipo_{ipo_type}',
                'threshold_value': 0,
                'message': messages.get(ipo_type, "IPO Alert"),
                'priority': 'Medium'
            }
            
        except Exception as e:
            print(f"❌ Error creating IPO alert: {str(e)}")
            return None
    
    def check_and_trigger_alerts(self):
        """Check all active alerts and trigger if conditions are met"""
        try:
            print("🔍 Checking active alerts...")
            
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Get all active alerts
            active_alerts = pd.read_sql_query('''
                SELECT * FROM smart_alerts 
                WHERE is_active = 1 AND is_triggered = 0
            ''', conn)
            
            triggered_alerts = []
            
            for _, alert in active_alerts.iterrows():
                try:
                    should_trigger = self.evaluate_alert_condition(alert)
                    
                    if should_trigger:
                        # Mark alert as triggered
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE smart_alerts 
                            SET is_triggered = 1, triggered_at = CURRENT_TIMESTAMP,
                                current_value = ?
                            WHERE id = ?
                        ''', (should_trigger.get('current_value', 0), alert['id']))
                        
                        triggered_alerts.append({
                            'alert_id': alert['id'],
                            'user_id': alert['user_id'],
                            'message': alert['alert_message'],
                            'priority': alert['priority_level'],
                            'current_value': should_trigger.get('current_value', 0)
                        })
                
                except Exception as alert_error:
                    print(f"⚠️ Error evaluating alert {alert['id']}: {str(alert_error)}")
                    continue
            
            conn.commit()
            conn.close()
            
            return triggered_alerts
            
        except Exception as e:
            print(f"❌ Error checking alerts: {str(e)}")
            return []
    
    def evaluate_alert_condition(self, alert):
        """Evaluate if alert condition is met"""
        try:
            condition_type = alert['condition_type']
            symbol = alert['symbol']
            threshold = alert['threshold_value']
            
            # Price-based alerts
            if condition_type.startswith('price_'):
                current_price = self.get_current_price(symbol)
                if current_price:
                    if condition_type == 'price_above' and current_price >= threshold:
                        return {'triggered': True, 'current_value': current_price}
                    elif condition_type == 'price_below' and current_price <= threshold:
                        return {'triggered': True, 'current_value': current_price}
            
            # Technical indicator alerts
            elif condition_type.startswith('rsi_'):
                rsi_value = self.get_current_rsi(symbol)
                if rsi_value:
                    if condition_type == 'rsi_overbought' and rsi_value > 70:
                        return {'triggered': True, 'current_value': rsi_value}
                    elif condition_type == 'rsi_oversold' and rsi_value < 30:
                        return {'triggered': True, 'current_value': rsi_value}
            
            # Market volatility alerts
            elif condition_type == 'market_volatility_high':
                volatility = self.get_market_volatility()
                if volatility and volatility > threshold:
                    return {'triggered': True, 'current_value': volatility}
            
            return False
            
        except Exception as e:
            print(f"❌ Error evaluating alert condition: {str(e)}")
            return False
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            if not symbol.endswith('.NS'):
                symbol += '.NS'
            
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="2d")
            
            if not hist_data.empty:
                return hist_data['Close'].iloc[-1]
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting current price for {symbol}: {str(e)}")
            return None
    
    def get_current_rsi(self, symbol):
        """Get current RSI for a symbol"""
        try:
            if not symbol.endswith('.NS'):
                symbol += '.NS'
            
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period="3mo")
            
            if not hist_data.empty and len(hist_data) > 14:
                prices = hist_data['Close']
                delta = prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi.iloc[-1]
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting RSI for {symbol}: {str(e)}")
            return None
    
    def get_market_volatility(self):
        """Get current market volatility (VIX equivalent)"""
        try:
            # Use NIFTY volatility as proxy
            nifty = yf.Ticker('^NSEI')
            hist_data = nifty.history(period="1mo")
            
            if not hist_data.empty:
                returns = hist_data['Close'].pct_change().dropna()
                volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
                return volatility
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting market volatility: {str(e)}")
            return None
    
    def generate_market_breadth_analysis(self):
        """Generate market breadth analysis"""
        try:
            print("📊 Generating market breadth analysis...")
            
            # Sample of stocks for breadth analysis
            stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
                     'ICICIBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS',
                     'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'NTPC.NS']
            
            advancing_stocks = 0
            declining_stocks = 0
            unchanged_stocks = 0
            
            for stock in stocks:
                try:
                    ticker = yf.Ticker(stock)
                    hist_data = ticker.history(period="2d")
                    
                    if not hist_data.empty and len(hist_data) > 1:
                        current_price = hist_data['Close'].iloc[-1]
                        prev_price = hist_data['Close'].iloc[-2]
                        
                        change_percent = ((current_price - prev_price) / prev_price) * 100
                        
                        if change_percent > 0.1:
                            advancing_stocks += 1
                        elif change_percent < -0.1:
                            declining_stocks += 1
                        else:
                            unchanged_stocks += 1
                
                except Exception as stock_error:
                    # Silently skip problematic stocks to avoid cluttering output
                    continue
            
            total_stocks = advancing_stocks + declining_stocks + unchanged_stocks
            
            if total_stocks > 0:
                advance_decline_ratio = advancing_stocks / declining_stocks if declining_stocks > 0 else float('inf')
                breadth_percentage = (advancing_stocks / total_stocks) * 100
                
                # Determine market breadth sentiment
                if breadth_percentage > 70:
                    breadth_sentiment = "Very Bullish"
                elif breadth_percentage > 55:
                    breadth_sentiment = "Bullish"
                elif breadth_percentage > 45:
                    breadth_sentiment = "Neutral"
                elif breadth_percentage > 30:
                    breadth_sentiment = "Bearish"
                else:
                    breadth_sentiment = "Very Bearish"
                
                return {
                    'advancing_stocks': advancing_stocks,
                    'declining_stocks': declining_stocks,
                    'unchanged_stocks': unchanged_stocks,
                    'total_analyzed': total_stocks,
                    'advance_decline_ratio': advance_decline_ratio,
                    'breadth_percentage': breadth_percentage,
                    'breadth_sentiment': breadth_sentiment,
                    'analysis_date': datetime.now().date()
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Error generating market breadth analysis: {str(e)}")
            return None
    
    def store_heatmap_data(self, heatmap_df):
        """Store heat map data in database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            
            for _, row in heatmap_df.iterrows():
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO market_heatmap 
                    (analysis_date, sector, performance_1d, performance_1w, 
                     performance_1m, performance_3m, volume_trend)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().date(), row['sector'], row['performance_1d'],
                    row['performance_1w'], row['performance_1m'], row['performance_3m'],
                    row['volume_trend']
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing heatmap data: {str(e)}")
    
    def store_correlation_data(self, correlation_matrix):
        """Store correlation data in database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            analysis_date = datetime.now().date()
            
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    symbol1 = correlation_matrix.columns[i]
                    symbol2 = correlation_matrix.columns[j]
                    corr_value = correlation_matrix.iloc[i, j]
                    
                    # Determine correlation strength
                    if abs(corr_value) > 0.7:
                        strength = "Strong"
                    elif abs(corr_value) > 0.4:
                        strength = "Moderate"
                    else:
                        strength = "Weak"
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO correlation_analysis 
                        (analysis_date, symbol_1, symbol_2, correlation_coefficient, 
                         correlation_strength, time_period)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (analysis_date, symbol1, symbol2, corr_value, strength, "1Y"))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error storing correlation data: {str(e)}")
    
    def generate_heatmap_summary(self, heatmap_df):
        """Generate summary insights from heat map data"""
        try:
            summary = []
            
            # Best and worst performing sectors
            best_1d = heatmap_df.loc[heatmap_df['performance_1d'].idxmax()]
            worst_1d = heatmap_df.loc[heatmap_df['performance_1d'].idxmin()]
            
            summary.append(f"🚀 **Best Performing Sector (1D):** {best_1d['sector']} (+{best_1d['performance_1d']:.2f}%)")
            summary.append(f"📉 **Worst Performing Sector (1D):** {worst_1d['sector']} ({worst_1d['performance_1d']:.2f}%)")
            
            # Monthly performance leaders
            best_1m = heatmap_df.loc[heatmap_df['performance_1m'].idxmax()]
            summary.append(f"📈 **Monthly Leader:** {best_1m['sector']} (+{best_1m['performance_1m']:.2f}%)")
            
            # Volume trends
            high_volume_sectors = heatmap_df[heatmap_df['volume_trend'] == 'High']['sector'].tolist()
            if high_volume_sectors:
                summary.append(f"🔥 **High Volume Sectors:** {', '.join(high_volume_sectors)}")
            
            # Overall market sentiment
            avg_1d_performance = heatmap_df['performance_1d'].mean()
            if avg_1d_performance > 1:
                summary.append("🟢 **Overall Market:** Bullish sentiment across sectors")
            elif avg_1d_performance < -1:
                summary.append("🔴 **Overall Market:** Bearish sentiment across sectors")
            else:
                summary.append("🟡 **Overall Market:** Mixed sentiment, sector-specific opportunities")
            
            return summary
            
        except Exception as e:
            print(f"❌ Error generating heatmap summary: {str(e)}")
            return ["Error generating market summary"]

# Test the Advanced Analytics System
if __name__ == "__main__":
    print("📈 Testing Advanced Analytics & Alerts System...")
    
    analytics = AdvancedAnalyticsSystem()
    
    # Test market heat map
    heatmap_result = analytics.generate_market_heatmap()
    if heatmap_result:
        print("✅ Market heat map generated successfully")
        print(f"📊 Analyzed {len(heatmap_result['heatmap_data'])} sectors")
    
    # Test correlation analysis
    correlation_result = analytics.generate_correlation_analysis()
    if correlation_result:
        print("✅ Correlation analysis completed")
        print(f"🔗 Analyzed {len(correlation_result['symbols'])} stocks")
    
    # Test smart alert creation
    alert_config = {
        'type': 'price_target',
        'symbol': 'HDFCBANK.NS',
        'target_price': 1500,
        'condition': 'above'
    }
    
    alert_result = analytics.create_smart_alert('test_user', alert_config)
    if alert_result['status'] == 'created':
        print("✅ Smart alert created successfully")
    
    # Test market breadth
    breadth_result = analytics.generate_market_breadth_analysis()
    if breadth_result:
        print(f"✅ Market breadth: {breadth_result['breadth_sentiment']} ({breadth_result['breadth_percentage']:.1f}%)")
    
    print("✅ Advanced Analytics & Alerts System test completed!")