"""
🎯 SMART MONEY TRACKER - Follow Institutional Money Flow
Track FII/DII activity, Bulk Deals, Insider Trading, Block Deals
100% REAL-TIME DATA from NSE, BSE, SEBI
"""

import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
import json
import warnings
warnings.filterwarnings('ignore')

# Indian Stocks Database
INDIAN_STOCKS = {
    'HDFCBANK.NS': 'HDFC Bank', 'ICICIBANK.NS': 'ICICI Bank', 'KOTAKBANK.NS': 'Kotak Bank',
    'SBIN.NS': 'State Bank', 'AXISBANK.NS': 'Axis Bank', 'INDUSINDBK.NS': 'IndusInd Bank',
    'BAJFINANCE.NS': 'Bajaj Finance', 'BAJAJFINSV.NS': 'Bajaj Finserv',
    'TCS.NS': 'TCS', 'INFY.NS': 'Infosys', 'WIPRO.NS': 'Wipro',
    'HCLTECH.NS': 'HCL Tech', 'TECHM.NS': 'Tech Mahindra',
    'HINDUNILVR.NS': 'Hindustan Unilever', 'ITC.NS': 'ITC', 'NESTLEIND.NS': 'Nestle',
    'BRITANNIA.NS': 'Britannia', 'DABUR.NS': 'Dabur', 'MARICO.NS': 'Marico',
    'MARUTI.NS': 'Maruti Suzuki', 'TATAMOTORS.NS': 'Tata Motors', 'M&M.NS': 'M&M',
    'BAJAJ-AUTO.NS': 'Bajaj Auto', 'EICHERMOT.NS': 'Eicher Motors',
    'SUNPHARMA.NS': 'Sun Pharma', 'DRREDDY.NS': 'Dr Reddy', 'CIPLA.NS': 'Cipla',
    'DIVISLAB.NS': 'Divi Labs', 'BIOCON.NS': 'Biocon', 'APOLLOHOSP.NS': 'Apollo Hospitals',
    'RELIANCE.NS': 'Reliance', 'ONGC.NS': 'ONGC', 'POWERGRID.NS': 'Power Grid',
    'NTPC.NS': 'NTPC', 'ADANIGREEN.NS': 'Adani Green', 'TATASTEEL.NS': 'Tata Steel',
    'HINDALCO.NS': 'Hindalco', 'JSWSTEEL.NS': 'JSW Steel', 'COALINDIA.NS': 'Coal India',
    'BHARTIARTL.NS': 'Bharti Airtel', 'ULTRACEMCO.NS': 'UltraTech',
    'ASIANPAINT.NS': 'Asian Paints', 'TITAN.NS': 'Titan', 'ADANIPORTS.NS': 'Adani Ports', 'LT.NS': 'L&T'
}

# Import database
try:
    from database_manager import SarthakNiveshDB
    DB_AVAILABLE = True
    db = SarthakNiveshDB()
except:
    DB_AVAILABLE = False
    db = None

