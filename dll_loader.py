import winreg as reg  # 用于访问 Windows 注册表
import ctypes
import win32gui
import win32api
from constant import My_Msg_StkData, RCV_WORK_SENDMSG, ROOT_PATH
from constant import *
import os
import csv
from utils import getCurrentTime,setup_logger,getCurrentTime_withDay
import datetime
import pytz
import time
import pickle
import gzip
from generate_func import *
import threading
from extended_api import init_dll_functions
from ctypes import wintypes

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
# 初始化dll函数参数
dll = init_dll_functions(dll)
# 获取当前时间戳
timestamp = time.time()
# 获取本地时间
local_time = time.localtime(timestamp)
folder_time = local_time
folder_name = time.strftime("%Y%m%d_%H%M%S", folder_time)

# 定义中国时区
china_timezone = pytz.timezone('Asia/Shanghai')
# 加载日志模块
logger = None
index = 0
# 初始化全局变量，上一次收到消息时间
last_message_time = time.time()
# 定时器 ID 和时间间隔（3秒）
TIMER_ID = 1
TIMER_INTERVAL = 3000  # 毫秒
def wnd_proc(hwnd, msg, wparam, lparam): # 参数：窗口，返回消息，消息类型，消息指针
    global last_message_time
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
        current_hour = f"{now_time.tm_hour:02d}"
        # 判断是不是新的一天，新的一天要创建新的文件夹，流水号清零，重新加载logger
        day_path = f'{ROOT_PATH}/{folder_name}/{day_time}'
        if not os.path.exists(day_path):
            index = 0
            os.makedirs(day_path)
            # 加载logger
            log_name = time.strftime('%Y%m%d-%H%M%S', now_time)
            global logger
            logger = setup_logger(f'{day_path}/log{log_name}.txt',logger_name=f'{day_path}/log{log_name}') # 创建logger
        # 判断是不是新的一个小时，如果是新的一个小时，创建一个新的csv文件夹和raw文件夹,raw文件夹中以二进制的形式来保存数据
        folder_path_csv = f'{day_path}/{current_hour}csv'
        # 检查文件夹是否存在，如果不存在则创建
        if not os.path.exists(folder_path_csv):
            os.makedirs(folder_path_csv)
        folder_path_raw = f'{day_path}/{current_hour}raw'
        # 检查文件夹是否存在，如果不存在则创建
        if not os.path.exists(folder_path_raw):
            os.makedirs(folder_path_raw)
        if wFileType == RCV_REPORT:
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.info(f"{day_time} {cuurent_time}  接收到RCV_REPORT-流水号：{index}")
            # 初始化行情以及交易日的实时行情都是在这个地方接收
            nBufSize = pHeader.contents.data_union.m_pReportV3[0].m_cbSize # 结构大小
            pBaseBuf = ctypes.cast(pHeader.contents.data_union.m_pReportV3, ctypes.POINTER(RCV_REPORT_STRUCTExV3))
            # 定义目标文件路径
            output_file = f'{folder_path_csv}/{index}补报告数据{cuurent_time.replace(":", "")}.csv'
            dat_file = f'{folder_path_raw}/{index}补报告数据{cuurent_time.replace(":", "")}.dat'
            # 初始化数据列表，批量写入的批次大小
            csv_list = []
            batch_size = 500  # 每次写入500条数据，批量写入以提高效率
            # 检查文件是否存在
            file_exists = os.path.isfile(output_file)
            # 先获取该结构体的大小
            struct_size = ctypes.sizeof(DAT_REPORT)
            # 打开文件，准备写入
            with open(output_file, mode='a', newline='') as file:
                with open(dat_file, "wb") as f:
                    writer = csv.writer(file)
                    # 如果文件不存在，写入表头
                    if not file_exists:
                        writer.writerow(csv_RCV_REPORT)
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
                        data = generate_data_RCV_REPORT(Buf,formatted_date)
                        dat_data = generate_dat_data_RCV_REPORT(data)
                        # 将dat_data写入二进制文件
                        dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                        f.write(dat_data)
                        # 添加数据到 csv_list
                        csv_list.append(data)
                        # 每到批次大小时，写入并清空缓存
                        if len(csv_list) >= batch_size:
                            writer.writerows(csv_list)
                            csv_list.clear()  # 清空列表准备下一个批次
                    # 写入最后一批数据
                    if csv_list:
                        writer.writerows(csv_list)
                        csv_list.clear()  # 清空列表准备下一个批次
        elif wFileType == RCV_FENBIDATA: # 分笔数据
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.info(f"{day_time} {cuurent_time}  接收到RCV_FENBIDATA-流水号：{index}")
            output_file = f'{folder_path_csv}/{index}分笔数据{cuurent_time.replace(":", "")}.csv'
            dat_file = f'{folder_path_raw}/{index}分笔数据{cuurent_time.replace(":", "")}.dat'
            # 初始化数据列表和批量写入大小
            csv_list = []
            batch_size = 500  # 每次写入500条数据
            # 检查文件是否存在，决定是否写入表头
            file_exists = os.path.isfile(output_file)
            struct_size = ctypes.sizeof(DAT_FENBI)
            # 打开文件，准备写入
            with open(output_file, mode='a', newline='') as file:
                with open(dat_file, "wb") as f:
                    writer = csv.writer(file)
                    # 如果文件不存在，写入表头
                    if not file_exists:
                        writer.writerow(csv_RCV_FENBI)
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
                            # 生成存入csv的数据
                            data = generate_data_RCV_FENBIDATA(pFenBi,formatted_date,pFenBiData)
                            # 根据数据生成一条dat_data
                            dat_data = generate_dat_data_RCV_FENBIDATA(data)
                            # 将dat_data写入二进制文件
                            dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                            f.write(dat_data)
                            csv_list.append(data)
                            # 每写入 batch_size 条数据就清空列表，写入文件
                            if len(csv_list) >= batch_size:
                                writer.writerows(csv_list)
                                csv_list.clear()  # 清空列表准备下一个批次
                    # 写入剩余的数据（如果有）
                    if csv_list:
                        writer.writerows(csv_list)
                        csv_list.clear()  # 清空列表准备下一个批次
        elif wFileType == RCV_FILEDATA:
            cuurent_time = getCurrentTime() # 获取目前时间
            if not pHeader.contents.data_union.m_pData or pHeader.contents.m_wDataType == FILE_TYPE_RES:
                logger.error(f"{day_time} {cuurent_time}  接收到无效RCV_FILEDATA数据")
                return 0
            wDataType = pHeader.contents.m_wDataType # 判断文件类型，用来判断是补分时还是日线等等
            # print(wDataType)
            if wDataType == FILE_HISTORY_EX:  # 补日线数据
                logger.info(f"{day_time} {cuurent_time}  接收到RCV_FILEDATA的日线数据-流水号：{index}")
                output_file = f'{folder_path_csv}/{index}补日线数据{cuurent_time.replace(":", "")}.csv'
                dat_file = f'{folder_path_raw}/{index}补日线数据{cuurent_time.replace(":", "")}.dat'
                struct_size = ctypes.sizeof(DAT_DAY_EX)   
                # 初始化数据列表和批量写入大小
                csv_list = []
                raw_list = []
                batch_size = 500  # 每次写入500条数据
                # 检查文件是否存在，决定是否写入表头
                file_exists = os.path.isfile(output_file)
                # 打开文件，准备写入
                with open(output_file, mode='a', newline='') as file:
                    with open(dat_file, "wb") as f:
                        writer = csv.writer(file)
                        # 如果文件不存在，写入表头
                        if not file_exists:
                            writer.writerow(csv_DAY_EX)
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
                                data = generate_data_DAY_EX(label,market, formatted_date,pDay[i])
                                dat_data = generate_dat_data_DAY_EX(data)
                                dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                                f.write(dat_data)
                                csv_list.append(data)
                            if len(csv_list) >= batch_size:
                                writer.writerows(csv_list)
                                csv_list.clear()  # 清空列表准备下一个批次
                        if csv_list:
                            writer.writerows(csv_list)
                            csv_list.clear()  # 清空列表准备下一个批次
            elif wDataType == FILE_5MINUTE_EX:  # 补五分钟线数据
                logger.info(f"{day_time} {cuurent_time}  接收到RCV_FILEDATA的五分钟数据-流水号：{index}")
                # 定义输出文件路径
                output_file = f'{folder_path_csv}/{index}补五分钟数据{cuurent_time.replace(":", "")}.csv'
                dat_file = f'{folder_path_raw}/{index}补五分钟数据{cuurent_time.replace(":", "")}.dat'
                struct_size = ctypes.sizeof(DAT_5MINUTE_EX)
                # 初始化数据列表和批量写入大小
                csv_list = []
                raw_list = []
                batch_size = 500  # 每次写入500条数据
                # 检查文件是否存在，决定是否写入表头
                file_exists = os.path.isfile(output_file)
                # 打开文件，准备写入
                with open(output_file, mode='a', newline='') as file:
                    with open(dat_file, "wb") as f:
                        writer = csv.writer(file)
                        # 如果文件不存在，写入表头
                        if not file_exists:
                            writer.writerow(csv_5MIN_EX)
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
                                data = generate_data_5MINUTE_EX(label, market, formatted_date,p5Min[i])
                                dat_data = generate_dat_data_5MINUTE_EX(data)
                                csv_list.append(data)
                                dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                                f.write(dat_data)
                            if len(csv_list) >= batch_size:
                                writer.writerows(csv_list)
                                csv_list.clear()  # 清空列表准备下一个批次
                        if csv_list:
                            writer.writerows(csv_list)
                            csv_list.clear()  # 清空列表准备下一个批次
            elif wDataType == FILE_MINUTE_EX:  # 分钟线数据，即分时数据
                logger.info(f"{day_time} {cuurent_time}  接收到RCV_FILEDATA的分时数据-流水号：{index}")
                # 定义输出文件路径
                output_file = f'{folder_path_csv}/{index}补分时数据{cuurent_time.replace(":", "")}.csv'
                dat_file = f'{folder_path_raw}/{index}补分时数据{cuurent_time.replace(":", "")}.dat'
                struct_size = ctypes.sizeof(DAT_MINUTE_EX)
                # 初始化数据列表和批量写入大小
                csv_list = []
                batch_size = 500  # 每次写入500条数据
                # 检查文件是否存在，决定是否写入表头
                file_exists = os.path.isfile(output_file)
                # 打开文件，准备写入
                with open(output_file, mode='a', newline='') as file:
                    with open(dat_file, "wb") as f:
                        writer = csv.writer(file)
                        # 如果文件不存在，写入表头
                        if not file_exists:
                            writer.writerow(csv_MINUTES_EX)
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
                                data = generate_data_MINUTE_EX(label, market, formatted_date,pMin[i])
                                csv_list.append(data)
                                dat_data = generate_dat_data_MINUTE_EX(data)
                                dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                                f.write(dat_data)
                            if len(csv_list) >= batch_size:
                                writer.writerows(csv_list)
                                csv_list.clear()  # 清空列表准备下一个批次
                        if csv_list:
                            writer.writerows(csv_list)
                            csv_list.clear()  # 清空列表准备下一个批次
                            
            elif wDataType == FILE_POWER_EX:  # 除权数据
                logger.info(f"{day_time} {cuurent_time}  接收到FILE_POWER_EX的除权数据-流水号：{index}")
                output_file = f'{folder_path_csv}/{index}补除权数据{cuurent_time.replace(":", "")}.csv'
                dat_file = f'{folder_path_raw}/{index}补除权数据{cuurent_time.replace(":", "")}.dat'
                # 初始化数据列表和批量写入大小
                csv_list = []
                raw_list = []
                batch_size = 500  # 每次写入500条数据
                # 检查文件是否存在，决定是否写入表头
                file_exists = os.path.isfile(output_file)
                struct_size = ctypes.sizeof(DAT_POWER_EX)
                # 打开文件，准备写入
                with open(output_file, mode='a', newline='') as file:
                    with open(dat_file, "wb") as f:
                        writer = csv.writer(file)
                        # 如果文件不存在，写入表头
                        if not file_exists:
                            writer.writerow(csv_RCV_POWER_EX)
                        pPower = pHeader.contents.data_union.m_pPower
                        for i in range(pHeader.contents.m_nPacketNum):
                            if pPower[i].m_head.m_dwHeadTag == EKE_HEAD_TAG:
                                # 文件头部分，获取股票代码
                                label = pPower[i].m_head.m_szLabel.decode('ascii')
                                market = pPower[i].m_head.m_wMarket
                            else:
                                # 具体 K 线数据
                                time_ = pPower[i].m_time
                                # 转换为 UTC 时间，显式指定时区为 UTC
                                dt = datetime.datetime.fromtimestamp(time_, tz=datetime.timezone.utc)
                                china_time = dt.astimezone(china_timezone)
                                # 格式化为字符串（可以根据需要调整格式）
                                formatted_date = china_time.strftime('%Y-%m-%d %H:%M:%S')
                                data = generate_data_POWER_EX(label, market, formatted_date,pPower[i])
                                dat_data = generate_dat_data_POWER_EX(data)
                                # 将dat_data写入二进制文件
                                dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                                f.write(dat_data)
                                csv_list.append(data)
                            if len(csv_list) >= batch_size:
                                writer.writerows(csv_list)
                                csv_list.clear()  # 清空列表准备下一个批次
                        if csv_list:
                            writer.writerows(csv_list)
                            csv_list.clear()  # 清空列表准备下一个批次
            elif wDataType == FILE_BASE_EX:  # 基本资料文件
                logger.info(f"{day_time} {cuurent_time}  接收到基本资料数据-流水号：{index}")
                m_FileLong = pHeader.contents.m_File.m_dwLen
                m_FileName = f'{folder_path_csv}/基本资料/{index}_'+pHeader.contents.m_File.m_szFileName.decode('utf-8')
                # 如果目录不存在，则创建它
                if not os.path.exists(os.path.dirname(m_FileName)):
                    os.makedirs(os.path.dirname(m_FileName))
                with open(m_FileName, "wb") as fp:
                    fp.write(ctypes.string_at(pHeader.contents.data_union.m_pData, m_FileLong))
            elif wDataType == FILE_NEWS_EX:  # 新闻类
                logger.info(f"{day_time} {cuurent_time}  接收到新闻数据-流水号：{index}")
                m_FileLong = pHeader.contents.m_File.m_dwLen
                m_FileName = f'{folder_path_csv}/新闻资讯/{index}_'+pHeader.contents.m_File.m_szFileName.decode('utf-8')
                # 如果目录不存在，则创建它
                if not os.path.exists(os.path.dirname(m_FileName)):
                    os.makedirs(os.path.dirname(m_FileName))
                with open(m_FileName, "wb") as fp:
                    fp.write(ctypes.string_at(pHeader.contents.data_union.m_pData, m_FileLong))

            else:
                logger.error(f"{day_time} {cuurent_time}  接收到无效RCV_FILEDATA数据-流水号：{index} - 数据类型：{wDataType}")
        elif wFileType == RCV_MKTTBLDATA: # 市场类型数据的接收
            pMarketTableHead = ctypes.cast(lPara, ctypes.POINTER(HLMarketType)).contents
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.info(f"{day_time} {cuurent_time}  接收到RCV_MKTTBLDATA-流水号：{index}")
            # 定义文件路径
            output_file = f'{folder_path_csv}/{index}市场类型数据{cuurent_time.replace(":", "")}.csv'
            dat_file = f'{folder_path_raw}/{index}市场类型数据{cuurent_time.replace(":", "")}.dat'
            struct_size = ctypes.sizeof(DAT_HLMarketType)
            # 检查文件是否存在
            file_exists = os.path.isfile(output_file)
            # 将数据写入 CSV 文件
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                with open(dat_file, "wb") as f:
                    writer = csv.writer(file)
                    # 如果文件不存在，写入标题行
                    if not file_exists:
                        writer.writerow(csv_RCV_MKTTBLDATA)
                    # 保存csv和dat数据
                    data = generate_data_MKTTBLDATA(pMarketTableHead)
                    dat_data = generate_dat_data_MKTTBLDATA(pMarketTableHead)
                    dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                    f.write(dat_data)
                    # 写入数据行
                    writer.writerow(data)
            # 定义RCV_TABLE_STRUCT文件路径
            output_file = f'{folder_path_csv}/{index}证券类型数据{cuurent_time.replace(":", "")}.csv'
            dat_file = f'{folder_path_raw}/{index}证券类型数据{cuurent_time.replace(":", "")}.dat'
            struct_size = ctypes.sizeof(DAT_TABLE_STRUCT)
            # 遍历市场代码表的每个记录
            with open(dat_file, "wb") as f:
                for i in range(pMarketTableHead.m_nCount):
                    # 计算 RCV_TABLE_STRUCT 的位置
                    offset = 54 + ctypes.sizeof(RCV_TABLE_STRUCT) * i
                    Buf = ctypes.cast(lPara + offset, ctypes.POINTER(RCV_TABLE_STRUCT)).contents
                    # 检查文件是否存在
                    file_exists = os.path.isfile(output_file)
                    # 将数据写入 CSV 文件
                    with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        # 如果文件不存在，写入标题行
                        if not file_exists:
                            writer.writerow(csv_TABLE_STRUCT)
                        # 写入数据行
                        data = generate_data_TABLE_STRUCT(Buf)
                        dat_data = generate_dat_data_TABLE_STRUCT(data)
                        writer.writerow(data)
                        dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                        f.write(dat_data)
                        
        elif wFileType == RCV_FINANCEDATA:
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.info(f"{day_time} {cuurent_time}  接收到RCV_FINANCEDATA-流水号：{index}")
            # 定义目标文件路径
            output_file = f'{folder_path_csv}/{index}金融类型数据{cuurent_time.replace(":", "")}.csv'
            dat_file = f'{folder_path_raw}/{index}金融类型数据{cuurent_time.replace(":", "")}.dat'
            struct_size = ctypes.sizeof(DAT_FINANCEDATA)

            # 初始化数据列表，批量写入的批次大小
            csv_list = []
            raw_list = []
            batch_size = 500  # 每次写入500条数据，批量写入以提高效率

            # 检查文件是否存在
            file_exists = os.path.isfile(output_file)
            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                with open(dat_file, "wb") as f:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(csv_FINANCEDATA)
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
                        data = generate_data_RCV_FINANCEDATA(Buf,formatted_date)
                        dat_data = generate_dat_data_RCV_FINANCEDATA(data)
                        dat_data = ctypes.string_at(ctypes.addressof(dat_data), struct_size)
                        f.write(dat_data)
                        csv_list.append(data)
                        # 每到达批次大小，写入一次并清空 data_list
                        if len(csv_list) >= batch_size:
                            # 如果是第一次写入文件，添加标题行
                            writer.writerows(csv_list)  # 批量写入数据
                            csv_list.clear()  # 清空数据列表
                    # 检查是否有剩余数据未写入
                    if csv_list:
                        writer.writerows(csv_list)  # 写入剩余的数据
                        csv_list.clear()
        else:
            cuurent_time = getCurrentTime() # 获取目前时间
            logger.error(f"{day_time} {cuurent_time}  接收到无效类型数据 - 流水号：{index} - 数据类型：{wFileType}") 
            return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)
    elif msg == win32con.WM_TIMER and wparam == TIMER_ID:
        # 定时器触发的操作
        current_time = time.time()
        print("Timer triggered.")
        if current_time - last_message_time >= 3:
            print("No messages received in the last 3 seconds. Performing other operations...")
            # 在这里执行其他操作
    else:
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
        print("股票接收程序初始化成功")
        # 激活接收程序
        # bSetup = ctypes.c_int(0) 
        # buf = ctypes.POINTER(ctypes.c_char)
        # ok = dll.SetupReceiver(bSetup)
        # if ok > 0:
        #     print("股票接收程序已经激活")
        # 创建文件夹
        if not os.path.exists(f'{ROOT_PATH}/{folder_name}'):
            os.makedirs(f'{ROOT_PATH}/{folder_name}', exist_ok=True)
            # print(f"Folder '{ROOT_PATH}/{folder_name}' created successfully.")
        # 创建log文件夹
        return True
    else:
        print("Stock_Init initialization failed.")
        return False
    
