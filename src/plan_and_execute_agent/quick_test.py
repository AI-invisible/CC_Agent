"""
Quick test to verify the code structure
"""
import sys
from pathlib import Path

# Test imports
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from src.models import AgentConfig, LLMConfig
    from src.agent import PlanAndExecuteAgent
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test basic instantiation
try:
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
except Exception as e:
    print(f"✗ Agent initialization failed: {e}")
    sys.exit(1)

# Check directory structure
import os
dirs_to_check = ['src', 'results', 'results/plans', 'results/executions', 'results/logs']
for dir_path in dirs_to_check:
    full_path = Path(dir_path)
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")
    else:
        print(f"✓ Directory exists: {dir_path}")

print("\n" + "="*60)
print("All checks passed! The code structure is correct.")
print("="*60)
print("\nNext steps:")
print("1. Run: python test_simple.py")
print("2. Or: python main.py")