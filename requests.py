# requests.py
from dll_loader import dll  # 导入已加载的 DLL 实例

def ask_stock_day(stock_code: str, time_period: int):
    """调用 AskStockDay 函数请求股票数据"""
    stock_code_bytes = stock_code.encode('ascii')
    result = dll.AskStockDay(stock_code_bytes, time_period)
    if result == -1:
        print(f"Failed to request stock day data for {stock_code}.")
    else:
        print(f"Successfully requested stock day data for {stock_code}.")
