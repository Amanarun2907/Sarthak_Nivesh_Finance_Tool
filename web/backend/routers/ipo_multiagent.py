"""
IPO Multi-Agent Framework — FastAPI Router
==========================================
Exposes the 6-agent hierarchical system via REST API
consumed by the React web interface.

Endpoints:
  POST /api/ipo_multiagent/analyze   — Run all 6 agents for a given IPO
  GET  /api/ipo_multiagent/status    — Health check
"""
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import JSONResponse
import sys, os, math
from pathlib import Path

# Ensure sections path is available
_ROOT = Path(__file__).resolve().parents[3]
_AGENT_DIR = _ROOT / "sections" / "06_agentic_ai_hub"
if str(_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENT_DIR))

router = APIRouter()


# ── Safe serialiser — replaces NaN/Inf so JSON doesn't break ─────────────────
def _safe(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    if isinstance(obj, dict):
        return {k: _safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_safe(v) for v in obj]
    return obj


# ── Health ────────────────────────────────────────────────────────────────────
@router.get("/status")
def status():
    return {
        "status":  "online",
        "service": "IPO Multi-Agent Framework",
        "agents":  6,
        "model":   "llama-3.3-70b-versatile",
        "paper":   "Hierarchical Multi-Agentic AI for IPO Investment & Exit Strategy",
    }


# ── Main analysis endpoint ────────────────────────────────────────────────────
@router.get("/analyze")
def analyze_ipo_get(
    ipo_name: str = "",
    symbol: str = "",
    issue_price: float = 0.0,
    listing_price: float = 0.0
):
    """GET endpoint for IPO analysis with query parameters."""
    if not ipo_name or not symbol:
        raise HTTPException(status_code=422, detail="ipo_name and symbol are required")
    
    return analyze_ipo({
        "ipo_name": ipo_name,
        "symbol": symbol,
        "issue_price": issue_price,
        "listing_price": listing_price,
        "current_price": 0.0,
        "sub_total": 0.0,
        "sub_qib": 0.0,
        "sub_retail": 0.0,
        "listing_date_str": ""
    })

@router.post("/analyze")
def analyze_ipo(data: dict = Body(...)):
    """
    Run the 6-agent framework and return a structured OrchestratorResult.

    Request body (JSON):
    {
        "ipo_name":          "Hyundai India",
        "symbol":            "HYUNDAI.NS",
        "issue_price":       1960.0,
        "listing_price":     1934.0,
        "current_price":     0.0,        // 0 = auto-fetch
        "sub_total":         17.0,
        "sub_qib":           36.5,
        "sub_retail":        6.8,
        "listing_date_str":  "2024-10-22" // or ""
    }
    """
    # ── Validate inputs ──────────────────────────────────────────────────────
    required = ["ipo_name", "symbol", "issue_price", "listing_price"]
    for field in required:
        if field not in data or data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required field: '{field}'"
            )

    ipo_name      = str(data["ipo_name"]).strip()
    symbol        = str(data["symbol"]).strip()
    issue_price   = float(data["issue_price"])
    listing_price = float(data["listing_price"])
    current_price = float(data.get("current_price", 0.0))
    sub_total     = float(data.get("sub_total",     0.0))
    sub_qib       = float(data.get("sub_qib",       0.0))
    sub_retail    = float(data.get("sub_retail",    0.0))
    listing_date  = str(data.get("listing_date_str", "")).strip()

    if issue_price < 0:
        raise HTTPException(status_code=422, detail="issue_price must be >= 0")

    # ── Import framework (lazy — only when route is called) ──────────────────
    try:
        from ipo_multi_agent_framework import run_ipo_multi_agent_analysis, OrchestratorResult
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import IPO Multi-Agent Framework: {str(e)}"
        )

    # ── Progress tracking ─────────────────────────────────────────────────────
    progress_log = []
    def _cb(step: int, msg: str):
        progress_log.append({"step": step, "message": msg})

    # ── Run analysis ──────────────────────────────────────────────────────────
    try:
        result: OrchestratorResult = run_ipo_multi_agent_analysis(
            ipo_name         = ipo_name,
            symbol           = symbol,
            issue_price      = issue_price,
            listing_price    = listing_price,
            current_price    = current_price,
            sub_total        = sub_total,
            sub_qib          = sub_qib,
            sub_retail       = sub_retail,
            listing_date_str = listing_date,
            progress_callback= _cb,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )

    # ── Serialise dataclass → dict ────────────────────────────────────────────
    payload = _safe({
        # ── Orchestrator output ───────────────────────────────────────────────
        "ipo_name":          result.ipo_name,
        "symbol":            result.symbol,
        "final_decision":    result.final_decision,
        "overall_score":     result.overall_score,
        "confidence":        result.confidence,
        "entry_strategy":    result.entry_strategy,
        "exit_strategy":     result.exit_strategy,
        "target_price":      result.target_price,
        "stop_loss":         result.stop_loss,
        "risk_level":        result.risk_level,
        "holding_period":    result.holding_period,
        "investment_thesis": result.investment_thesis,
        "key_risks":         result.key_risks,
        "key_catalysts":     result.key_catalysts,
        "monitoring_triggers": result.monitoring_triggers,
        "timestamp":         result.timestamp,

        # ── Per-agent scores ──────────────────────────────────────────────────
        "agent_scores": result.agent_scores,

        # ── Decision colour for UI ────────────────────────────────────────────
        "decision_color": (
            "#00ff88" if result.final_decision in ("INVEST",)
            else "#17a2b8" if result.final_decision == "PARTIAL_INVEST"
            else "#ffc107" if result.final_decision == "HOLD"
            else "#ff4757"
        ),

        # ── Progress log ──────────────────────────────────────────────────────
        "progress_log": progress_log,

        # ── Paper metadata ────────────────────────────────────────────────────
        "framework": {
            "name":    "Hierarchical Multi-Agentic AI for IPO Investment & Exit Strategy",
            "agents":  6,
            "weights": {
                "Price Movement Agent":   "20%",
                "Macroeconomic Agent":    "15%",
                "Sentiment Agent":        "20%",
                "Risk Agent":             "20%",
                "IPO Intelligence Agent": "25%",
            },
            "model":    "Groq Llama 3.3 70B",
            "keywords": ["Agentic AI", "Investment", "IPO", "Prediction"],
        },
    })

    return JSONResponse(content=payload)
