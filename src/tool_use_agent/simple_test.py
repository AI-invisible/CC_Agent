"""
Simple test to verify code structure without external dependencies
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from src.agent.base import AgentResponse, AgentConfig
        print("✓ AgentResponse and AgentConfig imported")

        from src.agent.config import ConfigManager
        print("✓ ConfigManager imported")

        from src.tools.base import BaseTool, ToolResult, ToolParameter
        print("✓ BaseTool, ToolResult, ToolParameter imported")

        from src.tools.registry import ToolRegistry
        print("✓ ToolRegistry imported")

        from src.context.session import SessionContext, Message, SessionManager
        print("✓ SessionContext, Message, SessionManager imported")

        from src.fallback.handler import FallbackHandler, FallbackChain
        print("✓ FallbackHandler, FallbackChain imported")

        from src.fallback.strategies import RetryHandler, AlternativeToolHandler
        print("✓ RetryHandler, AlternativeToolHandler imported")

        print("\n✓ All core imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_creation():
    """Test tool creation"""
    print("\nTesting tool creation...")
    try:
        from src.tools.base import ToolParameter

        param = ToolParameter(
            name="test_param",
            type="string",
            description="Test parameter"
        )
        print(f"✓ ToolParameter created: {param.name}")

        from src.tools.base import ToolResult

        result = ToolResult(success=True, data={"test": "data"})
        print(f"✓ ToolResult created: {result.success}")

        return True
    except Exception as e:
        print(f"✗ Tool creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_management():
    """Test session management"""
    print("\nTesting session management...")
    try:
        from src.context.session import SessionContext, Message, SessionManager

        manager = SessionManager()
        session = manager.create_session("test_session")
        print(f"✓ Session created: {session.session_id}")

        session.add_user_message("Hello")
        session.add_assistant_message("Hi there!")

        messages = session.get_recent_messages()
        print(f"✓ Session has {len(messages)} messages")

        context_str = session.summarize_context()
        print(f"✓ Context summary: {context_str[:50]}...")

        return True
    except Exception as e:
        print(f"✗ Session management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_chain():
    """Test fallback chain"""
    print("\nTesting fallback chain...")
    try:
        from src.fallback.handler import FallbackChain
        from src.fallback.strategies import FallbackResponseHandler

        chain = FallbackChain()
        chain.add_handler(FallbackResponseHandler())

        print(f"✓ Fallback chain created with {len(chain)} handlers")

        return True
    except Exception as e:
        print(f"✗ Fallback chain test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_config():
    """Test agent configuration"""
    print("\nTesting agent configuration...")
    try:
        from src.agent.base import AgentConfig

        config = AgentConfig(
            model_name="test-model",
            temperature=0.5,
            max_tokens=1000
        )
        print(f"✓ AgentConfig created: {config.model_name}")

        config_dict = config.to_dict()
        print(f"✓ Config converted to dict: {len(config_dict)} fields")

        return True
    except Exception as e:
        print(f"✗ Agent config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_registry():
    """Test tool registry"""
    print("\nTesting tool registry...")
    try:
        from src.tools.base import BaseTool, ToolResult, ToolParameter
        from src.tools.registry import ToolRegistry

        # Create a simple test tool
        class TestTool(BaseTool):
            def __init__(self):
                super().__init__()
                self._parameters = {
                    "input": ToolParameter(
                        name="input",
                        type="string",
                        description="Input parameter",
                        required=True
                    )
                }

            @property
            def name(self) -> str:
                return "test_tool"

            @property
            def description(self) -> str:
                return "Test tool"

            async def execute(self, input: str) -> ToolResult:
                return ToolResult(success=True, data={"result": input})

        registry = ToolRegistry()
        tool = TestTool()
        registry.register(tool)

        print(f"✓ Registered {len(registry)} tools")

        retrieved_tool = registry.get("test_tool")
        if retrieved_tool:
            print(f"✓ Retrieved tool: {retrieved_tool.name}")
        else:
            print("✗ Failed to retrieve tool")
            return False

        return True
    except Exception as e:
        print(f"✗ Tool registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    required_files = [
        "src/agent/base.py",
        "src/agent/config.py",
        "src/agent/tool_use_agent.py",
        "src/tools/base.py",
        "src/tools/registry.py",
        "src/tools/function_tool.py",
        "src/tools/examples/calculator.py",
        "src/tools/examples/weather.py",
        "src/tools/examples/search.py",
        "src/context/session.py",
        "src/fallback/handler.py",
        "src/fallback/strategies.py",
        "main.py",
        "requirements.txt"
    ]

    missing_files = []
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")

    if missing_files:
        print(f"\n✗ Missing files: {missing_files}")
        return False

    print(f"\n✓ All {len(required_files)} required files exist")
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Tool Use Agent - Structure Tests")
    print("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Tool Creation", test_tool_creation),
        ("Agent Configuration", test_agent_config),
        ("Session Management", test_session_management),
        ("Fallback Chain", test_fallback_chain),
        ("Tool Registry", test_tool_registry)
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{name:.<40} {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())