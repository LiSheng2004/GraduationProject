import ctypes
from constant import *

def uniConvert(path, struct_type):
    records = []
    struct_size = ctypes.sizeof(struct_type)
    with open(path, "rb") as f:
        while True:
            data = f.read(struct_size)
            if not data:  # 文件结束
                break
            # 创建结构体实例并从二进制数据中加载
            record = struct_type()
            ctypes.memmove(ctypes.addressof(record), data, struct_size)
            # 添加到记录列表
            records.append(record)
    print(f"读取 {len(records)} 条记录")
    print('-' * 40)
    print('打印第一条记录：')
    # 打印单个 record 的全部信息
    record = records[0]  # 假设只打印第一个记录
    for field_name, field_type in struct_type._fields_:
        value = getattr(record, field_name)
        if field_name == "m_szLabel":  # 股票代码，ascii 解码
            value = value.decode("ascii").strip("\x00")
        elif field_name == "m_szName":  # 股票名称，gbk 解码
            value = value.decode("gbk").strip("\x00")
        elif field_name == "formatted_date":  # 股票名称，gbk 解码
            value = value.decode("utf-8").strip("\x00")
        elif isinstance(value, ctypes.Array):  # 数组类型（如 c_float * 3）
            value = list(value)  # 转换为 Python 列表
        elif isinstance(value, bytes):  # 字符串字段（如 formatted_date）
            value = value.decode("ascii").strip("\x00")
        print(f"{field_name}: {value}")
    print('-' * 40)
    print('打印最后一条记录：')
    record = records[-1]  # 假设只打印第一个记录
    for field_name, field_type in struct_type._fields_:
        value = getattr(record, field_name)
        if field_name == "m_szLabel":  # 股票代码，ascii 解码
            value = value.decode("ascii").strip("\x00")
        elif field_name == "m_szName":  # 股票名称，gbk 解码
            value = value.decode("gbk").strip("\x00")
        elif field_name == "formatted_date":  # 股票名称，gbk 解码
            value = value.decode("utf-8").strip("\x00")
        elif isinstance(value, ctypes.Array):  # 数组类型（如 c_float * 3）
            value = list(value)  # 转换为 Python 列表
        elif isinstance(value, bytes):  # 字符串字段（如 formatted_date）
            value = value.decode("ascii").strip("\x00")
        print(f"{field_name}: {value}")
def raw2csv_report(path):
    uniConvert(path, DAT_REPORT)

def raw2csv_power_ex(path):
    uniConvert(path, DAT_POWER_EX)
def raw2csv_marketType(path):
    uniConvert(path, DAT_HLMarketType)
def raw2csv_table_struct(path):
    uniConvert(path, DAT_TABLE_STRUCT)

def raw2csv_finance_data(path):
    uniConvert(path, DAT_FINANCEDATA)

def raw2csv_minute_ex(path):
    uniConvert(path, DAT_MINUTE_EX)

def raw2csv_fenbi(path):
    uniConvert(path, DAT_FENBI)

def raw2csv_5minute_ex(path):
    uniConvert(path, DAT_5MINUTE_EX)
def raw2csv_day_ex(path):
    uniConvert(path, DAT_DAY_EX)

