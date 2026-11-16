# सार्थक निवेश - Comprehensive Risk Management System
# Advanced Risk Assessment, Portfolio Optimization & Diversification
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sqlite3
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')
from config import *

class ComprehensiveRiskManagement:
    def __init__(self):
        self.risk_free_rate = 0.06  # 6% risk-free rate (Indian government bonds)
        self.setup_risk_database()
        print("🛡️ Comprehensive Risk Management System initialized")
    
    def setup_risk_database(self):
        """Setup risk management database tables"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Portfolio risk assessment table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_risk (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id TEXT NOT NULL,
                    total_value REAL,
                    portfolio_beta REAL,
                    sharpe_ratio REAL,
                    sortino_ratio REAL,
                    max_drawdown REAL,
                    var_95 REAL,
                    var_99 REAL,
                    diversification_score REAL,
                    risk_rating TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Asset allocation table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS asset_allocation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    symbol TEXT,
                    allocation_percent REAL,
                    current_value REAL,
                    risk_contribution REAL,
                    expected_return REAL,
                    volatility REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Risk alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    portfolio_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    threshold_value REAL,
                    current_value REAL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Risk management database setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up risk database: {str(e)}")
    
    def calculate_portfolio_metrics(self, portfolio_data):
        """Calculate comprehensive portfolio risk metrics"""
        try:
            print("📊 Calculating comprehensive portfolio metrics...")
            
            # Get historical data for all assets
            symbols = portfolio_data['symbol'].tolist()
            weights = portfolio_data['weight'].values
            
            # Fetch price data
            price_data = {}
            returns_data = {}
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='2y')
                    
                    if not hist.empty:
                        price_data[symbol] = hist['Close']
                        returns_data[symbol] = hist['Close'].pct_change().dropna()
                except:
                    print(f"⚠️ Could not fetch data for {symbol}")
                    continue
            
            if not returns_data:
                return self.calculate_simulated_metrics(portfolio_data)
            
            # Create returns matrix
            returns_df = pd.DataFrame(returns_data)
            returns_df = returns_df.dropna()
            
            # Portfolio returns
            portfolio_returns = (returns_df * weights).sum(axis=1)
            
            # Calculate metrics
            metrics = {}
            
            # Basic metrics
            metrics['annual_return'] = portfolio_returns.mean() * 252
            metrics['annual_volatility'] = portfolio_returns.std() * np.sqrt(252)
            
            # Sharpe Ratio
            metrics['sharpe_ratio'] = (metrics['annual_return'] - self.risk_free_rate) / metrics['annual_volatility']
            
            # Sortino Ratio (downside deviation)
            downside_returns = portfolio_returns[portfolio_returns < 0]
            downside_deviation = downside_returns.std() * np.sqrt(252)
            metrics['sortino_ratio'] = (metrics['annual_return'] - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
            
            # Maximum Drawdown
            cumulative_returns = (1 + portfolio_returns).cumprod()
            rolling_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - rolling_max) / rolling_max
            metrics['max_drawdown'] = drawdown.min()
            
            # Value at Risk (VaR)
            metrics['var_95'] = np.percentile(portfolio_returns, 5) * np.sqrt(252)
            metrics['var_99'] = np.percentile(portfolio_returns, 1) * np.sqrt(252)
            
            # Portfolio Beta (against market index)
            try:
                nifty = yf.Ticker('^NSEI')
                nifty_hist = nifty.history(period='2y')
                nifty_returns = nifty_hist['Close'].pct_change().dropna()
                
                # Align dates
                common_dates = portfolio_returns.index.intersection(nifty_returns.index)
                if len(common_dates) > 50:
                    port_aligned = portfolio_returns.loc[common_dates]
                    nifty_aligned = nifty_returns.loc[common_dates]
                    
                    covariance = np.cov(port_aligned, nifty_aligned)[0][1]
                    market_variance = np.var(nifty_aligned)
                    metrics['portfolio_beta'] = covariance / market_variance if market_variance > 0 else 1.0
                else:
                    metrics['portfolio_beta'] = 1.0
            except:
                metrics['portfolio_beta'] = 1.0
            
            # Diversification Score
            correlation_matrix = returns_df.corr()
            avg_correlation = correlation_matrix.values[np.triu_indices_from(correlation_matrix.values, k=1)].mean()
            metrics['diversification_score'] = max(0, (1 - avg_correlation) * 100)
            
            # Risk Rating
            metrics['risk_rating'] = self.calculate_risk_rating(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error calculating portfolio metrics: {str(e)}")
            return self.calculate_simulated_metrics(portfolio_data)
    
    def calculate_simulated_metrics(self, portfolio_data):
        """Calculate simulated metrics when real data is unavailable"""
        try:
            # Simulate realistic metrics based on asset types
            asset_risk_profiles = {
                'Large Cap Equity': {'return': 0.12, 'volatility': 0.18, 'beta': 0.9},
                'Mid Cap Equity': {'return': 0.15, 'volatility': 0.25, 'beta': 1.2},
                'Small Cap Equity': {'return': 0.18, 'volatility': 0.35, 'beta': 1.5},
                'Debt/Bonds': {'return': 0.07, 'volatility': 0.05, 'beta': 0.1},
                'Gold/Commodities': {'return': 0.08, 'volatility': 0.20, 'beta': 0.3},
                'International': {'return': 0.10, 'volatility': 0.22, 'beta': 0.8}
            }
            
            # Calculate weighted portfolio metrics
            total_weight = portfolio_data['weight'].sum()
            weighted_return = 0
            weighted_volatility = 0
            weighted_beta = 0
            
            for _, asset in portfolio_data.iterrows():
                asset_type = self.classify_asset_type(asset['symbol'])
                profile = asset_risk_profiles.get(asset_type, asset_risk_profiles['Large Cap Equity'])
                
                weight = asset['weight'] / total_weight
                weighted_return += profile['return'] * weight
                weighted_volatility += (profile['volatility'] ** 2) * (weight ** 2)
                weighted_beta += profile['beta'] * weight
            
            weighted_volatility = np.sqrt(weighted_volatility)
            
            # Calculate derived metrics
            metrics = {
                'annual_return': weighted_return,
                'annual_volatility': weighted_volatility,
                'sharpe_ratio': (weighted_return - self.risk_free_rate) / weighted_volatility,
                'sortino_ratio': (weighted_return - self.risk_free_rate) / (weighted_volatility * 0.7),  # Approximate
                'max_drawdown': -weighted_volatility * 1.5,  # Approximate
                'var_95': -weighted_volatility * 1.65,  # 95% VaR
                'var_99': -weighted_volatility * 2.33,  # 99% VaR
                'portfolio_beta': weighted_beta,
                'diversification_score': min(100, len(portfolio_data) * 15)  # Based on number of assets
            }
            
            metrics['risk_rating'] = self.calculate_risk_rating(metrics)
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error calculating simulated metrics: {str(e)}")
            return {}
    
    def classify_asset_type(self, symbol):
        """Classify asset type based on symbol"""
        if symbol.endswith('.NS') or symbol.endswith('.BO'):
            # Indian stocks - classify by market cap (simplified)
            large_cap = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS']
            if symbol in large_cap:
                return 'Large Cap Equity'
            else:
                return 'Mid Cap Equity'
        elif 'GOLD' in symbol.upper() or 'COMMODITY' in symbol.upper():
            return 'Gold/Commodities'
        elif 'BOND' in symbol.upper() or 'DEBT' in symbol.upper():
            return 'Debt/Bonds'
        else:
            return 'Large Cap Equity'
    
    def calculate_risk_rating(self, metrics):
        """Calculate overall risk rating"""
        try:
            risk_score = 0
            
            # Volatility component (40% weight)
            if metrics['annual_volatility'] > 0.30:
                risk_score += 40
            elif metrics['annual_volatility'] > 0.20:
                risk_score += 30
            elif metrics['annual_volatility'] > 0.15:
                risk_score += 20
            else:
                risk_score += 10
            
            # Beta component (25% weight)
            if metrics['portfolio_beta'] > 1.5:
                risk_score += 25
            elif metrics['portfolio_beta'] > 1.2:
                risk_score += 20
            elif metrics['portfolio_beta'] > 0.8:
                risk_score += 15
            else:
                risk_score += 10
            
            # Sharpe ratio component (20% weight) - inverse scoring
            if metrics['sharpe_ratio'] < 0.5:
                risk_score += 20
            elif metrics['sharpe_ratio'] < 1.0:
                risk_score += 15
            elif metrics['sharpe_ratio'] < 1.5:
                risk_score += 10
            else:
                risk_score += 5
            
            # Diversification component (15% weight) - inverse scoring
            if metrics['diversification_score'] < 30:
                risk_score += 15
            elif metrics['diversification_score'] < 50:
                risk_score += 12
            elif metrics['diversification_score'] < 70:
                risk_score += 8
            else:
                risk_score += 5
            
            # Determine risk rating
            if risk_score >= 80:
                return "Very High Risk"
            elif risk_score >= 65:
                return "High Risk"
            elif risk_score >= 50:
                return "Moderate Risk"
            elif risk_score >= 35:
                return "Low Risk"
            else:
                return "Very Low Risk"
                
        except Exception as e:
            print(f"❌ Error calculating risk rating: {str(e)}")
            return "Moderate Risk"
    
    def optimize_portfolio(self, expected_returns, cov_matrix, risk_tolerance='moderate'):
        """Optimize portfolio allocation using Modern Portfolio Theory"""
        try:
            print("🎯 Optimizing portfolio allocation...")
            
            n_assets = len(expected_returns)
            
            # Risk tolerance mapping
            risk_multipliers = {
                'conservative': 0.5,
                'moderate': 1.0,
                'aggressive': 2.0
            }
            
            risk_multiplier = risk_multipliers.get(risk_tolerance, 1.0)
            
            # Objective function: maximize Sharpe ratio
            def objective(weights):
                portfolio_return = np.sum(weights * expected_returns)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
                return -sharpe_ratio * risk_multiplier  # Negative because we minimize
            
            # Constraints
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # Weights sum to 1
            
            # Bounds (0% to 40% per asset to ensure diversification)
            bounds = tuple((0, 0.4) for _ in range(n_assets))
            
            # Initial guess (equal weights)
            initial_guess = np.array([1/n_assets] * n_assets)
            
            # Optimize
            result = minimize(objective, initial_guess, method='SLSQP', 
                            bounds=bounds, constraints=constraints)
            
            if result.success:
                optimal_weights = result.x
                
                # Calculate optimized portfolio metrics
                opt_return = np.sum(optimal_weights * expected_returns)
                opt_volatility = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
                opt_sharpe = (opt_return - self.risk_free_rate) / opt_volatility
                
                return {
                    'weights': optimal_weights,
                    'expected_return': opt_return,
                    'volatility': opt_volatility,
                    'sharpe_ratio': opt_sharpe,
                    'success': True
                }
            else:
                return {'success': False, 'message': 'Optimization failed'}
                
        except Exception as e:
            print(f"❌ Error optimizing portfolio: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def generate_risk_recommendations(self, portfolio_metrics, portfolio_data):
        """Generate comprehensive risk management recommendations"""
        try:
            recommendations = []
            
            # Volatility recommendations
            if portfolio_metrics['annual_volatility'] > 0.25:
                recommendations.append({
                    'type': 'High Volatility Warning',
                    'severity': 'High',
                    'message': f"Portfolio volatility is {portfolio_metrics['annual_volatility']:.1%}, which is quite high. Consider adding more stable assets like bonds or large-cap stocks.",
                    'action': 'Reduce allocation to high-volatility assets'
                })
            
            # Diversification recommendations
            if portfolio_metrics['diversification_score'] < 50:
                recommendations.append({
                    'type': 'Poor Diversification',
                    'severity': 'Medium',
                    'message': f"Diversification score is {portfolio_metrics['diversification_score']:.1f}/100. Your portfolio may be too concentrated.",
                    'action': 'Add assets from different sectors or asset classes'
                })
            
            # Sharpe ratio recommendations
            if portfolio_metrics['sharpe_ratio'] < 0.8:
                recommendations.append({
                    'type': 'Low Risk-Adjusted Returns',
                    'severity': 'Medium',
                    'message': f"Sharpe ratio is {portfolio_metrics['sharpe_ratio']:.2f}, indicating poor risk-adjusted returns.",
                    'action': 'Review asset selection and consider higher-quality investments'
                })
            
            # Beta recommendations
            if portfolio_metrics['portfolio_beta'] > 1.3:
                recommendations.append({
                    'type': 'High Market Risk',
                    'severity': 'Medium',
                    'message': f"Portfolio beta is {portfolio_metrics['portfolio_beta']:.2f}, making it more volatile than the market.",
                    'action': 'Consider adding defensive stocks or bonds to reduce beta'
                })
            
            # Maximum drawdown recommendations
            if portfolio_metrics['max_drawdown'] < -0.20:
                recommendations.append({
                    'type': 'High Drawdown Risk',
                    'severity': 'High',
                    'message': f"Maximum drawdown is {portfolio_metrics['max_drawdown']:.1%}, indicating high potential losses.",
                    'action': 'Implement stop-loss strategies and reduce position sizes'
                })
            
            # Asset allocation recommendations
            asset_counts = portfolio_data.groupby('asset_type').size() if 'asset_type' in portfolio_data.columns else pd.Series()
            
            if len(asset_counts) < 3:
                recommendations.append({
                    'type': 'Limited Asset Classes',
                    'severity': 'Medium',
                    'message': "Portfolio is concentrated in few asset classes. Consider diversifying across equity, debt, and alternative investments.",
                    'action': 'Add different asset classes for better diversification'
                })
            
            # Positive recommendations
            if portfolio_metrics['sharpe_ratio'] > 1.5:
                recommendations.append({
                    'type': 'Excellent Risk-Adjusted Returns',
                    'severity': 'Positive',
                    'message': f"Sharpe ratio of {portfolio_metrics['sharpe_ratio']:.2f} indicates excellent risk-adjusted performance.",
                    'action': 'Maintain current allocation strategy'
                })
            
            if portfolio_metrics['diversification_score'] > 80:
                recommendations.append({
                    'type': 'Well Diversified',
                    'severity': 'Positive',
                    'message': f"Diversification score of {portfolio_metrics['diversification_score']:.1f}/100 indicates excellent diversification.",
                    'action': 'Continue maintaining diverse asset allocation'
                })
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Error generating recommendations: {str(e)}")
            return []
    
    def calculate_position_sizing(self, portfolio_value, risk_per_trade=0.02):
        """Calculate optimal position sizes based on risk management"""
        try:
            # Kelly Criterion for position sizing
            # Simplified version: risk 2% of portfolio per position
            
            max_position_size = portfolio_value * risk_per_trade
            
            return {
                'max_position_size': max_position_size,
                'recommended_positions': min(10, max(5, int(portfolio_value / 100000))),  # 5-10 positions based on portfolio size
                'risk_per_position': risk_per_trade,
                'max_sector_allocation': 0.25,  # 25% max per sector
                'max_single_stock': 0.10  # 10% max per single stock
            }
            
        except Exception as e:
            print(f"❌ Error calculating position sizing: {str(e)}")
            return {}

# Test the Comprehensive Risk Management System
if __name__ == "__main__":
    print("🛡️ Testing Comprehensive Risk Management System...")
    
    risk_manager = ComprehensiveRiskManagement()
    
    # Test with sample portfolio
    sample_portfolio = pd.DataFrame({
        'symbol': ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS'],
        'weight': [0.3, 0.25, 0.25, 0.2],
        'value': [300000, 250000, 250000, 200000]
    })
    
    # Calculate metrics
    metrics = risk_manager.calculate_portfolio_metrics(sample_portfolio)
    
    if metrics:
        print(f"✅ Portfolio Analysis Complete:")
        print(f"   Annual Return: {metrics.get('annual_return', 0):.2%}")
        print(f"   Volatility: {metrics.get('annual_volatility', 0):.2%}")
        print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"   Risk Rating: {metrics.get('risk_rating', 'N/A')}")
    
    print("✅ Comprehensive Risk Management System test completed!")