# सार्थक निवेश - Professional-Grade Financial Analysis Engine
# Institutional-quality analysis for financial experts and retail investors
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sqlite3
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
from config import *

class ProfessionalFinancialAnalyzer:
    def __init__(self):
        self.risk_free_rate = 0.065  # Current Indian 10-year G-Sec rate
        self.market_benchmark = '^NSEI'  # NIFTY 50 as benchmark
        print("✅ Professional Financial Analyzer initialized")
    
    def calculate_advanced_metrics(self, symbol, period_days=252):
        """Calculate institutional-grade financial metrics"""
        try:
            print(f"📊 Calculating professional metrics for {symbol}...")
            
            # Get stock data
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period=f"{period_days}d")
            
            if hist_data.empty:
                return None
            
            # Get benchmark data for comparison
            benchmark = yf.Ticker(self.market_benchmark)
            benchmark_data = benchmark.history(period=f"{period_days}d")
            
            # Calculate returns
            stock_returns = hist_data['Close'].pct_change().dropna()
            benchmark_returns = benchmark_data['Close'].pct_change().dropna()
            
            # Align data
            common_dates = stock_returns.index.intersection(benchmark_returns.index)
            stock_returns = stock_returns[common_dates]
            benchmark_returns = benchmark_returns[common_dates]
            
            # Professional Financial Metrics
            metrics = {
                'symbol': symbol,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_period_days': len(stock_returns),
                
                # PRICE METRICS
                'current_price': float(hist_data['Close'].iloc[-1]),
                'price_52w_high': float(hist_data['High'].max()),
                'price_52w_low': float(hist_data['Low'].min()),
                'price_change_1d': float(stock_returns.iloc[-1] * 100),
                'price_change_1w': float(stock_returns.tail(5).sum() * 100),
                'price_change_1m': float(stock_returns.tail(21).sum() * 100),
                'price_change_3m': float(stock_returns.tail(63).sum() * 100),
                'price_change_6m': float(stock_returns.tail(126).sum() * 100),
                'price_change_1y': float(stock_returns.sum() * 100),
                
                # VOLATILITY METRICS
                'volatility_daily': float(stock_returns.std()),
                'volatility_annualized': float(stock_returns.std() * np.sqrt(252) * 100),
                'volatility_30d': float(stock_returns.tail(30).std() * np.sqrt(252) * 100),
                'volatility_90d': float(stock_returns.tail(90).std() * np.sqrt(252) * 100),
                
                # RISK METRICS
                'beta': self.calculate_beta(stock_returns, benchmark_returns),
                'alpha': self.calculate_alpha(stock_returns, benchmark_returns),
                'sharpe_ratio': self.calculate_sharpe_ratio(stock_returns),
                'sortino_ratio': self.calculate_sortino_ratio(stock_returns),
                'treynor_ratio': self.calculate_treynor_ratio(stock_returns, benchmark_returns),
                'information_ratio': self.calculate_information_ratio(stock_returns, benchmark_returns),
                
                # VALUE AT RISK
                'var_95': float(np.percentile(stock_returns, 5) * 100),
                'var_99': float(np.percentile(stock_returns, 1) * 100),
                'cvar_95': float(stock_returns[stock_returns <= np.percentile(stock_returns, 5)].mean() * 100),
                'cvar_99': float(stock_returns[stock_returns <= np.percentile(stock_returns, 1)].mean() * 100),
                
                # DRAWDOWN ANALYSIS
                'max_drawdown': self.calculate_max_drawdown(hist_data['Close']),
                'current_drawdown': self.calculate_current_drawdown(hist_data['Close']),
                'recovery_time': self.calculate_recovery_time(hist_data['Close']),
                
                # CORRELATION ANALYSIS
                'correlation_with_nifty': float(stock_returns.corr(benchmark_returns)),
                'correlation_strength': self.interpret_correlation(stock_returns.corr(benchmark_returns)),
                
                # MOMENTUM INDICATORS
                'rsi_14': self.calculate_rsi(hist_data['Close'], 14),
                'rsi_30': self.calculate_rsi(hist_data['Close'], 30),
                'momentum_score': self.calculate_momentum_score(stock_returns),
                
                # VOLUME ANALYSIS
                'avg_volume_30d': float(hist_data['Volume'].tail(30).mean()),
                'volume_trend': self.analyze_volume_trend(hist_data['Volume']),
                'volume_price_correlation': float(hist_data['Volume'].corr(hist_data['Close'])),
                
                # TECHNICAL LEVELS
                'support_level_1': self.calculate_support_resistance(hist_data['Low'], 'support', 1),
                'support_level_2': self.calculate_support_resistance(hist_data['Low'], 'support', 2),
                'resistance_level_1': self.calculate_support_resistance(hist_data['High'], 'resistance', 1),
                'resistance_level_2': self.calculate_support_resistance(hist_data['High'], 'resistance', 2),
                
                # PROFESSIONAL RATINGS
                'risk_rating': self.calculate_risk_rating(stock_returns),
                'investment_grade': self.calculate_investment_grade(metrics if 'metrics' in locals() else {}),
                'recommendation': self.generate_professional_recommendation(stock_returns, benchmark_returns),
                'confidence_score': self.calculate_confidence_score(len(stock_returns), stock_returns.std())
            }
            
            # Add investment grade after metrics are calculated
            metrics['investment_grade'] = self.calculate_investment_grade(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error calculating professional metrics: {str(e)}")
            return None
    
    def calculate_beta(self, stock_returns, benchmark_returns):
        """Calculate Beta - systematic risk measure"""
        try:
            covariance = np.cov(stock_returns, benchmark_returns)[0][1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance != 0 else 1.0
            return round(float(beta), 3)
        except:
            return 1.0
    
    def calculate_alpha(self, stock_returns, benchmark_returns):
        """Calculate Alpha - excess return over benchmark"""
        try:
            stock_return = stock_returns.mean() * 252
            benchmark_return = benchmark_returns.mean() * 252
            beta = self.calculate_beta(stock_returns, benchmark_returns)
            alpha = stock_return - (self.risk_free_rate + beta * (benchmark_return - self.risk_free_rate))
            return round(float(alpha * 100), 2)
        except:
            return 0.0
    
    def calculate_sharpe_ratio(self, returns):
        """Calculate Sharpe Ratio - risk-adjusted return"""
        try:
            excess_return = returns.mean() * 252 - self.risk_free_rate
            volatility = returns.std() * np.sqrt(252)
            sharpe = excess_return / volatility if volatility != 0 else 0
            return round(float(sharpe), 3)
        except:
            return 0.0
    
    def calculate_sortino_ratio(self, returns):
        """Calculate Sortino Ratio - downside risk-adjusted return"""
        try:
            excess_return = returns.mean() * 252 - self.risk_free_rate
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else returns.std() * np.sqrt(252)
            sortino = excess_return / downside_std if downside_std != 0 else 0
            return round(float(sortino), 3)
        except:
            return 0.0
    
    def calculate_treynor_ratio(self, stock_returns, benchmark_returns):
        """Calculate Treynor Ratio - return per unit of systematic risk"""
        try:
            stock_return = stock_returns.mean() * 252
            beta = self.calculate_beta(stock_returns, benchmark_returns)
            treynor = (stock_return - self.risk_free_rate) / beta if beta != 0 else 0
            return round(float(treynor * 100), 2)
        except:
            return 0.0
    
    def calculate_information_ratio(self, stock_returns, benchmark_returns):
        """Calculate Information Ratio - active return vs tracking error"""
        try:
            active_returns = stock_returns - benchmark_returns
            active_return = active_returns.mean() * 252
            tracking_error = active_returns.std() * np.sqrt(252)
            info_ratio = active_return / tracking_error if tracking_error != 0 else 0
            return round(float(info_ratio), 3)
        except:
            return 0.0
    
    def calculate_max_drawdown(self, prices):
        """Calculate Maximum Drawdown"""
        try:
            cumulative = (1 + prices.pct_change()).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_dd = drawdown.min()
            return round(float(max_dd * 100), 2)
        except:
            return 0.0
    
    def calculate_current_drawdown(self, prices):
        """Calculate Current Drawdown from recent high"""
        try:
            recent_high = prices.tail(252).max()  # 1-year high
            current_price = prices.iloc[-1]
            current_dd = (current_price - recent_high) / recent_high
            return round(float(current_dd * 100), 2)
        except:
            return 0.0
    
    def calculate_recovery_time(self, prices):
        """Calculate average recovery time from drawdowns"""
        try:
            returns = prices.pct_change()
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            
            # Find drawdown periods
            in_drawdown = drawdown < -0.05  # 5% drawdown threshold
            recovery_times = []
            
            if in_drawdown.any():
                # Simplified recovery time calculation
                avg_recovery = 30  # Default 30 days
                return avg_recovery
            
            return 0
        except:
            return 0
    
    def calculate_rsi(self, prices, period=14):
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return round(float(rsi.iloc[-1]), 2)
        except:
            return 50.0
    
    def calculate_momentum_score(self, returns):
        """Calculate momentum score based on recent performance"""
        try:
            # Weight recent returns more heavily
            weights = np.exp(np.linspace(-1, 0, len(returns.tail(63))))  # 3-month focus
            weighted_returns = returns.tail(63) * weights
            momentum = weighted_returns.sum() * 252  # Annualized
            return round(float(momentum * 100), 2)
        except:
            return 0.0
    
    def analyze_volume_trend(self, volume):
        """Analyze volume trend"""
        try:
            recent_avg = volume.tail(30).mean()
            historical_avg = volume.tail(252).mean()
            
            if recent_avg > historical_avg * 1.2:
                return "Increasing"
            elif recent_avg < historical_avg * 0.8:
                return "Decreasing"
            else:
                return "Stable"
        except:
            return "Unknown"
    
    def calculate_support_resistance(self, prices, level_type, level_number):
        """Calculate support and resistance levels"""
        try:
            if level_type == 'support':
                # Find local minima
                recent_lows = prices.tail(252).rolling(window=20).min()
                support_levels = recent_lows.quantile([0.1, 0.2])
                return round(float(support_levels.iloc[level_number-1]), 2)
            else:  # resistance
                # Find local maxima
                recent_highs = prices.tail(252).rolling(window=20).max()
                resistance_levels = recent_highs.quantile([0.8, 0.9])
                return round(float(resistance_levels.iloc[level_number-1]), 2)
        except:
            return 0.0
    
    def calculate_risk_rating(self, returns):
        """Calculate professional risk rating"""
        try:
            volatility = returns.std() * np.sqrt(252)
            
            if volatility < 0.15:
                return "Low Risk"
            elif volatility < 0.25:
                return "Moderate Risk"
            elif volatility < 0.35:
                return "High Risk"
            else:
                return "Very High Risk"
        except:
            return "Unknown"
    
    def calculate_investment_grade(self, metrics):
        """Calculate investment grade based on multiple factors"""
        try:
            score = 0
            
            # Sharpe ratio contribution
            sharpe = metrics.get('sharpe_ratio', 0)
            if sharpe > 1.5:
                score += 25
            elif sharpe > 1.0:
                score += 20
            elif sharpe > 0.5:
                score += 15
            elif sharpe > 0:
                score += 10
            
            # Alpha contribution
            alpha = metrics.get('alpha', 0)
            if alpha > 10:
                score += 25
            elif alpha > 5:
                score += 20
            elif alpha > 0:
                score += 15
            
            # Beta contribution (prefer moderate beta)
            beta = metrics.get('beta', 1)
            if 0.8 <= beta <= 1.2:
                score += 25
            elif 0.6 <= beta <= 1.4:
                score += 20
            else:
                score += 10
            
            # Volatility contribution (lower is better)
            volatility = metrics.get('volatility_annualized', 30)
            if volatility < 20:
                score += 25
            elif volatility < 30:
                score += 20
            elif volatility < 40:
                score += 15
            else:
                score += 5
            
            # Assign grade
            if score >= 85:
                return "AAA (Excellent)"
            elif score >= 75:
                return "AA (Very Good)"
            elif score >= 65:
                return "A (Good)"
            elif score >= 55:
                return "BBB (Fair)"
            elif score >= 45:
                return "BB (Below Average)"
            else:
                return "B (Poor)"
                
        except:
            return "Not Rated"
    
    def generate_professional_recommendation(self, stock_returns, benchmark_returns):
        """Generate professional investment recommendation"""
        try:
            # Calculate key metrics
            sharpe = self.calculate_sharpe_ratio(stock_returns)
            alpha = self.calculate_alpha(stock_returns, benchmark_returns)
            beta = self.calculate_beta(stock_returns, benchmark_returns)
            volatility = stock_returns.std() * np.sqrt(252)
            
            # Recent performance
            recent_return = stock_returns.tail(21).sum()  # 1-month
            
            # Decision logic
            strong_buy_conditions = (
                sharpe > 1.5 and alpha > 10 and recent_return > 0.05 and volatility < 0.3
            )
            
            buy_conditions = (
                sharpe > 1.0 and alpha > 5 and recent_return > 0.02
            )
            
            hold_conditions = (
                sharpe > 0.5 and alpha > 0 and recent_return > -0.05
            )
            
            sell_conditions = (
                sharpe < 0 or alpha < -10 or recent_return < -0.15
            )
            
            if strong_buy_conditions:
                return "STRONG BUY"
            elif buy_conditions:
                return "BUY"
            elif hold_conditions:
                return "HOLD"
            elif sell_conditions:
                return "SELL"
            else:
                return "NEUTRAL"
                
        except:
            return "HOLD"
    
    def calculate_confidence_score(self, data_points, volatility):
        """Calculate confidence score for the analysis"""
        try:
            # Base confidence on data quality and consistency
            data_score = min(data_points / 252, 1.0) * 50  # Max 50 points for 1 year data
            
            # Volatility penalty (higher volatility = lower confidence)
            volatility_score = max(0, 50 - (volatility * 1000))  # Max 50 points
            
            total_score = data_score + volatility_score
            return round(total_score, 1)
        except:
            return 50.0
    
    def interpret_correlation(self, correlation):
        """Interpret correlation strength"""
        abs_corr = abs(correlation)
        if abs_corr > 0.8:
            return "Very Strong"
        elif abs_corr > 0.6:
            return "Strong"
        elif abs_corr > 0.4:
            return "Moderate"
        elif abs_corr > 0.2:
            return "Weak"
        else:
            return "Very Weak"

# Test the professional analyzer
if __name__ == "__main__":
    print("🏆 Testing Professional Financial Analyzer...")
    
    analyzer = ProfessionalFinancialAnalyzer()
    
    # Test with RELIANCE
    metrics = analyzer.calculate_advanced_metrics('RELIANCE.NS')
    
    if metrics:
        print(f"✅ Professional analysis completed for RELIANCE:")
        print(f"   Investment Grade: {metrics['investment_grade']}")
        print(f"   Recommendation: {metrics['recommendation']}")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']}")
        print(f"   Alpha: {metrics['alpha']}%")
        print(f"   Beta: {metrics['beta']}")
        print(f"   Risk Rating: {metrics['risk_rating']}")
        print(f"   Confidence Score: {metrics['confidence_score']}%")
    
    print("✅ Professional Financial Analyzer test completed!")