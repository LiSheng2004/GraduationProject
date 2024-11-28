import winreg as reg  # 用于访问 Windows 注册表
import ctypes
import ctypes
import win32gui
import win32api
from constant import My_Msg_StkData, RCV_WORK_SENDMSG
from constant import *
import os
import csv
from utils import getCurrentTime,setup_logger
import datetime
import pytz
import time


def get_dll_path_from_registry():
    # 打开注册表项
    try:
        # 指定要打开的注册表路径
        reg_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\stockdrv", 0, reg.KEY_READ)

        # 获取指定值 "Driver"
        dll_path, reg_type = reg.QueryValueEx(reg_key, "Driver")

        # 关闭注册表项
        reg.CloseKey(reg_key)
        return dll_path

    except FileNotFoundError:
        print("注册表项或值不存在")
        return None
    except Exception as e:
        print(f"无法从注册表中获取 DLL 路径: {e}")
        return None
def load_dll_from_registry():
    # 获取 DLL 的路径
    dll_path = get_dll_path_from_registry()
    
    if dll_path:
        print(f"从注册表中获取的 DLL 路径: {dll_path}")
        
        try:
            # 使用 ctypes 加载 DLL
            dll = ctypes.CDLL(dll_path)
            print(f"DLL 加载成功: {dll}")
            return dll
        except OSError as e:
            print(f"无法加载 DLL: {e}")
            return None
    else:
        print("无法加载 DLL，因为没有找到有效的路径")
        return None
# dll_loader.py
# 加载 DLL 并定义接口
dll = load_dll_from_registry()
# 规定Stock_Init的传入参数和返回值的类型
dll.Stock_Init.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int]
dll.Stock_Init.restype = ctypes.c_int

timestamp = time.time()
# 获取本地时间
local_time = time.localtime(timestamp)
folder_time = local_time
folder_name = time.strftime("%Y%m%d_%H%M%S", folder_time)

