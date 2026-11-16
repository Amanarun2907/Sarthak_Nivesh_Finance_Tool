"""
Multi-Agent Orchestrator System
===============================
Main orchestration system integrating CrewAI, ADK, A2A protocol, observability, and all components

Requirements Fulfilled:
- Complete multi-agent orchestration (Requirement #11)
- Context sharing & state updates (Requirement #1)
- Structured output using Pydantic (Requirement #3)
- All agentic design patterns integrated
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import all systems
from a2a_protocol import get_a2a_protocol, AgentState
from observability_system import get_observability_system
from guardrails_security import get_guardrails_system
from explainability_engine import get_explainability_engine
from agent_control_tower import get_agent_control_tower
from performance_evaluator import get_performance_evaluator
from mcp_tools import get_mcp_registry

# Import agents
from crewai_agents import create_crewai_price_agent, create_crewai_sentiment_agent
from adk_agents import create_adk_risk_agent, create_adk_ipo_agent


class InvestmentRecommendation(BaseModel):
    """Structured output for investment recommendations"""
    
    # Identifiers
    task_id: str
    symbol: str
    company_name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Final decision
    recommendation: str = Field(..., description="BUY, SELL, HOLD, or AVOID")
    confidence_score: float = Field(..., ge=0, le=100, description="Overall confidence (0-100)")
    
    # Agent scores
    price_score: float = Field(..., ge=0, le=100)
    sentiment_score: float = Field(..., ge=0, le=100)
    risk_score: float = Field(..., ge=0, le=100)
    ipo_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Weighted contributions
    weighted_price: float
    weighted_sentiment: float
    weighted_risk: float
    weighted_ipo: Optional[float] = None
    
    # Summary
    key_strengths: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    reasoning: List[str] = Field(default_factory=list)
    
    # Performance metrics
    total_duration_seconds: float
    total_cost_usd: float
    total_tokens: int
    
    # Explainability
    explainability_report: Optional[Dict] = None
    
    # Compliance
    validation_passed: bool = True
    validation_warnings: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_001",
                "symbol": "RELIANCE.NS",
                "company_name": "Reliance Industries",
                "recommendation": "BUY",
                "confidence_score": 78.5,
                "price_score": 75.0,
                "sentiment_score": 82.0,
                "risk_score": 65.0,
                "reasoning": ["Strong technical indicators", "Positive sentiment"]
            }
        }


class MultiAgentOrchestrator:
    """
    Central orchestrator for the multi-agent system
    Coordinates CrewAI and ADK agents with full observability and guardrails
    """
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        print("🚀 Initializing Multi-Agent Orchestrator...")
        
        # Initialize all systems
        self.protocol = get_a2a_protocol()
        self.observability = get_observability_system()
        self.guardrails = get_guardrails_system()
        self.explainability = get_explainability_engine()
        self.control_tower = get_agent_control_tower()
        self.performance = get_performance_evaluator()
        self.mcp_registry = get_mcp_registry()
        
        # Initialize agents
        print("📦 Creating CrewAI agents...")
        self.price_agent = create_crewai_price_agent()
        self.sentiment_agent = create_crewai_sentiment_agent()
        
        print("📦 Creating ADK agents...")
        self.risk_agent = create_adk_risk_agent(api_key=anthropic_api_key)
        self.ipo_agent = create_adk_ipo_agent(api_key=anthropic_api_key)
        
        # Agent weights for final decision
        self.agent_weights = {
            "price": 0.25,
            "sentiment": 0.25,
            "risk": 0.25,
            "ipo": 0.25
        }
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        print("✅ Multi-Agent Orchestrator initialized successfully!")
    
    def analyze_stock(
        self,
        symbol: str,
        company_name: str,
        analysis_type: str = "comprehensive"
    ) -> InvestmentRecommendation:
        """
        Perform comprehensive multi-agent stock analysis
        
        Args:
            symbol: Stock symbol
            company_name: Company name
            analysis_type: 'comprehensive', 'quick', or 'ipo_focus'
            
        Returns:
            InvestmentRecommendation with structured output
        """
        # Generate unique task ID
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        print(f"\n{'='*80}")
        print(f"🎯 Starting Multi-Agent Analysis")
        print(f"   Task ID: {task_id}")
        print(f"   Symbol: {symbol}")
        print(f"   Company: {company_name}")
        print(f"   Type: {analysis_type}")
        print(f"{'='*80}\n")
        
        # ═══ STEP 1: Input Validation ═══
        print("🛡️ Step 1: Input Validation (Guardrails)")
        symbol_validation = self.guardrails.validate_input(symbol=symbol)
        name_validation = self.guardrails.validate_input(name=company_name)
        
        if not symbol_validation.passed or not name_validation.passed:
            raise ValueError(f"Input validation failed: {symbol_validation.message}, {name_validation.message}")
        
        print("✅ Input validation passed")
        
        # ═══ STEP 2: Initialize Tracking ═══
        print("\n📊 Step 2: Initialize Tracking Systems")
        
        # Start performance tracking
        self.performance.start_task(
            task_id=task_id,
            task_type=f"stock_analysis_{analysis_type}",
            symbol=symbol,
            company_name=company_name
        )
        
        # Start observability trace
        trace_id = self.observability.start_task_trace(
            task_type="multi_agent_analysis",
            framework="orchestrator",
            symbol=symbol,
            company_name=company_name
        )
        
        # Start control tower task
        self.control_tower.start_task(task_id, company_name, symbol)
        
        # Create A2A shared state
        state = self.protocol.create_state(
            task_id=task_id,
            symbol=symbol,
            company_name=company_name,
            user_query=f"Analyze {company_name} ({symbol})",
            analysis_type=analysis_type,
            pending_agents=[
                self.price_agent.agent_id,
                self.sentiment_agent.agent_id,
                self.risk_agent.agent_id,
                self.ipo_agent.agent_id
            ]
        )
        
        print("✅ Tracking systems initialized")
        
        # ═══ STEP 3: Parallel Agent Execution ═══
        print("\n🤖 Step 3: Execute Agents in Parallel")
        
        agent_results = {}
        
        try:
            # Execute agents in parallel using thread pool
            futures = {}
            
            # CrewAI Price Agent
            futures["price"] = self.executor.submit(
                self._execute_with_monitoring,
                self.price_agent.analyze,
                "price_agent",
                symbol=symbol,
                task_id=task_id,
                trace_id=trace_id
            )
            
            # CrewAI Sentiment Agent
            futures["sentiment"] = self.executor.submit(
                self._execute_with_monitoring,
                self.sentiment_agent.analyze,
                "sentiment_agent",
                company_name=company_name,
                symbol=symbol,
                task_id=task_id,
                trace_id=trace_id
            )
            
            # ADK Risk Agent
            futures["risk"] = self.executor.submit(
                self._execute_with_monitoring,
                self.risk_agent.analyze,
                "risk_agent",
                symbol=symbol,
                company_name=company_name,
                task_id=task_id,
                trace_id=trace_id
            )
            
            # ADK IPO Agent (if IPO focus)
            if analysis_type in ["comprehensive", "ipo_focus"]:
                futures["ipo"] = self.executor.submit(
                    self._execute_with_monitoring,
                    self.ipo_agent.analyze,
                    "ipo_agent",
                    company_name=company_name,
                    symbol=symbol,
                    task_id=task_id,
                    trace_id=trace_id
                )
            
            # Collect results as they complete
            for agent_name, future in futures.items():
                try:
                    result = future.result(timeout=120)  # 2 minute timeout per agent
                    agent_results[agent_name] = result
                    print(f"   ✅ {agent_name.capitalize()} Agent completed")
                except Exception as e:
                    print(f"   ❌ {agent_name.capitalize()} Agent failed: {e}")
                    agent_results[agent_name] = {"score": 50, "error": str(e)}
            
            print("\n✅ All agents completed execution")
            
        except Exception as e:
            print(f"\n❌ Agent execution error: {e}")
            raise
        
        # ═══ STEP 4: Aggregate & Weight Scores ═══
        print("\n🔢 Step 4: Aggregate Scores")
        
        price_score = agent_results.get("price", {}).get("score", 50)
        sentiment_score = agent_results.get("sentiment", {}).get("score", 50)
        risk_score = 100 - agent_results.get("risk", {}).get("score", 50)  # Invert risk
        ipo_score = agent_results.get("ipo", {}).get("score", None)
        
        # Calculate weighted scores
        weighted_price = price_score * self.agent_weights["price"]
        weighted_sentiment = sentiment_score * self.agent_weights["sentiment"]
        weighted_risk = risk_score * self.agent_weights["risk"]
        weighted_ipo = ipo_score * self.agent_weights["ipo"] if ipo_score else 0
        
        # Final confidence score
        if ipo_score:
            confidence_score = weighted_price + weighted_sentiment + weighted_risk + weighted_ipo
        else:
            # Redistribute IPO weight
            total_weight = self.agent_weights["price"] + self.agent_weights["sentiment"] + self.agent_weights["risk"]
            confidence_score = (weighted_price + weighted_sentiment + weighted_risk) / total_weight * 100
        
        print(f"   Price Score: {price_score:.1f} → Weighted: {weighted_price:.1f}")
        print(f"   Sentiment Score: {sentiment_score:.1f} → Weighted: {weighted_sentiment:.1f}")
        print(f"   Risk Score: {risk_score:.1f} → Weighted: {weighted_risk:.1f}")
        if ipo_score:
            print(f"   IPO Score: {ipo_score:.1f} → Weighted: {weighted_ipo:.1f}")
        print(f"   Final Confidence: {confidence_score:.1f}/100")
        
        # ═══ STEP 5: Generate Recommendation ═══
        print("\n💡 Step 5: Generate Recommendation")
        
        recommendation = self._determine_recommendation(confidence_score)
        print(f"   Recommendation: {recommendation}")
        
        # ═══ STEP 6: Extract Key Insights ═══
        print("\n📝 Step 6: Extract Key Insights")
        
        key_strengths = []
        key_risks = []
        reasoning = []
        
        # Extract from agent results
        for agent_name, result in agent_results.items():
            if "strengths" in result:
                key_strengths.extend(result["strengths"][:2])
            if "risk_factors" in result:
                key_risks.extend([rf["factor"] for rf in result["risk_factors"][:2]])
            if "concerns" in result:
                key_risks.extend(result["concerns"][:2])
            if "reasoning" in result:
                reasoning.append(f"{agent_name.capitalize()}: {result['reasoning'][:200]}")
        
        print(f"   Strengths: {len(key_strengths)}")
        print(f"   Risks: {len(key_risks)}")
        
        # ═══ STEP 7: Explainability Report ═══
        print("\n🔍 Step 7: Generate Explainability Report")
        
        explainability_report = {
            "final_decision": recommendation,
            "overall_score": round(confidence_score, 2),
            "agent_scores": {
                "price": round(price_score, 2),
                "sentiment": round(sentiment_score, 2),
                "risk": round(risk_score, 2),
                "ipo": round(ipo_score, 2) if ipo_score else None
            },
            "weighted_contributions": {
                "price": round(weighted_price, 2),
                "sentiment": round(weighted_sentiment, 2),
                "risk": round(weighted_risk, 2),
                "ipo": round(weighted_ipo, 2) if ipo_score else None
            },
            "transparency": "All agent decisions tracked via LangFuse observability",
            "auditability": f"Trace ID: {trace_id}"
        }
        
        print("✅ Explainability report generated")
        
        # ═══ STEP 8: Finalize Tracking ═══
        print("\n📊 Step 8: Finalize Tracking & Metrics")
        
        # End performance tracking
        perf_report = self.performance.end_task(task_id)
        
        # End observability trace
        self.observability.end_task_trace(
            trace_id=trace_id,
            output_data={"recommendation": recommendation, "confidence": confidence_score}
        )
        
        # Complete control tower task
        self.control_tower.complete_task(task_id, {"recommendation": recommendation})
        
        print(f"   Duration: {perf_report.total_duration_seconds:.2f}s")
        print(f"   Cost: ${perf_report.total_cost_usd:.4f}")
        print(f"   Tokens: {perf_report.total_tokens:,}")
        print(f"   Grade: {perf_report.performance_grade}")
        
        # ═══ STEP 9: Output Validation ═══
        print("\n🛡️ Step 9: Output Validation")
        
        validation_warnings = []
        recommendation_dict = {
            "action": recommendation,
            "confidence_score": confidence_score,
            "reasoning": reasoning
        }
        
        output_validation = self.guardrails.validate_output(recommendation=recommendation_dict)
        
        if not output_validation.passed:
            validation_warnings.append(output_validation.message)
            print(f"   ⚠️ Validation warning: {output_validation.message}")
        else:
            print("   ✅ Output validation passed")
        
        # ═══ STEP 10: Create Structured Output ═══
        print("\n📦 Step 10: Create Structured Output")
        
        final_recommendation = InvestmentRecommendation(
            task_id=task_id,
            symbol=symbol,
            company_name=company_name,
            recommendation=recommendation,
            confidence_score=confidence_score,
            price_score=price_score,
            sentiment_score=sentiment_score,
            risk_score=risk_score,
            ipo_score=ipo_score,
            weighted_price=weighted_price,
            weighted_sentiment=weighted_sentiment,
            weighted_risk=weighted_risk,
            weighted_ipo=weighted_ipo,
            key_strengths=key_strengths[:5],
            key_risks=key_risks[:5],
            reasoning=reasoning[:5],
            total_duration_seconds=perf_report.total_duration_seconds,
            total_cost_usd=perf_report.total_cost_usd,
            total_tokens=perf_report.total_tokens,
            explainability_report=explainability_report,
            validation_passed=output_validation.passed,
            validation_warnings=validation_warnings
        )
        
        print("✅ Structured output created")
        
        # ═══ FINAL SUMMARY ═══
        print(f"\n{'='*80}")
        print(f"🎉 Analysis Complete!")
        print(f"   Recommendation: {recommendation}")
        print(f"   Confidence: {confidence_score:.1f}%")
        print(f"   Duration: {perf_report.total_duration_seconds:.2f}s")
        print(f"   Cost: ${perf_report.total_cost_usd:.4f}")
        print(f"   Performance Grade: {perf_report.performance_grade}")
        print(f"{'='*80}\n")
        
        return final_recommendation
    
    def _execute_with_monitoring(
        self,
        agent_func: callable,
        agent_name: str,
        **kwargs
    ) -> Dict:
        """Execute agent with monitoring and error handling"""
        try:
            return agent_func(**kwargs)
        except Exception as e:
            print(f"   ❌ {agent_name} error: {e}")
            return {"score": 50, "error": str(e), "reasoning": f"Agent execution failed: {e}"}
    
    def _determine_recommendation(self, confidence_score: float) -> str:
        """Determine recommendation based on confidence score"""
        if confidence_score >= 80:
            return "STRONG BUY"
        elif confidence_score >= 65:
            return "BUY"
        elif confidence_score >= 50:
            return "HOLD"
        elif confidence_score >= 35:
            return "SELL"
        else:
            return "AVOID"
    
    def get_performance_summary(self) -> Dict:
        """Get overall performance summary"""
        return self.performance.get_summary_statistics()
    
    def export_recommendation_json(self, recommendation: InvestmentRecommendation) -> str:
        """Export recommendation as JSON"""
        return recommendation.model_dump_json(indent=2)
    
    def shutdown(self):
        """Graceful shutdown"""
        print("\n🛑 Shutting down Multi-Agent Orchestrator...")
        self.executor.shutdown(wait=True)
        self.observability.flush()
        print("✅ Shutdown complete")


# Singleton instance
_orchestrator = None

def get_orchestrator(anthropic_api_key: Optional[str] = None) -> MultiAgentOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator(anthropic_api_key=anthropic_api_key)
    return _orchestrator


if __name__ == "__main__":
    # Test the orchestrator
    print("🧪 Testing Multi-Agent Orchestrator\n")
    
    # Create orchestrator
    orchestrator = get_orchestrator()
    
    # Run analysis
    recommendation = orchestrator.analyze_stock(
        symbol="RELIANCE.NS",
        company_name="Reliance Industries",
        analysis_type="comprehensive"
    )
    
    # Print results
    print("\n📄 Final Recommendation (JSON):")
    print(orchestrator.export_recommendation_json(recommendation))
    
    # Get performance summary
    print("\n📈 Performance Summary:")
    summary = orchestrator.get_performance_summary()
    print(json.dumps(summary, indent=2))
    
    # Shutdown
    orchestrator.shutdown()
    
    print("\n✅ Test complete!")
