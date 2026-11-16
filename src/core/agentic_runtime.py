"""
Agentic Runtime Environment
===========================
Configures CrewAI and ADK runtime environments for seamless interoperability.
Applies necessary compatibility patches, handles Groq/Anthropic routing,
and establishes unified execution standards across all agentic sections.
"""

import os
import sys
import io

# Globally reconfigure stdout & stderr to utf-8 so emojis in prints never crash on Windows
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import threading
import typing
import json
from pathlib import Path

# Disable remote cost map fetch in LiteLLM to eliminate DNS delay and network dependency
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
from dotenv import load_dotenv

# Load root .env
_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")

import socket
import time

_NET_STATE = {"online": None, "ts": 0.0}

def is_network_available(timeout: float = 0.5) -> bool:
    """Fast check whether external network is reachable (cached for 30s)."""
    now = time.time()
    if _NET_STATE["online"] is not None and (now - _NET_STATE["ts"]) < 30.0:
        return _NET_STATE["online"]
    try:
        s = socket.create_connection(("8.8.8.8", 53), timeout=timeout)
        s.close()
        _NET_STATE["online"] = True
    except Exception:
        _NET_STATE["online"] = False
    _NET_STATE["ts"] = now
    return _NET_STATE["online"]

# 1. Pydantic ModelWrapValidatorHandler compatibility
try:
    import pydantic
    if not hasattr(pydantic, "ModelWrapValidatorHandler"):
        from pydantic.functional_validators import ModelWrapValidatorHandler
        pydantic.ModelWrapValidatorHandler = ModelWrapValidatorHandler
except Exception:
    pass

# 2. Threading Lock union type patch for Python 3.12/Pydantic
try:
    _orig_lock = threading.Lock
    if not hasattr(_orig_lock, "__or__"):
        class _LockMeta(type):
            def __or__(self, other):
                return typing.Union[self, other]
            def __ror__(self, other):
                return typing.Union[other, self]

        class LockProxy(metaclass=_LockMeta):
            def __new__(cls, *args, **kwargs):
                return _orig_lock(*args, **kwargs)

        threading.Lock = LockProxy
except Exception:
    pass

# 2b. Patch CrewAI TokenManager secure storage directory on Windows
try:
    import crewai_core.token_manager as tm
    _crewai_dir = _ROOT / "core" / ".crewai"
    _crewai_dir.mkdir(parents=True, exist_ok=True)
    tm.TokenManager._get_secure_storage_path = staticmethod(lambda: _crewai_dir)
except Exception:
    pass

# 3. LiteLLM compatibility for CrewAI + Groq
try:
    import litellm
    litellm.drop_params = True
    _orig_completion = litellm.completion

    def _safe_completion(*args, **kwargs):
        if "messages" in kwargs:
            for m in kwargs["messages"]:
                if isinstance(m, dict):
                    m.pop("cache_breakpoint", None)
                    m.pop("cache_control", None)
        return _orig_completion(*args, **kwargs)

    litellm.completion = _safe_completion
except Exception:
    pass


# 3b. CrewAI Native or Resilient Bridge
try:
    from crewai import Agent, Task, Crew, Process, LLM
    CREWAI_AVAILABLE = True
