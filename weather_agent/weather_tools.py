from __future__ import annotations  # 让类型注解延迟解析，便于在注解中使用还未完全加载的类型。

from dataclasses import dataclass  # dataclass 用来简化只保存数据的类。

from weather_agent.data_loader import WeatherDataStore  # 导入数据仓库类，用来查询天气记录。
from weather_agent.models import WeatherRecord  # 导入单条天气记录的数据结构。


@dataclass(frozen=True)  # frozen=True 表示工具结果创建后不应再被修改。
class ToolResult:  # ToolResult 用统一格式保存每次工具调用的结果。
    name: str  # name 保存工具名称，方便 debug 时知道调用了哪个工具。
    content: str  # content 保存给 LLM 阅读的文本内容。
    raw: dict[str, object]  # raw 保存原始结构化数据，方便程序继续处理。


class WeatherToolkit:  # WeatherToolkit 是气象工具集合，Agent 会调用这里的方法。
    def __init__(self, store: WeatherDataStore) -> None:  # 构造函数接收一个数据仓库对象。
        self.store = store  # self.store 把数据仓库保存到当前工具对象中。

    def latest_weather(self, city: str) -> ToolResult:  # 定义“查询最新天气”的工具方法。
        latest = self.store.latest(city)  # 调用数据仓库，取出指定城市最新一条记录。
        content = (  # 用括号包住多行字符串，Python 会自动拼接这些字符串。
            f"{city}最新观测时间：{latest.time:%Y-%m-%d %H:%M}\n"  # f-string 中可以格式化 datetime 时间。
            f"天气：{latest.condition}\n"  # 把天气现象写入文本。
            f"气温：{latest.temperature_c:.1f}℃\n"  # :.1f 表示保留 1 位小数。
            f"湿度：{latest.humidity_pct:.0f}%\n"  # :.0f 表示不保留小数。
            f"风速：{latest.wind_speed_mps:.1f} m/s\n"  # 输出风速并保留 1 位小数。
            f"降水：{latest.precip_mm:.1f} mm\n"  # 输出降水量并保留 1 位小数。
            f"气压：{latest.pressure_hpa:.0f} hPa\n"  # 输出气压并不保留小数。
            f"预警：{latest.warning or '无'}"  # or 可以在 warning 为空时使用“无”作为默认显示。
        )  # 结束多行字符串拼接。
        return ToolResult(name="latest_weather", content=content, raw={"latest": latest})  # 返回统一格式的工具结果。

    def travel_advice(self, city: str) -> ToolResult:  # 定义“出行建议”的工具方法。
        latest = self.store.latest(city)  # 先获取最新天气，因为出行建议依赖最新状态。
        risk, reasons = self._estimate_outdoor_risk(latest)  # 调用内部方法，返回风险等级和原因列表。
        content = (  # 构造给 LLM 阅读的工具结果文本。
            f"{city}出行风险等级：{risk}\n"  # 写入风险等级。
            f"判断依据：{'；'.join(reasons)}\n"  # join 把多个原因拼成一个字符串。
            f"最新天气：{latest.condition}，{latest.temperature_c:.1f}℃，"  # 拼接天气现象和温度。
            f"湿度 {latest.humidity_pct:.0f}%，风速 {latest.wind_speed_mps:.1f} m/s，"  # 拼接湿度和风速。
            f"降水 {latest.precip_mm:.1f} mm\n"  # 拼接降水量。
            f"预警：{latest.warning or '无'}"  # warning 为空时显示“无”。
        )  # 结束工具结果文本构造。
        return ToolResult(  # 返回工具结果对象。
            name="travel_advice",  # 标记工具名为 travel_advice。
            content=content,  # 把刚才构造的文本放入 content。
            raw={"latest": latest, "risk": risk, "reasons": reasons},  # raw 中保留原始记录、风险等级和原因。
        )  # 结束 ToolResult 创建。

    def daily_summary(self, city: str) -> ToolResult:  # 定义“当天摘要”的工具方法。
        records = self.store.daily_records(city)  # 查询最新日期当天的全部记录。
        temps = [record.temperature_c for record in records]  # 列表推导式提取所有温度。
        rains = [record.precip_mm for record in records]  # 列表推导式提取所有降水量。
        warnings = [record.warning for record in records if record.warning]  # 只保留非空的预警信息。
        conditions = "、".join(dict.fromkeys(record.condition for record in records))  # dict.fromkeys 可在保持顺序的同时去重。
        content = (  # 构造当天摘要文本。
            f"{city}当日气象摘要：\n"  # 写入摘要标题。
            f"观测次数：{len(records)}\n"  # len() 计算列表长度。
            f"天气现象：{conditions}\n"  # 输出去重后的天气现象。
            f"气温范围：{min(temps):.1f}℃ 到 {max(temps):.1f}℃\n"  # min/max 分别计算最低和最高温度。
            f"累计降水：{sum(rains):.1f} mm\n"  # sum() 计算累计降水量。
            f"预警信息：{'；'.join(warnings) if warnings else '无'}"  # 条件表达式在没有预警时显示“无”。
        )  # 结束摘要文本构造。
        return ToolResult(  # 返回工具结果对象。
            name="daily_summary",  # 标记工具名为 daily_summary。
            content=content,  # 把摘要文本放入 content。
            raw={"records": records, "warnings": warnings},  # raw 中保留当天记录和预警列表。
        )  # 结束 ToolResult 创建。

    def _estimate_outdoor_risk(self, latest: WeatherRecord) -> tuple[str, list[str]]:  # 下划线开头表示这是类内部使用的辅助方法。
        reasons: list[str] = []  # 创建空列表，用来保存风险原因。

        if latest.warning:  # 如果预警字段不是空字符串，就认为存在预警。
            reasons.append(f"存在预警或关注信息：{latest.warning}")  # append 向原因列表追加一条说明。
        if latest.temperature_c >= 35:  # 判断温度是否达到高温阈值。
            reasons.append("气温达到或超过 35℃")  # 记录高温原因。
        if latest.precip_mm >= 10:  # 判断降水量是否达到较强降水阈值。
            reasons.append("近时段降水较强")  # 记录较强降水原因。
        elif latest.precip_mm > 0:  # elif 表示前一个 if 不成立时继续判断是否有小量降水。
            reasons.append("有降水，路面可能湿滑")  # 记录有降水原因。
        if latest.wind_speed_mps >= 10:  # 判断风速是否较大。
            reasons.append("风速较大")  # 记录大风原因。
        if latest.humidity_pct >= 80:  # 判断湿度是否偏高。
            reasons.append("湿度较高，体感闷热")  # 记录高湿原因。

        if not reasons:  # 如果 reasons 仍为空，说明没有触发任何风险规则。
            reasons.append("暂无明显高影响天气信号")  # 添加一个默认说明，避免返回空原因。

        if latest.warning or latest.precip_mm >= 10 or latest.wind_speed_mps >= 10 or latest.temperature_c >= 35:  # 多个条件用 or 连接，任意一个为真就进入高风险。
            return "高", reasons  # 返回元组，第一个值是风险等级，第二个值是原因列表。
        if latest.precip_mm > 0 or latest.temperature_c >= 32 or latest.humidity_pct >= 80:  # 中等风险规则。
            return "中", reasons  # 返回中风险。
        return "低", reasons  # 所有风险条件都不满足时返回低风险。
