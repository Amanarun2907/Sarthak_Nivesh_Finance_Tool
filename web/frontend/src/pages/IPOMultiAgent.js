/**
 * IPO Multi-Agent Framework — Advanced React UI
 * ================================================
 * Impactful · Advanced · User-Friendly
 * Groq Llama 3.3 70B · 6 Hierarchical Agents
 *
 * Authors: Aman Jain, Rohit Fogla, Vanshita Mehta, Disita Tirthani
 * Project: Sarthak Nivesh — B.Tech 3rd Year, BML Munjal University
 */

import React, { useState, useRef, useEffect } from 'react';
import PlotlyChart from '../components/PlotlyChart';
import { ipoMultiAgent } from '../api';
import toast from 'react-hot-toast';

// ── Agent definitions ─────────────────────────────────────────────────────────
const AGENTS = [
  { key: 'Price Movement Agent',   icon: '📊', color: '#00d4ff', weight: 20,
    desc: 'RSI · MACD · Bollinger Bands · Volume · Momentum · Support/Resistance' },
  { key: 'Macroeconomic Agent',    icon: '🌐', color: '#00ff88', weight: 15,
    desc: 'NIFTY · India VIX · FII/DII · USD/INR · Crude Oil · Dow Jones' },
  { key: 'Sentiment Agent',        icon: '📰', color: '#ffa502', weight: 20,
    desc: 'VADER · TextBlob · Financial Keywords · Google News RSS' },
  { key: 'Risk Agent',             icon: '🛡️', color: '#a855f7', weight: 20,
    desc: 'VaR(95%) · CVaR · Sharpe Ratio · Max Drawdown · Dynamic Stop-Loss' },
  { key: 'IPO Intelligence Agent', icon: '🚀', color: '#ff6b35', weight: 25,
    desc: 'GMP · Subscription Ratio · Post-Listing Milestones · Hold/Exit Logic' },
];

const DECISION_CFG = {
  INVEST:         { color: '#00ff88', glow: '0 0 30px rgba(0,255,136,0.4)',  bg: 'rgba(0,255,136,0.06)',  label: '✅ INVEST',         sub: 'Strong multi-agent buy signal — consider full allocation' },
  PARTIAL_INVEST: { color: '#00d4ff', glow: '0 0 30px rgba(0,212,255,0.4)', bg: 'rgba(0,212,255,0.06)',  label: '🔵 PARTIAL INVEST', sub: 'Good signal — consider half position, scale in on dips' },
  HOLD:           { color: '#ffa502', glow: '0 0 30px rgba(255,165,2,0.3)', bg: 'rgba(255,165,2,0.06)',  label: '⏸️ HOLD',            sub: 'Mixed signals — wait for clearer direction before acting' },
  EXIT:           { color: '#ff4757', glow: '0 0 30px rgba(255,71,87,0.4)', bg: 'rgba(255,71,87,0.06)',  label: '🔴 EXIT',            sub: 'Bearish signals — reduce exposure and protect capital' },
  STRONG_EXIT:    { color: '#cc0000', glow: '0 0 30px rgba(204,0,0,0.4)',   bg: 'rgba(204,0,0,0.06)',    label: '❌ STRONG EXIT',    sub: 'Multiple red flags — exit position immediately' },
};

const SAMPLE_IPOS = [
  { label: 'Bajaj Housing Finance', tag: '208x QIB · Strong HOLD',
    data: { ipo_name:'Bajaj Housing Finance', symbol:'BAJAJHFL.NS', issue_price:70, listing_price:150, current_price:0, sub_total:67.4, sub_qib:208.0, sub_retail:31.5, listing_date_str:'2024-09-16' }},
  { label: 'Hyundai India', tag: '17x Sub · Large Cap',
    data: { ipo_name:'Hyundai India', symbol:'HYUNDAI.NS', issue_price:1960, listing_price:1934, current_price:0, sub_total:17.4, sub_qib:36.5, sub_retail:6.8, listing_date_str:'2024-10-22' }},
  { label: 'Swiggy', tag: '3.6x Sub · New Age Tech',
    data: { ipo_name:'Swiggy', symbol:'SWIGGY.NS', issue_price:390, listing_price:420, current_price:0, sub_total:3.6, sub_qib:6.0, sub_retail:1.1, listing_date_str:'2024-11-13' }},
];

// ── Animated Counter ──────────────────────────────────────────────────────────
function AnimatedNumber({ value, decimals = 0, prefix = '', suffix = '' }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const end = parseFloat(value) || 0;
    const duration = 1200;
    const steps = 40;
    const increment = end / steps;
    let step = 0;
    const timer = setInterval(() => {
      step++;
      start = Math.min(start + increment, end);
      setDisplay(start);
      if (step >= steps) clearInterval(timer);
    }, duration / steps);
    return () => clearInterval(timer);
  }, [value]);
  return <>{prefix}{display.toFixed(decimals)}{suffix}</>;
}

