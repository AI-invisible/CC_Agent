"""
Test script to verify the basic structure
"""
import sys
import os
from src.agent.base import AgentResponse, AgentConfig
from src.agent.config import ConfigManager
from src.tools.base import BaseTool, ToolResult, ToolParameter
from src.tools.registry import ToolRegistry
from src.context.session import SessionContext, Message, SessionManager
from src.fallback.handler import FallbackHandler, FallbackChain
from src.fallback.strategies import RetryHandler, AlternativeToolHandler
from src.tools.examples.calculator import CalculatorTool
from src.tools.examples.weather import WeatherTool
from src.tools.examples.search import SearchTool

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from src.agent.base import AgentResponse, AgentConfig
        from src.agent.config import ConfigManager
        from src.tools.base import BaseTool, ToolResult, ToolParameter
        from src.tools.registry import ToolRegistry
        from src.context.session import SessionContext, Message, SessionManager
        from src.fallback.handler import FallbackHandler, FallbackChain
        from src.fallback.strategies import RetryHandler, AlternativeToolHandler
        from src.tools.examples.calculator import CalculatorTool
        from src.tools.examples.weather import WeatherTool
        from src.tools.examples.search import SearchTool
        print("✓ All imports successful")
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
        calculator = CalculatorTool()
        weather = WeatherTool()
        search = SearchTool()

        print(f"✓ Calculator tool created: {calculator.name}")
        print(f"✓ Weather tool created: {weather.name}")
        print(f"✓ Search tool created: {search.name}")
        return True
    except Exception as e:
        print(f"✗ Tool creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_registry():
    """Test tool registry"""
    print("\nTesting tool registry...")
    try:
        registry = ToolRegistry()
        registry.register(CalculatorTool())
        registry.register(WeatherTool())
        registry.register(SearchTool())

        print(f"✓ Registered {len(registry)} tools")
        print(f"✓ Tool list: {registry.list_tools()}")

        # Test tool retrieval
        calc_tool = registry.get("calculator")
        if calc_tool:
            print(f"✓ Retrieved calculator tool: {calc_tool.name}")
        else:
            print("✗ Failed to retrieve calculator tool")
            return False

        return True
    except Exception as e:
        print(f"✗ Tool registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_management():
    """Test session management"""
    print("\nTesting session management...")
    try:
        manager = SessionManager()
        session = manager.create_session("test_session")

        session.add_user_message("Hello")
        session.add_assistant_message("Hi there!")

        messages = session.get_recent_messages()
        print(f"✓ Created session with {len(messages)} messages")

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
        chain = FallbackChain()
        chain.add_handler(RetryHandler())
        chain.add_handler(AlternativeToolHandler())

        print(f"✓ Fallback chain created with {len(chain)} handlers")

        return True
    except Exception as e:
        print(f"✗ Fallback chain test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Tool Use Agent - Structure Tests")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Tool Creation", test_tool_creation),
        ("Tool Registry", test_tool_registry),
        ("Session Management", test_session_management),
        ("Fallback Chain", test_fallback_chain)
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