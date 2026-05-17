"""
Result recorder module for recording and managing execution results
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    StepResult,
    TaskExecution,
    TaskPlan
)


class ResultRecorder:
    """Result recorder for recording and managing execution results"""

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize result recorder

        Args:
            storage_dir: Directory for storing results
        """
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path(__file__).parent.parent.parent / "results"

        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.plans_dir = self.storage_dir / "plans"
        self.executions_dir = self.storage_dir / "executions"
        self.logs_dir = self.storage_dir / "logs"

        self.plans_dir.mkdir(exist_ok=True)
        self.executions_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def record_plan(self, plan: TaskPlan) -> bool:
        """
        Record task plan

        Args:
            plan: Task plan to record

        Returns:
            bool: True if successful
        """
        try:
            plan_file = self.plans_dir / f"{plan.plan_id}.json"

            plan_data = {
                "plan_id": plan.plan_id,
                "task_description": plan.task_description,
                "created_at": plan.created_at.isoformat(),
                "updated_at": plan.updated_at.isoformat(),
                "status": plan.status.value,
                "steps": [self._step_to_dict(step) for step in plan.steps],
                "metadata": plan.metadata
            }

            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Failed to record plan: {e}")
            return False

    def record_execution(self, execution: TaskExecution) -> bool:
        """
        Record task execution

        Args:
            execution: Task execution to record

        Returns:
            bool: True if successful
        """
        try:
            execution_file = self.executions_dir / f"{execution.execution_id}.json"

            execution_data = {
                "execution_id": execution.execution_id,
                "plan_id": execution.plan_id,
                "started_at": execution.started_at.isoformat(),
                "ended_at": execution.ended_at.isoformat() if execution.ended_at else None,
                "status": execution.status.value,
                "step_results": [self._step_result_to_dict(result) for result in execution.step_results],
                "total_duration": execution.total_duration,
                "summary": execution.summary
            }

            with open(execution_file, 'w', encoding='utf-8') as f:
                json.dump(execution_data, f, indent=2, ensure_ascii=False)

            # Also record as log
            self._log_execution(execution)

            return True

        except Exception as e:
            print(f"Failed to record execution: {e}")
            return False

    def record_step_result(self, result: StepResult) -> bool:
        """
        Record step result

        Args:
            result: Step result to record

        Returns:
            bool: True if successful
        """
        try:
            log_file = self.logs_dir / f"step_{result.step_id}.log"

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "step_id": result.step_id,
                "success": result.success,
                "output": str(result.output),
                "execution_time": result.execution_time,
                "error": result.error if hasattr(result, 'error') else None,
                "metadata": result.metadata
            }

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            return True

        except Exception as e:
            print(f"Failed to record step result: {e}")
            return False

    def get_plan(self, plan_id: str) -> Optional[TaskPlan]:
        """
        Get task plan by ID

        Args:
            plan_id: Plan ID

        Returns:
            Optional[TaskPlan]: Task plan if found
        """
        try:
            plan_file = self.plans_dir / f"{plan_id}.json"

            if not plan_file.exists():
                return None

            with open(plan_file, 'r', encoding='utf-8') as f:
                plan_data = json.load(f)

            steps = [self._dict_to_step(step_data) for step_data in plan_data.get("steps", [])]

            plan = TaskPlan(
                plan_id=plan_data["plan_id"],
                task_description=plan_data["task_description"],
                created_at=datetime.fromisoformat(plan_data["created_at"]),
                updated_at=datetime.fromisoformat(plan_data["updated_at"]),
                status=plan_data["status"],
                steps=steps,
                metadata=plan_data.get("metadata", {})
            )

            return plan

        except Exception as e:
            print(f"Failed to get plan: {e}")
            return None

    def get_execution(self, execution_id: str) -> Optional[TaskExecution]:
        """
        Get task execution by ID

        Args:
            execution_id: Execution ID

        Returns:
            Optional[TaskExecution]: Task execution if found
        """
        try:
            execution_file = self.executions_dir / f"{execution_id}.json"

            if not execution_file.exists():
                return None

            with open(execution_file, 'r', encoding='utf-8') as f:
                execution_data = json.load(f)

            step_results = [
                self._dict_to_step_result(result_data)
                for result_data in execution_data.get("step_results", [])
            ]

            execution = TaskExecution(
                execution_id=execution_data["execution_id"],
                plan_id=execution_data["plan_id"],
                started_at=datetime.fromisoformat(execution_data["started_at"]),
                ended_at=datetime.fromisoformat(execution_data["ended_at"]) if execution_data.get("ended_at") else None,
                status=execution_data["status"],
                step_results=step_results,
                total_duration=execution_data.get("total_duration"),
                summary=execution_data.get("summary")
            )

            return execution

        except Exception as e:
            print(f"Failed to get execution: {e}")
            return None

    def get_step_result(self, step_id: str) -> Optional[StepResult]:
        """
        Get step result by ID

        Args:
            step_id: Step ID

        Returns:
            Optional[StepResult]: Step result if found
        """
        try:
            log_file = self.logs_dir / f"step_{step_id}.log"

            if not log_file.exists():
                return None

            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Get the last entry
            if not lines:
                return None

            last_entry = json.loads(lines[-1].strip())

            result = StepResult(
                step_id=last_entry["step_id"],
                success=last_entry["success"],
                output=last_entry["output"],
                execution_time=last_entry["execution_time"],
                error=last_entry.get("error"),
                metadata=last_entry.get("metadata", {})
            )

            return result

        except Exception as e:
            print(f"Failed to get step result: {e}")
            return None

    def generate_report(self, execution_id: str) -> Dict[str, Any]:
        """
        Generate execution report

        Args:
            execution_id: Execution ID

        Returns:
            Dict[str, Any]: Execution report
        """
        execution = self.get_execution(execution_id)

        if not execution:
            return {"error": "Execution not found"}

        plan = self.get_plan(execution.plan_id)

        report = {
            "execution_id": execution.execution_id,
            "plan_id": execution.plan_id,
            "task_description": plan.task_description if plan else "Unknown",
            "status": execution.status.value,
            "started_at": execution.started_at.isoformat(),
            "ended_at": execution.ended_at.isoformat() if execution.ended_at else None,
            "total_duration": execution.total_duration,
            "total_steps": len(execution.step_results),
            "successful_steps": sum(1 for r in execution.step_results if r.success),
            "failed_steps": sum(1 for r in execution.step_results if not r.success),
            "summary": execution.summary,
            "step_details": [
                {
                    "step_id": result.step_id,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "output": str(result.output)[:200] + "..." if len(str(result.output)) > 200 else str(result.output)
                }
                for result in execution.step_results
            ]
        }

        return report

    def list_plans(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all plans

        Args:
            status: Filter by status

        Returns:
            List[Dict[str, Any]]: List of plans
        """
        try:
            plans = []

            for plan_file in self.plans_dir.glob("*.json"):
                with open(plan_file, 'r', encoding='utf-8') as f:
                    plan_data = json.load(f)

                if status is None or plan_data["status"] == status:
                    plans.append({
                        "plan_id": plan_data["plan_id"],
                        "task_description": plan_data["task_description"],
                        "created_at": plan_data["created_at"],
                        "status": plan_data["status"],
                        "num_steps": len(plan_data.get("steps", []))
                    })

            return sorted(plans, key=lambda x: x["created_at"], reverse=True)

        except Exception as e:
            print(f"Failed to list plans: {e}")
            return []

    def list_executions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all executions

        Args:
            status: Filter by status

        Returns:
            List[Dict[str, Any]]: List of executions
        """
        try:
            executions = []

            for execution_file in self.executions_dir.glob("*.json"):
                with open(execution_file, 'r', encoding='utf-8') as f:
                    execution_data = json.load(f)

                if status is None or execution_data["status"] == status:
                    executions.append({
                        "execution_id": execution_data["execution_id"],
                        "plan_id": execution_data["plan_id"],
                        "started_at": execution_data["started_at"],
                        "status": execution_data["status"],
                        "total_duration": execution_data.get("total_duration"),
                        "num_steps": len(execution_data.get("step_results", []))
                    })

            return sorted(executions, key=lambda x: x["started_at"], reverse=True)

        except Exception as e:
            print(f"Failed to list executions: {e}")
            return []

    def _step_to_dict(self, step: Any) -> Dict[str, Any]:
        """Convert step to dictionary"""
        return {
            "step_id": step.step_id,
            "step_number": step.step_number,
            "description": step.description,
            "step_type": step.step_type.value,
            "dependencies": step.dependencies,
            "input_data": step.input_data,
            "output_data": step.output_data,
            "status": step.status.value,
            "retry_count": step.retry_count,
            "start_time": step.start_time.isoformat() if step.start_time else None,
            "end_time": step.end_time.isoformat() if step.end_time else None,
            "estimated_duration": step.estimated_duration,
            "actual_duration": step.actual_duration,
            "metadata": step.metadata
        }

    def _dict_to_step(self, step_data: Dict[str, Any]) -> Any:
        """Convert dictionary to step"""
        from .models import Step, StepStatus, StepType

        return Step(
            step_id=step_data["step_id"],
            step_number=step_data["step_number"],
            description=step_data["description"],
            step_type=StepType(step_data["step_type"]),
            dependencies=step_data["dependencies"],
            input_data=step_data["input_data"],
            output_data=step_data["output_data"],
            status=StepStatus(step_data["status"]),
            retry_count=step_data["retry_count"],
            start_time=datetime.fromisoformat(step_data["start_time"]) if step_data.get("start_time") else None,
            end_time=datetime.fromisoformat(step_data["end_time"]) if step_data.get("end_time") else None,
            estimated_duration=step_data.get("estimated_duration"),
            actual_duration=step_data.get("actual_duration"),
            metadata=step_data.get("metadata", {})
        )

    def _step_result_to_dict(self, result: StepResult) -> Dict[str, Any]:
        """Convert step result to dictionary"""
        return {
            "step_id": result.step_id,
            "success": result.success,
            "output": str(result.output),
            "execution_time": result.execution_time,
            "error": result.error,
            "metadata": result.metadata
        }

    def _dict_to_step_result(self, result_data: Dict[str, Any]) -> StepResult:
        """Convert dictionary to step result"""
        return StepResult(
            step_id=result_data["step_id"],
            success=result_data["success"],
            output=result_data["output"],
            execution_time=result_data["execution_time"],
            error=result_data.get("error"),
            metadata=result_data.get("metadata", {})
        )

    def _log_execution(self, execution: TaskExecution) -> None:
        """
        Log execution to file

        Args:
            execution: Task execution to log
        """
        log_file = self.logs_dir / f"execution_{execution.execution_id}.log"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "execution_id": execution.execution_id,
            "plan_id": execution.plan_id,
            "status": execution.status.value,
            "summary": execution.summary
        }

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")