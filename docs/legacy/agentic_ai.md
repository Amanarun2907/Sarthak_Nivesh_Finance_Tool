# Agentic AI Project Documentation

## 1. Project Title
**Sarthak Nivesh: AI-Powered IPO & Stock Market Analysis Platform**

---

## 2. Team Members
| Name | Roll Number |
|------|-------------|
| Aman Jain | [Roll Number] |
| Jhalak Kapila | [Roll Number] |
| Khushi Hooda | [Roll Number] |

---

## 3. Problem Definition

### What problem are you addressing?
Retail investors in India face significant challenges when making investment decisions regarding IPOs, stocks, and portfolio management. The primary problems include:

- **Lack of comprehensive IPO analysis tools** that provide post-listing performance tracking and hold/exit recommendations
- **Information overload** from multiple sources without proper sentiment analysis and fake news detection
- **Limited access to professional-grade analytics** for stock analysis, risk assessment, and portfolio optimization
- **Difficulty in understanding complex market data** and translating it into actionable investment insights
- **Absence of personalized investment recommendations** based on individual risk profiles and financial goals

### Who are the intended users?
- **Retail Investors**: Individual investors looking for data-driven investment decisions in stocks, IPOs, and mutual funds
- **First-time Investors**: Beginners seeking educational content and simple investment guidance
- **Portfolio Managers**: Individuals managing their own investment portfolios and needing risk assessment tools
- **Students & Researchers**: Academic users studying market behavior and investment strategies

---

## 4. Objectives & Expected Outcomes

### Key Objectives

1. **Develop an Intelligent IPO Analysis System**
   - Create India's first comprehensive IPO intelligence platform
   - Provide post-listing performance tracking (30/60/90 days)
   - Generate AI-powered hold/exit recommendations with confidence scores
   - Track retail sentiment impact on IPO pricing

2. **Build a Multi-Agent Stock Analysis Framework**
   - Deploy specialized AI agents for price movement, macroeconomic factors, sentiment analysis, and risk assessment
   - Implement real-time data integration from authentic sources (NSE, BSE, Yahoo Finance)
   - Provide technical and fundamental analysis with professional-grade indicators

3. **Create a Comprehensive Portfolio & Risk Management System**
   - Enable portfolio tracking with real-time P&L calculation
   - Calculate advanced risk metrics (VaR, Beta, Sharpe Ratio)
   - Provide personalized mutual fund and SIP recommendations
   - Implement sentiment analysis with fake news detection

### Expected Outcomes

- **Working AI Tool**: Fully functional platform with IPO analysis, stock analysis, portfolio management, and sentiment analysis capabilities
- **Autonomous Agent System**: Team of 6 specialized AI agents working collaboratively to analyze market data and provide investment insights
- **User-Friendly Interface**: Streamlit-based web application with intuitive design and crystal-clear visualizations
- **Performance Validation**: Comprehensive evaluation report demonstrating accuracy on historical IPO and stock data

---

## 5. Proposed Methodology

### Agents and Their Roles

**1. Price Movement Agent**
- **Role**: Analyze historical price data and predict future movements
- **Responsibilities**:
  - Calculate technical indicators (RSI, MACD, Bollinger Bands, Moving Averages)
  - Identify price trends and patterns
  - Generate short-term price predictions using LSTM models
  - Detect support and resistance levels

**2. Macroeconomic Agent**
- **Role**: Analyze broader economic factors affecting stock performance
- **Responsibilities**:
  - Track sector-wise performance and trends
  - Monitor market indices (NIFTY, SENSEX)
  - Analyze institutional money flow (FII/DII data)
  - Evaluate market breadth and momentum

**3. Sentiment Agent**
- **Role**: Analyze news and social media sentiment
- **Responsibilities**:
  - Collect real-time news from Economic Times, MoneyControl, Business Standard
  - Perform multi-source sentiment analysis (VADER, TextBlob, Financial Keywords)
  - Detect fake news with 85%+ accuracy
  - Track retail investor sentiment impact on pricing

