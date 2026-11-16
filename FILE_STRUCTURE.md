# 📁 Sarthak Nivesh - Complete File Structure

> **Organized on:** October 26, 2026  
> **Project:** IPO Multi-Agent Intelligence Platform  
> **Team:** Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani

---

## 🚀 Quick Start

### Main Entry Points (Root Directory)
- **`🚀_DOUBLE_CLICK_TO_START.bat`** - Complete system launcher (Frontend + Backend)
- **`RUN_COMPLETE_PROJECT.bat`** - Alternative launcher
- **`START_COMPLETE_SYSTEM.bat`** - System startup script
- **`README.md`** - Main project documentation

### Essential Configuration
- **`.env`** - Environment variables (API keys, database)
- **`.gitignore`** - Git exclusion rules

---

## 📂 Directory Structure

### 🔧 **core/** - Core Backend Systems
```
core/
├── a2a_protocol.py                    # Agent-to-Agent communication protocol
├── agent_control_tower.py             # Real-time agent monitoring & orchestration
├── complete_platform_functions.py     # Integrated platform utilities
├── config.py                          # Base configuration
├── config_enhanced.py                 # Enhanced configuration with all features
├── data_service.py                    # Data fetching & processing
├── data_sync_service.py               # Real-time data synchronization
├── dynamic_exit_strategy.py           # ML-based exit strategy generator
├── enhanced_config.py                 # Production-ready configuration
├── explainability_engine.py           # AI explainability & transparency
├── guardrails_security.py             # Security & input validation
├── mcp_tools.py                       # Model Context Protocol tools
├── real_time_data_fetcher.py          # Live market data integration
├── requirements.txt                   # Core dependencies
└── run_*.bat                          # Core module launchers
```

**Purpose:** Contains all core backend logic, AI agent systems, security, and data services.

---

### 🗄️ **data/** - Database Storage
```
data/
└── sarthak_nivesh.db                  # SQLite database (portfolio, goals, IPOs)
```

**Purpose:** Local database for user data, portfolio holdings, SIP goals, and IPO tracking.

---

### 📚 **docs/** - Project Documentation (Legacy)
```
docs/
├── ALL_PAGES_*.md                     # Feature verification docs
├── COMPLETE_*.md                      # Comprehensive project summaries
├── DATABASE_SETUP_COMPLETE.md         # Database setup guide
├── ERROR_FREE_CONFIRMATION.md         # Testing confirmation
├── HACKATHON_FEATURES.md              # Competition-specific features
├── HOW_TO_USE_INTEGRATED_PLATFORM.md  # User guide
├── PHASE_*.md                         # Development phase reports
├── README*.md                         # Various README versions
└── WHY_TABS_ARE_EMPTY.md              # Troubleshooting guide
```

**Purpose:** Legacy documentation from development phases. **Most recent docs are in `project_documentation/`**.

---

