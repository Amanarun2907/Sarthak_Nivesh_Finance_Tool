import React, { useEffect, useState, useCallback } from 'react';
import { dashboard } from '../api';
import PlotlyChart from '../components/PlotlyChart';

const C_GREEN  = 'var(--accent-green)';
const C_RED    = 'var(--accent-red)';
const C_ORANGE = 'var(--accent-orange)';
const C_ACCENT = 'var(--accent)';
const C_SEC    = 'var(--text-secondary)';

function IndexCard({ label, data }) {
  if (!data) return null;
  if (data.live === false) {
    return (
      <div className="kpi-card" style={{ borderLeftColor: C_ORANGE }}>
        <div className="kpi-label">{label}</div>
        <div className="kpi-value" style={{ color: C_SEC, fontSize: '1.1rem' }}>
          Market data unavailable
        </div>
      </div>
    );
  }
  const up    = data.change_pct >= 0;
  const color = up ? C_GREEN : C_RED;
  return (
    <div className="kpi-card" style={{ borderLeftColor: color }}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={{ color, fontSize: '1.8rem' }}>
        {data.value?.toLocaleString('en-IN')}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 6 }}>
        <span style={{ color, fontWeight: 700, fontSize: '0.9rem' }}>
          {up ? '▲' : '▼'} {Math.abs(data.change_pct)}%
        </span>
        <span style={{ color: C_SEC, fontSize: '0.78rem' }}>
          {up ? '+' : ''}{data.change_pts?.toLocaleString('en-IN')} pts
        </span>
      </div>
    </div>
  );
}

