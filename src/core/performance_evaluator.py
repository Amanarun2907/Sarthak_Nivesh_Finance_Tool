"""
Performance Evaluation System
============================
End-to-end performance evaluation, cost estimation, and runtime tracking

Requirements Fulfilled:
- End-to-end performance evaluation (Requirement #10)
- Cost and running time estimates (Requirement #10)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pydantic import BaseModel
import psutil
import time
import threading
from collections import defaultdict
import json


class ModelPricing(BaseModel):
    """Pricing information for different AI models"""
    model_name: str
    input_cost_per_1k_tokens: float
    output_cost_per_1k_tokens: float
    context_window: int


# Standard pricing (as of 2024)
MODEL_PRICING = {
    "gpt-4": ModelPricing(
        model_name="gpt-4",
        input_cost_per_1k_tokens=0.03,
        output_cost_per_1k_tokens=0.06,
        context_window=8192
    ),
    "gpt-3.5-turbo": ModelPricing(
        model_name="gpt-3.5-turbo",
        input_cost_per_1k_tokens=0.0015,
        output_cost_per_1k_tokens=0.002,
        context_window=4096
    ),
    "claude-3-opus": ModelPricing(
        model_name="claude-3-opus",
        input_cost_per_1k_tokens=0.015,
        output_cost_per_1k_tokens=0.075,
        context_window=200000
    ),
    "claude-3-sonnet": ModelPricing(
        model_name="claude-3-sonnet",
        input_cost_per_1k_tokens=0.003,
        output_cost_per_1k_tokens=0.015,
        context_window=200000
    ),
    "claude-3-haiku": ModelPricing(
        model_name="claude-3-haiku",
        input_cost_per_1k_tokens=0.00025,
        output_cost_per_1k_tokens=0.00125,
        context_window=200000
    ),
}


@dataclass
class ExecutionMetrics:
    """Metrics for a single execution"""
    execution_id: str
    component_name: str
    component_type: str  # 'agent', 'tool', 'orchestrator'
    framework: str  # 'crewai', 'adk', 'custom'
    
    # Timing
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    
    # Resource usage
    memory_start_mb: float = 0.0
    memory_end_mb: float = 0.0
    memory_peak_mb: float = 0.0
    cpu_percent_avg: float = 0.0
    
    # AI Model usage
    model_name: Optional[str] = None
    tokens_input: int = 0
    tokens_output: int = 0
    api_calls: int = 0
    
    # Cost
    estimated_cost_usd: float = 0.0
    
    # Status
    status: str = "running"  # running, completed, failed
    error_message: Optional[str] = None
    
    # Additional metadata
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "execution_id": self.execution_id,
            "component_name": self.component_name,
            "component_type": self.component_type,
            "framework": self.framework,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": round(self.duration_seconds, 3),
            "memory_peak_mb": round(self.memory_peak_mb, 2),
            "cpu_percent_avg": round(self.cpu_percent_avg, 2),
            "model_name": self.model_name,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "total_tokens": self.tokens_input + self.tokens_output,
            "api_calls": self.api_calls,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
            "status": self.status,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


@dataclass
class TaskPerformanceReport:
    """Complete performance report for a task"""
    task_id: str
    task_type: str
    symbol: Optional[str] = None
    company_name: Optional[str] = None
    
    # Timing
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    
    # Component executions
    executions: List[ExecutionMetrics] = field(default_factory=list)
    
    # Aggregated metrics
    total_api_calls: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    peak_memory_mb: float = 0.0
    avg_cpu_percent: float = 0.0
    
    # Framework breakdown
    crewai_cost: float = 0.0
    adk_cost: float = 0.0
    tools_cost: float = 0.0
    
    # Success metrics
    successful_components: int = 0
    failed_components: int = 0
    success_rate: float = 0.0
    
    # Recommendations
    performance_grade: str = "A"  # A, B, C, D, F
    optimization_suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "symbol": self.symbol,
            "company_name": self.company_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "total_duration_seconds": round(self.total_duration_seconds, 3),
            "total_api_calls": self.total_api_calls,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "peak_memory_mb": round(self.peak_memory_mb, 2),
            "avg_cpu_percent": round(self.avg_cpu_percent, 2),
            "framework_costs": {
                "crewai": round(self.crewai_cost, 6),
                "adk": round(self.adk_cost, 6),
                "tools": round(self.tools_cost, 6)
            },
            "successful_components": self.successful_components,
            "failed_components": self.failed_components,
            "success_rate": round(self.success_rate, 2),
            "performance_grade": self.performance_grade,
            "optimization_suggestions": self.optimization_suggestions,
            "component_executions": [e.to_dict() for e in self.executions]
        }


class PerformanceEvaluator:
    """
    Comprehensive performance evaluation system
    Tracks cost, time, memory, and provides optimization recommendations
    """
    
    def __init__(self):
        self.active_tasks: Dict[str, TaskPerformanceReport] = {}
        self.active_executions: Dict[str, ExecutionMetrics] = {}
        self.completed_reports: List[TaskPerformanceReport] = []
        
        # Monitoring threads
        self.monitoring_active = False
        self.monitor_threads: Dict[str, threading.Thread] = {}
        
        # System baseline
        self.baseline_memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        self.baseline_cpu_percent = psutil.cpu_percent(interval=1)
        
        print("✅ Performance Evaluator initialized")
    
    def start_task(
        self,
        task_id: str,
        task_type: str,
        symbol: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> TaskPerformanceReport:
        """Start tracking a new task"""
        report = TaskPerformanceReport(
            task_id=task_id,
            task_type=task_type,
            symbol=symbol,
            company_name=company_name
        )
        
        self.active_tasks[task_id] = report
        
        return report
    
    def start_execution(
        self,
        task_id: str,
        execution_id: str,
        component_name: str,
        component_type: str,
        framework: str,
        model_name: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> ExecutionMetrics:
        """Start tracking a component execution"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        # Capture initial resource usage
        process = psutil.Process()
        memory_start_mb = process.memory_info().rss / 1024 / 1024
        
        execution = ExecutionMetrics(
            execution_id=execution_id,
            component_name=component_name,
            component_type=component_type,
            framework=framework,
            start_time=datetime.now(),
            memory_start_mb=memory_start_mb,
            memory_peak_mb=memory_start_mb,
            model_name=model_name,
            metadata=metadata or {}
        )
        
        self.active_executions[execution_id] = execution
        
        # Start resource monitoring thread
        self._start_resource_monitoring(execution_id)
        
        return execution
    
    def end_execution(
        self,
        execution_id: str,
        tokens_input: int = 0,
        tokens_output: int = 0,
        api_calls: int = 0,
        status: str = "completed",
        error_message: Optional[str] = None
    ):
        """End tracking for an execution"""
        if execution_id not in self.active_executions:
            print(f"⚠️ Execution {execution_id} not found")
            return
        
        execution = self.active_executions[execution_id]
        
        # Stop monitoring
        self._stop_resource_monitoring(execution_id)
        
        # Update metrics
        execution.end_time = datetime.now()
        execution.duration_seconds = (execution.end_time - execution.start_time).total_seconds()
        execution.tokens_input = tokens_input
        execution.tokens_output = tokens_output
        execution.api_calls = api_calls
        execution.status = status
        execution.error_message = error_message
        
        # Capture final memory
        process = psutil.Process()
        execution.memory_end_mb = process.memory_info().rss / 1024 / 1024
        
        # Calculate cost
        if execution.model_name and execution.model_name in MODEL_PRICING:
            pricing = MODEL_PRICING[execution.model_name]
            input_cost = (tokens_input / 1000) * pricing.input_cost_per_1k_tokens
            output_cost = (tokens_output / 1000) * pricing.output_cost_per_1k_tokens
            execution.estimated_cost_usd = input_cost + output_cost
        
        # Find parent task and add execution
        for task in self.active_tasks.values():
            if any(e.execution_id == execution_id for e in task.executions):
                break
        else:
            # Add to first available task (fallback)
            if self.active_tasks:
                task = list(self.active_tasks.values())[0]
                task.executions.append(execution)
        
        # Remove from active
        del self.active_executions[execution_id]
    
    def _start_resource_monitoring(self, execution_id: str):
        """Start monitoring resources for an execution"""
        if execution_id not in self.active_executions:
            return
        
        def monitor():
            process = psutil.Process()
            execution = self.active_executions.get(execution_id)
            if not execution:
                return
            
            cpu_samples = []
            
            while execution_id in self.active_executions:
                try:
                    # Memory
                    current_memory_mb = process.memory_info().rss / 1024 / 1024
                    if current_memory_mb > execution.memory_peak_mb:
                        execution.memory_peak_mb = current_memory_mb
                    
                    # CPU
                    cpu_percent = process.cpu_percent(interval=0.1)
                    cpu_samples.append(cpu_percent)
                    execution.cpu_percent_avg = sum(cpu_samples) / len(cpu_samples)
                    
                    time.sleep(0.5)
                except:
                    break
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        self.monitor_threads[execution_id] = thread
    
    def _stop_resource_monitoring(self, execution_id: str):
        """Stop monitoring resources"""
        if execution_id in self.monitor_threads:
            # Thread will stop automatically when execution is removed
            pass
    
    def end_task(
        self,
        task_id: str,
        status: str = "completed"
    ) -> TaskPerformanceReport:
        """End tracking for a task and generate report"""
        if task_id not in self.active_tasks:
            raise ValueError(f"Task {task_id} not found")
        
        report = self.active_tasks[task_id]
        report.end_time = datetime.now()
        report.total_duration_seconds = (report.end_time - report.start_time).total_seconds()
        
        # Aggregate metrics
        for execution in report.executions:
            report.total_api_calls += execution.api_calls
            report.total_tokens += execution.tokens_input + execution.tokens_output
            report.total_cost_usd += execution.estimated_cost_usd
            
            if execution.memory_peak_mb > report.peak_memory_mb:
                report.peak_memory_mb = execution.memory_peak_mb
            
            # Framework breakdown
            if execution.framework == "crewai":
                report.crewai_cost += execution.estimated_cost_usd
            elif execution.framework == "adk":
                report.adk_cost += execution.estimated_cost_usd
            elif execution.framework == "custom" and execution.component_type == "tool":
                report.tools_cost += execution.estimated_cost_usd
            
            # Success tracking
            if execution.status == "completed":
                report.successful_components += 1
            else:
                report.failed_components += 1
        
        # Calculate average CPU
        if report.executions:
            report.avg_cpu_percent = sum(e.cpu_percent_avg for e in report.executions) / len(report.executions)
        
        # Success rate
        total_components = report.successful_components + report.failed_components
        if total_components > 0:
            report.success_rate = (report.successful_components / total_components) * 100
        
        # Performance grading
        report.performance_grade = self._calculate_performance_grade(report)
        
        # Optimization suggestions
        report.optimization_suggestions = self._generate_optimization_suggestions(report)
        
        # Move to completed
        self.completed_reports.append(report)
        del self.active_tasks[task_id]
        
        return report
    
    def _calculate_performance_grade(self, report: TaskPerformanceReport) -> str:
        """Calculate performance grade based on multiple factors"""
        score = 100
        
        # Cost efficiency (lower is better)
        if report.total_cost_usd > 0.50:
            score -= 20
        elif report.total_cost_usd > 0.25:
            score -= 10
        elif report.total_cost_usd > 0.10:
            score -= 5
        
        # Speed (faster is better)
        if report.total_duration_seconds > 60:
            score -= 20
        elif report.total_duration_seconds > 30:
            score -= 10
        elif report.total_duration_seconds > 15:
            score -= 5
        
        # Memory efficiency
        if report.peak_memory_mb > 1000:
            score -= 15
        elif report.peak_memory_mb > 500:
            score -= 10
        elif report.peak_memory_mb > 250:
            score -= 5
        
        # Success rate
        if report.success_rate < 100:
            score -= (100 - report.success_rate) * 0.5
        
        # Determine grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_optimization_suggestions(self, report: TaskPerformanceReport) -> List[str]:
        """Generate optimization suggestions based on metrics"""
        suggestions = []
        
        # Cost optimization
        if report.total_cost_usd > 0.25:
            suggestions.append(f"💰 High cost detected (${report.total_cost_usd:.4f}). Consider using cheaper models for non-critical tasks.")
        
        if report.crewai_cost > report.adk_cost * 2:
            suggestions.append("💰 CrewAI costs are high. Consider migrating some agents to ADK.")
        
        # Performance optimization
        if report.total_duration_seconds > 45:
            suggestions.append(f"⚡ Slow execution ({report.total_duration_seconds:.1f}s). Consider parallelizing agent execution.")
        
        # Memory optimization
        if report.peak_memory_mb > 500:
            suggestions.append(f"🧠 High memory usage ({report.peak_memory_mb:.0f}MB). Consider streaming large responses.")
        
        # Token optimization
        if report.total_tokens > 50000:
            suggestions.append(f"📝 High token usage ({report.total_tokens:,}). Optimize prompts and reduce context size.")
        
        # Success rate
        if report.success_rate < 100:
            suggestions.append(f"⚠️ Some components failed ({report.failed_components}). Implement retry logic and error handling.")
        
        # API calls
        if report.total_api_calls > 20:
            suggestions.append(f"🌐 High API call count ({report.total_api_calls}). Implement caching to reduce redundant calls.")
        
        if not suggestions:
            suggestions.append("✅ Performance is optimal. No suggestions at this time.")
        
        return suggestions
    
    def get_summary_statistics(self) -> Dict:
        """Get summary statistics across all completed tasks"""
        if not self.completed_reports:
            return {
                "total_tasks": 0,
                "message": "No completed tasks yet"
            }
        
        total_tasks = len(self.completed_reports)
        total_cost = sum(r.total_cost_usd for r in self.completed_reports)
        total_duration = sum(r.total_duration_seconds for r in self.completed_reports)
        avg_duration = total_duration / total_tasks
        avg_cost = total_cost / total_tasks
        
        # Grade distribution
        grade_counts = defaultdict(int)
        for report in self.completed_reports:
            grade_counts[report.performance_grade] += 1
        
        return {
            "total_tasks": total_tasks,
            "total_cost_usd": round(total_cost, 4),
            "avg_cost_per_task": round(avg_cost, 4),
            "total_duration_seconds": round(total_duration, 2),
            "avg_duration_seconds": round(avg_duration, 2),
            "grade_distribution": dict(grade_counts),
            "success_rate": round(
                sum(r.success_rate for r in self.completed_reports) / total_tasks, 2
            )
        }
    
    def export_report_json(self, task_id: str) -> str:
        """Export task report as JSON"""
        # Find in active or completed
        report = self.active_tasks.get(task_id)
        if not report:
            for r in self.completed_reports:
                if r.task_id == task_id:
                    report = r
                    break
        
        if not report:
            return json.dumps({"error": f"Task {task_id} not found"})
        
        return json.dumps(report.to_dict(), indent=2)