# 定义中国时区
china_timezone = pytz.timezone('Asia/Shanghai')
# 加载日志模块
logger = setup_logger()
index = 0
def wnd_proc(hwnd, msg, wparam, lparam): # 参数：窗口，返回消息，消息类型，消息指针
    # print(f"Received message: {msg}")
    if msg == My_Msg_StkData: # 通过验证msg确定是否是dll发送的数据
        wFileType = wparam # 消息的类型
        lPara = lparam # 消息的指针
        pHeader = ctypes.cast(lPara, ctypes.POINTER(RCV_DATA)) # 用事先定义好的结构体进行指针的转换
        global index
        index = index + 1
        # 获取当前时间
        now = time.time()
        now_time = time.localtime(now)
        # 提取日期部分
        day_time = time.strftime("%Y%m%d", now_time)
        # 获取当前小时
        current_hour = now_time.tm_hour
        # 记录文件夹路径
        folder_path = f'./data/{folder_name}/{day_time}/{current_hour}'
        # 检查文件夹是否存在，如果不存在则创建
        if not os.path.exists(folder_path):
            # index = 0
            os.makedirs(folder_path)
        if wFileType == RCV_REPORT:
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.info(f"{cuurent_time}  接收到RCV_REPORT-流水号：{index}")
            # 初始化行情以及交易日的实时行情都是在这个地方接收
            nBufSize = pHeader.contents.data_union.m_pReportV3[0].m_cbSize # 结构大小
            pBaseBuf = ctypes.cast(pHeader.contents.data_union.m_pReportV3, ctypes.POINTER(RCV_REPORT_STRUCTExV3))
            # 定义目标文件路径
            output_file = f'{folder_path}/{index}补报告数据{cuurent_time.replace(":", "-")}.csv'
            # 初始化数据列表，批量写入的批次大小
            data_list = []
            batch_size = 500  # 每次写入500条数据，批量写入以提高效率
            # 检查文件是否存在
            file_exists = os.path.isfile(output_file)
            # 打开文件，准备写入
            with open(output_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writerow([
                        "结构大小", "成交时间", "股票市场类型", "股票代码", "股票名称", "昨收", "今开", "最高", "最低", "最新", 
                        "成交量", "成交额", "申买价1", "申买价2", "申买价3", "申买量1", "申买量2", "申买量3", 
                        "申卖价1", "申卖价2", "申卖价3", "申卖量1", "申卖量2", "申卖量3", 
                        "申买价4", "申买量4", "申卖价4", "申卖量4", 
                        "申买价5", "申买量5", "申卖价5", "申卖量5"
                    ])
                # print("RCV_REPORT")
                for i in range(pHeader.contents.m_nPacketNum): # 记录数
                    # 获取当前报文的内容
                    Buf = pBaseBuf[i]  # 直接访问数组中的元素
                    time_ = Buf.m_time
                    dt = datetime.datetime.fromtimestamp(time_, tz=datetime.timezone.utc)
                    # 将 UTC 时间转换为中国时区时间
                    china_time = dt.astimezone(china_timezone)
                    # 格式化为字符串（可以根据需要调整格式）
                    formatted_date = china_time.strftime('%Y-%m-%d %H:%M:%S')
                    # 添加数据到 data_list
                    data_list.append([
                        Buf.m_cbSize, formatted_date, Buf.m_wMarket, 
                        Buf.m_szLabel.decode('ascii'), Buf.m_szName.decode('gbk'), 
                        Buf.m_fLastClose, Buf.m_fOpen, Buf.m_fHigh, Buf.m_fLow, Buf.m_fNewPrice,
                        Buf.m_fVolume, Buf.m_fAmount,
                        Buf.m_fBuyPrice[0], Buf.m_fBuyPrice[1], Buf.m_fBuyPrice[2],
                        Buf.m_fBuyVolume[0], Buf.m_fBuyVolume[1], Buf.m_fBuyVolume[2],
                        Buf.m_fSellPrice[0], Buf.m_fSellPrice[1], Buf.m_fSellPrice[2],
                        Buf.m_fSellVolume[0], Buf.m_fSellVolume[1], Buf.m_fSellVolume[2],
                        Buf.m_fBuyPrice4, Buf.m_fBuyVolume4,
                        Buf.m_fSellPrice4, Buf.m_fSellVolume4,
                        Buf.m_fBuyPrice5, Buf.m_fBuyVolume5,
                        Buf.m_fSellPrice5, Buf.m_fSellVolume5
                    ])
                    # 每到批次大小时，写入并清空缓存
                    if len(data_list) >= batch_size:
                        writer.writerows(data_list)
                        data_list.clear()  # 清空列表准备下一个批次
                # 写入最后一批数据
                if data_list:
                    writer.writerows(data_list)
        elif wFileType == RCV_FENBIDATA: # 分笔数据
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.info(f"{cuurent_time}  接收到RCV_FENBIDATA-流水号：{index}")
            output_file = f'{folder_path}/{index}分笔数据{cuurent_time.replace(":", "-")}.csv'
            # 初始化数据列表和批量写入大小
            data_list = []
            batch_size = 500  # 每次写入500条数据
            # 检查文件是否存在，决定是否写入表头
            file_exists = os.path.isfile(output_file)
            # 打开文件，准备写入
            with open(output_file, mode='a', newline='') as file:
                writer = csv.writer(file)
                # 如果文件不存在，写入表头
                if not file_exists:
                    writer.writerow([
                        "股票代码", "市场类型","时间",'昨收' ,'今开','数据量',"开盘", "最高", "最低",'收盘','交易量','交易额','涨数','跌数'
                    ])
                    # 将 lPara 转换为 RCV_FENBI 类型的对象
                    pFenBi = ctypes.cast(lPara, ctypes.POINTER(RCV_FENBI)).contents
                    for i in range(pFenBi.m_nCount):
                        fenbi_data_offset = 30 + ctypes.sizeof(RCV_FENBI_STRUCTEx) * i
                        pFenBiData = ctypes.cast(lPara + fenbi_data_offset, ctypes.POINTER(RCV_FENBI_STRUCTEx)).contents
                        time_ = pFenBiData.m_lTime
                        dt = datetime.datetime.fromtimestamp(time_, tz=datetime.timezone.utc)
                        # 格式化为字符串（可以根据需要调整格式）
                        china_time = dt.astimezone(china_timezone)
                        # 格式化为字符串（可以根据需要调整格式）
                        formatted_date = china_time.strftime('%Y-%m-%d %H:%M:%S')
                        data_list.append([
                                        pFenBi.m_szLabel.decode('ascii'),  # 股票代码
                                        pFenBi.m_wMarket,                  # 市场类型
                                        pFenBi.m_lDate,                    # 日期
                                        pFenBi.m_fLastClose,               # 昨收
                                        pFenBi.m_fOpen,                    # 今开
                                        pFenBi.m_nCount,                   # 分笔数据数量
                                        formatted_date,                    # 格式化后的时间
                                        pFenBiData.m_fHigh,                # 最高价
                                        pFenBiData.m_fLow,                 # 最低价
                                        pFenBiData.m_fNewPrice,            # 最新价格
                                        pFenBiData.m_fVolume,              # 成交量
                                        pFenBiData.m_fAmount,              # 成交额
                                        pFenBiData.m_fBuyPrice,            # 申买价
                                        pFenBiData.m_fBuyVolume,           # 申买量
                                        pFenBiData.m_fSellPrice,           # 申卖价
                                        pFenBiData.m_fSellVolume           # 申卖量
                                    ])
                        # 每写入 batch_size 条数据就清空列表，写入文件
                        if len(data_list) >= batch_size:
                            writer.writerows(data_list)
                            data_list.clear()  # 清空列表准备下一个批次
                # 写入剩余的数据（如果有）
                if data_list:
                    writer.writerows(data_list)
        elif wFileType == RCV_FILEDATA:
            cuurent_time = getCurrentTime() # 获取目前时间
            if not pHeader.contents.data_union.m_pData or pHeader.contents.m_wDataType == FILE_TYPE_RES:
                logger.error(f"{cuurent_time}  接收到无效RCV_FILEDATA数据")
                return 0
            wDataType = pHeader.contents.m_wDataType # 判断文件类型，用来判断是补分时还是日线等等
            # print(wDataType)
            if wDataType == FILE_HISTORY_EX:  # 补日线数据
                logger.info(f"{cuurent_time}  接收到RCV_FILEDATA的日线数据-流水号：{index}")
                output_file = f'{folder_path}/{index}补日线数据{cuurent_time.replace(":", "-")}.csv'
                # 初始化数据列表和批量写入大小
                data_list = []
                batch_size = 500  # 每次写入500条数据
                # 检查文件是否存在，决定是否写入表头
                file_exists = os.path.isfile(output_file)
                # 打开文件，准备写入
                with open(output_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    # 如果文件不存在，写入表头
                    if not file_exists:
                        writer.writerow([
                            "股票代码", "市场类型","时间", "开盘", "最高", "最低",'收盘','交易量','交易额','涨数','跌数'
                        ])
                    pDay = pHeader.contents.data_union.m_pDay
                    for i in range(pHeader.contents.m_nPacketNum):
                        if pDay[i].m_head.m_dwHeadTag == EKE_HEAD_TAG:
                            # 文件头部分，获取股票代码
                            label = pDay[i].m_head.m_szLabel.decode('ascii')
                            market = pDay[i].m_head.m_wMarket
                        else:
                            # 具体 K 线数据
                            time_ = pDay[i].m_time
                            # 转换为 UTC 时间，显式指定时区为 UTC
                            dt = datetime.datetime.fromtimestamp(time_, tz=datetime.timezone.utc)
                            china_time = dt.astimezone(china_timezone)
                            # 格式化为字符串（可以根据需要调整格式）
                            formatted_date = china_time.strftime('%Y-%m-%d %H:%M:%S')
                            open_price = pDay[i].m_fOpen
                            high_price = pDay[i].m_fHigh
                            low_price = pDay[i].m_fLow
                            close_price = pDay[i].m_fClose
                            vol = pDay[i].m_fVolume
                            amount = pDay[i].m_fAmount
                            advance = pDay[i].m_wAdvance
                            m_wDecline = pDay[i].m_wDecline
                            data_list.append([label,market,formatted_date,open_price,high_price,low_price,close_price,vol,amount,advance,m_wDecline])
                        if len(data_list) >= batch_size:
                            writer.writerows(data_list)
                            data_list.clear()  # 清空列表准备下一个批次
                    if data_list:
                        writer.writerows(data_list)
            elif wDataType == FILE_5MINUTE_EX:  # 补五分钟线数据
                logger.info(f"{cuurent_time}  接收到RCV_FILEDATA的五分钟数据-流水号：{index}")
                # 定义输出文件路径
                output_file = f'{folder_path}/{index}补五分钟数据{cuurent_time.replace(":", "-")}.csv'
                # 初始化数据列表和批量写入大小
                data_list = []
                batch_size = 500  # 每次写入500条数据
                # 检查文件是否存在，决定是否写入表头
                file_exists = os.path.isfile(output_file)
                # 打开文件，准备写入
                with open(output_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    # 如果文件不存在，写入表头
                    if not file_exists:
                        writer.writerow([
                            "股票代码", "市场类型","时间", "开盘", "最高", "最低",'收盘','交易量','交易额','主动买量'
                        ])
                    p5Min = pHeader.contents.data_union.m_p5Min
                    for i in range(pHeader.contents.m_nPacketNum):
                        if p5Min[i].m_head.m_dwHeadTag == EKE_HEAD_TAG:
                            # 文件头部分，获取股票代码
                            label = p5Min[i].m_head.m_szLabel.decode('ascii')
                            market = p5Min[i].m_head.m_wMarket
                        else:
                            time_ = p5Min[i].m_time
                            # 转换为 UTC 时间，显式指定时区为 UTC
                            dt = datetime.datetime.fromtimestamp(time_, tz=datetime.timezone.utc)
                            # 格式化为字符串（可以根据需要调整格式）
                            china_time = dt.astimezone(china_timezone)
                            # 格式化为字符串（可以根据需要调整格式）
                            formatted_date = china_time.strftime('%Y-%m-%d %H:%M:%S')
                            open_price = p5Min[i].m_fOpen
                            high_price = p5Min[i].m_fHigh
                            low_price = p5Min[i].m_fLow
                            close_price = p5Min[i].m_fClose
                            vol = p5Min[i].m_fVolume
                            amount = p5Min[i].m_fAmount 
                            activeBuyVol = p5Min[i].m_fActiveBuyVol 
                            data_list.append([label,market,formatted_date,open_price,high_price,low_price,close_price,vol,amount,activeBuyVol])
                        if len(data_list) >= batch_size:
                            writer.writerows(data_list)
                            data_list.clear()  # 清空列表准备下一个批次
                    if data_list:
                        writer.writerows(data_list)
            elif wDataType == FILE_MINUTE_EX:  # 分钟线数据，即分时数据
                logger.info(f"{cuurent_time}  接收到RCV_FILEDATA的分时数据-流水号：{index}")
                # 定义输出文件路径
                output_file = f'{folder_path}/{index}补分时数据{cuurent_time.replace(":", "-")}.csv'
                # 初始化数据列表和批量写入大小
                data_list = []
                batch_size = 500  # 每次写入500条数据
                # 检查文件是否存在，决定是否写入表头
                file_exists = os.path.isfile(output_file)
                # 打开文件，准备写入
                with open(output_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    # 如果文件不存在，写入表头
                    if not file_exists:
                        writer.writerow([
                            "股票代码", "市场类型","时间", "最新价", "成交量", "成交金额"
                        ])
                    pMin = pHeader.contents.data_union.m_pMinute # 拿到数据
                    for i in range(pHeader.contents.m_nPacketNum):
                        if pMin[i].m_head.m_dwHeadTag == EKE_HEAD_TAG:
                            label = pMin[i].m_head.m_szLabel.decode('ascii')
                            market = pMin[i].m_head.m_wMarket
                        else:
                            time_ = pMin[i].m_time
                            # 转换为 UTC 时间，显式指定时区为 UTC
                            dt = datetime.datetime.fromtimestamp(time_, tz=datetime.timezone.utc)
                            china_time = dt.astimezone(china_timezone)
                            # 格式化为字符串（可以根据需要调整格式）
                            formatted_date = china_time.strftime('%Y-%m-%d %H:%M:%S')
                            price = pMin[i].m_fPrice
                            vol = pMin[i].m_fVolume
                            amount = pMin[i].m_fAmount
                            data_list.append([label,market,formatted_date,price,vol,amount])
                        if len(data_list) >= batch_size:
                            writer.writerows(data_list)
                            data_list.clear()  # 清空列表准备下一个批次
                    if data_list:
                        writer.writerows(data_list)
                            
            elif wDataType == FILE_POWER_EX:  # 除权数据
                logger.info(f"{cuurent_time}  接收到RCV_FILEDATA的除权数据-流水号：{index}")
                m_PowerData = {
                    "Power_Count": pHeader.contents.m_nPacketNum,
                    "m_RcvPower": pHeader.contents.data_union.m_pPower
                }
            elif wDataType == FILE_BASE_EX:  # 基本资料文件
                logger.info(f"{cuurent_time}  接收到基本资料数据-流水号：{index}")
                m_FileLong = pHeader.contents.m_File.m_dwLen
                m_FileName = f'{folder_path}/基本资料/{index}_'+pHeader.contents.m_File.m_szFileName.decode('utf-8')
                # 如果目录不存在，则创建它
                if not os.path.exists(os.path.dirname(m_FileName)):
                    os.makedirs(os.path.dirname(m_FileName))
                with open(m_FileName, "wb") as fp:
                    fp.write(ctypes.string_at(pHeader.contents.data_union.m_pData, m_FileLong))
            elif wDataType == FILE_NEWS_EX:  # 新闻类
                logger.info(f"{cuurent_time}  接收到新闻数据-流水号：{index}")
                m_File = f"公告消息: {pHeader.contents.m_File.m_szFileName.decode('utf-8')}"

            else:
                logger.error(f"{cuurent_time}  接收到无效RCV_FILEDATA数据")
        elif wFileType == RCV_MKTTBLDATA: # 市场类型数据的接收
            pMarketTableHead = ctypes.cast(lPara, ctypes.POINTER(HLMarketType)).contents
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.info(f"{cuurent_time}  接收到RCV_MKTTBLDATA-流水号：{index}")
            # 定义文件路径
            output_file = f'{folder_path}/{index}市场类型数据{cuurent_time.replace(":", "-")}.csv'
            # 检查文件是否存在
            file_exists = os.path.isfile(output_file)
            # 将数据写入 CSV 文件
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # 如果文件不存在，写入标题行
                if not file_exists:
                    writer.writerow([
                        "市场代码", "市场名称", "市场属性", "数据日期", 
                        "交易时段个数", "开市时间", "收市时间", "证券个数"
                    ])
                # 写入数据行
                writer.writerow([
                    pMarketTableHead.m_wMarket,
                    list(pMarketTableHead.m_Name),
                    pMarketTableHead.m_lProperty,
                    pMarketTableHead.m_lDate,
                    pMarketTableHead.m_PeriodCount,
                    list(pMarketTableHead.m_OpenTime),
                    list(pMarketTableHead.m_CloseTime),
                    pMarketTableHead.m_nCount,
                ])
            # 遍历市场代码表的每个记录
            for i in range(pMarketTableHead.m_nCount):
                # 计算 RCV_TABLE_STRUCT 的位置
                offset = 54 + ctypes.sizeof(RCV_TABLE_STRUCT) * i
                Buf = ctypes.cast(lPara + offset, ctypes.POINTER(RCV_TABLE_STRUCT)).contents
                # 定义文件路径
                output_file = f'{folder_path}/{index}证券类型数据{cuurent_time.replace(":", "-")}.csv'
                # 检查文件是否存在
                file_exists = os.path.isfile(output_file)
                # 将数据写入 CSV 文件
                with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # 如果文件不存在，写入标题行
                    if not file_exists:
                        writer.writerow([
                            '股票代码','股票名称',"每股手数"
                        ])
                    # 写入数据行
                    writer.writerow([
                        Buf.m_szLabel.decode('ascii'),
                        Buf.m_szName.decode('gbk'),
                        Buf.m_cProperty                 
                    ])
            
        elif wFileType == RCV_FINANCEDATA:
            
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.info(f"{cuurent_time}  接收到RCV_FINANCEDATA-流水号：{index}")
            # 定义目标文件路径
            output_file = f'{folder_path}/{index}金融类型数据{cuurent_time.replace(":", "-")}.csv'

            # 初始化数据列表，批量写入的批次大小
            data_list = []
            batch_size = 500  # 每次写入500条数据，批量写入以提高效率

            # 检查文件是否存在
            file_exists = os.path.isfile(output_file)
            for i in range(pHeader.contents.m_nPacketNum):
                # 计算偏移量并获取每条记录的指针
                offset = ctypes.cast(pHeader.contents.data_union.m_pData, ctypes.c_void_p).value + 166 * i
                Buf = ctypes.cast(offset, ctypes.POINTER(Fin_LJF_STRUCTEx)).contents
                # 将财务数据的日期转化为UTC时间
                dt = datetime.datetime.fromtimestamp(Buf.BGRQ, tz=datetime.timezone.utc)
                # 格式化为字符串（可以根据需要调整格式）
                china_time = dt.astimezone(china_timezone)
                # 格式化为字符串（可以根据需要调整格式）
                formatted_date = china_time.strftime('%Y-%m-%d %H:%M:%S')
                # 提取 Buf 中的数据并添加到 data_list
                data_list.append([
                    Buf.m_wMarket, Buf.N1, Buf.m_szLabel.decode('ascii'), formatted_date, Buf.ZGB, 
                    Buf.GJG, Buf.FQFRG, Buf.FRG, Buf.BGS, Buf.HGS, Buf.MQLT, Buf.ZGG, Buf.A2ZPG,
                    Buf.ZZC, Buf.LDZC, Buf.GDZC, Buf.WXZC, Buf.CQTZ, Buf.LDFZ, Buf.CQFZ,
                    Buf.ZBGJJ, Buf.MGGJJ, Buf.GDQY, Buf.ZYSR, Buf.ZYLR, Buf.QTLR, Buf.YYLR,
                    Buf.TZSY, Buf.BTSR, Buf.YYWSZ, Buf.SNSYTZ, Buf.LRZE, Buf.SHLR, Buf.JLR,
                    Buf.WFPLR, Buf.MGWFP, Buf.MGSY, Buf.MGJZC, Buf.TZMGJZC, Buf.GDQYB, Buf.JZCSYL
                ])

                # 每到达批次大小，写入一次并清空 data_list
                if len(data_list) >= batch_size:
                    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        # 如果是第一次写入文件，添加标题行
                        if not file_exists:
                            writer.writerow([
                                "股票市场类型", "保留字段", "股票代码", "财务数据的日期", "总股本", "国家股", "发起人法人股",
                                "法人股", "B股", "H股", "目前流通", "职工股", "A2转配股", "总资产(千元)", "流动资产",
                                "固定资产", "无形资产", "长期投资", "流动负债", "长期负债", "资本公积金", "每股公积金",
                                "股东权益", "主营收入", "主营利润", "其他利润", "营业利润", "投资收益", "补贴收入",
                                "营业外收支", "上年损益调整", "利润总额", "税后利润", "净利润", "未分配利润", "每股未分配",
                                "每股收益", "每股净资产", "调整每股净资产", "股东权益比", "净资收益率"
                            ])
                            file_exists = True  # 标记标题已写入
                        
                        writer.writerows(data_list)  # 批量写入数据
                        data_list = []  # 清空数据列表
            # 检查是否有剩余数据未写入
            if data_list:
                with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(data_list)  # 写入剩余的数据
        else:
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.error(f"{cuurent_time}  接收到无效类型数据")
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    return 0
    
# 创建和注册窗口
def create_window():
    wc = win32gui.WNDCLASS() # 实例化一个窗口实例
    wc.lpfnWndProc = wnd_proc # Long Pointer to Function Window Procedure 指定窗口处理函数
    wc.hInstance = win32api.GetModuleHandle(None) # Instance Handlewin32api.GetModuleHandle(None) 会返回当前运行模块的句柄。如果 None 被传入，则获取的是当前程序的实例句柄。
    wc.lpszClassName = "MyPythonWndClass" # 设立窗口类名
    win32gui.RegisterClass(wc) # 注册窗口，让windows系统知道类的存在
    hwnd = win32gui.CreateWindow(
        wc.lpszClassName,         # 类名，用于与前面注册的类关联
        "MyPythonWindow",          # 窗口标题
        0,                         # 窗口样式，0 表示窗口样式默认为无
        0, 0,                      # 窗口位置（x, y）
        0, 0,                      # 窗口大小（宽, 高）
        0,                         # 父窗口句柄，0 表示没有父窗口
        0,                         # 菜单句柄，0 表示无菜单
        wc.hInstance,              # 应用程序实例句柄
        None                       # 窗口创建数据，这里设为 None
    )
    return hwnd # 返回窗口句柄，操作窗口的唯一标识

# 初始化 DLL
def initialize_dll():
    # 创建窗口获取句柄
    hwnd = create_window()
    ok = dll.Stock_Init(hwnd, My_Msg_StkData, RCV_WORK_SENDMSG)
    if ok > 0:
        print("Stock_Init initialized successfully.")
        # 创建文件夹
        if not os.path.exists(f'./data/{folder_name}'):
            os.makedirs(f'./data/{folder_name}', exist_ok=True)
        # 创建log文件夹
        os.makedirs(f'./logs/', exist_ok=True)
        return True
    else:
        print("Stock_Init initialization failed.")
        return False

# 加载成功后启动消息循环
def run_message_loop():
    if initialize_dll(): # 初始化dll
        win32gui.PumpMessages() # 等待消息
