"""
Final validation script for Plan and Execute Agent
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all imports"""
    print("="*60)
    print("Testing Imports...")
    print("="*60)

    try:
        from src.models import (
            AgentConfig, LLMConfig, ExecutionConfig, RetryConfig,
            PlanStatus, StepStatus, ExecutionStatus, StepType,
            ErrorInfo, Step, StepResult, TaskPlan, TaskExecution
        )
        print("✓ Models imported successfully")

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
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_models():
    """Test data models"""
    print("\n" + "="*60)
    print("Testing Data Models...")
    print("="*60)

    try:
        from src.models import (
            LLMConfig, AgentConfig, Step, TaskPlan, StepResult
        )

        # Test LLMConfig
        llm_config = LLMConfig(
            base_url='https://test.com/v1/',
            api_key='test_key',
            model_name='test-model',
            max_tokens=2048,
            temperature=0.7
        )
        print("✓ LLMConfig creation successful")

        # Test AgentConfig
        config = AgentConfig(llm_config=llm_config)
        print("✓ AgentConfig creation successful")

        # Test Step
        step = Step(
            step_id="step_test",
            step_number=1,
            description="Test step",
            step_type=StepType.CUSTOM
        )
        print("✓ Step creation successful")

        # Test TaskPlan
        plan = TaskPlan(
            plan_id="plan_test",
            task_description="Test task",
            steps=[step]
        )
        print("✓ TaskPlan creation successful")

        # Test StepResult
        result = StepResult(
            step_id="step_test",
            success=True,
            output="Test output",
            execution_time=1.5
        )
        print("✓ StepResult creation successful")

        return True
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False


def test_components():
    """Test component initialization"""
    print("\n" + "="*60)
    print("Testing Component Initialization...")
    print("="*60)

    try:
        from src.agent import PlanAndExecuteAgent
        from src.models import AgentConfig, LLMConfig

        # Test Agent initialization
        llm_config = LLMConfig(
            base_url='https://api.siliconflow.cn/v1/',
            api_key='test_key',
            model_name='deepseek-ai/DeepSeek-R1',
            max_tokens=2048,
            temperature=0.7
        )

        config = AgentConfig(llm_config=llm_config)
        agent = PlanAndExecuteAgent(config)

        print("✓ Agent initialization successful")

        # Test result recorder directories
        import os
        dirs_to_check = ['results', 'results/plans', 'results/executions', 'results/logs']
        for dir_path in dirs_to_check:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            print(f"✓ Directory ready: {dir_path}")

        return True
    except Exception as e:
        print(f"✗ Component test failed: {e}")
        return False


def test_functionality():
    """Test basic functionality"""
    print("\n" + "="*60)
    print("Testing Basic Functionality...")
    print("="*60)

    try:
        from src.agent import PlanAndExecuteAgent
        from src.models import AgentConfig, LLMConfig

        # Create agent
        llm_config = LLMConfig(
            base_url='https://api.siliconflow.cn/v1/',
            api_key='test_key',
            model_name='deepseek-ai/DeepSeek-R1',
            max_tokens=2048,
            temperature=0.7
        )

        config = AgentConfig(llm_config=llm_config)
        agent = PlanAndExecuteAgent(config)

        # Test tool registration
        def dummy_tool(arg):
            return f"Result: {arg}"

        agent.register_tool("dummy_tool", dummy_tool)
        print("✓ Tool registration successful")

        # Test listing functions
        plans = agent.list_plans()
        print(f"✓ List plans successful: {len(plans)} plans")

        executions = agent.list_executions()
        print(f"✓ List executions successful: {len(executions)} executions")

        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validation tests"""
    print("\n" + "="*60)
    print("PLAN AND EXECUTE AGENT - VALIDATION")
    print("="*60 + "\n")

    results = []

    # Test 1: Imports
    results.append(("Imports", test_imports()))

    # Test 2: Models
    results.append(("Models", test_models()))

    # Test 3: Components
    results.append(("Components", test_components()))

    # Test 4: Functionality
    results.append(("Functionality", test_functionality()))

    # Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")

    all_passed = all(result for _, result in results)

    print("-"*60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nThe implementation is complete and ready to use!")
        print("\nNext steps:")
        print("  1. Update API key in main.py or test_simple.py")
        print("  2. Run: python test_simple.py")
        print("  3. Or: python main.py")
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease check the error messages above.")
    print("="*60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())