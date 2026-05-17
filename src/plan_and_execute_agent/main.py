"""
Main entry point for Plan and Execute Agent
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
from src.agent import PlanAndExecuteAgent
from src.models import AgentConfig, LLMConfig

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utils.CONSTANTS import API_KEY


# Sample tools for demonstration
def web_search(query: str) -> str:
    """Simulate web search tool"""
    return f"Search results for '{query}': Found 5 relevant articles"


def data_analysis(data: str) -> dict:
    """Simulate data analysis tool"""
    return {
        "summary": "Data analysis complete",
        "insights": ["Insight 1", "Insight 2"],
        "statistics": {"mean": 42, "std": 3.5}
    }


def generate_report(content: str) -> str:
    """Simulate report generation tool"""
    return f"Generated report: {content}"


async def main():
    """Main function"""
    # Configure LLM
    llm_config = LLMConfig(
        base_url='https://api.siliconflow.cn/v1/',
        api_key=API_KEY,
        model_name='deepseek-ai/DeepSeek-R1',
        max_tokens=4096,
        temperature=0.7
    )

    # Create agent configuration
    config = AgentConfig(llm_config=llm_config)

    # Initialize agent
    agent = PlanAndExecuteAgent(config)

    # Register tools
    agent.register_tool("web_search", web_search)
    agent.register_tool("data_analysis", data_analysis)
    agent.register_tool("generate_report", generate_report)

    # Example task
    task = """分析2024年奥运会田径项目的比赛数据，并生成一份分析报告。

具体要求：
1. 收集2024年奥运会田径项目的比赛数据
2. 分析各项比赛的成绩趋势和纪录
3. 识别表现突出的运动员
4. 生成一份包含数据可视化的分析报告"""

    # Execute task
    execution = await agent.execute_task(
        task=task,
        context={
            "year": 2024,
            "sport": "athletics",
            "output_format": "report"
        },
        save_plan=True,
        save_results=True
    )

    # Generate detailed report
    print("\nGenerating detailed report...")
    report = agent.generate_report(execution.execution_id)

    print("\nDetailed Report:")
    print("-" * 60)
    for key, value in report.items():
        if isinstance(value, list):
            print(f"\n{key}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{key}: {value}")

    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())