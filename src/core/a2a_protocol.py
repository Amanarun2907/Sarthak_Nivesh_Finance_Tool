"""
A2A (Agent-to-Agent) Protocol for Sarthak Nivesh
Enables interoperability between CrewAI and Anthropic ADK agents

Requirements Fulfilled:
- Agent to Agent communication using A2A protocol (Requirement #6)
- Interoperability: CrewAI + ADK agents working together (Requirement #7)
- Context Sharing & State Updates (Requirement #1)
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
import json
import uuid
from collections import defaultdict
import threading


class AgentFramework(str, Enum):
    """Agent framework types"""
    CREWAI = "crewai"
    ADK = "anthropic_adk"
    CUSTOM = "custom"


class MessageType(str, Enum):
    """A2A message types"""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    STATE_UPDATE = "state_update"
    ERROR = "error"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class A2AMessage(BaseModel):
    """
    Standardized message format for agent-to-agent communication
    """
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Routing
    sender_id: str
    sender_framework: AgentFramework
    receiver_id: Optional[str] = None  # None for broadcast
    receiver_framework: Optional[AgentFramework] = None
    
    # Message details
    message_type: MessageType
    priority: MessagePriority = MessagePriority.MEDIUM
    
    # Content
    action: str  # What the sender wants
    payload: Dict[str, Any]  # Data being sent
    context: Dict[str, Any] = Field(default_factory=dict)  # Shared state
    
    # Response tracking
    requires_response: bool = False
    in_response_to: Optional[str] = None  # Reference to original message_id
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender_id": "price_movement_agent",
                "sender_framework": "crewai",
                "receiver_id": "sentiment_agent",
                "receiver_framework": "anthropic_adk",
                "message_type": "request",
                "priority": "high",
                "action": "analyze_sentiment",
                "payload": {"symbol": "RELIANCE.NS"},
                "context": {"task_id": "task_123", "user_query": "Analyze Reliance"}
            }
        }


class AgentState(BaseModel):
    """
    Shared state container that agents can read/write
    Enables context sharing across frameworks
    """
    state_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # State data
    task_id: str
    symbol: Optional[str] = None
    company_name: Optional[str] = None
    
    # Intermediate results from agents
    agent_outputs: Dict[str, Any] = Field(default_factory=dict)
    
    # Shared context
    user_query: Optional[str] = None
    analysis_type: Optional[str] = None  # "stock", "ipo", "portfolio"
    
    # Progress tracking
    completed_agents: List[str] = Field(default_factory=list)
    pending_agents: List[str] = Field(default_factory=list)
    failed_agents: List[str] = Field(default_factory=list)
    
    # Final output
    final_recommendation: Optional[Dict] = None
    confidence_score: Optional[float] = None
    
    def update_agent_output(self, agent_id: str, output: Any):
        """Update output from an agent"""
        # Store raw output directly so downstream agents can read fields without unwrapping
        if isinstance(output, dict):
            self.agent_outputs[agent_id] = output
        else:
            self.agent_outputs[agent_id] = output
        self.updated_at = datetime.now()
        
        if agent_id in self.pending_agents:
            self.pending_agents.remove(agent_id)
        if agent_id not in self.completed_agents:
            self.completed_agents.append(agent_id)
    
    def mark_agent_failed(self, agent_id: str, error: str):
        """Mark agent as failed"""
        self.failed_agents.append(agent_id)
        self.agent_outputs[agent_id] = {
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.updated_at = datetime.now()
        
        if agent_id in self.pending_agents:
            self.pending_agents.remove(agent_id)
    
    def get_context_for_agent(self, agent_id: str) -> Dict:
        """
        Get relevant context for an agent
        Includes outputs from previously completed agents
        """
        return {
            "task_id": self.task_id,
            "symbol": self.symbol,
            "company_name": self.company_name,
            "user_query": self.user_query,
            "analysis_type": self.analysis_type,
            "previous_outputs": {
                agent: output for agent, output in self.agent_outputs.items()
                if agent in self.completed_agents
            },
            "completed_agents": self.completed_agents,
            "pending_agents": self.pending_agents
        }


class A2AProtocol:
    """
    Agent-to-Agent Protocol Handler
    Manages message routing, state synchronization, and framework interoperability
    """
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}  # agent_id -> agent_info
        self.message_queue: List[A2AMessage] = []
        self.message_history: List[A2AMessage] = []
        self.state_store: Dict[str, AgentState] = {}  # task_id -> state
        
        # Callbacks for message handling
        self.message_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Thread safety
        self.lock = threading.Lock()
        
        print("✅ A2A Protocol initialized")
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        framework: AgentFramework,
        capabilities: List[str],
        metadata: Optional[Dict] = None
    ):
        """
        Register an agent with the A2A protocol
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            framework: Agent framework (CrewAI or ADK)
            capabilities: List of actions the agent can perform
            metadata: Additional agent metadata
        """
        with self.lock:
            self.agents[agent_id] = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "framework": framework,
                "capabilities": capabilities,
                "metadata": metadata or {},
                "registered_at": datetime.now().isoformat(),
                "message_count": 0,
                "status": "active"
            }
            print(f"✅ Registered agent: {agent_name} ({framework.value})")
    
    def send_message(self, message: A2AMessage) -> str:
        """
        Send a message via A2A protocol
        
        Args:
            message: A2AMessage to send
            
        Returns:
            message_id
        """
        with self.lock:
            # Validate sender exists
            if message.sender_id not in self.agents:
                raise ValueError(f"Sender agent '{message.sender_id}' not registered")
            
            # Validate receiver exists (if specified)
            if message.receiver_id and message.receiver_id not in self.agents:
                raise ValueError(f"Receiver agent '{message.receiver_id}' not registered")
            
            # Add to queue
            self.message_queue.append(message)
            self.message_history.append(message)
            
            # Update sender stats
            self.agents[message.sender_id]["message_count"] += 1
            
            # Trigger callbacks
            self._trigger_handlers(message)
            
            return message.message_id
    
    def create_state(self, task_id: str, **kwargs) -> AgentState:
        """
        Create a new shared state for a task
        
        Args:
            task_id: Unique task identifier
            **kwargs: Additional state fields
            
        Returns:
            AgentState
        """
        with self.lock:
            if task_id in self.state_store:
                return self.state_store[task_id]
            
            state = AgentState(task_id=task_id, **kwargs)
            self.state_store[task_id] = state
            return state
    
    def get_state(self, task_id: str) -> Optional[AgentState]:
        """Get state for a task"""
        return self.state_store.get(task_id)
    
    def update_state(self, task_id: str, updates: Dict):
        """
        Update shared state
        
        Args:
            task_id: Task identifier
            updates: Dictionary of updates
        """
        with self.lock:
            state = self.state_store.get(task_id)
            if not state:
                raise ValueError(f"State for task '{task_id}' not found")
            
            for key, value in updates.items():
                if hasattr(state, key):
                    setattr(state, key, value)
            
            state.updated_at = datetime.now()
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        """
        Register a callback handler for specific message types
        
        Args:
            message_type: Type of message to handle
            handler: Callback function(message: A2AMessage) -> None
        """
        self.message_handlers[message_type.value].append(handler)
    
    def _trigger_handlers(self, message: A2AMessage):
        """Trigger registered handlers for a message"""
        handlers = self.message_handlers.get(message.message_type.value, [])
        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                print(f"❌ Handler error for {message.message_type}: {e}")
    
    def get_messages_for_agent(self, agent_id: str, unread_only: bool = True) -> List[A2AMessage]:
        """
        Get messages for a specific agent
        
        Args:
            agent_id: Agent identifier
            unread_only: Only return unread messages
            
        Returns:
            List of messages
        """
        with self.lock:
            messages = [
                msg for msg in self.message_queue
                if msg.receiver_id == agent_id or (msg.receiver_id is None and msg.message_type == MessageType.BROADCAST)
            ]
            
            if unread_only:
                # Remove from queue
                for msg in messages:
                    if msg in self.message_queue:
                        self.message_queue.remove(msg)
            
            return messages
    
    def create_request(
        self,
        sender_id: str,
        receiver_id: str,
        action: str,
        payload: Dict,
        context: Optional[Dict] = None,
        priority: MessagePriority = MessagePriority.MEDIUM
    ) -> A2AMessage:
        """
        Create a request message from one agent to another
        
        Args:
            sender_id: ID of sending agent
            receiver_id: ID of receiving agent
            action: Action to perform
            payload: Data for the action
            context: Shared context
            priority: Message priority
            
        Returns:
            A2AMessage
        """
        sender = self.agents.get(sender_id)
        receiver = self.agents.get(receiver_id)
        
        if not sender or not receiver:
            raise ValueError("Sender or receiver not registered")
        
        return A2AMessage(
            sender_id=sender_id,
            sender_framework=AgentFramework(sender["framework"]),
            receiver_id=receiver_id,
            receiver_framework=AgentFramework(receiver["framework"]),
            message_type=MessageType.REQUEST,
            priority=priority,
            action=action,
            payload=payload,
            context=context or {},
            requires_response=True
        )
    
    def create_response(
        self,
        sender_id: str,
        original_message: A2AMessage,
        payload: Dict,
        success: bool = True
    ) -> A2AMessage:
        """
        Create a response to a previous message
        
        Args:
            sender_id: ID of agent sending response
            original_message: Original request message
            payload: Response data
            success: Whether the request succeeded
            
        Returns:
            A2AMessage
        """
        sender = self.agents.get(sender_id)
        
        return A2AMessage(
            sender_id=sender_id,
            sender_framework=AgentFramework(sender["framework"]),
            receiver_id=original_message.sender_id,
            receiver_framework=original_message.sender_framework,
            message_type=MessageType.RESPONSE if success else MessageType.ERROR,
            priority=original_message.priority,
            action=f"response_to_{original_message.action}",
            payload=payload,
            context=original_message.context,
            in_response_to=original_message.message_id
        )
    
    def broadcast_state_update(
        self,
        sender_id: str,
        task_id: str,
        updates: Dict
    ) -> str:
        """
        Broadcast a state update to all agents working on a task
        
        Args:
            sender_id: ID of agent broadcasting
            task_id: Task identifier
            updates: State updates
            
        Returns:
            message_id
        """
        sender = self.agents.get(sender_id)
        
        message = A2AMessage(
            sender_id=sender_id,
            sender_framework=AgentFramework(sender["framework"]),
            receiver_id=None,  # Broadcast
            message_type=MessageType.STATE_UPDATE,
            priority=MessagePriority.MEDIUM,
            action="state_update",
            payload=updates,
            context={"task_id": task_id}
        )
        
        return self.send_message(message)
    
    def get_protocol_stats(self) -> Dict:
        """Get A2A protocol statistics"""
        with self.lock:
            return {
                "total_agents": len(self.agents),
                "crewai_agents": sum(1 for a in self.agents.values() if a["framework"] == AgentFramework.CREWAI),
                "adk_agents": sum(1 for a in self.agents.values() if a["framework"] == AgentFramework.ADK),
                "total_messages": len(self.message_history),
                "queued_messages": len(self.message_queue),
                "active_tasks": len(self.state_store),
                "framework_interop_messages": sum(
                    1 for msg in self.message_history
                    if msg.sender_framework != msg.receiver_framework
                )
            }
    
    def get_agent_communication_matrix(self) -> Dict:
        """Get agent communication patterns"""
        matrix = defaultdict(lambda: defaultdict(int))
        
        for msg in self.message_history:
            if msg.receiver_id:
                matrix[msg.sender_id][msg.receiver_id] += 1
        
        return dict(matrix)


# Singleton instance
_a2a_protocol = None

def get_a2a_protocol() -> A2AProtocol:
    """Get global A2A protocol instance"""
    global _a2a_protocol
    if _a2a_protocol is None:
        _a2a_protocol = A2AProtocol()
    return _a2a_protocol


if __name__ == "__main__":
    # Test A2A Protocol
    protocol = get_a2a_protocol()
    
    # Register agents
    protocol.register_agent(
        agent_id="price_agent",
        agent_name="Price Movement Agent",
        framework=AgentFramework.CREWAI,
        capabilities=["analyze_price", "calculate_indicators"]
    )
    
    protocol.register_agent(
        agent_id="sentiment_agent",
        agent_name="Sentiment Analysis Agent",
        framework=AgentFramework.ADK,
        capabilities=["analyze_sentiment", "detect_fake_news"]
    )
    
    # Create a task state
    state = protocol.create_state(
        task_id="task_001",
        symbol="RELIANCE.NS",
        company_name="Reliance Industries",
        user_query="Analyze Reliance stock",
        pending_agents=["price_agent", "sentiment_agent"]
    )
    
    # Send a message from CrewAI agent to ADK agent
    message = protocol.create_request(
        sender_id="price_agent",
        receiver_id="sentiment_agent",
        action="analyze_sentiment",
        payload={"symbol": "RELIANCE.NS", "price_change": 2.5},
        context=state.get_context_for_agent("sentiment_agent"),
        priority=MessagePriority.HIGH
    )
    
    msg_id = protocol.send_message(message)
    print(f"\n✅ Message sent: {msg_id}")
    print(f"   From: {message.sender_id} ({message.sender_framework.value})")
    print(f"   To: {message.receiver_id} ({message.receiver_framework.value})")
    print(f"   Action: {message.action}")
    
    # Get protocol stats
    stats = protocol.get_protocol_stats()
    print(f"\n📊 Protocol Stats:")
    print(f"   Total Agents: {stats['total_agents']}")
    print(f"   CrewAI Agents: {stats['crewai_agents']}")
    print(f"   ADK Agents: {stats['adk_agents']}")
    print(f"   Framework Interop Messages: {stats['framework_interop_messages']}")
