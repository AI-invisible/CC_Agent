"""
Main entry point for Tool Use Agent
"""
import asyncio
from typing import Optional

from src.agent.tool_use_agent import ToolUseAgent
from src.agent.base import AgentConfig
from src.tools.base import BaseTool
from src.tools.examples.calculator import CalculatorTool
from src.tools.examples.weather import WeatherTool
from src.tools.examples.search import SearchTool


async def main():
    """Main function to run the agent"""
    print("=" * 60)
    print("Tool Use Agent - Interactive Demo")
    print("=" * 60)
    print("\nThis agent can:")
    print("- Decide when to use tools based on your input")
    print("- Maintain conversation context across multiple turns")
    print("- Handle tool failures with fallback mechanisms")
    print("\nAvailable tools: calculator, weather, search")
    print("-" * 60)
    print("Type 'quit' or 'exit' to stop the conversation")
    print("Type 'clear' to clear the current session")
    print("-" * 60)

    # Initialize agent with default configuration
    config = AgentConfig(
        model_name="deepseek-ai/DeepSeek-R1",
        temperature=0.7,
        max_tokens=2000,
        max_tool_calls=5,
        tool_timeout=30,
        retry_attempts=3,
        max_context_messages=20,
        enable_fallback=True
    )

    agent = ToolUseAgent(config=config)

    # Register example tools
    agent.register_tool(CalculatorTool())
    agent.register_tool(WeatherTool())
    agent.register_tool(SearchTool())

    print(f"\nAgent initialized with {len(agent.list_tools())} tools.")
    print(f"Tools: {', '.join(agent.list_tools())}")
    print("-" * 60)

    # Conversation loop
    session_id = "demo_session"
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ['quit', 'exit']:
                print("\nGoodbye!")
                break

            if user_input.lower() == 'clear':
                agent.clear_session(session_id)
                print("Session cleared. Starting fresh conversation.")
                continue

            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  quit/exit - Stop the conversation")
                print("  clear      - Clear the current session")
                print("  help       - Show this help message")
                print("\nTry asking:")
                print("  - 'What's 15 + 27?'")
                print("  - 'What's the weather in Beijing?'")
                print("  - 'Search for Python programming'")
                print("  - 'Calculate 100 * 5.5'")
                continue

            # Process user message
            print("\nAgent: ", end='', flush=True)

            response = await agent.process_message(
                message=user_input,
                session_id=session_id
            )

            print(response.content)

            # Show tool usage info if available
            if response.tool_calls:
                print(f"\n[Agent used {len(response.tool_calls)} tool(s)]")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or restart the agent.")


async def test_agent():
    """Run automated tests"""
    print("=" * 60)
    print("Tool Use Agent - Automated Tests")
    print("=" * 60)

    # Initialize agent
    agent = ToolUseAgent()

    # Register tools
    agent.register_tool(CalculatorTool())
    agent.register_tool(WeatherTool())
    agent.register_tool(SearchTool())

    # Test cases
    test_cases = [
        {
            "name": "Calculator Test",
            "message": "What is 25 + 17?",
            "expected_keywords": ["42", "result"]
        },
        {
            "name": "Weather Test",
            "message": "What's the weather in Shanghai?",
            "expected_keywords": ["Shanghai", "temperature", "weather"]
        },
        {
            "name": "Search Test",
            "message": "Search for artificial intelligence",
            "expected_keywords": ["artificial intelligence", "result"]
        },
        {
            "name": "Multi-turn Context Test",
            "messages": [
                "What's 10 + 20?",
                "Now multiply the result by 2"
            ],
            "expected_keywords": ["60", "multiply"]
        }
    ]

    passed = 0
    failed = 0

    for test_case in test_cases:
        print(f"\n{'-' * 60}")
        print(f"Test: {test_case['name']}")
        print(f"{'-' * 60}")

        try:
            if "messages" in test_case:
                # Multi-turn test
                session_id = f"test_{test_case['name'].replace(' ', '_')}"
                for i, msg in enumerate(test_case['messages']):
                    print(f"\nTurn {i+1}: {msg}")
                    response = await agent.process_message(msg, session_id)
                    print(f"Response: {response.content[:200]}...")

                response = await agent.process_message("", session_id)
                last_response = response.content
            else:
                # Single message test
                message = test_case['message']
                print(f"Input: {message}")
                response = await agent.process_message(message)
                last_response = response.content

            print(f"Full Response: {last_response[:500]}...")

            # Check if expected keywords are present
            test_passed = True
            for keyword in test_case['expected_keywords']:
                if keyword.lower() not in last_response.lower():
                    test_passed = False
                    print(f"Missing keyword: {keyword}")

            if test_passed:
                print("✓ PASSED")
                passed += 1
            else:
                print("✗ FAILED")
                failed += 1

        except Exception as e:
            print(f"✗ FAILED with error: {str(e)}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_agent())
    else:
        asyncio.run(main())