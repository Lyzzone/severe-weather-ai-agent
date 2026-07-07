from __future__ import annotations  # 让类型注解延迟解析，属于常见的现代 Python 写法。


def build_prompt(question: str, tool_context: str) -> str:  # 定义函数，把用户问题和工具结果组装成 prompt。
    return (  # return 返回拼接完成的字符串。
        "你是一个气象数据智能助手。\n"  # 给模型设定角色。
        "请只根据下面的工具结果回答用户问题，不要编造没有出现的数据。\n"  # 约束模型只能根据工具结果回答。
        "回答要简洁、清楚，并给出可执行建议。\n\n"  # 说明回答风格。
        f"用户问题：\n{question}\n\n"  # 把用户原始问题放进 prompt。
        f"工具结果：\n{tool_context}\n"  # 把工具返回的上下文放进 prompt。
    )  # 结束多行字符串拼接。


class RuleBasedLLM:  # 定义一个规则版 LLM 类，用来模拟真实大模型。
    """A deterministic stand-in for a real LLM during early development."""  # 类文档字符串：说明这个类是早期开发用的确定性替身。

    def generate(self, prompt: str) -> str:  # generate 模拟“根据 prompt 生成回答”的模型接口。
        if "出行风险等级：高" in prompt:  # in 判断某段文字是否出现在 prompt 中。
            advice = "建议减少户外活动，必要出行时注意防暑、防雨或避开强天气时段。"  # 高风险时给出更保守的建议。
        elif "出行风险等级：中" in prompt:  # elif 表示继续判断另一种情况。
            advice = "可以出行，但建议携带雨具、关注临近预报，并预留通勤时间。"  # 中风险时给出注意事项。
        elif "出行风险等级：低" in prompt:  # 判断是否是低风险出行情境。
            advice = "整体适合出行，保持常规防晒和补水即可。"  # 低风险时给出正常出行建议。
        elif "当日气象摘要" in prompt:  # 判断用户是否在看当天摘要。
            advice = "以上是当日主要天气变化，可重点关注气温范围、累计降水和预警信息。"  # 摘要类问题的建议。
        else:  # else 处理前面条件都不满足的默认情况。
            advice = "以上是最新观测结果，可结合你的具体活动安排判断是否需要调整计划。"  # 默认建议。

        return f"{self._extract_tool_result(prompt)}\n\n建议：{advice}"  # 把工具结果和建议拼成最终回答。

    def _extract_tool_result(self, prompt: str) -> str:  # 内部辅助函数：从 prompt 中取出工具结果部分。
        marker = "工具结果："  # marker 是分隔标记，用来定位工具结果开始的位置。
        if marker not in prompt:  # 如果 prompt 里没有这个标记，就直接返回整个 prompt。
            return prompt.strip()  # strip() 去掉字符串前后的空白字符。
        return prompt.split(marker, 1)[1].strip()  # split(..., 1) 只切一次，[1] 取标记后面的内容。
