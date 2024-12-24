import win32con
import ctypes

# 根文件夹路径
ROOT_PATH = r"\\10.68.1.151\tj07166_001\Etornado-data"
# ROOT_PATH = './data'

# 各个csv文件表头
csv_RCV_REPORT = ["结构大小", "成交时间", "股票市场类型", "股票代码", "股票名称", "昨收", "今开", "最高", "最低", "最新", 
                "成交量", "成交额", "申买价1", "申买价2", "申买价3", "申买量1", "申买量2", "申买量3", 
                "申卖价1", "申卖价2", "申卖价3", "申卖量1", "申卖量2", "申卖量3", 
                "申买价4", "申买量4", "申卖价4", "申卖量4", 
                "申买价5", "申买量5", "申卖价5", "申卖量5"]
csv_RCV_FENBI = ["股票代码", "市场类型","日期",'昨收','今开','分别数量','具体时间','最高价' ,'最低价','最新价格',"成交量", "成交额", "申买价1", "申买价2", 
                "申买价3", "申买价4", "申买价5", "申买量1", "申买量2", "申买量3", 
                "申买量4", "申买量5", "申卖价1", "申卖价2", "申卖价3", "申卖价4", 
                "申卖价5", "申卖量1", "申卖量2", "申卖量3", "申卖量4", "申卖量5"]
csv_RCV_POWER_EX = ["股票代码", "市场类型","时间", "每股送", "每股配", "配股价",'每股红利',]
csv_RCV_MKTTBLDATA = ["市场代码", "市场名称", "市场属性", "数据日期", 
                    "交易时段个数", "开市时间", "收市时间", "证券个数"]
csv_TABLE_STRUCT = ['股票代码','股票名称',"每股手数"]
csv_FINANCEDATA = ["股票市场类型", "保留字段", "股票代码", "财务数据的日期", "总股本", "国家股", "发起人法人股",
                    "法人股", "B股", "H股", "目前流通", "职工股", "A2转配股", "总资产(千元)", "流动资产",
                    "固定资产", "无形资产", "长期投资", "流动负债", "长期负债", "资本公积金", "每股公积金",
                    "股东权益", "主营收入", "主营利润", "其他利润", "营业利润", "投资收益", "补贴收入",
                    "营业外收支", "上年损益调整", "利润总额", "税后利润", "净利润", "未分配利润", "每股未分配",
                    "每股收益", "每股净资产", "调整每股净资产", "股东权益比", "净资收益率"]
csv_MINUTES_EX = ["股票代码", "市场类型","时间", "最新价", "成交量", "成交金额"]
csv_DAY_EX = ["股票代码", "市场类型","时间", "开盘", "最高", "最低",'收盘','交易量','交易额','涨数','跌数']
csv_5MIN_EX = ["股票代码", "市场类型","时间", "开盘", "最高", "最低",'收盘','交易量','交易额','主动买量']

RCV_REPORT = 0x3f001234  # 1056969268
RCV_FILEDATA = 0x3f001235  # 1056969269
RCV_FENBIDATA = 0x3f001258  # 1056969288
RCV_MKTTBLDATA = 0x3f001259  # 1056969289
RCV_FINANCEDATA = 0x3f001300  # 1056969472

# 工作方式类型定义
RCV_WORK_SENDMSG = 4  # 消息工作方式

# 证券市场
SH_MARKET_EX = b'HS'  # 上海
SZ_MARKET_EX = b'ZS'  # 深圳
HK_MARKET_EX = b'KH'  # 香港

# 文件数据类型
# 结构数组形式的文件数据
FILE_HISTORY_EX = 2  # 补日线数据
FILE_MINUTE_EX = 4   # 补分钟线数据
FILE_POWER_EX = 6    # 补充除权数据
FILE_5MINUTE_EX = 81  # 补5分钟线数据

FILE_BASE_EX = 0x1000  # 钱龙兼容基本资料文件
FILE_NEWS_EX = 0x1002   # 新闻类
FILE_HTML_EX = 0x1004   # HTML文件
FILE_TYPE_RES = -1      # 保留

# 消息子类型
News_Sha_Ex = 2        # 上证消息
News_Szn_Ex = 4        # 深证消息
News_Fin_Ex = 6        # 财经报道
News_TVSta_Ex = 8      # 电视台通知
News_Unknown_Ex = -1    # 未知提供者

