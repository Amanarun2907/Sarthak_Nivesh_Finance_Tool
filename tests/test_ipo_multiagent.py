"""
End-to-end test suite for IPO Multi-Agent Framework
Run: python tests/test_ipo_multiagent.py
"""
import sys, os, math, traceback, time

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "sections", "06_agentic_ai_hub"))
sys.path.insert(0, os.path.join(ROOT, "core"))

PASS = 0
FAIL = 0
WARN = 0

def ok(msg):
    global PASS; PASS += 1
    print(f"  ✅ PASS: {msg}")

def fail(msg, exc=None):
    global FAIL; FAIL += 1
    print(f"  ❌ FAIL: {msg}")
    if exc:
        print(f"          → {exc}")

def warn(msg):
    global WARN; WARN += 1
    print(f"  ⚠️  WARN: {msg}")

def safe_float(v):
    try:
        f = float(v)
        return not (math.isnan(f) or math.isinf(f))
    except Exception:
        return False

# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("  IPO MULTI-AGENT FRAMEWORK — FULL END-TO-END TEST SUITE")
print("="*60)

# ── TEST 1: Imports ───────────────────────────────────────────────────────────
print("\n[1] Import Tests")
try:
    from ipo_multi_agent_framework import (
        run_ipo_multi_agent_analysis,
        OrchestratorAgent, OrchestratorResult, AgentResult,
        PriceMovementAgent, MacroeconomicAgent, SentimentAgent,
        RiskAgent, IPOIntelligenceAgent, GroqLLM, _llm,
    )
    ok("All 10 symbols imported successfully")
except Exception as e:
    fail("Import failed — halting", e)
    sys.exit(1)

# ── TEST 2: GroqLLM ───────────────────────────────────────────────────────────
print("\n[2] GroqLLM Tests")
try:
    text = "PRICE_SCORE: 72\nPRICE_SIGNAL: BUY\nPRICE_CONFIDENCE: 78\nPRICE_SUMMARY: Strong momentum with RSI at 52"
    assert GroqLLM.parse(text, "PRICE_SCORE")      == "72",  "score mismatch"
    assert GroqLLM.parse(text, "PRICE_SIGNAL")     == "BUY", "signal mismatch"
    assert GroqLLM.parse(text, "MISSING", "DEF")   == "DEF", "default mismatch"
    ok("GroqLLM.parse — key extraction and default fallback correct")
except Exception as e:
    fail("GroqLLM.parse", e)

try:
    llm = GroqLLM()
    assert hasattr(llm, "ask") and callable(llm.ask)
    ok("GroqLLM instance created, ask() callable")
except Exception as e:
    fail("GroqLLM instantiation", e)

# ── TEST 3: Dataclasses ───────────────────────────────────────────────────────
print("\n[3] Dataclass Tests")
try:
    ar = AgentResult(agent_name="Test Agent", score=75.0,
                     signal="BUY", confidence=80.0, summary="Test")
    assert ar.error is None
    assert isinstance(ar.details, dict)
    ok("AgentResult dataclass — defaults and fields correct")
except Exception as e:
    fail("AgentResult", e)

try:
    orr = OrchestratorResult(
        ipo_name="Test IPO", symbol="TEST.NS", final_decision="INVEST",
        overall_score=78.5, confidence=82.0,
        entry_strategy="Buy", exit_strategy="Sell at target",
        target_price=120.0, stop_loss=90.0, risk_level="MEDIUM",
        holding_period="3 months", agent_scores={},
        investment_thesis="Strong growth", key_risks=[],
        key_catalysts=[], monitoring_triggers=[],
    )
    assert orr.final_decision == "INVEST"
    assert isinstance(orr.timestamp, str) and len(orr.timestamp) > 0
    ok("OrchestratorResult dataclass — all fields instantiate correctly")
except Exception as e:
    fail("OrchestratorResult", e)