### 📖 **project_documentation/** - Organized Documentation ⭐
```
project_documentation/
├── guides/                            # User & developer guides
│   ├── FORMULA_QUICK_REFERENCE.txt
│   ├── HOW_TO_USE_ENHANCED_PAPER.txt
│   ├── IPO_INTELLIGENCE_COMPLETE_GUIDE.txt
│   ├── QUICK_REFERENCE.txt
│   ├── QUICK_START.txt
│   ├── RESEARCH_PAPER_GUIDE.txt
│   ├── RESEARCH_PAPER_IMPROVEMENTS.txt
│   └── START_HERE.txt
│
├── summaries/                         # Project status & summaries
│   ├── BACKEND_FIX_SUMMARY.txt
│   ├── CHARTS_GENERATED_SUMMARY.md
│   ├── COMPLETE_PACKAGE_SUMMARY.md
│   ├── COMPREHENSIVE_PROJECT_STATUS_REPORT.md
│   ├── FINAL_COMMAND_SUMMARY.txt
│   ├── FINAL_PROJECT_STATUS_REPORT.txt
│   ├── FRONTEND_REQUIREMENTS_MAP.txt
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── MATHEMATICAL_NOTATION_FIX_COMPLETE.md
│   ├── NEW_FILE_CREATED_SUMMARY.txt
│   ├── NON_MATHEMATICAL_VERSION_INFO.md
│   ├── ORGANIZATION_AND_PUSH_SUMMARY.txt
│   ├── PHENOMENAL_SYSTEM_COMPLETE.txt
│   ├── PROBLEM_COMPLETELY_SOLVED.txt
│   ├── PROJECT_ORGANIZATION.md
│   ├── SYSTEM_READY_SUMMARY.txt
│   ├── VISUALIZATIONS_INDEX.md
│   └── 🎯_ULTIMATE_SYSTEM_READY.txt
│
├── research_papers/                   # Academic papers
│   ├── IIT_MADRAS PAPER.docx
│   ├── Research_Paper_FINAL_READABLE.txt
│   ├── Research_Paper_IPO_Madras.txt
│   ├── Research_Paper_IPO_Madras_CLEAR_READABLE.txt
│   ├── Research_Paper_IPO_Madras_Enhanced.txt
│   ├── Research_Paper_IPO_Madras_Enhanced_Complete.txt
│   ├── Research_Paper_IPO_Madras_FINAL_CLEAR.txt
│   ├── Research_Paper_IPO_Madras_NO_MATH_VERSION.txt
│   └── Research_Paper_IPO_Madras_PERFECTLY_READABLE.txt
│
├── agentic_ai.md                      # Agentic AI architecture
├── B_T.md                             # Backtesting documentation
└── GROQ_API_FIXED.md                  # API integration guide
```

**Purpose:** ⭐ **START HERE** - All organized guides, summaries, and research papers.

---

### 📊 **archived_outputs/** - Generated Outputs & Results
```
archived_outputs/
├── test_results/                      # Test execution results
│   ├── backend_test_results.json
│   ├── final_test_results.json
│   └── ipo_intelligence_test_results.json
│
├── analysis_results/                  # IPO analysis outputs
│   ├── enhanced_analysis_SWIGGY_20261026_194702.json
│   └── enhanced_analysis_SWIGGY_20261026_195038.json
│
├── charts/                            # Dataset visualizations
│   ├── dataset_chart1_universe.png
│   ├── dataset_chart2_prices.png
│   ├── dataset_chart3_distribution.png
│   ├── dataset_chart4_stats_table.png
│   ├── dataset_chart5_correlation.png
│   ├── dataset_chart6_skew_kurt.png
│   ├── dataset_chart7_vol_heatmap.png
│   ├── dataset_chart8_tests.png
│   ├── dataset_chart9_rolling_vol.png
│   ├── dataset_chart10_architecture.png
│   ├── dataset_chart11_sector_map.png
│   ├── dataset_chart12_vader.png
│   ├── dataset_chart14_volume.png
│   └── dataset_chart15_summary.png
│
└── backtest_images/                   # Agent backtest results
    ├── agent1_backtest.png
    ├── agent2_backtest.png
    ├── agent3_backtest.png
    ├── agent4_backtest.png
    ├── agent5_backtest.png
    ├── agent6_backtest.png
    ├── bt_chart1_listing_gains.png
    ├── bt_chart2_multihorizon.png
    ├── bt_chart3_agent_scores.png
    ├── bt_chart4_accuracy.png
    ├── bt_chart5_portfolio.png
    ├── bt_chart6_agent_accuracy.png
    ├── bt_chart7_subscription.png
    ├── bt_chart8_risk_stats.png
    ├── bt_chart9_dashboard.png
    ├── combined_agentic_ai_backtest.png
    └── prediction_vs_actual.png
```

**Purpose:** All test outputs, analysis results, charts, and backtest visualizations.

---

### 🛠️ **utility_scripts/** - Helper Scripts
```
utility_scripts/
├── ipo_backtest/                      # IPO backtesting utilities
│   ├── build_ipo_backtest_nb.py
│   ├── ipo_bt_build_nb.py
│   ├── ipo_bt_embed_outputs.py
│   ├── ipo_bt_master.py
│   ├── ipo_bt_part1.py through part10.py
│   └── run_ipo_backtest.py
│
├── notebook_builders/                 # Jupyter notebook generators
│   ├── create_non_mathematical_version.py
│   └── nb_builder.py
│
├── fixes/                             # Bug fix & correction scripts
│   ├── fix_all_math_notation_final.py
│   ├── fix_complete_notation.py
│   ├── fix_math_notation.py
│   ├── fix_multi_charts.py
│   └── fix_nb_outputs.py
│
└── main_ultimate_final.py             # Legacy main entry point
```

