from __future__ import annotations  # 让类型注解可以延迟解析，便于在类内部引用类自己。

from dataclasses import dataclass  # dataclass 可以自动生成 __init__ 等基础方法。
from datetime import datetime  # datetime 用来表示具体日期和时间。


@dataclass(frozen=True)  # frozen=True 表示对象创建后不能随意修改字段，适合保存一条固定观测记录。
class WeatherRecord:  # class 用来定义一种自定义数据类型，这里表示“一条天气记录”。
    city: str  # str 表示字符串类型，city 保存城市名。
    time: datetime  # time 保存观测时间，类型是 datetime。
    temperature_c: float  # float 表示小数，temperature_c 保存摄氏温度。
    humidity_pct: float  # humidity_pct 保存相对湿度百分比。
    wind_speed_mps: float  # wind_speed_mps 保存风速，单位是 m/s。
    precip_mm: float  # precip_mm 保存降水量，单位是 mm。
    pressure_hpa: float  # pressure_hpa 保存气压，单位是 hPa。
    condition: str  # condition 保存天气现象，例如“多云”“中雨”。
    warning: str  # warning 保存预警或关注信息，没有预警时是空字符串。

    @classmethod  # classmethod 表示这个方法属于类本身，第一个参数是 cls 而不是 self。
    def from_csv_row(cls, row: dict[str, str]) -> "WeatherRecord":  # def 定义函数；这里把 CSV 的一行字典转成 WeatherRecord。
        return cls(  # return 返回函数结果；cls(...) 表示创建一个 WeatherRecord 对象。
            city=row["city"].strip(),  # row["city"] 读取城市字段；strip() 去掉前后空格。
            time=datetime.strptime(row["datetime"].strip(), "%Y-%m-%d %H:%M"),  # strptime 把时间字符串解析成 datetime。
            temperature_c=float(row["temperature_c"]),  # float(...) 把 CSV 中的字符串转成小数。
            humidity_pct=float(row["humidity_pct"]),  # 把湿度字符串转成小数。
            wind_speed_mps=float(row["wind_speed_mps"]),  # 把风速字符串转成小数。
            precip_mm=float(row["precip_mm"]),  # 把降水量字符串转成小数。
            pressure_hpa=float(row["pressure_hpa"]),  # 把气压字符串转成小数。
            condition=row["condition"].strip(),  # 读取天气现象并去掉多余空格。
            warning=row.get("warning", "").strip(),  # get 可以在字段不存在时返回默认值，这里默认是空字符串。
        )  # 右括号结束对象创建。