// ── Score Ring ────────────────────────────────────────────────────────────────
function ScoreRing({ score, size = 88 }) {
  const color = score >= 65 ? '#00ff88' : score >= 45 ? '#ffa502' : '#ff4757';
  const r = size / 2 - 7;
  const circ = 2 * Math.PI * r;
  const fill = (Math.max(0, Math.min(100, score)) / 100) * circ;
  return (
    <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1c2128" strokeWidth="7"/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="7"
          strokeDasharray={`${fill} ${circ}`} strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 1.2s cubic-bezier(0.4,0,0.2,1)' }}/>
      </svg>
      <div style={{ position:'absolute', inset:0, display:'flex',
        flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
        <div style={{ fontSize: size > 75 ? '1.2rem' : '0.9rem', fontWeight: 900, color, lineHeight:1 }}>
          {Math.round(score)}
        </div>
        <div style={{ fontSize:'0.55rem', color:'#484f58', marginTop:1 }}>/100</div>
      </div>
    </div>
  );
}

// ── Signal Badge ──────────────────────────────────────────────────────────────
function SignalBadge({ signal }) {
  const cfg = {
    STRONG_BUY:  { color:'#00ff88', bg:'rgba(0,255,136,0.12)',  border:'rgba(0,255,136,0.3)'  },
    BUY:         { color:'#00d4ff', bg:'rgba(0,212,255,0.12)',  border:'rgba(0,212,255,0.3)'  },
    HOLD:        { color:'#ffa502', bg:'rgba(255,165,2,0.12)',  border:'rgba(255,165,2,0.3)'  },
    SELL:        { color:'#ff4757', bg:'rgba(255,71,87,0.12)',  border:'rgba(255,71,87,0.3)'  },
    STRONG_SELL: { color:'#cc0000', bg:'rgba(204,0,0,0.12)',    border:'rgba(204,0,0,0.3)'    },
    'N/A':       { color:'#484f58', bg:'rgba(72,79,88,0.12)',   border:'rgba(72,79,88,0.3)'   },
  };
  const s = cfg[signal] || cfg['N/A'];
  return (
    <span style={{ background: s.bg, color: s.color, border: `1px solid ${s.border}`,
      borderRadius: 6, padding: '3px 9px', fontSize: '0.7rem', fontWeight: 800,
      letterSpacing: '0.04em' }}>
      {signal}
    </span>
  );
}

// ── Agent Card ────────────────────────────────────────────────────────────────
function AgentCard({ agent, result, isRunning }) {
  const [expanded, setExpanded] = useState(false);
  const score  = result?.score    ?? null;
  const signal = result?.signal   ?? null;
  const conf   = result?.confidence ?? null;
  const summary= result?.summary  ?? null;
  const hasResult = result !== null;

  return (
    <div style={{
      background: 'var(--bg-glass)',
      border: `1px solid ${hasResult ? agent.color : isRunning ? '#ffa50240' : 'var(--border)'}`,
      borderRadius: 14, padding: '1.1rem',
      boxShadow: hasResult ? `0 0 20px ${agent.color}20` : 'none',
      transition: 'all 0.4s cubic-bezier(0.4,0,0.2,1)',
    }}>
      {/* Header row */}
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:10 }}>
        <div style={{ fontSize:'1.5rem', flexShrink:0 }}>{agent.icon}</div>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontWeight:700, fontSize:'0.82rem', color: hasResult ? agent.color : 'var(--text-primary)',
            whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>
            {agent.key}
          </div>
          <div style={{ fontSize:'0.63rem', color:'#484f58', marginTop:1 }}>
            Weight: <span style={{ color: agent.color, fontWeight:700 }}>{agent.weight}%</span>
          </div>
        </div>
        {isRunning && !hasResult && (
          <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
            <div className="spinner-sm"/>
            <span style={{ fontSize:'0.65rem', color:'#ffa502' }}>Running…</span>
          </div>
        )}
        {hasResult && signal && <SignalBadge signal={signal}/>}
      </div>

      {/* Score bar */}
      {score !== null && (
        <div style={{ marginBottom: 8 }}>
          <div style={{ display:'flex', justifyContent:'space-between',
            fontSize:'0.65rem', color:'#484f58', marginBottom:4 }}>
            <span>Score</span>
            <span style={{ color: agent.color, fontWeight:800 }}>{score}/100</span>
          </div>
          <div style={{ height:6, background:'#1c2128', borderRadius:3, overflow:'hidden' }}>
            <div style={{ height:'100%', width:`${score}%`,
              background:`linear-gradient(90deg, ${agent.color}99, ${agent.color})`,
              borderRadius:3, transition:'width 1.2s cubic-bezier(0.4,0,0.2,1)' }}/>
          </div>
        </div>
      )}

      {/* Confidence */}
      {conf !== null && (
        <div style={{ fontSize:'0.65rem', color:'#484f58', marginBottom:8 }}>
          Confidence: <span style={{ color:'var(--text-secondary)', fontWeight:600 }}>{conf}%</span>
        </div>
      )}

      {/* Summary / description */}
      {summary ? (
        <div>
          <div style={{
            fontSize:'0.75rem', color:'var(--text-secondary)', lineHeight:1.6,
            display: expanded ? 'block' : '-webkit-box',
            WebkitLineClamp: expanded ? 'unset' : 3,
            WebkitBoxOrient: 'vertical',
            overflow: expanded ? 'visible' : 'hidden',
          }}>
            {summary}
          </div>
          {summary.length > 100 && (
            <button onClick={() => setExpanded(!expanded)}
              style={{ background:'none', border:'none', color: agent.color,
                fontSize:'0.63rem', cursor:'pointer', marginTop:4, padding:0 }}>
              {expanded ? '▲ Show less' : '▼ Show more'}
            </button>
          )}
        </div>
      ) : !hasResult && (
        <div style={{ fontSize:'0.68rem', color:'#484f58', lineHeight:1.5 }}>{agent.desc}</div>
      )}
    </div>
  );
}

// ── KPI Card ──────────────────────────────────────────────────────────────────
function KPICard({ label, value, sub, color, icon }) {
  return (
    <div style={{ background:'var(--bg-glass)', border:`1px solid ${color}30`,
      borderRadius:12, padding:'1rem', borderLeft:`3px solid ${color}`,
      transition:'all 0.3s' }}>
      <div style={{ fontSize:'0.65rem', color:'#484f58', textTransform:'uppercase',
        letterSpacing:'0.05em', marginBottom:4, display:'flex', alignItems:'center', gap:5 }}>
        {icon && <span>{icon}</span>}{label}
      </div>
      <div style={{ fontWeight:900, color, fontSize:'1.3rem', lineHeight:1, marginBottom:3 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize:'0.7rem', color:'var(--text-secondary)', marginTop:2 }}>{sub}</div>}
    </div>
  );
}

