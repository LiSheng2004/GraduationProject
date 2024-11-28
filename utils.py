import time
import logging
from datetime import datetime
import os

# 创建Logger
def setup_logger():
    # 获取今天的日期并格式化为字符串
    today_date = datetime.now().strftime('%Y%m%d-%H%M%S')
    log_filename = f'./logs/log{today_date}.txt'
    # 创建日志文件夹
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # 创建日志器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # 设置日志级别

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台输出 INFO 及以上级别的日志

    # 创建文件处理器
    file_handler = logging.FileHandler(log_filename, mode='a')  # 以追加模式写入文件
    file_handler.setLevel(logging.DEBUG)  # 文件输出 DEBUG 及以上级别的日志

    # 创建日志格式
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 将处理器添加到日志器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# 获取当前的时间，包括毫秒
def getCurrentTime():
    timestamp = time.time()
    # 获取本地时间
    local_time = time.localtime(timestamp)

    # 获取小数部分（毫秒）
    milliseconds = int((timestamp - int(timestamp)) * 1000)

    # 将时间转换为字符串格式 yyyy-mm-dd:hh-mm-ss
    # formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", local_time) + f".{milliseconds:03d}"
    formatted_time = time.strftime("%H:%M:%S", local_time) + f".{milliseconds:03d}"
    return formatted_time

if __name__ == "__main__":
    print(getCurrentTime())