# Definition For nInfo of Function GetStockDrvInfo(int nInfo,void * pBuf)
RI_IDSTRING = 1        # 厂商名称, 返回(LPCSTR)厂商名
RI_IDCODE = 2          # 卡号
RI_VERSION = 3         # 驱动程序版本
RI_V2SUPPORT = 6       # 支持深圳SJS库结构

# 数据长度常量
STKLABEL_LEN = 10      # 股号数据长度
STKNAME_LEN = 32       # 股名长度
MKTNAME_LEN = 16       # 码表所代表的市场名称

# 定义数据头标志 补充数据头
EKE_HEAD_TAG = 0xffffffff


My_Msg_StkData = win32con.WM_APP + 1

# 定义 RCV_FILE_HEADEx 结构体
class RCV_FILE_HEADEx(ctypes.Structure):
    _fields_ = [
        ("m_dwAttrib", ctypes.c_uint32),            # 文件子类型
        ("m_dwLen", ctypes.c_uint32),               # 文件长度
        ("m_dwSerialNo", ctypes.c_uint32),          # 序列号
        ("m_szFileName", ctypes.c_char * 260),      # 文件名或 URL，最大路径长度为 MAX_PATH (260)
    ]
import time

# 定义 RCV_REPORT_STRUCTExV3 结构体
class RCV_REPORT_STRUCTExV3(ctypes.Structure): # 158
    # 设置内存对齐
    _pack_ = 1
    _fields_ = [
        ("m_cbSize", ctypes.c_uint16),                # 结构大小 (WORD) 2
        ("m_time", ctypes.c_long),                    # 成交时间 (time_t) 4
        ("m_wMarket", ctypes.c_uint16),               # 股票市场类型 (WORD) 2
        ("m_szLabel", ctypes.c_char * STKLABEL_LEN), # 股票代码 10
        ("m_szName", ctypes.c_char * STKNAME_LEN),   # 股票名称 32 
        ("m_fLastClose", ctypes.c_float),             # 昨收 4
        ("m_fOpen", ctypes.c_float),                  # 今开 4
        ("m_fHigh", ctypes.c_float),                  # 最高 4
        ("m_fLow", ctypes.c_float),                   # 最低 4
        ("m_fNewPrice", ctypes.c_float),              # 最新 4 
        ("m_fVolume", ctypes.c_float),                # 成交量 4
        ("m_fAmount", ctypes.c_float),                # 成交额 4
        ("m_fBuyPrice", ctypes.c_float * 3),         # 申买价1,2,3 12 
        ("m_fBuyVolume", ctypes.c_float * 3),        # 申买量1,2,3 12
        ("m_fSellPrice", ctypes.c_float * 3),        # 申卖价1,2,3 12
        ("m_fSellVolume", ctypes.c_float * 3),       # 申卖量1,2,3 12 
        ("m_fBuyPrice4", ctypes.c_float),             # 申买价4 4  
        ("m_fBuyVolume4", ctypes.c_float),            # 申买量4 4
        ("m_fSellPrice4", ctypes.c_float),            # 申卖价4 4
        ("m_fSellVolume4", ctypes.c_float),           # 申卖量4 4
        ("m_fBuyPrice5", ctypes.c_float),             # 申买价5 4
        ("m_fBuyVolume5", ctypes.c_float),            # 申买量5 4
        ("m_fSellPrice5", ctypes.c_float),            # 申卖价5 4
        ("m_fSellVolume5", ctypes.c_float),           # 申卖量5 4
    ]

class RCV_EKE_HEADEx(ctypes.Structure):
    _fields_ = [
        ("m_dwHeadTag", ctypes.c_ulong),  # DWORD 通常是无符号长整型
        ("m_wMarket", ctypes.c_ushort),    # WORD 通常是无符号短整型
        ("m_szLabel", ctypes.c_char * STKLABEL_LEN),  # 股票代码
    ]
# 补日线数据
class RCV_HISTORY_STRUCTEx(ctypes.Union):
    class _Fields(ctypes.Structure):
        _fields_ = [
            ("m_time", ctypes.c_long),      # 使用 c_long 来表示 time_t
            ("m_fOpen", ctypes.c_float),
            ("m_fHigh", ctypes.c_float),
            ("m_fLow", ctypes.c_float),
            ("m_fClose", ctypes.c_float),
            ("m_fVolume", ctypes.c_float),
            ("m_fAmount", ctypes.c_float),
            ("m_wAdvance", ctypes.c_ushort),  # WORD 涨数,仅大盘有效
            ("m_wDecline", ctypes.c_ushort),  # WORD 跌数,仅大盘有效
        ]

    _fields_ = [
        ("data", _Fields),
        ("m_head", RCV_EKE_HEADEx),  # Union 中的另一个结构
    ]
    _anonymous_ = ("data",)
