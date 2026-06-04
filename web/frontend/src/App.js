import React, { useState } from 'react';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import StockIntelligence from './pages/StockIntelligence';
import MutualFunds from './pages/MutualFunds';
import SIPGoalPlanner from './pages/SIPGoalPlanner';
import IPOIntelligence from './pages/IPOIntelligence';
import SmartMoney from './pages/SmartMoney';
import PortfolioManager from './pages/PortfolioManager';
import AIFinanceCoach from './pages/AIFinanceCoach';
import NewsAndSentiment from './pages/NewsAndSentiment';
import AIAssistant from './pages/AIAssistant';
import AdvancedAnalytics from './pages/AdvancedAnalytics';
import AgenticAI from './pages/AgenticAI';
import IPOMultiAgent from './pages/IPOMultiAgent';

const PAGES = {
  dashboard:      Dashboard,
  stocks:         StockIntelligence,
  mf:             MutualFunds,
  sip:            SIPGoalPlanner,
  ipo:            IPOIntelligence,
  smartmoney:     SmartMoney,
  portfolio:      PortfolioManager,
  coach:          AIFinanceCoach,
  news:           NewsAndSentiment,
  assistant:      AIAssistant,
  analytics:      AdvancedAnalytics,
  agentic:        AgenticAI,
  ipo_multiagent: IPOMultiAgent,
};

export default function App() {
  const [page, setPage] = useState('dashboard');
  const PageComponent = PAGES[page] || Dashboard;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Toaster position="top-right" toastOptions={{
        duration: 3000,
        style: {
          background: '#111827', color: '#f0f6fc',
          border: '1px solid #21262d', borderRadius: 10,
          fontSize: '0.875rem',
        },
        success: { iconTheme: { primary: '#00ff88', secondary: '#000' } },
        error:   { iconTheme: { primary: '#ff4757', secondary: '#000' } },
      }}/>
      <Sidebar current={page} onNavigate={setPage} />
      <main style={{
        flex: 1, padding: '1.75rem 2rem',
        overflowY: 'auto', maxHeight: '100vh',
        background: 'radial-gradient(ellipse at top left, rgba(0,212,255,0.03) 0%, transparent 60%)',
      }}>
        <div className="fade-in" key={page}>
          <PageComponent />
        </div>
      </main>
    </div>
  );
}
