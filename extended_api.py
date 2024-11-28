# extended_api.py
import ctypes
# 从dll_loader中导入dll
from dll_loader import dll
from ctypes import wintypes

BOOL = wintypes.BOOL

# 定义函数参数和返回值
def setup_functions():
    # 激活接收程序函数
    dll.SetupReceiver.argtypes = [BOOL]
    dll.SetupReceiver.restype = ctypes.c_int

    # 补日线数据函数
    dll.AskStockDay.argtypes = [ctypes.c_char_p, ctypes.c_int]
    dll.AskStockDay.restype = ctypes.c_int

    # 补五分钟线数据函数
    dll.AskStockMn5.argtypes = [ctypes.c_char_p, ctypes.c_int]
    dll.AskStockMn5.restype = ctypes.c_int

    # 获取个股资料函数
    dll.AskStockBase.argtypes = [ctypes.c_char_p]
    dll.AskStockBase.restype = ctypes.c_int

    # 获取财经新闻函数
    dll.AskStockNews.argtypes = []
    dll.AskStockNews.restype = ctypes.c_int

    # 数据中止函数
    dll.AskStockHalt.argtypes = []
    dll.AskStockHalt.restype = ctypes.c_int

    # 获取分时数据函数
    dll.AskStockMin.argtypes = [ctypes.c_char_p]
    dll.AskStockMin.restype = ctypes.c_int

    # 获取分笔数据函数
    dll.AskStockPRP.argtypes = [ctypes.c_char_p]
    dll.AskStockPRP.restype = ctypes.c_int

    # 获取除权数据函数
    dll.AskStockPwr.argtypes = []
    dll.AskStockPwr.restype = ctypes.c_int

    # 获取财务数据函数
    dll.AskStockFin.argtypes = []
    dll.AskStockFin.restype = ctypes.c_int

# 补日线数据函数
def ask_stock_day(stock_code: str, time_period: int) -> int:
    stock_code_bytes = stock_code.encode('ascii') if stock_code else None
    return dll.AskStockDay(stock_code_bytes, time_period)

# 补五分钟线数据函数
def ask_stock_mn5(stock_code: str, time_period: int) -> int:
    stock_code_bytes = stock_code.encode('ascii') if stock_code else None
    return dll.AskStockMn5(stock_code_bytes, time_period)

# 获取个股资料函数
def ask_stock_base(stock_code: str) -> int:
    print("ask_stock_base")
    stock_code_bytes = stock_code.encode('ascii') if stock_code else None
    return dll.AskStockBase(stock_code_bytes)

# 获取财经新闻函数
def ask_stock_news() -> int:
    return dll.AskStockNews()

# 数据中止函数
def ask_stock_halt() -> int:
    return dll.AskStockHalt()

# 获取分时数据函数
def ask_stock_min(stock_code: str) -> int:
    stock_code_bytes = stock_code.encode('ascii') if stock_code else None
    return dll.AskStockMin(stock_code_bytes)

# 获取分笔数据函数
def ask_stock_prp(stock_code: str) -> int:
    stock_code_bytes = stock_code.encode('ascii') if stock_code else None
    return dll.AskStockPRP(stock_code_bytes)

# 获取除权数据函数
def ask_stock_pwr() -> int:
    return dll.AskStockPwr()

# 获取财务数据函数
def ask_stock_fin() -> int:
    return dll.AskStockFin()

# 激活接收程序
def setup_receiver(show_window: bool) -> int:
    return dll.SetupReceiver(BOOL(show_window))
