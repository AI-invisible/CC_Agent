"""
Base classes and interfaces for the agent
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class AgentResponse:
    """Agent response object"""
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "tool_calls": self.tool_calls,
            "tool_results": self.tool_results,
            "metadata": self.metadata,
            "success": self.success,
            "error": self.error
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResponse':
        """Create from dictionary"""
        return cls(
            content=data.get("content", ""),
            tool_calls=data.get("tool_calls"),
            tool_results=data.get("tool_results"),
            metadata=data.get("metadata", {}),
            success=data.get("success", True),
            error=data.get("error")
        )

@dataclass
class AgentConfig:
    """Agent configuration"""
    # LLM Configuration
    model_name: str = "deepseek-ai/DeepSeek-R1"
    temperature: float = 0.7
    max_tokens: int = 2000

    # Tool calling configuration
    max_tool_calls: int = 5
    tool_timeout: int = 30
    retry_attempts: int = 3

    # Context management configuration
    max_context_messages: int = 20
    context_summary_threshold: int = 15

    # Fallback handling configuration
    enable_fallback: bool = True
    fallback_timeout: int = 10

    # LangGraph configuration
    checkpoint_ns: str = "tool_use_agent"
    checkpointer_type: str = "memory"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "max_tool_calls": self.max_tool_calls,
            "tool_timeout": self.tool_timeout,
            "retry_attempts": self.retry_attempts,
            "max_context_messages": self.max_context_messages,
            "context_summary_threshold": self.context_summary_threshold,
            "enable_fallback": self.enable_fallback,
            "fallback_timeout": self.fallback_timeout,
            "checkpoint_ns": self.checkpoint_ns,
            "checkpointer_type": self.checkpointer_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentConfig':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def load_from_file(cls, config_path: str) -> 'AgentConfig':
        """Load from JSON or YAML file"""
        if config_path.endswith('.json'):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif config_path.endswith(('.yaml', '.yml')):
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config file format: {config_path}")
        return cls.from_dict(data)

    def save_to_file(self, config_path: str) -> None:
        """Save to JSON or YAML file"""
        data = self.to_dict()
        if config_path.endswith('.json'):
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif config_path.endswith(('.yaml', '.yml')):
            import yaml
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported config file format: {config_path}")