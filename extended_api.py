# extended_api.py
import ctypes
# 从dll_loader中导入dll
from ctypes import wintypes

BOOL = wintypes.BOOL

def init_dll_functions(dll):
    # 初始化dll函数参数
    # 规定Stock_Init的传入参数和返回值的类型
    dll.Stock_Init.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int]
    dll.Stock_Init.restype = ctypes.c_int
    # 定义函数参数和返回值
    # 激活接收程序函数
    dll.SetupReceiver.argtypes = [ctypes.c_int]
    dll.SetupReceiver.restype = ctypes.c_int
    # 取得股票驱动信息
    dll.SetupReceiver.argtypes = [ctypes.c_int,ctypes.POINTER(ctypes.c_char)]
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
    
    return dll

# 补日线数据函数
def ask_stock_day(dll,stock_code: str, time_period: int) -> str:
    # 创建缓冲区，假设最大长度为 256 字节
    buffer_size = 256
    stock_code_buffer = ctypes.create_string_buffer(buffer_size)
    stock_code_buffer.value = stock_code.encode('ascii')  # 初始化缓冲区内容为股票代码

    # 调用 DLL 函数
    result = dll.AskStockDay(stock_code_buffer, time_period)

    # 检查返回值
    if result != 1:  # 假设返回值 0 表示成功
        raise ValueError(f"AskStockDay failed with error code: {result}")

    # 从缓冲区读取返回数据
    return stock_code_buffer.value.decode('ascii')

# 补五分钟线数据函数
def ask_stock_mn5(dll,stock_code: str, time_period: int) -> int:
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
# def setup_receiver(dll,show_window: bool) -> int:
#     return dll.SetupReceiver(BOOL(show_window))
