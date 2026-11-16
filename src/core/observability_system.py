"""
LangFuse Observability System for Sarthak Nivesh
===============================================
Complete tracing, auditability, and provenance tracking for all agent operations

Requirements Fulfilled:
- Observability mechanism with tracing for auditability and provenance (Requirement #9)
- Task Monitoring & Logging using Callback functions (Requirement #5)
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
try:
    from langfuse import Langfuse
    from langfuse.decorators import observe, langfuse_context
except ImportError:
    Langfuse = None
    def observe(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator
    class _DummyContext:
        def update_current_observation(self, **kwargs):
            pass
    langfuse_context = _DummyContext()
from pydantic import BaseModel, Field
import json
import uuid
import threading
import time
from collections import defaultdict


class TraceMetadata(BaseModel):
    """Metadata for trace tracking"""
    trace_id: str
    session_id: str
    user_id: Optional[str] = None
    task_type: str
    symbol: Optional[str] = None
    company_name: Optional[str] = None
    framework: str  # 'crewai' or 'adk'
    timestamp: datetime = Field(default_factory=datetime.now)


class SpanMetrics(BaseModel):
    """Metrics for individual span"""
    span_id: str
    trace_id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    input_data: Dict = Field(default_factory=dict)
    output_data: Dict = Field(default_factory=dict)
    metadata: Dict = Field(default_factory=dict)
    status: str = "running"  # running, completed, failed
    error: Optional[str] = None
    
    # Cost tracking
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    
    # Performance metrics
    memory_mb: float = 0.0
    cpu_percent: float = 0.0


class ObservabilityCallback:
    """
    Callback system for monitoring agent execution
    Integrates with LangFuse for distributed tracing
    """
    
    def __init__(self, langfuse_client: Optional[Langfuse] = None):
        self.langfuse = langfuse_client
        self.active_traces: Dict[str, TraceMetadata] = {}
        self.active_spans: Dict[str, SpanMetrics] = {}
        self.callback_handlers: List[Callable] = []
        self.lock = threading.Lock()
        
        # Performance tracking
        self.total_traces = 0
        self.total_spans = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        
    def register_handler(self, handler: Callable):
        """Register a callback handler for monitoring events"""
        self.callback_handlers.append(handler)
    
    def start_trace(
        self,
        task_type: str,
        session_id: str,
        framework: str,
        symbol: Optional[str] = None,
        company_name: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Start a new trace for a task
        
        Args:
            task_type: Type of task (e.g., 'stock_analysis', 'ipo_prediction')
            session_id: Session identifier
            framework: 'crewai' or 'adk'
            symbol: Stock symbol
            company_name: Company name
            user_id: User identifier
            metadata: Additional metadata
            
        Returns:
            trace_id
        """
        trace_id = str(uuid.uuid4())
        
        trace_metadata = TraceMetadata(
            trace_id=trace_id,
            session_id=session_id,
            user_id=user_id,
            task_type=task_type,
            symbol=symbol,
            company_name=company_name,
            framework=framework
        )
        
        with self.lock:
            self.active_traces[trace_id] = trace_metadata
            self.total_traces += 1
        
        # Log to LangFuse
        if self.langfuse:
            try:
                self.langfuse.trace(
                    id=trace_id,
                    name=task_type,
                    session_id=session_id,
                    user_id=user_id,
                    metadata={
                        "framework": framework,
                        "symbol": symbol,
                        "company_name": company_name,
                        **(metadata or {})
                    }
                )
            except Exception as e:
                print(f"⚠️ LangFuse trace error: {e}")
        
        # Trigger callbacks
        self._trigger_callbacks('trace_started', {
            'trace_id': trace_id,
            'task_type': task_type,
            'framework': framework
        })
        
        return trace_id
    
    def start_span(
        self,
        trace_id: str,
        name: str,
        input_data: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Start a new span within a trace
        
        Args:
            trace_id: Parent trace ID
            name: Span name (e.g., 'price_agent_execution', 'sentiment_analysis')
            input_data: Input data for the span
            metadata: Additional metadata
            
        Returns:
            span_id
        """
        span_id = str(uuid.uuid4())
        
        span = SpanMetrics(
            span_id=span_id,
            trace_id=trace_id,
            name=name,
            start_time=datetime.now(),
            input_data=input_data or {},
            metadata=metadata or {}
        )
        
        with self.lock:
            self.active_spans[span_id] = span
            self.total_spans += 1
        
        # Log to LangFuse
        if self.langfuse:
            try:
                self.langfuse.span(
                    id=span_id,
                    trace_id=trace_id,
                    name=name,
                    input=input_data,
                    metadata=metadata
                )
            except Exception as e:
                print(f"⚠️ LangFuse span error: {e}")
        
        # Trigger callbacks
        self._trigger_callbacks('span_started', {
            'span_id': span_id,
            'trace_id': trace_id,
            'name': name
        })
        
        return span_id
    
    def end_span(
        self,
        span_id: str,
        output_data: Optional[Dict] = None,
        status: str = "completed",
        error: Optional[str] = None,
        tokens_input: int = 0,
        tokens_output: int = 0,
        cost_usd: float = 0.0,
        memory_mb: float = 0.0,
        cpu_percent: float = 0.0
    ):
        """
        End a span with results
        
        Args:
            span_id: Span identifier
            output_data: Output data from the span
            status: 'completed' or 'failed'
            error: Error message if failed
            tokens_input: Input tokens consumed
            tokens_output: Output tokens generated
            cost_usd: Cost in USD
            memory_mb: Memory usage in MB
            cpu_percent: CPU usage percentage
        """
        if span_id not in self.active_spans:
            print(f"⚠️ Span {span_id} not found")
            return
        
        span = self.active_spans[span_id]
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.output_data = output_data or {}
        span.status = status
        span.error = error
        span.tokens_input = tokens_input
        span.tokens_output = tokens_output
        span.cost_usd = cost_usd
        span.memory_mb = memory_mb
        span.cpu_percent = cpu_percent
        
        # Update global metrics
        with self.lock:
            self.total_cost += cost_usd
            self.total_tokens += tokens_input + tokens_output
        
        # Log to LangFuse
        if self.langfuse:
            try:
                self.langfuse.span(
                    id=span_id,
                    trace_id=span.trace_id,
                    name=span.name,
                    input=span.input_data,
                    output=output_data,
                    metadata={
                        **span.metadata,
                        "duration_ms": span.duration_ms,
                        "tokens_input": tokens_input,
                        "tokens_output": tokens_output,
                        "cost_usd": cost_usd,
                        "memory_mb": memory_mb,
                        "cpu_percent": cpu_percent
                    },
                    level="ERROR" if status == "failed" else "DEFAULT",
                    status_message=error if error else None
                )
                self.langfuse.flush()
            except Exception as e:
                print(f"⚠️ LangFuse span end error: {e}")
        
        # Trigger callbacks
        self._trigger_callbacks('span_ended', {
            'span_id': span_id,
            'trace_id': span.trace_id,
            'name': span.name,
            'duration_ms': span.duration_ms,
            'status': status,
            'cost_usd': cost_usd
        })
    
    def end_trace(
        self,
        trace_id: str,
        output_data: Optional[Dict] = None,
        status: str = "completed",
        metadata: Optional[Dict] = None
    ):
        """
        End a trace
        
        Args:
            trace_id: Trace identifier
            output_data: Final output from the trace
            status: 'completed' or 'failed'
            metadata: Additional metadata
        """
        if trace_id not in self.active_traces:
            print(f"⚠️ Trace {trace_id} not found")
            return
        
        trace = self.active_traces[trace_id]
        
        # Calculate total metrics for this trace
        trace_spans = [s for s in self.active_spans.values() if s.trace_id == trace_id]
        total_duration = sum(s.duration_ms or 0 for s in trace_spans)
        total_cost = sum(s.cost_usd for s in trace_spans)
        total_tokens = sum(s.tokens_input + s.tokens_output for s in trace_spans)
        
        # Log to LangFuse
        if self.langfuse:
            try:
                self.langfuse.trace(
                    id=trace_id,
                    name=trace.task_type,
                    session_id=trace.session_id,
                    user_id=trace.user_id,
                    output=output_data,
                    metadata={
                        **(metadata or {}),
                        "total_duration_ms": total_duration,
                        "total_cost_usd": total_cost,
                        "total_tokens": total_tokens,
                        "status": status
                    }
                )
                self.langfuse.flush()
            except Exception as e:
                print(f"⚠️ LangFuse trace end error: {e}")
        
        # Trigger callbacks
        self._trigger_callbacks('trace_ended', {
            'trace_id': trace_id,
            'task_type': trace.task_type,
            'total_duration_ms': total_duration,
            'total_cost_usd': total_cost,
            'status': status
        })
        
        # Clean up
        with self.lock:
            if trace_id in self.active_traces:
                del self.active_traces[trace_id]
    
    def log_event(
        self,
        trace_id: str,
        name: str,
        metadata: Optional[Dict] = None,
        level: str = "DEFAULT"
    ):
        """
        Log an event within a trace
        
        Args:
            trace_id: Trace identifier
            name: Event name
            metadata: Event metadata
            level: Log level (DEFAULT, DEBUG, WARNING, ERROR)
        """
        if self.langfuse:
            try:
                self.langfuse.event(
                    trace_id=trace_id,
                    name=name,
                    metadata=metadata,
                    level=level
                )
            except Exception as e:
                print(f"⚠️ LangFuse event error: {e}")
        
        # Trigger callbacks
        self._trigger_callbacks('event_logged', {
            'trace_id': trace_id,
            'name': name,
            'level': level
        })
    
    def _trigger_callbacks(self, event_type: str, data: Dict):
        """Trigger all registered callback handlers"""
        for handler in self.callback_handlers:
            try:
                handler(event_type, data)
            except Exception as e:
                print(f"⚠️ Callback error: {e}")
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of all metrics"""
        with self.lock:
            active_traces_count = len(self.active_traces)
            active_spans_count = len(self.active_spans)
            
            return {
                "total_traces": self.total_traces,
                "total_spans": self.total_spans,
                "active_traces": active_traces_count,
                "active_spans": active_spans_count,
                "total_cost_usd": round(self.total_cost, 4),
                "total_tokens": self.total_tokens,
                "avg_cost_per_trace": round(self.total_cost / max(self.total_traces, 1), 4)
            }
    
    def get_trace_details(self, trace_id: str) -> Optional[Dict]:
        """Get detailed information about a trace"""
        if trace_id not in self.active_traces:
            return None
        
        trace = self.active_traces[trace_id]
        spans = [s for s in self.active_spans.values() if s.trace_id == trace_id]
        
        return {
            "trace_metadata": trace.model_dump(),
            "spans": [
                {
                    "span_id": s.span_id,
                    "name": s.name,
                    "duration_ms": s.duration_ms,
                    "status": s.status,
                    "tokens": s.tokens_input + s.tokens_output,
                    "cost_usd": s.cost_usd
                }
                for s in spans
            ],
            "total_duration_ms": sum(s.duration_ms or 0 for s in spans),
            "total_cost_usd": sum(s.cost_usd for s in spans)
        }


class ObservabilitySystem:
    """
    Complete observability system with LangFuse integration
    Provides tracing, monitoring, and auditability for all operations
    """
    
    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None
    ):
        # Initialize LangFuse client
        if public_key and secret_key:
            try:
                self.langfuse = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=host or "https://cloud.langfuse.com"
                )
                print("✅ LangFuse client initialized")
            except Exception as e:
                print(f"⚠️ LangFuse initialization failed: {e}")
                print("📊 Operating in local-only mode")
                self.langfuse = None
        else:
            print("📊 LangFuse credentials not provided - operating in local-only mode")
            self.langfuse = None
        
        # Initialize callback system
        self.callback_system = ObservabilityCallback(self.langfuse)
        
        # Session management
        self.current_session_id = str(uuid.uuid4())
        
        print("✅ Observability System initialized")
    
    def start_task_trace(
        self,
        task_type: str,
        framework: str,
        **kwargs
    ) -> str:
        """Start tracing a new task"""
        return self.callback_system.start_trace(
            task_type=task_type,
            session_id=self.current_session_id,
            framework=framework,
            **kwargs
        )
    
    def start_agent_span(
        self,
        trace_id: str,
        agent_name: str,
        input_data: Optional[Dict] = None,
        **kwargs
    ) -> str:
        """Start tracing an agent execution"""
        return self.callback_system.start_span(
            trace_id=trace_id,
            name=f"agent_{agent_name}",
            input_data=input_data,
            **kwargs
        )
    
    def end_agent_span(
        self,
        span_id: str,
        output_data: Optional[Dict] = None,
        **kwargs
    ):
        """End agent execution span"""
        self.callback_system.end_span(
            span_id=span_id,
            output_data=output_data,
            **kwargs
        )
    
    def end_task_trace(
        self,
        trace_id: str,
        output_data: Optional[Dict] = None,
        **kwargs
    ):
        """End task trace"""
        self.callback_system.end_trace(
            trace_id=trace_id,
            output_data=output_data,
            **kwargs
        )
    
    def log_agent_decision(
        self,
        trace_id: str,
        agent_name: str,
        decision: str,
        reasoning: str,
        confidence: float
    ):
        """Log an agent decision for auditability"""
        self.callback_system.log_event(
            trace_id=trace_id,
            name=f"{agent_name}_decision",
            metadata={
                "agent": agent_name,
                "decision": decision,
                "reasoning": reasoning,
                "confidence": confidence
            }
        )
    
    def log_tool_usage(
        self,
        trace_id: str,
        tool_name: str,
        input_params: Dict,
        output_result: Dict,
        duration_ms: float
    ):
        """Log tool usage for transparency"""
        self.callback_system.log_event(
            trace_id=trace_id,
            name=f"tool_{tool_name}",
            metadata={
                "tool": tool_name,
                "input": input_params,
                "output": output_result,
                "duration_ms": duration_ms
            }
        )
    
    def log_error(
        self,
        trace_id: str,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None
    ):
        """Log error for debugging"""
        self.callback_system.log_event(
            trace_id=trace_id,
            name=f"error_{error_type}",
            metadata={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace
            },
            level="ERROR"
        )
    
    def get_performance_metrics(self) -> Dict:
        """Get overall performance metrics"""
        return self.callback_system.get_metrics_summary()
    
    def get_trace_audit_log(self, trace_id: str) -> Optional[Dict]:
        """Get complete audit log for a trace"""
        return self.callback_system.get_trace_details(trace_id)
    
    def register_monitoring_callback(self, callback: Callable):
        """Register custom monitoring callback"""
        self.callback_system.register_handler(callback)
    
    def flush(self):
        """Flush all pending traces to LangFuse"""
        if self.langfuse:
            try:
                self.langfuse.flush()
            except Exception as e:
                print(f"⚠️ LangFuse flush error: {e}")


