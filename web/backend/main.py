"""
सार्थक निवेश — FastAPI Backend
Author: Aman Jain (B.Tech 2023-27)
All data is 100% real-time. Zero dummy data.
"""

import sys
import os
import io

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from pathlib import Path

# ── Add project sections and core to path ────────────────────────────────────
_ROOT = Path(__file__).resolve().parents[2]
for _sub in [
    _ROOT / "src" / "sections" / "02_stock_intelligence",
    _ROOT / "src" / "sections" / "03_mutual_fund_sip",
    _ROOT / "src" / "sections" / "04_ipo_intelligence",
    _ROOT / "src" / "sections" / "05_smart_money_tracker",
    _ROOT / "src" / "sections" / "06_agentic_ai_hub",
    _ROOT / "src" / "sections" / "07_portfolio_risk",
    _ROOT / "src" / "sections" / "08_news_sentiment",
    _ROOT / "src" / "sections" / "09_ai_assistant",
    _ROOT / "src" / "sections" / "10_advanced_analytics",
    _ROOT / "src" / "core",
    _ROOT / "src" / "modules",
    _ROOT / "web" / "backend",
]:
    p = str(_sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")
import agentic_runtime

import importlib

_ROUTER_SPECS = [
    ("dashboard",                "/api/dashboard",               "Dashboard"),
    ("stocks",                   "/api/stocks",                  "Stocks"),
    ("mutual_funds",             "/api/mf",                      "Mutual Funds"),
    ("sip_goals",                "/api/sip",                     "SIP Goals"),
    ("ipo",                      "/api/ipo",                     "IPO"),
    ("smart_money",              "/api/smartmoney",              "Smart Money"),
    ("portfolio",                "/api/portfolio",               "Portfolio"),
    ("news",                     "/api/news",                    "News"),
    ("ai_assistant",             "/api/ai",                      "AI"),
    ("analytics",                "/api/analytics",               "Analytics"),
    ("agentic",                  "/api/agentic",                 "Agentic AI"),
    ("ipo_multiagent",           "/api/ipo_multiagent",          "IPO Multi-Agent"),
]

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

_FAILED_ROUTERS = []
for _mod_name, _prefix, _tag in _ROUTER_SPECS:
    try:
        _mod = importlib.import_module(f"routers.{_mod_name}")
        app.include_router(getattr(_mod, "router"), prefix=_prefix, tags=[_tag])
    except Exception as _e:
        _FAILED_ROUTERS.append({"router": _mod_name, "error": f"{type(_e).__name__}: {_e}"})
        print(f"⚠️ Router '{_mod_name}' failed to load and was skipped: {_e}")

app.state.failed_routers = _FAILED_ROUTERS

@app.get("/failed_routers")
def failed_routers():
    return {"failed_routers": _FAILED_ROUTERS}

@app.get("/")
def root():
    return {"status": "ok", "message": "सार्थक निवेश API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
