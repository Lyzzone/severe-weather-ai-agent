from __future__ import annotations  # 让类型注解延迟解析，便于写更现代的类型标注。

from dataclasses import dataclass  # dataclass 用来快速定义保存数据的类。

from weather_agent.config import AppConfig  # 导入应用配置类。
from weather_agent.data_loader import WeatherDataStore  # 导入气象数据仓库。
from weather_agent.llm import RuleBasedLLM, build_prompt  # 导入规则版 LLM 和 prompt 构造函数。
from weather_agent.weather_tools import ToolResult, WeatherToolkit  # 导入工具结果类型和工具集合。


@dataclass(frozen=True)  # frozen=True 让响应对象创建后不可变，便于调试和测试。
class AgentResponse:  # AgentResponse 保存一次问答的完整结果。
    question: str  # question 保存用户原始问题。
    city: str  # city 保存识别出的城市。
    intent: str  # intent 保存识别出的用户意图。
    tool_name: str  # tool_name 保存本次调用的工具名称。
    prompt: str  # prompt 保存发送给模型的完整提示词。
    answer: str  # answer 保存最终返回给用户的回答。


class WeatherAgent:  # WeatherAgent 是整个智能助手的核心编排类。
    def __init__(  # __init__ 定义创建 WeatherAgent 时需要准备哪些对象。
        self,  # self 代表当前正在创建的 WeatherAgent 对象。
        store: WeatherDataStore,  # store 是数据仓库，负责提供气象数据。
        default_city: str = "北京",  # default_city 有默认值，调用者不传时使用“北京”。
        llm: RuleBasedLLM | None = None,  # llm 可以传入模型对象；None 表示不传。
    ) -> None:  # -> None 表示这个函数没有返回值。
        self.store = store  # 把数据仓库保存到当前对象。
        self.default_city = default_city  # 保存默认城市。
        self.toolkit = WeatherToolkit(store)  # 创建工具集合，工具集合内部会使用同一个数据仓库。
        self.llm = llm or RuleBasedLLM()  # 如果外部没有传 llm，就创建一个默认的规则版 LLM。

    @classmethod  # classmethod 让我们可以通过 WeatherAgent.from_config(...) 创建对象。
    def from_config(cls, config: AppConfig) -> "WeatherAgent":  # 这个工厂方法根据配置创建 Agent。
        store = WeatherDataStore.from_csv(config.data_path)  # 根据配置中的 CSV 路径读取数据。
        return cls(store=store, default_city=config.default_city)  # 创建并返回 WeatherAgent 对象。

    def answer(self, question: str, city: str | None = None) -> AgentResponse:  # 对外暴露的主方法：输入问题，输出回答。
        detected_city = self._detect_city(question, city)  # 第一步：识别城市。
        intent = self._detect_intent(question)  # 第二步：识别用户意图。
        tool_result = self._run_tool(intent, detected_city)  # 第三步：根据意图调用对应工具。
        prompt = build_prompt(question, tool_result.content)  # 第四步：把问题和工具结果组装成 prompt。
        answer = self.llm.generate(prompt)  # 第五步：调用模型接口生成最终回答。

        return AgentResponse(  # 把本次问答的中间过程和最终结果一起返回。
            question=question,  # 保存原始问题。
            city=detected_city,  # 保存识别出的城市。
            intent=intent,  # 保存识别出的意图。
            tool_name=tool_result.name,  # 保存调用的工具名。
            prompt=prompt,  # 保存完整 prompt，debug 时很有用。
            answer=answer,  # 保存最终答案。
        )  # 结束 AgentResponse 创建。

    def _detect_city(self, question: str, city: str | None) -> str:  # 内部方法：识别问题中的城市。
        if city:  # 如果用户通过参数手动指定了城市，就优先使用它。
            return city  # 直接返回手动指定的城市。
        for candidate in self.store.cities():  # 遍历数据中所有可用城市。
            if candidate in question:  # 判断城市名是否出现在用户问题里。
                return candidate  # 找到城市后立即返回。
        return self.default_city  # 如果没有识别到城市，就返回默认城市。

    def _detect_intent(self, question: str) -> str:  # 内部方法：用关键词判断用户意图。
        travel_keywords = ("出门", "出行", "适合", "风险", "预警", "安全吗")  # 元组保存出行建议相关关键词。
        summary_keywords = ("总结", "概况", "一天", "今日", "趋势")  # 元组保存天气总结相关关键词。

        if any(keyword in question for keyword in travel_keywords):  # any() 只要有一个关键词命中就返回 True。
            return "travel_advice"  # 返回出行建议意图。
        if any(keyword in question for keyword in summary_keywords):  # 检查是否命中总结类关键词。
            return "daily_summary"  # 返回当天总结意图。
        return "latest_weather"  # 默认意图是查询最新天气。

    def _run_tool(self, intent: str, city: str) -> ToolResult:  # 内部方法：根据意图选择并调用工具。
        if intent == "travel_advice":  # 如果意图是出行建议。
            return self.toolkit.travel_advice(city)  # 调用出行建议工具。
        if intent == "daily_summary":  # 如果意图是当天总结。
            return self.toolkit.daily_summary(city)  # 调用当天摘要工具。
        return self.toolkit.latest_weather(city)  # 其他情况默认调用最新天气工具。
