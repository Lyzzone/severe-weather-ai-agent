# 气象数据智能助手

这是一个从零开始学习 AI 应用开发的最小项目框架。它先用本地 CSV 数据和规则版 LLM 跑通完整流程，不依赖第三方库，也不需要 API Key。等你理解整体链路后，可以把 `weather_agent/llm.py` 中的规则版模型替换成真实大模型。

## 项目能做什么

你可以用自然语言提问：

```powershell
python -m weather_agent.cli "北京今天适合出门吗？"
python -m weather_agent.cli "上海天气总结"
python -m weather_agent.cli "广州现在天气怎么样？" --debug
```

助手会完成这条链路：

```text
用户问题 -> 识别城市和意图 -> 调用气象工具 -> 组织提示词 -> 生成中文回答
```

## 目录结构

```text
severe-weather-ai-agent/
├── data/
│   └── sample_weather.csv          # 示例气象数据
├── docs/
│   └── code_walkthrough.md         # 逐步代码解释
├── tests/
│   └── test_agent.py               # 最小单元测试
├── weather_agent/
│   ├── __init__.py
│   ├── agent.py                    # Agent 编排层
│   ├── cli.py                      # 命令行入口
│   ├── config.py                   # 配置读取
│   ├── data_loader.py              # CSV 数据读取和查询
│   ├── llm.py                      # 规则版 LLM 和提示词构造
│   ├── models.py                   # 数据结构
│   └── weather_tools.py            # 气象工具函数
└── requirements.txt
```

## 第 1 步：准备 Python 环境

本项目只使用 Python 标准库，建议 Python 3.10 或更新版本。

```powershell
python --version
python -m weather_agent.cli "北京今天适合出门吗？"
```

如果你以后接入真实大模型、数据库或 Web 服务，再把依赖写入 `requirements.txt`。

## 第 2 步：理解数据

示例数据在 `data/sample_weather.csv`：

```csv
city,datetime,temperature_c,humidity_pct,wind_speed_mps,precip_mm,pressure_hpa,condition,warning
北京,2026-07-07 14:00,35.6,55,5.8,0.0,1001,晴热,高温提醒
```

每一行是一条某城市某时刻的气象观测。真实项目里，这里可以换成：

- 气象站 CSV
- NetCDF / GRIB 文件
- 数据库
- 实时天气 API
- 你自己的模型预测结果

## 第 3 步：理解 Agent 的核心思想

这个项目里的 Agent 很简单，但已经包含 AI 应用最重要的几个角色：

- `WeatherDataStore`：负责读取和查询数据。
- `WeatherToolkit`：把数据查询包装成工具，比如最新天气、出行建议、天气总结。
- `RuleBasedLLM`：负责把工具结果组织成自然语言回答。
- `WeatherAgent`：负责把上面几层串起来。

关键代码在 `weather_agent/agent.py`：

```python
city = self._detect_city(question, city)
intent = self._detect_intent(question)
tool_result = self._run_tool(intent, city)
prompt = build_prompt(question, tool_result.content)
answer = self.llm.generate(prompt)
```

这就是很多 AI 应用的通用骨架：

```text
输入 -> 路由 -> 工具调用 -> 提示词 -> 模型输出
```

## 第 4 步：打开 debug 模式学习提示词

```powershell
python -m weather_agent.cli "北京今天适合出门吗？" --debug
```

你会看到：

- 识别出的城市
- 识别出的意图
- 调用的工具
- 传给模型的 prompt

这一步很重要，因为真实 AI 应用的效果通常不只取决于模型，也取决于你给模型的上下文是否清晰、结构是否稳定。

## 第 5 步：运行测试

```powershell
python -m unittest discover -s tests
```

测试会确认：

- 助手能回答基本问题。
- 城市识别能从问题中提取城市名。
- 出行建议会调用正确工具。

## 下一步可以扩展什么

建议按这个顺序扩展：

1. 接入真实大模型，把 `RuleBasedLLM` 换成 OpenAI、通义、智谱、DeepSeek 或本地模型。
2. 把 CSV 换成数据库或实时天气 API。
3. 增加更多工具，比如强对流风险、降雨趋势、雷达回波解释。
4. 做一个 Web API，比如 FastAPI。
5. 做一个前端页面，让用户直接聊天。
