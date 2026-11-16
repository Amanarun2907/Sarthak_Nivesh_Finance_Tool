# 🚀 Ye Dil Maange More - सार्थक निवेश

## India's Most Advanced Investment Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

> **"Ye Dil Maange More"** - Because your investments deserve more intelligence, more insights, and more returns!

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Modules](#modules)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Integration](#api-integration)
- [Database Schema](#database-schema)
- [Screenshots](#screenshots)
- [Team](#team)
- [Future Scope](#future-scope)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**सार्थक निवेश (Sarthak Nivesh)** is a comprehensive, AI-powered investment intelligence platform designed specifically for Indian retail investors. It combines real-time market data, advanced analytics, AI-driven insights, and professional portfolio management tools into a single, user-friendly interface.

### 🌟 What Makes Us Different?

- **100% Real-time Data**: Live market data from NSE, BSE, AMFI, and multiple financial APIs
- **120+ Stocks Tracking**: Comprehensive coverage across all major sectors
- **2400+ Mutual Funds**: Real-time NAV data from AMFI
- **AI-Powered Analysis**: Groq Llama 3.3 70B for intelligent insights
- **Professional Tools**: Institutional-grade analytics for retail investors
- **Zero Cost**: Completely free platform with no hidden charges

---

## ✨ Key Features

### 📊 **Stock Intelligence (50+ Stocks)**
- **Real-time Price Tracking**: Live data from Yahoo Finance
- **Technical Analysis**: 
  - RSI, MACD, Bollinger Bands, Stochastic Oscillator
  - ADX, Beta, Sharpe Ratio, Moving Averages
  - Support/Resistance levels
- **Fundamental Analysis**:
  - P/E Ratio, P/B Ratio, Market Cap, EPS
  - ROE, ROA, Debt/Equity, Profit Margins
  - Revenue, EBITDA, Cash Flow metrics
- **AI Recommendations**: Multi-factor scoring with confidence levels
- **Price Prediction**: ML-based forecasting with confidence intervals
- **News & Sentiment**: Real-time news with sentiment analysis
- **Stock Comparison**: Side-by-side comparison of multiple stocks

### 💰 **Mutual Fund Center (2400+ Funds)**
- **Real-time NAV**: Direct from AMFI API
- **9 Categories**: Large Cap, Mid Cap, Small Cap, Flexi Cap, Index, ELSS, Debt, Hybrid, Gold
- **Advanced Filters**: By returns, expense ratio, minimum SIP
- **SIP Calculator**: 
  - Basic and Step-up SIP calculations
  - Goal-based planning
  - Inflation-adjusted returns
- **Fund Comparison**: Compare up to 3 funds simultaneously
- **Personalized Recommendations**: Based on age, risk appetite, goals
- **Educational Content**: Complete guide for beginners

### 🚀 **IPO Intelligence Hub**
- **Live IPO Data**: Real-time from NSE, MoneyControl, Chittorgarh
- **Comprehensive Analysis**:
  - Price band, lot size, issue size
  - Subscription status (live updates)
  - GMP (Grey Market Premium)
  - Listing predictions
- **AI-Powered Ratings**: Risk assessment and recommendations
- **Historical Performance**: Track past IPO listings
- **Application Guide**: Step-by-step IPO application process

### 💰 **Smart Money Tracker**
- **FII/DII Flow**: Real-time institutional money tracking from NSE
- **Bulk Deals**: Large institutional trades (>0.5% equity)
- **Block Deals**: Off-market institutional trades
- **Volume Analysis**: Detect unusual trading activity
- **Sector Flow**: Money movement across sectors
- **AI Signals**: Buy/Sell recommendations based on institutional activity

### 🛡️ **Portfolio & Risk Management**
- **Portfolio Tracking**: 120+ stocks with real-time P&L
- **Advanced Metrics**:
  - Portfolio Beta, Sharpe Ratio
  - Value at Risk (VaR)
  - Maximum Drawdown
  - Diversification Score
- **Risk Assessment**: Professional risk analysis
- **Rebalancing Suggestions**: AI-powered optimization
- **Performance Analytics**: Sector-wise and stock-wise returns
- **Auto-save**: Automatic database backup

### 📰 **News & Sentiment Analysis**
- **Real-time News**: From MoneyControl, Economic Times, Business Standard
- **Sentiment Analysis**: TextBlob + VADER algorithms
- **Sector Sentiment**: Track sentiment by sector
- **Trending Topics**: Identify market trends
- **Stock-specific News**: Filter news by stock
- **Impact Scoring**: Measure news impact on stocks

### 🤖 **AI Investment Assistant**
- **Groq-Powered**: Llama 3.3 70B model
- **Natural Language**: Chat-based interface
- **Capabilities**:
  - Stock analysis and recommendations
  - Mutual fund selection
  - Portfolio review
  - Market outlook
  - Investment strategies
- **Context-Aware**: Understands Indian market context

### 📈 **Advanced Analytics**
- **Sector Heat Maps**: Visual sector performance
- **Correlation Analysis**: Inter-stock relationships
- **Volume Intelligence**: Institutional activity detection
- **Momentum Tracking**: Trend identification
- **Market Breadth**: Advance/Decline analysis
- **Sector Rotation**: Identify rotating sectors

---

## 🛠️ Technology Stack

### **Frontend**
- **Streamlit**: Modern web framework for data apps
- **Plotly**: Interactive charts and visualizations
- **HTML/CSS**: Custom styling and components

### **Backend**
- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **SQLite**: Local database for portfolio storage

### **APIs & Data Sources**
- **Yahoo Finance (yfinance)**: Stock market data
- **AMFI API**: Mutual fund NAV data
- **NSE India API**: FII/DII, bulk/block deals
- **MoneyControl**: News and IPO data
- **Economic Times**: Financial news
- **Chittorgarh**: IPO tracking

### **AI & ML**
- **Groq API**: LLM for AI insights (Llama 3.3 70B)
- **TextBlob**: Sentiment analysis
- **VADER**: Financial sentiment analysis
- **scikit-learn**: Machine learning models
- **BeautifulSoup**: Web scraping

### **Technical Analysis**
- **TA-Lib**: Technical indicators
- **Custom Algorithms**: RSI, MACD, Bollinger Bands, ADX

---

## 🏗️ Architecture

```
सार्थक निवेश Platform
│
├── Frontend Layer (Streamlit)
│   ├── Dashboard
│   ├── Stock Intelligence
│   ├── Mutual Fund Center
│   ├── IPO Hub
│   ├── Smart Money Tracker
│   ├── Portfolio Management
│   ├── News & Sentiment
│   ├── AI Assistant
│   └── Advanced Analytics
│
├── Data Layer
│   ├── Real-time APIs
│   │   ├── Yahoo Finance
│   │   ├── AMFI
│   │   ├── NSE India
│   │   └── News Sources
│   │
│   ├── Data Processing
│   │   ├── Data Fetchers
│   │   ├── Data Cleaners
│   │   └── Data Validators
│   │
│   └── Caching Layer
│       └── Streamlit Cache (TTL-based)
│
├── Analytics Engine
│   ├── Technical Analysis
│   │   ├── Indicators (RSI, MACD, etc.)
│   │   ├── Pattern Recognition
│   │   └── Signal Generation
│   │
│   ├── Fundamental Analysis
│   │   ├── Financial Metrics
│   │   ├── Valuation Models
│   │   └── Company Analysis
│   │
│   ├── Sentiment Analysis
│   │   ├── News Processing
│   │   ├── TextBlob/VADER
│   │   └── Impact Scoring
│   │
│   └── Risk Analysis
│       ├── Portfolio Metrics
│       ├── VaR Calculation
│       └── Diversification Scoring
│
├── AI Layer (Groq)
│   ├── Market Analysis
│   ├── Stock Recommendations
│   ├── Portfolio Review
│   ├── News Summarization
│   └── Conversational AI
│
└── Database Layer (SQLite)
    ├── Portfolio Holdings
    ├── Transaction History
    ├── User Preferences
    └── Cache Storage
```

---

## 📦 Modules

### Core Modules

1. **main_ultimate_final.py** (5,700+ lines)
   - Main application entry point
   - All page routing and navigation
   - Dashboard and core functionality

2. **realtime_mutual_fund_fetcher.py**
   - AMFI API integration
   - MF API integration
   - Data merging and enrichment
   - 2400+ funds tracking

3. **realtime_news_fetcher.py**
   - Multi-source news aggregation
   - Sentiment analysis
   - Sector sentiment tracking
   - Trending topics detection

4. **smart_money_live.py**
   - FII/DII tracking from NSE
   - Bulk/Block deals monitoring
   - Volume analysis
   - Sector flow tracking

5. **portfolio_risk_manager.py**
   - Portfolio tracking
   - Risk metrics calculation
   - Performance analytics
   - Rebalancing suggestions

6. **groq_ai_analyzer.py**
   - Groq API integration
   - AI-powered insights
   - Market analysis
   - Conversational AI

7. **realtime_ipo_system.py**
   - Live IPO tracking
   - Multi-source data aggregation
   - GMP tracking
   - Subscription monitoring

8. **advanced_analytics_realtime.py**
   - Sector heat maps
   - Correlation analysis
   - Volume intelligence
   - Market breadth

9. **database_manager.py**
   - SQLite database management
   - Auto-save functionality
   - Data persistence
   - Query optimization

10. **enhanced_quick_actions.py**
    - Quick action handlers
    - SIP calculations
    - Goal planning
    - Investment recommendations

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for real-time data)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/sarthak-nivesh.git
cd sarthak-nivesh
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your Groq API key from: https://console.groq.com/

### Step 5: Run the Application

```bash
streamlit run main_ultimate_final.py
```

The application will open in your default browser at `http://localhost:8501`

---

## ⚙️ Configuration

### config.py

```python
# Application Configuration
APP_NAME = "सार्थक निवेश"
APP_VERSION = "2.0.0"
TEAM_MEMBERS = ["Aman Jain", "Rohit Fogla", "Vanshita Mehta", "Disita Tirthani"]

# API Configuration
GROQ_API_KEY = "your_api_key"

# Data Refresh Intervals (seconds)
STOCK_DATA_TTL = 300  # 5 minutes
MF_DATA_TTL = 1800    # 30 minutes
NEWS_DATA_TTL = 600   # 10 minutes

# Database Configuration
DB_PATH = "sarthak_nivesh.db"
AUTO_SAVE = True

# Display Configuration
STOCKS_PER_PAGE = 30
NEWS_PER_PAGE = 20
```

---

## 📖 Usage Guide

### For Beginners

1. **Start with Dashboard**: Get overview of market indices and top movers
2. **Explore Mutual Funds**: Learn about different fund categories
3. **Use SIP Calculator**: Plan your monthly investments
4. **Read Educational Content**: Understand investment basics

### For Intermediate Investors

1. **Stock Intelligence**: Analyze stocks with technical indicators
2. **Portfolio Tracking**: Monitor your holdings and P&L
3. **News & Sentiment**: Stay updated with market news
4. **IPO Analysis**: Evaluate upcoming IPOs

### For Advanced Traders

1. **Advanced Analytics**: Use sector heat maps and correlation analysis
2. **Smart Money Tracker**: Follow institutional money flow
3. **Risk Management**: Optimize portfolio with VaR and Beta
4. **AI Assistant**: Get AI-powered trading insights

---

## 🔌 API Integration

### Yahoo Finance (yfinance)

```python
import yfinance as yf

# Fetch stock data
ticker = yf.Ticker("RELIANCE.NS")
data = ticker.history(period="1y")
info = ticker.info
```

### AMFI API

```python
import requests

# Fetch mutual fund NAV
url = "https://www.amfiindia.com/spages/NAVAll.txt"
response = requests.get(url)
data = response.text
```

### NSE India API

```python
import requests

# Fetch FII/DII data
session = requests.Session()
session.get("https://www.nseindia.com")
url = "https://www.nseindia.com/api/fiidiiTradeReact"
data = session.get(url).json()
```

### Groq API

```python
from groq import Groq

client = Groq(api_key="your_api_key")
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Analyze RELIANCE stock"}]
)
```

---

## 🗄️ Database Schema

### Portfolio Holdings Table

```sql
CREATE TABLE portfolio_holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    company_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    buy_price REAL NOT NULL,
    buy_date TEXT NOT NULL,
    sector TEXT,
    current_price REAL,
    current_value REAL,
    pnl REAL,
    pnl_pct REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Transaction History Table

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    transaction_type TEXT NOT NULL, -- BUY/SELL
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    transaction_date TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)
*Real-time market overview with NIFTY, SENSEX, top gainers/losers*

### Stock Intelligence
![Stock Analysis](screenshots/stock_intelligence.png)
*Comprehensive technical and fundamental analysis*

### Mutual Fund Center
![Mutual Funds](screenshots/mutual_funds.png)
*2400+ funds with real-time NAV and SIP calculator*

### Portfolio Management
![Portfolio](screenshots/portfolio.png)
*Professional portfolio tracking with risk metrics*

### AI Assistant
![AI Assistant](screenshots/ai_assistant.png)
*Groq-powered conversational AI for investment advice*

---

## 👥 Team

### Development Team

- **Aman Jain** - Lead Developer & Architect
- **Rohit Fogla** - Backend & API Integration
- **Vanshita Mehta** - Frontend & UI/UX
- **Disita Tirthani** - Data Analytics & Testing

### Contact

- **Email**: team@sarthaknivesh.com
- **GitHub**: https://github.com/sarthaknivesh
- **LinkedIn**: [Team LinkedIn]

---

## 🔮 Future Scope

### Phase 1: Enhanced Features (Q2 2026)

1. **Mobile Application**
   - Native Android/iOS apps
   - Push notifications for price alerts
   - Offline portfolio tracking

2. **Social Trading**
   - Follow expert investors
   - Copy trading functionality
   - Community discussions

3. **Advanced Charting**
   - TradingView integration
   - Custom indicators
   - Drawing tools

4. **Backtesting Engine**
   - Strategy backtesting
   - Historical performance analysis
   - Optimization tools

### Phase 2: AI & Automation (Q3 2026)

1. **Robo-Advisory**
   - Automated portfolio management
   - Auto-rebalancing
   - Tax-loss harvesting

2. **Predictive Analytics**
   - Price prediction models
   - Earnings prediction
   - Market crash detection

3. **Natural Language Trading**
   - Voice commands
   - WhatsApp bot integration
   - Telegram alerts

4. **Smart Alerts**
   - Custom alert conditions
   - Multi-channel notifications
   - AI-generated insights

### Phase 3: Institutional Features (Q4 2026)

1. **Options & Derivatives**
   - Options chain analysis
   - Greeks calculator
   - Strategy builder

2. **Algorithmic Trading**
   - Strategy marketplace
   - Automated execution
   - Paper trading

3. **Research Reports**
   - AI-generated reports
   - Sector analysis
   - Company deep-dives

4. **API Access**
   - Developer API
   - Webhook integrations
   - Custom dashboards

### Phase 4: Global Expansion (2027)

1. **International Markets**
   - US stocks (NYSE, NASDAQ)
   - European markets
   - Asian markets

2. **Cryptocurrency**
   - Crypto portfolio tracking
   - DeFi integration
   - NFT tracking

3. **Multi-language Support**
   - Hindi, Tamil, Telugu, Bengali
   - Regional language support
   - Localized content

4. **Premium Features**
   - Advanced analytics
   - Priority support
   - Exclusive research

### Long-term Vision

- **AI-First Platform**: Complete AI-driven investment management
- **Democratize Investing**: Make institutional-grade tools accessible to everyone
- **Financial Literacy**: Educate 10 million Indians about investing
- **Zero-Commission Trading**: Partner with brokers for commission-free trading
- **Wealth Management**: Comprehensive wealth management platform

---

## 🤝 Contributing

We welcome contributions from the community!

### How to Contribute

1. **Fork the Repository**
2. **Create Feature Branch**
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit Changes**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push to Branch**
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Open Pull Request**

### Contribution Guidelines

- Follow PEP 8 style guide
- Write clear commit messages
- Add tests for new features
- Update documentation
- Ensure all tests pass

### Areas for Contribution

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation
- 🎨 UI/UX improvements
- 🧪 Testing
- 🌐 Translations

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 सार्थक निवेश Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## ⚠️ Disclaimer

**Important**: This platform is for educational and informational purposes only. It is not financial advice.

- **Not Financial Advice**: All information provided is for educational purposes
- **Do Your Research**: Always conduct your own research before investing
- **Risk Warning**: Investments in securities market are subject to market risks
- **No Guarantees**: Past performance is not indicative of future results
- **Consult Professionals**: Consult with a certified financial advisor before making investment decisions

**We are not SEBI registered investment advisors. Use this platform at your own risk.**

---

## 🙏 Acknowledgments

- **Yahoo Finance** for stock market data
- **AMFI** for mutual fund data
- **NSE India** for institutional data
- **Groq** for AI capabilities
- **Streamlit** for the amazing framework
- **Open Source Community** for various libraries

---

## 📞 Support

### Get Help

- **Documentation**: [Read the Docs](https://docs.sarthaknivesh.com)
- **FAQ**: [Frequently Asked Questions](https://sarthaknivesh.com/faq)
- **Email**: support@sarthaknivesh.com
- **Discord**: [Join our community](https://discord.gg/sarthaknivesh)

### Report Issues

Found a bug? [Create an issue](https://github.com/sarthaknivesh/issues)

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=sarthaknivesh/sarthak-nivesh&type=Date)](https://star-history.com/#sarthaknivesh/sarthak-nivesh&Date)

---

## 📊 Project Stats

- **Lines of Code**: 15,000+
- **Modules**: 15+
- **Stocks Tracked**: 120+
- **Mutual Funds**: 2,400+
- **API Integrations**: 10+
- **Features**: 50+
- **Development Time**: 6 months
- **Team Size**: 4 developers

---

<div align="center">

### Made with ❤️ in India

**"Ye Dil Maange More" - Because Your Investments Deserve More!**

[Website](https://sarthaknivesh.com) • [Documentation](https://docs.sarthaknivesh.com) • [Blog](https://blog.sarthaknivesh.com)

---

**⭐ Star us on GitHub — it motivates us a lot!**

</div>
