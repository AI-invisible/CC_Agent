"""
Task executor module for executing plans and steps
"""
import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from openai import OpenAI

from .models import (
    AgentConfig,
    ExecutionStatus,
    PlanStatus,
    Step,
    StepResult,
    StepStatus,
    TaskExecution,
    TaskPlan
)
from .error_handler import ErrorHandler


class TaskExecutor:
    """Task executor for executing plans and steps"""

    def __init__(self, config: AgentConfig):
        """
        Initialize task executor

        Args:
            config: Agent configuration
        """
        self.config = config
        self.error_handler = ErrorHandler(config.retry_config)
        self.client = OpenAI(
            base_url=config.llm_config.base_url,
            api_key=config.llm_config.api_key
        )
        self.tool_registry: Dict[str, Callable] = {}

    async def execute(
        self,
        plan: TaskPlan,
        user_intervention: Optional[Dict[str, Any]] = None
    ) -> TaskExecution:
        """
        Execute task plan

        Args:
            plan: Execution plan
            user_intervention: User intervention options

        Returns:
            TaskExecution: Execution result
        """
        execution_id = str(uuid.uuid4())

        # Create execution record
        execution = TaskExecution(
            execution_id=execution_id,
            plan_id=plan.plan_id,
            status=ExecutionStatus.RUNNING
        )

        # Update plan status
        plan.status = PlanStatus.EXECUTING

        try:
            # Execute steps
            step_results = []
            context = {
                "plan": plan,
                "execution": execution,
                "user_intervention": user_intervention or {},
                "step_outputs": {}
            }

            for step in plan.steps:
                # Check if step should be executed
                if not self._should_execute_step(step, context):
                    step.status = StepStatus.SKIPPED
                    continue

                # Execute step
                step_result = await self.execute_step(step, context)
                step_results.append(step_result)

                # Store output in context for dependent steps
                context["step_outputs"][step.step_id] = step_result.output

                # Check if execution should continue
                if not step_result.success and not self._can_continue_on_failure(step, context):
                    execution.status = ExecutionStatus.FAILED
                    break

            # Update execution
            execution.step_results = step_results
            execution.ended_at = datetime.now()
            execution.total_duration = (
                execution.ended_at - execution.started_at
            ).total_seconds()

            # Determine final status
            if execution.status == ExecutionStatus.RUNNING:
                if all(r.success for r in step_results):
                    execution.status = ExecutionStatus.COMPLETED
                    plan.status = PlanStatus.COMPLETED
                else:
                    execution.status = ExecutionStatus.FAILED
                    plan.status = PlanStatus.FAILED

            # Generate summary
            execution.summary = self._generate_summary(execution, plan)

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.ended_at = datetime.now()
            execution.total_duration = (
                execution.ended_at - execution.started_at
            ).total_seconds()
            execution.summary = f"Execution failed with error: {str(e)}"

        return execution

    async def execute_step(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> StepResult:
        """
        Execute a single step

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            StepResult: Step execution result
        """
        start_time = datetime.now()
        step.start_time = start_time
        step.status = StepStatus.RUNNING

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._execute_step_internal(step, context),
                timeout=self.config.execution_config.timeout_per_step
            )

            # Calculate execution time
            end_time = datetime.now()
            step.end_time = end_time
            step.actual_duration = int((end_time - start_time).total_seconds())

            if result.success:
                step.status = StepStatus.COMPLETED
                step.output_data = result.output

            return result

        except asyncio.TimeoutError:
            step.status = StepStatus.FAILED
            step.end_time = datetime.now()

            error = Exception(f"Step execution timed out after {self.config.execution_config.timeout_per_step}s")

            # Try to retry
            if self.error_handler.should_retry(error, step.retry_count):
                step.retry_count += 1
                step.status = StepStatus.RETRYING
                return await self.error_handler.retry_step(step, self._execute_step_internal, context)

            # Return failure
            return StepResult(
                step_id=step.step_id,
                success=False,
                output=None,
                execution_time=self.config.execution_config.timeout_per_step,
                error=type(error).__name__
            )

        except Exception as e:
            step.status = StepStatus.FAILED
            step.end_time = datetime.now()

            # Try to retry
            if self.error_handler.should_retry(e, step.retry_count):
                step.retry_count += 1
                step.status = StepStatus.RETRYING
                return await self.error_handler.retry_step(step, self._execute_step_internal, context)

            # Handle error
            return await self.error_handler.handle_error(step, e, context)

    async def _execute_step_internal(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> StepResult:
        """
        Internal step execution logic

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            StepResult: Execution result
        """
        start_time = datetime.now()

        try:
            # Execute based on step type
            if step.step_type.value == "tool_call":
                output = await self._execute_tool_call(step, context)
            elif step.step_type.value == "decision":
                output = await self._execute_decision(step, context)
            else:
                # Default: use LLM to execute step
                output = await self._execute_with_llm(step, context)

            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return StepResult(
                step_id=step.step_id,
                success=True,
                output=output,
                execution_time=execution_time,
                metadata={}
            )

        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()

            return StepResult(
                step_id=step.step_id,
                success=False,
                output=str(e),
                execution_time=execution_time,
                error=type(e).__name__
            )

    async def _execute_tool_call(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute a tool call step

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Any: Tool output
        """
        tool_name = step.input_data.get("tool_name")
        if not tool_name:
            raise ValueError("Tool name not specified in step input")

        tool_func = self.tool_registry.get(tool_name)
        if not tool_func:
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        # Prepare tool arguments
        tool_args = step.input_data.get("tool_args", {})

        # Inject context outputs
        for key, value in context.get("step_outputs", {}).items():
            tool_args[f"output_{key}"] = value

        # Call tool
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**tool_args)
        else:
            result = tool_func(**tool_args)

        return result

    async def _execute_decision(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a decision step

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            Dict[str, Any]: Decision result
        """
        prompt = self._build_decision_prompt(step, context)

        response = self.client.chat.completions.create(
            model=self.config.llm_config.model_name,
            messages=[
                {"role": "system", "content": "You are a decision-making assistant. Respond with JSON only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=self.config.llm_config.temperature
        )

        content = response.choices[0].message.content

        # Parse decision result
        try:
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            return result
        except json.JSONDecodeError:
            # Fallback: return as plain text
            return {"decision": content}

    async def _execute_with_llm(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute step using LLM

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            str: LLM response
        """
        prompt = self._build_execution_prompt(step, context)

        response = self.client.chat.completions.create(
            model=self.config.llm_config.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful task execution assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=self.config.llm_config.max_tokens,
            temperature=self.config.llm_config.temperature
        )

        return response.choices[0].message.content

    def _build_execution_prompt(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for step execution"""
        prompt = f"""Execute the following step:

Step Description: {step.description}
Step Type: {step.step_type.value}

Context from previous steps:
{json.dumps(context.get("step_outputs", {}), indent=2, ensure_ascii=False)}

Please execute this step and provide the result."""

        return prompt

    def _build_decision_prompt(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for decision step"""
        prompt = f"""Make a decision based on the following information:

Decision Task: {step.description}

Available Context:
{json.dumps(context.get("step_outputs", {}), indent=2, ensure_ascii=False)}

Please make your decision and respond in JSON format with the following structure:
{{
  "decision": "your decision",
  "reasoning": "your reasoning",
  "confidence": 0.0-1.0
}}"""

        return prompt

    def _should_execute_step(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if step should be executed

        Args:
            step: Step to check
            context: Execution context

        Returns:
            bool: True if should execute
        """
        # Check if already completed
        if step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]:
            return False

        # Check if dependencies are satisfied
        step_outputs = context.get("step_outputs", {})
        for dep_id in step.dependencies:
            if dep_id not in step_outputs:
                return False

        # Check user intervention
        user_intervention = context.get("user_intervention", {})
        if user_intervention.get("skip_step") == step.step_id:
            return False

        return True

    def _can_continue_on_failure(
        self,
        step: Step,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if execution can continue after step failure

        Args:
            step: Failed step
            context: Execution context

        Returns:
            bool: True if can continue
        """
        # Check user intervention
        user_intervention = context.get("user_intervention", {})

        # If user explicitly chose to skip failed step
        if user_intervention.get("action") == "skip_failed":
            return True

        # Check step metadata
        if step.metadata.get("continue_on_failure", False):
            return True

        # Check if no dependent steps
        plan = context.get("plan")
        if plan:
            dependent_count = sum(
                1 for s in plan.steps
                if step.step_id in s.dependencies
            )
            return dependent_count == 0

        return False

    def _generate_summary(
        self,
        execution: TaskExecution,
        plan: TaskPlan
    ) -> str:
        """
        Generate execution summary

        Args:
            execution: Task execution record
            plan: Task plan

        Returns:
            str: Summary text
        """
        total_steps = len(plan.steps)
        completed_steps = len(execution.step_results)
        successful_steps = sum(1 for r in execution.step_results if r.success)
        failed_steps = completed_steps - successful_steps

        summary = f"""Task Execution Summary:
- Total Steps: {total_steps}
- Completed Steps: {completed_steps}
- Successful Steps: {successful_steps}
- Failed Steps: {failed_steps}
- Total Duration: {execution.total_duration:.2f}s
- Status: {execution.status.value}"""

        return summary

    def register_tool(self, name: str, func: Callable) -> None:
        """
        Register a tool for execution

        Args:
            name: Tool name
            func: Tool function
        """
        self.tool_registry[name] = func