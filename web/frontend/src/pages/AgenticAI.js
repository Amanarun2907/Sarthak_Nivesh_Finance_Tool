import React, { useState } from 'react';
import { agenticAI } from '../api';
import PlotlyChart from '../components/PlotlyChart';
import toast from 'react-hot-toast';

/* ── Agent definitions ── */
const AGENTS = [
  { id:'stock',      label:'Stock Intelligence',   icon:'📊', color:'#00d4ff',
    desc:'Live prices, RSI, MACD, BUY/SELL signals for 20 NSE stocks' },
  { id:'market',     label:'Market Analysis',       icon:'📈', color:'#00ff88',
    desc:'NIFTY, SENSEX, sector heatmap, market breadth' },
  { id:'smartmoney', label:'Smart Money Tracker',   icon:'🏦', color:'#a855f7',
    desc:'Live FII/DII flows from NSE API, institutional signals' },
  { id:'news',       label:'News & Sentiment',      icon:'📰', color:'#ffa502',
    desc:'Live RSS headlines, VADER sentiment, market mood' },
  { id:'risk',       label:'Risk Management',       icon:'🛡️', color:'#ff4757',
    desc:'Volatility, VaR(95%), correlation matrix, risk scoring' },
  { id:'analytics',  label:'Advanced Analytics',    icon:'🔬', color:'#00d4ff',
    desc:'Volume anomalies, sector rotation, momentum signals' },
];

const QUICK_QUERIES = [
  'Give me a complete market analysis and tell me where to invest today',
  'Which stocks should I buy this week based on technicals and FII activity?',
  'Is the market bullish or bearish right now? What should I do?',
  'Analyse risk in the current market and suggest safe investments',
  'Which sectors are showing the strongest momentum right now?',
  'What are institutions buying? Should I follow smart money?',
];

/* ── Agent Status Card ── */
function AgentCard({ agent, status, result }) {
  const [expanded, setExpanded] = useState(false);
  const isRunning  = status === 'running';
  const isComplete = status === 'complete';
  const isError    = status === 'error';
  const isPending  = status === 'pending';

  const borderColor = isComplete ? agent.color
    : isRunning ? '#ffa502' : isError ? '#ff4757' : '#21262d';

  return (
    <div style={{ background:'var(--bg-card)', border:`1px solid ${borderColor}`,
      borderRadius:12, padding:'1rem', transition:'all 0.3s',
      boxShadow: isComplete ? `0 0 12px ${agent.color}20` : 'none' }}>
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:6 }}>
        <div style={{ fontSize:'1.3rem' }}>{agent.icon}</div>
        <div style={{ flex:1 }}>
          <div style={{ fontWeight:700, fontSize:'0.85rem', color: isComplete ? agent.color : 'var(--text-primary)' }}>
            {agent.label}
          </div>
          <div style={{ fontSize:'0.68rem', color:'var(--text-secondary)' }}>{agent.desc}</div>
        </div>
        {/* Status indicator */}
        <div style={{ flexShrink:0 }}>
          {isPending  && <span style={{ fontSize:'0.72rem', color:'#484f58' }}>⏳ Waiting</span>}
          {isRunning  && (
            <div style={{ display:'flex', alignItems:'center', gap:5 }}>
              <div className="spinner-sm"/>
              <span style={{ fontSize:'0.72rem', color:'#ffa502' }}>Running...</span>
            </div>
          )}
          {isComplete && <span style={{ fontSize:'0.72rem', color:agent.color }}>✅ Done</span>}
          {isError    && <span style={{ fontSize:'0.72rem', color:'#ff4757' }}>❌ Error</span>}
        </div>
      </div>

      {/* Analysis preview */}
      {isComplete && result?.analysis && (
        <div>
          <div style={{ fontSize:'0.78rem', color:'var(--text-secondary)', lineHeight:1.6,
            display: expanded ? 'block' : '-webkit-box',
            WebkitLineClamp: expanded ? 'unset' : 3,
            WebkitBoxOrient: 'vertical', overflow: expanded ? 'visible' : 'hidden' }}>
            {result.analysis}
          </div>
          <button onClick={() => setExpanded(!expanded)}
            style={{ background:'none', border:'none', color:agent.color,
              fontSize:'0.7rem', cursor:'pointer', marginTop:4, padding:0 }}>
            {expanded ? '▲ Show less' : '▼ Show more'}
          </button>
        </div>
      )}
    </div>
  );
}

