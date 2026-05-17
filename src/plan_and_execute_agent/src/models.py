"""
Data models for Plan and Execute Agent
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PlanStatus(str, Enum):
    """Plan status enumeration"""
    DRAFT = "draft"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Step status enumeration"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class ExecutionStatus(str, Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepType(str, Enum):
    """Step type enumeration"""
    TOOL_CALL = "tool_call"
    DATA_PROCESSING = "data_processing"
    DECISION = "decision"
    WAITING = "waiting"
    CUSTOM = "custom"


class ErrorInfo(BaseModel):
    """Error information model"""
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    context: Optional[Dict[str, Any]] = None


class Step(BaseModel):
    """Execution step model"""
    step_id: str
    step_number: int
    description: str
    step_type: StepType = StepType.CUSTOM
    dependencies: List[str] = Field(default_factory=list)
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    status: StepStatus = StepStatus.PENDING
    retry_count: int = 0
    error_info: Optional[ErrorInfo] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    estimated_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel):
    """Step execution result model"""
    step_id: str
    success: bool
    output: Any = None
    execution_time: float = 0.0
    error: Optional[ErrorInfo] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskPlan(BaseModel):
    """Task plan model"""
    plan_id: str
    task_description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: PlanStatus = PlanStatus.DRAFT
    steps: List[Step] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskExecution(BaseModel):
    """Task execution record model"""
    execution_id: str
    plan_id: str
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    step_results: List[StepResult] = Field(default_factory=list)
    total_duration: Optional[float] = None
    summary: Optional[str] = None


class LLMConfig(BaseModel):
    """LLM configuration model"""
    base_url: str
    api_key: str
    model_name: str = "deepseek-ai/DeepSeek-R1"
    max_tokens: int = 4096
    temperature: float = 0.7


class ExecutionConfig(BaseModel):
    """Execution configuration model"""
    max_concurrent_steps: int = 1
    timeout_per_step: int = 300
    total_timeout: int = 3600
    enable_parallel: bool = False
    checkpoint_interval: int = 60


class RetryConfig(BaseModel):
    """Retry configuration model"""
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    retryable_errors: List[str] = Field(default_factory=list)


class AgentConfig(BaseModel):
    """Agent configuration model"""
    llm_config: LLMConfig
    execution_config: ExecutionConfig = Field(default_factory=ExecutionConfig)
    retry_config: RetryConfig = Field(default_factory=RetryConfig)