**4. Risk Agent**
- **Role**: Assess investment risk and portfolio optimization
- **Responsibilities**:
  - Calculate portfolio risk metrics (volatility, VaR, max drawdown)
  - Compute Beta, Sharpe Ratio, and diversification scores
  - Provide rebalancing recommendations
  - Evaluate sector concentration and correlation

**5. IPO Intelligence Agent**
- **Role**: Comprehensive IPO analysis and recommendations
- **Responsibilities**:
  - Track post-IPO performance (30/60/90 days)
  - Calculate liquidity scores and volatility metrics
  - Generate hold/exit recommendations with confidence levels
  - Analyze subscription data and grey market premium (GMP)

**6. Orchestrator Agent**
- **Role**: Coordinate all specialized agents and synthesize insights
- **Responsibilities**:
  - Route queries to appropriate specialized agents
  - Aggregate multi-agent outputs into unified recommendations
  - Resolve conflicts between agent recommendations
  - Generate final investment advice with confidence scores

### Tools/APIs to be Used

**Data Sources & APIs**:
- **Yahoo Finance (yfinance)**: Real-time stock prices, historical data, technical indicators
- **AMFI API**: Mutual fund NAV data (2400+ funds)
- **NSE India API**: FII/DII flows, bulk/block deals, institutional data
- **NewsAPI**: Financial news aggregation
- **RSS Feeds**: Economic Times, MoneyControl, Business Standard
- **BeautifulSoup**: Web scraping for IPO data

**Technical Analysis Libraries**:
- **Pandas & NumPy**: Data manipulation and numerical computations
- **Plotly**: Interactive charts and visualizations
- **scikit-learn**: Machine learning models for predictions

**NLP & Sentiment Analysis**:
- **TextBlob**: Basic sentiment analysis
- **VADER Sentiment**: Financial sentiment scoring
- **Custom keyword analysis**: Domain-specific financial sentiment

### LLM/Model and Agentic AI Framework

**Large Language Model**:
- **Groq (Llama 3.3 70B Versatile)**: Ultra-fast inference for AI-powered insights
- **Use Cases**: Natural language query processing, investment recommendations, conversational AI assistant

**Agentic AI Framework**:
- **CrewAI**: Multi-agent orchestration framework
- **Features**:
  - Agent role definition and specialization
  - Task assignment and delegation
  - Collaborative decision-making
  - Sequential and hierarchical workflows

**Machine Learning Models**:
- **LSTM Neural Networks**: Stock price prediction (65-75% accuracy)
- **Random Forest & Gradient Boosting**: IPO performance prediction (70-75% accuracy)
- **Ensemble Methods**: Multi-model sentiment analysis (85%+ accuracy)
- **Statistical Models**: Risk assessment using Modern Portfolio Theory

### Brief Workflow of the Proposed System

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE (Streamlit)                  │
│  Dashboard | Stock Analysis | IPO Hub | Portfolio | Sentiment   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                           │
│  • Routes user queries to specialized agents                     │
│  • Aggregates multi-agent insights                              │
│  • Generates final recommendations                              │
└───┬─────────────┬─────────────┬──────────────┬─────────────┬───┘
    │             │             │              │             │
    ▼             ▼             ▼              ▼             ▼
┌────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌─────────────┐
│ Price  │  │  Macro   │  │Sentiment │  │  Risk  │  │IPO Intelligence│
│Movement│  │ Economic │  │  Agent   │  │ Agent  │  │    Agent      │
│ Agent  │  │  Agent   │  │          │  │        │  │              │
└───┬────┘  └────┬─────┘  └────┬─────┘  └───┬────┘  └──────┬──────┘
    │            │             │            │              │
    │ Technical  │ Market      │ News       │ Portfolio    │ IPO
    │ Analysis   │ Indicators  │ Sentiment  │ Metrics      │ Analysis
    │            │             │            │              │
    ▼            ▼             ▼            ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PROCESSING LAYER                         │