# 补充分时线数据
class RCV_MINUTE_STRUCTEx(ctypes.Union):
    # _pack_ = 1
    class InnerStruct(ctypes.Structure):
            _fields_ = [
            ("m_time", ctypes.c_long),                     # time_t 对应 32 位的有符号整数
            ("m_fPrice", ctypes.c_float),
            ("m_fVolume", ctypes.c_float),
            ("m_fAmount", ctypes.c_float)
        ]
    _fields_ = [
        ("m_head", RCV_EKE_HEADEx),                   # RCV_EKE_HEADEx 结构体
        ("m_inner_struct", InnerStruct)               # 内部结构体
    ]
    # 设置 _anonymous_ 以便可以直接访问内部结构体的字段
    _anonymous_ = ("m_inner_struct",)
# 接收除权数据
class RCV_POWER_STRUCTEx(ctypes.Union):
    class _Fields(ctypes.Structure):
        _fields_ = [
            ("m_time", ctypes.c_long),       # 使用 c_long 来表示 time_t
            ("m_fGive", ctypes.c_float),     # 每股送
            ("m_fPei", ctypes.c_float),      # 每股配
            ("m_fPeiPrice", ctypes.c_float), # 配股价
            ("m_fProfit", ctypes.c_float),    # 每股红利
        ]
    _fields_ = [
        ("data", _Fields),
        ("m_head", RCV_EKE_HEADEx),  # Union 中的另一个结构
    ]
    _anonymous_ = ("data",)
# 补五分钟数据
class RCV_HISMINUTE_STRUCTEx(ctypes.Union):
    class _Fields(ctypes.Structure):
        _fields_ = [
            ("m_time", ctypes.c_long),         # 使用 c_long 来表示 time_t
            ("m_fOpen", ctypes.c_float),       # 开盘
            ("m_fHigh", ctypes.c_float),       # 最高
            ("m_fLow", ctypes.c_float),        # 最低
            ("m_fClose", ctypes.c_float),      # 收盘
            ("m_fVolume", ctypes.c_float),     # 量
            ("m_fAmount", ctypes.c_float),     # 额
            ("m_fActiveBuyVol", ctypes.c_float), # 主动买量
        ]

    _fields_ = [
        ("data", _Fields),
        ("m_head", RCV_EKE_HEADEx),  # Union 中的另一个结构
    ]
    _anonymous_ = ("data",)
# 定义联合体
class RCV_DATA_UNION(ctypes.Union):
    _fields_ = [
        ("m_pReportV3", ctypes.POINTER(RCV_REPORT_STRUCTExV3)), # 报告数据
        ("m_pDay", ctypes.POINTER(RCV_HISTORY_STRUCTEx)), # 补日线数据
        ("m_pMinute", ctypes.POINTER(RCV_MINUTE_STRUCTEx)), # 补分钟数据
        ("m_pPower", ctypes.POINTER(RCV_POWER_STRUCTEx)), # 补除权数据
        ("m_p5Min", ctypes.POINTER(RCV_HISMINUTE_STRUCTEx)), # 补五分钟数据
        ("m_pData", ctypes.c_void_p),  # 使用 void* 表示通用指针
    ]

# 定义 RCV_DATA 结构体
class RCV_DATA(ctypes.Structure):
    # _pack_ = 1
    _fields_ = [
        ("m_wDataType", ctypes.c_int),        # 文件类型
        ("m_nPacketNum", ctypes.c_int),       # 记录数
        ("m_File", RCV_FILE_HEADEx),          # 文件接口
        ("m_bDISK", ctypes.c_bool),           # 文件是否已存盘
        ("data_union", RCV_DATA_UNION),       # 联合体
    ]
class RCV_TABLE_STRUCT(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_szLabel", ctypes.c_char * STKLABEL_LEN),  # 股票代码,以'\0'结尾,如 "500500"
        ("m_szName", ctypes.c_char * STKNAME_LEN),    # 股票名称,以'\0'结尾,"上证指数"
        ("m_cProperty", ctypes.c_ushort),               # 每手股数
    ]

