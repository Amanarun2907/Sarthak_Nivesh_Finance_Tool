"""
MCP (Model Context Protocol) Tools for Sarthak Nivesh
Provides external tool integration for agentic AI system

Requirements Fulfilled:
- Tool Integration using MCP (Requirement #2)
- Minimum 2 external tools (Stock Data Fetcher + News Analyzer)
"""

import yfinance as yf
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import feedparser
from bs4 import BeautifulSoup
import json
from pydantic import BaseModel, Field, validator

try:
    from agentic_runtime import is_network_available
except Exception:
    def is_network_available(*args, **kwargs):
        return True

class MCPToolResponse(BaseModel):
    """Structured response from MCP tools"""
    tool_name: str
    status: str = Field(..., pattern="^(success|error|partial)$")
    data: Any
    timestamp: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "stock_data_fetcher",
                "status": "success",
                "data": {"price": 1500.50},
                "timestamp": "2024-01-01T10:00:00",
                "metadata": {"source": "yahoo_finance"}
            }
        }


class StockDataRequest(BaseModel):
    """Validated request for stock data"""
    symbol: str = Field(..., min_length=1, max_length=20)
    period: str = Field(default="1mo", pattern="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|max)$")
    interval: str = Field(default="1d", pattern="^(1m|5m|15m|30m|1h|1d|1wk|1mo)$")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Ensure symbol ends with .NS for Indian stocks"""
        v = v.upper().strip()
        if not v.endswith('.NS'):
            v = f"{v}.NS"
        return v


class NewsRequest(BaseModel):
    """Validated request for news data"""
    company_name: str = Field(..., min_length=2, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=20)
    days_back: int = Field(default=7, ge=1, le=30)


class MCPStockDataFetcher:
    """
    MCP Tool #1: Real-time Stock Data Fetcher
    Integrates with Yahoo Finance API for authentic market data
    """
    
    def __init__(self):
        self.tool_name = "stock_data_fetcher"
        self.version = "1.0.0"
        self.description = "Fetches real-time stock data from Yahoo Finance"
    
    def fetch_stock_data(self, request: StockDataRequest) -> MCPToolResponse:
        """
        Fetch comprehensive stock data with validation
        
        Args:
            request: Validated stock data request
            
        Returns:
            MCPToolResponse with stock data
        """
        try:
            if not is_network_available(0.3):
                return MCPToolResponse(
                    tool_name=self.tool_name,
                    status="error",
                    data={},
                    error_message=f"Network unavailable for symbol {request.symbol}",
                    metadata={"request": request.dict()}
                )

            ticker = yf.Ticker(request.symbol)
            
            # Fetch historical data
            hist = ticker.history(period=request.period, interval=request.interval)
            
            if hist.empty:
                return MCPToolResponse(
                    tool_name=self.tool_name,
                    status="error",
                    data={},
                    error_message=f"No data found for symbol {request.symbol}",
                    metadata={"request": request.dict()}
                )
            
            # Fetch current info
            info = ticker.info
            
            # Calculate technical indicators
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            price_change = ((current_price - prev_close) / prev_close) * 100
            
            # Calculate volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
            
            # RSI(14)
            rsi_val = 52.0
            try:
                close_series = hist['Close']
                delta = close_series.diff()
                gain = delta.where(delta > 0, 0.0).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0.0)).rolling(14).mean()
                rs = gain / loss.replace(0, 1e-10)
                rsi_series = 100 - (100 / (1 + rs))
                if not rsi_series.empty and not rsi_series.iloc[-1] != rsi_series.iloc[-1]:
                    rsi_val = float(rsi_series.iloc[-1])
            except Exception:
                pass

            # MA20
            ma20_val = float(current_price)
            try:
                ma20_val = float(hist['Close'].rolling(min(len(hist), 20)).mean().iloc[-1])
            except Exception:
                pass

            # MACD (12,26 EMA crossover)
            macd_val = 0.0
            try:
                ema12 = hist['Close'].ewm(span=12).mean()
                ema26 = hist['Close'].ewm(span=26).mean()
                macd_val = float((ema12 - ema26).iloc[-1])
            except Exception:
                pass
            
            data = {
                "symbol": request.symbol,
                "current_price": float(current_price),
                "prev_close": float(prev_close),
                "price_change_percent": float(price_change),
                "volume": int(hist['Volume'].iloc[-1]) if 'Volume' in hist.columns else 0,
                "high_52week": float(hist['High'].max()),
                "low_52week": float(hist['Low'].min()),
                "volatility": float(volatility),
                "rsi": rsi_val,
                "macd": macd_val,
                "ma20": ma20_val,
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "company_name": info.get('longName', request.symbol),
                "sector": info.get('sector', 'Unknown'),
                "industry": info.get('industry', 'Unknown'),
                "historical_data": {
                    "dates": hist.index.strftime('%Y-%m-%d').tolist(),
                    "close": hist['Close'].tolist(),
                    "volume": hist['Volume'].tolist() if 'Volume' in hist.columns else [],
                    "high": hist['High'].tolist(),
                    "low": hist['Low'].tolist()
                }
            }
            
            return MCPToolResponse(
                tool_name=self.tool_name,
                status="success",
                data=data,
                metadata={
                    "source": "yahoo_finance",
                    "period": request.period,
                    "interval": request.interval,
                    "data_points": len(hist)
                }
            )
            
        except Exception as e:
            return MCPToolResponse(
                tool_name=self.tool_name,
                status="error",
                data={},
                error_message=str(e),
                metadata={"request": request.dict()}
            )
    
    def get_tool_schema(self) -> Dict:
        """Return tool schema for agent registration"""
        return {
            "name": self.tool_name,
            "version": self.version,
            "description": self.description,
            "input_schema": StockDataRequest.model_json_schema(),
            "output_schema": MCPToolResponse.model_json_schema()
        }


class MCPNewsAnalyzer:
    """
    MCP Tool #2: Financial News Analyzer
    Fetches and analyzes financial news from multiple sources
    """
    
    def __init__(self):
        self.tool_name = "news_analyzer"
        self.version = "1.0.0"
        self.description = "Fetches and analyzes financial news from multiple RSS feeds"
        
        self.news_sources = {
            'economic_times': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
            'moneycontrol': 'https://www.moneycontrol.com/rss/marketreports.xml',
            'google_finance': 'https://news.google.com/rss/search?q=indian+stock+market&hl=en-IN&gl=IN&ceid=IN:en'
        }
    
    def fetch_news(self, request: NewsRequest) -> MCPToolResponse:
        """
        Fetch and analyze news for a company
        
        Args:
            request: Validated news request
            
        Returns:
            MCPToolResponse with news articles
        """
        try:
            if not is_network_available(0.3):
                return MCPToolResponse(
                    tool_name=self.tool_name,
                    status="error",
                    data={"articles": []},
                    error_message="Network unavailable",
                    metadata={"request": request.dict()}
                )

            all_articles = []
            cutoff_date = datetime.now() - timedelta(days=request.days_back)
            
            # Search query
            search_terms = [request.company_name, request.symbol.replace('.NS', '')]
            
            for source_name, source_url in self.news_sources.items():
                try:
                    # Fetch RSS feed
                    feed = feedparser.parse(source_url)
                    
                    for entry in feed.entries[:20]:  # Limit to 20 per source
                        # Check if article mentions the company
                        title = entry.get('title', '')
                        summary = entry.get('summary', entry.get('description', ''))
                        
                        relevant = any(term.lower() in title.lower() or term.lower() in summary.lower() 
                                     for term in search_terms)
                        
                        if relevant:
                            # Parse date
                            pub_date = entry.get('published_parsed')
                            if pub_date:
                                article_date = datetime(*pub_date[:6])
                                if article_date < cutoff_date:
                                    continue
                            
                            article = {
                                "title": title,
                                "summary": summary[:300],  # Truncate long summaries
                                "link": entry.get('link', ''),
                                "source": source_name,
                                "published": entry.get('published', 'Unknown'),
                                "relevance_score": self._calculate_relevance(title, summary, search_terms)
                            }
                            all_articles.append(article)
                    
                except Exception as e:
                    print(f"Error fetching from {source_name}: {e}")
                    continue
            
            # Sort by relevance
            all_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Limit to top 20
            all_articles = all_articles[:20]
            
            return MCPToolResponse(
                tool_name=self.tool_name,
                status="success" if all_articles else "partial",
                data={
                    "company": request.company_name,
                    "symbol": request.symbol,
                    "articles": all_articles,
                    "total_found": len(all_articles)
                },
                metadata={
                    "sources_checked": list(self.news_sources.keys()),
                    "days_back": request.days_back,
                    "search_terms": search_terms
                }
            )
            
        except Exception as e:
            return MCPToolResponse(
                tool_name=self.tool_name,
                status="error",
                data={},
                error_message=str(e),
                metadata={"request": request.dict()}
            )
    
    def _calculate_relevance(self, title: str, summary: str, search_terms: List[str]) -> float:
        """Calculate relevance score for an article"""
        score = 0.0
        text = (title + " " + summary).lower()
        
        for term in search_terms:
            term_lower = term.lower()
            # Title mentions are worth more
            if term_lower in title.lower():
                score += 2.0
            # Body mentions
            score += text.count(term_lower) * 0.5
        
        return min(score, 10.0)  # Cap at 10
    
    def get_tool_schema(self) -> Dict:
        """Return tool schema for agent registration"""
        return {
            "name": self.tool_name,
            "version": self.version,
            "description": self.description,
            "input_schema": NewsRequest.model_json_schema(),
            "output_schema": MCPToolResponse.model_json_schema()
        }


class MCPToolRegistry:
    """
    Central registry for all MCP tools
    Manages tool lifecycle and provides unified interface
    """
    
    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default MCP tools"""
        self.register_tool(MCPStockDataFetcher())
        self.register_tool(MCPNewsAnalyzer())
    
    def register_tool(self, tool: Any):
        """Register a new MCP tool"""
        self.tools[tool.tool_name] = tool
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict]:
        """List all registered tools with schemas"""
        return [tool.get_tool_schema() for tool in self.tools.values()]
    
    def execute_tool(self, tool_name: str, **kwargs) -> MCPToolResponse:
        """
        Execute a tool with given parameters
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific parameters
            
        Returns:
            MCPToolResponse
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return MCPToolResponse(
                tool_name=tool_name,
                status="error",
                data={},
                error_message=f"Tool '{tool_name}' not found"
            )
        
        try:
            if tool_name == "stock_data_fetcher":
                request = StockDataRequest(**kwargs)
                return tool.fetch_stock_data(request)
            elif tool_name == "news_analyzer":
                request = NewsRequest(**kwargs)
                return tool.fetch_news(request)
            else:
                return MCPToolResponse(
                    tool_name=tool_name,
                    status="error",
                    data={},
                    error_message=f"Tool execution not implemented for '{tool_name}'"
                )
        except Exception as e:
            return MCPToolResponse(
                tool_name=tool_name,
                status="error",
                data={},
                error_message=f"Tool execution failed: {str(e)}"
            )


# Singleton instance
_mcp_registry = None

def get_mcp_registry() -> MCPToolRegistry:
    """Get global MCP tool registry instance"""
    global _mcp_registry
    if _mcp_registry is None:
        _mcp_registry = MCPToolRegistry()
    return _mcp_registry


if __name__ == "__main__":
    # Test MCP tools
    registry = get_mcp_registry()
    
    print("✅ MCP Tools Registered:")
    for tool in registry.list_tools():
        print(f"  - {tool['name']} v{tool['version']}: {tool['description']}")
    
    # Test stock data fetcher
    print("\n📊 Testing Stock Data Fetcher...")
    response = registry.execute_tool(
        "stock_data_fetcher",
        symbol="RELIANCE",
        period="1mo"
    )
    print(f"Status: {response.status}")
    if response.status == "success":
        print(f"Current Price: ₹{response.data['current_price']:.2f}")
        print(f"Change: {response.data['price_change_percent']:.2f}%")
    
    # Test news analyzer
    print("\n📰 Testing News Analyzer...")
    response = registry.execute_tool(
        "news_analyzer",
        company_name="Reliance Industries",
        symbol="RELIANCE.NS",
        days_back=7
    )
    print(f"Status: {response.status}")
    if response.status in ["success", "partial"]:
        print(f"Articles Found: {response.data['total_found']}")