function MoverRow({ item, type, rank }) {
  const up    = type === 'gainer';
  const color = up ? C_GREEN : C_RED;
  return (
    <div className="mover-card" style={{ borderLeft: '3px solid ' + color }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 22, height: 22, borderRadius: '50%',
          background: color + '22',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '0.65rem', fontWeight: 700, color, flexShrink: 0,
        }}>{rank}</div>
        <div>
          <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{item.name}</div>
          <div style={{ fontSize: '0.72rem', color: C_SEC }}>{item.symbol}</div>
        </div>
      </div>
      <div style={{ textAlign: 'right' }}>
        <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>
          ₹{item.price?.toLocaleString('en-IN')}
        </div>
        <div style={{ color, fontWeight: 700, fontSize: '0.82rem' }}>
          {up ? '+' : ''}{item.change_pct}%
        </div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [indices,     setIndices]     = useState(null);
  const [movers,      setMovers]      = useState(null);
  const [breadth,     setBreadth]     = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [refreshing,  setRefreshing]  = useState(false);
  const [error,       setError]       = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const load = useCallback((isRefresh = false) => {
    if (isRefresh) setRefreshing(true); else setLoading(true);
    setError(null);
    Promise.all([dashboard.indices(), dashboard.movers(), dashboard.breadth()])
      .then(([i, m, b]) => {
        setIndices(i.data);
        setMovers(m.data);
        setBreadth(b.data);
        setLastUpdated(new Date());
      })
      .catch((e) => setError(e.message || 'Failed to fetch market data'))
      .finally(() => { setLoading(false); setRefreshing(false); });
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <div className="loading-text">Fetching live market data from NSE and Yahoo Finance...</div>
      </div>
    );
  }

  if (error && !indices && !movers && !breadth) {
    return (
      <div className="loading">
        <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>⚠️</div>
        <div className="loading-text" style={{ marginBottom: '1rem' }}>
          Could not load market data: {error}
        </div>
        <button className="btn btn-primary" onClick={() => load()}>Retry</button>
      </div>
    );
  }

  const isLive = indices?.nifty?.live !== false &&
                 movers?.live !== false &&
                 breadth?.live !== false;

  const nifty   = indices?.nifty;
  const sensex  = indices?.sensex;
  const adRatio = breadth?.ad_ratio || 0;
  const mktSentiment = adRatio > 1.5 ? 'Bullish 🐂' : adRatio < 0.67 ? 'Bearish 🐻' : 'Neutral ⚖️';
  const sentColor    = adRatio > 1.5 ? C_GREEN : adRatio < 0.67 ? C_RED : C_ORANGE;

  const breadthPie = breadth ? [{
    type: 'pie',
    labels: ['Advancing', 'Declining', 'Unchanged'],
    values: [breadth.advancing, breadth.declining, breadth.unchanged],
    marker: { colors: ['#00ff88', '#ff4757', '#ffa502'], line: { color: '#060910', width: 2 } },
    hole: 0.55,
    textinfo: 'label+percent',
    textfont: { color: '#f0f6fc', size: 11 },
    hovertemplate: '<b>%{label}</b><br>%{value} stocks<extra></extra>',
  }] : [];

  const gainersBar = movers?.gainers?.length ? [{
    type: 'bar',
    x: movers.gainers.map(g => g.symbol),
    y: movers.gainers.map(g => g.change_pct),
    marker: { color: 'rgba(0,255,136,0.7)', line: { color: '#00ff88', width: 1 } },
    text: movers.gainers.map(g => '+' + g.change_pct + '%'),
    textposition: 'outside',
    hovertemplate: '<b>%{x}</b><br>+%{y}%<extra></extra>',
  }] : [];

  const losersBar = movers?.losers?.length ? [{
    type: 'bar',
    x: movers.losers.map(l => l.symbol),
    y: movers.losers.map(l => l.change_pct),
    marker: { color: 'rgba(255,71,87,0.7)', line: { color: '#ff4757', width: 1 } },
    text: movers.losers.map(l => l.change_pct + '%'),
    textposition: 'outside',
    hovertemplate: '<b>%{x}</b><br>%{y}%<extra></extra>',
  }] : [];

  return (
    <div>
      {/* Header */}
      <div className="page-header">
        <div className="section-title">🏠 Live Market Dashboard</div>
        <div className="section-subtitle">
          <span className="pulse-dot" style={{ background: isLive ? undefined : C_ORANGE }} />
          <span>{isLive ? 'All data live · NSE + Yahoo Finance' : 'Market data unavailable · showing last cached data'}</span>
          <span style={{ marginLeft: 'auto', color: C_SEC, fontSize: '0.75rem' }}>
            Updated: {lastUpdated?.toLocaleTimeString('en-IN')}
          </span>
          <button className="btn btn-secondary"
            style={{ padding: '5px 12px', fontSize: '0.75rem' }}
            disabled={refreshing}
            onClick={() => load(true)}>
            {refreshing ? '⏳ Refreshing…' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      {error && (
        <div className="card" style={{
          borderLeft: '3px solid ' + C_ORANGE, marginBottom: '1rem',
          color: C_ORANGE, fontSize: '0.85rem',
        }}>
          ⚠️ Partial data failure: {error}
        </div>
      )}

      {/* Index KPIs */}
      <div className="grid-4" style={{ marginBottom: '1.5rem' }}>
        <IndexCard label="NIFTY 50" data={nifty} />
        <IndexCard label="SENSEX"   data={sensex} />
        <div className="kpi-card" style={{ borderLeftColor: sentColor }}>
          <div className="kpi-label">Market Sentiment</div>
          <div className="kpi-value" style={{ color: sentColor, fontSize: '1.3rem' }}>
            {mktSentiment}
          </div>
          <div className="kpi-sub">A/D Ratio: {breadth?.ad_ratio}</div>
        </div>
        <div className="kpi-card" style={{ borderLeftColor: C_ACCENT }}>
          <div className="kpi-label">Breadth Strength</div>
          <div className="kpi-value" style={{ color: C_ACCENT }}>{breadth?.strength}%</div>
          <div style={{ marginTop: 8 }}>
            <div className="score-bar-track">
              <div className="score-bar-fill" style={{
                width: (breadth?.strength || 0) + '%',
                background: 'linear-gradient(90deg,#ff4757,#ffa502,#00ff88)',
              }} />
            </div>
          </div>
        </div>
      </div>

      {/* Movers */}
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div style={{ fontWeight: 700, color: C_GREEN, marginBottom: '1rem',
            display: 'flex', alignItems: 'center', gap: 8 }}>
            🚀 Top Gainers
            <span className="badge badge-green">{movers?.gainers?.length || 0}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
            {movers?.gainers?.length
              ? movers.gainers.map((g, i) => (
                  <MoverRow key={g.symbol} item={g} type="gainer" rank={i + 1} />
                ))
              : <div style={{ color: C_SEC, fontSize: '0.82rem', padding: '0.5rem 0' }}>
                  No stocks advanced in the tracked universe.
                </div>}
          </div>
        </div>
        <div className="card">
          <div style={{ fontWeight: 700, color: C_RED, marginBottom: '1rem',
            display: 'flex', alignItems: 'center', gap: 8 }}>
            📉 Top Losers
            <span className="badge badge-red">{movers?.losers?.length || 0}</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 7 }}>
            {movers?.losers?.length
              ? movers.losers.map((l, i) => (
                  <MoverRow key={l.symbol} item={l} type="loser" rank={i + 1} />
                ))
              : <div style={{ color: C_SEC, fontSize: '0.82rem', padding: '0.5rem 0' }}>
                  No stocks declined in the tracked universe.
                </div>}
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid-3" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div style={{ fontWeight: 600, color: C_ACCENT, marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            ⚡ Market Breadth
          </div>
          <PlotlyChart data={breadthPie}
            layout={{
              height: 280, showlegend: true,
              legend: { orientation: 'h', y: -0.15 },
              annotations: [{
                text: '<b>' + (breadth?.total || 0) + '</b><br>stocks',
                x: 0.5, y: 0.5, showarrow: false,
                font: { color: '#f0f6fc', size: 13 },
              }],
            }} />
        </div>
        <div className="card">
          <div style={{ fontWeight: 600, color: C_GREEN, marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            📈 Gainers % Change
          </div>
          <PlotlyChart data={gainersBar}
            layout={{ height: 280, showlegend: false,
              yaxis: { title: '% Change', ticksuffix: '%' }, bargap: 0.3 }} />
        </div>
        <div className="card">
          <div style={{ fontWeight: 600, color: C_RED, marginBottom: '0.5rem', fontSize: '0.85rem' }}>
            📉 Losers % Change
          </div>
          <PlotlyChart data={losersBar}
            layout={{ height: 280, showlegend: false,
              yaxis: { title: '% Change', ticksuffix: '%' }, bargap: 0.3 }} />
        </div>
      </div>

      {/* Stats */}
      <div className="card">
        <div style={{ fontWeight: 600, color: C_ACCENT, marginBottom: '1rem' }}>
          📊 Market Statistics
        </div>
        <div className="grid-5">
          {[
            { label: 'Total Tracked', val: breadth?.total,     color: C_ACCENT  },
            { label: 'Advancing',     val: breadth?.advancing, color: C_GREEN   },
            { label: 'Declining',     val: breadth?.declining, color: C_RED     },
            { label: 'Unchanged',     val: breadth?.unchanged, color: C_ORANGE  },
            { label: 'A/D Ratio',     val: breadth?.ad_ratio,  color: sentColor },
          ].map(s => (
            <div key={s.label} style={{
              textAlign: 'center', padding: '0.75rem',
              background: 'var(--bg-secondary)', borderRadius: 10,
            }}>
              <div style={{ fontSize: '0.7rem', color: C_SEC, marginBottom: 4,
                textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {s.label}
              </div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: s.color }}>
                {s.val}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
