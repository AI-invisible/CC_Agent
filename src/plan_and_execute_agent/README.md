# Plan and Execute Agent

一个基于LangChain框架实现的Plan-and-Execute（规划-执行）Agent，能够将复杂任务拆解为可执行的步骤，并按顺序执行每个步骤，同时提供完整的执行记录和错误处理机制。

## 功能特性

### 核心功能
1. **任务计划生成** - 使用LLM将复杂任务拆解为具体的执行步骤
2. **任务分解** - 将复杂任务分解为原子性的执行步骤，确定依赖关系
3. **执行监控** - 实时监控执行状态和进度
4. **结果记录** - 记录每个步骤的执行结果并汇总
5. **错误处理** - 支持失败重试和步骤跳过

### 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                   Plan-And-Execute Agent                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Plan Generator│  │Task Executor │  │Result Recorder│   │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Error Handler │  │Tool Manager  │  │Config Manager│   │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ↓                     ↓                     ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    LLM API   │    │  Tool APIs   │    │  Storage     │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 项目结构

```
plan_and_execute_agent/
├── src/
│   ├── __init__.py           # 包初始化
│   ├── models.py             # 数据模型定义
│   ├── plan_generator.py     # 计划生成模块
│   ├── task_executor.py      # 任务执行模块
│   ├── error_handler.py      # 错误处理模块
│   ├── result_recorder.py    # 结果记录模块
│   └── agent.py              # Agent主类
├── main.py                   # 主入口文件（示例）
├── test_simple.py            # 简单测试文件
├── requirements.txt          # 依赖列表
├── install.bat              # Windows安装脚本
├── plan/
│   └── plan.md              # 需求文档
└── results/                 # 运行时生成的结果目录
    ├── plans/               # 保存的计划
    ├── executions/          # 执行记录
    └── logs/                # 日志文件
```

## 安装

### 方法1: 使用安装脚本（Windows）
```bash
install.bat
```

### 方法2: 手动安装
```bash
cd D:\PythonProject\CC_Agent\src\plan_and_execute_agent
pip install -r requirements.txt
```

## 快速开始

### 基本使用

```python
import asyncio
from src.agent import PlanAndExecuteAgent
from src.models import AgentConfig, LLMConfig

async def main():
    # 配置LLM
    llm_config = LLMConfig(
        base_url='https://api.siliconflow.cn/v1/',
        api_key='your_api_key',
        model_name='deepseek-ai/DeepSeek-R1',
        max_tokens=4096,
        temperature=0.7
    )

    # 创建Agent
    config = AgentConfig(llm_config=llm_config)
    agent = PlanAndExecuteAgent(config)

    # 执行任务
    execution = await agent.execute_task(
        task="帮我研究一下奥运会的历史，找出3个重要的历史时刻并总结",
        context={},
        save_plan=True,
        save_results=True
    )

    # 查看结果
    print(f"执行状态: {execution.status.value}")
    print(f"总耗时: {execution.total_duration:.2f}秒")

if __name__ == "__main__":
    asyncio.run(main())
```

### 运行示例

1. **简单测试**
```bash
python test_simple.py
```

2. **完整示例**
```bash
python main.py
```

## 主要模块说明

### 1. PlanGenerator（计划生成器）
- 负责将复杂任务拆解为可执行的步骤
- 使用LLM进行任务理解和步骤分解
- 验证计划的完整性和合理性
- 检测和避免循环依赖

### 2. TaskExecutor（任务执行器）
- 按照生成的计划执行各个步骤
- 支持步骤的串行执行（并行执行可配置）
- 实时监控执行状态和进度
- 提供执行超时控制

### 3. ErrorHandler（错误处理器）
- 处理执行过程中的各种错误和异常
- 支持自动重试失败的步骤
- 可配置重试次数和重试策略
- 支持指数退避等高级重试算法
- 允许用户选择跳过失败或阻塞的步骤

### 4. ResultRecorder（结果记录器）
- 记录每个步骤的执行结果
- 汇总整体任务执行情况
- 提供详细的执行日志和审计追踪
- 支持执行历史查询和报告生成

## 配置说明

### LLM配置
```python
llm_config = LLMConfig(
    base_url='https://api.siliconflow.cn/v1/',  # API地址
    api_key='your_api_key',                      # API密钥
    model_name='deepseek-ai/DeepSeek-R1',        # 模型名称
    max_tokens=4096,                             # 最大token数
    temperature=0.7                              # 温度参数
)
```

