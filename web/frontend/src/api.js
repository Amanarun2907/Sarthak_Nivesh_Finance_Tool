import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: BASE, timeout: 60000 });

export const dashboard = {
  indices:  () => api.get('/api/dashboard/indices'),
  movers:   () => api.get('/api/dashboard/movers'),
  breadth:  () => api.get('/api/dashboard/breadth'),
};

export const stocks = {
  list:         ()           => api.get('/api/stocks/list'),
  ohlcv:        (sym, period)=> api.get('/api/stocks/ohlcv', { params: { symbol: sym, period } }),
  technicals:   (sym)        => api.get('/api/stocks/technicals', { params: { symbol: sym } }),
  fundamentals: (sym)        => api.get('/api/stocks/fundamentals', { params: { symbol: sym } }),
};

export const mf = {
  categories:  ()            => api.get('/api/mf/categories'),
  funds:       (cat, limit)  => api.get('/api/mf/funds', { params: { category: cat, limit: limit||20 } }),
  navHistory:  (code, days)  => api.get('/api/mf/nav_history', { params: { scheme_code: code, days: days||365 } }),
};

export const sip = {
  returns:    (profile)  => api.get(`/api/sip/returns/${profile}`),
  calculate:  (data)     => api.post('/api/sip/calculate', data),
  saveGoal:   (data)     => api.post('/api/sip/save', data),
  getGoals:   ()         => api.get('/api/sip/goals'),
  deleteGoal: (id)       => api.delete(`/api/sip/goals/${id}`),
};

export const ipo = {
  live:       () => api.get('/api/ipo/live'),
  detail:     (url) => api.get('/api/ipo/detail', { params: { url } }),
  aiAnalysis: (url, name) => api.get('/api/ipo/ai_analysis', { params: { url, name } }),
};

export const smartMoney = {
  fiiDii:      () => api.get('/api/smartmoney/fii_dii'),
  bulkDeals:   () => api.get('/api/smartmoney/bulk_deals'),
  blockDeals:  () => api.get('/api/smartmoney/block_deals'),
  sectorFlow:  () => api.get('/api/smartmoney/sector_flow'),
};

export const portfolio = {
  holdings:  ()     => api.get('/api/portfolio/holdings'),
  add:       (data) => api.post('/api/portfolio/add', data),
  delete:    (id)   => api.delete(`/api/portfolio/delete/${id}`),
  metrics:   ()     => api.get('/api/portfolio/metrics'),
};

export const news = {
  live:            (limit) => api.get('/api/news/live', { params: { limit: limit||40 } }),
  sectorSentiment: ()      => api.get('/api/news/sector_sentiment'),
};

export const ai = {
  chat:        (question) => api.post('/api/ai/chat', { question }),
  explainLoss: (language) => api.post('/api/ai/explain_loss', { language }),
};

export const analytics = {
  sectorHeatmap: ()       => api.get('/api/analytics/sector_heatmap'),
  correlation:   (period) => api.get('/api/analytics/correlation', { params: { period: period||'3mo' } }),
  volumeAnalysis:()       => api.get('/api/analytics/volume_analysis'),
  marketBreadth: ()       => api.get('/api/analytics/market_breadth'),
};

export const agenticAI = {
  run: (query, agents) => api.post('/api/agentic/run', { query, agents }, { timeout: 180000 }),
};

export const ipoMultiAgent = {
  status:  ()     => api.get('/api/ipo_multiagent/status'),
  analyze: (data) => api.post('/api/ipo_multiagent/analyze', data, { timeout: 300000 }),
};

export default api;
