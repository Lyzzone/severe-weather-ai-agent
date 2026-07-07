# 代码逐步解释

这份文档按 AI 应用开发的常见分层来解释代码。你可以一边读，一边打开对应文件。

## 1. 数据结构：`weather_agent/models.py`

`WeatherRecord` 是一条气象记录：

```python
@dataclass(frozen=True)
class WeatherRecord:
    city: str
    time: datetime
    temperature_c: float
    humidity_pct: float
    wind_speed_mps: float
    precip_mm: float
    pressure_hpa: float
    condition: str
    warning: str
```

为什么要先定义数据结构？

- 让后续代码知道一条天气数据有哪些字段。
- 避免到处使用松散的 `dict`，降低拼错字段名的概率。
- 方便 IDE 自动提示，也方便以后写测试。

`from_csv_row()` 的作用是把 CSV 中的字符串转成 Python 类型：

- `datetime` 字符串转成 `datetime` 对象。
- 温度、湿度、降水等字符串转成 `float`。
- 缺失的预警字段转成空字符串。

## 2. 配置层：`weather_agent/config.py`

`AppConfig` 负责保存项目配置：

```python
@dataclass(frozen=True)
class AppConfig:
    data_path: Path
    default_city: str
```

`from_env()` 会读取环境变量：

- `WEATHER_DATA_PATH`：数据文件路径。
- `DEFAULT_CITY`：用户没指定城市时默认使用的城市。

配置层的好处是：以后你不需要在业务代码里到处改路径，只改环境变量或配置对象即可。

## 3. 数据读取层：`weather_agent/data_loader.py`

`WeatherDataStore` 做三件事：

1. 从 CSV 读取所有记录。
2. 按城市查询记录。
3. 提供常见查询，比如最新记录、城市列表、一天摘要。

核心方法：

```python
def latest(self, city: str) -> WeatherRecord:
    records = self.records_for_city(city)
    return max(records, key=lambda item: item.time)
```

这里的 `max(..., key=...)` 表示：按时间字段找最新的一条记录。

为什么不在 Agent 里直接读 CSV？

- Agent 只负责“编排”，不应该关心 CSV 细节。
- 数据来源以后可能换成数据库或 API，只要保持 `WeatherDataStore` 的方法不变，Agent 就不用改。

## 4. 工具层：`weather_agent/weather_tools.py`

AI Agent 经常会调用工具。这里的 `WeatherToolkit` 就是工具集合：

- `latest_weather()`：查询最新天气。
- `travel_advice()`：生成出行建议。
- `daily_summary()`：总结一天情况。

工具返回 `ToolResult`：

```python
@dataclass(frozen=True)
class ToolResult:
    name: str
    content: str
    raw: dict[str, object]
```

`content` 是给模型看的结构化文本，`raw` 是给程序继续处理的原始数据。

`travel_advice()` 里有一个简单风险判断：

```python
if latest.warning or latest.precip_mm >= 10 or latest.wind_speed_mps >= 10 or latest.temperature_c >= 35:
    risk = "高"
elif latest.precip_mm > 0 or latest.temperature_c >= 32 or latest.humidity_pct >= 80:
    risk = "中"
else:
    risk = "低"
```

这不是复杂 AI，但很适合教学：先用确定规则把数据变成可解释的结论，再交给模型组织语言。

## 5. 模型层：`weather_agent/llm.py`

`RuleBasedLLM` 是一个“假模型”，它不调用外部 API，而是根据 prompt 生成固定风格的回答。

为什么要先做假模型？

- 新手可以先学清楚应用架构。
- 不需要 API Key，不会产生调用费用。
- 测试稳定，不会因为模型输出变化而失败。

`build_prompt()` 展示了真实 AI 应用中的常见 prompt 结构：

```text
你是一个气象数据智能助手。
请只根据下面的工具结果回答用户问题。

用户问题：
...

工具结果：
...
```

这段 prompt 的目的：

- 限制模型只根据工具结果回答。
- 明确模型角色。
- 把用户问题和工具结果分开，减少混淆。

以后接入真实大模型时，可以保留 `build_prompt()`，只替换 `RuleBasedLLM.generate()` 的内部实现。

## 6. Agent 编排层：`weather_agent/agent.py`

`WeatherAgent` 是核心编排器：

```python
def answer(self, question: str, city: str | None = None) -> AgentResponse:
    detected_city = self._detect_city(question, city)
    intent = self._detect_intent(question)
    tool_result = self._run_tool(intent, detected_city)
    prompt = build_prompt(question, tool_result.content)
    answer = self.llm.generate(prompt)
    return AgentResponse(...)
```

它按顺序做五件事：

1. 从问题里找城市。
2. 判断用户想问什么。
3. 调用合适的气象工具。
4. 把工具结果放进 prompt。
5. 让模型生成回答。

这就是“工具增强型 AI 助手”的最小闭环。

## 7. 命令行入口：`weather_agent/cli.py`

`cli.py` 让你可以在终端里运行助手：

```powershell
python -m weather_agent.cli "北京今天适合出门吗？"
```

`argparse` 负责解析参数：

- `question`：用户问题。
- `--city`：手动指定城市。
- `--data`：手动指定 CSV 数据路径。
- `--debug`：打印中间过程，方便学习。

命令行入口通常只是薄薄一层，它不应该写太多业务逻辑。业务逻辑应该放在 Agent、工具和数据层中。

## 8. 测试：`tests/test_agent.py`

测试使用 Python 自带的 `unittest`。

```powershell
python -m unittest discover -s tests
```

测试的目标不是覆盖所有情况，而是保证核心链路不会断：

- 能创建 Agent。
- 能从问题中识别城市。
- 能根据“出门”这类词调用出行建议工具。

当你以后重构代码或接入真实模型时，测试能帮你确认基本功能还在。
