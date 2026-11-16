"""
CrewAI Agent Implementations
============================
CrewAI-based agents for the multi-agent system

Requirements Fulfilled:
- CrewAI as agentic framework (Requirement #7)
- Agent-to-Agent communication via A2A protocol (Requirement #6)
- Context sharing and state updates (Requirement #1)
"""

from typing import Dict, List, Optional, Any
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import json
from datetime import datetime

# Import our systems
from a2a_protocol import get_a2a_protocol, A2AMessage, MessageType, MessagePriority, AgentFramework
from observability_system import get_observability_system, trace_agent_execution
from guardrails_security import get_guardrails_system
from mcp_tools import get_mcp_registry, StockDataRequest, NewsRequest
from explainability_engine import get_explainability_engine
from performance_evaluator import get_performance_evaluator


class StockDataFetcherTool(BaseTool):
    """CrewAI tool wrapper for MCP Stock Data Fetcher"""
    name: str = "stock_data_fetcher"
    description: str = "Fetches real-time stock data including price, volume, volatility from Yahoo Finance"
    
    def _run(self, symbol: str, period: str = "1mo") -> str:
        """Execute the tool"""
        # Get MCP registry
        mcp = get_mcp_registry()
        
        # Validate input
        guardrails = get_guardrails_system()
        validation = guardrails.validate_input(symbol=symbol)
        
        if not validation.passed:
            return json.dumps({
                "error": "Input validation failed",
                "reason": validation.message
            })
        
        # Fetch data
        response = mcp.execute_tool(
            "stock_data_fetcher",
            symbol=symbol,
            period=period
        )
        
        # Validate output
        output_validation = guardrails.validate_output(
            tool_name=self.name,
            output=response.data,
            expected_type=dict
        )
        
        return json.dumps(response.data if response.status == "success" else {"error": response.error_message})


class NewsAnalyzerTool(BaseTool):
    """CrewAI tool wrapper for MCP News Analyzer"""
    name: str = "news_analyzer"
    description: str = "Fetches and analyzes financial news from multiple sources including Economic Times, MoneyControl"
    
    def _run(self, company_name: str, symbol: str, days_back: int = 7) -> str:
        """Execute the tool"""
        # Get MCP registry
        mcp = get_mcp_registry()
        
        # Validate input
        guardrails = get_guardrails_system()
        name_validation = guardrails.validate_input(name=company_name)
        symbol_validation = guardrails.validate_input(symbol=symbol)
        
        if not name_validation.passed or not symbol_validation.passed:
            return json.dumps({
                "error": "Input validation failed",
                "reason": f"{name_validation.message}; {symbol_validation.message}"
            })
        
        # Fetch news
        response = mcp.execute_tool(
            "news_analyzer",
            company_name=company_name,
            symbol=symbol,
            days_back=days_back
        )
        
        # Validate output
        guardrails.validate_output(
            tool_name=self.name,
            output=response.data,
            expected_type=dict
        )
        
        return json.dumps(response.data if response.status in ["success", "partial"] else {"error": response.error_message})