**Purpose:** Development utilities, backtest builders, notebook generators, and fix scripts.

---

### 🧪 **test_scripts/** - Testing Suite
```
test_scripts/
├── COMPREHENSIVE_BACKEND_TEST.py      # Complete backend validation
├── final_comprehensive_test.py        # End-to-end system test
├── final_section_verification.py      # Frontend section verification
├── quick_bug_test.py                  # Quick debugging tool
├── test_api_comprehensive.py          # API endpoint testing
├── test_final_comprehensive.py        # Final integration test
├── TEST_FIXED_SYSTEM.py               # Fixed system validation
├── TEST_IPO_INTELLIGENCE.py           # IPO intelligence module test
├── test_ipo_intelligence_e2e.py       # End-to-end IPO test
├── test_phase1.py                     # Phase 1 tests
├── test_phase2.py                     # Phase 2 tests
└── TEST_ULTIMATE_SYSTEM.py            # Ultimate system test (all 10 requirements)
```

**Purpose:** Comprehensive test suite for all modules and requirements.

---

### 🚀 **deployment/** - Deployment Scripts
```
deployment/
└── bat_files/                         # Windows batch launchers
    ├── RUN_COMPLETE_PROJECT.bat       # Main launcher (also in root)
    ├── START_COMPLETE_SYSTEM.bat      # System startup (also in root)
    ├── 🚀_DOUBLE_CLICK_TO_START.bat  # Quick start (also in root)
    └── [other development .bat files]
```

**Purpose:** Deployment and launcher scripts (main ones copied to root for easy access).

---

### 🌐 **web/** - Full-Stack Application
```
web/
├── backend/                           # FastAPI Backend
│   ├── routers/                       # API endpoints
│   │   ├── ipo_ultimate_fixed.py     # ⭐ MAIN: Enhanced IPO system (ALL 10 requirements)
│   │   ├── ipo_multiagent_ultimate.py
│   │   ├── ipo_intelligence_complete.py
│   │   ├── agent_control_tower_api.py
│   │   ├── dashboard.py
│   │   ├── stocks.py
│   │   ├── mutual_funds.py
│   │   ├── sip_goals.py
│   │   ├── ipo.py
│   │   ├── smart_money.py
│   │   ├── portfolio.py
│   │   ├── news.py
│   │   ├── ai_assistant.py
│   │   ├── analytics.py
│   │   └── agentic.py
│   │
│   └── main.py                        # FastAPI app entry point
│
└── frontend/                          # React Frontend
    ├── src/
    │   ├── pages/                     # Main application pages
    │   │   ├── IPOMultiAgent.js      # ⭐ IPO Multi-Agent (ALL 10 requirements)
    │   │   ├── AgenticAI.js          # Agentic AI Hub
    │   │   ├── EnhancedIPOAnalysis.js
    │   │   ├── AgentControlTower.js  # Real-time monitoring
    │   │   ├── Dashboard.js
    │   │   ├── StockIntelligence.js
    │   │   ├── MutualFunds.js
    │   │   ├── SIPGoals.js
    │   │   ├── IPOIntelligence.js
    │   │   ├── SmartMoney.js
    │   │   ├── Portfolio.js
    │   │   ├── News.js
    │   │   └── Analytics.js
    │   │
    │   ├── components/                # Reusable components
    │   ├── api.js                     # ⭐ API client (updated with ipoFixed endpoints)
    │   └── App.js                     # Main React app
    │
    ├── public/
    └── package.json
```

**Purpose:** Complete full-stack web application (React frontend + FastAPI backend).

---

### 📔 **sections/** - Modular Application Sections
```
sections/
├── 02_stock_intelligence/
├── 03_mutual_fund_sip/
├── 04_ipo_intelligence/
├── 05_smart_money_tracker/
├── 06_agentic_ai_hub/
├── 07_portfolio_risk/
├── 08_news_sentiment/
├── 09_ai_assistant/
└── 10_advanced_analytics/
```

