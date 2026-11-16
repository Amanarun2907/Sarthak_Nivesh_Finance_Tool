"""
Dynamic Exit Strategy Engine
============================
Real-time, adaptive exit signals based on live market data, technical indicators,
and AI-powered risk management.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math


class ExitSignalType(Enum):
    """Types of exit signals."""
    PROFIT_TARGET = "profit_target"
    STOP_LOSS = "stop_loss"
    TRAILING_STOP = "trailing_stop"
    TIME_BASED = "time_based"
    TECHNICAL = "technical"
    NEWS_DRIVEN = "news_driven"
    VOLUME_DECLINE = "volume_decline"
    MOMENTUM_REVERSAL = "momentum_reversal"


@dataclass
class ExitSignal:
    """Individual exit signal with reasoning."""
    signal_type: ExitSignalType
    severity: str  # 'critical', 'high', 'medium', 'low'
    action: str  # 'exit_full', 'exit_partial_75', 'exit_partial_50', 'exit_partial_25', 'monitor'
    reasoning: str
    triggered_at: float  # price at which signal triggered
    current_price: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'signal_type': self.signal_type.value,
            'severity': self.severity,
            'action': self.action,
            'reasoning': self.reasoning,
            'triggered_at': round(self.triggered_at, 2),
            'current_price': round(self.current_price, 2),
            'timestamp': self.timestamp
        }


@dataclass
class ExitStrategy:
    """Complete exit strategy with dynamic parameters."""
    ipo_name: str
    symbol: str
    entry_price: float
    current_price: float
    position_size: int
    days_held: int
    
    # Dynamic thresholds
    profit_target_1: float  # 25% exit
    profit_target_2: float  # 50% exit
    profit_target_3: float  # 75% exit
    stop_loss: float
    trailing_stop_pct: float
    
    # Current state
    current_return_pct: float = 0.0
    unrealized_pnl: float = 0.0
    highest_price_seen: float = 0.0
    trailing_stop_price: float = 0.0
    
    # Signals
    active_signals: List[ExitSignal] = field(default_factory=list)
    executed_exits: List[Dict] = field(default_factory=list)
    
    # Recommendations
    recommended_action: str = "HOLD"
    confidence: float = 0.0
    reasoning: List[str] = field(default_factory=list)
    
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            'ipo_name': self.ipo_name,
            'symbol': self.symbol,
            'entry_price': round(self.entry_price, 2),
            'current_price': round(self.current_price, 2),
            'position_size': self.position_size,
            'days_held': self.days_held,
            'profit_target_1': round(self.profit_target_1, 2),
            'profit_target_2': round(self.profit_target_2, 2),
            'profit_target_3': round(self.profit_target_3, 2),
            'stop_loss': round(self.stop_loss, 2),
            'trailing_stop_pct': round(self.trailing_stop_pct, 2),
            'current_return_pct': round(self.current_return_pct, 2),
            'unrealized_pnl': round(self.unrealized_pnl, 2),
            'highest_price_seen': round(self.highest_price_seen, 2),
            'trailing_stop_price': round(self.trailing_stop_price, 2),
            'active_signals': [s.to_dict() for s in self.active_signals],
            'executed_exits': self.executed_exits,
            'recommended_action': self.recommended_action,
            'confidence': round(self.confidence, 2),
            'reasoning': self.reasoning,
            'timestamp': self.timestamp
        }


class DynamicExitEngine:
    """
    Advanced exit strategy engine with real-time adaptation.
    """
    
    def __init__(self):
        self.strategies: Dict[str, ExitStrategy] = {}
    
    def create_exit_strategy(
        self,
        ipo_name: str,
        symbol: str,
        entry_price: float,
        current_price: float,
        position_size: int,
        days_held: int,
        risk_profile: str = "moderate"
    ) -> ExitStrategy:
        """
        Create a dynamic exit strategy tailored to the IPO and risk profile.
        
        Risk profiles:
        - conservative: Tight stops, quick profit booking
        - moderate: Balanced approach
        - aggressive: Wide stops, higher targets
        """
        
        # Calculate dynamic targets based on risk profile
        if risk_profile == "conservative":
            profit_targets = [
                entry_price * 1.10,  # 10% for 25% exit
                entry_price * 1.15,  # 15% for 50% exit
                entry_price * 1.20,  # 20% for 75% exit
            ]
            stop_loss = entry_price * 0.95  # 5% stop loss
            trailing_stop_pct = 3.0  # 3% trailing stop
            
        elif risk_profile == "aggressive":
            profit_targets = [
                entry_price * 1.25,  # 25% for 25% exit
                entry_price * 1.40,  # 40% for 50% exit
                entry_price * 1.60,  # 60% for 75% exit
            ]
            stop_loss = entry_price * 0.90  # 10% stop loss
            trailing_stop_pct = 7.0  # 7% trailing stop
            
        else:  # moderate
            profit_targets = [
                entry_price * 1.15,  # 15% for 25% exit
                entry_price * 1.25,  # 25% for 50% exit
                entry_price * 1.35,  # 35% for 75% exit
            ]
            stop_loss = entry_price * 0.92  # 8% stop loss
            trailing_stop_pct = 5.0  # 5% trailing stop
        
        # Adjust for listing day premium
        listing_gain = ((current_price - entry_price) / entry_price) * 100
        if listing_gain > 30:  # High listing gain
            # Tighten stop loss to protect gains
            stop_loss = max(stop_loss, entry_price * 1.10)
            trailing_stop_pct = min(trailing_stop_pct, 4.0)
        
        # Calculate current metrics
        current_return_pct = ((current_price - entry_price) / entry_price) * 100
        unrealized_pnl = (current_price - entry_price) * position_size
        highest_price = max(entry_price, current_price)
        trailing_stop_price = highest_price * (1 - trailing_stop_pct / 100)
        
        strategy = ExitStrategy(
            ipo_name=ipo_name,
            symbol=symbol,
            entry_price=entry_price,
            current_price=current_price,
            position_size=position_size,
            days_held=days_held,
            profit_target_1=profit_targets[0],
            profit_target_2=profit_targets[1],
            profit_target_3=profit_targets[2],
            stop_loss=stop_loss,
            trailing_stop_pct=trailing_stop_pct,
            highest_price_seen=highest_price,
            trailing_stop_price=trailing_stop_price,
            current_return_pct=current_return_pct,
            unrealized_pnl=unrealized_pnl
        )
        
        # Store strategy
        self.strategies[symbol] = strategy
        
        return strategy
    
    def update_strategy(
        self,
        symbol: str,
        current_price: float,
        volume: Optional[int] = None,
        volatility: Optional[float] = None,
        news_sentiment: Optional[float] = None,
        technical_indicators: Optional[Dict] = None
    ) -> ExitStrategy:
        """
        Update strategy with real-time data and generate exit signals.
        """
        
        if symbol not in self.strategies:
            raise ValueError(f"No strategy found for {symbol}")
        
        strategy = self.strategies[symbol]
        strategy.current_price = current_price
        strategy.days_held += 1
        
        # Update highest price and trailing stop
        if current_price > strategy.highest_price_seen:
            strategy.highest_price_seen = current_price
            strategy.trailing_stop_price = current_price * (1 - strategy.trailing_stop_pct / 100)
        
        # Calculate current returns
        strategy.current_return_pct = ((current_price - strategy.entry_price) / strategy.entry_price) * 100
        strategy.unrealized_pnl = (current_price - strategy.entry_price) * strategy.position_size
        
        # Update current price in the strategy
        strategy.current_price = current_price
        
        # Clear previous signals
        strategy.active_signals = []
        strategy.reasoning = []
        
        # ── Signal Generation ─────────────────────────────────────────────────
        
        # 1. Stop Loss Signal
        if current_price <= strategy.stop_loss:
            strategy.active_signals.append(ExitSignal(
                signal_type=ExitSignalType.STOP_LOSS,
                severity='critical',
                action='exit_full',
                reasoning=f"Price ₹{current_price:.2f} breached stop loss at ₹{strategy.stop_loss:.2f}. Exit immediately to limit losses.",
                triggered_at=strategy.stop_loss,
                current_price=current_price
            ))
            strategy.reasoning.append("⚠️ STOP LOSS TRIGGERED - Exit entire position")
        
        # 2. Trailing Stop Signal
        if current_price <= strategy.trailing_stop_price:
            strategy.active_signals.append(ExitSignal(
                signal_type=ExitSignalType.TRAILING_STOP,
                severity='high',
                action='exit_partial_75',
                reasoning=f"Price ₹{current_price:.2f} hit trailing stop at ₹{strategy.trailing_stop_price:.2f}. Protect profits from peak of ₹{strategy.highest_price_seen:.2f}.",
                triggered_at=strategy.trailing_stop_price,
                current_price=current_price
            ))
            strategy.reasoning.append(f"📉 Trailing stop hit - Book 75% at {strategy.current_return_pct:.1f}% return")
        
        # 3. Profit Target Signals
        if current_price >= strategy.profit_target_3:
            strategy.active_signals.append(ExitSignal(
                signal_type=ExitSignalType.PROFIT_TARGET,
                severity='medium',
                action='exit_partial_75',
                reasoning=f"Price ₹{current_price:.2f} exceeded target 3 at ₹{strategy.profit_target_3:.2f}. Book major profits.",
                triggered_at=strategy.profit_target_3,
                current_price=current_price
            ))
            strategy.reasoning.append(f"🎯 Target 3 achieved - Book 75% profits at {strategy.current_return_pct:.1f}%")
            
        elif current_price >= strategy.profit_target_2:
            strategy.active_signals.append(ExitSignal(
                signal_type=ExitSignalType.PROFIT_TARGET,
                severity='medium',
                action='exit_partial_50',
                reasoning=f"Price ₹{current_price:.2f} reached target 2 at ₹{strategy.profit_target_2:.2f}. Lock in half position.",
                triggered_at=strategy.profit_target_2,
                current_price=current_price
            ))
            strategy.reasoning.append(f"🎯 Target 2 achieved - Book 50% profits at {strategy.current_return_pct:.1f}%")
            
        elif current_price >= strategy.profit_target_1:
            strategy.active_signals.append(ExitSignal(
                signal_type=ExitSignalType.PROFIT_TARGET,
                severity='low',
                action='exit_partial_25',
                reasoning=f"Price ₹{current_price:.2f} hit target 1 at ₹{strategy.profit_target_1:.2f}. Consider booking partial profits.",
                triggered_at=strategy.profit_target_1,
                current_price=current_price
            ))
            strategy.reasoning.append(f"🎯 Target 1 achieved - Consider booking 25% at {strategy.current_return_pct:.1f}%")
        
        # 4. Time-Based Signals
        if strategy.days_held >= 30 and strategy.current_return_pct < 5:
            strategy.active_signals.append(ExitSignal(
                signal_type=ExitSignalType.TIME_BASED,
                severity='medium',
                action='exit_partial_50',
                reasoning=f"Held for {strategy.days_held} days with only {strategy.current_return_pct:.1f}% return. Consider redeployment.",
                triggered_at=current_price,
                current_price=current_price
            ))
            strategy.reasoning.append(f"⏰ Long hold with minimal gains - Review position")
        
        # 5. Volume-Based Signals
        if volume is not None:
            avg_volume = 1000000  # Placeholder: should come from historical data
            if volume < avg_volume * 0.3:
                strategy.active_signals.append(ExitSignal(
                    signal_type=ExitSignalType.VOLUME_DECLINE,
                    severity='low',
                    action='monitor',
                    reasoning=f"Volume dropped to {volume:,} (70% below average). Indicates weak interest.",
                    triggered_at=current_price,
                    current_price=current_price
                ))
                strategy.reasoning.append("📊 Low volume - Monitor for liquidity issues")
        
        # 6. Volatility-Based Signals
        if volatility is not None and volatility > 25:
            strategy.active_signals.append(ExitSignal(
                signal_type=ExitSignalType.TECHNICAL,
                severity='medium',
                action='exit_partial_25',
                reasoning=f"High volatility ({volatility:.1f}%) increases risk. Consider reducing exposure.",
                triggered_at=current_price,
                current_price=current_price
            ))
            strategy.reasoning.append(f"📈 High volatility ({volatility:.1f}%) - Reduce exposure")
        
        # 7. News Sentiment Signal
        if news_sentiment is not None and news_sentiment < -0.5:
            strategy.active_signals.append(ExitSignal(
                signal_type=ExitSignalType.NEWS_DRIVEN,
                severity='high',
                action='exit_partial_50',
                reasoning=f"Negative news sentiment ({news_sentiment:.2f}) suggests deteriorating outlook.",
                triggered_at=current_price,
                current_price=current_price
            ))
            strategy.reasoning.append(f"📰 Negative news ({news_sentiment:.2f}) - Exit 50%")
        
        # 8. Technical Indicators (RSI, MACD)
        if technical_indicators:
            rsi = technical_indicators.get('rsi')
            macd_signal = technical_indicators.get('macd_signal')
            
            if rsi and rsi > 70:
                strategy.active_signals.append(ExitSignal(
                    signal_type=ExitSignalType.TECHNICAL,
                    severity='medium',
                    action='exit_partial_25',
                    reasoning=f"RSI overbought ({rsi:.1f}) suggests potential correction.",
                    triggered_at=current_price,
                    current_price=current_price
                ))
                strategy.reasoning.append(f"📊 RSI overbought ({rsi:.1f}) - Book partial profits")
            
            if macd_signal == 'bearish_crossover':
                strategy.active_signals.append(ExitSignal(
                    signal_type=ExitSignalType.MOMENTUM_REVERSAL,
                    severity='medium',
                    action='exit_partial_50',
                    reasoning="MACD bearish crossover indicates momentum reversal.",
                    triggered_at=current_price,
                    current_price=current_price
                ))
                strategy.reasoning.append("📉 MACD bearish crossover - Exit 50%")
        
        # ── Determine Final Recommendation ────────────────────────────────────
        
        critical_signals = [s for s in strategy.active_signals if s.severity == 'critical']
        high_signals = [s for s in strategy.active_signals if s.severity == 'high']
        medium_signals = [s for s in strategy.active_signals if s.severity == 'medium']
        
        if critical_signals:
            strategy.recommended_action = "EXIT_FULL"
            strategy.confidence = 0.95
            strategy.reasoning.insert(0, "🚨 CRITICAL EXIT REQUIRED")
            
        elif len(high_signals) >= 2 or (high_signals and len(medium_signals) >= 2):
            strategy.recommended_action = "EXIT_75"
            strategy.confidence = 0.85
            strategy.reasoning.insert(0, "⚠️ MAJOR EXIT RECOMMENDED")
            
        elif len(high_signals) == 1 or len(medium_signals) >= 3:
            strategy.recommended_action = "EXIT_50"
            strategy.confidence = 0.75
            strategy.reasoning.insert(0, "📊 PARTIAL EXIT SUGGESTED")
            
        elif len(medium_signals) >= 1:
            strategy.recommended_action = "EXIT_25"
            strategy.confidence = 0.65
            strategy.reasoning.insert(0, "💡 CONSIDER PARTIAL BOOKING")
            
        else:
            strategy.recommended_action = "HOLD"
            strategy.confidence = 0.80
            strategy.reasoning.insert(0, f"✅ HOLD - Current return: {strategy.current_return_pct:.1f}%")
        
        strategy.timestamp = datetime.now().isoformat()
        
        return strategy
    
    def get_strategy(self, symbol: str) -> Optional[ExitStrategy]:
        """Get current exit strategy for a symbol."""
        return self.strategies.get(symbol)
    
    def execute_exit(self, symbol: str, exit_percentage: int, execution_price: float) -> Dict:
        """Record an executed exit."""
        if symbol not in self.strategies:
            raise ValueError(f"No strategy found for {symbol}")
        
        strategy = self.strategies[symbol]
        
        exit_record = {
            'timestamp': datetime.now().isoformat(),
            'exit_percentage': exit_percentage,
            'execution_price': execution_price,
            'pnl_realized': (execution_price - strategy.entry_price) * strategy.position_size * (exit_percentage / 100),
            'return_pct': ((execution_price - strategy.entry_price) / strategy.entry_price) * 100,
            'reason': strategy.recommended_action
        }
        
        strategy.executed_exits.append(exit_record)
        strategy.position_size = int(strategy.position_size * (1 - exit_percentage / 100))
        
        return exit_record


# Singleton instance
_exit_engine = None

def get_dynamic_exit_engine() -> DynamicExitEngine:
    """Get or create singleton instance."""
    global _exit_engine
    if _exit_engine is None:
        _exit_engine = DynamicExitEngine()
    return _exit_engine