# Singleton instance
_observability_system = None

def get_observability_system(
    public_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    host: Optional[str] = None
) -> ObservabilitySystem:
    """Get or create global observability system instance"""
    global _observability_system
    if _observability_system is None:
        _observability_system = ObservabilitySystem(public_key, secret_key, host)
    return _observability_system


# Decorator for automatic tracing
def trace_agent_execution(agent_name: str, framework: str):
    """
    Decorator to automatically trace agent execution
    
    Usage:
        @trace_agent_execution(agent_name="price_agent", framework="crewai")
        def execute_price_agent(symbol: str) -> Dict:
            # Agent logic here
            return result
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            obs_system = get_observability_system()
            
            # Start trace
            trace_id = obs_system.start_task_trace(
                task_type=f"{agent_name}_execution",
                framework=framework
            )
            
            # Start span
            span_id = obs_system.start_agent_span(
                trace_id=trace_id,
                agent_name=agent_name,
                input_data={"args": str(args), "kwargs": str(kwargs)}
            )
            
            try:
                # Execute function
                start_time = time.time()
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # End span successfully
                obs_system.end_agent_span(
                    span_id=span_id,
                    output_data={"result": str(result)[:500]},  # Truncate large outputs
                    status="completed"
                )
                
                # End trace
                obs_system.end_task_trace(
                    trace_id=trace_id,
                    output_data={"success": True},
                    status="completed"
                )
                
                return result
                
            except Exception as e:
                # Log error
                obs_system.log_error(
                    trace_id=trace_id,
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                
                # End span with failure
                obs_system.end_agent_span(
                    span_id=span_id,
                    status="failed",
                    error=str(e)
                )
                
                # End trace with failure
                obs_system.end_task_trace(
                    trace_id=trace_id,
                    status="failed"
                )
                
                raise
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Test observability system
    obs = get_observability_system()
    
    # Test trace
    trace_id = obs.start_task_trace(
        task_type="test_analysis",
        framework="crewai",
        symbol="RELIANCE.NS"
    )
    
    # Test span
    span_id = obs.start_agent_span(
        trace_id=trace_id,
        agent_name="test_agent",
        input_data={"symbol": "RELIANCE.NS"}
    )
    
    # Simulate work
    import time
    time.sleep(0.1)
    
    # End span
    obs.end_agent_span(
        span_id=span_id,
        output_data={"score": 75.5},
        status="completed",
        tokens_input=100,
        tokens_output=50,
        cost_usd=0.001
    )
    
    # End trace
    obs.end_task_trace(
        trace_id=trace_id,
        output_data={"recommendation": "BUY"},
        status="completed"
    )
    
    # Get metrics
    metrics = obs.get_performance_metrics()
    print("\n📊 Performance Metrics:")
    print(json.dumps(metrics, indent=2))
    
    print("\n✅ Observability system test complete")