**Purpose:** Modular section implementations (Streamlit prototypes and backend logic).

---

### 📓 **notebooks/** - Jupyter Notebooks
```
notebooks/
└── [Jupyter notebooks for analysis, backtesting, research]
```

**Purpose:** Interactive analysis notebooks and research experiments.

---

### 🔬 **research/** & **research_paper/**
```
research/                              # Research datasets & experiments
research_paper/                        # Paper drafts & LaTeX sources
```

**Purpose:** Academic research materials and paper development.

---

### 📦 **Other Directories**

- **`tests/`** - Unit tests for core modules
- **`scripts/`** - Miscellaneous helper scripts
- **`scripts_archive/`** - Archived old scripts
- **`modules/`** - Shared Python modules
- **`logos/`** - Brand assets and logos
- **`exports/`** - Data exports
- **`Poster_Presentation/`** - Competition poster materials
- **`.venv/`** - Python virtual environment
- **`.vscode/`** - VS Code configuration
- **`.git/`** - Git repository data

---

## 🎯 Where to Find Things

### 🔍 Need to...?

| **Task** | **Location** |
|----------|-------------|
| **Start the system** | Root: `🚀_DOUBLE_CLICK_TO_START.bat` |
| **Read documentation** | `project_documentation/guides/START_HERE.txt` |
| **Check requirements** | `project_documentation/summaries/FRONTEND_REQUIREMENTS_MAP.txt` |
| **View test results** | `archived_outputs/test_results/` |
| **See charts/graphs** | `archived_outputs/charts/` & `archived_outputs/backtest_images/` |
| **Read research paper** | `project_documentation/research_papers/` |
| **Update backend API** | `web/backend/routers/ipo_ultimate_fixed.py` ⭐ |
| **Update frontend** | `web/frontend/src/pages/IPOMultiAgent.js` ⭐ |
| **Run tests** | `test_scripts/TEST_ULTIMATE_SYSTEM.py` |
| **Configure environment** | Root: `.env` |
| **Check core logic** | `core/` directory |

---

## ⭐ Key Files (Most Important)

### Backend
1. **`web/backend/routers/ipo_ultimate_fixed.py`** - Main IPO analysis system (ALL 10 requirements)
2. **`web/backend/main.py`** - FastAPI application
3. **`core/agent_control_tower.py`** - Real-time agent monitoring
4. **`core/a2a_protocol.py`** - Agent-to-agent communication

### Frontend
1. **`web/frontend/src/pages/IPOMultiAgent.js`** - Main IPO interface
2. **`web/frontend/src/api.js`** - API client configuration
3. **`web/frontend/src/pages/AgentControlTower.js`** - Monitoring dashboard

### Documentation
1. **`project_documentation/guides/START_HERE.txt`** - Quick start guide
2. **`project_documentation/summaries/🎯_ULTIMATE_SYSTEM_READY.txt`** - System status
3. **`FILE_STRUCTURE.md`** - This file!
4. **`README.md`** - Main project README

### Testing
1. **`test_scripts/TEST_ULTIMATE_SYSTEM.py`** - Complete system test
2. **`test_scripts/TEST_FIXED_SYSTEM.py`** - Fixed system validation

---

## 🚀 Running the System

### Option 1: Double-Click Launcher (Easiest)
```
🚀_DOUBLE_CLICK_TO_START.bat
```

### Option 2: Manual Start

**Backend:**
```bash
cd web/backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd web/frontend
npm start
```

### Option 3: Alternative Launcher
```
RUN_COMPLETE_PROJECT.bat
```

---

## 📞 Support

- **Documentation:** `project_documentation/guides/`
- **Issues:** Check `project_documentation/summaries/` for known issues
- **Research:** `project_documentation/research_papers/`

---

## 🎉 System Status

✅ **Backend:** Operational (Port 8000)  
✅ **Frontend:** React + Node.js  
✅ **All 10 Requirements:** Implemented & Tested  
✅ **File Structure:** Organized  
✅ **Documentation:** Complete  

**Last Updated:** October 26, 2026  
**Version:** 2.0 (Organized & Production-Ready)