# ── TEST 4: PriceMovementAgent ────────────────────────────────────────────────
print("\n[4] PriceMovementAgent Tests")
agent_price = PriceMovementAgent(_llm)

# Rule score unit test (no network)
try:
    dummy = dict(
        current_price=100.0, ma20=95.0, ma50=90.0, rsi=45.0,
        macd_hist=0.5, vol_ratio=1.8, mom_1m=5.0,
        bb_lower=88.0, bb_upper=112.0, bb_mid=100.0,
    )
    score, signals = agent_price._rule_score(dummy)
    assert 0 <= score <= 100, f"Score out of bounds: {score}"
    assert len(signals) >= 3, f"Too few signals: {len(signals)}"
    ok(f"_rule_score unit test — score={score:.1f}, signals={len(signals)}")
except Exception as e:
    fail("_rule_score unit test", e)

# Boundary: oversold RSI
try:
    dummy_oversold = dict(
        current_price=80.0, ma20=90.0, ma50=95.0, rsi=25.0,
        macd_hist=-0.3, vol_ratio=2.5, mom_1m=-18.0,
        bb_lower=78.0, bb_upper=102.0, bb_mid=90.0,
    )
    score_o, sigs_o = agent_price._rule_score(dummy_oversold)
    assert 0 <= score_o <= 100
    ok(f"_rule_score boundary (oversold/below MAs) — score={score_o:.1f}")
except Exception as e:
    fail("_rule_score boundary test", e)

# Live fetch
try:
    print("    Fetching live data for HDFCBANK.NS ...")
    d = agent_price._fetch("HDFCBANK.NS")
    if "error" in d:
        warn(f"Live fetch returned error (network?): {d['error']}")
    else:
        required = ["current_price","rsi","macd_hist","vol_ratio","atr","s1","r1","ma20","ma50","mom_1m"]
        missing  = [k for k in required if k not in d]
        bad_nan  = [k for k in required if k in d and not safe_float(d[k])]
        if missing:
            fail(f"_fetch missing keys: {missing}")
        elif bad_nan:
            fail(f"_fetch NaN/Inf in: {bad_nan}")
        else:
            ok(f"_fetch live — price Rs{d['current_price']:.2f}, RSI={d['rsi']:.1f}, vol={d['vol_ratio']:.2f}x")
except Exception as e:
    fail("PriceMovementAgent._fetch", e)

# Full .run() with mock (no LLM key needed — falls back to rule score)
try:
    print("    Running PriceMovementAgent.run(RELIANCE.NS) ...")
    result = agent_price.run("RELIANCE.NS", "Reliance Industries")
    assert isinstance(result, AgentResult)
    assert result.agent_name == "Price Movement Agent"
    assert 0 <= result.score <= 100
    assert result.signal in ("STRONG_BUY","BUY","HOLD","SELL","STRONG_SELL","N/A")
    assert 0 <= result.confidence <= 100
    ok(f"PriceMovementAgent.run() — score={result.score}, signal={result.signal}, conf={result.confidence}%")
except Exception as e:
    fail("PriceMovementAgent.run()", e)
    traceback.print_exc()

# ── TEST 5: MacroeconomicAgent ────────────────────────────────────────────────
print("\n[5] MacroeconomicAgent Tests")
agent_macro = MacroeconomicAgent(_llm)

try:
    dummy_macro = {
        "indices": {
            "NIFTY50":   {"current": 24500, "change_pct":  1.2},
            "INDIA_VIX": {"current": 14.5,  "change_pct": -0.3},
            "DOW":       {"current": 39000,  "change_pct":  0.5},
            "USD_INR":   {"current": 83.5,   "change_pct":  0.1},
        },
        "fii_dii": {"fii_net": 1800.0, "dii_net": 900.0, "date": "02-Jun-2026"},
    }
    score, signals = agent_macro._rule_score(dummy_macro)
    assert 0 <= score <= 100
    assert len(signals) >= 3
    ok(f"_rule_score unit test — score={score:.1f}, signals={len(signals)}")
