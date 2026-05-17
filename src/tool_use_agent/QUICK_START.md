# Quick Start Guide - Tool Use Agent

## Installation

```bash
cd D:\PythonProject\CC_Agent\src\tool_use_agent
pip install -r requirements.txt
```

## Running the Agent

### Interactive Mode
```bash
python main.py
```

### Run Tests
```bash
python test_structure.py
```

## Basic Usage

### 1. Simple Example

```python
import asyncio
from src.agent.tool_use_agent import ToolUseAgent
from src.tools.examples.calculator import CalculatorTool

async def demo():
    # Initialize agent
    agent = ToolUseAgent()

    # Register a tool
    agent.register_tool(CalculatorTool())

    # Ask a question
    response = await agent.process_message("What's 25 + 17?")
    print(response.content)

asyncio.run(demo())
```

### 2. Multi-turn Conversation

```python
import asyncio
from src.agent.tool_use_agent import ToolUseAgent
from src.tools.examples.calculator import CalculatorTool

async def demo():
    agent = ToolUseAgent()
    agent.register_tool(CalculatorTool())

    session_id = "my_session"

    # First question
    response1 = await agent.process_message("What's 10 + 20?", session_id)
    print(response1.content)

    # Follow-up (agent remembers context)
    response2 = await agent.process_message("Now multiply by 3", session_id)
    print(response2.content)

asyncio.run(demo())
```

### 3. Multiple Tools

```python
import asyncio
from src.agent.tool_use_agent import ToolUseAgent
from src.tools.examples.calculator import CalculatorTool
from src.tools.examples.weather import WeatherTool
from src.tools.examples.search import SearchTool

async def demo():
    agent = ToolUseAgent()

    # Register all tools
    agent.register_tool(CalculatorTool())
    agent.register_tool(WeatherTool())
    agent.register_tool(SearchTool())

    # Agent will decide which tool to use
    response1 = await agent.process_message("Calculate 100 * 5")
    print(response1.content)

    response2 = await agent.process_message("What's the weather in Tokyo?")
    print(response2.content)

    response3 = await agent.process_message("Search for Python tutorials")
    print(response3.content)

asyncio.run(demo())
```

## Creating Custom Tools

### Method 1: Extend BaseTool

```python
from src.tools.base import BaseTool, ToolResult, ToolParameter

class GreetingTool(BaseTool):
    def __init__(self):
        super().__init__()
        self._parameters = {
            "name": ToolParameter(
                name="name",
                type="string",
                description="Name to greet",
                required=True
            )
        }

    @property
    def name(self) -> str:
        return "greeting"

    @property
    def description(self) -> str:
        return "Say hello to someone"

    async def execute(self, name: str) -> ToolResult:
        return ToolResult(
            success=True,
            data={"greeting": f"Hello, {name}!"}
        )

# Use the tool
agent.register_tool(GreetingTool())
```

### Method 2: Use Decorator

```python
from src.tools.function_tool import tool

@tool(
    name="hello",
    description="Say hello",
    parameters={
        "name": {
            "type": "string",
            "description": "Name to greet",
            "required": True
        }
    }
)
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

# Register the tool
agent.register_tool(say_hello)
```

## Configuration

### Using Default Config

```python
from src.agent.tool_use_agent import ToolUseAgent

agent = ToolUseAgent()  # Uses default config
```

### Using Custom Config

```python
from src.agent.tool_use_agent import ToolUseAgent
from src.agent.base import AgentConfig

config = AgentConfig(
    model_name="deepseek-ai/DeepSeek-R1",
    temperature=0.7,
    max_tokens=2000,
    max_tool_calls=5,
    enable_fallback=True
)

agent = ToolUseAgent(config=config)
```

### Using Config File

```python
from src.agent.config import ConfigManager
from src.agent.tool_use_agent import ToolUseAgent

config_manager = ConfigManager()
config = config_manager.load_config("default")  # Loads from configs/default.yaml

agent = ToolUseAgent(config=config)
```

## Session Management

```python
# Create a session
response1 = await agent.process_message("Hello", session_id="session_1")

# Continue the session
response2 = await agent.process_message("How are you?", session_id="session_1")

# Get session context
context = agent.get_session_context("session_1")
print(f"Messages: {len(context.messages)}")

# Clear session
agent.clear_session("session_1")
```

## Error Handling

The agent automatically handles errors with fallback mechanisms:

```python
# If a tool fails, the agent will:
# 1. Retry the operation
# 2. Try alternative tools
# 3. Provide a graceful fallback response
# 4. Return user-friendly error messages

response = await agent.process_message("Use a tool that doesn't exist")
print(response.content)  # Friendly error message
```

## Testing Tools Individually

```python
import asyncio
from src.tools.examples.calculator import CalculatorTool

async def test_tool():
    tool = CalculatorTool()
    result = await tool(operation="add", a=10, b=20)

    if result.success:
        print(f"Result: {result.data}")
    else:
        print(f"Error: {result.error}")

asyncio.run(test_tool())
```

## Environment Variables

```bash
# Set API credentials (optional)
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.siliconflow.cn/v1/"
```

## Common Issues

### Import Errors
```bash
# Make sure you're in the correct directory
cd D:\PythonProject\CC_Agent\src\tool_use_agent

# Install dependencies
pip install -r requirements.txt
```

### API Connection Issues
```python
# Check your API credentials
# The default config uses a demo API key
# Set your own key in environment or config file
```

### Tool Not Working
```python
# Check if tool is registered
if "my_tool" in agent.tool_registry:
    print("Tool is registered")
else:
    print("Tool not found")

# List all tools
print(agent.list_tools())
```

## Getting Help

- Read the full documentation in README.md
- Check the example code in main.py
- Review the implementation status in IMPLEMENTATION_STATUS.md
- Run test_structure.py to verify your setup

## Tips

1. **Start Simple**: Begin with the calculator tool to understand the basics
2. **Use Interactive Mode**: Run `python main.py` to test interactively
3. **Check Logs**: The agent prints tool usage information
4. **Clear Sessions**: Use `clear` command in interactive mode to restart
5. **Customize Config**: Adjust parameters in configs/default.yaml

## Example Commands to Try

In interactive mode:
```
What's 15 + 27?
What's the weather in Beijing?
Search for Python programming
Calculate 100 * 5.5
What's 100 - 30?
```