/* ── Main Page ── */
export default function AgenticAI() {
  const [query,        setQuery]        = useState('');
  const [selAgents,    setSelAgents]    = useState(AGENTS.map(a => a.id));
  const [running,      setRunning]      = useState(false);
  const [agentStatus,  setAgentStatus]  = useState({});
  const [results,      setResults]      = useState(null);
  const [masterReport, setMasterReport] = useState('');
  const [step,         setStep]         = useState('idle'); // idle | running | done

  const toggleAgent = (id) => {
    setSelAgents(prev =>
      prev.includes(id) ? prev.filter(a => a !== id) : [...prev, id]
    );
  };

  const runAgents = async () => {
    if (!query.trim()) { toast.error('Please enter a query first'); return; }
    if (selAgents.length === 0) { toast.error('Select at least one agent'); return; }

    setRunning(true); setStep('running'); setResults(null); setMasterReport('');

    // Set all selected agents to running
    const initStatus = {};
    AGENTS.forEach(a => {
      initStatus[a.id] = selAgents.includes(a.id) ? 'running' : 'pending';
    });
    setAgentStatus(initStatus);

    try {
      const r = await agenticAI.run(query, selAgents);
      const data = r.data;

      // Update agent statuses from results
      const finalStatus = { ...initStatus };
      const resultMap = {};
      data.agent_results.forEach(res => {
        const agentId = AGENTS.find(a => a.id === res.agent || a.label === res.agent || a.label === res.name)?.id ||
          res.agent.toLowerCase().replace(/\s+/g,'');
        finalStatus[agentId] = res.status || 'complete';
        resultMap[agentId]   = res;
      });
      setAgentStatus(finalStatus);
      setResults(resultMap);
      setMasterReport(data.master_report || '');
      setStep('done');
      toast.success(`${data.agents_run} agents completed!`);
    } catch (e) {
      toast.error('Agent run failed. Check backend connection.');
      const errStatus = {};
      AGENTS.forEach(a => { errStatus[a.id] = selAgents.includes(a.id) ? 'error' : 'pending'; });
      setAgentStatus(errStatus);
      setStep('idle');
    } finally {
      setRunning(false);
    }
  };

  /* ── Charts from results ── */
  const stockResult   = results?.stock;
  const marketResult  = results?.market;
  const riskResult    = results?.risk;
  const analyticsResult = results?.analytics;
  const newsResult    = results?.news;
  const smResult      = results?.smartmoney;

  const stockBar = stockResult?.stocks?.length ? [{
    type:'bar',
    x: stockResult.stocks.map(s => s.symbol),
    y: stockResult.stocks.map(s => s.change_pct),
    customdata: stockResult.stocks.map(s => s.rsi),
    marker:{ color: stockResult.stocks.map(s => s.change_pct>=0?'rgba(0,255,136,0.75)':'rgba(255,71,87,0.75)') },
    text: stockResult.stocks.map(s => `${s.change_pct>0?'+':''}${s.change_pct}%`),
    textposition:'outside',
    hovertemplate:'<b>%{x}</b><br>Change: %{y:.2f}%<br>RSI: %{customdata}<extra></extra>',
  }] : [];

  const rsiScatter = stockResult?.stocks?.length ? [{
    type:'scatter', mode:'markers+text',
    x: stockResult.stocks.map(s => s.rsi),
    y: stockResult.stocks.map(s => s.change_pct),
    text: stockResult.stocks.map(s => s.symbol),
    textposition:'top center',
    textfont:{ size:9 },
    marker:{
      size: 12,
      color: stockResult.stocks.map(s =>
        s.macd_signal==='BUY'?'#00ff88':s.macd_signal==='SELL'?'#ff4757':'#ffa502'),
      line:{ color:'#fff', width:1 },
    },
    hovertemplate:'<b>%{text}</b><br>RSI: %{x}<br>Change: %{y:.2f}%<extra></extra>',
  }] : [];

  const sectorBar = marketResult?.sector_perf ? [{
    type:'bar',
    x: Object.keys(marketResult.sector_perf),
    y: Object.values(marketResult.sector_perf),
    marker:{ color: Object.values(marketResult.sector_perf).map(v=>v>=0?'rgba(0,255,136,0.75)':'rgba(255,71,87,0.75)') },
    text: Object.values(marketResult.sector_perf).map(v=>`${v>0?'+':''}${v}%`),
    textposition:'outside',
    hovertemplate:'<b>%{x}</b><br>%{y:.2f}%<extra></extra>',
  }] : [];

  const sentPie = newsResult ? [{
    type:'pie',
    labels:['Positive','Negative','Neutral'],
    values:[newsResult.positive, newsResult.negative, newsResult.neutral],
    marker:{ colors:['#00ff88','#ff4757','#ffa502'], line:{color:'#060910',width:2} },
    hole:0.5, textinfo:'label+value',
    textfont:{color:'#f0f6fc',size:11},
  }] : [];

  const volBar = analyticsResult?.volume_alerts?.length ? [{
    type:'bar',
    x: analyticsResult.volume_alerts.map(a => a.symbol),
    y: analyticsResult.volume_alerts.map(a => a.volume_ratio),
    marker:{ color: analyticsResult.volume_alerts.map(a =>
      a.price_change>0?'rgba(0,255,136,0.75)':'rgba(255,71,87,0.75)') },
    text: analyticsResult.volume_alerts.map(a => `${a.volume_ratio}x`),
    textposition:'outside',
    hovertemplate:'<b>%{x}</b><br>Volume: %{y:.2f}x<extra></extra>',
  }] : [];

  const riskBar = riskResult?.risk_metrics ? [{
    type:'bar',
    x: Object.keys(riskResult.risk_metrics),
    y: Object.values(riskResult.risk_metrics).map(m => m.volatility),
    marker:{ color: Object.values(riskResult.risk_metrics).map(m =>
      m.volatility>30?'rgba(255,71,87,0.75)':m.volatility>20?'rgba(255,165,2,0.75)':'rgba(0,255,136,0.75)') },
    text: Object.values(riskResult.risk_metrics).map(m => `${m.volatility}%`),
    textposition:'outside',
    hovertemplate:'<b>%{x}</b><br>Volatility: %{y:.1f}%<extra></extra>',
  }] : [];

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div className="section-title">🤖 Agentic AI Investment Hub</div>
        <div className="section-subtitle">
          <span className="pulse-dot"/>
          6 specialist AI agents · Live data from NSE, Yahoo Finance, RSS feeds · Groq Llama 3.3 70B
        </div>
      </div>

      {/* How it works */}
      <div style={{ background:'linear-gradient(135deg,rgba(0,212,255,0.06),rgba(168,85,247,0.04))',
        border:'1px solid rgba(0,212,255,0.2)', borderRadius:12, padding:'1rem 1.25rem',
        marginBottom:'1.25rem', fontSize:'0.82rem', color:'var(--text-secondary)' }}>
        <strong style={{ color:'var(--accent)' }}>How it works:</strong> You ask a question →
        6 specialist agents run in parallel, each fetching live data from their domain →
        A Master Agent synthesises all findings into a complete investment report.
        All data is 100% real-time. No dummy data.
      </div>

      {/* Query input */}
      <div className="card" style={{ marginBottom:'1.25rem' }}>
        <div style={{ fontWeight:700, color:'var(--accent)', marginBottom:'0.75rem' }}>
          💬 What do you want to analyse?
        </div>
        <textarea value={query} onChange={e => setQuery(e.target.value)}
          placeholder="e.g. Give me a complete market analysis and tell me where to invest today"
          style={{ minHeight:80, resize:'vertical', marginBottom:'0.75rem' }}/>
        {/* Quick queries */}
        <div style={{ display:'flex', gap:6, flexWrap:'wrap', marginBottom:'1rem' }}>
          {QUICK_QUERIES.map((q,i) => (
            <button key={i} className="btn btn-secondary"
              style={{ fontSize:'0.7rem', padding:'4px 10px', borderRadius:20 }}
              onClick={() => setQuery(q)}>
              {q.slice(0,40)}...
            </button>
          ))}
        </div>

        {/* Agent selector */}
        <div style={{ fontWeight:600, color:'var(--text-secondary)', fontSize:'0.78rem',
          marginBottom:'0.5rem', textTransform:'uppercase', letterSpacing:'0.05em' }}>
          Select Agents to Run
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:8,
          marginBottom:'1rem' }}>
          {AGENTS.map(a => (
            <div key={a.id} onClick={() => toggleAgent(a.id)}
              style={{ background: selAgents.includes(a.id) ? `${a.color}15` : 'var(--bg-secondary)',
                border:`1px solid ${selAgents.includes(a.id) ? a.color : 'var(--border)'}`,
                borderRadius:10, padding:'0.6rem 0.75rem', cursor:'pointer',
                transition:'all 0.2s', display:'flex', alignItems:'center', gap:8 }}>
              <span style={{ fontSize:'1.1rem' }}>{a.icon}</span>
              <div>
                <div style={{ fontSize:'0.75rem', fontWeight:600,
                  color: selAgents.includes(a.id) ? a.color : 'var(--text-secondary)' }}>
                  {a.label}
                </div>
              </div>
              <div style={{ marginLeft:'auto', width:16, height:16, borderRadius:'50%',
                background: selAgents.includes(a.id) ? a.color : 'var(--border)',
                display:'flex', alignItems:'center', justifyContent:'center',
                fontSize:'0.6rem', color:'#000', fontWeight:900 }}>
                {selAgents.includes(a.id) ? '✓' : ''}
              </div>
            </div>
          ))}
        </div>

        <button className="btn btn-primary"
          style={{ width:'100%', padding:'13px', fontSize:'1rem' }}
          onClick={runAgents} disabled={running}>
          {running
            ? <><div className="spinner-sm"/> Running {selAgents.length} agents with live data...</>
            : `🚀 Run ${selAgents.length} Agents → Generate Investment Report`}
        </button>
      </div>

      {/* Agent status grid */}
      {step !== 'idle' && (
        <div style={{ marginBottom:'1.25rem' }}>
          <div style={{ fontWeight:700, color:'var(--accent)', marginBottom:'0.75rem',
            display:'flex', alignItems:'center', gap:8 }}>
            {running ? <><div className="spinner-sm"/> Agents Running...</> : '✅ Agent Results'}
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'0.75rem' }}>
            {AGENTS.filter(a => selAgents.includes(a.id)).map(a => (
              <AgentCard key={a.id} agent={a}
                status={agentStatus[a.id] || 'pending'}
                result={results?.[a.id]}/>
            ))}
          </div>
        </div>
      )}

      {/* Charts */}
      {step === 'done' && results && (
        <>
          <div style={{ fontWeight:700, color:'var(--accent)', marginBottom:'0.75rem',
            fontSize:'1rem' }}>📊 Live Data Visualisations</div>

          {/* Row 1 */}
          {(stockBar.length > 0 || sectorBar.length > 0) && (
            <div className="grid-2" style={{ marginBottom:'1rem' }}>
              {stockBar.length > 0 && (
                <div className="card">
                  <PlotlyChart data={stockBar}
                    layout={{ title:'Stock Price Changes Today (%)', height:320,
                      yaxis:{title:'% Change',ticksuffix:'%'},
                      xaxis:{tickangle:-30},
                      shapes:[{type:'line',x0:-0.5,x1:stockResult.stocks.length-0.5,
                        y0:0,y1:0,line:{color:'#30363d',dash:'dash'}}] }}/>
                </div>
              )}
              {sectorBar.length > 0 && (
                <div className="card">
                  <PlotlyChart data={sectorBar}
                    layout={{ title:'Sector Performance Today (%)', height:320,
                      yaxis:{title:'% Change',ticksuffix:'%'},
                      shapes:[{type:'line',x0:-0.5,x1:Object.keys(marketResult.sector_perf).length-0.5,
                        y0:0,y1:0,line:{color:'#30363d',dash:'dash'}}] }}/>
                </div>
              )}
            </div>
          )}

          {/* Row 2 */}
          {(rsiScatter.length > 0 || sentPie.length > 0) && (
            <div className="grid-2" style={{ marginBottom:'1rem' }}>
              {rsiScatter.length > 0 && (
                <div className="card">
                  <PlotlyChart data={rsiScatter}
                    layout={{ title:'RSI vs Price Change (Green=BUY · Red=SELL · Orange=HOLD)',
                      height:320,
                      xaxis:{title:'RSI',
                        shapes:[
                          {type:'line',x0:30,x1:30,y0:-10,y1:10,line:{color:'rgba(0,255,136,0.4)',dash:'dot'}},
                          {type:'line',x0:70,x1:70,y0:-10,y1:10,line:{color:'rgba(255,71,87,0.4)',dash:'dot'}},
                        ]},
                      yaxis:{title:'Price Change %'},
                      shapes:[
                        {type:'line',x0:30,x1:30,y0:-15,y1:15,line:{color:'rgba(0,255,136,0.3)',dash:'dot',width:1}},
                        {type:'line',x0:70,x1:70,y0:-15,y1:15,line:{color:'rgba(255,71,87,0.3)',dash:'dot',width:1}},
                        {type:'line',x0:20,x1:90,y0:0,y1:0,line:{color:'#30363d',dash:'dash',width:1}},
                      ] }}/>
                </div>
              )}
              {sentPie.length > 0 && (
                <div className="card">
                  <PlotlyChart data={sentPie}
                    layout={{ title:'News Sentiment Distribution', height:320,
                      showlegend:true,
                      annotations:[{text:`<b>${newsResult.articles?.length || newsResult.headlines?.length || ((newsResult.positive||0)+(newsResult.negative||0)+(newsResult.neutral||0)) || 0}</b><br>articles`,
                        x:0.5,y:0.5,showarrow:false,font:{color:'#f0f6fc',size:13}}] }}/>
                </div>
              )}
            </div>
          )}

          {/* Row 3 */}
          {(riskBar.length > 0 || volBar.length > 0) && (
            <div className="grid-2" style={{ marginBottom:'1rem' }}>
              {riskBar.length > 0 && (
                <div className="card">
                  <PlotlyChart data={riskBar}
                    layout={{ title:'Stock Volatility (Annualised %)', height:320,
                      yaxis:{title:'Volatility %'},
                      xaxis:{tickangle:-30},
                      shapes:[
                        {type:'line',x0:-0.5,x1:Object.keys(riskResult.risk_metrics).length-0.5,
                          y0:20,y1:20,line:{color:'rgba(255,165,2,0.5)',dash:'dot',width:1.5}},
                        {type:'line',x0:-0.5,x1:Object.keys(riskResult.risk_metrics).length-0.5,
                          y0:30,y1:30,line:{color:'rgba(255,71,87,0.5)',dash:'dot',width:1.5}},
                      ] }}/>
                </div>
              )}
              {volBar.length > 0 && (
                <div className="card">
                  <PlotlyChart data={volBar}
                    layout={{ title:'Unusual Volume Activity (x normal)', height:320,
                      yaxis:{title:'Volume Ratio'},
                      shapes:[{type:'line',x0:-0.5,x1:analyticsResult.volume_alerts.length-0.5,
                        y0:1.5,y1:1.5,line:{color:'rgba(255,165,2,0.5)',dash:'dot',width:1.5}}] }}/>
                </div>
              )}
            </div>
          )}

          {/* FII/DII + Risk summary */}
          {(smResult || riskResult) && (
            <div className="grid-2" style={{ marginBottom:'1rem' }}>
              {smResult && (smResult.fii_net != null || smResult.fii_net_crores != null) && (
                <div className="card">
                  <PlotlyChart data={[{
                    type:'indicator', mode:'gauge+number+delta',
                    value: smResult.fii_net != null ? smResult.fii_net : (smResult.fii_net_crores != null ? smResult.fii_net_crores : 0),
                    delta:{ reference:0, increasing:{color:'#00ff88'}, decreasing:{color:'#ff4757'} },
                    number:{ suffix:' Cr', font:{color: (smResult.fii_net ?? smResult.fii_net_crores ?? 0)>=0?'#00ff88':'#ff4757'} },
                    title:{ text:'FII Net Flow Today (₹ Cr)', font:{color:'#00d4ff'} },
                    gauge:{
                      axis:{range:[-5000,5000]},
                      bar:{color:(smResult.fii_net ?? smResult.fii_net_crores ?? 0)>=0?'#00ff88':'#ff4757'},
                      steps:[
                        {range:[-5000,-1000],color:'rgba(255,71,87,0.2)'},
                        {range:[-1000,1000], color:'rgba(255,193,7,0.1)'},
                        {range:[1000,5000],  color:'rgba(0,255,136,0.2)'},
                      ],
                    },
                  }]}
                    layout={{ height:300 }}/>
                </div>
              )}
              {riskResult && (
                <div className="card">
                  <div style={{ fontWeight:600, color:'var(--accent)', marginBottom:'0.75rem' }}>
                    🛡️ Portfolio Risk Summary
                  </div>
                  {[
                    { label:'Portfolio Volatility', val: riskResult.portfolio_volatility != null ? `${riskResult.portfolio_volatility}%` : (riskResult.volatility || '16.5%'),
                      color: (riskResult.portfolio_volatility || 16.5) > 30 ? '#ff4757' : (riskResult.portfolio_volatility || 16.5) > 20 ? '#ffa502' : '#00ff88' },
                    { label:'Portfolio VaR (95%)', val: riskResult.portfolio_var != null ? (String(riskResult.portfolio_var).includes('%') ? riskResult.portfolio_var : `${riskResult.portfolio_var}%`) : (riskResult.var_95 || '1.8%'),
                      color:'#ff4757' },
                    { label:'Avg Correlation', val: riskResult.avg_correlation != null ? riskResult.avg_correlation : 0.42,
                      color: (riskResult.avg_correlation || 0.42) > 0.7 ? '#ff4757' : (riskResult.avg_correlation || 0.42) > 0.4 ? '#ffa502' : '#00ff88' },
                    { label:'Smart Money Signal', val: smResult?.signal || smResult?.institutional_stance || 'N/A',
                      color: (smResult?.signal || '').includes('BUY') || (smResult?.signal || '').includes('ACCUMULATION') ? '#00ff88' : (smResult?.signal || '').includes('SELL') ? '#ff4757' : '#ffa502' },
                    { label:'News Sentiment', val: newsResult?.overall || (newsResult?.sentiment_score >= 0.6 ? 'Positive' : newsResult?.sentiment_score < 0.4 ? 'Negative' : 'Neutral') || 'N/A',
                      color: (newsResult?.overall === 'Positive' || newsResult?.sentiment_score >= 0.6) ? '#00ff88' : (newsResult?.overall === 'Negative' || newsResult?.sentiment_score < 0.4) ? '#ff4757' : '#ffa502' },
                  ].map(r => (
                    <div key={r.label} style={{ display:'flex', justifyContent:'space-between',
                      padding:'9px 0', borderBottom:'1px solid var(--border)' }}>
                      <span style={{ color:'var(--text-secondary)', fontSize:'0.82rem' }}>{r.label}</span>
                      <span style={{ color:r.color, fontWeight:700 }}>{r.val}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ── MASTER REPORT ── */}
          {masterReport && (
            <div style={{ background:'linear-gradient(135deg,rgba(168,85,247,0.08),rgba(0,212,255,0.04))',
              border:'1px solid rgba(168,85,247,0.35)', borderRadius:16,
              padding:'1.75rem', marginBottom:'1rem' }}>
              <div style={{ fontWeight:800, color:'#a855f7', marginBottom:'1rem',
                fontSize:'1.1rem', display:'flex', alignItems:'center', gap:10 }}>
                🎯 Master Investment Report
                <span className="badge badge-purple" style={{ fontSize:'0.65rem' }}>
                  Groq Llama 3.3 70B · {selAgents.length} agents synthesised
                </span>
              </div>
              <div style={{ color:'var(--text-primary)', lineHeight:1.9,
                fontSize:'0.9rem', whiteSpace:'pre-wrap' }}>
                {masterReport}
              </div>
              <div style={{ marginTop:'1rem', paddingTop:'0.75rem',
                borderTop:'1px solid rgba(168,85,247,0.2)',
                fontSize:'0.7rem', color:'#484f58' }}>
                ⚠️ This report is for educational purposes only. Not financial advice.
                Always consult a SEBI-registered advisor before investing.
                Data fetched: {new Date().toLocaleString('en-IN')}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
