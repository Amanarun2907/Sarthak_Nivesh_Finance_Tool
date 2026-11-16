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
_AGENT_DIR = _ROOT / "src" / "sections" / "06_agentic_ai_hub"
_CORE_DIR = _ROOT / "src" / "core"
for _p in [str(_AGENT_DIR), str(_CORE_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

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
        "model":   "Groq Llama 3.3 70B",
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

    # ── Import framework (lazy with reload to prevent stale module cache) ──────────────────
    try:
        import importlib
        import ipo_multi_agent_framework
        importlib.reload(ipo_multi_agent_framework)
        from ipo_multi_agent_framework import run_ipo_multi_agent_analysis, OrchestratorResult, MultiAgentOrchestrator
    except Exception as e:
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
        "markdown_report":   getattr(result, "markdown_report", ""),
        "timestamp":         result.timestamp,

        # ── Dynamic Exit Plan (multi-tier ladder) ─────────────────────────────
        "dynamic_exit_plan": (
            result.dynamic_exit_plan.dict() if result.dynamic_exit_plan else None
        ),

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


# ── Standalone Exit Strategy endpoint ────────────────────────────────────────
@router.post("/exit_strategy")
def get_exit_strategy(data: dict = Body(...)):
    """
    Generate a dynamic multi-tier exit strategy for a given IPO/stock position.
    Can be called independently (without running all 6 agents) when user asks
    specifically about exit strategy for a stock they already hold.

    Request body:
    {
        "ipo_name":       "Bajaj Housing Finance",
        "symbol":         "BAJAJHFL.NS",
        "entry_price":    70.0,       // price at which investor bought
        "current_price":  150.0,      // current market price (0 = auto-fetch)
        "holding_qty":    100,        // optional: number of shares held
        "risk_profile":   "moderate"  // "conservative"|"moderate"|"aggressive"
    }
    """
    import time

    ipo_name     = str(data.get("ipo_name", "IPO")).strip()
    symbol       = str(data.get("symbol",   "NSE")).strip()
    entry_price  = float(data.get("entry_price",   0.0))
    current_price= float(data.get("current_price", 0.0))
    holding_qty  = int(data.get("holding_qty",  0))
    risk_profile = str(data.get("risk_profile", "moderate")).lower()

    if entry_price <= 0:
        raise HTTPException(status_code=422, detail="entry_price must be > 0")

    try:
        from ipo_multi_agent_framework import (
            _build_dynamic_exit_plan, AgentResult, get_adk_client
        )
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Framework import failed: {e}")

    # Fetch current price if not provided
    if current_price <= 0:
        try:
            import yfinance as yf
            sym = symbol if (".NS" in symbol or ".BO" in symbol) else f"{symbol}.NS"
            t = yf.Ticker(sym)
            lp = t.fast_info.last_price
            if lp and lp > 0:
                current_price = float(lp)
            else:
                current_price = entry_price
        except Exception:
            current_price = entry_price

    # Adjust risk multiplier
    risk_mult = {"conservative": 0.75, "moderate": 1.0, "aggressive": 1.3}.get(risk_profile, 1.0)
    pnl_pct  = round((current_price - entry_price) / entry_price * 100, 2) if entry_price > 0 else 0.0
    pnl_abs  = round((current_price - entry_price) * holding_qty, 2) if holding_qty > 0 else 0.0

    # Build synthetic agent results for the exit plan
    score = 60.0 + min(pnl_pct * 0.5, 20.0)  # score based on current P&L
    score = max(20.0, min(score, 90.0))
    final_decision = "HOLD" if pnl_pct >= 0 else ("EXIT" if pnl_pct < -8 else "HOLD")
    risk_level = "HIGH" if pnl_pct < -10 else ("ELEVATED" if pnl_pct < -5 else "MODERATE")

    mock_risk_result = AgentResult(
        agent_name="Risk Agent",
        score=score,
        signal=final_decision,
        confidence=78.0,
        summary=f"Position P&L: {pnl_pct:+.2f}%",
        details={
            "var_95_pct": max(5.0, 8.5 * risk_mult),
            "max_drawdown_pct": max(10.0, 18.0 * risk_mult),
        }
    )
    mock_price_result = AgentResult(
        agent_name="Price Movement Agent",
        score=score,
        signal=final_decision,
        confidence=72.0,
        summary=f"Current ₹{current_price:.2f}, Entry ₹{entry_price:.2f}",
        details={
            "support_levels": [round(current_price * 0.92, 2), round(current_price * 0.87, 2)],
            "resistance_levels": [round(current_price * 1.08, 2), round(current_price * 1.15, 2)],
        }
    )

    agent_results = {
        "Risk Agent": mock_risk_result,
        "Price Movement Agent": mock_price_result,
        "Macroeconomic Agent": AgentResult(agent_name="Macroeconomic Agent", score=65.0, signal="HOLD", confidence=70.0, summary="Macro baseline", details={"macro_regime": "Cautious"}),
        "Sentiment Agent": AgentResult(agent_name="Sentiment Agent", score=62.0, signal="HOLD", confidence=68.0, summary="Neutral sentiment", details={"sentiment_mood": "Neutral"}),
        "IPO Intelligence Agent": AgentResult(agent_name="IPO Intelligence Agent", score=score, signal=final_decision, confidence=75.0, summary=f"Entry ₹{entry_price:.2f}", details={"fair_value_band": f"₹{entry_price*0.90:.0f}–₹{entry_price*1.15:.0f}"}),
    }

    adk = get_adk_client()
    try:
        dyn_exit = _build_dynamic_exit_plan(
            ipo_name=ipo_name, symbol=symbol,
            entry_price=current_price if current_price > entry_price else entry_price,
            overall_score=score,
            final_decision=final_decision,
            risk_level=risk_level,
            agent_results=agent_results,
            adk_client=adk,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exit plan generation failed: {str(e)}")

    return _safe({
        "ipo_name":       ipo_name,
        "symbol":         symbol,
        "entry_price":    entry_price,
        "current_price":  current_price,
        "pnl_pct":        pnl_pct,
        "pnl_abs":        pnl_abs,
        "holding_qty":    holding_qty,
        "risk_profile":   risk_profile,
        "current_decision": final_decision,
        "risk_level":     risk_level,
        "dynamic_exit_plan": dyn_exit.dict(),
        "timestamp": __import__("datetime").datetime.now().isoformat(),
    })
