# -*- coding: utf-8 -*-
# @Author : jiaqi
# @Time : 2026/5/17
# @File : use_llm.py.py
# @description :
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utils.CONSTANTS import API_KEY

url = 'https://api.siliconflow.cn/v1/'
api_key = API_KEY

client = OpenAI(
    base_url=url,
    api_key=api_key
)

# 发送带有流式输出的请求
content = ""
reasoning_content=""
messages = [
    {"role": "user", "content": "奥运会的传奇名将有哪些？"}
]
response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1",
    messages=messages,
    stream=True,  # 启用流式输出
    max_tokens=4096
)

# 初始化标志变量以检测reasoning_content的第一个和最后一个输出
is_first_reasoning = True
is_content_start = True

# 逐步接收并处理响应
for chunk in response:
    if chunk.choices[0].delta.content:
        if not is_first_reasoning and is_content_start:
            print("</think>")
            is_content_start = False
        content += chunk.choices[0].delta.content
        print(chunk.choices[0].delta.content, end='')  # 防止输出换行

    if chunk.choices[0].delta.reasoning_content:
        if is_first_reasoning:  # 如果是第一个reasoning的输出
            print("</think>", end='')  # 在第一个reasoning_content输出之前添加</think>
            is_first_reasoning = False
        reasoning_content += chunk.choices[0].delta.reasoning_content
        print(chunk.choices[0].delta.reasoning_content, end='')  # 防止输出换行
