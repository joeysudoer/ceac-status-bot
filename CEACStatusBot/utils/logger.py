from datetime import datetime


def log_with_timestamp(message: str) -> None:
    """打印带时间戳的日志信息
    
    格式: YYYY-MM-DD HH:mm:ss - {message}
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} - {message}")


def get_timestamp() -> str:
    """获取格式化的时间戳字符串
    
    Returns:
        格式化的时间戳字符串: YYYY-MM-DD HH:mm:ss
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

