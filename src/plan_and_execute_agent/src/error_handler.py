"""
Error handler module for managing execution errors and retries
"""
import asyncio
import time
from datetime import datetime
from typing import Any, Dict, Optional

from .models import (
    ErrorInfo,
    RetryConfig,
    Step,
    StepResult,
    StepStatus
)


class ErrorHandler:
    """Error handler for managing execution errors and retries"""

    def __init__(self, retry_config: RetryConfig):
        """
        Initialize error handler

        Args:
            retry_config: Retry configuration
        """
        self.retry_config = retry_config

    def should_retry(
        self,
        error: Exception,
        retry_count: int
    ) -> bool:
        """
        Determine if a step should be retried

        Args:
            error: The error that occurred
            retry_count: Current retry count

        Returns:
            bool: True if should retry
        """
        # Check max retries
        if retry_count >= self.retry_config.max_retries:
            return False

        # Check if error is retryable
        error_type = type(error).__name__
        if self.retry_config.retryable_errors:
            return error_type in self.retry_config.retryable_errors

        # Default: retry on common retryable errors
        retryable_types = {
            'ConnectionError',
            'TimeoutError',
            'APIError',
            'RateLimitError',
            'TemporaryFailure'
        }

        return error_type in retryable_types

    async def retry_step(
        self,
        step: Step,
        execute_func,
        context: Dict[str, Any]
    ) -> StepResult:
        """
        Retry a failed step with exponential backoff

        Args:
            step: The step to retry
            execute_func: Function to execute the step
            context: Execution context

        Returns:
            StepResult: Result of retry execution
        """
        retry_count = 0
        last_error = None

        while retry_count <= self.retry_config.max_retries:
            try:
                # Execute step
                result = await execute_func(step, context)

                if result.success:
                    return result

                # If execution failed but not raised exception, treat as error
                last_error = Exception(result.output)

            except Exception as e:
                last_error = e

            # Check if should retry
            if not self.should_retry(last_error, retry_count):
                break

            # Calculate delay with exponential backoff
            if self.retry_config.exponential_backoff:
                delay = self.retry_config.retry_delay * (2 ** retry_count)
            else:
                delay = self.retry_config.retry_delay

            retry_count += 1

            if retry_count <= self.retry_config.max_retries:
                # Log retry attempt
                await self._log_retry_attempt(step, retry_count, delay, last_error)
                await asyncio.sleep(delay)

        # All retries failed
        error_info = ErrorInfo(
            error_type=type(last_error).__name__,
            error_message=str(last_error),
            stack_trace=traceback_str(last_error),
            context={"retry_count": retry_count}
        )

        return StepResult(
            step_id=step.step_id,
            success=False,
            output=None,
            execution_time=0.0,
            error=error_info
        )

    async def handle_error(
        self,
        step: Step,
        error: Exception,
        execution_context: Dict[str, Any]
    ) -> StepResult:
        """
        Handle execution error

        Args:
            step: The step that failed
            error: The error that occurred
            execution_context: Execution context

        Returns:
            StepResult: Error handling result
        """
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback_str(error),
            context=execution_context
        )

        # Record error in step
        step.error_info = error_info

        # Determine if should skip or fail
        can_skip = self._can_skip_step(step, execution_context)

        if can_skip:
            step.status = StepStatus.SKIPPED
            return StepResult(
                step_id=step.step_id,
                success=False,
                output=None,
                execution_time=0.0,
                error=error_info,
                metadata={"action": "skipped"}
            )
        else:
            step.status = StepStatus.FAILED
            return StepResult(
                step_id=step.step_id,
                success=False,
                output=None,
                execution_time=0.0,
                error=error_info,
                metadata={"action": "failed"}
            )

    def _can_skip_step(
        self,
        step: Step,
        execution_context: Dict[str, Any]
    ) -> bool:
        """
        Determine if a step can be skipped

        Args:
            step: The step to check
            execution_context: Execution context

        Returns:
            bool: True if step can be skipped
        """
        # Check if step has skip flag in metadata
        if step.metadata.get("can_skip", False):
            return True

        # Check if step is optional (no dependent steps)
        plan = execution_context.get("plan")
        if plan:
            # Count how many steps depend on this step
            dependent_count = sum(
                1 for s in plan.steps
                if step.step_id in s.dependencies
            )
            return dependent_count == 0

        return False

    async def _log_retry_attempt(
        self,
        step: Step,
        retry_count: int,
        delay: float,
        error: Exception
    ) -> None:
        """
        Log retry attempt

        Args:
            step: The step being retried
            retry_count: Current retry count
            delay: Delay before next retry
            error: The error that occurred
        """
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] Retrying step {step.step_id} (attempt {retry_count + 1}/{self.retry_config.max_retries}) "
              f"after {delay:.2f}s delay. Error: {error}")


def traceback_str(error: Exception) -> str:
    """
    Get traceback string from exception

    Args:
        error: The exception

    Returns:
        str: Traceback string
    """
    import traceback
    return ''.join(traceback.format_exception(type(error), error, error.__traceback__))