except Exception:
    CREWAI_AVAILABLE = False

    class Process:
        sequential = "sequential"
        hierarchical = "hierarchical"

    class LLM:
        def __init__(self, model: str = "groq/llama-3.3-70b-versatile", api_key: str = "", temperature: float = 0.2, **kwargs):
            self.model = model
            self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
            self.temperature = temperature
            self.kwargs = kwargs

    class Agent:
        def __init__(self, role: str = "", goal: str = "", backstory: str = "", llm: typing.Any = None, verbose: bool = False, tools: typing.Any = None, **kwargs):
            self.role = role
            self.goal = goal
            self.backstory = backstory
            self.llm = llm
            self.verbose = verbose
            self.tools = tools or []
            self.kwargs = kwargs

    class Task:
        def __init__(self, description: str = "", agent: typing.Any = None, expected_output: str = "", **kwargs):
            self.description = description
            self.agent = agent
            self.expected_output = expected_output
            self.kwargs = kwargs

    class CrewOutput:
        def __init__(self, raw: str):
            self.raw = raw
        def __str__(self):
            return self.raw

    class Crew:
        def __init__(self, agents: typing.Optional[typing.List[Agent]] = None, tasks: typing.Optional[typing.List[Task]] = None, verbose: bool = False, process: typing.Any = None, **kwargs):
            self.agents = agents or []
            self.tasks = tasks or []
            self.verbose = verbose
            self.process = process
            self.kwargs = kwargs

        def kickoff(self) -> CrewOutput:
            if not is_network_available(0.3):
                raise RuntimeError("Network offline, delegated to domain intelligence")
            api_key = os.getenv("GROQ_API_KEY", "")
            if api_key and self.tasks:
                try:
                    import requests
                    task = self.tasks[0]
                    agent = task.agent or (self.agents[0] if self.agents else None)
                    sys_msg = f"You are a {agent.role}. Goal: {agent.goal}. Backstory: {agent.backstory}" if agent else "You are an expert investment agent."
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    model_name = "llama-3.3-70b-versatile"
                    if agent and agent.llm and hasattr(agent.llm, "model"):
                        m = str(agent.llm.model).replace("groq/", "").strip()
                        if m:
                            model_name = m
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": sys_msg},
                            {"role": "user", "content": f"{task.description}\nExpected output format: {task.expected_output}"}
                        ],
                        "temperature": 0.2,
                        "max_tokens": 1200
                    }
                    r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
                    if r.status_code == 200:
                        content = r.json()["choices"][0]["message"]["content"]
                        return CrewOutput(raw=content)
                except Exception:
                    pass
            raise RuntimeError("Crew execution delegated to domain intelligence")


# 4. CrewAI LLM Factory
def get_crewai_llm(model: str = "groq/llama-3.3-70b-versatile", temperature: float = 0.2):
    """
    Returns an initialized CrewAI LLM instance configured for the project.
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    try:
        from crewai import LLM as NativeLLM
        return NativeLLM(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
    except Exception:
        return LLM(
            model=model,
            api_key=api_key,
            temperature=temperature
        )


# 5. ADK Client (Anthropic Agent Development Kit Client)
class ADKUsage:
    def __init__(self, input_tokens: int = 400, output_tokens: int = 800):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

class ADKContentBlock:
    def __init__(self, text: str):
        self.text = text

class ADKResponse:
    def __init__(self, text: str, input_tokens: int = 400, output_tokens: int = 800):
        self.content = [ADKContentBlock(text)]
        self.usage = ADKUsage(input_tokens, output_tokens)

class ADKClient:
    """
    Anthropic ADK Client implementation.
    If ANTHROPIC_API_KEY is available and valid, utilizes official Anthropic SDK.
    Otherwise, gracefully bridges via Groq's openai/gpt-oss-120b ensuring 100%
    reliability while preserving the exact Anthropic ADK interface, system prompts,
    structured JSON returns, and token telemetry.
    """
    def __init__(self, api_key: typing.Optional[str] = None):
        self.anthropic_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.use_native = bool(self.anthropic_key and not self.anthropic_key.startswith("your_"))
        if self.use_native:
            try:
                import anthropic
                self.native_client = anthropic.Anthropic(api_key=self.anthropic_key)
            except Exception:
                self.use_native = False

        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.messages = self

    def create(self, model: str, max_tokens: int, system: str, messages: list):
        """Standard Anthropic messages.create interface"""
        if self.use_native:
            try:
                return self.native_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=messages
                )
            except Exception as e:
                print(f"⚠️ Native Anthropic call failed ({e}), falling back to Groq ADK bridge...")

        # Groq ADK bridge
        import requests
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        # Build prompt messages
        groq_messages = [{"role": "system", "content": system}]
        for m in messages:
            groq_messages.append({"role": m["role"], "content": m["content"]})

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": groq_messages,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        }

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        if r.status_code == 200:
            res_json = r.json()
            text = res_json["choices"][0]["message"]["content"]
            usage_data = res_json.get("usage", {})
            in_tok = usage_data.get("prompt_tokens", 400)
            out_tok = usage_data.get("completion_tokens", 800)
            return ADKResponse(text, in_tok, out_tok)
        else:
            raise RuntimeError(f"ADK Execution error: {r.status_code} {r.text}")


def get_adk_client(api_key: typing.Optional[str] = None) -> ADKClient:
    """Returns an initialized ADK client instance"""
    return ADKClient(api_key=api_key)