class HLMarketType(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_wMarket", ctypes.c_ushort),                 # 市场代码 2
        ("m_Name", ctypes.c_char * MKTNAME_LEN),       # 市场名称 16
        ("m_lProperty", ctypes.c_ulong),                # 市场属性 4
        ("m_lDate", ctypes.c_ulong),                    # 数据日期 4
        ("m_PeriodCount", ctypes.c_ushort),            # 交易时段个数 2
        ("m_OpenTime", ctypes.c_ushort * 5),           # 开市时间 10
        ("m_CloseTime", ctypes.c_ushort * 5),          # 收市时间 10
        ("m_nCount", ctypes.c_ushort),                  # 该市场的证券个数 2
        ("m_Data", ctypes.POINTER(RCV_TABLE_STRUCT)),   # 指向证券数据的指针
    ]

class Fin_LJF_STRUCTEx(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_wMarket", ctypes.c_ushort),                 # 股票市场类型
        ("N1", ctypes.c_ushort),                        # 保留字段
        ("m_szLabel", ctypes.c_char * 10),             # 股票代码
        ("BGRQ", ctypes.c_long),                        # 财务数据的日期
        ("ZGB", ctypes.c_float),                        # 总股本
        ("GJG", ctypes.c_float),                        # 国家股
        ("FQFRG", ctypes.c_float),                      # 发起人法人股
        ("FRG", ctypes.c_float),                        # 法人股
        ("BGS", ctypes.c_float),                        # B股
        ("HGS", ctypes.c_float),                        # H股
        ("MQLT", ctypes.c_float),                       # 目前流通
        ("ZGG", ctypes.c_float),                        # 职工股
        ("A2ZPG", ctypes.c_float),                      # A2转配股
        ("ZZC", ctypes.c_float),                        # 总资产(千元)
        ("LDZC", ctypes.c_float),                       # 流动资产
        ("GDZC", ctypes.c_float),                       # 固定资产
        ("WXZC", ctypes.c_float),                       # 无形资产
        ("CQTZ", ctypes.c_float),                       # 长期投资
        ("LDFZ", ctypes.c_float),                       # 流动负债
        ("CQFZ", ctypes.c_float),                       # 长期负债
        ("ZBGJJ", ctypes.c_float),                      # 资本公积金
        ("MGGJJ", ctypes.c_float),                      # 每股公积金
        ("GDQY", ctypes.c_float),                       # 股东权益
        ("ZYSR", ctypes.c_float),                       # 主营收入
        ("ZYLR", ctypes.c_float),                       # 主营利润
        ("QTLR", ctypes.c_float),                       # 其他利润
        ("YYLR", ctypes.c_float),                       # 营业利润
        ("TZSY", ctypes.c_float),                       # 投资收益
        ("BTSR", ctypes.c_float),                       # 补贴收入
        ("YYWSZ", ctypes.c_float),                      # 营业外收支
        ("SNSYTZ", ctypes.c_float),                     # 上年损益调整
        ("LRZE", ctypes.c_float),                       # 利润总额
        ("SHLR", ctypes.c_float),                       # 税后利润
        ("JLR", ctypes.c_float),                        # 净利润
        ("WFPLR", ctypes.c_float),                      # 未分配利润
        ("MGWFP", ctypes.c_float),                      # 每股未分配
        ("MGSY", ctypes.c_float),                       # 每股收益
        ("MGJZC", ctypes.c_float),                      # 每股净资产
        ("TZMGJZC", ctypes.c_float),                    # 调整每股净资产
        ("GDQYB", ctypes.c_float),                      # 股东权益比
        ("JZCSYL", ctypes.c_float),                     # 净资收益率
    ]

# 定义 RCV_FENBI_STRUCTEx 结构体
class RCV_FENBI_STRUCTEx(ctypes.Structure):
    _fields_ = [
        ("m_lTime", ctypes.c_long),  # hhmmss 格式时间，如93056表示9:30:56
        ("m_fHigh", ctypes.c_float),  # 最高价
        ("m_fLow", ctypes.c_float),   # 最低价
        ("m_fNewPrice", ctypes.c_float),  # 最新价格
        ("m_fVolume", ctypes.c_float),    # 成交量
        ("m_fAmount", ctypes.c_float),    # 成交额
        ("m_lStroke", ctypes.c_long),  # 保留字段
        ("m_fBuyPrice", ctypes.c_float * 5),  # 申买价1,2,3,4,5
        ("m_fBuyVolume", ctypes.c_float * 5), # 申买量1,2,3,4,5
        ("m_fSellPrice", ctypes.c_float * 5), # 申卖价1,2,3,4,5
        ("m_fSellVolume", ctypes.c_float * 5), # 申卖量1,2,3,4,5
    ]

