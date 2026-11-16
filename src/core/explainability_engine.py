"""
Explainability Engine for IPO Multi-Agent Framework
===================================================
Provides transparent reasoning traces and feature importance for all agent decisions.
"""
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
import json
from datetime import datetime


@dataclass
class FeatureContribution:
    """Individual feature's contribution to agent score."""
    feature_name: str
    value: Any
    contribution: float  # -100 to +100
    reasoning: str
    weight: float = 1.0


@dataclass
class AgentExplanation:
    """Complete explanation for a single agent's decision."""
    agent_name: str
    final_score: float
    confidence: float
    features: List[FeatureContribution] = field(default_factory=list)
    reasoning_chain: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'agent_name': self.agent_name,
            'final_score': round(self.final_score, 2),
            'confidence': round(self.confidence, 2),
            'features': [
                {
                    'name': f.feature_name,
                    'value': f.value,
                    'contribution': round(f.contribution, 2),
                    'reasoning': f.reasoning,
                    'weight': f.weight
                }
                for f in self.features
            ],
            'reasoning_chain': self.reasoning_chain,
            'data_sources': self.data_sources,
            'warnings': self.warnings,
            'timestamp': self.timestamp
        }


@dataclass
class OrchestratorExplanation:
    """Master explanation showing how all agents contributed to final decision."""
    final_decision: str
    overall_score: float
    confidence: float
    agent_explanations: Dict[str, AgentExplanation] = field(default_factory=dict)
    agent_weights: Dict[str, float] = field(default_factory=dict)
    weighted_contributions: Dict[str, float] = field(default_factory=dict)
    decision_reasoning: List[str] = field(default_factory=list)
    key_factors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'final_decision': self.final_decision,
            'overall_score': round(self.overall_score, 2),
            'confidence': round(self.confidence, 2),
            'agent_explanations': {
                name: exp.to_dict() 
                for name, exp in self.agent_explanations.items()
            },
            'agent_weights': {
                name: round(weight, 3) 
                for name, weight in self.agent_weights.items()
            },
            'weighted_contributions': {
                name: round(contrib, 2) 
                for name, contrib in self.weighted_contributions.items()
            },
            'decision_reasoning': self.decision_reasoning,
            'key_factors': self.key_factors,
            'risk_factors': self.risk_factors,
            'timestamp': self.timestamp
        }


