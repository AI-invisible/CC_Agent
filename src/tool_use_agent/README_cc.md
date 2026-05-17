# Tool Use Agent

A LangGraph-based intelligent agent with tool calling capabilities, multi-turn conversation support, and robust fallback handling.

## Features

- **Intelligent Tool Calling**: The agent automatically decides when to use tools based on user input
- **Multi-turn Context**: Maintains conversation state across multiple interactions
- **Fallback Handling**: Gracefully handles tool failures with multiple fallback strategies
- **Extensible Architecture**: Easy to add custom tools and handlers
- **LangGraph Integration**: Built on LangGraph for state management and workflow orchestration

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables (optional):
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.siliconflow.cn/v1/"
```

## Quick Start

### Interactive Mode

Run the agent in interactive mode:
```bash
python main.py
```

### Automated Tests

Run automated tests:
```bash
python main.py test
```

## Usage Example

```python
import asyncio
from src.agent.tool_use_agent import ToolUseAgent
from src.tools.examples.calculator import CalculatorTool
from src.tools.examples.weather import WeatherTool

async def main():
    # Initialize agent
    agent = ToolUseAgent()

    # Register tools
    agent.register_tool(CalculatorTool())
    agent.register_tool(WeatherTool())

    # Process messages
    response1 = await agent.process_message("What's 25 + 17?", session_id="demo")
    print(response1.content)

    response2 = await agent.process_message("What's the weather in Beijing?", session_id="demo")
    print(response2.content)

asyncio.run(main())
```

## Architecture

```
tool_use_agent/
├── src/
│   ├── agent/           # Core agent implementation
│   │   ├── base.py      # Base classes and configuration
│   │   ├── config.py    # Configuration management
│   │   └── tool_use_agent.py  # Main agent class
│   ├── tools/           # Tool framework
│   │   ├── base.py      # Base tool classes
│   │   ├── registry.py  # Tool registry
│   │   ├── function_tool.py  # Function tool wrapper
│   │   └── examples/    # Example tools
│   ├── context/         # Context management
│   │   └── session.py   # Session and message handling
│   └── fallback/        # Fallback handling
│       ├── handler.py   # Base handlers
│       └── strategies.py  # Fallback strategies
├── configs/             # Configuration files
├── main.py             # Entry point
└── requirements.txt    # Dependencies
```

## Creating Custom Tools

### Option 1: Extend BaseTool

```python
from src.tools.base import BaseTool, ToolResult, ToolParameter

class MyTool(BaseTool):
    def __init__(self):
        super().__init__()
        self._parameters = {
            "param1": ToolParameter(
                name="param1",
                type="string",
                description="Parameter description",
                required=True
            )
        }

    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "My custom tool"

    async def execute(self, param1: str) -> ToolResult:
        # Your tool logic here
        return ToolResult(success=True, data={"result": "..."})

# Register the tool
agent.register_tool(MyTool())
```

### Option 2: Use Function Decorator

```python
from src.tools.function_tool import tool

@tool(
    name="my_function_tool",
    description="A function-based tool",
    parameters={
        "input": {
            "type": "string",
            "description": "Input parameter",
            "required": True
        }
    }
)
def my_function(input: str) -> str:
    return f"Processed: {input}"

# Register the tool
agent.register_tool(my_function)
```

## Fallback Handling

The agent includes multiple fallback strategies:

1. **Retry Handler**: Automatically retries failed operations
2. **Alternative Tool Handler**: Tries alternative tools when primary tool fails
3. **Graceful Degradation Handler**: Provides partial functionality
4. **Fallback Response Handler**: Returns friendly error messages

Custom fallback handlers can be added:

```python
from src.fallback.handler import FallbackHandler

class CustomFallbackHandler(FallbackHandler):
    def can_handle(self, error: Exception) -> bool:
        # Determine if this handler can handle the error
        return True

    async def handle(self, error: Exception, context: dict) -> str:
        # Handle the error
        return "Custom fallback response"

# Add to agent's fallback chain
agent.fallback_chain.add_handler(CustomFallbackHandler())
```

## Configuration

Configuration can be provided via:

1. **YAML/JSON files** in the `configs/` directory
2. **Environment variables** (e.g., `OPENAI_API_KEY`)
3. **Programmatic configuration** (AgentConfig object)

Example config file (`configs/default.yaml`):

```yaml
model_name: "deepseek-ai/DeepSeek-R1"
temperature: 0.7
max_tokens: 2000
max_tool_calls: 5
enable_fallback: true
```

## Session Management

The agent supports multi-session conversation management:

```python
# Create new session
response = await agent.process_message("Hello", session_id="session_1")

# Continue same session
response = await agent.process_message("What's the weather?", session_id="session_1")

# Get session context
context = agent.get_session_context("session_1")
print(f"Messages: {len(context.messages)}")

# Clear session
agent.clear_session("session_1")
```

## Requirements

- Python 3.9+
- langgraph >= 0.0.20
- langchain-core >= 1.0.0
- openai >= 1.0.0
- pydantic >= 2.0.0

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.