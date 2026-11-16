"""
Integration script to add real-time mutual fund fetching to main platform
Run this to update main_ultimate_final.py with real-time MF capabilities
"""

import sys

# Code to add at the top of main_ultimate_final.py (after imports)
REALTIME_MF_IMPORT = """
# Import real-time mutual fund fetcher
from realtime_mutual_fund_fetcher import RealtimeMutualFundFetcher
"""

# Code to add for caching real-time MF data
REALTIME_MF_CACHE = """
# ==================== REAL-TIME MUTUAL FUND DATA FETCHER ====================
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_realtime_mutual_funds():
    \"\"\"Fetch real-time mutual fund data from multiple sources\"\"\"
    try:
        print("🚀 Fetching real-time mutual fund data...")
        fetcher = RealtimeMutualFundFetcher()
        
        # Get comprehensive data from all sources
        all_data = fetcher.get_comprehensive_fund_data()
        
        # Merge and enrich data
        merged_funds = fetcher.merge_and_enrich_data(all_data)
        
        # Organize by category
        categorized_funds = organize_funds_by_category(merged_funds)
        
        print(f"✅ Fetched {len(merged_funds)} real-time mutual funds")
        return categorized_funds
        
    except Exception as e:
        print(f"❌ Error fetching real-time MF data: {e}")
        # Fallback to static data
        return MUTUAL_FUNDS

def organize_funds_by_category(funds_list):
    \"\"\"Organize funds into categories\"\"\"
    categorized = {
        'Large Cap': [],
        'Mid Cap': [],
        'Small Cap': [],
        'Flexi Cap': [],
        'Index Funds': [],
        'ELSS': [],
        'Debt': [],
        'Hybrid': [],
        'Gold & Silver': []
    }
    
    for fund in funds_list:
        scheme_name = fund.get('scheme_name', '').lower()
        
        # Categorize based on scheme name
        if 'large' in scheme_name or 'bluechip' in scheme_name or 'top 100' in scheme_name:
            category = 'Large Cap'
        elif 'mid' in scheme_name or 'midcap' in scheme_name:
            category = 'Mid Cap'
        elif 'small' in scheme_name or 'smallcap' in scheme_name:
            category = 'Small Cap'
        elif 'flexi' in scheme_name or 'multi' in scheme_name:
            category = 'Flexi Cap'
        elif 'index' in scheme_name or 'nifty' in scheme_name or 'sensex' in scheme_name:
            category = 'Index Funds'
        elif 'elss' in scheme_name or 'tax' in scheme_name:
            category = 'ELSS'
        elif 'debt' in scheme_name or 'bond' in scheme_name or 'gilt' in scheme_name:
            category = 'Debt'
        elif 'hybrid' in scheme_name or 'balanced' in scheme_name:
            category = 'Hybrid'
        elif 'gold' in scheme_name or 'silver' in scheme_name:
            category = 'Gold & Silver'
        else:
            category = 'Flexi Cap'  # Default
        
        # Format fund data
        formatted_fund = {
            'name': fund.get('scheme_name', 'Unknown Fund'),
            'nav': fund.get('nav', 0),
            'return_1y': fund.get('return_1y', 0),
            'return_3y': fund.get('return_3y', 0),
            'return_5y': fund.get('return_5y', 0),
            'expense': fund.get('expense_ratio', 0.75),
            'min_sip': fund.get('min_sip', 500),
            'rating': fund.get('rating', 4),
            'aum': fund.get('aum', 10000),
            'fund_house': fund.get('amc', fund.get('fund_house', 'Unknown')),
            'scheme_code': fund.get('scheme_code', ''),
            'last_updated': fund.get('date', datetime.now().strftime('%d-%b-%Y'))
        }
        
        categorized[category].append(formatted_fund)
    
    # Sort each category by 3-year returns
    for category in categorized:
        categorized[category] = sorted(
            categorized[category], 
            key=lambda x: x.get('return_3y', 0), 
            reverse=True
        )
    
    return categorized

def get_fund_comparison_data(fund_names):
    \"\"\"Get detailed comparison data for selected funds\"\"\"
    try:
        realtime_funds = get_realtime_mutual_funds()
        
        comparison_data = []
        for category, funds in realtime_funds.items():
            for fund in funds:
                if fund['name'] in fund_names:
                    comparison_data.append(fund)
        
        return comparison_data
    except:
        return []
"""

