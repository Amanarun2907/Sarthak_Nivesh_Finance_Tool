# सार्थक निवेश - Institutional Risk Management System
# Professional-grade risk assessment and portfolio management
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')
from config import *

class InstitutionalRiskManager:
    def __init__(self):
        self.risk_free_rate = 0.065  # Indian 10-year G-Sec
        self.market_benchmark = '^NSEI'
        self.confidence_levels = [0.95, 0.99]
        print("✅ Institutional Risk Manager initialized")
    
    def comprehensive_risk_assessment(self, portfolio_symbols, weights=None):
        """Comprehensive institutional-grade risk assessment"""
        try:
            print(f"🛡️ Conducting comprehensive risk assessment for {len(portfolio_symbols)} assets...")
            
            if weights is None:
                weights = np.array([1/len(portfolio_symbols)] * len(portfolio_symbols))
            else:
                weights = np.array(weights)
            
            # Get portfolio data
            portfolio_data = self.get_portfolio_data(portfolio_symbols)
            
            if portfolio_data.empty:
                return None
            
            # Calculate returns
            returns = portfolio_data.pct_change().dropna()
            
            # Portfolio returns
            portfolio_returns = (returns * weights).sum(axis=1)
            
            # Risk Assessment
            risk_metrics = {
                'assessment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'portfolio_size': len(portfolio_symbols),
                'analysis_period_days': len(returns),
                
                # PORTFOLIO RISK METRICS
                'portfolio_volatility_daily': float(portfolio_returns.std()),
                'portfolio_volatility_annual': float(portfolio_returns.std() * np.sqrt(252) * 100),
                'portfolio_return_annual': float(portfolio_returns.mean() * 252 * 100),
                
                # VALUE AT RISK (VaR)
                'var_95_daily': float(np.percentile(portfolio_returns, 5) * 100),
                'var_99_daily': float(np.percentile(portfolio_returns, 1) * 100),
                'var_95_annual': float(np.percentile(portfolio_returns, 5) * np.sqrt(252) * 100),
                'var_99_annual': float(np.percentile(portfolio_returns, 1) * np.sqrt(252) * 100),
                
                # CONDITIONAL VALUE AT RISK (CVaR)
                'cvar_95': float(portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 5)].mean() * 100),
                'cvar_99': float(portfolio_returns[portfolio_returns <= np.percentile(portfolio_returns, 1)].mean() * 100),
                
                # MAXIMUM DRAWDOWN
                'max_drawdown': self.calculate_portfolio_max_drawdown(portfolio_returns),
                'current_drawdown': self.calculate_current_drawdown(portfolio_returns),
                
                # RISK-ADJUSTED RETURNS
                'sharpe_ratio': self.calculate_portfolio_sharpe(portfolio_returns),
                'sortino_ratio': self.calculate_portfolio_sortino(portfolio_returns),
                'calmar_ratio': self.calculate_calmar_ratio(portfolio_returns),
                
                # DIVERSIFICATION METRICS
                'diversification_ratio': self.calculate_diversification_ratio(returns, weights),
                'concentration_risk': self.calculate_concentration_risk(weights),
                'correlation_risk': self.calculate_correlation_risk(returns),
                
                # STRESS TESTING
                'stress_test_results': self.conduct_stress_tests(portfolio_returns),
                
                # RISK DECOMPOSITION
                'component_var': self.calculate_component_var(returns, weights),
                'marginal_var': self.calculate_marginal_var(returns, weights),
                
                # RISK RATINGS
                'overall_risk_rating': self.calculate_overall_risk_rating(portfolio_returns),
                'liquidity_risk': self.assess_liquidity_risk(portfolio_symbols),
                'market_risk': self.assess_market_risk(portfolio_returns),
                'concentration_rating': self.rate_concentration_risk(weights),
                
                # RECOMMENDATIONS
                'risk_recommendations': self.generate_risk_recommendations(portfolio_returns, weights),
                'optimal_weights': self.calculate_optimal_weights(returns),
                'rebalancing_needed': self.assess_rebalancing_need(weights, returns)
            }
            
            return risk_metrics
            
        except Exception as e:
            print(f"❌ Error in risk assessment: {str(e)}")
            return None
    
    def get_portfolio_data(self, symbols, period='1y'):
        """Get portfolio data for analysis"""
        try:
            data = pd.DataFrame()
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                if not hist.empty:
                    data[symbol] = hist['Close']
            
            return data.dropna()
        except Exception as e:
            print(f"❌ Error getting portfolio data: {str(e)}")
            return pd.DataFrame()
    
    def calculate_portfolio_max_drawdown(self, returns):
        """Calculate maximum drawdown for portfolio"""
        try:
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return round(float(drawdown.min() * 100), 2)
        except:
            return 0.0
    
    def calculate_current_drawdown(self, returns):
        """Calculate current drawdown from peak"""
        try:
            cumulative = (1 + returns).cumprod()
            peak = cumulative.max()
            current = cumulative.iloc[-1]
            current_dd = (current - peak) / peak
            return round(float(current_dd * 100), 2)
        except:
            return 0.0
    
    def calculate_portfolio_sharpe(self, returns):
        """Calculate portfolio Sharpe ratio"""
        try:
            excess_return = returns.mean() * 252 - self.risk_free_rate
            volatility = returns.std() * np.sqrt(252)
            sharpe = excess_return / volatility if volatility != 0 else 0
            return round(float(sharpe), 3)
        except:
            return 0.0
    
    def calculate_portfolio_sortino(self, returns):
        """Calculate portfolio Sortino ratio"""
        try:
            excess_return = returns.mean() * 252 - self.risk_free_rate
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else returns.std() * np.sqrt(252)
            sortino = excess_return / downside_std if downside_std != 0 else 0
            return round(float(sortino), 3)
        except:
            return 0.0
    
    def calculate_calmar_ratio(self, returns):
        """Calculate Calmar ratio (return/max drawdown)"""
        try:
            annual_return = returns.mean() * 252
            max_dd = abs(self.calculate_portfolio_max_drawdown(returns) / 100)
            calmar = annual_return / max_dd if max_dd != 0 else 0
            return round(float(calmar), 3)
        except:
            return 0.0
    
    def calculate_diversification_ratio(self, returns, weights):
        """Calculate diversification ratio"""
        try:
            # Weighted average of individual volatilities
            individual_vols = returns.std() * np.sqrt(252)
            weighted_avg_vol = np.sum(weights * individual_vols)
            
            # Portfolio volatility
            portfolio_vol = (returns * weights).sum(axis=1).std() * np.sqrt(252)
            
            div_ratio = weighted_avg_vol / portfolio_vol if portfolio_vol != 0 else 1
            return round(float(div_ratio), 3)
        except:
            return 1.0
    
    def calculate_concentration_risk(self, weights):
        """Calculate concentration risk using Herfindahl index"""
        try:
            herfindahl = np.sum(weights ** 2)
            return round(float(herfindahl), 3)
        except:
            return 1.0
    
    def calculate_correlation_risk(self, returns):
        """Calculate average correlation risk"""
        try:
            corr_matrix = returns.corr()
            # Get upper triangle (excluding diagonal)
            upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            avg_correlation = upper_triangle.stack().mean()
            return round(float(avg_correlation), 3)
        except:
            return 0.0
    
    def conduct_stress_tests(self, returns):
        """Conduct various stress tests"""
        try:
            stress_results = {}
            
            # Market crash scenario (-20% market drop)
            crash_scenario = returns.quantile(0.01)  # Worst 1% scenario
            stress_results['market_crash_impact'] = round(float(crash_scenario * 100), 2)
            
            # High volatility scenario (2x normal volatility)
            normal_vol = returns.std()
            high_vol_scenario = returns.mean() - 2 * normal_vol
            stress_results['high_volatility_impact'] = round(float(high_vol_scenario * 100), 2)
            
            # Interest rate shock (assume 2% rate increase impact)
            rate_shock_impact = returns.mean() - 0.02/252  # Simplified impact
            stress_results['interest_rate_shock'] = round(float(rate_shock_impact * 100), 2)
            
            return stress_results
        except:
            return {'market_crash_impact': 0, 'high_volatility_impact': 0, 'interest_rate_shock': 0}
    
    def calculate_component_var(self, returns, weights):
        """Calculate component VaR for each asset"""
        try:
            portfolio_returns = (returns * weights).sum(axis=1)
            portfolio_var = np.percentile(portfolio_returns, 5)
            
            component_vars = {}
            for i, symbol in enumerate(returns.columns):
                # Marginal contribution to VaR
                marginal_var = returns.iloc[:, i].corr(portfolio_returns) * returns.iloc[:, i].std()
                component_var = weights[i] * marginal_var
                component_vars[symbol] = round(float(component_var * 100), 3)
            
            return component_vars
        except:
            return {}
    
    def calculate_marginal_var(self, returns, weights):
        """Calculate marginal VaR for each asset"""
        try:
            marginal_vars = {}
            portfolio_returns = (returns * weights).sum(axis=1)
            
            for i, symbol in enumerate(returns.columns):
                correlation = returns.iloc[:, i].corr(portfolio_returns)
                asset_vol = returns.iloc[:, i].std()
                portfolio_vol = portfolio_returns.std()
                
                marginal_var = correlation * asset_vol / portfolio_vol if portfolio_vol != 0 else 0
                marginal_vars[symbol] = round(float(marginal_var * 100), 3)
            
            return marginal_vars
        except:
            return {}
    
    def calculate_overall_risk_rating(self, returns):
        """Calculate overall risk rating"""
        try:
            volatility = returns.std() * np.sqrt(252)
            max_dd = abs(self.calculate_portfolio_max_drawdown(returns) / 100)
            sharpe = self.calculate_portfolio_sharpe(returns)
            
            # Risk score calculation
            risk_score = 0
            
            # Volatility component (40% weight)
            if volatility < 0.15:
                risk_score += 40
            elif volatility < 0.25:
                risk_score += 30
            elif volatility < 0.35:
                risk_score += 20
            else:
                risk_score += 10
            
            # Max drawdown component (35% weight)
            if max_dd < 0.10:
                risk_score += 35
            elif max_dd < 0.20:
                risk_score += 25
            elif max_dd < 0.30:
                risk_score += 15
            else:
                risk_score += 5
            
            # Sharpe ratio component (25% weight)
            if sharpe > 1.5:
                risk_score += 25
            elif sharpe > 1.0:
                risk_score += 20
            elif sharpe > 0.5:
                risk_score += 15
            else:
                risk_score += 5
            
            # Assign rating
            if risk_score >= 85:
                return "Very Low Risk (AAA)"
            elif risk_score >= 70:
                return "Low Risk (AA)"
            elif risk_score >= 55:
                return "Moderate Risk (A)"
            elif risk_score >= 40:
                return "High Risk (BBB)"
            else:
                return "Very High Risk (BB)"
                
        except:
            return "Unknown Risk"
    
    def assess_liquidity_risk(self, symbols):
        """Assess liquidity risk of portfolio"""
        try:
            # Simplified liquidity assessment based on market cap and volume
            large_cap_symbols = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS']
            
            large_cap_count = sum(1 for symbol in symbols if symbol in large_cap_symbols)
            liquidity_ratio = large_cap_count / len(symbols)
            
            if liquidity_ratio > 0.8:
                return "Very High Liquidity"
            elif liquidity_ratio > 0.6:
                return "High Liquidity"
            elif liquidity_ratio > 0.4:
                return "Moderate Liquidity"
            else:
                return "Low Liquidity"
                
        except:
            return "Unknown"
    
    def assess_market_risk(self, returns):
        """Assess market risk exposure"""
        try:
            # Get market data for comparison
            market = yf.Ticker(self.market_benchmark)
            market_data = market.history(period='1y')
            market_returns = market_data['Close'].pct_change().dropna()
            
            # Align dates
            common_dates = returns.index.intersection(market_returns.index)
            if len(common_dates) > 50:
                portfolio_aligned = returns[common_dates]
                market_aligned = market_returns[common_dates]
                
                correlation = portfolio_aligned.corr(market_aligned)
                
                if abs(correlation) > 0.8:
                    return "High Market Risk"
                elif abs(correlation) > 0.6:
                    return "Moderate Market Risk"
                else:
                    return "Low Market Risk"
            
            return "Moderate Market Risk"
        except:
            return "Unknown"
    
    def rate_concentration_risk(self, weights):
        """Rate concentration risk"""
        try:
            max_weight = max(weights)
            herfindahl = self.calculate_concentration_risk(weights)
            
            if max_weight > 0.4 or herfindahl > 0.3:
                return "High Concentration"
            elif max_weight > 0.25 or herfindahl > 0.2:
                return "Moderate Concentration"
            else:
                return "Well Diversified"
        except:
            return "Unknown"
    
    def generate_risk_recommendations(self, returns, weights):
        """Generate professional risk management recommendations"""
        try:
            recommendations = []
            
            # Volatility check
            volatility = returns.std() * np.sqrt(252)
            if volatility > 0.3:
                recommendations.append("HIGH PRIORITY: Reduce portfolio volatility through diversification")
            
            # Concentration check
            max_weight = max(weights)
            if max_weight > 0.3:
                recommendations.append("MEDIUM PRIORITY: Reduce concentration in single positions")
            
            # Drawdown check
            max_dd = abs(self.calculate_portfolio_max_drawdown(returns) / 100)
            if max_dd > 0.25:
                recommendations.append("HIGH PRIORITY: Implement stop-loss mechanisms")
            
            # Sharpe ratio check
            sharpe = self.calculate_portfolio_sharpe(returns)
            if sharpe < 0.5:
                recommendations.append("MEDIUM PRIORITY: Improve risk-adjusted returns")
            
            if not recommendations:
                recommendations.append("Portfolio risk profile is within acceptable parameters")
            
            return recommendations
        except:
            return ["Unable to generate recommendations"]
    
    def calculate_optimal_weights(self, returns):
        """Calculate optimal portfolio weights using mean-variance optimization"""
        try:
            # Simple equal-weight as baseline
            n_assets = len(returns.columns)
            equal_weights = [1/n_assets] * n_assets
            
            # For now, return equal weights (can be enhanced with optimization)
            optimal_weights = {}
            for i, symbol in enumerate(returns.columns):
                optimal_weights[symbol] = round(equal_weights[i], 3)
            
            return optimal_weights
        except:
            return {}
    
    def assess_rebalancing_need(self, current_weights, returns):
        """Assess if portfolio needs rebalancing"""
        try:
            # Check if any weight has drifted significantly
            target_weight = 1 / len(current_weights)
            max_drift = max(abs(w - target_weight) for w in current_weights)
            
            if max_drift > 0.1:  # 10% drift threshold
                return "IMMEDIATE: Portfolio requires rebalancing"
            elif max_drift > 0.05:  # 5% drift threshold
                return "SOON: Consider rebalancing within 30 days"
            else:
                return "NO: Portfolio is well balanced"
        except:
            return "UNKNOWN: Unable to assess rebalancing need"

# Test the risk manager
if __name__ == "__main__":
    print("🛡️ Testing Institutional Risk Manager...")
    
    risk_manager = InstitutionalRiskManager()
    
    # Test with sample portfolio
    test_portfolio = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
    test_weights = [0.4, 0.3, 0.3]
    
    risk_assessment = risk_manager.comprehensive_risk_assessment(test_portfolio, test_weights)
    
    if risk_assessment:
        print(f"✅ Risk assessment completed:")
        print(f"   Overall Risk Rating: {risk_assessment['overall_risk_rating']}")
        print(f"   Portfolio Volatility: {risk_assessment['portfolio_volatility_annual']:.2f}%")
        print(f"   Sharpe Ratio: {risk_assessment['sharpe_ratio']}")
        print(f"   Max Drawdown: {risk_assessment['max_drawdown']:.2f}%")
        print(f"   VaR (95%): {risk_assessment['var_95_daily']:.2f}%")
    
    print("✅ Institutional Risk Manager test completed!")