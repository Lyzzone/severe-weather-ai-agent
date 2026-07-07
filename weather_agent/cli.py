from __future__ import annotations  # 让类型注解延迟解析，是现代 Python 项目常用写法。

import argparse  # argparse 是标准库，用来解析命令行参数。
import sys  # sys 提供和 Python 解释器相关的功能，例如标准输出。
from pathlib import Path  # Path 用来表示文件路径。

from weather_agent.agent import WeatherAgent  # 导入智能助手核心类。
from weather_agent.config import AppConfig  # 导入配置类。


def build_parser() -> argparse.ArgumentParser:  # 定义函数，用来创建命令行参数解析器。
    parser = argparse.ArgumentParser(description="气象数据智能助手")  # 创建 ArgumentParser 对象，并设置程序说明。
    parser.add_argument("question", nargs="?", default="北京今天适合出门吗？", help="用户问题")  # 添加位置参数；nargs="?" 表示可选。
    parser.add_argument("--city", help="手动指定城市")  # 添加可选参数 --city。
    parser.add_argument("--data", type=Path, help="CSV 气象数据路径")  # 添加可选参数 --data，并把输入转成 Path。
    parser.add_argument("--debug", action="store_true", help="打印 Agent 中间过程")  # store_true 表示出现 --debug 时值为 True。
    return parser  # 返回配置好的参数解析器。


def main() -> None:  # main 是命令行程序的主入口函数。
    if hasattr(sys.stdout, "reconfigure"):  # hasattr 判断对象是否拥有某个属性或方法。
        sys.stdout.reconfigure(encoding="utf-8")  # 在 Windows 终端中把标准输出设置为 UTF-8，避免中文乱码。

    args = build_parser().parse_args()  # parse_args() 读取用户在命令行输入的参数。
    config = AppConfig.from_env()  # 从环境变量加载默认配置。
    if args.data:  # 如果用户手动传入了 --data 参数。
        config = AppConfig(data_path=args.data, default_city=config.default_city)  # 创建新的配置对象，只替换数据路径。

    agent = WeatherAgent.from_config(config)  # 根据配置创建 WeatherAgent。
    response = agent.answer(args.question, city=args.city)  # 把用户问题交给 Agent，得到回答对象。

    print(response.answer)  # print 把最终答案输出到终端。

    if args.debug:  # 如果用户启用了 debug 模式，就打印中间过程。
        print("\n--- debug ---")  # 打印 debug 区域标题。
        print(f"city: {response.city}")  # 打印识别出的城市。
        print(f"intent: {response.intent}")  # 打印识别出的意图。
        print(f"tool: {response.tool_name}")  # 打印调用的工具名。
        print("prompt:")  # 打印 prompt 标题。
        print(response.prompt)  # 打印完整 prompt，方便学习 Agent 如何组织上下文。


if __name__ == "__main__":  # 只有直接运行这个文件时，这个条件才成立。
    main()  # 调用 main() 启动命令行程序。