# 定义 RCV_FENBI 结构体
class RCV_FENBI(ctypes.Structure):
    _fields_ = [
        ("m_wMarket", ctypes.c_ushort),  # 股票市场类型 (WORD)
        ("m_szLabel", ctypes.c_char * STKLABEL_LEN),  # 股票代码，最大长度为 10
        ("m_lDate", ctypes.c_long),     # 分笔数据的日期，格式为时间戳
        ("m_fLastClose", ctypes.c_float),  # 昨收
        ("m_fOpen", ctypes.c_float),       # 今开
        ("m_nCount", ctypes.c_ushort),     # 数据量，分笔的数量
        ("m_Data", ctypes.POINTER(RCV_FENBI_STRUCTEx)),  # 指向分笔数据的指针
    ]

# 定义 DAT_FENBI 结构体
class DAT_FENBI(ctypes.Structure):
    _pack_ = 1  # 内存紧密对齐
    _fields_ = [
        ("m_szLabel", ctypes.c_char * 10),  # 股票代码，最大长度为10
        ("m_wMarket", ctypes.c_ushort),    # 市场类型
        ("m_lDate", ctypes.c_long),        # 日期，时间戳格式
        ("m_fLastClose", ctypes.c_float),  # 昨收
        ("m_fOpen", ctypes.c_float),       # 今开
        ("m_nCount", ctypes.c_ushort),     # 分笔数据数量
        ("formatted_date", ctypes.c_char * 20), # 格式化日期字符串，长度为20
        ("m_fHigh", ctypes.c_float),       # 最高价
        ("m_fLow", ctypes.c_float),        # 最低价
        ("m_fNewPrice", ctypes.c_float),   # 最新价格
        ("m_fVolume", ctypes.c_float),     # 成交量
        ("m_fAmount", ctypes.c_float),     # 成交额

        # 分开申买价和申买量
        ("m_fBuyPrice1", ctypes.c_float),  # 申买价1
        ("m_fBuyPrice2", ctypes.c_float),  # 申买价2
        ("m_fBuyPrice3", ctypes.c_float),  # 申买价3
        ("m_fBuyPrice4", ctypes.c_float),  # 申买价4
        ("m_fBuyPrice5", ctypes.c_float),  # 申买价5

        ("m_fBuyVolume1", ctypes.c_float), # 申买量1
        ("m_fBuyVolume2", ctypes.c_float), # 申买量2
        ("m_fBuyVolume3", ctypes.c_float), # 申买量3
        ("m_fBuyVolume4", ctypes.c_float), # 申买量4
        ("m_fBuyVolume5", ctypes.c_float), # 申买量5

        # 分开申卖价和申卖量
        ("m_fSellPrice1", ctypes.c_float), # 申卖价1
        ("m_fSellPrice2", ctypes.c_float), # 申卖价2
        ("m_fSellPrice3", ctypes.c_float), # 申卖价3
        ("m_fSellPrice4", ctypes.c_float), # 申卖价4
        ("m_fSellPrice5", ctypes.c_float), # 申卖价5

        ("m_fSellVolume1", ctypes.c_float), # 申卖量1
        ("m_fSellVolume2", ctypes.c_float), # 申卖量2
        ("m_fSellVolume3", ctypes.c_float), # 申卖量3
        ("m_fSellVolume4", ctypes.c_float), # 申卖量4
        ("m_fSellVolume5", ctypes.c_float), # 申卖量5
    ]

