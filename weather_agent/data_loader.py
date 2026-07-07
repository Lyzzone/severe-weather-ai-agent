from __future__ import annotations  # 让类型注解延迟解析，便于写更清晰的类型提示。

import csv  # csv 是 Python 标准库，用来读取 CSV 表格文件。
from collections import defaultdict  # defaultdict 可以在字典缺少 key 时自动创建默认值。
from pathlib import Path  # Path 用来表示和检查文件路径。

from weather_agent.models import WeatherRecord  # 导入 WeatherRecord 数据结构，用来保存每条气象记录。


class WeatherDataStore:  # 这个类负责保存和查询所有天气数据。
    def __init__(self, records: list[WeatherRecord]) -> None:  # __init__ 是构造函数，对象创建时自动运行。
        if not records:  # if 用来做条件判断；这里判断列表是否为空。
            raise ValueError("气象数据为空，请检查 CSV 文件。")  # raise 主动抛出异常，提醒调用者数据有问题。
        self._records = sorted(records, key=lambda item: item.time)  # sorted 按时间排序；lambda 定义一个临时小函数。
        self._by_city: dict[str, list[WeatherRecord]] = defaultdict(list)  # 创建“城市 -> 记录列表”的字典。
        for record in self._records:  # for 循环逐条处理所有天气记录。
            self._by_city[record.city].append(record)  # append 把当前记录加入对应城市的列表。

    @classmethod  # classmethod 表示这个方法用于从类本身创建对象。
    def from_csv(cls, path: str | Path) -> "WeatherDataStore":  # 这个函数从 CSV 文件创建 WeatherDataStore。
        csv_path = Path(path)  # 把字符串路径转换成 Path 对象。
        if not csv_path.exists():  # exists() 判断文件是否真实存在。
            raise FileNotFoundError(f"找不到气象数据文件：{csv_path}")  # 文件不存在时抛出专门的文件异常。

        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:  # with 会自动关闭文件，避免资源泄漏。
            reader = csv.DictReader(file)  # DictReader 把每一行 CSV 转成字典。
            records = [WeatherRecord.from_csv_row(row) for row in reader]  # 列表推导式把每一行转换成 WeatherRecord。
        return cls(records)  # 用读取出的记录创建并返回 WeatherDataStore。

    def cities(self) -> list[str]:  # 这个方法返回所有可用城市名。
        return sorted(self._by_city.keys())  # keys() 取出所有城市名，sorted() 排序后返回列表。

    def records_for_city(self, city: str) -> list[WeatherRecord]:  # 这个方法查询某个城市的所有记录。
        records = self._by_city.get(city)  # get 从字典读取数据，key 不存在时返回 None。
        if not records:  # 如果 records 是 None 或空列表，就说明没有这个城市的数据。
            available = "、".join(self.cities())  # join 把城市列表拼成一个中文顿号分隔的字符串。
            raise ValueError(f"没有找到城市“{city}”的数据。可用城市：{available}")  # f-string 可以把变量值插入字符串。
        return list(records)  # 返回列表副本，避免外部代码直接修改内部列表。

    def latest(self, city: str) -> WeatherRecord:  # 这个方法返回某城市最新一条记录。
        return self.records_for_city(city)[-1]  # [-1] 表示取列表最后一个元素，因为前面已经按时间排序。

    def daily_records(self, city: str) -> list[WeatherRecord]:  # 这个方法返回最新日期当天的所有记录。
        records = self.records_for_city(city)  # 先取出这个城市的所有记录。
        latest_day = records[-1].time.date()  # date() 从 datetime 中取出日期部分。
        return [record for record in records if record.time.date() == latest_day]  # 列表推导式筛选出同一天的记录。
