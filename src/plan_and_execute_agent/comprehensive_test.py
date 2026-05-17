"""
Comprehensive test for Plan and Execute Agent
"""
import asyncio
import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import PlanAndExecuteAgent
from src.models import AgentConfig, LLMConfig, StepType, StepStatus, ExecutionStatus


def test_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("Test 1: Module Imports")
    print("=" * 60)

    try:
        from src.models import (
            PlanStatus, StepStatus, ExecutionStatus, StepType,
            ErrorInfo, Step, StepResult, TaskPlan, TaskExecution,
            LLMConfig, ExecutionConfig, RetryConfig, AgentConfig
        )
        print("✓ All models imported successfully")

        from src.plan_generator import PlanGenerator
        print("✓ PlanGenerator imported successfully")

        from src.task_executor import TaskExecutor
        print("✓ TaskExecutor imported successfully")

        from src.error_handler import ErrorHandler
        print("✓ ErrorHandler imported successfully")

        from src.result_recorder import ResultRecorder
        print("✓ ResultRecorder imported successfully")

        from src.agent import PlanAndExecuteAgent
        print("✓ PlanAndExecuteAgent imported successfully")

        return True

    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False


def test_models():
    """Test model creation and validation"""
    print("\n" + "=" * 60)
    print("Test 2: Model Creation")
    print("=" * 60)

    try:
        # Test LLMConfig
        llm_config = LLMConfig(
            base_url='https://api.siliconflow.cn/v1/',
            api_key='test-key',
            model_name='deepseek-ai/DeepSeek-R1',
            max_tokens=4096,
            temperature=0.7
        )
        print(f"✓ LLMConfig created: {llm_config.model_name}")

        # Test AgentConfig
        agent_config = AgentConfig(llm_config=llm_config)
        print(f"✓ AgentConfig created")

        # Test Step
        step = Step(
            step_id="test_step",
            step_number=1,
            description="Test step",
            step_type=StepType.TOOL_CALL
        )
        print(f"✓ Step created: {step.description}")

        # Test StepResult
        result = StepResult(
            step_id="test_step",
            success=True,
            output="Test output"
        )
        print(f"✓ StepResult created: {result.success}")

        # Test TaskPlan
        plan = TaskPlan(
            plan_id="test_plan",
            task_description="Test task",
            steps=[step]
        )
        print(f"✓ TaskPlan created with {len(plan.steps)} steps")

        # Test TaskExecution
        execution = TaskExecution(
            execution_id="test_execution",
            plan_id="test_plan",
            step_results=[result]
        )
        print(f"✓ TaskExecution created: {execution.execution_id}")

        return True

    except Exception as e:
        print(f"✗ Model creation failed: {e}")
        traceback.print_exc()
        return False


def test_result_recorder():
    """Test result recorder functionality"""
    print("\n" + "=" * 60)
    print("Test 3: Result Recorder")
    print("=" * 60)

    try:
        from src.result_recorder import ResultRecorder
        from src.models import TaskPlan, Step, StepType, PlanStatus

        # Create recorder
        recorder = ResultRecorder()
        print(f"✓ ResultRecorder created")

        # Create a test plan
        step = Step(
            step_id="test_step",
            step_number=1,
            description="Test step",
            step_type=StepType.CUSTOM
        )

        plan = TaskPlan(
            plan_id="test_plan_123",
            task_description="Test task",
            status=PlanStatus.READY,
            steps=[step]
        )

        # Record plan
        success = recorder.record_plan(plan)
        print(f"✓ Plan recorded: {success}")

        # Retrieve plan
        retrieved_plan = recorder.get_plan("test_plan_123")
        print(f"✓ Plan retrieved: {retrieved_plan is not None}")

        # List plans
        plans = recorder.list_plans()
        print(f"✓ Listed {len(plans)} plans")

        # Test execution recording
        from src.models import TaskExecution, StepResult, ExecutionStatus

        step_result = StepResult(
            step_id="test_step",
            success=True,
            output="Test output"
        )

        execution = TaskExecution(
            execution_id="test_execution_123",
            plan_id="test_plan_123",
            status=ExecutionStatus.COMPLETED,
            step_results=[step_result]
        )

        # Record execution
        success = recorder.record_execution(execution)
        print(f"✓ Execution recorded: {success}")

        # Retrieve execution
        retrieved_execution = recorder.get_execution("test_execution_123")
        print(f"✓ Execution retrieved: {retrieved_execution is not None}")

        # Generate report
        report = recorder.generate_report("test_execution_123")
        print(f"✓ Report generated with keys: {list(report.keys())}")

        # List executions
        executions = recorder.list_executions()
        print(f"✓ Listed {len(executions)} executions")

        return True

    except Exception as e:
        print(f"✗ Result recorder test failed: {e}")
        traceback.print_exc()
        return False


def test_error_handler():
    """Test error handler functionality"""
    print("\n" + "=" * 60)
    print("Test 4: Error Handler")
    print("=" * 60)

    try:
        from src.error_handler import ErrorHandler
        from src.models import RetryConfig, Step, StepResult

        # Create error handler
        retry_config = RetryConfig(max_retries=3, retry_delay=1.0)
        handler = ErrorHandler(retry_config)
        print(f"✓ ErrorHandler created")

        # Test retry decision
        error = Exception("Test error")
        should_retry = handler.should_retry(error, 0)
        print(f"✓ Retry decision: {should_retry}")

        # Test retry decision with max retries exceeded
        should_retry = handler.should_retry(error, 10)
        print(f"✓ Retry decision (max exceeded): {should_retry}")

        # Test with specific retryable error
        timeout_error = TimeoutError("Test timeout")
        should_retry = handler.should_retry(timeout_error, 0)
        print(f"✓ Retry decision (timeout): {should_retry}")

        return True

    except Exception as e:
        print(f"✗ Error handler test failed: {e}")
        traceback.print_exc()
        return False