│  • Data fetchers • Cleaners • Validators • Cache                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA SOURCES                                │
│  Yahoo Finance | AMFI | NSE India | News APIs | Web Scraping   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (SQLite)                             │
│  Portfolio Holdings | Transactions | Cache | User Preferences   │
└─────────────────────────────────────────────────────────────────┘
```

**Workflow Steps**:

1. **User Input**: User queries through Streamlit interface (e.g., "Analyze Reliance Industries")

2. **Orchestrator Routing**: Orchestrator agent analyzes query and delegates to relevant specialized agents

3. **Parallel Agent Execution**:
   - Price Movement Agent: Fetches historical data, calculates technical indicators
   - Macro Agent: Analyzes sector performance, market trends
   - Sentiment Agent: Collects news, performs sentiment analysis
   - Risk Agent: Calculates risk metrics if portfolio-related
   - IPO Agent: Provides IPO-specific analysis if applicable

4. **Data Collection**: Each agent fetches required data from APIs and databases

5. **Agent Analysis**: Agents process data using ML models and statistical methods

6. **Result Aggregation**: Orchestrator collects all agent outputs

7. **Synthesis & Recommendation**: Orchestrator generates unified recommendation with confidence score

8. **Presentation**: Results displayed through interactive visualizations and clear explanations

---

## 6. Feasibility & Resources

### Data Sources
- **Yahoo Finance API**: Free, unlimited access to stock data (15-min delay)
- **AMFI API**: Free, official mutual fund NAV data
- **NSE India API**: Free, institutional trading data
- **RSS Feeds**: Free access to Economic Times, MoneyControl, Business Standard
- **NewsAPI**: 1000 free API calls/day for news aggregation

**Data Authenticity**: 100% real data from official sources, no dummy or simulated data

### APIs/Tools
- **Groq API**: Free tier with generous limits for Llama 3.3 70B
- **Yahoo Finance (yfinance)**: Open-source Python library
- **BeautifulSoup**: Free web scraping library
- **Streamlit**: Free and open-source web framework
- **SQLite**: Embedded database, no separate server required

### Software/Frameworks
- **Python 3.8+**: Core programming language
- **Streamlit**: Frontend framework
- **CrewAI**: Multi-agent orchestration
- **Pandas & NumPy**: Data processing
- **Plotly**: Interactive visualizations
- **scikit-learn**: Machine learning
- **TextBlob & VADER**: Sentiment analysis

### Compute/Resources Required
- **Development Machine**: Standard laptop/desktop (4GB+ RAM)
- **Production Deployment**: 
  - Cloud hosting (AWS/GCP/Azure free tier) or
  - Streamlit Community Cloud (free hosting)
- **Storage**: 1-2GB for database and cached data
- **Internet**: Stable connection for real-time data fetching

**Estimated Monthly Cost**: $0 (using free tiers) to $10-20 (with premium APIs)

---

## 7. Team Members & Individual Understanding

| Member | Role/Responsibility | Individual Understanding |
|--------|---------------------|--------------------------|
| **Aman Jain** | **Project Lead & Backend Development**<br>- Multi-agent system architecture<br>- API integration (Yahoo Finance, AMFI, NSE)<br>- Database design and management<br>- Stock & IPO analysis algorithms | Understanding: Expertise in Python backend development, AI/ML model integration, CrewAI framework implementation, real-time data processing, and system architecture design. Responsible for building the core agent orchestration system and ensuring seamless integration between agents. |
| **Jhalak Kapila** | **Frontend Development & UI/UX**<br>- Streamlit interface design<br>- Interactive visualizations (Plotly)<br>- User experience optimization<br>- Responsive layout implementation | Understanding: Proficiency in Streamlit framework, data visualization libraries, frontend design principles, and creating intuitive user interfaces. Responsible for translating complex financial data into clear, actionable visualizations that users can easily understand. |
| **Khushi Hooda** | **AI/ML & Sentiment Analysis**<br>- NLP models (TextBlob, VADER)<br>- Fake news detection algorithm<br>- Machine learning models (LSTM, Random Forest)<br>- Model training and evaluation | Understanding: Strong foundation in natural language processing, sentiment analysis techniques, machine learning algorithms, and model optimization. Responsible for developing accurate sentiment analysis systems and predictive models for stock and IPO performance. |

---

## 8. Project Timeline

| Activity | Week(s) | Deliverable |
|----------|---------|-------------|
| **Problem & Design** | Week 1-2 | - Requirements documentation<br>- System architecture design<br>- Agent role definitions<br>- API research and selection<br>- Database schema design |
| **Development/Coding** | Week 3-8 | - Multi-agent system implementation<br>- API integrations (Yahoo Finance, AMFI, NSE)<br>- Technical analysis algorithms<br>- Sentiment analysis module<br>- IPO intelligence system<br>- Portfolio management features |
| **Integration & Testing/Debugging** | Week 9-10 | - Agent coordination testing<br>- API reliability testing<br>- End-to-end workflow validation<br>- Performance optimization<br>- Bug fixing and refinement |
| **Evaluation & Refinement** | Week 11 | - Accuracy evaluation on historical data<br>- Model performance tuning<br>- User experience improvements<br>- Code refactoring and optimization |
| **Presentation/Interface UI** | Week 12 | - Final UI polish<br>- Dashboard enhancements<br>- Visualization improvements<br>- User documentation<br>- Demo preparation |
| **Deployment** | Week 13 | - Production environment setup<br>- Streamlit Cloud deployment<br>- Performance monitoring setup<br>- Security hardening |
| **Final Demo** | Week 14 | - Live demonstration<br>- Presentation to stakeholders<br>- Documentation handover<br>- Project showcase |

---

## 9. Team Responsibility Matrix

| Activity | Aman Jain | Jhalak Kapila | Khushi Hooda |
|----------|-----------|---------------|--------------|
| **Agent Design** | Lead - Agent architecture, orchestration logic, workflow design | Support - User interaction design | Support - ML model architecture |
| **Agent/Tool Development** | Lead - Backend agents (Price Movement, Macro, Risk, IPO), API integration, orchestrator | Support - Frontend integration, API testing | Lead - Sentiment Agent, ML models (LSTM, Random Forest), NLP pipeline |
| **Integration & Testing** | Lead - System integration, API testing, database operations | Lead - UI testing, visualization testing, user flow testing | Lead - Model validation, accuracy testing, sentiment analysis testing |
| **Evaluation & Documentation** | Support - Performance metrics, technical documentation | Support - User guide, UI documentation | Lead - Model evaluation report, accuracy metrics, performance analysis |
| **Presentation/Interface UI** | Support - Technical demos, backend explanations | Lead - UI/UX design, frontend presentation, visual demonstrations | Support - ML model explanations, accuracy presentations |
| **Deployment** | Lead - Server deployment, API configuration, database setup, production monitoring | Support - Frontend deployment, UI optimization | Support - Model deployment, testing in production |

**Collaboration Notes**:
- Daily standups for progress tracking
- Shared GitHub repository for version control
- Weekly code reviews and integration meetings
- Agile methodology with 2-week sprints
- Documentation maintained throughout development

---

## 10. Technical Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────┐
│                    SARTHAK NIVESH PLATFORM                         │
│                                                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              PRESENTATION LAYER (Streamlit)                  │ │
│  │  • Dashboard  • Stock Analysis  • IPO Hub  • Portfolio      │ │
│  │  • Mutual Funds  • News & Sentiment  • AI Assistant         │ │
│  └────────────────────────────┬────────────────────────────────┘ │
│                               │                                   │
│  ┌────────────────────────────▼────────────────────────────────┐ │
│  │                    ORCHESTRATOR AGENT                        │ │
│  │  (CrewAI Framework)                                         │ │
│  │  • Query routing  • Agent coordination                      │ │
│  │  • Result aggregation  • Conflict resolution               │ │
│  └─┬────────┬────────┬────────┬────────┬────────────────────┘ │
│    │        │        │        │        │                        │
│  ┌─▼──┐  ┌─▼──┐  ┌─▼────┐ ┌─▼───┐ ┌─▼──────────┐           │
│  │Price│  │Macro│  │Senti-│ │Risk │ │IPO Intelli-│           │
│  │Move │  │Econ │  │ment  │ │Agent│ │gence Agent │           │
│  │Agent│  │Agent│  │Agent │ │     │ │            │           │
│  └─┬──┘  └─┬──┘  └─┬────┘ └─┬───┘ └─┬──────────┘           │
│    │        │        │        │        │                        │
│  ┌─▼────────▼────────▼────────▼────────▼────────────────────┐ │
│  │              AI/ML PROCESSING LAYER                       │ │
│  │  • LSTM (Price Prediction)                                │ │
│  │  • Random Forest (IPO Analysis)                           │ │
│  │  • Ensemble Sentiment (VADER + TextBlob + Keywords)      │ │
│  │  • Statistical Models (Risk Metrics, MPT)                │ │
│  └────────────────────────────┬──────────────────────────────┘ │
│                               │                                   │
│  ┌────────────────────────────▼──────────────────────────────┐ │
│  │              DATA PROCESSING LAYER                         │ │
│  │  • Data Fetchers  • Cleaners  • Validators               │ │
│  │  • Caching (TTL-based)  • Error Handling                 │ │
│  └─┬────────┬────────┬────────┬────────┬────────────────────┘ │
│    │        │        │        │        │                        │
│  ┌─▼──────┐ │      ┌─▼──────┐ │      ┌─▼─────────┐           │
│  │Yahoo   │ │      │NSE     │ │      │NewsAPI/   │           │
│  │Finance │ │      │India   │ │      │RSS Feeds  │           │
│  └────────┘ │      └────────┘ │      └───────────┘           │
│           ┌─▼──────┐        ┌─▼──────┐                        │
│           │AMFI    │        │Web     │                        │
│           │API     │        │Scraping│                        │
│           └────────┘        └────────┘                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              DATABASE LAYER (SQLite)                      │ │
│  │  • Portfolio Holdings  • Transactions  • User Prefs      │ │
│  │  • Cached Data  • Historical Analysis                    │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

---

## 11. Success Metrics

### Quantitative Metrics
- **IPO Recommendation Accuracy**: Target 70%+ for hold/exit recommendations
- **Stock Price Prediction Accuracy**: Target 65-75% for short-term trends
- **Sentiment Analysis Accuracy**: Target 85%+ for financial news classification
- **Fake News Detection Rate**: Target 85%+ precision in identifying unreliable sources
- **System Response Time**: < 5 seconds for standard queries
- **Data Freshness**: Real-time updates every 5-15 minutes during market hours

### Qualitative Metrics
- User-friendly interface with intuitive navigation
- Clear and actionable investment insights
- Professional-grade visualizations
- Comprehensive educational content
- Reliable and authentic data sources

---

## 12. Risk Mitigation

### Technical Risks
- **API Rate Limits**: Use multiple data sources and implement caching
- **Data Quality**: Validate and cross-check data from multiple sources
- **Model Accuracy**: Use ensemble methods and conservative confidence thresholds
- **System Downtime**: Implement error handling and fallback mechanisms

### Compliance & Legal
- **Disclaimer**: Clear notice that platform is for educational purposes only
- **No Financial Advice**: Explicit statement that it's not registered investment advisory
- **Data Attribution**: Proper credits to all data sources
- **User Risk Awareness**: Prominent risk warnings throughout the platform

---

## 13. Future Enhancements

### Phase 2 (Post-Completion)
- Mobile application (Android/iOS)
- Options and derivatives analysis
- Cryptocurrency portfolio tracking
- Social trading features
- Premium subscription tier
- Multi-language support (Hindi, regional languages)
- Voice-based queries and commands
- Advanced pattern recognition algorithms
- Automated portfolio rebalancing
- Tax optimization suggestions

---

**Project Status**: Development Phase
**Expected Completion**: Week 14
**Target Deployment**: Streamlit Community Cloud

---

**Disclaimer**: This platform is developed for educational and research purposes. It does not constitute financial advice. Users should conduct their own research and consult with certified financial advisors before making investment decisions.
