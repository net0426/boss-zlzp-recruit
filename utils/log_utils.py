import logging
import os
from datetime import datetime


# 初始化日志配置
def init_logger():
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志文件名
    log_file = os.path.join(log_dir, f"recruit_{datetime.now().strftime('%Y%m%d')}.log")

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),  # 写入文件
            logging.StreamHandler()  # 输出到控制台
        ]
    )
    return logging.getLogger("招聘筛选系统")


# 全局日志对象
logger = init_logger()