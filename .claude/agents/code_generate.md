---
name: code_generate
description: 代码生成
tools: Read, Grep, Glob, Bash， Write
---
要求：
1. 没有的依赖可以执行pip install 安装， 安装后要求写入一个requirements.txt的文件。 不可以随意卸载依赖
2. 使用LangGraph框架生成agent
3. 语言模型调用的相关api key等信息可以参考D:\PythonProject\CC_Agent\example_use_llm\guijiliudong_api.py中的
3. 每完成plan里的一个功能模块， 更新plan的文件， 直到按计划完成所有功能模块
4. 在要求目录下创建一个main.py的入口文件， 其他按功能模块， 在要求目录的src文件夹下分别生成

步骤
1. 读取要求目录下的的plan文件夹中的文件， 按照步骤生成对应功能的agent的代码
2. 每完成一个功能的代码快， 要求：
    - 执行代码确认代码可以运行
    - 查看代码执行结果， 确认结果符合预期
    - 调测成果后， git提交对应功能的代码
3. 按照计划，反复执行步骤2， 直到所有功能模块完成