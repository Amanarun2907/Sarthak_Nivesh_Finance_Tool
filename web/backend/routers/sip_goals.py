"""
SIP Goal Planner — Complete Backend
- Inflation-adjusted target calculation
- Live AMFI returns (3Y CAGR from mfapi.in)
- Live fund recommendations per risk profile
- Groq AI advice for the plan
- SQLite goal persistence
"""
from fastapi import APIRouter, Body
import sqlite3, os, requests, numpy as np
from datetime import datetime
from pathlib import Path

router = APIRouter()
_DB = Path(__file__).resolve().parents[3] / "data" / "sarthak_nivesh.db"

PROFILE_KEYWORDS = {
    "Conservative": ["gilt fund", "liquid fund", "overnight fund",
                     "money market fund", "ultra short", "low duration", "short term debt"],
    "Moderate":     ["large cap fund", "index fund", "nifty 50 index",
                     "bluechip", "flexi cap fund", "balanced advantage", "large & mid cap"],
    "Aggressive":   ["small cap fund", "mid cap fund", "multi cap fund",
                     "quant small", "quant mid", "emerging bluechip"],
}
FALLBACK = {"Conservative": 7.5, "Moderate": 12.0, "Aggressive": 16.0}
PROFILE_DESC = {
    "Conservative": "Low risk · Debt & Gilt funds · Stable returns · Best for short goals",
    "Moderate":     "Medium risk · Large Cap & Index funds · Balanced growth",
    "Aggressive":   "High risk · Small & Mid Cap · Maximum growth potential",
}

# ── DB ────────────────────────────────────────────────────────────────────────

def _ensure_table():
    _DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB))
    conn.execute("""CREATE TABLE IF NOT EXISTS sip_goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        goal_name TEXT, goal_type TEXT, target_today REAL, years INTEGER,
        inflation REAL, existing_savings REAL, monthly_sip REAL,
        risk_profile TEXT, expected_return REAL, status TEXT DEFAULT 'Active')""")
    conn.commit(); conn.close()

# ── AMFI live data ────────────────────────────────────────────────────────────

def _fetch_cagr(code: str, years: int = 3):
    try:
        r = requests.get(f"https://api.mfapi.in/mf/{code}", timeout=10)
        if r.status_code != 200:
            return None
        data = list(reversed(r.json().get("data", [])))
        target_idx = years * 365
        if len(data) < target_idx // 2:
            return None
        idx = min(target_idx, len(data) - 1)
        latest = float(data[-1]["nav"])
        old    = float(data[-idx]["nav"])
        if old <= 0:
            return None
        return round(((latest / old) ** (1.0 / years) - 1) * 100, 2)
    except Exception:
        return None


def _fetch_amfi_funds(profile: str, max_funds: int = 5):
    """Fetch live Direct-Growth funds from AMFI matching the profile."""
    kws = PROFILE_KEYWORDS[profile]
    funds = []
    try:
        r = requests.get("https://www.amfiindia.com/spages/NAVAll.txt", timeout=20)
        if r.status_code != 200:
            return funds
        for line in r.text.strip().split("\n"):
            parts = line.strip().split(";")
            if len(parts) < 6:
                continue
            try:
                code     = parts[0].strip()
                name     = parts[3].strip()
                nav      = float(parts[4].strip())
                nav_date = parts[5].strip()
                nl       = name.lower()
                if "direct" not in nl or "growth" not in nl or nav <= 0:
                    continue
                if not any(kw in nl for kw in kws):
                    continue
                funds.append({"scheme_code": code, "name": name,
                              "nav": nav, "nav_date": nav_date})
            except Exception:
                continue
        # Sort by NAV desc (older = more established)
        funds = sorted(funds, key=lambda x: x["nav"], reverse=True)[:max_funds * 3]
        # Enrich with live 3Y CAGR
        enriched = []
        for f in funds:
            cagr = _fetch_cagr(f["scheme_code"], 3)
            if cagr and 1 < cagr < 60:
                f["cagr_3y"] = cagr
                enriched.append(f)
            if len(enriched) >= max_funds:
                break
        return enriched[:max_funds]
    except Exception as e:
        print(f"AMFI error: {e}")
        return []


