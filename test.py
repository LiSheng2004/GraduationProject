import ctypes
from constant import *

# 假设 pBaseBuf 是一个指向 RCV_REPORT_STRUCTExV3 结构体数组的指针
# 先获取该结构体的大小
struct_size = ctypes.sizeof(RCV_REPORT_STRUCTExV3)
print("struct_size:", struct_size)
records = []

with open(r"F:\研究生\研一\计算理论\tornado-seeker\data\20241206_234159\20241206\23\raw\37补报告数据2342-09.246.dat", "rb") as f:
    while True:
        data = f.read(struct_size)
        if not data:  # 文件结束
            break
        
        # 创建结构体实例并从二进制数据中加载
        record = RCV_REPORT_STRUCTExV3()
        ctypes.memmove(ctypes.addressof(record), data, struct_size)
        
        # 添加到记录列表
        records.append(record)
# 打印单个 record 的全部信息
record = records[0]  # 假设只打印第一个记录

print("Record Details:")
for field_name, field_type in RCV_REPORT_STRUCTExV3._fields_:
    value = getattr(record, field_name)
    if field_name == "m_szLabel":  # 股票代码，ascii 解码
        value = value.decode("ascii").strip("\x00")
    elif field_name == "m_szName":  # 股票名称，gbk 解码
        value = value.decode("gbk").strip("\x00")
    elif isinstance(value, ctypes.Array):  # 数组类型（如 c_float * 3）
        value = list(value)  # 转换为 Python 列表
    elif isinstance(value, bytes):  # 字符串字段（如 formatted_date）
        value = value.decode("ascii").strip("\x00")
    print(f"{field_name}: {value}")