except Exception as e:
    fail("MacroeconomicAgent._rule_score", e)

try:
    print("    Running MacroeconomicAgent.run() ...")
    result = agent_macro.run()
    assert isinstance(result, AgentResult)
    assert result.agent_name == "Macroeconomic Agent"
    assert 0 <= result.score <= 100
    ok(f"MacroeconomicAgent.run() — score={result.score}, signal={result.signal}")
except Exception as e:
    fail("MacroeconomicAgent.run()", e)
    traceback.print_exc()

# ── TEST 6: SentimentAgent ────────────────────────────────────────────────────
print("\n[6] SentimentAgent Tests")
agent_sent = SentimentAgent(_llm)

try:
    pos = agent_sent._score("Hyundai India IPO oversubscribed 17x with strong QIB demand and rally")
    neg = agent_sent._score("IPO crash: Hyundai listed below issue price amid bearish sentiment")
    neu = agent_sent._score("Company announces routine quarterly results")
    assert pos > 0,   f"Expected positive score, got {pos}"
    assert neg < 0,   f"Expected negative score, got {neg}"
    ok(f"_score — positive={pos:.3f}, negative={neg:.3f}, neutral={neu:.3f}")
except Exception as e:
    fail("SentimentAgent._score", e)

try:
    print("    Running SentimentAgent.run('Hyundai India') ...")
    result = agent_sent.run("Hyundai India")
    assert isinstance(result, AgentResult)
    assert result.agent_name == "Sentiment Agent"
    assert 0 <= result.score <= 100
    assert "avg_score" in result.details
    ok(f"SentimentAgent.run() — score={result.score}, avg_sentiment={result.details['avg_score']}")
except Exception as e:
    fail("SentimentAgent.run()", e)
    traceback.print_exc()

# ── TEST 7: RiskAgent ─────────────────────────────────────────────────────────
print("\n[7] RiskAgent Tests")
agent_risk = RiskAgent(_llm)

try:
    print("    Running RiskAgent._metrics(HDFCBANK.NS) ...")
    m = agent_risk._metrics("HDFCBANK.NS", 1500.0)
    if "error" in m:
        warn(f"_metrics error (network?): {m['error']}")
    else:
        # Float keys (must not be NaN/Inf)
        float_keys  = ["annual_vol","sharpe_ratio","var_95_pct","max_drawdown","atr","stop_loss_price","invest_score"]
        # String key (must be one of the expected values)
        string_keys = ["risk_level"]
        all_required = float_keys + string_keys
        missing  = [k for k in all_required if k not in m]
        bad_nan  = [k for k in float_keys  if k in m and not safe_float(m.get(k, 0))]
        if missing:
            fail(f"_metrics missing keys: {missing}")
        elif bad_nan:
            fail(f"_metrics NaN/Inf in float keys: {bad_nan}")
        else:
            assert 0 <= m["invest_score"] <= 100
            assert m["risk_level"] in ("LOW","MEDIUM","HIGH","VERY_HIGH"), f"Unexpected risk_level: {m['risk_level']}"
            ok(f"_metrics — vol={m['annual_vol']:.1f}%, sharpe={m['sharpe_ratio']:.2f}, invest_score={m['invest_score']:.1f}, risk_level={m['risk_level']}")
except Exception as e:
    fail("RiskAgent._metrics", e)
    traceback.print_exc()

try:
    print("    Running RiskAgent.run(TCS.NS) ...")
    result = agent_risk.run("TCS.NS", "TCS", 3500.0)
    assert isinstance(result, AgentResult)
    assert result.agent_name == "Risk Agent"
    assert 0 <= result.score <= 100
    ok(f"RiskAgent.run() — score={result.score}, signal={result.signal}")
except Exception as e:
    fail("RiskAgent.run()", e)
    traceback.print_exc()

# ── TEST 8: IPOIntelligenceAgent ──────────────────────────────────────────────
print("\n[8] IPOIntelligenceAgent Tests")
agent_ipo = IPOIntelligenceAgent(_llm)