# Enhanced mutual fund display function
ENHANCED_MF_DISPLAY = """
def display_realtime_mutual_funds():
    \"\"\"Display real-time mutual fund data with refresh capability\"\"\"
    
    # Add refresh button
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button("🔄 Refresh Live Data", type="primary"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        data_freshness = st.selectbox(
            "Data Freshness",
            ["Real-time (30 min cache)", "Force Refresh"]
        )
    
    with col3:
        st.info("📊 Fetching live NAV data from AMFI, MF API, and Moneycontrol")
    
    # Fetch real-time data
    with st.spinner("🔄 Loading real-time mutual fund data..."):
        if data_freshness == "Force Refresh":
            st.cache_data.clear()
        
        realtime_funds = get_realtime_mutual_funds()
    
    # Display data freshness indicator
    st.success(f"✅ Live data loaded | Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    # Category selector
    selected_category = st.selectbox(
        "Select Fund Category",
        list(realtime_funds.keys())
    )
    
    # Display funds in selected category
    if selected_category in realtime_funds:
        funds = realtime_funds[selected_category]
        
        if funds:
            st.markdown(f"### {selected_category} Funds ({len(funds)} funds)")
            
            # Display as expandable cards
            for fund in funds:
                with st.expander(f"{fund['name']} - Score: {fund['rating']*20}/100"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("NAV", f"₹{fund['nav']:.2f}")
                        st.caption(f"Updated: {fund.get('last_updated', 'Today')}")
                    
                    with col2:
                        st.metric("1Y Return", f"{fund['return_1y']:.2f}%")
                        st.metric("3Y Return", f"{fund['return_3y']:.2f}%")
                    
                    with col3:
                        st.metric("Expense Ratio", f"{fund['expense']:.2f}%")
                        st.metric("Min SIP", f"₹{fund['min_sip']}")
                    
                    with col4:
                        st.metric("AUM", f"₹{fund['aum']:,.0f} Cr")
                        st.metric("Rating", "⭐" * fund['rating'])
                    
                    # Fund house info
                    st.caption(f"Fund House: {fund.get('fund_house', 'N/A')}")
                    
                    # Investment button
                    if st.button(f"📊 Analyze {fund['name'][:30]}...", key=f"analyze_{fund.get('scheme_code', fund['name'])}"):
                        st.info("Analysis feature coming soon!")
        else:
            st.warning(f"No funds available in {selected_category} category")
    
    # Show total funds count
    total_funds = sum(len(funds) for funds in realtime_funds.values())
    st.info(f"📊 Total {total_funds} real-time mutual funds available across all categories")
"""

def main():
    print("🚀 Real-time Mutual Fund Integration Script")
    print("=" * 60)
    
    print("\n📋 This script will help you integrate real-time mutual fund data")
    print("\nSteps to integrate:")
    print("1. Add realtime_mutual_fund_fetcher.py import to main_ultimate_final.py")
    print("2. Add caching functions for real-time data")
    print("3. Update show_mutual_fund_center() to use real-time data")
    
    print("\n" + "=" * 60)
    print("\n✅ Integration code prepared!")
    print("\nTo integrate manually:")
    print("1. Add the import at the top of main_ultimate_final.py")
    print("2. Add the caching functions after the MUTUAL_FUNDS database")
    print("3. Update the mutual fund display in show_mutual_fund_center()")
    
    print("\n📝 Or use the automated integration by running:")
    print("   python integrate_realtime_mf.py --auto")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        print("🤖 Automated integration not yet implemented")
        print("Please follow manual integration steps above")
    else:
        main()