class ExplainabilityEngine:
    """
    Generates human-readable explanations for agent decisions.
    Tracks feature importance, reasoning chains, and decision paths.
    """
    
    def __init__(self):
        self.agent_weights = {
            'Price Movement Agent': 0.20,
            'Macroeconomic Agent': 0.15,
            'Sentiment Agent': 0.20,
            'Risk Agent': 0.20,
            'IPO Intelligence Agent': 0.25
        }
    
    def explain_price_movement_agent(
        self, 
        score: float,
        listing_gain: float,
        current_return: float,
        volume_trend: str,
        volatility: float,
        technical_indicators: Dict
    ) -> AgentExplanation:
        """Generate explanation for Price Movement Agent."""
        features = []
        reasoning = []
        
        # Listing gain contribution
        if listing_gain > 20:
            contribution = +30
            reasoning.append(f"Strong listing gain of {listing_gain:.1f}% indicates high demand")
        elif listing_gain > 10:
            contribution = +15
            reasoning.append(f"Moderate listing gain of {listing_gain:.1f}%")
        elif listing_gain >= 0:
            contribution = 0
            reasoning.append(f"Modest listing gain of {listing_gain:.1f}%")
        else:
            contribution = -20
            reasoning.append(f"Negative listing day performance: {listing_gain:.1f}%")
        
        features.append(FeatureContribution(
            feature_name="Listing Day Gain (%)",
            value=f"{listing_gain:.1f}%",
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.4
        ))
        
        # Current return contribution
        if current_return > 15:
            contribution = +25
            reasoning.append(f"Excellent current returns of {current_return:.1f}%")
        elif current_return > 5:
            contribution = +10
            reasoning.append(f"Positive returns of {current_return:.1f}%")
        elif current_return >= -5:
            contribution = 0
            reasoning.append(f"Near break-even at {current_return:.1f}%")
        else:
            contribution = -15
            reasoning.append(f"Negative returns of {current_return:.1f}%")
        
        features.append(FeatureContribution(
            feature_name="Current Return (%)",
            value=f"{current_return:.1f}%",
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.35
        ))
        
        # Volume trend
        volume_mapping = {'High': +15, 'Medium': +5, 'Low': -10, 'Unknown': 0}
        contribution = volume_mapping.get(volume_trend, 0)
        reasoning.append(f"{volume_trend} trading volume " + 
                        ("supports price momentum" if contribution > 0 else "indicates weak interest"))
        
        features.append(FeatureContribution(
            feature_name="Volume Trend",
            value=volume_trend,
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.15
        ))
        
        # Volatility assessment
        if volatility < 10:
            contribution = +10
            reasoning.append(f"Low volatility ({volatility:.1f}%) indicates price stability")
        elif volatility < 20:
            contribution = 0
            reasoning.append(f"Moderate volatility ({volatility:.1f}%)")
        else:
            contribution = -10
            reasoning.append(f"High volatility ({volatility:.1f}%) increases risk")
        
        features.append(FeatureContribution(
            feature_name="Volatility (%)",
            value=f"{volatility:.1f}%",
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.10
        ))
        
        return AgentExplanation(
            agent_name="Price Movement Agent",
            final_score=score,
            confidence=0.85,
            features=features,
            reasoning_chain=reasoning,
            data_sources=["Yahoo Finance", "NSE Real-time Data"],
            warnings=["Price data subject to market volatility"] if volatility > 15 else []
        )
    
    def explain_sentiment_agent(
        self,
        score: float,
        news_sentiment: float,
        social_sentiment: float,
        analyst_recommendations: int,
        news_count: int,
        social_mentions: int
    ) -> AgentExplanation:
        """Generate explanation for Sentiment Agent."""
        features = []
        reasoning = []
        
        # News sentiment
        if news_sentiment > 0.6:
            contribution = +30
            reasoning.append(f"Highly positive news sentiment ({news_sentiment:.2f}) from {news_count} articles")
        elif news_sentiment > 0.2:
            contribution = +15
            reasoning.append(f"Moderately positive news coverage ({news_sentiment:.2f})")
        elif news_sentiment >= -0.2:
            contribution = 0
            reasoning.append(f"Neutral news sentiment ({news_sentiment:.2f})")
        else:
            contribution = -20
            reasoning.append(f"Negative news sentiment ({news_sentiment:.2f}) raises concerns")
        
        features.append(FeatureContribution(
            feature_name="News Sentiment Score",
            value=f"{news_sentiment:.2f}",
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.40
        ))
        
        # Social sentiment
        if social_sentiment > 0.5:
            contribution = +25
            reasoning.append(f"Strong community support ({social_mentions} mentions, {social_sentiment:.2f} score)")
        elif social_sentiment > 0.1:
            contribution = +10
            reasoning.append(f"Positive social buzz ({social_mentions} mentions)")
        elif social_sentiment >= -0.1:
            contribution = 0
            reasoning.append(f"Mixed social sentiment ({social_mentions} mentions)")
        else:
            contribution = -15
            reasoning.append(f"Negative social sentiment ({social_mentions} mentions)")
        
        features.append(FeatureContribution(
            feature_name="Social Media Sentiment",
            value=f"{social_sentiment:.2f}",
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.35
        ))
        
        # Analyst recommendations
        if analyst_recommendations >= 5:
            contribution = +20
            reasoning.append(f"{analyst_recommendations} analyst recommendations suggest institutional confidence")
        elif analyst_recommendations >= 2:
            contribution = +10
            reasoning.append(f"{analyst_recommendations} analyst reports provide coverage")
        else:
            contribution = 0
            reasoning.append(f"Limited analyst coverage ({analyst_recommendations} reports)")
        
        features.append(FeatureContribution(
            feature_name="Analyst Coverage",
            value=analyst_recommendations,
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.25
        ))
        
        warnings = []
        if news_count < 5:
            warnings.append("Limited news coverage may indicate low market interest")
        if social_mentions < 100:
            warnings.append("Low social media activity suggests limited retail attention")
        
        return AgentExplanation(
            agent_name="Sentiment Agent",
            final_score=score,
            confidence=0.75,
            features=features,
            reasoning_chain=reasoning,
            data_sources=["Google News", "Reddit", "Economic Times", "MoneyControl"],
            warnings=warnings
        )
    
    def explain_ipo_intelligence_agent(
        self,
        score: float,
        subscription_data: Dict,
        gmp: float,
        sector_performance: str,
        company_fundamentals: Dict
    ) -> AgentExplanation:
        """Generate explanation for IPO Intelligence Agent."""
        features = []
        reasoning = []
        
        # Subscription analysis
        total_sub = subscription_data.get('total', 0)
        qib_sub = subscription_data.get('qib', 0)
        retail_sub = subscription_data.get('retail', 0)
        
        if total_sub > 50:
            contribution = +35
            reasoning.append(f"Exceptional subscription: {total_sub:.1f}x (QIB: {qib_sub:.1f}x, Retail: {retail_sub:.1f}x)")
        elif total_sub > 20:
            contribution = +25
            reasoning.append(f"Strong subscription: {total_sub:.1f}x indicates high demand")
        elif total_sub > 5:
            contribution = +10
            reasoning.append(f"Moderate subscription: {total_sub:.1f}x")
        elif total_sub > 1:
            contribution = 0
            reasoning.append(f"Fully subscribed but modest demand: {total_sub:.1f}x")
        else:
            contribution = -25
            reasoning.append(f"Under-subscribed: {total_sub:.1f}x indicates weak demand")
        
        features.append(FeatureContribution(
            feature_name="Total Subscription (x)",
            value=f"{total_sub:.1f}x",
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.40
        ))
        
        # GMP (Grey Market Premium)
        if gmp > 50:
            contribution = +30
            reasoning.append(f"Very high GMP of ₹{gmp:.0f} suggests strong listing expectations")
        elif gmp > 20:
            contribution = +20
            reasoning.append(f"Positive GMP of ₹{gmp:.0f} indicates market optimism")
        elif gmp > 0:
            contribution = +5
            reasoning.append(f"Modest GMP of ₹{gmp:.0f}")
        elif gmp == 0:
            contribution = 0
            reasoning.append("No GMP data or trading at par")
        else:
            contribution = -15
            reasoning.append(f"Negative GMP of ₹{gmp:.0f} suggests caution")
        
        features.append(FeatureContribution(
            feature_name="Grey Market Premium (₹)",
            value=f"₹{gmp:.0f}",
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.25
        ))
        
        # Sector performance
        sector_map = {'Strong': +20, 'Moderate': +10, 'Weak': -10, 'Unknown': 0}
        contribution = sector_map.get(sector_performance, 0)
        reasoning.append(f"{sector_performance} sector performance " +
                        ("provides tailwinds" if contribution > 0 else "creates headwinds"))
        
        features.append(FeatureContribution(
            feature_name="Sector Trend",
            value=sector_performance,
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.20
        ))
        
        # Company fundamentals
        fundamentals_score = company_fundamentals.get('score', 50)
        if fundamentals_score > 70:
            contribution = +15
            reasoning.append(f"Strong fundamentals (score: {fundamentals_score}/100)")
        elif fundamentals_score > 50:
            contribution = +5
            reasoning.append(f"Adequate fundamentals (score: {fundamentals_score}/100)")
        else:
            contribution = -10
            reasoning.append(f"Weak fundamentals (score: {fundamentals_score}/100)")
        
        features.append(FeatureContribution(
            feature_name="Company Fundamentals",
            value=f"{fundamentals_score}/100",
            contribution=contribution,
            reasoning=reasoning[-1],
            weight=0.15
        ))
        
        warnings = []
        if qib_sub < 1:
            warnings.append("QIB under-subscription indicates institutional skepticism")
        if gmp < 0:
            warnings.append("Negative GMP suggests listing day losses likely")
        
        return AgentExplanation(
            agent_name="IPO Intelligence Agent",
            final_score=score,
            confidence=0.90,
            features=features,
            reasoning_chain=reasoning,
            data_sources=["NSE", "BSE", "IPO Watch", "Chittorgarh"],
            warnings=warnings
        )
    
    def generate_orchestrator_explanation(
        self,
        final_decision: str,
        overall_score: float,
        agent_scores: Dict[str, float],
        agent_explanations: Dict[str, AgentExplanation]
    ) -> OrchestratorExplanation:
        """Generate master explanation from all agent inputs."""
        
        # Calculate weighted contributions
        weighted_contributions = {}
        for agent_name, score in agent_scores.items():
            weight = self.agent_weights.get(agent_name, 0)
            weighted_contributions[agent_name] = score * weight
        
        # Generate decision reasoning
        decision_reasoning = [
            f"Final decision '{final_decision}' based on weighted analysis of {len(agent_scores)} specialized agents",
            f"Overall confidence score: {overall_score:.1f}/100",
        ]
        
        # Identify top contributing agents
        sorted_agents = sorted(
            weighted_contributions.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        decision_reasoning.append(
            f"Primary influence: {sorted_agents[0][0]} (contribution: {sorted_agents[0][1]:.1f})"
        )
        decision_reasoning.append(
            f"Secondary influence: {sorted_agents[1][0]} (contribution: {sorted_agents[1][1]:.1f})"
        )
        
        # Extract key factors from all agents
        key_factors = []
        risk_factors = []
        
        for agent_name, explanation in agent_explanations.items():
            # Top positive feature
            positive_features = [f for f in explanation.features if f.contribution > 0]
            if positive_features:
                top_positive = max(positive_features, key=lambda f: f.contribution)
                key_factors.append(f"{agent_name}: {top_positive.reasoning}")
            
            # Top negative feature
            negative_features = [f for f in explanation.features if f.contribution < 0]
            if negative_features:
                top_negative = min(negative_features, key=lambda f: f.contribution)
                risk_factors.append(f"{agent_name}: {top_negative.reasoning}")
            
            # Add warnings
            risk_factors.extend([f"{agent_name}: {w}" for w in explanation.warnings])
        
        # Decision threshold reasoning
        if overall_score >= 75:
            decision_reasoning.append("Score exceeds STRONG BUY threshold (75+): High confidence investment")
        elif overall_score >= 65:
            decision_reasoning.append("Score meets BUY threshold (65-75): Recommended for investment")
        elif overall_score >= 50:
            decision_reasoning.append("Score in HOLD range (50-65): Neutral stance, monitor closely")
        else:
            decision_reasoning.append("Score below 50: Risk factors dominate, cautious approach")
        
        return OrchestratorExplanation(
            final_decision=final_decision,
            overall_score=overall_score,
            confidence=min(0.95, sum(e.confidence for e in agent_explanations.values()) / len(agent_explanations)),
            agent_explanations=agent_explanations,
            agent_weights=self.agent_weights,
            weighted_contributions=weighted_contributions,
            decision_reasoning=decision_reasoning,
            key_factors=key_factors[:5],  # Top 5
            risk_factors=risk_factors[:5]   # Top 5
        )


# Singleton instance
_explainability_engine = None

def get_explainability_engine() -> ExplainabilityEngine:
    """Get or create singleton instance."""
    global _explainability_engine
    if _explainability_engine is None:
        _explainability_engine = ExplainabilityEngine()
    return _explainability_engine