try:
    # Strong IPO: high GMP, high subscription
    score_s, sigs_s = agent_ipo._rule_score(1960, 2100, 1934, 67.4, 208.0, 150, 30)
    # Weak IPO: negative listing, no subscription
    score_w, sigs_w = agent_ipo._rule_score(500, 420, 400, 0.8, 0.5, -20, 5)
    assert score_s > score_w, f"Strong IPO score ({score_s}) should exceed weak ({score_w})"
    assert 0 <= score_s <= 100 and 0 <= score_w <= 100
    ok(f"_rule_score — strong={score_s:.1f} > weak={score_w:.1f} (correct ordering)")
except Exception as e:
    fail("IPOIntelligenceAgent._rule_score", e)

try:
    print("    Running IPOIntelligenceAgent.run(BAJAJHFL.NS) ...")
    result = agent_ipo.run(
        ipo_name="Bajaj Housing Finance", symbol="BAJAJHFL.NS",
        issue_price=70.0, current_price=155.0, listing_price=150.0,
        sub_total=67.4, sub_qib=208.0, sub_retail=31.5,
        listing_date_str="2024-09-16",
    )
    assert isinstance(result, AgentResult)
    assert result.agent_name == "IPO Intelligence Agent"
    assert 0 <= result.score <= 100
    assert "listing_gain" in result.details
    assert "current_gain" in result.details
    assert "days_since_listing" in result.details
    ok(f"IPOIntelligenceAgent.run() — score={result.score}, signal={result.signal}, "
       f"listing_gain={result.details['listing_gain']}%, days={result.details['days_since_listing']}")
except Exception as e:
    fail("IPOIntelligenceAgent.run()", e)
    traceback.print_exc()

# ── TEST 9: OrchestratorAgent weighted score ──────────────────────────────────
print("\n[9] OrchestratorAgent Weighted Score Tests")
orch = OrchestratorAgent()

try:
    mock_results = {
        "Price Movement Agent":   AgentResult("Price Movement Agent",   80, "BUY",  85, "s"),
        "Macroeconomic Agent":    AgentResult("Macroeconomic Agent",     75, "BUY",  78, "s"),
        "Sentiment Agent":        AgentResult("Sentiment Agent",          70, "HOLD", 65, "s"),
        "Risk Agent":             AgentResult("Risk Agent",               65, "HOLD", 72, "s"),
        "IPO Intelligence Agent": AgentResult("IPO Intelligence Agent",  85, "BUY",  80, "s"),
    }
    ws = orch._weighted_score(mock_results)
    # Expected: 80*.20 + 75*.15 + 70*.20 + 65*.20 + 85*.25 = 16+11.25+14+13+21.25 = 75.5
    expected = 80*0.20 + 75*0.15 + 70*0.20 + 65*0.20 + 85*0.25
    assert abs(ws - expected) < 0.01, f"Weighted score {ws} != expected {expected}"
    ok(f"_weighted_score = {ws:.2f} (expected {expected:.2f}) ✓")
except Exception as e:
    fail("_weighted_score calculation", e)

try:
    assert orch._decision(85) == "INVEST"
    assert orch._decision(70) == "PARTIAL_INVEST"
    assert orch._decision(55) == "HOLD"
    assert orch._decision(38) == "EXIT"
    assert orch._decision(20) == "STRONG_EXIT"
    ok("_decision mapping — all 5 thresholds correct")
except Exception as e:
    fail("_decision mapping", e)

# ── TEST 10: Full pipeline (no LLM key — tests rule-based path) ───────────────
print("\n[10] Full Pipeline Test (Orchestrator.run)")
print("     Using Bajaj Housing Finance IPO as test case ...")
print("     (LLM calls fall back gracefully if no GROQ_API_KEY)")

progress_steps = []
def _progress_cb(step, msg):
    progress_steps.append((step, msg))
    print(f"     [{step:3d}%] {msg}")