# 定义 DAT_REPORT 结构体
class DAT_REPORT(ctypes.Structure):
    _pack_ = 1  # 内存紧密对齐
    _fields_ = [
    ("m_cbSize", ctypes.c_uint16),                # 结构大小 (WORD) 2
    ("formatted_date", ctypes.c_char * 20),                    # 成交时间 (time_t) 4
    ("m_wMarket", ctypes.c_uint16),               # 股票市场类型 (WORD) 2
    ("m_szLabel", ctypes.c_char * STKLABEL_LEN), # 股票代码 10
    ("m_szName", ctypes.c_char * STKNAME_LEN),   # 股票名称 32 
    ("m_fLastClose", ctypes.c_float),             # 昨收 4
    ("m_fOpen", ctypes.c_float),                  # 今开 4
    ("m_fHigh", ctypes.c_float),                  # 最高 4
    ("m_fLow", ctypes.c_float),                   # 最低 4
    ("m_fNewPrice", ctypes.c_float),              # 最新 4 
    ("m_fVolume", ctypes.c_float),                # 成交量 4
    ("m_fAmount", ctypes.c_float),                # 成交额 4
    # 拆分申买价
    ("m_fBuyPrice1", ctypes.c_float),            # 申买价1
    ("m_fBuyPrice2", ctypes.c_float),            # 申买价2
    ("m_fBuyPrice3", ctypes.c_float),            # 申买价3
    # 拆分申买量
    ("m_fBuyVolume1", ctypes.c_float),           # 申买量1
    ("m_fBuyVolume2", ctypes.c_float),           # 申买量2
    ("m_fBuyVolume3", ctypes.c_float),           # 申买量3
    # 拆分申卖价
    ("m_fSellPrice1", ctypes.c_float),           # 申卖价1
    ("m_fSellPrice2", ctypes.c_float),           # 申卖价2
    ("m_fSellPrice3", ctypes.c_float),           # 申卖价3
    # 拆分申卖量
    ("m_fSellVolume1", ctypes.c_float),          # 申卖量1
    ("m_fSellVolume2", ctypes.c_float),          # 申卖量2
    ("m_fSellVolume3", ctypes.c_float),          # 申卖量3
    ("m_fBuyPrice4", ctypes.c_float),             # 申买价4 4  
    ("m_fBuyVolume4", ctypes.c_float),            # 申买量4 4
    ("m_fSellPrice4", ctypes.c_float),            # 申卖价4 4
    ("m_fSellVolume4", ctypes.c_float),           # 申卖量4 4
    ("m_fBuyPrice5", ctypes.c_float),             # 申买价5 4
    ("m_fBuyVolume5", ctypes.c_float),            # 申买量5 4
    ("m_fSellPrice5", ctypes.c_float),            # 申卖价5 4
    ("m_fSellVolume5", ctypes.c_float),           # 申卖量5 4
]

# 定义 DAT_POWER_EX 结构体
class DAT_POWER_EX(ctypes.Structure):
    _pack_ = 1  # 内存紧密对齐
    _fields_ = [
    ("m_szLabel", ctypes.c_char * STKLABEL_LEN),  # 股票代码
    ("m_wMarket", ctypes.c_ushort),    # WORD 通常是无符号短整型
    ("formatted_date", ctypes.c_char * 20), # 日期
    ("m_fGive", ctypes.c_float),     # 每股送
    ("m_fPei", ctypes.c_float),      # 每股配
    ("m_fPeiPrice", ctypes.c_float), # 配股价
    ("m_fProfit", ctypes.c_float),    # 每股红利
    ]

class DAT_HLMarketType(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_wMarket", ctypes.c_ushort),                 # 市场代码 2
        ("m_Name", ctypes.c_char * MKTNAME_LEN),       # 市场名称 16
        ("m_lProperty", ctypes.c_ulong),                # 市场属性 4
        ("m_lDate", ctypes.c_ulong),                    # 数据日期 4
        ("m_PeriodCount", ctypes.c_ushort),            # 交易时段个数 2
        ("m_OpenTime", ctypes.c_ushort * 5),           # 开市时间 10
        ("m_CloseTime", ctypes.c_ushort * 5),          # 收市时间 10
        ("m_nCount", ctypes.c_ushort),                  # 该市场的证券个数 2
    ]

class DAT_TABLE_STRUCT(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_szLabel", ctypes.c_char * STKLABEL_LEN),  # 股票代码,以'\0'结尾,如 "500500"
        ("m_szName", ctypes.c_char * STKNAME_LEN),    # 股票名称,以'\0'结尾,"上证指数"
        ("m_cProperty", ctypes.c_ushort),               # 每手股数
    ]