// ── List Section ──────────────────────────────────────────────────────────────
function ListSection({ title, items, color, icon }) {
  return (
    <div className="card">
      <div style={{ fontWeight:700, color, marginBottom:10, fontSize:'0.88rem',
        display:'flex', alignItems:'center', gap:6 }}>
        <span>{icon}</span>{title}
      </div>
      {items?.length > 0
        ? items.map((item, i) => (
          <div key={i} style={{ display:'flex', gap:8, alignItems:'flex-start',
            padding:'7px 0', borderBottom: i < items.length-1 ? '1px solid var(--border)' : 'none' }}>
            <span style={{ color, fontSize:'0.8rem', flexShrink:0, marginTop:1 }}>›</span>
            <span style={{ fontSize:'0.78rem', color:'var(--text-primary)', lineHeight:1.55 }}>
              {item}
            </span>
          </div>
        ))
        : <div style={{ color:'#484f58', fontSize:'0.75rem', fontStyle:'italic' }}>
            No data available
          </div>
      }
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function IPOMultiAgent() {
  const [form, setForm] = useState({
    ipo_name:'', symbol:'', issue_price:'',
    listing_price:'', current_price:'',
    sub_total:'', sub_qib:'', sub_retail:'',
    listing_date_str:'',
  });
  const [running,  setRunning]  = useState(false);
  const [progress, setProgress] = useState(0);
  const [progMsg,  setProgMsg]  = useState('');
  const [result,   setResult]   = useState(null);
  const [step,     setStep]     = useState('idle');
  const [tab,      setTab]      = useState('overview');
  const pollRef = useRef(null);
  const resultsRef = useRef(null);

  const upd = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const loadSample = (s) => {
    setForm({
      ipo_name:         s.data.ipo_name,
      symbol:           s.data.symbol,
      issue_price:      String(s.data.issue_price),
      listing_price:    String(s.data.listing_price),
      current_price:    '',
      sub_total:        String(s.data.sub_total),
      sub_qib:          String(s.data.sub_qib),
      sub_retail:       String(s.data.sub_retail || ''),
      listing_date_str: s.data.listing_date_str || '',
    });
    toast.success(`Loaded: ${s.label}`);
  };

  const runAnalysis = async () => {
    if (!form.ipo_name.trim())  { toast.error('Enter IPO / Company Name'); return; }
    if (!form.symbol.trim())    { toast.error('Enter NSE Symbol (e.g. HYUNDAI.NS)'); return; }
    if (!form.issue_price)      { toast.error('Enter Issue Price'); return; }
    if (!form.listing_price)    { toast.error('Enter Listing Price'); return; }

    setRunning(true); setStep('running'); setResult(null); setProgress(3);
    setProgMsg('Initialising 6-agent hierarchical framework…');

    const stages = [
      [10, 'Agent 1 — Price Movement: fetching RSI, MACD, Bollinger Bands…'],
      [25, 'Agent 2 — Macroeconomic: NIFTY, VIX, FII/DII, global indices…'],
      [45, 'Agent 3 — Sentiment: Google News RSS, VADER, TextBlob…'],
      [62, 'Agent 4 — Risk: VaR(95%), CVaR, Sharpe ratio, drawdown…'],
      [80, 'Agent 5 — IPO Intelligence: GMP, subscription, milestones…'],
      [91, 'Orchestrator Agent synthesising all 5 reports → Final decision…'],
    ];
    let si = 0;
    pollRef.current = setInterval(() => {
      if (si < stages.length) {
        setProgress(stages[si][0]);
        setProgMsg(stages[si][1]);
        si++;
      }
    }, 4500);

    try {
      const r = await ipoMultiAgent.analyze({
        ipo_name:         form.ipo_name.trim(),
        symbol:           form.symbol.trim(),
        issue_price:      parseFloat(form.issue_price),
        listing_price:    parseFloat(form.listing_price),
        current_price:    parseFloat(form.current_price)  || 0,
        sub_total:        parseFloat(form.sub_total)       || 0,
        sub_qib:          parseFloat(form.sub_qib)         || 0,
        sub_retail:       parseFloat(form.sub_retail)      || 0,
        listing_date_str: form.listing_date_str || '',
      });
      clearInterval(pollRef.current);
      setProgress(100);
      setProgMsg('✅ 6-agent analysis complete!');
      setResult(r.data);
      setStep('done');
      setTab('overview');
      toast.success(`Analysis complete! Decision: ${r.data.final_decision}`);
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior:'smooth' }), 300);
    } catch (e) {
      clearInterval(pollRef.current);
      const msg = e?.response?.data?.detail || e.message || 'Analysis failed';
      toast.error(msg);
      setStep('idle');
    } finally {
      setRunning(false);
    }
  };

  // ── Derived chart data ─────────────────────────────────────────────────────
  const agentData = result?.agent_scores
    ? AGENTS.map(a => ({ ...a, score: result.agent_scores[a.key]?.score ?? 50,
        signal: result.agent_scores[a.key]?.signal ?? 'HOLD',
        confidence: result.agent_scores[a.key]?.confidence ?? 60,
        summary: result.agent_scores[a.key]?.summary ?? '' }))
    : [];

  const radarData = agentData.length ? [{
    type: 'scatterpolar', fill: 'toself', mode: 'lines+markers',
    r:     [...agentData.map(a => a.score), agentData[0].score],
    theta: [...agentData.map(a => a.key.replace(' Agent', '')), agentData[0].key.replace(' Agent', '')],
    line:  { color: result?.decision_color || '#00d4ff', width: 2.5 },
    fillcolor: (result?.decision_color || '#00d4ff') + '20',
    marker: { color: agentData.map(a => a.color), size: 8 },
    name: 'Agent Scores',
    hovertemplate: '<b>%{theta}</b><br>Score: %{r}/100<extra></extra>',
  }] : [];

  const barData = agentData.length ? [{
    type: 'bar', orientation: 'h',
    y: agentData.map(a => a.key.replace(' Agent', '')),
    x: agentData.map(a => a.score),
    marker: {
      color: agentData.map(a => a.color),
      line: { color: agentData.map(a => a.color), width: 1 },
    },
    text: agentData.map(a => `${a.score}/100`),
    textposition: 'outside',
    textfont: { size: 11 },
    hovertemplate: '<b>%{y}</b><br>Score: %{x}/100<extra></extra>',
  }] : [];

  // Score gauge
  const gaugeData = result ? [{
    type: 'indicator', mode: 'gauge+number',
    value: result.overall_score,
    title: { text: 'Composite Score', font: { color:'#8b949e', size:13 } },
    number: { suffix: '/100', font: { color: result.decision_color, size:28, weight:900 } },
    gauge: {
      axis: { range:[0,100], tickwidth:1, tickcolor:'#30363d', tickfont:{color:'#484f58',size:9} },
      bar:  { color: result.decision_color },
      bgcolor: '#0d1117',
      borderwidth: 1, bordercolor: '#21262d',
      steps: [
        { range:[0,30],  color:'rgba(204,0,0,0.1)'     },
        { range:[30,45], color:'rgba(255,71,87,0.1)'   },
        { range:[45,65], color:'rgba(255,165,2,0.1)'   },
        { range:[65,80], color:'rgba(0,212,255,0.1)'   },
        { range:[80,100],color:'rgba(0,255,136,0.1)'   },
      ],
      threshold: { line:{color:'#fff',width:2}, thickness:0.75, value: result.overall_score },
    },
  }] : [];

  // Weights donut
  const weightsData = [{
    type: 'pie',
    labels: AGENTS.map(a => a.key.replace(' Agent', '')),
    values: AGENTS.map(a => a.weight),
    marker: { colors: AGENTS.map(a => a.color), line:{color:'#060910',width:3} },
    hole: 0.55, textinfo: 'label+percent',
    textfont: { size: 10, color: '#f0f6fc' },
    hovertemplate: '<b>%{label}</b><br>Weight: %{value}%<extra></extra>',
  }];

  const decCfg = result ? (DECISION_CFG[result.final_decision] || DECISION_CFG.HOLD) : null;

  const TABS = [
    { id:'overview',   label:'📊 Overview'        },
    { id:'agents',     label:'🤖 Agent Results'    },
    { id:'charts',     label:'📈 Charts'           },
    { id:'strategy',   label:'🎯 Strategy'         },
    { id:'risks',      label:'⚠️ Risks & Catalysts' },
  ];

  return (
    <div style={{ maxWidth: 1400 }}>

      {/* ── PAGE HEADER ─────────────────────────────────────────────────── */}
      <div className="page-header">
        <div className="section-title">
          🧬 IPO Multi-Agent Framework
        </div>
        <div className="section-subtitle">
          <span className="pulse-dot"/>
          6-agent hierarchical AI system &nbsp;·&nbsp; Groq Llama 3.3 70B
          &nbsp;·&nbsp; Real-time data: NSE · Yahoo Finance · Google News
        </div>
      </div>

      {/* ── PAPER CITATION ──────────────────────────────────────────────── */}
      <div style={{ background:'linear-gradient(135deg,rgba(168,85,247,0.08),rgba(0,212,255,0.04))',
        border:'1px solid rgba(168,85,247,0.2)', borderRadius:12,
        padding:'0.9rem 1.25rem', marginBottom:'1.25rem', fontSize:'0.8rem' }}>
        <div style={{ fontWeight:700, color:'#a855f7', marginBottom:3, fontSize:'0.82rem' }}>
          📄 Research Reference
        </div>
        <div style={{ color:'var(--text-secondary)', lineHeight:1.6 }}>
          "A multi-agentic AI framework integrating multiple autonomous agents for IPO investment
          &amp; exit strategy — hierarchical multi-agent system processing heterogeneous financial
          information: price movements, macroeconomic indicators, investor sentiment, risk signals."
        </div>
        <div style={{ marginTop:6, display:'flex', gap:8, flexWrap:'wrap' }}>
          {['Agentic AI','IPO','Investment','Prediction','LLM'].map(tag => (
            <span key={tag} className="badge badge-purple" style={{ fontSize:'0.65rem' }}>{tag}</span>
          ))}
        </div>
      </div>

      {/* ── ARCHITECTURE DIAGRAM ─────────────────────────────────────────── */}
      <div className="card" style={{ marginBottom:'1.25rem' }}>
        <div style={{ fontWeight:700, color:'var(--accent)', marginBottom:'1rem', fontSize:'0.9rem' }}>
          🏗️ Hierarchical Multi-Agent Architecture
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:14 }}>
          {AGENTS.map((a, i) => (
            <div key={a.key} style={{ background:`${a.color}0d`,
              border:`1px solid ${a.color}35`, borderRadius:12,
              padding:'0.85rem 0.75rem', textAlign:'center', position:'relative' }}>
              <div style={{ position:'absolute', top:-1, left:'50%', transform:'translateX(-50%)',
                background: a.color, color:'#000', fontSize:'0.55rem', fontWeight:900,
                padding:'1px 7px', borderRadius:'0 0 6px 6px', letterSpacing:'0.04em' }}>
                AGENT {i+1}
              </div>
              <div style={{ fontSize:'1.6rem', margin:'10px 0 6px' }}>{a.icon}</div>
              <div style={{ fontSize:'0.65rem', fontWeight:700, color: a.color, marginBottom:3, lineHeight:1.3 }}>
                {a.key.replace(' Agent', '')}
              </div>
              <div style={{ fontSize:'0.6rem', color:'#484f58', lineHeight:1.4, marginBottom:5 }}>
                {a.desc.split(' · ')[0]}
              </div>
              <div style={{ display:'inline-block', background:`${a.color}20`,
                color: a.color, fontWeight:900, fontSize:'0.72rem',
                padding:'2px 8px', borderRadius:20 }}>
                {a.weight}%
              </div>
            </div>
          ))}
        </div>
        {/* Arrow + Orchestrator */}
        <div style={{ display:'flex', alignItems:'center', gap:12, justifyContent:'center' }}>
          <div style={{ flex:1, height:1, background:'linear-gradient(90deg,transparent,#a855f740)' }}/>
          <div style={{ fontSize:'1rem', color:'#a855f7' }}>⬇️</div>
          <div style={{ background:'linear-gradient(135deg,rgba(168,85,247,0.15),rgba(0,212,255,0.08))',
            border:'1.5px solid rgba(168,85,247,0.4)', borderRadius:10,
            padding:'8px 24px', textAlign:'center' }}>
            <div style={{ fontSize:'0.65rem', color:'#a855f7', fontWeight:700,
              letterSpacing:'0.06em', textTransform:'uppercase' }}>
              Agent 6 — Orchestrator
            </div>
            <div style={{ fontSize:'0.78rem', color:'var(--text-primary)', fontWeight:600, marginTop:2 }}>
              Weighted Synthesis → <span style={{ color:'#a855f7' }}>INVEST / EXIT Decision</span>
            </div>
          </div>
          <div style={{ flex:1, height:1, background:'linear-gradient(90deg,#a855f740,transparent)' }}/>
        </div>
      </div>

      {/* ── INPUT FORM ────────────────────────────────────────────────────── */}
      <div className="card" style={{ marginBottom:'1.25rem' }}>
        <div style={{ fontWeight:700, color:'var(--accent)', marginBottom:'0.9rem', fontSize:'0.9rem' }}>
          📝 IPO Input Parameters
        </div>

        {/* Sample loaders */}
        <div style={{ marginBottom:'1rem' }}>
          <div style={{ fontSize:'0.68rem', color:'#484f58', marginBottom:6,
            textTransform:'uppercase', letterSpacing:'0.06em' }}>
            Quick Load Sample IPO
          </div>
          <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
            {SAMPLE_IPOS.map(s => (
              <button key={s.label} onClick={() => loadSample(s)}
                className="btn btn-secondary"
                style={{ fontSize:'0.75rem', padding:'6px 14px', borderRadius:24 }}>
                <span style={{ fontWeight:700 }}>{s.label}</span>
                <span style={{ color:'#484f58', marginLeft:5, fontSize:'0.65rem' }}>
                  {s.tag}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Form grid — 3 columns */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'0.85rem',
          marginBottom:'1rem' }}>
          {[
            { k:'ipo_name',         label:'IPO / Company Name *',    ph:'e.g. Bajaj Housing Finance', t:'text'   },
            { k:'symbol',           label:'NSE Symbol *',             ph:'e.g. BAJAJHFL.NS',           t:'text'   },
            { k:'issue_price',      label:'Issue Price (₹) *',        ph:'e.g. 70',                    t:'number' },
            { k:'listing_price',    label:'Listing Price (₹) *',      ph:'e.g. 150',                   t:'number' },
            { k:'current_price',    label:'Current Price (₹)',         ph:'0 = auto-fetch from Yahoo',  t:'number' },
            { k:'sub_total',        label:'Total Subscription (×)',    ph:'e.g. 67.4',                  t:'number' },
            { k:'sub_qib',          label:'QIB Subscription (×)',      ph:'e.g. 208',                   t:'number' },
            { k:'sub_retail',       label:'Retail Subscription (×)',   ph:'e.g. 31.5',                  t:'number' },
            { k:'listing_date_str', label:'Listing Date',              ph:'YYYY-MM-DD',                 t:'date'   },
          ].map(f => (
            <div key={f.k}>
              <label>{f.label}</label>
              <input type={f.t} value={form[f.k]}
                onChange={e => upd(f.k, e.target.value)}
                placeholder={f.ph}
                style={{ width:'100%', boxSizing:'border-box' }}/>
            </div>
          ))}
        </div>

        <button onClick={runAnalysis} disabled={running}
          className="btn btn-primary"
          style={{ width:'100%', padding:'14px', fontSize:'1rem', fontWeight:700 }}>
          {running
            ? <><div className="spinner-sm"/> Running 6-agent IPO analysis with Groq Llama 3.3 70B…</>
            : '🚀 Run 6-Agent IPO Analysis'}
        </button>
      </div>

      {/* ── PROGRESS ─────────────────────────────────────────────────────── */}
      {step === 'running' && (
        <div className="card" style={{ marginBottom:'1.25rem' }}>
          <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center',
            marginBottom:8 }}>
            <span style={{ fontSize:'0.82rem', color:'var(--accent)', fontWeight:600 }}>
              {progMsg}
            </span>
            <span style={{ fontSize:'0.82rem', color:'#484f58', fontWeight:700 }}>
              {progress}%
            </span>
          </div>
          <div style={{ height:8, background:'#1c2128', borderRadius:4, overflow:'hidden',
            marginBottom:'1.25rem' }}>
            <div style={{ height:'100%', width:`${progress}%`, borderRadius:4,
              background:'linear-gradient(90deg,#a855f7,#00d4ff,#00ff88)',
              backgroundSize:'200% 100%',
              transition:'width 1s cubic-bezier(0.4,0,0.2,1)',
              animation:'shimmer 2s linear infinite' }}/>
          </div>
          {/* Inline agent status during run */}
          <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'0.75rem' }}>
            {AGENTS.map(a => <AgentCard key={a.key} agent={a} result={null} isRunning={true}/>)}
          </div>
        </div>
      )}

      {/* ── RESULTS ──────────────────────────────────────────────────────── */}
      {step === 'done' && result && decCfg && (
        <div ref={resultsRef} className="fade-in">

          {/* Decision Banner */}
          <div style={{ background: decCfg.bg, border:`2px solid ${decCfg.color}`,
            borderRadius:16, padding:'2rem', marginBottom:'1.25rem',
            textAlign:'center', boxShadow: decCfg.glow }}>
            <div style={{ fontSize:'2.2rem', fontWeight:900, color: decCfg.color,
              letterSpacing:'0.05em', marginBottom:6 }}>
              {decCfg.label}
            </div>
            <div style={{ color:'var(--text-secondary)', fontSize:'0.9rem',
              marginBottom:'1.5rem' }}>
              {decCfg.sub}
            </div>

            {/* KPI strip */}
            <div style={{ display:'flex', justifyContent:'center', gap:'3rem',
              flexWrap:'wrap' }}>
              {[
                { label:'Overall Score',   val:`${result.overall_score}/100`, color: decCfg.color    },
                { label:'Confidence',      val:`${result.confidence}%`,       color:'#00d4ff'         },
                { label:'Target Price',    val:`₹${(result.target_price||0).toLocaleString('en-IN')}`, color:'#00ff88' },
                { label:'Stop Loss',       val:`₹${(result.stop_loss||0).toLocaleString('en-IN')}`,   color:'#ff4757' },
                { label:'Risk Level',      val: result.risk_level,
                  color: result.risk_level==='LOW'?'#00ff88':result.risk_level==='MEDIUM'?'#ffa502':'#ff4757' },
                { label:'Holding Period',  val: result.holding_period,        color:'#a855f7'         },
              ].map(m => (
                <div key={m.label} style={{ textAlign:'center' }}>
                  <div style={{ fontSize:'0.62rem', color:'#484f58', textTransform:'uppercase',
                    letterSpacing:'0.06em', marginBottom:3 }}>{m.label}</div>
                  <div style={{ fontWeight:900, color:m.color, fontSize:'1.1rem' }}>{m.val}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Result Tabs */}
          <div className="tab-bar" style={{ marginBottom:'1.25rem' }}>
            {TABS.map(t => (
              <button key={t.id} className={`tab ${tab===t.id?'active':''}`}
                onClick={() => setTab(t.id)}>
                {t.label}
              </button>
            ))}
          </div>

          {/* ── TAB: OVERVIEW ─────────────────────────────────────────── */}
          {tab === 'overview' && (
            <div className="fade-in">
              {/* Score Gauge + Weights + KPIs */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr',
                gap:'1rem', marginBottom:'1.25rem' }}>

                {/* Gauge */}
                <div className="card">
                  <PlotlyChart data={gaugeData}
                    layout={{ height:220, margin:{t:40,b:10,l:20,r:20} }}/>
                </div>

                {/* Agent weights donut */}
                <div className="card">
                  <PlotlyChart data={weightsData}
                    layout={{ title:{text:'Agent Weights',font:{color:'#8b949e',size:12}},
                      height:220, margin:{t:35,b:5,l:5,r:5}, showlegend:false,
                      annotations:[{text:'Weights',x:0.5,y:0.5,showarrow:false,
                        font:{color:'#484f58',size:11}}] }}/>
                </div>

                {/* Quick KPIs */}
                <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                  {[
                    { label:'Final Decision', val: result.final_decision.replace('_',' '), color: decCfg.color, icon:'🎯' },
                    { label:'Confidence',     val: `${result.confidence}%`,                color:'#00d4ff',      icon:'📊' },
                    { label:'Risk Level',     val: result.risk_level,
                      color: result.risk_level==='LOW'?'#00ff88':result.risk_level==='MEDIUM'?'#ffa502':'#ff4757', icon:'🛡️' },
                    { label:'Holding Period', val: result.holding_period,                   color:'#a855f7',      icon:'📅' },
                  ].map(k => (
                    <KPICard key={k.label} {...k}/>
                  ))}
                </div>
              </div>

              {/* Investment Thesis */}
              {result.investment_thesis && result.investment_thesis !== 'N/A' && (
                <div style={{ background:'linear-gradient(135deg,rgba(168,85,247,0.08),rgba(0,212,255,0.04))',
                  border:'1px solid rgba(168,85,247,0.25)', borderRadius:14,
                  padding:'1.5rem', marginBottom:'1.25rem' }}>
                  <div style={{ fontWeight:700, color:'#a855f7', marginBottom:'0.75rem',
                    fontSize:'0.9rem', display:'flex', alignItems:'center', gap:8 }}>
                    🧠 Investment Thesis
                    <span className="badge badge-purple" style={{ fontSize:'0.62rem' }}>
                      Groq Llama 3.3 70B
                    </span>
                  </div>
                  <div style={{ fontSize:'0.875rem', color:'var(--text-primary)',
                    lineHeight:1.85, whiteSpace:'pre-wrap' }}>
                    {result.investment_thesis}
                  </div>
                </div>
              )}

              {/* Entry + Exit strategy */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr',
                gap:'1rem', marginBottom:'1.25rem' }}>
                <div className="card" style={{ borderLeft:'3px solid #00ff88' }}>
                  <div style={{ fontWeight:700, color:'#00ff88', marginBottom:8,
                    display:'flex', alignItems:'center', gap:6 }}>
                    📈 Entry Strategy
                  </div>
                  <div style={{ fontSize:'0.85rem', color:'var(--text-primary)', lineHeight:1.75 }}>
                    {result.entry_strategy || 'N/A'}
                  </div>
                </div>
                <div className="card" style={{ borderLeft:'3px solid #ff4757' }}>
                  <div style={{ fontWeight:700, color:'#ff4757', marginBottom:8,
                    display:'flex', alignItems:'center', gap:6 }}>
                    📤 Exit Strategy
                  </div>
                  <div style={{ fontSize:'0.85rem', color:'var(--text-primary)', lineHeight:1.75 }}>
                    {result.exit_strategy || 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ── TAB: AGENT RESULTS ────────────────────────────────────── */}
          {tab === 'agents' && (
            <div className="fade-in">
              <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)',
                gap:'0.85rem', marginBottom:'1.25rem' }}>
                {AGENTS.map(a => (
                  <AgentCard key={a.key} agent={a}
                    result={agentData.find(d => d.key === a.key) || null}
                    isRunning={false}/>
                ))}
              </div>

              {/* Detailed scores table */}
              <div className="card">
                <div style={{ fontWeight:700, color:'var(--accent)', marginBottom:'0.75rem',
                  fontSize:'0.88rem' }}>
                  📋 Agent Score Summary
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        {['Agent','Weight','Score','Signal','Confidence','Status'].map(h => (
                          <th key={h}>{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {AGENTS.map(a => {
                        const d = agentData.find(x => x.key === a.key);
                        const sc = d?.score ?? 50;
                        const status = sc>=65?'Good':sc>=45?'Neutral':'Weak';
                        const sc_color = sc>=65?'#00ff88':sc>=45?'#ffa502':'#ff4757';
                        return (
                          <tr key={a.key}>
                            <td><span style={{color:a.color,fontWeight:700}}>
                              {a.icon} {a.key}
                            </span></td>
                            <td><span style={{color:a.color,fontWeight:700}}>{a.weight}%</span></td>
                            <td>
                              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                                <div style={{ flex:1, height:6, background:'#1c2128',
                                  borderRadius:3, overflow:'hidden', minWidth:60 }}>
                                  <div style={{ height:'100%', width:`${sc}%`,
                                    background:a.color, borderRadius:3 }}/>
                                </div>
                                <span style={{ color:sc_color, fontWeight:700, fontSize:'0.82rem' }}>
                                  {sc}
                                </span>
                              </div>
                            </td>
                            <td><SignalBadge signal={d?.signal||'N/A'}/></td>
                            <td style={{ color:'var(--text-secondary)' }}>{d?.confidence||'—'}%</td>
                            <td>
                              <span style={{ color:sc_color, fontSize:'0.75rem', fontWeight:600 }}>
                                {status}
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                      {/* Weighted total row */}
                      <tr style={{ background:'rgba(0,212,255,0.04)',
                        borderTop:'2px solid var(--border)' }}>
                        <td style={{ fontWeight:700, color:'var(--accent)' }}>
                          🎯 Orchestrator (Weighted)
                        </td>
                        <td style={{ color:'#484f58' }}>100%</td>
                        <td>
                          <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                            <div style={{ flex:1, height:6, background:'#1c2128',
                              borderRadius:3, overflow:'hidden', minWidth:60 }}>
                              <div style={{ height:'100%',
                                width:`${result.overall_score}%`,
                                background: decCfg.color, borderRadius:3 }}/>
                            </div>
                            <span style={{ color: decCfg.color, fontWeight:900, fontSize:'0.9rem' }}>
                              {result.overall_score}
                            </span>
                          </div>
                        </td>
                        <td>
                          <span style={{ background: `${decCfg.color}20`, color: decCfg.color,
                            border:`1px solid ${decCfg.color}40`, borderRadius:6,
                            padding:'3px 9px', fontSize:'0.72rem', fontWeight:800 }}>
                            {result.final_decision.replace('_',' ')}
                          </span>
                        </td>
                        <td style={{ color: decCfg.color, fontWeight:800 }}>
                          {result.confidence}%
                        </td>
                        <td>
                          <span style={{ color: decCfg.color, fontSize:'0.75rem', fontWeight:700 }}>
                            Final
                          </span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ── TAB: CHARTS ───────────────────────────────────────────── */}
          {tab === 'charts' && (
            <div className="fade-in">
              {/* Row 1: Radar + Horizontal Bar */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr',
                gap:'1rem', marginBottom:'1rem' }}>
                <div className="card">
                  <PlotlyChart data={radarData}
                    layout={{ title:{text:'Agent Score Radar',font:{color:'#8b949e',size:13}},
                      height:360, margin:{l:40,r:40,t:50,b:30},
                      polar:{ bgcolor:'#0d1117',
                        radialaxis:{ range:[0,100], visible:true, tickfont:{color:'#484f58',size:9},
                          gridcolor:'#21262d', linecolor:'#21262d' },
                        angularaxis:{ tickfont:{color:'#8b949e',size:10}, gridcolor:'#21262d',
                          linecolor:'#21262d' } } }}/>
                </div>
                <div className="card">
                  <PlotlyChart data={barData}
                    layout={{ title:{text:'Agent Scores vs INVEST Threshold',font:{color:'#8b949e',size:13}},
                      height:360, margin:{l:130,r:60,t:50,b:30},
                      xaxis:{ range:[0,115], title:{text:'Score',font:{color:'#484f58'}},
                        showgrid:true, gridcolor:'#21262d' },
                      yaxis:{ showgrid:false },
                      shapes:[{ type:'line', x0:65, x1:65, y0:-0.5,
                        y1:AGENTS.length-0.5, line:{color:'rgba(0,255,136,0.4)',
                        dash:'dot',width:2} }],
                      annotations:[{ x:65, y:AGENTS.length-0.5, text:'INVEST',
                        showarrow:false, font:{color:'#00ff88',size:10},
                        xanchor:'left', xshift:5 }] }}/>
                </div>
              </div>

              {/* Row 2: Gauge + Weights */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr',
                gap:'1rem', marginBottom:'1rem' }}>
                <div className="card">
                  <PlotlyChart data={gaugeData}
                    layout={{ height:280, margin:{t:60,b:20,l:30,r:30} }}/>
                </div>
                <div className="card">
                  <PlotlyChart data={weightsData}
                    layout={{ title:{text:'Agent Weight Distribution',font:{color:'#8b949e',size:13}},
                      height:280, margin:{t:50,b:10,l:10,r:10}, showlegend:true,
                      legend:{font:{color:'#8b949e',size:10},
                        orientation:'v', x:1.05} }}/>
                </div>
              </div>
            </div>
          )}

          {/* ── TAB: STRATEGY ─────────────────────────────────────────── */}
          {tab === 'strategy' && (
            <div className="fade-in">
              {/* Trade setup cards */}
              <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)',
                gap:'0.85rem', marginBottom:'1.25rem' }}>
                {[
                  { label:'Target Price',   val:`₹${(result.target_price||0).toLocaleString('en-IN')}`, color:'#00ff88', icon:'🎯', sub:'3-6 month target' },
                  { label:'Stop Loss',      val:`₹${(result.stop_loss||0).toLocaleString('en-IN')}`,   color:'#ff4757', icon:'🛑', sub:'Hard stop-loss' },
                  { label:'Risk Level',     val: result.risk_level,
                    color: result.risk_level==='LOW'?'#00ff88':result.risk_level==='MEDIUM'?'#ffa502':'#ff4757',
                    icon:'⚖️', sub:'Risk assessment' },
                  { label:'Holding Period', val: result.holding_period, color:'#a855f7', icon:'📅', sub:'Suggested duration' },
                ].map(k => <KPICard key={k.label} {...k}/>)}
              </div>

              {/* Entry and exit */}
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr',
                gap:'1rem', marginBottom:'1.25rem' }}>
                <div className="card" style={{ borderLeft:'3px solid #00ff88' }}>
                  <div style={{ fontWeight:700, color:'#00ff88', marginBottom:10,
                    fontSize:'0.9rem', display:'flex', alignItems:'center', gap:6 }}>
                    📈 Entry Strategy
                  </div>
                  <div style={{ fontSize:'0.875rem', color:'var(--text-primary)',
                    lineHeight:1.8 }}>
                    {result.entry_strategy || 'N/A'}
                  </div>
                </div>
                <div className="card" style={{ borderLeft:'3px solid #ff4757' }}>
                  <div style={{ fontWeight:700, color:'#ff4757', marginBottom:10,
                    fontSize:'0.9rem', display:'flex', alignItems:'center', gap:6 }}>
                    📤 Exit Strategy
                  </div>
                  <div style={{ fontSize:'0.875rem', color:'var(--text-primary)',
                    lineHeight:1.8 }}>
                    {result.exit_strategy || 'N/A'}
                  </div>
                </div>
              </div>

              {/* Investment Thesis */}
              {result.investment_thesis && result.investment_thesis !== 'N/A' && (
                <div style={{ background:'linear-gradient(135deg,rgba(168,85,247,0.08),rgba(0,212,255,0.04))',
                  border:'1px solid rgba(168,85,247,0.25)', borderRadius:14,
                  padding:'1.5rem' }}>
                  <div style={{ fontWeight:700, color:'#a855f7', marginBottom:'0.75rem',
                    fontSize:'0.9rem', display:'flex', alignItems:'center', gap:8 }}>
                    🧠 Investment Thesis
                    <span className="badge badge-purple" style={{ fontSize:'0.62rem' }}>
                      Orchestrator Agent · Groq Llama 3.3 70B
                    </span>
                  </div>
                  <div style={{ fontSize:'0.875rem', color:'var(--text-primary)',
                    lineHeight:1.85, whiteSpace:'pre-wrap' }}>
                    {result.investment_thesis}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── TAB: RISKS & CATALYSTS ────────────────────────────────── */}
          {tab === 'risks' && (
            <div className="fade-in">
              <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)',
                gap:'1rem', marginBottom:'1.25rem' }}>
                <ListSection title="Key Risks" items={result.key_risks}
                  color="#ff4757" icon="⚠️"/>
                <ListSection title="Key Catalysts" items={result.key_catalysts}
                  color="#00ff88" icon="🚀"/>
                <ListSection title="Monitor Triggers" items={result.monitoring_triggers}
                  color="#ffa502" icon="📡"/>
              </div>
            </div>
          )}

          {/* Framework footer */}
          <div style={{ background:'#080c12', border:'1px solid #1c2128',
            borderRadius:10, padding:'0.9rem 1.25rem', marginTop:'0.75rem',
            display:'flex', justifyContent:'space-between', flexWrap:'wrap',
            gap:8, fontSize:'0.7rem', color:'#484f58' }}>
            <span>🤖 <span style={{color:'#8b949e'}}>Groq Llama 3.3 70B</span></span>
            <span>🏗️ <span style={{color:'#8b949e'}}>6-Agent Hierarchical System</span></span>
            <span>📊 <span style={{color:'#8b949e'}}>Price(20%) + Macro(15%) + Sentiment(20%) + Risk(20%) + IPO(25%)</span></span>
            <span>⏱️ <span style={{color:'#8b949e'}}>{new Date(result.timestamp).toLocaleString('en-IN')}</span></span>
          </div>
          <div style={{ textAlign:'center', fontSize:'0.68rem', color:'#484f58',
            padding:'0.6rem 0' }}>
            ⚠️ Educational purposes only. Not financial advice.
            Consult a SEBI-registered investment advisor before investing.
          </div>
        </div>
      )}
    </div>
  );
}