PROFILE_FALLBACK_FUNDS = {
    "Conservative": [
        {"scheme_code": "119841", "name": "ICICI Prudential All Seasons Bond - Direct Growth", "nav": 38.60, "cagr_3y": 7.90},
        {"scheme_code": "120704", "name": "HDFC Corporate Bond Fund - Direct Growth", "nav": 32.40, "cagr_3y": 7.40},
        {"scheme_code": "119597", "name": "SBI Magnum Gilt Fund - Direct Growth", "nav": 64.80, "cagr_3y": 7.60},
    ],
    "Moderate": [
        {"scheme_code": "122639", "name": "Parag Parikh Flexi Cap Fund - Direct Growth", "nav": 84.15, "cagr_3y": 21.60},
        {"scheme_code": "120716", "name": "UTI Nifty 50 Index Fund - Direct Growth", "nav": 178.60, "cagr_3y": 16.90},
        {"scheme_code": "118989", "name": "HDFC Top 100 Fund - Direct Growth", "nav": 1120.35, "cagr_3y": 19.50},
    ],
    "Aggressive": [
        {"scheme_code": "118778", "name": "Nippon India Small Cap Fund - Direct Growth", "nav": 172.40, "cagr_3y": 29.80},
        {"scheme_code": "125354", "name": "Quant Small Cap Fund - Direct Growth", "nav": 268.10, "cagr_3y": 33.20},
        {"scheme_code": "120586", "name": "Motilal Oswal Midcap Fund - Direct Growth", "nav": 96.25, "cagr_3y": 32.40},
    ]
}

def _live_return(profile: str):
    funds = _fetch_amfi_funds(profile, max_funds=5)
    cagrs = [f["cagr_3y"] for f in funds if f.get("cagr_3y")]
    if cagrs:
        avg = round(float(np.mean(cagrs)), 2)
        return {
            "return_pct": avg,
            "source": f"Live AMFI + mfapi.in — avg 3Y CAGR of {len(cagrs)} {profile} funds",
            "funds": funds,
        }
    return {
        "return_pct": FALLBACK[profile],
        "source": "Historical average (AMFI temporarily unavailable)",
        "funds": PROFILE_FALLBACK_FUNDS.get(profile, PROFILE_FALLBACK_FUNDS["Moderate"]),
    }

# ── Math ──────────────────────────────────────────────────────────────────────

def _sip_needed(fv: float, rate: float, years: int, existing: float = 0) -> float:
    r = rate / 100 / 12
    n = years * 12
    fv_ex = existing * ((1 + r) ** n)
    rem   = max(0, fv - fv_ex)
    if r == 0:
        return rem / n if n else 0
    return max(0, rem * r / (((1 + r) ** n - 1) * (1 + r)))


def _build_series(sip: float, rate: float, years: int, existing: float = 0):
    r   = rate / 100 / 12
    val = existing
    inv = existing
    series = []
    for m in range(1, years * 12 + 1):
        val = val * (1 + r) + sip
        inv += sip
        if m % 12 == 0:
            series.append({
                "year":     m // 12,
                "invested": round(inv, 0),
                "value":    round(val, 0),
                "gain":     round(val - inv, 0),
            })
    return series

# ── AI Advice ─────────────────────────────────────────────────────────────────

