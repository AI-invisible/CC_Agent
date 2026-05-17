"""
Comprehensive functionality tests for Tool Use Agent
Tests tool calling, context management, and fallback handling
"""
import sys
import os
import asyncio

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_async_tools():
    """Test async tool execution"""
    print("\nTesting async tool execution...")
    try:
        from src.tools.base import BaseTool, ToolResult, ToolParameter

        class AsyncTestTool(BaseTool):
            def __init__(self):
                super().__init__()
                self._parameters = {
                    "delay": ToolParameter(
                        name="delay",
                        type="float",
                        description="Delay in seconds",
                        required=False,
                        default=0.1
                    )
                }

            @property
            def name(self) -> str:
                return "async_test_tool"

            @property
            def description(self) -> str:
                return "Async test tool"

            async def execute(self, delay: float = 0.1) -> ToolResult:
                await asyncio.sleep(delay)
                return ToolResult(
                    success=True,
                    data={"delayed_for": delay},
                    tool_name=self.name
                )

        async def run_test():
            tool = AsyncTestTool()
            result = await tool(delay=0.01)
            print(f"✓ Async tool executed: {result.success}")
            print(f"✓ Tool returned: {result.data}")
            return result.success

        success = asyncio.run(run_test())
        return success
    except Exception as e:
        print(f"✗ Async tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_parameter_validation():
    """Test tool parameter validation"""
    print("\nTesting tool parameter validation...")
    try:
        from src.tools.base import BaseTool, ToolResult, ToolParameter

        class ValidatedTool(BaseTool):
            def __init__(self):
                super().__init__()
                self._parameters = {
                    "required_param": ToolParameter(
                        name="required_param",
                        type="string",
                        description="Required parameter",
                        required=True
                    ),
                    "number_param": ToolParameter(
                        name="number_param",
                        type="integer",
                        description="Number parameter",
                        required=True,
                        constraints={"min": 0, "max": 100}
                    )
                }

            @property
            def name(self) -> str:
                return "validated_tool"

            @property
            def description(self) -> str:
                return "Tool with parameter validation"

            async def execute(self, required_param: str, number_param: int) -> ToolResult:
                return ToolResult(
                    success=True,
                    data={"required_param": required_param, "number_param": number_param}
                )

        async def run_test():
            tool = ValidatedTool()

            # Test valid parameters
            result1 = await tool(required_param="test", number_param=50)
            if not result1.success:
                print(f"✗ Valid parameters failed: {result1.error}")
                return False
            print(f"✓ Valid parameters accepted")

            # Test missing required parameter
            result2 = await tool(number_param=50)
            if result2.success:
                print(f"✗ Missing required parameter not caught")
                return False
            print(f"✓ Missing required parameter caught: {result2.error}")

            # Test invalid range
            result3 = await tool(required_param="test", number_param=150)
            if result3.success:
                print(f"✗ Invalid range not caught")
                return False
            print(f"✓ Invalid range caught: {result3.error}")

            return True

        success = asyncio.run(run_test())
        return success
    except Exception as e:
        print(f"✗ Parameter validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_messages():
    """Test context message management"""
    print("\nTesting context message management...")
    try:
        from src.context.session import SessionContext, SessionManager

        manager = SessionManager()
        session = manager.create_session("test_messages")

        # Add messages
        session.add_user_message("Hello")
        session.add_assistant_message("Hi there!", tool_calls=[{"name": "test"}])
        session.add_user_message("How are you?")

        # Test message count
        messages = session.get_recent_messages()
        if len(messages) != 3:
            print(f"✗ Expected 3 messages, got {len(messages)}")
            return False
        print(f"✓ Message count correct: {len(messages)}")

        # Test message types
        user_msgs = [m for m in messages if m.role == "user"]
        assistant_msgs = [m for m in messages if m.role == "assistant"]
        if len(user_msgs) != 2 or len(assistant_msgs) != 1:
            print(f"✗ Message types incorrect")
            return False
        print(f"✓ Message types correct: {len(user_msgs)} user, {len(assistant_msgs)} assistant")

        # Test message content
        if messages[0].content != "Hello":
            print(f"✗ First message content incorrect")
            return False
        print(f"✓ Message content correct")

        # Test tool calls
        if not assistant_msgs[0].tool_calls:
            print(f"✗ Tool calls not stored")
            return False
        print(f"✓ Tool calls stored correctly")

        return True
    except Exception as e:
        print(f"✗ Context message test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_handler_execution():
    """Test fallback handler execution"""
    print("\nTesting fallback handler execution...")
    try:
        from src.fallback.handler import FallbackHandler, FallbackChain
        from src.fallback.strategies import FallbackResponseHandler
        import asyncio

        class TestFallbackHandler(FallbackHandler):
            def can_handle(self, error: Exception) -> bool:
                return "test" in str(error).lower()

            async def handle(self, error: Exception, context: dict) -> str:
                return f"Handled test error: {str(error)}"

            def get_priority(self) -> int:
                return 50

        async def run_test():
            chain = FallbackChain()
            chain.add_handler(TestFallbackHandler())
            chain.add_handler(FallbackResponseHandler())

            # Test custom handler
            error = Exception("Test error occurred")
            result = await chain.handle_error(error, {})
            if "Test error" not in result:
                print(f"✗ Custom handler not used")
                return False
            print(f"✓ Custom handler executed: {result[:50]}...")

            # Test fallback handler
            error2 = Exception("Generic error")
            result2 = await chain.handle_error(error2, {})
            if "apologize" not in result2.lower():
                print(f"✗ Fallback handler not used")
                return False
            print(f"✓ Fallback handler executed")

            return True

        success = asyncio.run(run_test())
        return success
    except Exception as e:
        print(f"✗ Fallback handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tool_registry_operations():
    """Test tool registry operations"""
    print("\nTesting tool registry operations...")
    try:
        from src.tools.base import BaseTool, ToolResult, ToolParameter
        from src.tools.registry import ToolRegistry

        # Create test tools
        class Tool1(BaseTool):
            def __init__(self):
                super().__init__()
                self._parameters = {}
            @property
            def name(self) -> str:
                return "tool1"
            @property
            def description(self) -> str:
                return "Tool 1"
            async def execute(self) -> ToolResult:
                return ToolResult(success=True, data={"tool": "1"})

        class Tool2(BaseTool):
            def __init__(self):
                super().__init__()
                self._parameters = {}
            @property
            def name(self) -> str:
                return "tool2"
            @property
            def description(self) -> str:
                return "Tool 2"
            async def execute(self) -> ToolResult:
                return ToolResult(success=True, data={"tool": "2"})

        async def run_test():
            registry = ToolRegistry()

            # Test registration
            registry.register(Tool1())
            registry.register(Tool2(), alias="t2")

            if len(registry) != 2:
                print(f"✗ Registration failed")
                return False
            print(f"✓ Tools registered: {len(registry)}")

            # Test retrieval by name
            tool1 = registry.get("tool1")
            if not tool1 or tool1.name != "tool1":
                print(f"✗ Retrieval by name failed")
                return False
            print(f"✓ Tool retrieved by name: {tool1.name}")

            # Test retrieval by alias
            tool2 = registry.get("t2")
            if not tool2 or tool2.name != "tool2":
                print(f"✗ Retrieval by alias failed")
                return False
            print(f"✓ Tool retrieved by alias: {tool2.name}")

            # Test listing
            tool_list = registry.list_tools()
            if "tool1" not in tool_list or "tool2" not in tool_list:
                print(f"✗ Listing failed")
                return False
            print(f"✓ Tools listed: {tool_list}")

            # Test search
            search_results = registry.search("tool")
            if len(search_results) != 2:
                print(f"✗ Search failed")
                return False
            print(f"✓ Search results: {len(search_results)}")

            # Test unregistration
            registry.unregister("tool1")
            if len(registry) != 1:
                print(f"✗ Unregistration failed")
                return False
            print(f"✓ Tool unregistered")

            return True

        success = asyncio.run(run_test())
        return success
    except Exception as e:
        print(f"✗ Tool registry operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration management"""
    print("\nTesting configuration management...")
    try:
        from src.agent.base import AgentConfig

        # Test default configuration
        config1 = AgentConfig()
        if config1.model_name != "deepseek-ai/DeepSeek-R1":
            print(f"✗ Default config incorrect")
            return False
        print(f"✓ Default config created: {config1.model_name}")

        # Test custom configuration
        config2 = AgentConfig(
            model_name="custom-model",
            temperature=0.5,
            max_tokens=500
        )
        if config2.temperature != 0.5:
            print(f"✗ Custom config incorrect")
            return False
        print(f"✓ Custom config created")

        # Test serialization
        config_dict = config2.to_dict()
        if config_dict["model_name"] != "custom-model":
            print(f"✗ Serialization failed")
            return False
        print(f"✓ Config serialized")

        # Test deserialization
        config3 = AgentConfig.from_dict(config_dict)
        if config3.model_name != "custom-model":
            print(f"✗ Deserialization failed")
            return False
        print(f"✓ Config deserialized")

        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_manager():
    """Test session manager"""
    print("\nTesting session manager...")
    try:
        from src.context.session import SessionManager

        manager = SessionManager()

        # Test session creation
        session1 = manager.create_session("session1")
        if session1.session_id != "session1":
            print(f"✗ Session creation failed")
            return False
        print(f"✓ Session created: {session1.session_id}")

        # Test session retrieval
        retrieved = manager.get_session("session1")
        if not retrieved or retrieved.session_id != "session1":
            print(f"✗ Session retrieval failed")
            return False
        print(f"✓ Session retrieved")

        # Test session listing
        sessions = manager.list_sessions()
        if "session1" not in sessions:
            print(f"✗ Session listing failed")
            return False
        print(f"✓ Sessions listed: {sessions}")

        # Test session deletion
        deleted = manager.delete_session("session1")
        if not deleted:
            print(f"✗ Session deletion failed")
            return False
        print(f"✓ Session deleted")

        # Test session count
        count = manager.get_session_count()
        if count != 0:
            print(f"✗ Session count incorrect")
            return False
        print(f"✓ Session count correct: {count}")

        return True
    except Exception as e:
        print(f"✗ Session manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all functionality tests"""
    print("=" * 60)
    print("Tool Use Agent - Functionality Tests")
    print("=" * 60)

    tests = [
        ("Async Tools", test_async_tools),
        ("Parameter Validation", test_tool_parameter_validation),
        ("Context Messages", test_context_messages),
        ("Fallback Handlers", test_fallback_handler_execution),
        ("Tool Registry Operations", test_tool_registry_operations),
        ("Configuration", test_configuration),
        ("Session Manager", test_session_manager)
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
        print("\n✓ All functionality tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())