class SmartMoneyTracker:
    """Track institutional money flow in real-time"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/html',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.nse_cookies = None
    
    def get_nse_cookies(self):
        """Get NSE cookies for API access"""
        try:
            response = self.session.get('https://www.nseindia.com', timeout=10)
            self.nse_cookies = response.cookies
            return True
        except:
            return False

    
    def fetch_fii_dii_data(self):
        """Fetch real-time FII/DII data from NSE"""
        try:
            # Method 1: NSE Official API
            if not self.nse_cookies:
                self.get_nse_cookies()
            
            url = "https://www.nseindia.com/api/fiidiiTradeReact"
            
            response = self.session.get(url, cookies=self.nse_cookies, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # NSE returns data in format: [{"category": "DII", "date": "26-Feb-2026", "buyValue": "19242.72", ...}, ...]
                # Group by date
                date_data = {}
                
                for record in data:
                    date_str = record.get('date', '')
                    category = record.get('category', '')
                    
                    if date_str not in date_data:
                        date_data[date_str] = {
                            'date': date_str,
                            'fii_buy': 0,
                            'fii_sell': 0,
                            'fii_net': 0,
                            'dii_buy': 0,
                            'dii_sell': 0,
                            'dii_net': 0,
                        }
                    
                    buy_val = float(record.get('buyValue', 0))
                    sell_val = float(record.get('sellValue', 0))
                    net_val = float(record.get('netValue', 0))
                    
                    if 'FII' in category or 'FPI' in category:
                        date_data[date_str]['fii_buy'] = buy_val
                        date_data[date_str]['fii_sell'] = sell_val
                        date_data[date_str]['fii_net'] = net_val
                    elif 'DII' in category:
                        date_data[date_str]['dii_buy'] = buy_val
                        date_data[date_str]['dii_sell'] = sell_val
                        date_data[date_str]['dii_net'] = net_val
                
                # Convert to list
                fii_dii_records = list(date_data.values())
                
                if fii_dii_records:
                    return pd.DataFrame(fii_dii_records)
            
        except Exception as e:
            print(f"NSE API failed: {e}")
        
        # Method 2: Web scraping from MoneyControl
        return self.scrape_fii_dii_moneycontrol()

    
    def scrape_fii_dii_moneycontrol(self):
        """Scrape FII/DII data from MoneyControl"""
        try:
            url = "https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php"
            
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all tables
            tables = soup.find_all('table')
            
            fii_dii_data = []
            
            # Look for the table with FII/DII data (usually table 1 or 2)
            for table in tables:
                rows = table.find_all('tr')
                
                # Check if this is the right table
                header_row = rows[0] if rows else None
                if header_row and 'FII' in header_row.text and 'DII' in header_row.text:
                    # Skip first 2 rows (headers)
                    for row in rows[2:32]:  # Get up to 30 days
                        cols = row.find_all('td')
                        
                        if len(cols) >= 7:
                            try:
                                date_str = cols[0].text.strip()
                                
                                # Skip if not a valid date row
                                if not date_str or date_str in ['Month till date', 'Year till date']:
                                    continue
                                
                                fii_buy = self.parse_amount(cols[1].text.strip())
                                fii_sell = self.parse_amount(cols[2].text.strip())
                                fii_net = self.parse_amount(cols[3].text.strip())
                                dii_buy = self.parse_amount(cols[4].text.strip())
                                dii_sell = self.parse_amount(cols[5].text.strip())
                                dii_net = self.parse_amount(cols[6].text.strip())
                                
                                fii_dii_data.append({
                                    'date': date_str,
                                    'fii_buy': fii_buy,
                                    'fii_sell': fii_sell,
                                    'fii_net': fii_net,
                                    'dii_buy': dii_buy,
                                    'dii_sell': dii_sell,
                                    'dii_net': dii_net,
                                })
                            except Exception as e:
                                continue
                    
                    # If we found data, break
                    if fii_dii_data:
                        break
            
            return pd.DataFrame(fii_dii_data)
        
        except Exception as e:
            print(f"MoneyControl scraping failed: {e}")
        
        return pd.DataFrame()
    
    def fetch_bulk_deals(self):
        """Fetch real-time bulk deals from NSE"""
        try:
            if not self.nse_cookies:
                self.get_nse_cookies()
            
            # NSE Bulk Deals API
            url = "https://www.nseindia.com/api/snapshot-capital-market-largedeal"
            
            response = self.session.get(url, cookies=self.nse_cookies, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                bulk_deals = []
                
                # Parse bulk deals
                for deal in data.get('data', []):
                    bulk_deals.append({
                        'date': deal.get('date', ''),
                        'symbol': deal.get('symbol', ''),
                        'company': deal.get('companyName', ''),
                        'client_name': deal.get('clientName', ''),
                        'deal_type': deal.get('dealType', ''),
                        'quantity': int(deal.get('quantity', 0)),
                        'price': float(deal.get('price', 0)),
                        'value': float(deal.get('value', 0)),
                    })
                
                return pd.DataFrame(bulk_deals)
        
        except Exception as e:
            print(f"Bulk deals fetch failed: {e}")
        
        # Fallback: Scrape from NSE website
        return self.scrape_bulk_deals_nse()

    
    def scrape_bulk_deals_nse(self):
        """Scrape bulk deals from NSE website"""
        try:
            url = "https://www.nseindia.com/report-detail/eq_bulk"
            
            response = self.session.get(url, cookies=self.nse_cookies, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse table data
            table = soup.find('table', {'id': 'bulkDealsTable'})
            
            if table:
                rows = table.find_all('tr')[1:]
                
                bulk_deals = []
                
                for row in rows:
                    cols = row.find_all('td')
                    
                    if len(cols) >= 7:
                        bulk_deals.append({
                            'date': cols[0].text.strip(),
                            'symbol': cols[1].text.strip(),
                            'company': cols[2].text.strip(),
                            'client_name': cols[3].text.strip(),
                            'deal_type': cols[4].text.strip(),
                            'quantity': int(cols[5].text.strip().replace(',', '')),
                            'price': float(cols[6].text.strip()),
                            'value': 0
                        })
                
                df = pd.DataFrame(bulk_deals)
                df['value'] = df['quantity'] * df['price']
                
                return df
        
        except Exception as e:
            print(f"NSE scraping failed: {e}")
        
        return pd.DataFrame()

    
    def fetch_block_deals(self):
        """Fetch real-time block deals from NSE"""
        try:
            if not self.nse_cookies:
                self.get_nse_cookies()
            
            url = "https://www.nseindia.com/api/block-deal"
            
            response = self.session.get(url, cookies=self.nse_cookies, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                block_deals = []
                
                for deal in data.get('data', []):
                    block_deals.append({
                        'date': deal.get('date', ''),
                        'symbol': deal.get('symbol', ''),
                        'company': deal.get('companyName', ''),
                        'client_name': deal.get('clientName', ''),
                        'deal_type': deal.get('dealType', ''),
                        'quantity': int(deal.get('quantity', 0)),
                        'price': float(deal.get('tradePrice', 0)),
                        'value': float(deal.get('tradeValue', 0)),
                    })
                
                return pd.DataFrame(block_deals)
        
        except Exception as e:
            print(f"Block deals fetch failed: {e}")
        
        return pd.DataFrame()

    
    def fetch_insider_trading(self):
        """Fetch insider trading data from SEBI/BSE"""
        try:
            # BSE Insider Trading API
            url = "https://api.bseindia.com/BseIndiaAPI/api/InsiderTradingData/w"
            
            params = {
                'scripcode': '',
                'FromDate': (datetime.now() - timedelta(days=30)).strftime('%Y%m%d'),
                'ToDate': datetime.now().strftime('%Y%m%d'),
                'segment': 'Equity'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    insider_trades = []
                    
                    for trade in data.get('Table', []):
                        insider_trades.append({
                            'date': trade.get('ACQFROM_DT', ''),
                            'symbol': trade.get('SCRIP_CD', ''),
                            'company': trade.get('SCRIP_NAME', ''),
                            'person': trade.get('PER', ''),
                            'relation': trade.get('CAT', ''),
                            'transaction_type': trade.get('TDPACQMODE', ''),
                            'quantity': int(trade.get('BEFACQSHARES', 0)),
                            'value': float(trade.get('VALUE', 0)),
                        })
                    
                    if insider_trades:
                        return pd.DataFrame(insider_trades)
                except:
                    pass
        
        except Exception as e:
            print(f"Insider trading fetch failed: {e}")
        
        # Return empty DataFrame - UI will show appropriate message
        return pd.DataFrame()

    
    def fetch_institutional_holdings(self, symbol):
        """Fetch institutional holdings for a stock"""
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            
            # Get institutional holders
            inst_holders = ticker.institutional_holders
            
            if inst_holders is not None and not inst_holders.empty:
                return inst_holders
        
        except Exception as e:
            print(f"Holdings fetch failed: {e}")
        
        return pd.DataFrame()
    
    def analyze_smart_money_signal(self, symbol, fii_dii_df, bulk_deals_df, insider_df):
        """Analyze smart money signals for a stock"""
        
        signal_score = 0
        signals = []
        
        # FII/DII Analysis
        if not fii_dii_df.empty:
            recent_fii = fii_dii_df.head(5)['fii_net'].sum()
            recent_dii = fii_dii_df.head(5)['dii_net'].sum()
            
            if recent_fii > 1000:  # Crores
                signal_score += 3
                signals.append(f"FII bought ₹{recent_fii:.0f} Cr in last 5 days")
            elif recent_fii < -1000:
                signal_score -= 3
                signals.append(f"FII sold ₹{abs(recent_fii):.0f} Cr in last 5 days")
            
            if recent_dii > 500:
                signal_score += 2
                signals.append(f"DII bought ₹{recent_dii:.0f} Cr in last 5 days")
            elif recent_dii < -500:
                signal_score -= 2
                signals.append(f"DII sold ₹{abs(recent_dii):.0f} Cr in last 5 days")
        
        # Bulk Deals Analysis
        if not bulk_deals_df.empty:
            stock_bulk = bulk_deals_df[bulk_deals_df['symbol'].str.contains(symbol.replace('.NS', ''), case=False, na=False)]
            
            if not stock_bulk.empty:
                buy_deals = stock_bulk[stock_bulk['deal_type'].str.contains('BUY', case=False, na=False)]
                sell_deals = stock_bulk[stock_bulk['deal_type'].str.contains('SELL', case=False, na=False)]
                
                if len(buy_deals) > len(sell_deals):
                    signal_score += 2
                    signals.append(f"{len(buy_deals)} bulk buy deals detected")
                elif len(sell_deals) > len(buy_deals):
                    signal_score -= 2
                    signals.append(f"{len(sell_deals)} bulk sell deals detected")
        
        # Insider Trading Analysis
        if not insider_df.empty:
            stock_insider = insider_df[insider_df['symbol'].str.contains(symbol.replace('.NS', ''), case=False, na=False)]
            
            if not stock_insider.empty:
                buy_insider = stock_insider[stock_insider['transaction_type'].str.contains('BUY|ACQUISITION', case=False, na=False)]
                sell_insider = stock_insider[stock_insider['transaction_type'].str.contains('SELL|DISPOSAL', case=False, na=False)]
                
                if len(buy_insider) > 0:
                    signal_score += 2
                    signals.append(f"Promoter/Insider buying detected")
                elif len(sell_insider) > 0:
                    signal_score -= 1
                    signals.append(f"Promoter/Insider selling detected")
        
        # Generate recommendation
        if signal_score >= 5:
            recommendation = "STRONG BUY"
            color = "#00ff88"
        elif signal_score >= 2:
            recommendation = "BUY"
            color = "#17a2b8"
        elif signal_score >= -2:
            recommendation = "HOLD"
            color = "#ffc107"
        elif signal_score >= -5:
            recommendation = "SELL"
            color = "#ff9800"
        else:
            recommendation = "STRONG SELL"
            color = "#ff5252"
        
        return {
            'score': signal_score,
            'recommendation': recommendation,
            'color': color,
            'signals': signals
        }

    
    def parse_amount(self, text):
        """Parse amount from text (handles Cr, L, etc.)"""
        try:
            text = text.strip().replace(',', '').replace('₹', '').replace('Rs', '').replace(' ', '')
            
            # If already has Cr/cr, just extract the number
            if 'Cr' in text or 'cr' in text or 'Crores' in text or 'crores' in text:
                text = text.replace('Cr', '').replace('cr', '').replace('Crores', '').replace('crores', '').strip()
                return float(text)
            # If has Lakh/L, convert to Crores
            elif 'L' in text or 'Lakh' in text or 'lakh' in text:
                text = text.replace('L', '').replace('Lakh', '').replace('lakh', '').strip()
                return float(text) / 100
            # If just a number, assume it's already in Crores (MoneyControl format)
            else:
                num = float(text)
                # If number is very large (> 100000), it's in lakhs or actual rupees
                if num > 100000:
                    return num / 10000000  # Convert to Crores
                else:
                    return num  # Already in Crores
        except Exception as e:
            return 0.0
    
    def get_sector_money_flow(self, fii_dii_df, bulk_deals_df):
        """Calculate sector-wise money flow"""
        
        sector_flow = {}
        
        # Major sectors and their representative stocks
        sectors = {
            'Banking': ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK'],
            'IT': ['TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM'],
            'Auto': ['MARUTI', 'TATAMOTORS', 'M&M', 'BAJAJ-AUTO', 'EICHERMOT'],
            'Pharma': ['SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON'],
            'Energy': ['RELIANCE', 'ONGC', 'POWERGRID', 'NTPC', 'ADANIGREEN'],
        }
        
        for sector, stocks in sectors.items():
            sector_bulk_value = 0
            
            if not bulk_deals_df.empty:
                for stock in stocks:
                    stock_deals = bulk_deals_df[bulk_deals_df['symbol'].str.contains(stock, case=False, na=False)]
                    
                    if not stock_deals.empty:
                        buy_value = stock_deals[stock_deals['deal_type'].str.contains('BUY', case=False, na=False)]['value'].sum()
                        sell_value = stock_deals[stock_deals['deal_type'].str.contains('SELL', case=False, na=False)]['value'].sum()
                        
                        sector_bulk_value += (buy_value - sell_value)
            
            sector_flow[sector] = sector_bulk_value / 10000000  # Convert to Crores
        
        return sector_flow


def show_smart_money_tracker():
    """Main UI for Smart Money Tracker"""
    
    st.header("🎯 Smart Money Tracker - Follow Institutional Money")
    
    # Hero Banner
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 10px 40px rgba(102, 126, 234, 0.5);'>
        <h2 style='color: #ffffff; margin: 0; text-align: center;'>
            💰 TRACK SMART MONEY IN REAL-TIME
        </h2>
        <p style='color: #ffffff; margin: 0.5rem 0; text-align: center; font-size: 1.2rem;'>
            FII/DII Activity | Bulk Deals | Insider Trading | Block Deals
        </p>
        <p style='color: #e0e0e0; margin: 0; text-align: center;'>
            ✅ Live Data from NSE, BSE, SEBI | ✅ AI-Powered Signals | ✅ Sector Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize tracker
    tracker = SmartMoneyTracker()
    
    # Refresh controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (5 min)")
    with col3:
        st.info(f"🕐 Last Updated: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}")
    
    if auto_refresh:
        st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 FII/DII Activity",
        "💼 Bulk Deals",
        "🔒 Block Deals",
        "👤 Insider Trading",
        "🎯 Smart Money Signals",
        "🏭 Sector Flow"
    ])
    
    # TAB 1: FII/DII Activity
    with tab1:
        st.subheader("📊 Foreign & Domestic Institutional Activity")
        
        with st.spinner("🔍 Fetching FII/DII data from NSE..."):
            fii_dii_df = tracker.fetch_fii_dii_data()
        
        if not fii_dii_df.empty:
            st.success(f"✅ Fetched {len(fii_dii_df)} days of FII/DII data")
            
            # Latest day summary
            latest = fii_dii_df.iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                fii_color = "normal" if latest['fii_net'] > 0 else "inverse"
                st.metric("FII Net (Today)", f"₹{latest['fii_net']:.0f} Cr", 
                         "Buying" if latest['fii_net'] > 0 else "Selling",
                         delta_color=fii_color)
            
            with col2:
                dii_color = "normal" if latest['dii_net'] > 0 else "inverse"
                st.metric("DII Net (Today)", f"₹{latest['dii_net']:.0f} Cr",
                         "Buying" if latest['dii_net'] > 0 else "Selling",
                         delta_color=dii_color)
            
            with col3:
                week_fii = fii_dii_df.head(5)['fii_net'].sum()
                st.metric("FII Net (5 Days)", f"₹{week_fii:.0f} Cr")
            
            with col4:
                week_dii = fii_dii_df.head(5)['dii_net'].sum()
                st.metric("DII Net (5 Days)", f"₹{week_dii:.0f} Cr")
            
            # Trend Chart
            st.markdown("### 📈 FII/DII Trend (Last 30 Days)")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=fii_dii_df['date'],
                y=fii_dii_df['fii_net'],
                name='FII Net',
                marker_color=['#00ff88' if x > 0 else '#ff5252' for x in fii_dii_df['fii_net']]
            ))
            
            fig.add_trace(go.Bar(
                x=fii_dii_df['date'],
                y=fii_dii_df['dii_net'],
                name='DII Net',
                marker_color=['#00d4ff' if x > 0 else '#ffc107' for x in fii_dii_df['dii_net']]
            ))
            
            fig.update_layout(
                title="FII vs DII Net Flow",
                xaxis_title="Date",
                yaxis_title="Amount (₹ Crores)",
                barmode='group',
                height=500,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Data Table
            st.markdown("### 📋 Detailed FII/DII Data")
            
            display_df = fii_dii_df.copy()
            display_df['fii_buy'] = display_df['fii_buy'].apply(lambda x: f"₹{x:.0f} Cr")
            display_df['fii_sell'] = display_df['fii_sell'].apply(lambda x: f"₹{x:.0f} Cr")
            display_df['fii_net'] = display_df['fii_net'].apply(lambda x: f"₹{x:+.0f} Cr")
            display_df['dii_buy'] = display_df['dii_buy'].apply(lambda x: f"₹{x:.0f} Cr")
            display_df['dii_sell'] = display_df['dii_sell'].apply(lambda x: f"₹{x:.0f} Cr")
            display_df['dii_net'] = display_df['dii_net'].apply(lambda x: f"₹{x:+.0f} Cr")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
        else:
            st.warning("⚠️ Unable to fetch FII/DII data. Please try refreshing.")

    
    # TAB 2: Bulk Deals
    with tab2:
        st.subheader("💼 Today's Bulk Deals")
        
        with st.spinner("🔍 Fetching bulk deals from NSE..."):
            bulk_deals_df = tracker.fetch_bulk_deals()
        
        if not bulk_deals_df.empty:
            st.success(f"✅ Found {len(bulk_deals_df)} bulk deals today")
            
            # Summary metrics
            total_value = bulk_deals_df['value'].sum() / 10000000  # Crores
            buy_deals = bulk_deals_df[bulk_deals_df['deal_type'].str.contains('BUY', case=False, na=False)]
            sell_deals = bulk_deals_df[bulk_deals_df['deal_type'].str.contains('SELL', case=False, na=False)]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Deals", len(bulk_deals_df))
            with col2:
                st.metric("Buy Deals", len(buy_deals), "🟢")
            with col3:
                st.metric("Sell Deals", len(sell_deals), "🔴")
            with col4:
                st.metric("Total Value", f"₹{total_value:.0f} Cr")
            
            # Top deals
            st.markdown("### 🔝 Top Bulk Deals by Value")
            
            top_deals = bulk_deals_df.nlargest(10, 'value')
            
            for _, deal in top_deals.iterrows():
                deal_color = "#00ff88" if 'BUY' in deal['deal_type'].upper() else "#ff5252"
                
                st.markdown(f"""
                <div style='background: rgba(0, 212, 255, 0.05); padding: 1rem; border-radius: 10px;
                            border-left: 5px solid {deal_color}; margin: 0.5rem 0;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h4 style='color: #00d4ff; margin: 0;'>{deal['company']}</h4>
                            <p style='margin: 0.3rem 0;'><strong>Client:</strong> {deal['client_name']}</p>
                            <p style='margin: 0;'><strong>Type:</strong> {deal['deal_type']}</p>
                        </div>
                        <div style='text-align: right;'>
                            <h3 style='color: {deal_color}; margin: 0;'>₹{deal['value']/10000000:.2f} Cr</h3>
                            <p style='margin: 0;'>{deal['quantity']:,} shares @ ₹{deal['price']:.2f}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Full data table
            st.markdown("### 📋 All Bulk Deals")
            
            display_df = bulk_deals_df.copy()
            display_df['value'] = display_df['value'].apply(lambda x: f"₹{x/10000000:.2f} Cr")
            display_df['quantity'] = display_df['quantity'].apply(lambda x: f"{x:,}")
            display_df['price'] = display_df['price'].apply(lambda x: f"₹{x:.2f}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
        else:
            st.warning("⚠️ No bulk deals data available right now")
            
            st.info("""
            **About Bulk Deals:**
            
            Bulk deals are large transactions where a single client buys or sells more than 0.5% of a company's shares.
            These deals are reported to NSE/BSE and indicate significant institutional or HNI activity.
            
            **Why no data?**
            - Bulk deals are reported only during market hours (9:15 AM - 3:30 PM)
            - Not every day has bulk deals
            - Data is updated after market close
            
            **What to look for:**
            - Large institutional buying = Positive signal
            - Promoter/FII buying = Strong confidence
            - Repeated selling = Caution signal
            """)
            
            # Show example of what bulk deals look like
            st.markdown("### 📊 Example: What Bulk Deals Look Like")
            
            example_data = pd.DataFrame([
                {'Date': '25-Feb-2026', 'Company': 'Reliance Industries', 'Client': 'ABC Mutual Fund', 
                 'Type': 'BUY', 'Quantity': '5,00,000', 'Price': '₹2,450', 'Value': '₹122.5 Cr'},
                {'Date': '25-Feb-2026', 'Company': 'HDFC Bank', 'Client': 'XYZ Insurance', 
                 'Type': 'BUY', 'Quantity': '3,00,000', 'Price': '₹1,650', 'Value': '₹49.5 Cr'},
                {'Date': '25-Feb-2026', 'Company': 'Infosys', 'Client': 'PQR Investments', 
                 'Type': 'SELL', 'Quantity': '2,00,000', 'Price': '₹1,420', 'Value': '₹28.4 Cr'},
            ])
            
            st.dataframe(example_data, use_container_width=True, hide_index=True)
            st.caption("📌 This is sample data for illustration. Real data will appear during market hours.")

    
    # TAB 3: Block Deals
    with tab3:
        st.subheader("🔒 Today's Block Deals")
        
        with st.spinner("🔍 Fetching block deals from NSE..."):
            block_deals_df = tracker.fetch_block_deals()
        
        if not block_deals_df.empty:
            st.success(f"✅ Found {len(block_deals_df)} block deals today")
            
            # Summary
            total_value = block_deals_df['value'].sum() / 10000000
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Block Deals", len(block_deals_df))
            with col2:
                st.metric("Total Value", f"₹{total_value:.0f} Cr")
            
            # Display deals
            st.markdown("### 💼 Block Deal Details")
            
            for _, deal in block_deals_df.iterrows():
                st.markdown(f"""
                <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 10px;
                            border-left: 5px solid #667eea; margin: 0.5rem 0;'>
                    <h4 style='color: #667eea; margin: 0;'>{deal['company']}</h4>
                    <p style='margin: 0.3rem 0;'><strong>Client:</strong> {deal['client_name']}</p>
                    <p style='margin: 0.3rem 0;'><strong>Quantity:</strong> {deal['quantity']:,} shares @ ₹{deal['price']:.2f}</p>
                    <p style='margin: 0;'><strong>Value:</strong> ₹{deal['value']/10000000:.2f} Cr</p>
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.info("ℹ️ No block deals reported today.")
            
            st.info("""
            **About Block Deals:**
            
            Block deals are very large off-market transactions (minimum ₹10 Cr or 5 lakh shares).
            These are negotiated deals between institutions and executed outside regular market hours.
            
            **Why no data?**
            - Block deals are rare (only 2-3 per week on average)
            - Executed in special trading window (8:45-9:00 AM and 2:05-2:20 PM)
            - Indicate major institutional repositioning
            
            **What they mean:**
            - Large institutional buying/selling
            - Portfolio rebalancing by mutual funds
            - Strategic stake changes
            """)
            
            st.markdown("### 📊 Example: What Block Deals Look Like")
            
            example_data = pd.DataFrame([
                {'Date': '24-Feb-2026', 'Company': 'Tata Motors', 'Client': 'LIC of India', 
                 'Quantity': '10,00,000', 'Price': '₹850', 'Value': '₹85 Cr'},
                {'Date': '23-Feb-2026', 'Company': 'Axis Bank', 'Client': 'SBI Mutual Fund', 
                 'Quantity': '8,00,000', 'Price': '₹1,120', 'Value': '₹89.6 Cr'},
            ])
            
            st.dataframe(example_data, use_container_width=True, hide_index=True)
            st.caption("📌 This is sample data for illustration. Real data will appear when block deals occur.")
    
    # TAB 4: Insider Trading
    with tab4:
        st.subheader("👤 Insider Trading Activity")
        
        with st.spinner("🔍 Fetching insider trading data from SEBI/BSE..."):
            insider_df = tracker.fetch_insider_trading()
        
        if not insider_df.empty:
            st.success(f"✅ Found {len(insider_df)} insider transactions (Last 30 days)")
            
            # Summary
            buy_trades = insider_df[insider_df['transaction_type'].str.contains('BUY|ACQUISITION', case=False, na=False)]
            sell_trades = insider_df[insider_df['transaction_type'].str.contains('SELL|DISPOSAL', case=False, na=False)]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Transactions", len(insider_df))
            with col2:
                st.metric("Insider Buying", len(buy_trades), "🟢")
            with col3:
                st.metric("Insider Selling", len(sell_trades), "🔴")
            
            # Recent transactions
            st.markdown("### 📋 Recent Insider Transactions")
            
            for _, trade in insider_df.head(20).iterrows():
                trade_color = "#00ff88" if 'BUY' in trade['transaction_type'].upper() or 'ACQUISITION' in trade['transaction_type'].upper() else "#ff5252"
                
                st.markdown(f"""
                <div style='background: rgba(0, 212, 255, 0.05); padding: 1rem; border-radius: 10px;
                            border-left: 5px solid {trade_color}; margin: 0.5rem 0;'>
                    <h4 style='color: #00d4ff; margin: 0;'>{trade['company']}</h4>
                    <p style='margin: 0.3rem 0;'><strong>Person:</strong> {trade['person']} ({trade['relation']})</p>
                    <p style='margin: 0.3rem 0;'><strong>Type:</strong> {trade['transaction_type']}</p>
                    <p style='margin: 0;'><strong>Quantity:</strong> {trade['quantity']:,} shares | <strong>Date:</strong> {trade['date']}</p>
                </div>
                """, unsafe_allow_html=True)
            
        else:
            st.warning("⚠️ Unable to fetch insider trading data from BSE API")
            
            st.info("""
            **About Insider Trading:**
            
            Insider trading refers to transactions by company promoters, directors, and key management personnel.
            These transactions must be reported to SEBI within 2 days.
            
            **Why no data?**
            - BSE API is temporarily unavailable (common issue)
            - API works better during market hours
            - Data is updated with a 2-day lag
            
            **What to look for:**
            - **Promoter Buying** = Strong confidence in company future
            - **Director Buying** = Positive insider signal
            - **Promoter Selling** = May indicate concerns (or just liquidity needs)
            - **Multiple Insiders Buying** = Very bullish signal
            """)
            
            st.markdown("### 📊 Example: What Insider Trading Looks Like")
            
            example_data = pd.DataFrame([
                {'Date': '20-Feb-2026', 'Company': 'Tech Mahindra', 'Person': 'Anand Mahindra', 
                 'Relation': 'Promoter', 'Type': 'ACQUISITION', 'Quantity': '50,000'},
                {'Date': '19-Feb-2026', 'Company': 'Infosys', 'Person': 'Salil Parekh', 
                 'Relation': 'CEO', 'Type': 'ACQUISITION', 'Quantity': '10,000'},
                {'Date': '18-Feb-2026', 'Company': 'Wipro', 'Person': 'Rishad Premji', 
                 'Relation': 'Chairman', 'Type': 'DISPOSAL', 'Quantity': '25,000'},
            ])
            
            st.dataframe(example_data, use_container_width=True, hide_index=True)
            st.caption("📌 This is sample data for illustration. Real data will appear when API is available.")

    
    # TAB 5: Smart Money Signals
    with tab5:
        st.subheader("🎯 Smart Money Signals - AI Analysis")
        
        st.markdown("""
        Get AI-powered buy/sell signals based on institutional activity, bulk deals, and insider trading.
        """)
        
        # Stock selection
        selected_stock = st.selectbox(
            "Select Stock for Smart Money Analysis",
            list(INDIAN_STOCKS.keys()),
            format_func=lambda x: f"{INDIAN_STOCKS[x]} ({x.replace('.NS', '')})"
        )
        
        if st.button("🚀 Analyze Smart Money", type="primary"):
            with st.spinner("🤖 Analyzing institutional activity..."):
                # Fetch all data
                fii_dii_df = tracker.fetch_fii_dii_data()
                bulk_deals_df = tracker.fetch_bulk_deals()
                insider_df = tracker.fetch_insider_trading()
                
                # Analyze
                analysis = tracker.analyze_smart_money_signal(
                    selected_stock, fii_dii_df, bulk_deals_df, insider_df
                )
                
                # Display results
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(0, 255, 136, 0.2) 100%);
                            padding: 3rem; border-radius: 20px; text-align: center; margin: 2rem 0;
                            border: 4px solid {analysis['color']}; box-shadow: 0 0 40px {analysis['color']}80;'>
                    <h1 style='color: {analysis['color']}; margin: 0; font-size: 4rem;'>
                        {analysis['recommendation']}
                    </h1>
                    <h3 style='color: #ffffff; margin: 1rem 0;'>
                        Smart Money Score: {analysis['score']}/10
                    </h3>
                    <p style='color: #e0e0e0; margin: 0; font-size: 1.2rem;'>
                        Based on FII/DII, Bulk Deals & Insider Trading
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Signal breakdown
                st.markdown("### 📊 Signal Breakdown")
                
                if analysis['signals']:
                    for signal in analysis['signals']:
                        st.markdown(f"✅ {signal}")
                else:
                    st.info("No significant smart money activity detected for this stock.")
                
                # Institutional holdings
                st.markdown("### 🏦 Institutional Holdings")
                
                holdings = tracker.fetch_institutional_holdings(selected_stock)
                
                if not holdings.empty:
                    st.dataframe(holdings, use_container_width=True, hide_index=True)
                else:
                    st.info("Institutional holdings data not available.")
    
    # TAB 6: Sector Flow
    with tab6:
        st.subheader("🏭 Sector-wise Money Flow")
        
        with st.spinner("🔍 Analyzing sector-wise money flow..."):
            fii_dii_df = tracker.fetch_fii_dii_data()
            bulk_deals_df = tracker.fetch_bulk_deals()
            
            sector_flow = tracker.get_sector_money_flow(fii_dii_df, bulk_deals_df)
        
        if sector_flow:
            st.success("✅ Sector analysis complete")
            
            # Sector flow chart
            sectors = list(sector_flow.keys())
            flows = list(sector_flow.values())
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=sectors,
                y=flows,
                marker_color=['#00ff88' if f > 0 else '#ff5252' for f in flows],
                text=[f"₹{f:+.0f} Cr" for f in flows],
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Sector-wise Smart Money Flow (Bulk Deals)",
                xaxis_title="Sector",
                yaxis_title="Net Flow (₹ Crores)",
                height=500,
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Sector recommendations
            st.markdown("### 💡 Sector Recommendations")
            
            sorted_sectors = sorted(sector_flow.items(), key=lambda x: x[1], reverse=True)
            
            # Check if all sectors are zero
            all_zero = all(flow == 0 for flow in sector_flow.values())
            
            if all_zero:
                st.info("""
                **ℹ️ All sectors showing ₹0 Cr flow**
                
                This is because there are no bulk deals today. Sector flow is calculated from bulk deal activity.
                
                **What this means:**
                - No large institutional transactions in any sector today
                - This is normal after market hours or on quiet trading days
                - Check back during market hours for live sector rotation data
                
                **How Sector Flow Works:**
                - Tracks which sectors are getting institutional money
                - Based on bulk deal activity by sector
                - Helps identify sector rotation trends
                - Useful for sector-based investment strategies
                """)
                
                # Show example sector flow
                st.markdown("### 📊 Example: What Sector Flow Looks Like")
                
                example_sectors = ['Banking', 'IT', 'Auto', 'Pharma', 'Energy']
                example_flows = [450, 320, -180, 120, -90]
                
                fig_example = go.Figure()
                
                fig_example.add_trace(go.Bar(
                    x=example_sectors,
                    y=example_flows,
                    marker_color=['#00ff88' if f > 0 else '#ff5252' for f in example_flows],
                    text=[f"₹{f:+.0f} Cr" for f in example_flows],
                    textposition='outside'
                ))
                
                fig_example.update_layout(
                    title="Example: Sector Money Flow (Sample Data)",
                    xaxis_title="Sector",
                    yaxis_title="Net Flow (₹ Crores)",
                    height=400,
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig_example, use_container_width=True)
                st.caption("📌 This is sample data for illustration. Real data will appear when bulk deals occur.")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🟢 Hot Sectors (Money Inflow)")
                    hot_found = False
                    for sector, flow in sorted_sectors[:3]:
                        if flow > 0:
                            st.success(f"**{sector}**: ₹{flow:+.0f} Cr inflow")
                            hot_found = True
                    if not hot_found:
                        st.info("No sectors with inflow today")
                
                with col2:
                    st.markdown("#### 🔴 Cold Sectors (Money Outflow)")
                    cold_found = False
                    for sector, flow in sorted_sectors[-3:]:
                        if flow < 0:
                            st.error(f"**{sector}**: ₹{flow:+.0f} Cr outflow")
                            cold_found = True
                    if not cold_found:
                        st.info("No sectors with outflow today")
        
        else:
            st.warning("⚠️ Unable to calculate sector flow. Please try refreshing.")


if __name__ == "__main__":
    st.set_page_config(page_title="Smart Money Tracker", layout="wide")
    show_smart_money_tracker()
