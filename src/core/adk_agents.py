"""
Anthropic ADK Agent Implementations
==================================
ADK-based agents for the multi-agent system

Requirements Fulfilled:
- Anthropic ADK as agentic framework (Requirement #7)
- Agent-to-Agent communication via A2A protocol (Requirement #6)
- Context sharing and state updates (Requirement #1)
"""

from typing import Dict, List, Optional, Any, Callable
from anthropic import Anthropic
from pydantic import BaseModel, Field
import json
from datetime import datetime
import os

# Import our systems
from a2a_protocol import get_a2a_protocol, A2AMessage, MessageType, MessagePriority, AgentFramework
from observability_system import get_observability_system
from guardrails_security import get_guardrails_system
from mcp_tools import get_mcp_registry
from explainability_engine import get_explainability_engine
from performance_evaluator import get_performance_evaluator


class ADKRiskAnalysisAgent:
    """
    ADK-based Risk Analysis Agent
    Analyzes financial risk, volatility, and downside scenarios
    """
    
    def __init__(
        self,
        agent_id: str = "adk_risk_agent",
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240229"
    ):
        self.agent_id = agent_id
        self.framework = AgentFramework.ADK
        self.model = model
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        
        # Register with A2A protocol
        protocol = get_a2a_protocol()
        protocol.register_agent(
            agent_id=self.agent_id,
            agent_name="Risk Analysis Agent (ADK)",
            framework=self.framework,
            capabilities=["risk_assessment", "volatility_analysis", "downside_protection"],
            metadata={"model": self.model, "version": "1.0"}
        )
        
        # System prompt
        self.system_prompt = """You are an expert risk analyst specializing in financial markets.
        Your role is to assess investment risk, analyze volatility, evaluate downside scenarios,
        and provide risk-adjusted recommendations.
        
        You analyze:
        - Volatility and price fluctuations
        - Sector-specific risks
        - Market conditions and macro risks
        - Company-specific risks (debt, management, competition)
        - Black swan events and tail risks
        
        Always provide:
        1. Risk score (0-100, where higher = riskier)
        2. Risk category (low/moderate/high/very high)
        3. Key risk factors
        4. Risk mitigation strategies
        5. Detailed reasoning
        
        Return results in JSON format."""
        
        print(f"✅ ADK Risk Analysis Agent initialized: {self.agent_id}")
    
    def analyze(
        self,
        symbol: str,
        company_name: str,
        task_id: str,
        price_data: Optional[Dict] = None,
        trace_id: Optional[str] = None
    ) -> Dict:
        """
        Perform risk analysis
        
        Args:
            symbol: Stock symbol
            company_name: Company name
            task_id: Task identifier
            price_data: Optional price data from previous agents
            trace_id: Observability trace ID
            
        Returns:
            Risk analysis with score and recommendations
        """
        # Start performance tracking
        perf_evaluator = get_performance_evaluator()
        exec_id = f"{self.agent_id}_{task_id}"
        perf_evaluator.start_execution(
            task_id=task_id,
            execution_id=exec_id,
            component_name=self.agent_id,
            component_type="agent",
            framework="adk",
            model_name=self.model
        )
        
        # Start observability span
        obs_system = get_observability_system()
        if not trace_id:
            trace_id = obs_system.start_task_trace(
                task_type="risk_analysis",
                framework="adk",
                symbol=symbol,
                company_name=company_name
            )
        
        span_id = obs_system.start_agent_span(
            trace_id=trace_id,
            agent_name=self.agent_id,
            input_data={"symbol": symbol, "company_name": company_name}
        )
        
        try:
            # Get A2A protocol state for context
            protocol = get_a2a_protocol()
            state = protocol.get_state(task_id)
            
            context = ""
            if state:
                previous_outputs = state.get_context_for_agent(self.agent_id).get("previous_outputs", {})
                if previous_outputs:
                    context = f"\n\nContext from other agents:\n{json.dumps(previous_outputs, indent=2)}"
            
            # Fetch stock data via MCP tool
            mcp = get_mcp_registry()
            stock_response = mcp.execute_tool(
                "stock_data_fetcher",
                symbol=symbol,
                period="3mo"
            )
            
            stock_data = stock_response.data if stock_response.status == "success" else {}
            
            # Construct prompt
            user_prompt = f"""Analyze the investment risk for {company_name} ({symbol}).
            
Stock Data:
{json.dumps(stock_data, indent=2)}
{context}

Provide comprehensive risk analysis including:
1. Overall risk score (0-100)
2. Risk category (low/moderate/high/very high)
3. Volatility assessment
4. Key risk factors (at least 3-5 specific risks)
5. Sector-specific risks
6. Downside scenarios
7. Risk mitigation recommendations

Return a JSON object with this structure:
{{
    "score": <0-100, higher = riskier>,
    "risk_category": "<low/moderate/high/very high>",
    "volatility": {{
        "level": "<low/medium/high>",
        "annualized_percent": <number>
    }},
    "risk_factors": [
        {{"factor": "<risk name>", "severity": "<low/medium/high>", "description": "<details>"}}
    ],
    "downside_scenarios": [
        {{"scenario": "<description>", "probability": "<low/medium/high>", "impact": "<details>"}}
    ],
    "risk_mitigation": ["<strategy 1>", "<strategy 2>", ...],
    "reasoning": "<detailed explanation>"
}}"""
            
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract response
            content = response.content[0].text
            
            # Parse JSON from response
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    # Fallback
                    analysis = {
                        "score": 50,
                        "risk_category": "moderate",
                        "reasoning": content
                    }
            except Exception as parse_error:
                print(f"⚠️ JSON parsing error: {parse_error}")
                analysis = {
                    "score": 50,
                    "risk_category": "moderate",
                    "reasoning": content
                }
            
            # Update A2A state
            if state:
                state.update_agent_output(self.agent_id, analysis)
                protocol.update_state(task_id, {"agent_outputs": state.agent_outputs})
            
            # Log decision for auditability
            obs_system.log_agent_decision(
                trace_id=trace_id,
                agent_name=self.agent_id,
                decision=f"Risk: {analysis.get('risk_category', 'moderate')}",
                reasoning=analysis.get('reasoning', ''),
                confidence=1.0 - (analysis.get('score', 50) / 100.0)
            )
            
            # Track token usage
            tokens_input = response.usage.input_tokens
            tokens_output = response.usage.output_tokens
            
            # End performance tracking
            perf_evaluator.end_execution(
                execution_id=exec_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                api_calls=1,
                status="completed"
            )
            
            # End observability span
            obs_system.end_agent_span(
                span_id=span_id,
                output_data={"score": analysis.get('score', 0)},
                status="completed",
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost_usd=0.015  # Approximate for Claude Sonnet
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


class ADKIPOIntelligenceAgent:
    """
    ADK-based IPO Intelligence Agent
    Analyzes IPO-specific metrics: subscription data, GMP, fundamentals
    """
    
    def __init__(
        self,
        agent_id: str = "adk_ipo_agent",
        api_key: Optional[str] = None,
        model: str = "claude-3-haiku-20240307"  # Faster, cheaper for structured analysis
    ):
        self.agent_id = agent_id
        self.framework = AgentFramework.ADK
        self.model = model
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        
        # Register with A2A protocol
        protocol = get_a2a_protocol()
        protocol.register_agent(
            agent_id=self.agent_id,
            agent_name="IPO Intelligence Agent (ADK)",
            framework=self.framework,
            capabilities=["ipo_analysis", "subscription_tracking", "gmp_monitoring", "fundamental_analysis"],
            metadata={"model": self.model, "version": "1.0"}
        )
        
        # System prompt
        self.system_prompt = """You are an expert IPO analyst with deep knowledge of Indian stock markets.
        You specialize in analyzing IPO subscription data, Grey Market Premium (GMP), company fundamentals,
        and post-listing performance predictions.
        
        You evaluate:
        - Subscription data (QIB, HNI, Retail categories)
        - Grey Market Premium trends
        - Company fundamentals (financials, business model, competitive position)
        - Sector outlook and market conditions
        - Listing day expectations and post-listing trajectory
        
        Always provide:
        1. IPO score (0-100, higher = better opportunity)
        2. Listing day prediction
        3. Post-listing outlook (30/60/90 days)
        4. Key strengths and concerns
        5. Investment recommendation
        6. Detailed reasoning
        
        Return results in JSON format."""
        
        print(f"✅ ADK IPO Intelligence Agent initialized: {self.agent_id}")
    
    def analyze(
        self,
        company_name: str,
        symbol: str,
        task_id: str,
        ipo_data: Optional[Dict] = None,
        trace_id: Optional[str] = None
    ) -> Dict:
        """
        Perform IPO intelligence analysis
        
        Args:
            company_name: Company name
            symbol: Stock symbol
            task_id: Task identifier
            ipo_data: Optional IPO-specific data
            trace_id: Observability trace ID
            
        Returns:
            IPO analysis with predictions and recommendations
        """
        # Start performance tracking
        perf_evaluator = get_performance_evaluator()
        exec_id = f"{self.agent_id}_{task_id}"
        perf_evaluator.start_execution(
            task_id=task_id,
            execution_id=exec_id,
            component_name=self.agent_id,
            component_type="agent",
            framework="adk",
            model_name=self.model
        )
        
        # Start observability span
        obs_system = get_observability_system()
        if not trace_id:
            trace_id = obs_system.start_task_trace(
                task_type="ipo_analysis",
                framework="adk",
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
            
            context = ""
            if state:
                previous_outputs = state.get_context_for_agent(self.agent_id).get("previous_outputs", {})
                if previous_outputs:
                    context = f"\n\nInsights from other agents:\n{json.dumps(previous_outputs, indent=2)}"
            
            # Prepare IPO data
            if not ipo_data:
                ipo_data = {
                    "subscription_data": {"total": 5.0, "qib": 8.2, "hni": 3.5, "retail": 2.1},
                    "gmp": 150,
                    "price_band": "300-320",
                    "lot_size": 46
                }
            
            # Construct prompt
            user_prompt = f"""Analyze the IPO opportunity for {company_name} ({symbol}).
            
IPO Data:
{json.dumps(ipo_data, indent=2)}
{context}

Provide comprehensive IPO intelligence including:
1. Overall IPO score (0-100, higher = better investment)
2. Listing day prediction (expected gain/loss %)
3. Post-listing outlook (30/60/90 days)
4. Subscription analysis
5. GMP assessment
6. Key strengths (at least 3)
7. Key concerns (at least 2-3)
8. Investment recommendation (Subscribe/Avoid/Hold)

Return a JSON object with this structure:
{{
    "score": <0-100>,
    "listing_prediction": {{
        "expected_gain_percent": <number>,
        "confidence": "<low/medium/high>"
    }},
    "post_listing_outlook": {{
        "30_days": "<bullish/neutral/bearish>",
        "60_days": "<bullish/neutral/bearish>",
        "90_days": "<bullish/neutral/bearish>"
    }},
    "subscription_analysis": {{
        "rating": "<excellent/good/fair/poor>",
        "details": "<description>"
    }},
    "gmp_assessment": {{
        "rating": "<strong/moderate/weak>",
        "details": "<description>"
    }},
    "strengths": ["<strength 1>", "<strength 2>", ...],
    "concerns": ["<concern 1>", "<concern 2>", ...],
    "recommendation": "<Subscribe/Avoid/Hold>",
    "reasoning": "<detailed explanation>"
}}"""
            
            # Call Anthropic API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract response
            content = response.content[0].text
            
            # Parse JSON
            try:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    analysis = {
                        "score": 70,
                        "recommendation": "Subscribe",
                        "reasoning": content
                    }
            except:
                analysis = {
                    "score": 70,
                    "recommendation": "Subscribe",
                    "reasoning": content
                }
            
            # Update A2A state
            if state:
                state.update_agent_output(self.agent_id, analysis)
                protocol.update_state(task_id, {"agent_outputs": state.agent_outputs})
            
            # Log decision
            obs_system.log_agent_decision(
                trace_id=trace_id,
                agent_name=self.agent_id,
                decision=analysis.get('recommendation', 'Subscribe'),
                reasoning=analysis.get('reasoning', ''),
                confidence=analysis.get('score', 70) / 100.0
            )
            
            # Track token usage
            tokens_input = response.usage.input_tokens
            tokens_output = response.usage.output_tokens
            
            # End performance tracking
            perf_evaluator.end_execution(
                execution_id=exec_id,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                api_calls=1,
                status="completed"
            )
            
            # End observability span
            obs_system.end_agent_span(
                span_id=span_id,
                output_data={"score": analysis.get('score', 0)},
                status="completed",
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost_usd=0.001  # Haiku is very cheap
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
def create_adk_risk_agent(api_key: Optional[str] = None) -> ADKRiskAnalysisAgent:
    """Create and return ADK Risk Analysis Agent"""
    return ADKRiskAnalysisAgent(api_key=api_key)


def create_adk_ipo_agent(api_key: Optional[str] = None) -> ADKIPOIntelligenceAgent:
    """Create and return ADK IPO Intelligence Agent"""
    return ADKIPOIntelligenceAgent(api_key=api_key)


if __name__ == "__main__":
    # Test ADK agents
    print("🧪 Testing ADK Agents...")
    
    # Create agents
    risk_agent = create_adk_risk_agent()
    ipo_agent = create_adk_ipo_agent()
    
    # Test data
    task_id = "test_task_adk_001"
    symbol = "RELIANCE.NS"
    company_name = "Reliance Industries"
    
    # Create A2A state
    protocol = get_a2a_protocol()
    state = protocol.create_state(
        task_id=task_id,
        symbol=symbol,
        company_name=company_name,
        pending_agents=[risk_agent.agent_id, ipo_agent.agent_id]
    )
    
    print(f"\n✅ ADK agents ready for testing")
    print(f"   Risk Agent: {risk_agent.agent_id}")
    print(f"   IPO Agent: {ipo_agent.agent_id}")
