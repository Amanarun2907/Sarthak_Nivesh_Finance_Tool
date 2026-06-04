import React, { useState } from 'react';

const NAV = [
  { id: 'dashboard',  label: 'Dashboard',          icon: '🏠', desc: 'Live market overview' },
  { id: 'stocks',     label: 'Stock Intelligence',  icon: '📊', desc: '50+ NSE stocks' },
  { id: 'mf',         label: 'Mutual Funds',        icon: '💰', desc: '2400+ live funds' },
  { id: 'sip',        label: 'SIP Goal Planner',    icon: '🎯', desc: 'Inflation-adjusted' },
  { id: 'ipo',        label: 'IPO Intelligence',    icon: '🚀', desc: 'Live GMP & scoring' },
  { id: 'smartmoney', label: 'Smart Money',         icon: '🏦', desc: 'FII/DII tracker' },
  { id: 'portfolio',  label: 'Portfolio & Risk',    icon: '🛡️', desc: 'P&L + risk metrics' },
  { id: 'coach',      label: 'AI Finance Coach',    icon: '🧠', desc: 'Explain my portfolio' },
  { id: 'agentic',        label: 'Agentic AI Hub',      icon: '🤖', desc: '6 agents · Full report' },
  { id: 'ipo_multiagent', label: 'IPO Multi-Agent',      icon: '🧬', desc: '6-agent IPO INVEST/EXIT' },
  { id: 'news',       label: 'News & Sentiment',    icon: '📰', desc: 'Live RSS + VADER' },
  { id: 'assistant',  label: 'AI Assistant',        icon: '💬', desc: 'Groq Llama 3.3 70B' },
  { id: 'analytics',  label: 'Advanced Analytics',  icon: '📈', desc: 'Heatmaps & correlation' },
];

export default function Sidebar({ current, onNavigate }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside style={{
      width: collapsed ? 64 : 240,
      minHeight: '100vh',
      background: 'linear-gradient(180deg, #060910 0%, #0d1117 100%)',
      borderRight: '1px solid #21262d',
      display: 'flex', flexDirection: 'column',
      position: 'sticky', top: 0, height: '100vh',
      transition: 'width 0.25s ease',
      flexShrink: 0, zIndex: 100,
    }}>
      {/* Logo */}
      <div style={{
        padding: collapsed ? '1rem 0' : '1.25rem 1rem',
        borderBottom: '1px solid #21262d',
        display: 'flex', alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'space-between',
        minHeight: 72,
      }}>
        {!collapsed && (
          <div>
            <div style={{ fontSize: '1rem', fontWeight: 900, color: '#00d4ff', lineHeight: 1.2,
              background: 'linear-gradient(135deg,#00d4ff,#00ff88)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              सार्थक निवेश
            </div>
            <div style={{ fontSize: '0.65rem', color: '#8b949e', marginTop: 2, letterSpacing: '0.05em' }}>
              INVESTMENT INTELLIGENCE
            </div>
          </div>
        )}
        {collapsed && <span style={{ fontSize: '1.3rem' }}>📈</span>}
        <button onClick={() => setCollapsed(!collapsed)} style={{
          background: 'none', border: '1px solid #21262d', borderRadius: 6,
          color: '#8b949e', cursor: 'pointer', padding: '4px 6px', fontSize: '0.7rem',
          transition: 'all 0.2s', flexShrink: 0,
        }}
          onMouseEnter={e => e.currentTarget.style.borderColor = '#00d4ff'}
          onMouseLeave={e => e.currentTarget.style.borderColor = '#21262d'}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {/* Live indicator */}
      {!collapsed && (
        <div style={{ padding: '8px 1rem', borderBottom: '1px solid #21262d',
          display: 'flex', alignItems: 'center', gap: 6 }}>
          <span className="pulse-dot"/>
          <span style={{ fontSize: '0.68rem', color: '#8b949e' }}>LIVE DATA ACTIVE</span>
        </div>
      )}

      {/* Nav */}
      <nav style={{ flex: 1, padding: '0.5rem', overflowY: 'auto', overflowX: 'hidden' }}>
        {NAV.map(item => {
          const active = current === item.id;
          return (
            <button key={item.id} onClick={() => onNavigate(item.id)}
              title={collapsed ? item.label : ''}
              style={{
                display: 'flex', alignItems: 'center',
                gap: collapsed ? 0 : 10,
                justifyContent: collapsed ? 'center' : 'flex-start',
                width: '100%', padding: collapsed ? '10px 0' : '9px 12px',
                borderRadius: 8, border: 'none', cursor: 'pointer',
                textAlign: 'left', marginBottom: 2,
                background: active
                  ? 'linear-gradient(135deg,rgba(0,212,255,0.15),rgba(0,255,136,0.08))'
                  : 'transparent',
                borderLeft: active ? '2px solid #00d4ff' : '2px solid transparent',
                transition: 'all 0.15s',
              }}
              onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; }}
              onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent'; }}
            >
              <span style={{ fontSize: '1.05rem', flexShrink: 0 }}>{item.icon}</span>
              {!collapsed && (
                <div style={{ overflow: 'hidden' }}>
                  <div style={{ fontSize: '0.82rem', fontWeight: active ? 600 : 400,
                    color: active ? '#00d4ff' : '#c9d1d9', lineHeight: 1.2 }}>
                    {item.label}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#484f58', marginTop: 1 }}>
                    {item.desc}
                  </div>
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div style={{ padding: '0.75rem 1rem', borderTop: '1px solid #21262d' }}>
          <div style={{ fontSize: '0.68rem', color: '#484f58', lineHeight: 1.6 }}>
            <div style={{ color: '#8b949e', fontWeight: 600 }}>Aman Jain</div>
            <div>B.Tech 2023–27</div>
            <div style={{ color: '#00d4ff', marginTop: 3 }}>100% Real-time · Zero Dummy Data</div>
          </div>
        </div>
      )}
    </aside>
  );
}
