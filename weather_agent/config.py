from __future__ import annotations  # 让类型注解延迟解析，提升类型提示兼容性。

import os  # os 用来读取环境变量等操作系统信息。
from dataclasses import dataclass  # dataclass 用来快速创建只保存数据的类。
from pathlib import Path  # Path 用面向对象的方式表示文件路径。


@dataclass(frozen=True)  # frozen=True 让配置对象不可变，避免运行中被意外修改。
class AppConfig:  # AppConfig 用来集中保存应用配置。
    data_path: Path  # data_path 表示 CSV 气象数据文件路径。
    default_city: str  # default_city 表示没有识别到城市时使用的默认城市。

    @classmethod  # classmethod 让我们可以用 AppConfig.from_env() 创建配置对象。
    def from_env(cls) -> "AppConfig":  # 这个函数从环境变量读取配置。
        return cls(  # 返回一个 AppConfig 实例。
            data_path=Path(os.getenv("WEATHER_DATA_PATH", "data/sample_weather.csv")),  # getenv 读取环境变量，读不到就用默认路径。
            default_city=os.getenv("DEFAULT_CITY", "北京"),  # 读取默认城市，读不到就使用“北京”。
        )  # 结束 AppConfig 的创建。