def _ai_advice(goal_name: str, goal_type: str, target: float, years: int,
               inflation: float, existing: float, profiles: dict) -> str:
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        return None
    mod = profiles.get("Moderate", {})
    fv  = target * ((1 + inflation / 100) ** years)
    prompt = f"""
You are an expert Indian financial advisor. A user wants to plan a SIP for the following goal:

Goal: {goal_name} ({goal_type})
Target Amount Today: ₹{target:,.0f}
Inflation-Adjusted Target ({years} years at {inflation}%): ₹{fv:,.0f}
Time Horizon: {years} years
Existing Savings: ₹{existing:,.0f}

Calculated SIP Requirements (from live AMFI data):
- Conservative ({profiles.get('Conservative',{}).get('return_pct',7.5)}% p.a.): ₹{profiles.get('Conservative',{}).get('monthly_sip',0):,.0f}/month
- Moderate ({mod.get('return_pct',12)}% p.a.): ₹{mod.get('monthly_sip',0):,.0f}/month
- Aggressive ({profiles.get('Aggressive',{}).get('return_pct',16)}% p.a.): ₹{profiles.get('Aggressive',{}).get('monthly_sip',0):,.0f}/month

Provide a warm, practical AI financial plan with these 4 sections:
1. **My Assessment** — Is this goal realistic? Is the timeline right?
2. **My Recommendation** — Which risk profile should they choose and why? (Consider their goal type and timeline)
3. **Key Risks to Watch** — 2-3 specific risks for this goal
4. **Pro Tips** — 2-3 actionable tips to reach this goal faster

Keep it under 250 words. Be warm, encouraging, and specific to Indian markets.
Use ₹ symbol for amounts. Speak like a trusted advisor, not a robot.
""".strip()
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {key}"},
            json={"model": "openai/gpt-oss-120b", "temperature": 0.65,
                  "max_tokens": 500,
                  "messages": [
                      {"role": "system", "content": "You are a trusted Indian financial advisor. Be warm, specific, and practical."},
                      {"role": "user", "content": prompt},
                  ]},
            timeout=35,
        )
        if r.status_code == 200:
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
    return None

# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/calculate")
def calculate(data: dict = Body(...)):
    target    = float(data.get("target_today", 1000000))
    years     = int(data.get("years", 10))
    inflation = float(data.get("inflation", 6.0))
    existing  = float(data.get("existing_savings", 0))
    goal_name = data.get("goal_name", "My Goal")
    goal_type = data.get("goal_type", "Custom")

    fv = target * ((1 + inflation / 100) ** years)

    profiles = {}
    for profile in ["Conservative", "Moderate", "Aggressive"]:
        live = _live_return(profile)
        ret  = live["return_pct"]
        sip  = _sip_needed(fv, ret, years, existing)
        ser  = _build_series(sip, ret, years, existing)
        total_val = float(ser[-1]["value"]) if ser else 0
        total_inv = float(ser[-1]["invested"]) if ser else 0
        profiles[profile] = {
            "return_pct":    ret,
            "source":        live["source"],
            "monthly_sip":   round(sip, 0),
            "total_value":   round(total_val, 0),
            "total_invested":round(total_inv, 0),
            "total_gain":    round(total_val - total_inv, 0),
            "series":        ser,
            "funds":         live["funds"],
            "description":   PROFILE_DESC[profile],
        }

    # AI advice
    ai_advice = _ai_advice(goal_name, goal_type, target, years,
                           inflation, existing, profiles)

    return {
        "future_target": round(fv, 2),
        "profiles":      profiles,
        "ai_advice":     ai_advice,
        "goal_name":     goal_name,
        "goal_type":     goal_type,
        "years":         years,
        "inflation":     inflation,
        "target_today":  target,
        "existing":      existing,
    }


@router.post("/save")
def save_goal(data: dict = Body(...)):
    _ensure_table()
    _DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB))
    conn.execute("""INSERT INTO sip_goals
        (goal_name, goal_type, target_today, years, inflation,
         existing_savings, monthly_sip, risk_profile, expected_return)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (data.get("goal_name"), data.get("goal_type"), data.get("target_today"),
         data.get("years"), data.get("inflation"), data.get("existing_savings"),
         data.get("monthly_sip"), data.get("risk_profile"), data.get("expected_return")))
    conn.commit(); conn.close()
    return {"status": "saved"}


@router.get("/goals")
def get_goals():
    _ensure_table()
    _DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB))
    rows = conn.execute(
        "SELECT * FROM sip_goals WHERE status='Active' ORDER BY created_at DESC"
    ).fetchall()
    cols = ["id", "created_at", "goal_name", "goal_type", "target_today", "years",
            "inflation", "existing_savings", "monthly_sip", "risk_profile",
            "expected_return", "status"]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]


@router.delete("/goals/{goal_id}")
def delete_goal(goal_id: int):
    _DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_DB))
    conn.execute("UPDATE sip_goals SET status='Deleted' WHERE id=?", (goal_id,))
    conn.commit(); conn.close()
    return {"status": "deleted"}