class DAT_FINANCEDATA(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_wMarket", ctypes.c_ushort),                 # 股票市场类型
        ("N1", ctypes.c_ushort),                        # 保留字段
        ("m_szLabel", ctypes.c_char * 10),             # 股票代码
        ("formatted_date", ctypes.c_char * 20),          # 日期
        ("ZGB", ctypes.c_float),                        # 总股本
        ("GJG", ctypes.c_float),                        # 国家股
        ("FQFRG", ctypes.c_float),                      # 发起人法人股
        ("FRG", ctypes.c_float),                        # 法人股
        ("BGS", ctypes.c_float),                        # B股
        ("HGS", ctypes.c_float),                        # H股
        ("MQLT", ctypes.c_float),                       # 目前流通
        ("ZGG", ctypes.c_float),                        # 职工股
        ("A2ZPG", ctypes.c_float),                      # A2转配股
        ("ZZC", ctypes.c_float),                        # 总资产(千元)
        ("LDZC", ctypes.c_float),                       # 流动资产
        ("GDZC", ctypes.c_float),                       # 固定资产
        ("WXZC", ctypes.c_float),                       # 无形资产
        ("CQTZ", ctypes.c_float),                       # 长期投资
        ("LDFZ", ctypes.c_float),                       # 流动负债
        ("CQFZ", ctypes.c_float),                       # 长期负债
        ("ZBGJJ", ctypes.c_float),                      # 资本公积金
        ("MGGJJ", ctypes.c_float),                      # 每股公积金
        ("GDQY", ctypes.c_float),                       # 股东权益
        ("ZYSR", ctypes.c_float),                       # 主营收入
        ("ZYLR", ctypes.c_float),                       # 主营利润
        ("QTLR", ctypes.c_float),                       # 其他利润
        ("YYLR", ctypes.c_float),                       # 营业利润
        ("TZSY", ctypes.c_float),                       # 投资收益
        ("BTSR", ctypes.c_float),                       # 补贴收入
        ("YYWSZ", ctypes.c_float),                      # 营业外收支
        ("SNSYTZ", ctypes.c_float),                     # 上年损益调整
        ("LRZE", ctypes.c_float),                       # 利润总额
        ("SHLR", ctypes.c_float),                       # 税后利润
        ("JLR", ctypes.c_float),                        # 净利润
        ("WFPLR", ctypes.c_float),                      # 未分配利润
        ("MGWFP", ctypes.c_float),                      # 每股未分配
        ("MGSY", ctypes.c_float),                       # 每股收益
        ("MGJZC", ctypes.c_float),                      # 每股净资产
        ("TZMGJZC", ctypes.c_float),                    # 调整每股净资产
        ("GDQYB", ctypes.c_float),                      # 股东权益比
        ("JZCSYL", ctypes.c_float),                     # 净资收益率
    ]

class DAT_MINUTE_EX(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_szLabel", ctypes.c_char * 10),             # 股票代码
        ("m_wMarket", ctypes.c_ushort),                 # 市场代码
        ("formatted_date", ctypes.c_char * 20),          # 日期
        ("m_fPrice", ctypes.c_float),
        ("m_fVolume", ctypes.c_float),
        ("m_fAmount", ctypes.c_float),
    ]

class DAT_5MINUTE_EX(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_szLabel", ctypes.c_char * 10),             # 股票代码
        ("m_wMarket", ctypes.c_ushort),                 # 市场代码
        ("formatted_date", ctypes.c_char * 20),          # 日期
        ("m_fOpen", ctypes.c_float),       # 开盘
        ("m_fHigh", ctypes.c_float),       # 最高
        ("m_fLow", ctypes.c_float),        # 最低
        ("m_fClose", ctypes.c_float),      # 收盘
        ("m_fVolume", ctypes.c_float),     # 量
        ("m_fAmount", ctypes.c_float),     # 额
        ("m_fActiveBuyVol", ctypes.c_float), # 主动买量
    ]
class DAT_DAY_EX(ctypes.Structure):
    _pack_ = 1  # 设置结构体对齐
    _fields_ = [
        ("m_szLabel", ctypes.c_char * 10),             # 股票代码
        ("m_wMarket", ctypes.c_ushort),                 # 市场代码
        ("formatted_date", ctypes.c_char * 20),          # 日期
        ("m_fOpen", ctypes.c_float),
        ("m_fHigh", ctypes.c_float),
        ("m_fLow", ctypes.c_float),
        ("m_fClose", ctypes.c_float),
        ("m_fVolume", ctypes.c_float),
        ("m_fAmount", ctypes.c_float),
        ("m_wAdvance", ctypes.c_ushort),  # WORD 涨数,仅大盘有效
        ("m_wDecline", ctypes.c_ushort),  # WORD 跌数,仅大盘有效
    ]