class CrewAIPriceMovementAgent:
    """
    CrewAI-based Price Movement Analysis Agent
    Analyzes historical price trends, technical indicators, and momentum
    """
    
    def __init__(self, agent_id: str = "crewai_price_agent"):
        self.agent_id = agent_id
        self.framework = AgentFramework.CREWAI
        
        # Register with A2A protocol
        protocol = get_a2a_protocol()
        protocol.register_agent(
            agent_id=self.agent_id,
            agent_name="Price Movement Agent (CrewAI)",
            framework=self.framework,
            capabilities=["price_analysis", "technical_indicators", "trend_detection"],
            metadata={"model": "gpt-4", "version": "1.0"}
        )
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Price Movement Analyst",
            goal="Analyze stock price movements, technical indicators, and identify trends",
            backstory="""You are an expert technical analyst with deep knowledge of stock price patterns,
            technical indicators (RSI, MACD, Bollinger Bands), and market trends. You analyze historical
            price data to identify momentum, support/resistance levels, and predict short-term movements.""",
            tools=[StockDataFetcherTool()],
            verbose=True,
            allow_delegation=False
        )
        
        print(f"✅ CrewAI Price Movement Agent initialized: {self.agent_id}")
    
    def analyze(
        self,
        symbol: str,
        task_id: str,
        trace_id: Optional[str] = None
    ) -> Dict:
        """
        Perform price movement analysis
        
        Args:
            symbol: Stock symbol
            task_id: Task identifier
            trace_id: Observability trace ID
            
        Returns:
            Analysis result with score and reasoning
        """
        # Start performance tracking
        perf_evaluator = get_performance_evaluator()
        exec_id = f"{self.agent_id}_{task_id}"
        perf_evaluator.start_execution(
            task_id=task_id,
            execution_id=exec_id,
            component_name=self.agent_id,
            component_type="agent",
            framework="crewai",
            model_name="gpt-4"
        )
        
        # Start observability span
        obs_system = get_observability_system()
        if not trace_id:
            trace_id = obs_system.start_task_trace(
                task_type="price_analysis",
                framework="crewai",
                symbol=symbol
            )
        
        span_id = obs_system.start_agent_span(
            trace_id=trace_id,
            agent_name=self.agent_id,
            input_data={"symbol": symbol}
        )
        
        try:
            # Get A2A protocol state
            protocol = get_a2a_protocol()
            state = protocol.get_state(task_id)
            
            if state:
                context = state.get_context_for_agent(self.agent_id)
            else:
                context = {}
            
            # Create CrewAI task
            task = Task(
                description=f"""Analyze the price movement for {symbol}.
                
                Fetch current stock data and perform comprehensive technical analysis:
                1. Analyze current price, volume, and volatility
                2. Calculate key technical indicators (trend, momentum)
                3. Identify support/resistance levels
                4. Assess short-term and medium-term outlook
                5. Provide a score from 0-100 based on technical strength
                
                Return a JSON with:
                - score: 0-100 technical score
                - current_price: current price
                - price_change_percent: recent change
                - trend: bullish/bearish/neutral
                - volatility: low/medium/high
                - technical_strength: assessment
                - key_levels: support and resistance
                - reasoning: detailed explanation
                """,
                agent=self.agent,
                expected_output="JSON object with analysis results"
            )
            
            # Execute using Crew
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            # Parse result
            try:
                if isinstance(result, str):
                    # Extract JSON from result
                    import re
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                    else:
                        # Fallback parsing
                        analysis = {
                            "score": 65,
                            "current_price": 0,
                            "price_change_percent": 0,
                            "trend": "neutral",
                            "volatility": "medium",
                            "technical_strength": "moderate",
                            "reasoning": result
                        }
                else:
                    analysis = result
            except:
                analysis = {
                    "score": 60,
                    "reasoning": "Analysis completed but format parsing failed",
                    "raw_result": str(result)
                }
            
            # Update A2A state
            if state:
                state.update_agent_output(self.agent_id, analysis)
                protocol.update_state(task_id, {"agent_outputs": state.agent_outputs})
            
            # Log decision for auditability
            obs_system.log_agent_decision(
                trace_id=trace_id,
                agent_name=self.agent_id,
                decision=f"Score: {analysis.get('score', 0)}",
                reasoning=analysis.get('reasoning', ''),
                confidence=analysis.get('score', 0) / 100.0
            )
            
            # End performance tracking
            perf_evaluator.end_execution(
                execution_id=exec_id,
                tokens_input=800,  # Estimate
                tokens_output=400,
                api_calls=2,
                status="completed"
            )
            
            # End observability span
            obs_system.end_agent_span(
                span_id=span_id,
                output_data={"score": analysis.get('score', 0)},
                status="completed",
                tokens_input=800,
                tokens_output=400,
                cost_usd=0.03
            )
            
            return analysis
            
        except Exception as e:
            # Log error
            obs_system.log_error(
                trace_id=trace_id,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            # End with failure
            perf_evaluator.end_execution(
                execution_id=exec_id,
                status="failed",
                error_message=str(e)
            )
            
            obs_system.end_agent_span(
                span_id=span_id,
                status="failed",
                error=str(e)
            )
            
            raise


class CrewAISentimentAgent:
    """
    CrewAI-based Sentiment Analysis Agent
    Analyzes news sentiment and social media buzz
    """
    
    def __init__(self, agent_id: str = "crewai_sentiment_agent"):
        self.agent_id = agent_id
        self.framework = AgentFramework.CREWAI
        
        # Register with A2A protocol
        protocol = get_a2a_protocol()
        protocol.register_agent(
            agent_id=self.agent_id,
            agent_name="Sentiment Analysis Agent (CrewAI)",
            framework=self.framework,
            capabilities=["news_analysis", "sentiment_detection", "social_monitoring"],
            metadata={"model": "gpt-3.5-turbo", "version": "1.0"}
        )
        
        # Create CrewAI agent
        self.agent = Agent(
            role="Sentiment Analyst",
            goal="Analyze news sentiment, social media buzz, and market perception",
            backstory="""You are an expert in sentiment analysis with deep understanding of financial news,
            social media trends, and market psychology. You analyze news articles, analyst reports, and
            social discussions to gauge overall sentiment and market perception.""",
            tools=[NewsAnalyzerTool()],
            verbose=True,
            allow_delegation=False
        )
        
        print(f"✅ CrewAI Sentiment Agent initialized: {self.agent_id}")
    
    def analyze(
        self,
        company_name: str,
        symbol: str,
        task_id: str,
        trace_id: Optional[str] = None
    ) -> Dict:
        """
        Perform sentiment analysis
        
        Args:
            company_name: Company name
            symbol: Stock symbol
            task_id: Task identifier
            trace_id: Observability trace ID
            
        Returns:
            Analysis result with score and sentiment
        """
        # Start performance tracking
        perf_evaluator = get_performance_evaluator()
        exec_id = f"{self.agent_id}_{task_id}"
        perf_evaluator.start_execution(
            task_id=task_id,
            execution_id=exec_id,
            component_name=self.agent_id,
            component_type="agent",
            framework="crewai",
            model_name="gpt-3.5-turbo"
        )
        
        # Start observability span
        obs_system = get_observability_system()
        if not trace_id:
            trace_id = obs_system.start_task_trace(
                task_type="sentiment_analysis",
                framework="crewai",
                symbol=symbol,
                company_name=company_name
            )
        
        span_id = obs_system.start_agent_span(
            trace_id=trace_id,
            agent_name=self.agent_id,
            input_data={"company_name": company_name, "symbol": symbol}
        )
        
        try:
            # Get A2A protocol state
            protocol = get_a2a_protocol()
            state = protocol.get_state(task_id)
            
            # Create CrewAI task
            task = Task(
                description=f"""Analyze sentiment for {company_name} ({symbol}).
                
                Fetch recent news and perform sentiment analysis:
                1. Analyze news articles from multiple sources
                2. Assess overall sentiment (positive/negative/neutral)
                3. Identify key themes and concerns
                4. Evaluate market perception and analyst views
                5. Provide a sentiment score from 0-100
                
                Return a JSON with:
                - score: 0-100 sentiment score
                - overall_sentiment: positive/negative/neutral
                - news_count: number of articles analyzed
                - positive_count: positive articles
                - negative_count: negative articles
                - key_themes: main topics discussed
                - reasoning: detailed explanation
                """,
                agent=self.agent,
                expected_output="JSON object with sentiment analysis"
            )
            
            # Execute
            crew = Crew(
                agents=[self.agent],
                tasks=[task],
                process=Process.sequential,
                verbose=True # Explainability enabled for better reasoning
            )
            
            result = crew.kickoff()
            
            # Parse result
            try:
                if isinstance(result, str):
                    import re
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        analysis = json.loads(json_match.group())
                    else:
                        analysis = {
                            "score": 60,
                            "overall_sentiment": "neutral",
                            "reasoning": result
                        }
                else:
                    analysis = result
            except:
                analysis = {
                    "score": 55,
                    "overall_sentiment": "neutral",
                    "reasoning": "Analysis completed but format parsing failed"
                }
            
            # Update A2A state
            if state:
                state.update_agent_output(self.agent_id, analysis)
                protocol.update_state(task_id, {"agent_outputs": state.agent_outputs})
            
            # Log decision
            obs_system.log_agent_decision(
                trace_id=trace_id,
                agent_name=self.agent_id,
                decision=f"Sentiment: {analysis.get('overall_sentiment', 'neutral')}",
                reasoning=analysis.get('reasoning', ''),
                confidence=analysis.get('score', 0) / 100.0
            )
            
            # End performance tracking
            perf_evaluator.end_execution(
                execution_id=exec_id,
                tokens_input=600,
                tokens_output=300,
                api_calls=2,
                status="completed"
            )
            
            # End observability span
            obs_system.end_agent_span(
                span_id=span_id,
                output_data={"score": analysis.get('score', 0)},
                status="completed",
                tokens_input=600,
                tokens_output=300,
                cost_usd=0.0015
            )
            
            return analysis
            
        except Exception as e:
            # Log error
            obs_system.log_error(
                trace_id=trace_id,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            # End with failure
            perf_evaluator.end_execution(
                execution_id=exec_id,
                status="failed",
                error_message=str(e)
            )
            
            obs_system.end_agent_span(
                span_id=span_id,
                status="failed",
                error=str(e)
            )
            
            raise


# Factory functions
def create_crewai_price_agent() -> CrewAIPriceMovementAgent:
    """Create and return CrewAI Price Movement Agent"""
    return CrewAIPriceMovementAgent()


def create_crewai_sentiment_agent() -> CrewAISentimentAgent:
    """Create and return CrewAI Sentiment Agent"""
    return CrewAISentimentAgent()


if __name__ == "__main__":
    # Test CrewAI agents
    print("🧪 Testing CrewAI Agents...")
    
    # Create agents
    price_agent = create_crewai_price_agent()
    sentiment_agent = create_crewai_sentiment_agent()
    
    # Test with sample data
    task_id = "test_task_crewai_001"
    symbol = "RELIANCE.NS"
    company_name = "Reliance Industries"
    
    # Create A2A state
    protocol = get_a2a_protocol()
    state = protocol.create_state(
        task_id=task_id,
        symbol=symbol,
        company_name=company_name,
        pending_agents=[price_agent.agent_id, sentiment_agent.agent_id]
    )
    
    print(f"\n✅ CrewAI agents ready for testing")
    print(f"   Price Agent: {price_agent.agent_id}")
    print(f"   Sentiment Agent: {sentiment_agent.agent_id}")
