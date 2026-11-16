"""
Agent Control Tower — Multi-Agent Orchestration Dashboard
=========================================================
Real-time monitoring, governance, and observability for the 6-agent framework.

Features:
- Live agent health monitoring
- Task progress tracking
- Cost attribution per agent
- Human-in-the-loop escalation
- Anomaly detection
- Audit trail & replay
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import time
import threading
from collections import defaultdict


class AgentStatus(Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"
    THROTTLED = "throttled"


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentMetrics:
    """Real-time metrics for an individual agent."""
    agent_name: str
    status: AgentStatus
    current_task: Optional[str] = None
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_runtime_sec: float = 0.0
    avg_runtime_sec: float = 0.0
    api_calls_made: int = 0
    tokens_consumed: int = 0
    estimated_cost_usd: float = 0.0
    last_execution: Optional[str] = None
    error_count: int = 0
    last_error: Optional[str] = None
    health_score: float = 100.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'agent_name': self.agent_name,
            'status': self.status.value,
            'current_task': self.current_task,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_runtime_sec': round(self.total_runtime_sec, 2),
            'avg_runtime_sec': round(self.avg_runtime_sec, 2),
            'api_calls_made': self.api_calls_made,
            'tokens_consumed': self.tokens_consumed,
            'estimated_cost_usd': round(self.estimated_cost_usd, 4),
            'last_execution': self.last_execution,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'health_score': round(self.health_score, 1)
        }


@dataclass
class TaskExecution:
    """Individual task execution record."""
    task_id: str
    ipo_name: str
    symbol: str
    status: TaskStatus
    started_at: str
    completed_at: Optional[str] = None
    duration_sec: float = 0.0
    agent_calls: List[str] = field(default_factory=list)
    result: Optional[Dict] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'ipo_name': self.ipo_name,
            'symbol': self.symbol,
            'status': self.status.value,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'duration_sec': round(self.duration_sec, 2),
            'agent_calls': self.agent_calls,
            'result': self.result,
            'error': self.error
        }


@dataclass
class AgentCall:
    """Individual agent invocation with lineage."""
    call_id: str
    task_id: str
    agent_name: str
    parent_call_id: Optional[str] = None  # For agent-to-agent calls
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    duration_sec: float = 0.0
    input_data: Dict = field(default_factory=dict)
    output_data: Dict = field(default_factory=dict)
    tools_used: List[str] = field(default_factory=list)
    api_calls: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0
    status: str = "running"
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'call_id': self.call_id,
            'task_id': self.task_id,
            'agent_name': self.agent_name,
            'parent_call_id': self.parent_call_id,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'duration_sec': round(self.duration_sec, 2),
            'tools_used': self.tools_used,
            'api_calls': self.api_calls,
            'tokens_used': self.tokens_used,
            'cost_usd': round(self.cost_usd, 4),
            'status': self.status,
            'error': self.error
        }


@dataclass
class AnomalyAlert:
    """Anomaly detection alert."""
    alert_id: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    agent_name: str
    anomaly_type: str  # 'excessive_calls', 'high_cost', 'looping', 'timeout', 'high_error_rate'
    description: str
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved: bool = False
    resolution: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'alert_id': self.alert_id,
            'severity': self.severity,
            'agent_name': self.agent_name,
            'anomaly_type': self.anomaly_type,
            'description': self.description,
            'detected_at': self.detected_at,
            'resolved': self.resolved,
            'resolution': self.resolution
        }


class AgentControlTower:
    """
    Central monitoring and governance system for multi-agent framework.
    """
    
    def __init__(self):
        # Agent metrics
        self.agent_metrics: Dict[str, AgentMetrics] = {
            'Price Movement Agent': AgentMetrics('Price Movement Agent', AgentStatus.IDLE),
            'Macroeconomic Agent': AgentMetrics('Macroeconomic Agent', AgentStatus.IDLE),
            'Sentiment Agent': AgentMetrics('Sentiment Agent', AgentStatus.IDLE),
            'Risk Agent': AgentMetrics('Risk Agent', AgentStatus.IDLE),
            'IPO Intelligence Agent': AgentMetrics('IPO Intelligence Agent', AgentStatus.IDLE),
            'Orchestrator': AgentMetrics('Orchestrator', AgentStatus.IDLE),
        }
        
        # Task tracking
        self.tasks: Dict[str, TaskExecution] = {}
        self.agent_calls: Dict[str, AgentCall] = {}
        
        # Anomaly detection
        self.anomaly_alerts: List[AnomalyAlert] = []
        self.alert_counter = 0
        
        # Cost tracking
        self.total_cost_usd = 0.0
        self.cost_by_agent: Dict[str, float] = defaultdict(float)
        self.cost_by_task: Dict[str, float] = defaultdict(float)
        
        # Human approval queue
        self.approval_queue: List[Dict] = []
        
        # Audit trail
        self.audit_log: List[Dict] = []
        
        # Real-time subscribers (WebSocket connections)
        self.subscribers: List[Callable] = []
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
    
    # ── Task Management ───────────────────────────────────────────────────────
    
    def start_task(self, task_id: str, ipo_name: str, symbol: str) -> TaskExecution:
        """Start tracking a new IPO analysis task."""
        with self.lock:
            task = TaskExecution(
                task_id=task_id,
                ipo_name=ipo_name,
                symbol=symbol,
                status=TaskStatus.IN_PROGRESS,
                started_at=datetime.now().isoformat()
            )
            self.tasks[task_id] = task
            
            self._log_audit('task_started', {
                'task_id': task_id,
                'ipo_name': ipo_name,
                'symbol': symbol
            })
            
            self._notify_subscribers('task_started', task.to_dict())
            
            return task
    
    def complete_task(self, task_id: str, result: Dict):
        """Mark task as completed with result."""
        with self.lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            task.duration_sec = (
                datetime.fromisoformat(task.completed_at) - 
                datetime.fromisoformat(task.started_at)
            ).total_seconds()
            task.result = result
            
            self._log_audit('task_completed', {
                'task_id': task_id,
                'duration_sec': task.duration_sec
            })
            
            self._notify_subscribers('task_completed', task.to_dict())
    
    def fail_task(self, task_id: str, error: str):
        """Mark task as failed with error."""
        with self.lock:
            if task_id not in self.tasks:
                return
            
            task = self.tasks[task_id]
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now().isoformat()
            task.error = error
            
            self._log_audit('task_failed', {
                'task_id': task_id,
                'error': error
            })
            
            self._notify_subscribers('task_failed', task.to_dict())
    
    # ── Agent Call Tracking ───────────────────────────────────────────────────
    
    def start_agent_call(
        self,
        call_id: str,
        task_id: str,
        agent_name: str,
        input_data: Dict,
        parent_call_id: Optional[str] = None
    ) -> AgentCall:
        """Track start of an agent invocation."""
        with self.lock:
            # Update agent status
            if agent_name in self.agent_metrics:
                metrics = self.agent_metrics[agent_name]
                metrics.status = AgentStatus.RUNNING
                metrics.current_task = task_id
            
            # Create call record
            call = AgentCall(
                call_id=call_id,
                task_id=task_id,
                agent_name=agent_name,
                parent_call_id=parent_call_id,
                input_data=input_data
            )
            self.agent_calls[call_id] = call
            
            # Update task's agent calls
            if task_id in self.tasks:
                self.tasks[task_id].agent_calls.append(agent_name)
            
            self._log_audit('agent_call_started', {
                'call_id': call_id,
                'agent_name': agent_name,
                'task_id': task_id
            })
            
            self._notify_subscribers('agent_call_started', call.to_dict())
            
            return call
    
    def complete_agent_call(
        self,
        call_id: str,
        output_data: Dict,
        tools_used: List[str],
        api_calls: int,
        tokens_used: int,
        cost_usd: float
    ):
        """Track completion of an agent call."""
        with self.lock:
            if call_id not in self.agent_calls:
                return
            
            call = self.agent_calls[call_id]
            call.completed_at = datetime.now().isoformat()
            call.duration_sec = (
                datetime.fromisoformat(call.completed_at) - 
                datetime.fromisoformat(call.started_at)
            ).total_seconds()
            call.output_data = output_data
            call.tools_used = tools_used
            call.api_calls = api_calls
            call.tokens_used = tokens_used
            call.cost_usd = cost_usd
            call.status = "completed"
            
            # Update agent metrics
            agent_name = call.agent_name
            metrics = None
            if agent_name in self.agent_metrics:
                metrics = self.agent_metrics[agent_name]
                metrics.status = AgentStatus.COMPLETED
                metrics.tasks_completed += 1
                metrics.total_runtime_sec += call.duration_sec
                metrics.avg_runtime_sec = metrics.total_runtime_sec / metrics.tasks_completed
                metrics.api_calls_made += api_calls
                metrics.tokens_consumed += tokens_used
                metrics.estimated_cost_usd += cost_usd
                metrics.last_execution = call.completed_at
                
                # Update health score based on performance
                if call.duration_sec > 60:  # Slow execution
                    metrics.health_score = max(0, metrics.health_score - 5)
            
            # Update cost tracking
            self.total_cost_usd += cost_usd
            self.cost_by_agent[agent_name] += cost_usd
            self.cost_by_task[call.task_id] += cost_usd
            
            # Anomaly detection
            if metrics:
                self._detect_anomalies(call, metrics)
            
            self._log_audit('agent_call_completed', {
                'call_id': call_id,
                'agent_name': agent_name,
                'duration_sec': call.duration_sec,
                'cost_usd': cost_usd
            })
            
            self._notify_subscribers('agent_call_completed', call.to_dict())
    
    def fail_agent_call(self, call_id: str, error: str):
        """Track failed agent call."""
        with self.lock:
            if call_id not in self.agent_calls:
                return
            
            call = self.agent_calls[call_id]
            call.status = "failed"
            call.error = error
            call.completed_at = datetime.now().isoformat()
            
            # Update agent metrics
            agent_name = call.agent_name
            if agent_name in self.agent_metrics:
                metrics = self.agent_metrics[agent_name]
                metrics.status = AgentStatus.FAILED
                metrics.tasks_failed += 1
                metrics.error_count += 1
                metrics.last_error = error
                metrics.health_score = max(0, metrics.health_score - 10)
            
            self._log_audit('agent_call_failed', {
                'call_id': call_id,
                'agent_name': agent_name,
                'error': error
            })
            
            self._notify_subscribers('agent_call_failed', call.to_dict())
    
    # ── Anomaly Detection ─────────────────────────────────────────────────────
    
    def _detect_anomalies(self, call: AgentCall, metrics: AgentMetrics):
        """Detect anomalous behavior in agent execution."""
        
        # 1. Excessive API calls
        if call.api_calls > 50:
            self._create_alert(
                severity='high',
                agent_name=call.agent_name,
                anomaly_type='excessive_calls',
                description=f"Agent made {call.api_calls} API calls in single execution (threshold: 50)"
            )
        
        # 2. High cost
        if call.cost_usd > 0.50:
            self._create_alert(
                severity='high',
                agent_name=call.agent_name,
                anomaly_type='high_cost',
                description=f"Single call cost ${call.cost_usd:.4f} (threshold: $0.50)"
            )
        
        # 3. Timeout/slow execution
        if call.duration_sec > 120:
            self._create_alert(
                severity='medium',
                agent_name=call.agent_name,
                anomaly_type='timeout',
                description=f"Agent execution took {call.duration_sec:.1f}s (threshold: 120s)"
            )
        
        # 4. High error rate
        if metrics.tasks_completed > 0:
            error_rate = metrics.tasks_failed / (metrics.tasks_completed + metrics.tasks_failed)
            if error_rate > 0.20:  # 20% error rate
                self._create_alert(
                    severity='critical',
                    agent_name=call.agent_name,
                    anomaly_type='high_error_rate',
                    description=f"Agent error rate: {error_rate:.1%} (threshold: 20%)"
                )
        
        # 5. Looping detection (same agent called multiple times in short period)
        recent_calls = [
            c for c in self.agent_calls.values()
            if c.agent_name == call.agent_name and c.task_id == call.task_id
        ]
        if len(recent_calls) > 5:
            self._create_alert(
                severity='high',
                agent_name=call.agent_name,
                anomaly_type='looping',
                description=f"Agent called {len(recent_calls)} times for same task (potential loop)"
            )
    
    def _create_alert(self, severity: str, agent_name: str, anomaly_type: str, description: str):
        """Create anomaly alert."""
        alert = AnomalyAlert(
            alert_id=f"ALERT-{self.alert_counter:04d}",
            severity=severity,
            agent_name=agent_name,
            anomaly_type=anomaly_type,
            description=description
        )
        self.alert_counter += 1
        self.anomaly_alerts.append(alert)
        
        self._log_audit('anomaly_detected', alert.to_dict())
        self._notify_subscribers('anomaly_alert', alert.to_dict())
    
    # ── Human Approval Interface ──────────────────────────────────────────────
    
    def request_approval(
        self,
        task_id: str,
        agent_name: str,
        decision: str,
        reasoning: str,
        timeout_sec: int = 300
    ) -> Dict:
        """Request human approval for critical decision."""
        approval_request = {
            'request_id': f"APPROVAL-{len(self.approval_queue):04d}",
            'task_id': task_id,
            'agent_name': agent_name,
            'decision': decision,
            'reasoning': reasoning,
            'requested_at': datetime.now().isoformat(),
            'timeout_sec': timeout_sec,
            'status': 'pending',
            'response': None
        }
        
        self.approval_queue.append(approval_request)
        
        # Update agent status
        if agent_name in self.agent_metrics:
            self.agent_metrics[agent_name].status = AgentStatus.WAITING_APPROVAL
        
        self._log_audit('approval_requested', approval_request)
        self._notify_subscribers('approval_requested', approval_request)
        
        return approval_request
    
    def respond_approval(self, request_id: str, approved: bool, comment: str = ""):
        """User responds to approval request."""
        for request in self.approval_queue:
            if request['request_id'] == request_id:
                request['status'] = 'approved' if approved else 'rejected'
                request['response'] = {
                    'approved': approved,
                    'comment': comment,
                    'responded_at': datetime.now().isoformat()
                }
                
                self._log_audit('approval_responded', request)
                self._notify_subscribers('approval_responded', request)
                break
    
    # ── Query & Reporting ─────────────────────────────────────────────────────
    
    def get_dashboard_summary(self) -> Dict:
        """Get real-time dashboard summary."""
        with self.lock:
            active_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS]
            completed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
            failed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.FAILED]
            
            return {
                'timestamp': datetime.now().isoformat(),
                'tasks': {
                    'total': len(self.tasks),
                    'active': len(active_tasks),
                    'completed': len(completed_tasks),
                    'failed': len(failed_tasks)
                },
                'agents': {
                    name: metrics.to_dict()
                    for name, metrics in self.agent_metrics.items()
                },
                'cost': {
                    'total_usd': round(self.total_cost_usd, 4),
                    'by_agent': {k: round(v, 4) for k, v in self.cost_by_agent.items()}
                },
                'anomalies': {
                    'total': len(self.anomaly_alerts),
                    'unresolved': len([a for a in self.anomaly_alerts if not a.resolved]),
                    'recent': [a.to_dict() for a in self.anomaly_alerts[-5:]]
                },
                'approvals': {
                    'pending': len([a for a in self.approval_queue if a['status'] == 'pending'])
                }
            }
    
    def get_agent_lineage(self, task_id: str) -> Dict:
        """Get agent call lineage (DAG) for a task."""
        calls = [c for c in self.agent_calls.values() if c.task_id == task_id]
        
        # Build DAG structure
        nodes = []
        edges = []
        
        for call in calls:
            nodes.append({
                'id': call.call_id,
                'agent': call.agent_name,
                'duration_sec': call.duration_sec,
                'cost_usd': call.cost_usd,
                'status': call.status
            })
            
            if call.parent_call_id:
                edges.append({
                    'source': call.parent_call_id,
                    'target': call.call_id
                })
        
        return {
            'task_id': task_id,
            'nodes': nodes,
            'edges': edges
        }
    
    def get_audit_trail(self, task_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get audit trail with optional task filter."""
        if task_id:
            filtered = [log for log in self.audit_log if log.get('data', {}).get('task_id') == task_id]
            return filtered[-limit:]
        return self.audit_log[-limit:]
    
    def replay_task(self, task_id: str) -> Dict:
        """Replay complete execution trace for a task."""
        if task_id not in self.tasks:
            return {'error': 'Task not found'}
        
        task = self.tasks[task_id]
        calls = [c.to_dict() for c in self.agent_calls.values() if c.task_id == task_id]
        audit = self.get_audit_trail(task_id)
        
        return {
            'task': task.to_dict(),
            'agent_calls': calls,
            'audit_trail': audit,
            'lineage': self.get_agent_lineage(task_id)
        }
    
    # ── Internal Helpers ──────────────────────────────────────────────────────
    
    def _log_audit(self, event_type: str, data: Dict):
        """Log event to audit trail."""
        self.audit_log.append({
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        })
    
    def _notify_subscribers(self, event_type: str, data: Dict):
        """Notify WebSocket subscribers of event."""
        message = {
            'event': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        for subscriber in self.subscribers:
            try:
                subscriber(message)
            except Exception as e:
                print(f"Subscriber notification error: {e}")
    
    def subscribe(self, callback: Callable):
        """Subscribe to real-time events."""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from events."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)


# Singleton instance
_control_tower = None

def get_agent_control_tower() -> AgentControlTower:
    """Get or create singleton instance."""
    global _control_tower
    if _control_tower is None:
        _control_tower = AgentControlTower()
    return _control_tower