# Singleton instance
_performance_evaluator = None

def get_performance_evaluator() -> PerformanceEvaluator:
    """Get or create global performance evaluator instance"""
    global _performance_evaluator
    if _performance_evaluator is None:
        _performance_evaluator = PerformanceEvaluator()
    return _performance_evaluator


if __name__ == "__main__":
    # Test performance evaluator
    evaluator = get_performance_evaluator()
    
    # Start task
    task_id = "test_task_001"
    evaluator.start_task(
        task_id=task_id,
        task_type="stock_analysis",
        symbol="RELIANCE.NS"
    )
    
    # Start execution
    exec_id = "exec_001"
    evaluator.start_execution(
        task_id=task_id,
        execution_id=exec_id,
        component_name="price_agent",
        component_type="agent",
        framework="crewai",
        model_name="gpt-4"
    )
    
    # Simulate work
    time.sleep(2)
    
    # End execution
    evaluator.end_execution(
        execution_id=exec_id,
        tokens_input=500,
        tokens_output=300,
        api_calls=2,
        status="completed"
    )
    
    # End task
    report = evaluator.end_task(task_id)
    
    # Print report
    print("\n📊 Performance Report:")
    print(json.dumps(report.to_dict(), indent=2))
    
    # Print statistics
    print("\n📈 Summary Statistics:")
    stats = evaluator.get_summary_statistics()
    print(json.dumps(stats, indent=2))
    
    print("\n✅ Performance evaluator test complete")
