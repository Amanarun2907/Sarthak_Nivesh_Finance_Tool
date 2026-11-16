"""
🚀 QUICK SETUP GUIDE
===================
Follow these steps to get your phenomenal multi-agent system running!

STEP 1: INSTALL DEPENDENCIES
-----------------------------
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║        🚀 SARTHAK NIVESH - SETUP GUIDE                                    ║
║        Multi-Agent Investment Intelligence Platform                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 STEP 1: Install Dependencies
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run the following command to install all required packages:

    pip install -r requirements.txt

This will install:
✅ CrewAI (v0.94.0) - Multi-agent orchestration
✅ Anthropic SDK (v0.40.0) - Claude AI integration
✅ Pydantic (v2.10.3) - Data validation & structured outputs
✅ LangFuse (v2.56.1) - Observability & tracing
✅ Guardrails AI (v0.5.14) - Security & validation
✅ Additional dependencies for performance monitoring


🔑 STEP 2: Set Up API Keys
━━━━━━━━━━━━━━━━━━━━━━━━━━

You need API keys for the AI models:

1. ANTHROPIC API KEY (Required for ADK agents):
   
   Windows (PowerShell):
   $env:ANTHROPIC_API_KEY="your_anthropic_api_key_here"
   
   Linux/Mac:
   export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
   
   Get your key from: https://console.anthropic.com/

2. OPENAI API KEY (Required for CrewAI agents):
   
   Windows (PowerShell):
   $env:OPENAI_API_KEY="your_openai_api_key_here"
   
   Linux/Mac:
   export OPENAI_API_KEY="your_openai_api_key_here"
   
   Get your key from: https://platform.openai.com/

3. LANGFUSE (Optional - for cloud observability):
   
   Windows (PowerShell):
   $env:LANGFUSE_PUBLIC_KEY="your_public_key"
   $env:LANGFUSE_SECRET_KEY="your_secret_key"
   
   Linux/Mac:
   export LANGFUSE_PUBLIC_KEY="your_public_key"
   export LANGFUSE_SECRET_KEY="your_secret_key"
   
   Get keys from: https://cloud.langfuse.com/
   Note: System works without LangFuse in local-only mode


📁 STEP 3: Verify File Structure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ensure you have these core files:

core/
├── main_system.py              ← Main execution file
├── multi_agent_orchestrator.py ← Central orchestrator
├── crewai_agents.py            ← CrewAI agents (Price, Sentiment)
├── adk_agents.py               ← ADK agents (Risk, IPO)
├── a2a_protocol.py             ← Agent-to-agent communication
├── observability_system.py     ← LangFuse tracing
├── guardrails_security.py      ← Security & validation
├── explainability_engine.py    ← Transparency system
├── agent_control_tower.py      ← Real-time monitoring
├── performance_evaluator.py    ← Cost & time tracking
├── mcp_tools.py                ← External tools integration
├── test_complete_system.py     ← Verification tests
└── requirements.txt            ← Dependencies


🧪 STEP 4: Run System Tests
━━━━━━━━━━━━━━━━━━━━━━━━━

Before using the system, verify everything works:

    python test_complete_system.py

This will test all 10 requirements:
✅ Context sharing & state updates
✅ MCP tool integration (2+ tools)
✅ Pydantic structured outputs
✅ Task monitoring with callbacks
✅ A2A protocol communication
✅ CrewAI + ADK frameworks
✅ Guardrails security
✅ LangFuse observability
✅ Performance evaluation
✅ Complete system integration


🎯 STEP 5: Run Your First Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Interactive Mode (Recommended for first use):

    python main_system.py

Follow the prompts to analyze any stock!


Batch Mode (Multiple stocks at once):

    python main_system.py batch stocks.json

Create stocks.json:
[
  {"symbol": "RELIANCE.NS", "company_name": "Reliance Industries"},
  {"symbol": "TCS.NS", "company_name": "Tata Consultancy Services"},
  {"symbol": "INFY.NS", "company_name": "Infosys Limited"}
]


📊 UNDERSTANDING THE OUTPUT
━━━━━━━━━━━━━━━━━━━━━━━━━

The system provides:

1. RECOMMENDATION: BUY/SELL/HOLD/AVOID/STRONG BUY
2. CONFIDENCE SCORE: 0-100 overall confidence
3. AGENT SCORES:
   - Price Movement (CrewAI): Technical analysis
   - Sentiment Analysis (CrewAI): News & social media
   - Risk Assessment (ADK): Volatility & downside
   - IPO Intelligence (ADK): IPO-specific metrics
4. KEY STRENGTHS: Top positive factors
5. KEY RISKS: Main concerns
6. PERFORMANCE METRICS: Duration, cost, tokens used
7. EXPLAINABILITY: Complete audit trail
8. JSON EXPORT: Structured output for integration


🔍 EXPLAINABILITY → TRANSPARENCY → TRUST → ADOPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every decision includes:
✅ Agent reasoning & confidence levels
✅ Weighted score contributions
✅ Complete execution trace (via LangFuse)
✅ Security validation results
✅ Performance metrics & cost breakdown
✅ Audit trail with trace IDs

This ensures complete transparency and builds trust!


💡 TIPS FOR BEST RESULTS
━━━━━━━━━━━━━━━━━━━━━━

1. Use valid Indian stock symbols (e.g., RELIANCE.NS, TCS.NS)
2. Provide accurate company names for better news analysis
3. Choose "comprehensive" for full multi-agent analysis
4. Check LangFuse dashboard for detailed execution traces
5. Review performance metrics to optimize costs
6. Export JSON for integration with other systems


🆘 TROUBLESHOOTING
━━━━━━━━━━━━━━━━

Problem: "ANTHROPIC_API_KEY not found"
Solution: Set the environment variable (see Step 2)

Problem: "Module not found" errors
Solution: Run: pip install -r requirements.txt

Problem: Agent execution fails
Solution: 
  1. Verify API keys are correct
  2. Check internet connection
  3. Review error logs in console
  4. Run tests: python test_complete_system.py

Problem: High costs
Solution: 
  1. Use "quick" analysis type
  2. Review performance report suggestions
  3. Consider using cheaper models in config


📧 SUPPORT
━━━━━━━━━

For issues or questions:
1. Check error messages in console
2. Review test results: core/test_results.json
3. Check LangFuse traces for detailed logs
4. Review performance reports for optimization


╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║        ✅ SETUP COMPLETE! Ready to analyze stocks!                        ║
║                                                                            ║
║        Run: python main_system.py                                         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

# Quick setup verification
print("\n🔍 Quick Setup Verification:\n")

import sys
import os

# Check Python version
python_version = sys.version_info
if python_version >= (3, 8):
    print(f"✅ Python version: {python_version.major}.{python_version.minor}")
else:
    print(f"❌ Python version: {python_version.major}.{python_version.minor} (Need 3.8+)")

# Check if requirements.txt exists
if os.path.exists("requirements.txt"):
    print("✅ requirements.txt found")
else:
    print("❌ requirements.txt not found")

# Check for API keys
if os.getenv("ANTHROPIC_API_KEY"):
    print("✅ ANTHROPIC_API_KEY is set")
else:
    print("⚠️  ANTHROPIC_API_KEY not set (required for ADK agents)")

if os.getenv("OPENAI_API_KEY"):
    print("✅ OPENAI_API_KEY is set")
else:
    print("⚠️  OPENAI_API_KEY not set (required for CrewAI agents)")

if os.getenv("LANGFUSE_PUBLIC_KEY"):
    print("✅ LANGFUSE keys are set (cloud observability enabled)")
else:
    print("ℹ️  LANGFUSE keys not set (will use local-only mode)")

# Check core files
core_files = [
    "main_system.py",
    "multi_agent_orchestrator.py",
    "crewai_agents.py",
    "adk_agents.py",
    "a2a_protocol.py",
    "observability_system.py",
    "guardrails_security.py",
    "performance_evaluator.py",
    "test_complete_system.py"
]

missing_files = []
for file in core_files:
    if not os.path.exists(file):
        missing_files.append(file)

if missing_files:
    print(f"\n❌ Missing files: {', '.join(missing_files)}")
else:
    print("\n✅ All core files present")

print("\n" + "="*80)
print("🚀 Ready to start! Run: python main_system.py")
print("="*80 + "\n")