import datetime
import pytz
import time
import ctypes
import logging

# 假设 logger 已经设置
logger = logging.getLogger(__name__)

def execute_daily_task(dll):
    """每天5点执行某项操作，传入dll作为参数"""
    done = False
    while True:
        # 获取当前时间，设置时区为中国标准时间（CST）
        china_tz = pytz.timezone('Asia/Shanghai')
        china_time = datetime.datetime.now(china_tz)
        
        # 格式化时间为 YYYYMMDD HHMM
        date_str = china_time.strftime('%Y%m%d')  # 日期部分
        time_str = china_time.strftime('%H%M')    # 时间部分，24小时制

        # 获取秒数和毫秒部分
        seconds = china_time.second
        milliseconds = int(china_time.microsecond / 1000)  # 获取毫秒
        time_milli_str = f"{seconds:02d}.{milliseconds:03d}"  # 格式化为秒.毫秒

        # 生成类似 "20241214 2149-09.624" 的格式
        formatted_time = f"{date_str} {time_str}-{time_milli_str}"

        # 判断是否到达5点
        if china_time.hour == 17 and china_time.minute == 0 and not done:
            logger.info(f"{formatted_time} 时间到了，执行定时操作")
            # 执行您需要的定时操作，使用 dll 参数
            # 在这里执行与 DLL 相关的操作
            buffer_size = 256  # 假设最大长度为256字节
            pBuf = ctypes.create_string_buffer(buffer_size)
            result = dll.AskStockPRP(pBuf)
            done = True
        # 每天凌晨将done变量重置为False
        if china_time.hour == 0 and china_time.minute == 0 and china_time.second == 0:
            done = False
        # 每分钟检查一次
        time.sleep(40)


# 加载成功后启动消息循环
def run_message_loop():
    if initialize_dll(): # 初始化dll
        try:
            # 启动定时任务线程，并将dll传入该线程
            scheduler_thread = threading.Thread(target=execute_daily_task, args=(dll,), daemon=True)
            scheduler_thread.start()
            
            # 启动消息循环
            win32gui.PumpMessages()  # 等待消息
        except KeyboardInterrupt:
            # 取消定时器
            # user32.KillTimer(None, TIMER_ID)
            print("Timer killed.")
