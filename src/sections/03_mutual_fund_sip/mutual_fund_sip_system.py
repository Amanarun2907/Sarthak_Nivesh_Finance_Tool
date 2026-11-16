# सार्थक निवेश - Comprehensive Mutual Fund & SIP System
# Advanced Mutual Fund Analysis, SIP Optimization & Recommendations
# Team: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import sqlite3
import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings('ignore')
from config import *

class MutualFundSIPSystem:
    def __init__(self):
        self.setup_mf_database()
        print("💰 Comprehensive Mutual Fund & SIP System initialized")
    
    def setup_mf_database(self):
        """Setup mutual fund and SIP database tables"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Mutual fund master data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mutual_funds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scheme_code TEXT UNIQUE NOT NULL,
                    scheme_name TEXT NOT NULL,
                    fund_house TEXT NOT NULL,
                    category TEXT NOT NULL,
                    sub_category TEXT,
                    nav REAL,
                    nav_date DATE,
                    expense_ratio REAL,
                    aum_crores REAL,
                    fund_manager TEXT,
                    inception_date DATE,
                    min_investment REAL,
                    min_sip REAL,
                    exit_load TEXT,
                    risk_rating TEXT,
                    return_1y REAL,
                    return_3y REAL,
                    return_5y REAL,
                    alpha REAL,
                    beta REAL,
                    sharpe_ratio REAL,
                    sortino_ratio REAL,
                    standard_deviation REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # SIP recommendations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sip_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_profile TEXT NOT NULL,
                    risk_tolerance TEXT NOT NULL,
                    investment_horizon TEXT NOT NULL,
                    monthly_amount REAL NOT NULL,
                    recommended_funds TEXT NOT NULL,
                    allocation_strategy TEXT NOT NULL,
                    expected_return REAL,
                    projected_value REAL,
                    reasoning TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # SIP performance tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sip_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scheme_code TEXT NOT NULL,
                    sip_amount REAL NOT NULL,
                    start_date DATE NOT NULL,
                    current_value REAL,
                    invested_amount REAL,
                    returns_absolute REAL,
                    returns_percentage REAL,
                    xirr REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Fund comparison analysis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fund_comparison (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    comparison_name TEXT NOT NULL,
                    fund_codes TEXT NOT NULL,
                    comparison_metrics TEXT NOT NULL,
                    winner_fund TEXT,
                    analysis_summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ Mutual Fund & SIP database setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up MF database: {str(e)}")
    
    def collect_mutual_fund_data(self):
        """Collect comprehensive mutual fund data"""
        try:
            print("📊 Collecting comprehensive mutual fund data...")
            
            # Sample comprehensive mutual fund data (in real implementation, would use MF APIs)
            mutual_funds_data = [
                {
                    'scheme_code': 'MF001',
                    'scheme_name': 'SBI Bluechip Fund - Direct Growth',
                    'fund_house': 'SBI Mutual Fund',
                    'category': 'Equity',
                    'sub_category': 'Large Cap',
                    'nav': 85.45,
                    'expense_ratio': 0.98,
                    'aum_crores': 15420.50,
                    'fund_manager': 'Dinesh Ahuja',
                    'min_investment': 5000,
                    'min_sip': 500,
                    'exit_load': '1% if redeemed within 1 year',
                    'risk_rating': 'Moderate',
                    'return_1y': 18.45,
                    'return_3y': 15.20,
                    'return_5y': 12.80,
                    'alpha': 2.15,
                    'beta': 0.95,
                    'sharpe_ratio': 1.25,
                    'standard_deviation': 16.80
                },
                {
                    'scheme_code': 'MF002',
                    'scheme_name': 'HDFC Mid-Cap Opportunities Fund - Direct Growth',
                    'fund_house': 'HDFC Mutual Fund',
                    'category': 'Equity',
                    'sub_category': 'Mid Cap',
                    'nav': 142.30,
                    'expense_ratio': 1.25,
                    'aum_crores': 8750.25,
                    'fund_manager': 'Chirag Setalvad',
                    'min_investment': 5000,
                    'min_sip': 1000,
                    'exit_load': '1% if redeemed within 1 year',
                    'risk_rating': 'High',
                    'return_1y': 25.60,
                    'return_3y': 18.90,
                    'return_5y': 16.45,
                    'alpha': 4.20,
                    'beta': 1.15,
                    'sharpe_ratio': 1.45,
                    'standard_deviation': 22.50
                },
                {
                    'scheme_code': 'MF003',
                    'scheme_name': 'ICICI Prudential Balanced Advantage Fund - Direct Growth',
                    'fund_house': 'ICICI Prudential Mutual Fund',
                    'category': 'Hybrid',
                    'sub_category': 'Dynamic Asset Allocation',
                    'nav': 68.75,
                    'expense_ratio': 1.05,
                    'aum_crores': 12350.80,
                    'fund_manager': 'Ihab Dalwai',
                    'min_investment': 5000,
                    'min_sip': 1000,
                    'exit_load': '1% if redeemed within 1 year',
                    'risk_rating': 'Moderate',
                    'return_1y': 14.25,
                    'return_3y': 12.80,
                    'return_5y': 11.20,
                    'alpha': 1.80,
                    'beta': 0.75,
                    'sharpe_ratio': 1.15,
                    'standard_deviation': 12.40
                },
                {
                    'scheme_code': 'MF004',
                    'scheme_name': 'Axis Long Term Equity Fund - Direct Growth',
                    'fund_house': 'Axis Mutual Fund',
                    'category': 'Equity',
                    'sub_category': 'ELSS',
                    'nav': 95.20,
                    'expense_ratio': 1.15,
                    'aum_crores': 6890.45,
                    'fund_manager': 'Jinesh Gopani',
                    'min_investment': 500,
                    'min_sip': 500,
                    'exit_load': 'Lock-in period of 3 years',
                    'risk_rating': 'Moderate to High',
                    'return_1y': 20.15,
                    'return_3y': 16.50,
                    'return_5y': 14.20,
                    'alpha': 3.10,
                    'beta': 1.05,
                    'sharpe_ratio': 1.35,
                    'standard_deviation': 18.90
                },
                {
                    'scheme_code': 'MF005',
                    'scheme_name': 'Franklin India Ultra Short Bond Fund - Direct Growth',
                    'fund_house': 'Franklin Templeton Mutual Fund',
                    'category': 'Debt',
                    'sub_category': 'Ultra Short Duration',
                    'nav': 12.85,
                    'expense_ratio': 0.45,
                    'aum_crores': 4520.30,
                    'fund_manager': 'Murthy Nagarajan',
                    'min_investment': 5000,
                    'min_sip': 1000,
                    'exit_load': 'Nil',
                    'risk_rating': 'Low',
                    'return_1y': 6.80,
                    'return_3y': 7.20,
                    'return_5y': 7.50,
                    'alpha': 0.50,
                    'beta': 0.15,
                    'sharpe_ratio': 2.10,
                    'standard_deviation': 2.80
                },
                {
                    'scheme_code': 'MF006',
                    'scheme_name': 'Mirae Asset Large Cap Fund - Direct Growth',
                    'fund_house': 'Mirae Asset Mutual Fund',
                    'category': 'Equity',
                    'sub_category': 'Large Cap',
                    'nav': 78.90,
                    'expense_ratio': 0.85,
                    'aum_crores': 9850.75,
                    'fund_manager': 'Neelesh Surana',
                    'min_investment': 5000,
                    'min_sip': 1000,
                    'exit_load': '1% if redeemed within 1 year',
                    'risk_rating': 'Moderate',
                    'return_1y': 19.80,
                    'return_3y': 16.20,
                    'return_5y': 13.50,
                    'alpha': 2.80,
                    'beta': 0.92,
                    'sharpe_ratio': 1.40,
                    'standard_deviation': 15.60
                }
            ]
            
            # Insert data into database
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            for fund in mutual_funds_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO mutual_funds 
                    (scheme_code, scheme_name, fund_house, category, sub_category, nav, 
                     expense_ratio, aum_crores, fund_manager, min_investment, min_sip, 
                     exit_load, risk_rating, return_1y, return_3y, return_5y, alpha, 
                     beta, sharpe_ratio, standard_deviation, nav_date, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fund['scheme_code'], fund['scheme_name'], fund['fund_house'],
                    fund['category'], fund['sub_category'], fund['nav'],
                    fund['expense_ratio'], fund['aum_crores'], fund['fund_manager'],
                    fund['min_investment'], fund['min_sip'], fund['exit_load'],
                    fund['risk_rating'], fund['return_1y'], fund['return_3y'],
                    fund['return_5y'], fund['alpha'], fund['beta'],
                    fund['sharpe_ratio'], fund['standard_deviation'],
                    datetime.now().date(), datetime.now()
                ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Collected data for {len(mutual_funds_data)} mutual funds")
            return mutual_funds_data
            
        except Exception as e:
            print(f"❌ Error collecting mutual fund data: {str(e)}")
            return []
    
    def analyze_sip_performance(self, scheme_code, monthly_amount, start_date, current_date=None):
        """Analyze SIP performance with real calculations"""
        try:
            if current_date is None:
                current_date = datetime.now().date()
            
            print(f"📈 Analyzing SIP performance for {scheme_code}...")
            
            # Calculate SIP performance (simplified simulation)
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            current_dt = current_date if isinstance(current_date, type(start_dt)) else datetime.strptime(current_date, '%Y-%m-%d').date()
            
            # Calculate number of months
            months_invested = (current_dt.year - start_dt.year) * 12 + (current_dt.month - start_dt.month)
            
            if months_invested <= 0:
                return None
            
            # Get fund data
            conn = sqlite3.connect(DATABASE_PATH)
            fund_data = pd.read_sql_query(
                "SELECT * FROM mutual_funds WHERE scheme_code = ?", 
                conn, params=[scheme_code]
            )
            conn.close()
            
            if fund_data.empty:
                return None
            
            fund = fund_data.iloc[0]
            
            # Simulate SIP performance based on historical returns
            annual_return = fund['return_3y'] / 100 if fund['return_3y'] else 0.12
            monthly_return = (1 + annual_return) ** (1/12) - 1
            
            # Calculate SIP maturity value using compound interest
            total_invested = monthly_amount * months_invested
            
            # SIP future value calculation
            if monthly_return > 0:
                future_value = monthly_amount * (((1 + monthly_return) ** months_invested - 1) / monthly_return) * (1 + monthly_return)
            else:
                future_value = total_invested
            
            # Calculate returns
            absolute_return = future_value - total_invested
            percentage_return = (absolute_return / total_invested) * 100 if total_invested > 0 else 0
            
            # Calculate XIRR (simplified)
            annual_return_achieved = ((future_value / total_invested) ** (12 / months_invested) - 1) * 100 if months_invested > 0 else 0
            
            performance = {
                'scheme_code': scheme_code,
                'scheme_name': fund['scheme_name'],
                'monthly_amount': monthly_amount,
                'months_invested': months_invested,
                'total_invested': total_invested,
                'current_value': future_value,
                'absolute_return': absolute_return,
                'percentage_return': percentage_return,
                'annualized_return': annual_return_achieved,
                'fund_category': fund['category'],
                'fund_subcategory': fund['sub_category']
            }
            
            return performance
            
        except Exception as e:
            print(f"❌ Error analyzing SIP performance: {str(e)}")
            return None
    
    def recommend_sip_portfolio(self, user_profile):
        """Generate comprehensive SIP portfolio recommendations"""
        try:
            print("💡 Generating SIP portfolio recommendations...")
            
            monthly_amount = user_profile.get('monthly_amount', 10000)
            risk_tolerance = user_profile.get('risk_tolerance', 'moderate')
            investment_horizon = user_profile.get('investment_horizon', '5-10 years')
            age = user_profile.get('age', 30)
            
            # Get available funds
            conn = sqlite3.connect(DATABASE_PATH)
            funds_df = pd.read_sql_query("SELECT * FROM mutual_funds", conn)
            conn.close()
            
            if funds_df.empty:
                return None
            
            # Asset allocation based on age and risk tolerance
            equity_allocation = self.calculate_equity_allocation(age, risk_tolerance)
            debt_allocation = 100 - equity_allocation
            
            recommendations = []
            
            # Equity allocation
            if equity_allocation > 0:
                equity_amount = (monthly_amount * equity_allocation) / 100
                
                # Large cap allocation (40-60% of equity)
                large_cap_funds = funds_df[funds_df['sub_category'] == 'Large Cap'].sort_values('sharpe_ratio', ascending=False)
                if not large_cap_funds.empty:
                    large_cap_allocation = equity_amount * 0.5
                    recommendations.append({
                        'fund': large_cap_funds.iloc[0],
                        'allocation_amount': large_cap_allocation,
                        'allocation_percentage': (large_cap_allocation / monthly_amount) * 100,
                        'reason': 'Stable large-cap exposure for consistent returns'
                    })
                
                # Mid cap allocation (20-40% of equity) - only for moderate to aggressive investors
                if risk_tolerance in ['moderate', 'aggressive']:
                    mid_cap_funds = funds_df[funds_df['sub_category'] == 'Mid Cap'].sort_values('return_3y', ascending=False)
                    if not mid_cap_funds.empty:
                        mid_cap_allocation = equity_amount * 0.3
                        recommendations.append({
                            'fund': mid_cap_funds.iloc[0],
                            'allocation_amount': mid_cap_allocation,
                            'allocation_percentage': (mid_cap_allocation / monthly_amount) * 100,
                            'reason': 'Mid-cap exposure for higher growth potential'
                        })
                
                # ELSS allocation for tax saving
                elss_funds = funds_df[funds_df['sub_category'] == 'ELSS'].sort_values('return_3y', ascending=False)
                if not elss_funds.empty:
                    elss_allocation = min(equity_amount * 0.2, 12500)  # Max 1.5L per year
                    recommendations.append({
                        'fund': elss_funds.iloc[0],
                        'allocation_amount': elss_allocation,
                        'allocation_percentage': (elss_allocation / monthly_amount) * 100,
                        'reason': 'Tax-saving investment under Section 80C'
                    })
            
            # Debt allocation
            if debt_allocation > 0:
                debt_amount = (monthly_amount * debt_allocation) / 100
                debt_funds = funds_df[funds_df['category'] == 'Debt'].sort_values('return_3y', ascending=False)
                
                if not debt_funds.empty:
                    recommendations.append({
                        'fund': debt_funds.iloc[0],
                        'allocation_amount': debt_amount,
                        'allocation_percentage': (debt_amount / monthly_amount) * 100,
                        'reason': 'Debt allocation for stability and capital preservation'
                    })
            
            # Hybrid funds for balanced approach
            if risk_tolerance == 'conservative':
                hybrid_funds = funds_df[funds_df['category'] == 'Hybrid'].sort_values('sharpe_ratio', ascending=False)
                if not hybrid_funds.empty:
                    hybrid_allocation = monthly_amount * 0.3
                    recommendations.append({
                        'fund': hybrid_funds.iloc[0],
                        'allocation_amount': hybrid_allocation,
                        'allocation_percentage': (hybrid_allocation / monthly_amount) * 100,
                        'reason': 'Balanced hybrid fund for moderate risk-return profile'
                    })
            
            # Calculate expected returns and projections
            total_expected_return = 0
            total_allocation = 0
            
            for rec in recommendations:
                fund_return = rec['fund']['return_3y'] if rec['fund']['return_3y'] else 12
                weight = rec['allocation_percentage'] / 100
                total_expected_return += fund_return * weight
                total_allocation += rec['allocation_percentage']
            
            # Normalize allocations if they don't add up to 100%
            if total_allocation != 100 and recommendations:
                adjustment_factor = 100 / total_allocation
                for rec in recommendations:
                    rec['allocation_percentage'] *= adjustment_factor
                    rec['allocation_amount'] *= adjustment_factor
            
            # Calculate projections
            years = self.extract_years_from_horizon(investment_horizon)
            projected_value = self.calculate_sip_projection(monthly_amount, total_expected_return, years)
            
            portfolio_recommendation = {
                'recommendations': recommendations,
                'total_monthly_amount': monthly_amount,
                'equity_allocation': equity_allocation,
                'debt_allocation': debt_allocation,
                'expected_annual_return': total_expected_return,
                'investment_horizon_years': years,
                'projected_value': projected_value,
                'total_investment': monthly_amount * 12 * years,
                'expected_gain': projected_value - (monthly_amount * 12 * years)
            }
            
            return portfolio_recommendation
            
        except Exception as e:
            print(f"❌ Error generating SIP recommendations: {str(e)}")
            return None
    
    def calculate_equity_allocation(self, age, risk_tolerance):
        """Calculate optimal equity allocation based on age and risk tolerance"""
        # Base allocation using age rule: 100 - age
        base_equity = max(20, min(80, 100 - age))
        
        # Adjust based on risk tolerance
        risk_adjustments = {
            'conservative': -20,
            'moderate': 0,
            'aggressive': +15
        }
        
        adjustment = risk_adjustments.get(risk_tolerance, 0)
        equity_allocation = max(10, min(90, base_equity + adjustment))
        
        return equity_allocation
    
    def extract_years_from_horizon(self, horizon):
        """Extract number of years from investment horizon string"""
        horizon_mapping = {
            '1-3 years': 2,
            '3-5 years': 4,
            '5-10 years': 7,
            '10+ years': 15
        }
        return horizon_mapping.get(horizon, 7)
    
    def calculate_sip_projection(self, monthly_amount, annual_return_percent, years):
        """Calculate SIP maturity value"""
        try:
            monthly_return = (annual_return_percent / 100) / 12
            months = years * 12
            
            if monthly_return > 0:
                future_value = monthly_amount * (((1 + monthly_return) ** months - 1) / monthly_return) * (1 + monthly_return)
            else:
                future_value = monthly_amount * months
            
            return future_value
            
        except Exception as e:
            print(f"❌ Error calculating SIP projection: {str(e)}")
            return monthly_amount * 12 * years
    
    def compare_mutual_funds(self, fund_codes, comparison_type='comprehensive'):
        """Compare multiple mutual funds across various parameters"""
        try:
            print(f"🔍 Comparing mutual funds: {fund_codes}")
            
            conn = sqlite3.connect(DATABASE_PATH)
            
            # Get fund data
            placeholders = ','.join(['?' for _ in fund_codes])
            query = f"SELECT * FROM mutual_funds WHERE scheme_code IN ({placeholders})"
            funds_df = pd.read_sql_query(query, conn, params=fund_codes)
            conn.close()
            
            if funds_df.empty:
                return None
            
            comparison_metrics = {}
            
            # Performance comparison
            performance_metrics = ['return_1y', 'return_3y', 'return_5y', 'sharpe_ratio', 'alpha']
            for metric in performance_metrics:
                comparison_metrics[metric] = funds_df[['scheme_name', metric]].set_index('scheme_name')[metric].to_dict()
            
            # Risk comparison
            risk_metrics = ['standard_deviation', 'beta', 'expense_ratio']
            for metric in risk_metrics:
                comparison_metrics[metric] = funds_df[['scheme_name', metric]].set_index('scheme_name')[metric].to_dict()
            
            # Fund characteristics
            char_metrics = ['aum_crores', 'min_sip', 'fund_house', 'category']
            for metric in char_metrics:
                comparison_metrics[metric] = funds_df[['scheme_name', metric]].set_index('scheme_name')[metric].to_dict()
            
            # Determine winner based on comprehensive scoring
            winner = self.determine_fund_winner(funds_df)
            
            comparison_result = {
                'funds_compared': funds_df['scheme_name'].tolist(),
                'comparison_metrics': comparison_metrics,
                'winner': winner,
                'comparison_summary': self.generate_comparison_summary(funds_df, winner)
            }
            
            return comparison_result
            
        except Exception as e:
            print(f"❌ Error comparing mutual funds: {str(e)}")
            return None
    
    def determine_fund_winner(self, funds_df):
        """Determine the best fund based on comprehensive scoring"""
        try:
            scores = {}
            
            for _, fund in funds_df.iterrows():
                score = 0
                
                # Performance score (40% weight)
                if fund['return_3y']:
                    score += (fund['return_3y'] / 20) * 40  # Normalize to 40 points max
                
                # Risk-adjusted returns (30% weight)
                if fund['sharpe_ratio']:
                    score += min(fund['sharpe_ratio'] * 15, 30)  # Max 30 points
                
                # Cost efficiency (20% weight)
                if fund['expense_ratio']:
                    score += max(0, (2 - fund['expense_ratio']) * 10)  # Lower expense ratio = higher score
                
                # Fund size and stability (10% weight)
                if fund['aum_crores']:
                    score += min(fund['aum_crores'] / 1000, 10)  # Larger AUM = higher score (max 10)
                
                scores[fund['scheme_name']] = score
            
            winner = max(scores, key=scores.get) if scores else None
            return winner
            
        except Exception as e:
            print(f"❌ Error determining winner: {str(e)}")
            return None
    
    def generate_comparison_summary(self, funds_df, winner):
        """Generate a comprehensive comparison summary"""
        try:
            summary = []
            
            if winner:
                winner_fund = funds_df[funds_df['scheme_name'] == winner].iloc[0]
                summary.append(f"🏆 Winner: {winner}")
                summary.append(f"📈 3-Year Return: {winner_fund['return_3y']:.2f}%")
                summary.append(f"📊 Sharpe Ratio: {winner_fund['sharpe_ratio']:.2f}")
                summary.append(f"💰 Expense Ratio: {winner_fund['expense_ratio']:.2f}%")
            
            # Performance analysis
            best_performer = funds_df.loc[funds_df['return_3y'].idxmax()]
            summary.append(f"🚀 Best 3Y Performance: {best_performer['scheme_name']} ({best_performer['return_3y']:.2f}%)")
            
            # Risk analysis
            lowest_risk = funds_df.loc[funds_df['standard_deviation'].idxmin()]
            summary.append(f"🛡️ Lowest Risk: {lowest_risk['scheme_name']} ({lowest_risk['standard_deviation']:.2f}% volatility)")
            
            # Cost analysis
            lowest_cost = funds_df.loc[funds_df['expense_ratio'].idxmin()]
            summary.append(f"💸 Lowest Cost: {lowest_cost['scheme_name']} ({lowest_cost['expense_ratio']:.2f}% expense ratio)")
            
            return '; '.join(summary)
            
        except Exception as e:
            print(f"❌ Error generating summary: {str(e)}")
            return "Comparison completed successfully"

# Test the Mutual Fund & SIP System
if __name__ == "__main__":
    print("💰 Testing Mutual Fund & SIP System...")
    
    mf_system = MutualFundSIPSystem()
    
    # Collect mutual fund data
    funds_data = mf_system.collect_mutual_fund_data()
    
    if funds_data:
        print(f"✅ Collected data for {len(funds_data)} mutual funds")
        
        # Test SIP recommendation
        user_profile = {
            'monthly_amount': 15000,
            'risk_tolerance': 'moderate',
            'investment_horizon': '5-10 years',
            'age': 28
        }
        
        recommendations = mf_system.recommend_sip_portfolio(user_profile)
        
        if recommendations:
            print(f"💡 SIP Recommendations Generated:")
            print(f"   Expected Return: {recommendations['expected_annual_return']:.2f}%")
            print(f"   Projected Value: ₹{recommendations['projected_value']:,.0f}")
            print(f"   Number of Funds: {len(recommendations['recommendations'])}")
    
    print("✅ Mutual Fund & SIP System test completed!")