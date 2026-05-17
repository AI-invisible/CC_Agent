"""
Plan generator module for decomposing complex tasks
"""
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .models import (
    AgentConfig,
    LLMConfig,
    PlanStatus,
    Step,
    StepType,
    TaskPlan
)


class PlanGenerator:
    """Plan generator for decomposing complex tasks into executable steps"""

    def __init__(self, llm_config: LLMConfig):
        """
        Initialize plan generator

        Args:
            llm_config: LLM configuration
        """
        self.llm_config = llm_config
        self.client = OpenAI(
            base_url=llm_config.base_url,
            api_key=llm_config.api_key
        )

    def generate(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TaskPlan:
        """
        Generate task execution plan

        Args:
            task: Task description
            context: Task context

        Returns:
            TaskPlan: Generated execution plan
        """
        plan_id = str(uuid.uuid4())

        # Construct prompt for plan generation
        prompt = self._build_plan_prompt(task, context)

        # Call LLM to generate plan
        plan_data = self._call_llm(prompt)

        # Parse plan data
        steps = self._parse_steps(plan_data)

        # Create task plan
        task_plan = TaskPlan(
            plan_id=plan_id,
            task_description=task,
            status=PlanStatus.READY,
            steps=steps,
            metadata=context or {}
        )

        # Validate plan
        self._validate_plan(task_plan)

        return task_plan

    def _build_plan_prompt(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for plan generation"""
        prompt = f"""You are a task planning expert. Please analyze the following task and break it down into executable steps.

Task: {task}

Context:
{json.dumps(context, indent=2, ensure_ascii=False) if context else "No additional context provided"}

Requirements:
1. Break down the task into clear, executable steps
2. Each step should have a specific goal
3. Determine dependencies between steps
4. Assign appropriate types to each step (tool_call, data_processing, decision, waiting, custom)
5. Estimate the execution time for each step

Please provide the plan in the following JSON format:

{{
  "steps": [
    {{
      "description": "Step description",
      "type": "tool_call",
      "dependencies": [],
      "estimated_duration": 10
    }}
  ]
}}

Ensure your response is valid JSON only, without any additional text or explanation."""

        return prompt

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        """
        Call LLM to generate plan

        Args:
            prompt: Prompt for plan generation

        Returns:
            Dict[str, Any]: Plan data from LLM
        """
        try:
            response = self.client.chat.completions.create(
                model=self.llm_config.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates structured JSON plans."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.llm_config.max_tokens,
                temperature=self.llm_config.temperature
            )

            content = response.choices[0].message.content

            # Extract JSON from response
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            plan_data = json.loads(content)
            return plan_data

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to call LLM: {e}")

    def _parse_steps(self, plan_data: Dict[str, Any]) -> List[Step]:
        """
        Parse steps from plan data

        Args:
            plan_data: Plan data from LLM

        Returns:
            List[Step]: List of parsed steps
        """
        steps = []
        steps_data = plan_data.get("steps", [])

        step_dict = {}
        for idx, step_data in enumerate(steps_data):
            step_type_str = step_data.get("type", "custom")

            # Map string to StepType enum
            try:
                step_type = StepType(step_type_str)
            except ValueError:
                step_type = StepType.CUSTOM

            # Ensure dependencies is a list of strings
            dependencies = step_data.get("dependencies", [])
            if isinstance(dependencies, int):
                dep_tmp = step_dict.get(dependencies, "")
                if not dep_tmp:
                    dependencies = []
                else:
                    dependencies = [dep_tmp]
            elif isinstance(dependencies, str):
                dependencies = [dependencies]
            elif not isinstance(dependencies, list):
                dependencies = []

            new_dep = []
            for value in dependencies:
                if not value:
                    continue
                if isinstance(value, int):
                    dep_tmp = step_dict.get(value, "")
                    if dep_tmp:
                        new_dep.append(dep_tmp)
                    continue
                new_dep.append(value)
            dependencies = new_dep

            id_tmp = f"step_{uuid.uuid4().hex[:8]}"
            step_dict[id] = id_tmp
            step = Step(
                step_id=id_tmp,
                step_number=idx + 1,
                description=step_data.get("description", f"Step {idx + 1}"),
                step_type=step_type,
                dependencies=dependencies,
                estimated_duration=step_data.get("estimated_duration")
            )

            steps.append(step)

        return steps

    def _validate_plan(self, plan: TaskPlan) -> bool:
        """
        Validate the generated plan

        Args:
            plan: Task plan to validate

        Returns:
            bool: True if plan is valid

        Raises:
            ValueError: If plan is invalid
        """
        if not plan.steps:
            raise ValueError("Plan must contain at least one step")

        # Check step dependencies
        step_ids = {step.step_id for step in plan.steps}

        for step in plan.steps:
            for dep_id in step.dependencies:
                if dep_id not in step_ids:
                    raise ValueError(f"Step {step.step_id} depends on non-existent step {dep_id}")

        # Check for circular dependencies
        if self._has_circular_dependencies(plan.steps):
            raise ValueError("Plan contains circular dependencies")

        return True

    def _has_circular_dependencies(self, steps: List[Step]) -> bool:
        """
        Check for circular dependencies using DFS

        Args:
            steps: List of steps

        Returns:
            bool: True if circular dependencies exist
        """
        visited = set()
        recursion_stack = set()

        step_map = {step.step_id: step for step in steps}

        def visit(step_id: str) -> bool:
            visited.add(step_id)
            recursion_stack.add(step_id)

            step = step_map.get(step_id)
            if step:
                for dep_id in step.dependencies:
                    if dep_id not in visited:
                        if visit(dep_id):
                            return True
                    elif dep_id in recursion_stack:
                        return True

            recursion_stack.remove(step_id)
            return False

        for step in steps:
            if step.step_id not in visited:
                if visit(step.step_id):
                    return True

        return False