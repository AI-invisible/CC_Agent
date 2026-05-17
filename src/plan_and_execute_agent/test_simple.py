"""
Simple test for Plan and Execute Agent
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import PlanAndExecuteAgent
from src.models import AgentConfig, LLMConfig


async def test_simple_task():
    """Test with a simple task"""
    # Configure LLM
    llm_config = LLMConfig(
        base_url='https://api.siliconflow.cn/v1/',
        api_key='sk-kagazldxzrbgubldmwhwxjyntqbfhxxswafrvjwxczyzvuxo',
        model_name='deepseek-ai/DeepSeek-R1',
        max_tokens=2048,
        temperature=0.7
    )

    # Create agent configuration
    config = AgentConfig(llm_config=llm_config)

    # Initialize agent
    agent = PlanAndExecuteAgent(config)

    # Simple task
    task = "帮我研究一下奥运会的历史，找出3个重要的历史时刻并总结"

    print("Starting test...")
    print(f"Task: {task}\n")

    # Execute task
    execution = await agent.execute_task(
        task=task,
        context={},
        save_plan=True,
        save_results=True
    )

    print(f"\nTest completed!")
    print(f"Execution ID: {execution.execution_id}")
    print(f"Status: {execution.status.value}")

    return execution


if __name__ == "__main__":
    asyncio.run(test_simple_task())