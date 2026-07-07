import unittest  # unittest 是 Python 标准库中的测试框架。

from weather_agent.agent import WeatherAgent  # 导入要测试的 Agent 类。
from weather_agent.data_loader import WeatherDataStore  # 导入数据仓库类，用来准备测试数据。


class WeatherAgentTest(unittest.TestCase):  # 测试类继承 unittest.TestCase，表示这里是一组测试用例。
    def setUp(self) -> None:  # setUp 会在每个测试方法运行前自动执行。
        store = WeatherDataStore.from_csv("data/sample_weather.csv")  # 从示例 CSV 读取测试数据。
        self.agent = WeatherAgent(store=store)  # 创建 Agent，并保存到 self 上供测试方法使用。

    def test_answer_latest_weather(self) -> None:  # 测试普通天气查询是否能走 latest_weather 意图。
        response = self.agent.answer("广州现在天气怎么样？")  # 调用 Agent，模拟用户提问。
        self.assertEqual(response.city, "广州")  # assertEqual 判断两个值是否相等。
        self.assertEqual(response.intent, "latest_weather")  # 检查意图是否识别为最新天气。
        self.assertIn("广州最新观测时间", response.answer)  # assertIn 判断某段文字是否出现在答案中。

    def test_answer_travel_advice(self) -> None:  # 测试出行类问题是否能调用 travel_advice 工具。
        response = self.agent.answer("北京今天适合出门吗？")  # 模拟用户询问是否适合出门。
        self.assertEqual(response.tool_name, "travel_advice")  # 检查调用的工具是否正确。
        self.assertIn("出行风险等级", response.answer)  # 检查答案中是否包含出行风险信息。

    def test_answer_daily_summary(self) -> None:  # 测试总结类问题是否能调用 daily_summary 工具。
        response = self.agent.answer("上海天气总结")  # 模拟用户要求总结上海天气。
        self.assertEqual(response.tool_name, "daily_summary")  # 检查调用的工具是否为当天摘要工具。
        self.assertIn("当日气象摘要", response.answer)  # 检查答案中是否包含摘要标题。


if __name__ == "__main__":  # 只有直接运行这个测试文件时，这个条件才成立。
    unittest.main()  # 启动 unittest 测试运行器。