async def test_agent_creation():
    """Test agent creation and configuration"""
    print("\n" + "=" * 60)
    print("Test 5: Agent Creation")
    print("=" * 60)

    try:
        # Configure LLM
        llm_config = LLMConfig(
            base_url='https://api.siliconflow.cn/v1/',
            api_key='test-key',
            model_name='deepseek-ai/DeepSeek-R1',
            max_tokens=4096,
            temperature=0.7
        )

        # Create agent configuration
        config = AgentConfig(llm_config=llm_config)

        # Initialize agent
        agent = PlanAndExecuteAgent(config)
        print(f"✓ Agent created successfully")

        # Check components
        print(f"✓ Plan generator: {agent.plan_generator is not None}")
        print(f"✓ Task executor: {agent.task_executor is not None}")
        print(f"✓ Result recorder: {agent.result_recorder is not None}")

        return True

    except Exception as e:
        print(f"✗ Agent creation failed: {e}")
        traceback.print_exc()
        return False


async def test_tool_registration():
    """Test tool registration"""
    print("\n" + "=" * 60)
    print("Test 6: Tool Registration")
    print("=" * 60)

    try:
        # Configure LLM
        llm_config = LLMConfig(
            base_url='https://api.siliconflow.cn/v1/',
            api_key='test-key',
            model_name='deepseek-ai/DeepSeek-R1'
        )

        # Create agent
        config = AgentConfig(llm_config=llm_config)
        agent = PlanAndExecuteAgent(config)

        # Define test tools
        def simple_tool(input_text: str) -> str:
            return f"Processed: {input_text}"

        # Register tools
        agent.register_tool("simple_tool", simple_tool)
        print(f"✓ Tool 'simple_tool' registered")

        # Check if tool is in registry
        if "simple_tool" in agent.task_executor.tool_registry:
            print(f"✓ Tool found in registry")
        else:
            print(f"✗ Tool not found in registry")
            return False

        # Test tool call
        result = agent.task_executor.tool_registry["simple_tool"]("test input")
        print(f"✓ Tool executed: {result}")

        return True

    except Exception as e:
        print(f"✗ Tool registration failed: {e}")
        traceback.print_exc()
        return False


async def test_simple_execution():
    """Test a simple task execution"""
    print("\n" + "=" * 60)
    print("Test 7: Simple Task Execution (Requires API Key)")
    print("=" * 60)

    try:
        # Configure LLM with actual API key
        llm_config = LLMConfig(
            base_url='https://api.siliconflow.cn/v1/',
            api_key='sk-kagazldxzrbgubldmwhwxjyntqbfhxxswafrvjwxczyzvuxo',
            model_name='deepseek-ai/DeepSeek-R1',
            max_tokens=2048,
            temperature=0.7
        )

        # Create agent
        config = AgentConfig(llm_config=llm_config)
        agent = PlanAndExecuteAgent(config)

        # Simple task
        task = "分析一下人工智能的发展历程，总结出3个重要的里程碑事件"

        print(f"Task: {task}\n")

        # Execute task
        execution = await agent.execute_task(
            task=task,
            context={},
            save_plan=True,
            save_results=True
        )

        print(f"\n✓ Execution completed!")
        print(f"  Execution ID: {execution.execution_id}")
        print(f"  Status: {execution.status.value}")
        print(f"  Total Duration: {execution.total_duration:.2f}s")
        print(f"  Steps Completed: {len(execution.step_results)}")
        print(f"  Successful: {sum(1 for r in execution.step_results if r.success)}")
        print(f"  Failed: {sum(1 for r in execution.step_results if not r.success)}")

        return True

    except Exception as e:
        print(f"✗ Task execution failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PLAN AND EXECUTE AGENT - COMPREHENSIVE TEST")
    print("=" * 60 + "\n")

    results = []

    # Test 1: Imports
    results.append(("Module Imports", test_imports()))

    # Test 2: Models
    results.append(("Model Creation", test_models()))

    # Test 3: Result Recorder
    results.append(("Result Recorder", test_result_recorder()))

    # Test 4: Error Handler
    results.append(("Error Handler", test_error_handler()))

    # Test 5: Agent Creation (async)
    try:
        results.append(("Agent Creation", asyncio.run(test_agent_creation())))
    except Exception as e:
        print(f"✗ Agent creation test failed: {e}")
        results.append(("Agent Creation", False))

    # Test 6: Tool Registration (async)
    try:
        results.append(("Tool Registration", asyncio.run(test_tool_registration())))
    except Exception as e:
        print(f"✗ Tool registration test failed: {e}")
        results.append(("Tool Registration", False))

    # Test 7: Simple Execution (async, requires API)
    print("\n" + "=" * 60)
    print("Running full execution test...")
    print("=" * 60)
    try:
        results.append(("Simple Task Execution", asyncio.run(test_simple_execution())))
    except Exception as e:
        print(f"✗ Simple execution test failed: {e}")
        results.append(("Simple Task Execution", False))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {total - passed} TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())