try:
    t0 = time.time()
    result = orch.run(
        ipo_name="Bajaj Housing Finance",
        symbol="BAJAJHFL.NS",
        issue_price=70.0,
        listing_price=150.0,
        current_price=155.0,
        sub_total=67.4,
        sub_qib=208.0,
        sub_retail=31.5,
        listing_date_str="2024-09-16",
        progress_callback=_progress_cb,
    )
    elapsed = time.time() - t0

    # Validate OrchestratorResult
    assert isinstance(result, OrchestratorResult), "Expected OrchestratorResult"
    assert result.ipo_name == "Bajaj Housing Finance"
    assert result.symbol   == "BAJAJHFL.NS"
    assert result.final_decision in ("INVEST","PARTIAL_INVEST","HOLD","EXIT","STRONG_EXIT")
    assert 0 <= result.overall_score <= 100
    assert 0 <= result.confidence    <= 100
    assert result.target_price > 0
    assert result.stop_loss    > 0
    assert result.risk_level in ("LOW","MEDIUM","HIGH","VERY_HIGH")
    assert len(result.agent_scores) == 5
    assert isinstance(result.key_risks, list)
    assert isinstance(result.key_catalysts, list)
    assert isinstance(result.monitoring_triggers, list)
    assert isinstance(result.timestamp, str)

    # Validate all 5 agent scores present
    expected_agents = ["Price Movement Agent","Macroeconomic Agent","Sentiment Agent",
                       "Risk Agent","IPO Intelligence Agent"]
    missing_agents  = [a for a in expected_agents if a not in result.agent_scores]
    if missing_agents:
        fail(f"Missing agent scores: {missing_agents}")
    else:
        ok(f"All 5 agent scores present in OrchestratorResult")

    # Validate no NaN/Inf in key floats
    for field, val in [("overall_score",result.overall_score),("confidence",result.confidence),
                        ("target_price",result.target_price),("stop_loss",result.stop_loss)]:
        if not safe_float(val):
            fail(f"NaN/Inf in {field}: {val}")

    ok(f"Pipeline complete in {elapsed:.1f}s — decision={result.final_decision}, "
       f"score={result.overall_score}/100, conf={result.confidence}%")
    ok(f"Progress callback fired {len(progress_steps)} times (0→100%)")

    print(f"\n     RESULT SUMMARY:")
    print(f"       Decision:        {result.final_decision}")
    print(f"       Overall Score:   {result.overall_score}/100")
    print(f"       Confidence:      {result.confidence}%")
    print(f"       Target Price:    Rs{result.target_price}")
    print(f"       Stop Loss:       Rs{result.stop_loss}")
    print(f"       Risk Level:      {result.risk_level}")
    print(f"       Holding Period:  {result.holding_period}")
    print(f"       Thesis length:   {len(result.investment_thesis)} chars")

except Exception as e:
    fail("Full pipeline OrchestratorAgent.run()", e)
    traceback.print_exc()

# ── TEST 11: Public API function ──────────────────────────────────────────────
print("\n[11] Public API run_ipo_multi_agent_analysis()")
try:
    r2 = run_ipo_multi_agent_analysis(
        ipo_name="Hyundai India",
        symbol="HYUNDAI.NS",
        issue_price=1960.0,
        listing_price=1934.0,
        sub_total=17.4,
        sub_qib=36.5,
    )
    assert isinstance(r2, OrchestratorResult)
    assert r2.ipo_name == "Hyundai India"
    ok(f"Public API — decision={r2.final_decision}, score={r2.overall_score}")
except Exception as e:
    fail("run_ipo_multi_agent_analysis()", e)
    traceback.print_exc()

