"""
सार्थक निवेश — FastAPI Backend
Author: Aman Jain (B.Tech 2023-27)
All data is 100% real-time. Zero dummy data.
"""

import sys
import os
from pathlib import Path

# ── Add project sections and core to path ────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[2]
for _sub in [
    _ROOT / "sections" / "02_stock_intelligence",
    _ROOT / "sections" / "03_mutual_fund_sip",
    _ROOT / "sections" / "04_ipo_intelligence",
    _ROOT / "sections" / "05_smart_money_tracker",
    _ROOT / "sections" / "06_agentic_ai_hub",
    _ROOT / "sections" / "07_portfolio_risk",
    _ROOT / "sections" / "08_news_sentiment",
    _ROOT / "sections" / "09_ai_assistant",
    _ROOT / "sections" / "10_advanced_analytics",
    _ROOT / "core",
]:
    p = str(_sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")

from routers import (
    dashboard, stocks, mutual_funds, sip_goals,
    ipo, smart_money, portfolio, news,
    ai_assistant, analytics, agentic, ipo_multiagent
)

app = FastAPI(
    title="सार्थक निवेश API",
    description="Real-time Indian Investment Intelligence Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router,    prefix="/api/dashboard",    tags=["Dashboard"])
app.include_router(stocks.router,       prefix="/api/stocks",       tags=["Stocks"])
app.include_router(mutual_funds.router, prefix="/api/mf",           tags=["Mutual Funds"])
app.include_router(sip_goals.router,    prefix="/api/sip",          tags=["SIP Goals"])
app.include_router(ipo.router,          prefix="/api/ipo",          tags=["IPO"])
app.include_router(smart_money.router,  prefix="/api/smartmoney",   tags=["Smart Money"])
app.include_router(portfolio.router,    prefix="/api/portfolio",    tags=["Portfolio"])
app.include_router(news.router,         prefix="/api/news",         tags=["News"])
app.include_router(ai_assistant.router, prefix="/api/ai",           tags=["AI"])
app.include_router(analytics.router,    prefix="/api/analytics",    tags=["Analytics"])
app.include_router(agentic.router,         prefix="/api/agentic",         tags=["Agentic AI"])
app.include_router(ipo_multiagent.router,  prefix="/api/ipo_multiagent",  tags=["IPO Multi-Agent"])

@app.get("/")
def root():
    return {"status": "ok", "message": "सार्थक निवेश API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