### 执行配置
```python
execution_config = ExecutionConfig(
    max_concurrent_steps=1,      # 最大并发步骤数
    timeout_per_step=300,        # 每步超时时间(秒)
    total_timeout=3600,          # 总超时时间(秒)
    enable_parallel=False,       # 是否启用并行执行
    checkpoint_interval=60       # 检查点间隔(秒)
)
```

### 重试配置
```python
retry_config = RetryConfig(
    max_retries=3,               # 最大重试次数
    retry_delay=1.0,             # 重试延迟(秒)
    exponential_backoff=True,    # 是否启用指数退避
    retryable_errors=[]          # 可重试的错误类型
)
```

## 工具注册

Agent支持注册自定义工具，工具可以在步骤执行时被调用：

```python
def web_search(query: str) -> str:
    """模拟网络搜索工具"""
    return f"Search results for '{query}'"

# 注册工具
agent.register_tool("web_search", web_search)
```

## 结果查询

### 查询执行状态
```python
status = agent.get_execution_status(execution_id)
```

### 获取执行结果
```python
execution = agent.get_execution_result(execution_id)
```

### 生成详细报告
```python
report = agent.generate_report(execution_id)
print(report)
```

### 列出所有计划
```python
plans = agent.list_plans()
for plan in plans:
    print(f"{plan['plan_id']}: {plan['task_description']}")
```

### 列出所有执行记录
```python
executions = agent.list_executions()
for exec in executions:
    print(f"{exec['execution_id']}: {exec['status']}")
```

## 输出示例

```
============================================================
Task: 帮我研究一下奥运会的历史，找出3个重要的历史时刻并总结
============================================================

Step 1: Generating execution plan...
Plan saved with ID: plan_xxxxxxxx

Generated plan with 3 steps:
  1. 研究奥运会的历史发展 [custom]
  2. 识别3个重要的历史时刻 [custom]
  3. 总结并归纳重要时刻的意义 [custom]

------------------------------------------------------------

Step 2: Executing plan...
执行步骤: 1/3 - 研究奥运会的历史发展
执行步骤: 2/3 - 识别3个重要的历史时刻
执行步骤: 3/3 - 总结并归纳重要时刻的意义

Execution saved with ID: exec_xxxxxxxx

------------------------------------------------------------

Step 3: Execution Results
------------------------------------------------------------
✓ Step 1: step_xxxxxx
  Status: Success
  Execution Time: 3.45s
  Output: 奥运会起源于古希腊...

✓ Step 2: step_xxxxxx
  Status: Success
  Execution Time: 2.87s
  Output: 1896年第一届现代奥运会...

✓ Step 3: step_xxxxxx
  Status: Success
  Execution Time: 3.12s
  Output: 总结：奥运会经历了...

------------------------------------------------------------
Execution Summary:
  Total Steps: 3
  Successful: 3
  Failed: 0
  Total Duration: 9.44s
  Final Status: completed
============================================================
```

## 错误处理

Agent提供完善的错误处理机制：

1. **自动重试** - 失败的步骤会自动重试（可配置次数）
2. **指数退避** - 重试间隔会逐渐增加
3. **步骤跳过** - 可以跳过失败的步骤继续执行
4. **错误记录** - 所有错误都会被详细记录
5. **继续执行** - 可以在步骤失败后继续执行后续步骤

## 数据存储

执行结果保存在 `results/` 目录下：

- `plans/` - 保存生成的计划
- `executions/` - 保存执行记录
- `logs/` - 保存详细日志

所有数据以JSON格式存储，便于查询和分析。

## 技术栈

- **编程语言**: Python 3.8+
- **LLM框架**: OpenAI API
- **数据模型**: Pydantic
- **异步处理**: asyncio
- **数据存储**: JSON

## 未来扩展

1. **并行执行** - 支持无依赖步骤的并行执行
2. **工具集成** - 集成更多常用工具（搜索、计算等）
3. **可视化** - 提供执行流程的可视化展示
4. **Web界面** - 提供Web管理界面
5. **多Agent协作** - 支持多个Agent协同工作

## 许可证

MIT License

## 作者

jiaqi

## 更新日志

### v0.1.0 (2024-05-17)
- 初始版本发布
- 实现核心功能：计划生成、任务执行、结果记录、错误处理
- 支持失败重试和步骤跳过
- 提供完整的执行记录和报告生成