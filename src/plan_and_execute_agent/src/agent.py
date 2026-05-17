"""
Main Agent class for Plan and Execute Agent
"""
from typing import Any, Dict, Optional

from .models import (
    AgentConfig,
    LLMConfig,
    TaskExecution,
    TaskPlan
)
from .plan_generator import PlanGenerator
from .task_executor import TaskExecutor
from .result_recorder import ResultRecorder


class PlanAndExecuteAgent:
    """Plan and Execute Agent for decomposing and executing complex tasks"""

    def __init__(self, config: AgentConfig):
        """
        Initialize the agent

        Args:
            config: Agent configuration
        """
        self.config = config

        # Initialize components
        self.plan_generator = PlanGenerator(config.llm_config)
        self.task_executor = TaskExecutor(config)
        self.result_recorder = ResultRecorder()

    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        save_plan: bool = True,
        save_results: bool = True
    ) -> TaskExecution:
        """
        Execute a complex task

        Args:
            task: Task description
            context: Task context information
            save_plan: Whether to save the plan
            save_results: Whether to save the results

        Returns:
            TaskExecution: Task execution result
        """
        print(f"\n{'='*60}")
        print(f"Task: {task}")
        print(f"{'='*60}\n")

        # Step 1: Generate plan
        print("Step 1: Generating execution plan...")
        plan = await self.generate_plan(task, context)

        if save_plan:
            self.result_recorder.record_plan(plan)
            print(f"Plan saved with ID: {plan.plan_id}")

        print(f"\nGenerated plan with {len(plan.steps)} steps:")
        for step in plan.steps:
            print(f"  {step.step_number}. {step.description} [{step.step_type.value}]")
            if step.dependencies:
                print(f"     Dependencies: {step.dependencies}")

        print("\n" + "-"*60 + "\n")

        # Step 2: Execute plan
        print("Step 2: Executing plan...")
        execution = await self.execute_plan(plan)

        if save_results:
            self.result_recorder.record_execution(execution)
            print(f"Execution saved with ID: {execution.execution_id}")

        # Step 3: Display results
        print("\n" + "-"*60 + "\n")
        print("Step 3: Execution Results")
        print("-"*60)

        for idx, result in enumerate(execution.step_results, 1):
            status = "✓" if result.success else "✗"
            print(f"{status} Step {idx}: {result.step_id}")
            print(f"  Status: {'Success' if result.success else 'Failed'}")
            print(f"  Execution Time: {result.execution_time:.2f}s")

            if result.success:
                output_preview = str(result.output)[:100]
                if len(str(result.output)) > 100:
                    output_preview += "..."
                print(f"  Output: {output_preview}")
            else:
                print(f"  Error: {result.error}")

            print()

        print("-"*60)
        print(f"Execution Summary:")
        print(f"  Total Steps: {len(execution.step_results)}")
        print(f"  Successful: {sum(1 for r in execution.step_results if r.success)}")
        print(f"  Failed: {sum(1 for r in execution.step_results if not r.success)}")
        print(f"  Total Duration: {execution.total_duration:.2f}s")
        print(f"  Final Status: {execution.status.value}")
        print("="*60 + "\n")

        return execution

    async def generate_plan(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskPlan:
        """
        Generate execution plan for a task

        Args:
            task: Task description
            context: Task context information

        Returns:
            TaskPlan: Generated execution plan
        """
        return self.plan_generator.generate(task, context)

    async def execute_plan(
        self,
        plan: TaskPlan,
        user_intervention: Optional[Dict[str, Any]] = None
    ) -> TaskExecution:
        """
        Execute a task plan

        Args:
            plan: Execution plan
            user_intervention: User intervention options

        Returns:
            TaskExecution: Execution result
        """
        return await self.task_executor.execute(plan, user_intervention)

    def register_tool(self, name: str, func) -> None:
        """
        Register a tool for the agent to use

        Args:
            name: Tool name
            func: Tool function
        """
        self.task_executor.register_tool(name, func)

    def get_execution_status(self, execution_id: str) -> str:
        """
        Get execution status

        Args:
            execution_id: Execution ID

        Returns:
            str: Execution status
        """
        execution = self.result_recorder.get_execution(execution_id)
        return execution.status.value if execution else "Not found"

    def get_execution_result(self, execution_id: str) -> Optional[TaskExecution]:
        """
        Get execution result

        Args:
            execution_id: Execution ID

        Returns:
            Optional[TaskExecution]: Execution result
        """
        return self.result_recorder.get_execution(execution_id)

    def generate_report(self, execution_id: str) -> Dict[str, Any]:
        """
        Generate execution report

        Args:
            execution_id: Execution ID

        Returns:
            Dict[str, Any]: Execution report
        """
        return self.result_recorder.generate_report(execution_id)

    def list_plans(self, status: Optional[str] = None) -> list:
        """
        List all plans

        Args:
            status: Filter by status

        Returns:
            list: List of plans
        """
        return self.result_recorder.list_plans(status)

    def list_executions(self, status: Optional[str] = None) -> list:
        """
        List all executions

        Args:
            status: Filter by status

        Returns:
            list: List of executions
        """
        return self.result_recorder.list_executions(status)