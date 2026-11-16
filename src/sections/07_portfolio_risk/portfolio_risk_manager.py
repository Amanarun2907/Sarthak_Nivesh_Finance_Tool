"""
🛡️ ADVANCED PORTFOLIO & RISK MANAGEMENT SYSTEM
Real-time portfolio tracking, risk analysis, and optimization
Author: Aman Jain (B.Tech 2023-27)
"""

import sqlite3
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

from config import *

class PortfolioRiskManager:
    def __init__(self):
        self.setup_database()
        print("🛡️ Portfolio & Risk Management System initialized")
    
    def setup_database(self):
        """Setup portfolio database"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Portfolio holdings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    symbol TEXT NOT NULL,
                    company_name TEXT,
                    quantity REAL NOT NULL,
                    buy_price REAL NOT NULL,
                    buy_date DATE,
                    sector TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Portfolio transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    symbol TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    transaction_date DATE,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Watchlist table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    symbol TEXT NOT NULL,
                    company_name TEXT,
                    target_price REAL,
                    stop_loss REAL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            print("✅ Portfolio database setup complete")
            
        except Exception as e:
            print(f"❌ Database setup error: {e}")
    
    def add_holding(self, symbol, company_name, quantity, buy_price, buy_date=None, sector=None):
        """Add stock to portfolio"""
        try:
            if buy_date is None:
                buy_date = datetime.now().strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO portfolio_holdings 
                (symbol, company_name, quantity, buy_price, buy_date, sector)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (symbol, company_name, quantity, buy_price, buy_date, sector))
            
            # Also add to transactions
            cursor.execute("""
                INSERT INTO portfolio_transactions 
                (symbol, transaction_type, quantity, price, transaction_date)
                VALUES (?, 'BUY', ?, ?, ?)
            """, (symbol, quantity, buy_price, buy_date))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Added {quantity} shares of {company_name} at ₹{buy_price}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding holding: {e}")
            return False
    
    def get_portfolio_holdings(self, user_id='default'):
        """Get all portfolio holdings with current prices"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            df = pd.read_sql_query("""
                SELECT * FROM portfolio_holdings 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, conn, params=(user_id,))
            conn.close()
            
            if df.empty:
                return pd.DataFrame()
            
            # Fetch current prices
            holdings_data = []
            for _, row in df.iterrows():
                try:
                    sym = str(row['symbol']).strip()
                    ticker_sym = sym if sym.endswith(".NS") else sym + ".NS"
                    ticker = yf.Ticker(ticker_sym)
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        
                        invested = row['quantity'] * row['buy_price']
                        current_value = row['quantity'] * current_price
                        pnl = current_value - invested
                        pnl_pct = (pnl / invested) * 100
                        
                        holdings_data.append({
                            'id': row['id'],
                            'symbol': row['symbol'],
                            'company_name': row['company_name'],
                            'quantity': row['quantity'],
                            'buy_price': row['buy_price'],
                            'current_price': current_price,
                            'invested': invested,
                            'current_value': current_value,
                            'pnl': pnl,
                            'pnl_pct': pnl_pct,
                            'buy_date': row['buy_date'],
                            'sector': row['sector']
                        })
                except:
                    continue
            
            return pd.DataFrame(holdings_data)
            
        except Exception as e:
            print(f"❌ Error getting holdings: {e}")
            return pd.DataFrame()
    
    def calculate_portfolio_metrics(self, holdings_df):
        """Calculate comprehensive portfolio metrics"""
        if holdings_df.empty:
            return None
        
        try:
            total_invested = holdings_df['invested'].sum()
            total_current = holdings_df['current_value'].sum()
            total_pnl = total_current - total_invested
            total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
            
            # Calculate portfolio beta (market risk)
            portfolio_beta = self._calculate_portfolio_beta(holdings_df)
            
            # Calculate Sharpe ratio
            sharpe_ratio = self._calculate_sharpe_ratio(holdings_df)
            
            # Sector allocation
            sector_allocation = holdings_df.groupby('sector')['current_value'].sum().to_dict()
            
            # Top gainers and losers
            top_gainer = holdings_df.loc[holdings_df['pnl_pct'].idxmax()] if not holdings_df.empty else None
            top_loser = holdings_df.loc[holdings_df['pnl_pct'].idxmin()] if not holdings_df.empty else None
            
            metrics = {
                'total_invested': total_invested,
                'total_current': total_current,
                'total_pnl': total_pnl,
                'total_pnl_pct': total_pnl_pct,
                'portfolio_beta': portfolio_beta,
                'sharpe_ratio': sharpe_ratio,
                'sector_allocation': sector_allocation,
                'top_gainer': top_gainer,
                'top_loser': top_loser,
                'num_holdings': len(holdings_df),
                'diversification_score': self._calculate_diversification_score(holdings_df)
            }
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error calculating metrics: {e}")
            return None
    
    def _calculate_portfolio_beta(self, holdings_df):
        """Calculate portfolio beta against NIFTY 50"""
        try:
            # Get NIFTY 50 data
            nifty = yf.Ticker("^NSEI")
            nifty_hist = nifty.history(period="1y")
            
            if nifty_hist.empty:
                return 1.0
            
            nifty_returns = nifty_hist['Close'].pct_change().dropna()
            
            # Calculate weighted beta
            total_value = holdings_df['current_value'].sum()
            portfolio_beta = 0
            
            for _, holding in holdings_df.iterrows():
                try:
                    _sym = str(holding['symbol']).strip()
                    _tsym = _sym if _sym.endswith(".NS") else _sym + ".NS"
                    ticker = yf.Ticker(_tsym)
                    hist = ticker.history(period="1y")
                    
                    if not hist.empty and len(hist) > 20:
                        stock_returns = hist['Close'].pct_change().dropna()
                        
                        # Align dates
                        common_dates = stock_returns.index.intersection(nifty_returns.index)
                        if len(common_dates) > 20:
                            stock_ret = stock_returns.loc[common_dates]
                            market_ret = nifty_returns.loc[common_dates]
                            
                            # Calculate beta
                            covariance = np.cov(stock_ret, market_ret)[0][1]
                            market_variance = np.var(market_ret)
                            beta = covariance / market_variance if market_variance != 0 else 1.0
                            
                            # Weight by portfolio allocation
                            weight = holding['current_value'] / total_value
                            portfolio_beta += beta * weight
                except:
                    continue
            
            return portfolio_beta if portfolio_beta > 0 else 1.0
            
        except Exception as e:
            print(f"⚠️ Beta calculation error: {e}")
            return 1.0
    
    def _calculate_sharpe_ratio(self, holdings_df, risk_free_rate=0.07):
        """Calculate portfolio Sharpe ratio"""
        try:
            # Get historical returns for each stock
            returns_data = []
            weights = []
            total_value = holdings_df['current_value'].sum()
            
            for _, holding in holdings_df.iterrows():
                try:
                    _sym = str(holding['symbol']).strip()
                    _tsym = _sym if _sym.endswith(".NS") else _sym + ".NS"
                    ticker = yf.Ticker(_tsym)
                    hist = ticker.history(period="1y")
                    
                    if not hist.empty and len(hist) > 20:
                        returns = hist['Close'].pct_change().dropna()
                        returns_data.append(returns)
                        weights.append(holding['current_value'] / total_value)
                except:
                    continue
            
            if not returns_data:
                return 0.0
            
            # Calculate portfolio returns
            portfolio_returns = sum(ret * weight for ret, weight in zip(returns_data, weights))
            
            # Calculate Sharpe ratio
            excess_return = portfolio_returns.mean() * 252 - risk_free_rate  # Annualized
            portfolio_std = portfolio_returns.std() * np.sqrt(252)  # Annualized
            
            sharpe = excess_return / portfolio_std if portfolio_std != 0 else 0.0
            
            return sharpe
            
        except Exception as e:
            print(f"⚠️ Sharpe ratio calculation error: {e}")
            return 0.0
    
    def _calculate_diversification_score(self, holdings_df):
        """Calculate diversification score (0-100)"""
        try:
            # Factors: number of stocks, sector diversity, concentration
            num_stocks = len(holdings_df)
            num_sectors = holdings_df['sector'].nunique() if 'sector' in holdings_df.columns else 1
            
            # Concentration (Herfindahl index)
            total_value = holdings_df['current_value'].sum()
            weights = holdings_df['current_value'] / total_value
            herfindahl = (weights ** 2).sum()
            
            # Score components
            stock_score = min(num_stocks / 15 * 40, 40)  # Max 40 points for 15+ stocks
            sector_score = min(num_sectors / 8 * 30, 30)  # Max 30 points for 8+ sectors
            concentration_score = (1 - herfindahl) * 30  # Max 30 points for low concentration
            
            total_score = stock_score + sector_score + concentration_score
            
            return min(total_score, 100)
            
        except Exception as e:
            print(f"⚠️ Diversification score error: {e}")
            return 50.0
    
    def calculate_risk_metrics(self, holdings_df):
        """Calculate detailed risk metrics"""
        try:
            risk_metrics = {}
            
            # Value at Risk (VaR) - 95% confidence
            returns_data = []
            weights = []
            total_value = holdings_df['current_value'].sum()
            
            for _, holding in holdings_df.iterrows():
                try:
                    _sym = str(holding['symbol']).strip()
                    _tsym = _sym if _sym.endswith(".NS") else _sym + ".NS"
                    ticker = yf.Ticker(_tsym)
                    hist = ticker.history(period="1y")
                    
                    if not hist.empty:
                        returns = hist['Close'].pct_change().dropna()
                        returns_data.append(returns)
                        weights.append(holding['current_value'] / total_value)
                except:
                    continue
            
            if returns_data:
                # Portfolio returns
                portfolio_returns = sum(ret * weight for ret, weight in zip(returns_data, weights))
                
                # VaR calculation
                var_95 = np.percentile(portfolio_returns, 5)
                var_amount = total_value * abs(var_95)
                
                # Maximum drawdown
                cumulative_returns = (1 + portfolio_returns).cumprod()
                running_max = cumulative_returns.expanding().max()
                drawdown = (cumulative_returns - running_max) / running_max
                max_drawdown = drawdown.min()
                
                # Volatility
                volatility = portfolio_returns.std() * np.sqrt(252) * 100  # Annualized %
                
                risk_metrics = {
                    'var_95': var_amount,
                    'var_95_pct': var_95 * 100,
                    'max_drawdown': max_drawdown * 100,
                    'volatility': volatility,
                    'risk_level': self._assess_risk_level(volatility)
                }
            
            return risk_metrics
            
        except Exception as e:
            print(f"❌ Risk metrics error: {e}")
            return {}
    
    def _assess_risk_level(self, volatility):
        """Assess risk level based on volatility"""
        if volatility < 15:
            return "LOW"
        elif volatility < 25:
            return "MODERATE"
        elif volatility < 35:
            return "HIGH"
        else:
            return "VERY HIGH"
    
    def get_portfolio_recommendations(self, holdings_df):
        """Generate portfolio optimization recommendations"""
        try:
            recommendations = []
            
            if holdings_df.empty:
                return ["Start building your portfolio by adding stocks"]
            
            # Check diversification
            num_stocks = len(holdings_df)
            if num_stocks < 8:
                recommendations.append(f"📊 **Increase Diversification**: You have only {num_stocks} stocks. Consider adding 8-15 stocks for better risk management.")
            elif num_stocks > 25:
                recommendations.append(f"⚠️ **Over-Diversification**: You have {num_stocks} stocks. Consider consolidating to 15-20 quality stocks for better tracking.")
            
            # Check sector concentration
            if 'sector' in holdings_df.columns:
                sector_allocation = holdings_df.groupby('sector')['current_value'].sum()
                total_value = holdings_df['current_value'].sum()
                max_sector_pct = (sector_allocation.max() / total_value) * 100
                
                if max_sector_pct > 40:
                    max_sector = sector_allocation.idxmax()
                    recommendations.append(f"⚠️ **Sector Concentration**: {max_sector_pct:.1f}% in {max_sector}. Reduce to below 30% for better diversification.")
                
                # Suggest underweight sectors
                sector_pcts = (sector_allocation / total_value * 100).to_dict()
                underweight_sectors = []
                
                if sector_pcts.get('IT', 0) < 10:
                    underweight_sectors.append('IT')
                if sector_pcts.get('Banking', 0) < 15:
                    underweight_sectors.append('Banking')
                if sector_pcts.get('Pharma', 0) < 5:
                    underweight_sectors.append('Pharma')
                
                if underweight_sectors:
                    recommendations.append(f"💡 **Sector Opportunity**: Consider adding exposure to {', '.join(underweight_sectors)} sectors.")
            
            # Check individual stock concentration
            max_holding_pct = (holdings_df['current_value'].max() / holdings_df['current_value'].sum()) * 100
            if max_holding_pct > 20:
                max_stock = holdings_df.loc[holdings_df['current_value'].idxmax(), 'company_name']
                recommendations.append(f"🎯 **Stock Concentration**: {max_holding_pct:.1f}% in {max_stock}. Consider reducing to below 15%.")
            
            # Check for losers
            big_losers = holdings_df[holdings_df['pnl_pct'] < -20]
            if not big_losers.empty:
                loser_names = ', '.join(big_losers['company_name'].head(3).tolist())
                recommendations.append(f"🔴 **Review Losers**: {len(big_losers)} stocks down >20% ({loser_names}). Consider stop-loss or averaging down if fundamentals strong.")
            
            # Check for big winners
            big_winners = holdings_df[holdings_df['pnl_pct'] > 50]
            if not big_winners.empty:
                winner_names = ', '.join(big_winners['company_name'].head(3).tolist())
                recommendations.append(f"🎉 **Book Profits**: {len(big_winners)} stocks up >50% ({winner_names}). Consider partial profit booking to secure gains.")
            
            # Check for stagnant stocks
            stagnant = holdings_df[(holdings_df['pnl_pct'] > -5) & (holdings_df['pnl_pct'] < 5)]
            if len(stagnant) > len(holdings_df) * 0.4:
                recommendations.append(f"📊 **Stagnant Holdings**: {len(stagnant)} stocks showing minimal movement. Review and consider rebalancing.")
            
            # Portfolio value recommendations
            total_value = holdings_df['current_value'].sum()
            if total_value < 50000:
                recommendations.append(f"💰 **Build Capital**: Portfolio value ₹{total_value:,.0f}. Consider increasing investment to ₹50,000+ for better diversification.")
            elif total_value > 1000000:
                recommendations.append(f"🏆 **Strong Portfolio**: Portfolio value ₹{total_value:,.0f}. Consider professional wealth management services.")
            
            # Risk-based recommendations
            total_pnl_pct = holdings_df['pnl_pct'].mean()
            if total_pnl_pct < -10:
                recommendations.append(f"⚠️ **High Losses**: Average loss of {total_pnl_pct:.1f}%. Review investment thesis and consider cutting losses on weak positions.")
            elif total_pnl_pct > 30:
                recommendations.append(f"🚀 **Excellent Returns**: Average gain of {total_pnl_pct:.1f}%. Consider booking partial profits and rebalancing.")
            
            if not recommendations:
                recommendations.append("✅ **Well Balanced**: Your portfolio shows good diversification and risk management!")
            
            return recommendations
            
        except Exception as e:
            print(f"❌ Recommendations error: {e}")
            return ["Unable to generate recommendations"]
    
    def delete_holding(self, holding_id):
        """Delete a holding from portfolio"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM portfolio_holdings WHERE id = ?", (holding_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error deleting holding: {e}")
            return False
    
    def clear_portfolio(self, user_id='default'):
        """Clear entire portfolio"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM portfolio_holdings WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"❌ Error clearing portfolio: {e}")
            return False
    
    def get_sector_wise_analysis(self, holdings_df):
        """Get detailed sector-wise analysis"""
        try:
            if holdings_df.empty or 'sector' not in holdings_df.columns:
                return None
            
            sector_analysis = holdings_df.groupby('sector').agg({
                'invested': 'sum',
                'current_value': 'sum',
                'pnl': 'sum',
                'quantity': 'count'
            }).reset_index()
            
            sector_analysis.columns = ['sector', 'invested', 'current_value', 'pnl', 'num_stocks']
            sector_analysis['pnl_pct'] = (sector_analysis['pnl'] / sector_analysis['invested']) * 100
            sector_analysis['allocation_pct'] = (sector_analysis['current_value'] / sector_analysis['current_value'].sum()) * 100
            
            return sector_analysis.sort_values('current_value', ascending=False)
            
        except Exception as e:
            print(f"❌ Sector analysis error: {e}")
            return None
    
    def calculate_correlation_matrix(self, holdings_df):
        """Calculate correlation between portfolio stocks"""
        try:
            if holdings_df.empty or len(holdings_df) < 2:
                return None
            
            # Fetch historical data for all stocks
            returns_data = {}
            
            for _, holding in holdings_df.iterrows():
                try:
                    _sym = str(holding['symbol']).strip()
                    _tsym = _sym if _sym.endswith(".NS") else _sym + ".NS"
                    ticker = yf.Ticker(_tsym)
                    hist = ticker.history(period="6mo")
                    
                    if not hist.empty and len(hist) > 20:
                        returns = hist['Close'].pct_change().dropna()
                        returns_data[holding['company_name']] = returns
                except:
                    continue
            
            if len(returns_data) < 2:
                return None
            
            # Create correlation matrix
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            
            return correlation_matrix
            
        except Exception as e:
            print(f"❌ Correlation matrix error: {e}")
            return None
    
    def get_portfolio_timeline(self, holdings_df):
        """Get portfolio performance over time using a single batch fetch per stock."""
        try:
            if holdings_df.empty:
                return None

            earliest_date = pd.to_datetime(holdings_df['buy_date']).min()
            start_str = earliest_date.strftime('%Y-%m-%d')

            # Fetch full history for every stock in ONE call each (not per-day)
            price_histories = {}
            for _, holding in holdings_df.iterrows():
                try:
                    _sym = str(holding['symbol']).strip()
                    _tsym = _sym if _sym.endswith(".NS") else _sym + ".NS"
                    ticker = yf.Ticker(_tsym)
                    hist = ticker.history(start=start_str)
                    if not hist.empty:
                        price_histories[holding['symbol']] = {
                            'closes': hist['Close'],
                            'quantity': holding['quantity'],
                            'buy_date': pd.to_datetime(holding['buy_date'])
                        }
                except Exception:
                    continue

            if not price_histories:
                return None

            # Build a combined date index
            all_dates = sorted(set(
                date for info in price_histories.values()
                for date in info['closes'].index
            ))

            timeline = []
            for date in all_dates:
                total_value = 0.0
                for symbol, info in price_histories.items():
                    if date >= info['buy_date'].tz_localize(date.tzinfo) if date.tzinfo else info['buy_date']:
                        closes = info['closes']
                        # Get closest available price on or before this date
                        available = closes[closes.index <= date]
                        if not available.empty:
                            total_value += float(available.iloc[-1]) * info['quantity']
                if total_value > 0:
                    timeline.append({'date': date, 'value': total_value})

            return pd.DataFrame(timeline) if timeline else None

        except Exception as e:
            print(f"❌ Timeline error: {e}")
            return None
    
    def get_top_movers(self, holdings_df, top_n=5):
        """Get top gainers and losers"""
        try:
            if holdings_df.empty:
                return None, None
            
            sorted_df = holdings_df.sort_values('pnl_pct', ascending=False)
            
            top_gainers = sorted_df.head(top_n)[[
                'company_name', 'symbol', 'pnl_pct', 'pnl', 'current_value'
            ]]
            
            top_losers = sorted_df.tail(top_n)[[
                'company_name', 'symbol', 'pnl_pct', 'pnl', 'current_value'
            ]]
            
            return top_gainers, top_losers
            
        except Exception as e:
            print(f"❌ Top movers error: {e}")
            return None, None


def main():
    """Test the portfolio system"""
    print("🛡️ Testing Portfolio & Risk Management System")
    print("="*60)
    
    pm = PortfolioRiskManager()
    
    # Test adding holdings
    pm.add_holding("RELIANCE", "Reliance Industries", 10, 2500, sector="Energy")
    pm.add_holding("TCS", "Tata Consultancy Services", 5, 3500, sector="IT")
    pm.add_holding("HDFCBANK", "HDFC Bank", 15, 1600, sector="Banking")
    
    # Get holdings
    holdings = pm.get_portfolio_holdings()
    print(f"\n✅ Portfolio has {len(holdings)} holdings")
    
    # Calculate metrics
    metrics = pm.calculate_portfolio_metrics(holdings)
    if metrics:
        print(f"\n📊 Portfolio Metrics:")
        print(f"   Total Invested: ₹{metrics['total_invested']:,.0f}")
        print(f"   Current Value: ₹{metrics['total_current']:,.0f}")
        print(f"   P&L: ₹{metrics['total_pnl']:,.0f} ({metrics['total_pnl_pct']:.2f}%)")
        print(f"   Beta: {metrics['portfolio_beta']:.2f}")
        print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"   Diversification Score: {metrics['diversification_score']:.1f}/100")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    main()