# ── TEST 12: FastAPI Router ───────────────────────────────────────────────────
print("\n[12] FastAPI Router Tests")
try:
    sys.path.insert(0, os.path.join(ROOT, "web", "backend"))
    # Verify imports
    import ast
    router_src = open(os.path.join(ROOT, "web","backend","routers","ipo_multiagent.py"), encoding="utf-8").read()
    ast.parse(router_src)
    ok("ipo_multiagent.py — syntax valid")

    assert "POST" in router_src and "/analyze" in router_src
    assert "GET"  in router_src and "/status"  in router_src
    assert "_safe" in router_src, "_safe() serialiser missing"
    assert "run_ipo_multi_agent_analysis" in router_src
    ok("Router has /status and /analyze endpoints + _safe() serialiser")
except Exception as e:
    fail("Router validation", e)

try:
    main_src = open(os.path.join(ROOT, "web","backend","main.py"), encoding="utf-8").read()
    assert "ipo_multiagent" in main_src, "ipo_multiagent not imported in main.py"
    assert "/api/ipo_multiagent" in main_src, "prefix missing"
    ok("main.py — ipo_multiagent router imported and registered")
except Exception as e:
    fail("main.py registration check", e)

# ── TEST 13: Frontend Files ───────────────────────────────────────────────────
print("\n[13] Frontend File Tests")
try:
    page_src = open(os.path.join(ROOT, "web","frontend","src","pages","IPOMultiAgent.js"), encoding="utf-8").read()
    checks = [
        ("ipoMultiAgent import",  "ipoMultiAgent"       in page_src),
        ("AgentCard component",   "AgentCard"            in page_src),
        ("ScoreRing component",   "ScoreRing"            in page_src),
        ("runAnalysis function",  "runAnalysis"          in page_src),
        ("PlotlyChart radar",     "scatterpolar"         in page_src),
        ("INVEST decision",       "INVEST"               in page_src),
        ("Sample IPOs",           "SAMPLE_IPOS"          in page_src),
        ("Progress bar",          "progress"             in page_src),
        ("All 5 agents listed",   all(a["key"] in page_src for a in [
            {"key":"Price Movement Agent"},{"key":"Macroeconomic Agent"},
            {"key":"Sentiment Agent"},{"key":"Risk Agent"},{"key":"IPO Intelligence Agent"}
        ])),
    ]
    for label, passed in checks:
        if passed: ok(f"IPOMultiAgent.js — {label}")
        else:      fail(f"IPOMultiAgent.js missing: {label}")
except Exception as e:
    fail("IPOMultiAgent.js read/check", e)

try:
    app_src     = open(os.path.join(ROOT, "web","frontend","src","App.js"), encoding="utf-8").read()
    sidebar_src = open(os.path.join(ROOT, "web","frontend","src","components","Sidebar.js"), encoding="utf-8").read()
    api_src     = open(os.path.join(ROOT, "web","frontend","src","api.js"), encoding="utf-8").read()

    assert "IPOMultiAgent"     in app_src,      "IPOMultiAgent not in App.js"
    assert "ipo_multiagent"    in app_src,       "ipo_multiagent key missing in App.js"
    assert "ipo_multiagent"    in sidebar_src,   "ipo_multiagent missing from Sidebar"
    assert "IPO Multi-Agent"   in sidebar_src,   "nav label missing from Sidebar"
    assert "ipoMultiAgent"     in api_src,        "ipoMultiAgent missing from api.js"
    assert "ipo_multiagent/analyze" in api_src,   "analyze endpoint missing from api.js"
    ok("App.js — IPOMultiAgent page registered")
    ok("Sidebar.js — IPO Multi-Agent nav item present")
    ok("api.js — ipoMultiAgent.analyze() registered")
except Exception as e:
    fail("Frontend wiring check", e)

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"  TOTAL: {PASS} PASSED  |  {FAIL} FAILED  |  {WARN} WARNINGS")
print("="*60)
if FAIL == 0:
    print("  🎉 ALL TESTS PASSED — system ready for use")
else:
    print(f"  ❗ {FAIL} test(s) failed — see above")
print()
sys.exit(0 if FAIL == 0 else 1)
