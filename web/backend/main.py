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

# ── ADKClient hard patch — applied immediately after agentic_runtime loads ────
# Verified available Groq chat models for this account (checked 2025-11-16):
#   openai/gpt-oss-120b, openai/gpt-oss-20b, qwen/qwen3.8-27b, allam-2-7b
# Every other model (llama-*, claude-*, gpt-4*, mixtral-*) is NOT available and
# returns a 404 model_not_found error. This patch makes ADKClient.create() ONLY
# try the three verified models, regardless of what `model` argument is passed.
try:
    import requests as _req_mod
    _GROQ_CANDIDATES = [
        "openai/gpt-oss-120b",
        "qwen/qwen3.8-27b",
        "openai/gpt-oss-20b",
    ]

    def _patched_adk_create(self, model: str, max_tokens: int, system: str, messages: list):
        """
        Patched ADKClient.create() that ignores the `model` argument and only
        tries verified available Groq models. The `model` arg is intentionally
        ignored because callers may pass claude-3-sonnet or other unavailable names.
        """
        # Try native Anthropic if available
        if getattr(self, "use_native", False):
            try:
                return self.native_client.messages.create(
                    model=model, max_tokens=max_tokens,
                    system=system, messages=messages
                )
            except Exception as e:
                print(f"⚠️ Native Anthropic call failed ({e}), using Groq bridge...")

        groq_key = os.environ.get("GROQ_API_KEY", getattr(self, "groq_key", ""))
        if not groq_key:
            raise RuntimeError("ADK bridge: GROQ_API_KEY not set")

        headers = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json",
        }
        groq_messages = [{"role": "system", "content": system}]
        for m in messages:
            groq_messages.append({"role": m["role"], "content": m["content"]})

        last_err = ""
        for candidate in _GROQ_CANDIDATES:
            try:
                payload = {
                    "model": candidate,
                    "messages": groq_messages,
                    "temperature": 0.2,
                    "max_tokens": max_tokens,
                }
                r = _req_mod.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers, json=payload, timeout=60
                )
                if r.status_code == 200:
                    res = r.json()
                    text = res["choices"][0]["message"]["content"]
                    usage = res.get("usage", {})
                    in_tok = usage.get("prompt_tokens", 400)
                    out_tok = usage.get("completion_tokens", 800)
                    # Return an ADKResponse-compatible object
                    from agentic_runtime import ADKResponse
                    return ADKResponse(text, in_tok, out_tok)
                last_err = f"{r.status_code}: {r.text[:200]}"
            except Exception as exc:
                last_err = str(exc)
                continue

        raise RuntimeError(
            f"ADK bridge: all candidate models failed. Last error: {last_err}"
        )

    # Monkey-patch the ADKClient class so ALL instances (including ones already
    # created in routers) use this method.
    agentic_runtime.ADKClient.create = _patched_adk_create
    # Also patch the messages attribute (ADKClient sets self.messages = self)
    # so adk.messages.create(...) also hits the patched method.
    print("✅ ADKClient.create() patched: only verified Groq models will be used")
except Exception as _patch_err:
    print(f"⚠️ ADKClient patch failed (non-fatal): {_patch_err}")

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
