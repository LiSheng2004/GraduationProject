from constant import DAT_FENBI,DAT_REPORT,DAT_POWER_EX,DAT_HLMarketType,DAT_TABLE_STRUCT,DAT_FINANCEDATA,DAT_MINUTE_EX,DAT_5MINUTE_EX,DAT_DAY_EX

def generate_data_RCV_FENBIDATA(pFenBi,formatted_date,pFenBiData):
    return [pFenBi.m_szLabel.decode('ascii'),  # 股票代码
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
            *pFenBiData.m_fBuyPrice,            # 申买价
            *pFenBiData.m_fBuyVolume,           # 申买量
            *pFenBiData.m_fSellPrice,           # 申卖价
            *pFenBiData.m_fSellVolume]           # 申卖量]
def generate_dat_data_RCV_FENBIDATA(data):
    return DAT_FENBI(
        m_szLabel=data[0].encode('ascii'),
        m_wMarket=data[1],
        m_lDate=data[2],
        m_fLastClose=data[3],
        m_fOpen=data[4],
        m_nCount=data[5],
        formatted_date=data[6].encode('utf-8'),
        m_fHigh=data[7],
        m_fLow=data[8],
        m_fNewPrice=data[9],
        m_fVolume=data[10],
        m_fAmount=data[11],
        m_fBuyPrice1=data[12],
        m_fBuyPrice2=data[13],
        m_fBuyPrice3=data[14],
        m_fBuyPrice4=data[15],
        m_fBuyPrice5=data[16],
        m_fBuyVolume1=data[17],
        m_fBuyVolume2=data[18],
        m_fBuyVolume3=data[19],
        m_fBuyVolume4=data[20],
        m_fBuyVolume5=data[21],
        m_fSellPrice1=data[22],
        m_fSellPrice2=data[23],
        m_fSellPrice3=data[24],
        m_fSellPrice4=data[25],
        m_fSellPrice5=data[26],
        m_fSellVolume1=data[27],
        m_fSellVolume2=data[28],
        m_fSellVolume3=data[29],
        m_fSellVolume4=data[30],
        m_fSellVolume5=data[31]
    )
    
def generate_data_RCV_REPORT(Buf,formatted_date):
    return [
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
]

def generate_dat_data_RCV_REPORT(data):
    return DAT_REPORT(
        m_cbSize=data[0],
        formatted_date=data[1].encode('utf-8'),
        m_wMarket=data[2],
        m_szLabel=data[3].encode('ascii'),
        m_szName=data[4].encode('gbk'),
        m_fLastClose=data[5],
        m_fOpen=data[6],
        m_fHigh=data[7],
        m_fLow=data[8],
        m_fNewPrice=data[9],
        m_fVolume=data[10],
        m_fAmount=data[11],
        m_fBuyPrice1=data[12],
        m_fBuyPrice2=data[13],
        m_fBuyPrice3=data[14],
        m_fBuyVolume1=data[15],
        m_fBuyVolume2=data[16],
        m_fBuyVolume3=data[17],
        m_fSellPrice1=data[18],
        m_fSellPrice2=data[19],
        m_fSellPrice3=data[20],
        m_fSellVolume1=data[21],
        m_fSellVolume2=data[22],
        m_fSellVolume3=data[23],
        m_fBuyPrice4=data[24],
        m_fBuyVolume4=data[25],
        m_fSellPrice4=data[26],
        m_fSellVolume4=data[27],
        m_fBuyPrice5=data[28],
        m_fBuyVolume5=data[29],
        m_fSellPrice5=data[30],
        m_fSellVolume5=data[31]
    )
def generate_data_POWER_EX(label, market, formatted_date,pPower):
    return [
            label,market,formatted_date,pPower.m_fGive,pPower.m_fPei,pPower.m_fPeiPrice,pPower.m_fProfit]
def generate_dat_data_POWER_EX(data):
    return DAT_POWER_EX(
        m_szLabel=data[0].encode('ascii'),  # 股票代码，ASCII 编码
        m_wMarket=data[1],  # 市场类型
        formatted_date=data[2].encode('utf-8'),  # 日期，UTF-8 编码
        m_fGive=data[3],  # 每股送
        m_fPei=data[4],  # 每股配
        m_fPeiPrice=data[5],  # 配股价
        m_fProfit=data[6]  # 每股红利
    )

def generate_data_MKTTBLDATA(pMarketTableHead):
    return [
            pMarketTableHead.m_wMarket,
            list(pMarketTableHead.m_Name),
            pMarketTableHead.m_lProperty,
            pMarketTableHead.m_lDate,
            pMarketTableHead.m_PeriodCount,
            list(pMarketTableHead.m_OpenTime),
            list(pMarketTableHead.m_CloseTime),
            pMarketTableHead.m_nCount,]

def generate_dat_data_MKTTBLDATA(pMarketTableHead):
    return DAT_HLMarketType(
        m_wMarket=pMarketTableHead.m_wMarket,
        m_Name=pMarketTableHead.m_Name,
        m_lProperty=pMarketTableHead.m_lProperty,
        m_lDate=pMarketTableHead.m_lDate,
        m_PeriodCount=pMarketTableHead.m_PeriodCount,
        m_OpenTime=pMarketTableHead.m_OpenTime,
        m_CloseTime=pMarketTableHead.m_CloseTime,
        m_nCount=pMarketTableHead.m_nCount
    )
    
def generate_data_TABLE_STRUCT(Buf):
    return [
            Buf.m_szLabel.decode('ascii'),
            Buf.m_szName.decode('gbk'),
            Buf.m_cProperty                 
        ]
def generate_dat_data_TABLE_STRUCT(data):
    return DAT_TABLE_STRUCT(
        m_szLabel=data[0].encode('ascii'),
        m_szName=data[1].encode('gbk'),
        m_cProperty=data[2]
    )
def generate_data_RCV_FINANCEDATA(Buf,formatted_date):
    return [
            Buf.m_wMarket, Buf.N1, Buf.m_szLabel.decode('ascii'), formatted_date, Buf.ZGB, 
            Buf.GJG, Buf.FQFRG, Buf.FRG, Buf.BGS, Buf.HGS, Buf.MQLT, Buf.ZGG, Buf.A2ZPG,
            Buf.ZZC, Buf.LDZC, Buf.GDZC, Buf.WXZC, Buf.CQTZ, Buf.LDFZ, Buf.CQFZ,
            Buf.ZBGJJ, Buf.MGGJJ, Buf.GDQY, Buf.ZYSR, Buf.ZYLR, Buf.QTLR, Buf.YYLR,
            Buf.TZSY, Buf.BTSR, Buf.YYWSZ, Buf.SNSYTZ, Buf.LRZE, Buf.SHLR, Buf.JLR,
            Buf.WFPLR, Buf.MGWFP, Buf.MGSY, Buf.MGJZC, Buf.TZMGJZC, Buf.GDQYB, Buf.JZCSYL
        ]
def generate_dat_data_RCV_FINANCEDATA(data):
    return DAT_FINANCEDATA(
        m_wMarket=data[0],
        N1=data[1],
        m_szLabel=data[2].encode('ascii'),
        formatted_date=data[3].encode('utf-8'),
        ZGB=data[4],
        GJG=data[5],
        FQFRG=data[6],
        FRG=data[7],
        BGS=data[8],
        HGS=data[9],
        MQLT=data[10],
        ZGG=data[11],
        A2ZPG=data[12],
        ZZC=data[13],
        LDZC=data[14],
        GDZC=data[15],
        WXZC=data[16],
        CQTZ=data[17],
        LDFZ=data[18],
        CQFZ=data[19],
        ZBGJJ=data[20],
        MGGJJ=data[21],
        GDQY=data[22],
        ZYSR=data[23],
        ZYLR=data[24],
        QTLR=data[25],
        YYLR=data[26],
        TZSY=data[27],
        BTSR=data[28],
        YYWSZ=data[29],
        SNSYTZ=data[30],
        LRZE=data[31],
        SHLR=data[32],
        JLR=data[33],
        WFPLR=data[34],
        MGWFP=data[35],
        MGSY=data[36],
        MGJZC=data[37],
        TZMGJZC=data[38],
        GDQYB=data[39],
        JZCSYL=data[40]
    )
def generate_data_MINUTE_EX(label, market, formatted_date,pMin):
    return [label,market,formatted_date,pMin.m_fPrice,pMin.m_fVolume,pMin.m_fAmount]
def generate_dat_data_MINUTE_EX(data):
    return DAT_MINUTE_EX(
        m_szLabel=data[0].encode('ascii'),  # 股票代码，ASCII 编码
        m_wMarket=data[1],  # 市场类型
        formatted_date=data[2].encode('utf-8'),  # 日期，UTF-8 编码
        m_fPrice = data[3],  # 价格
        m_fVolume = data[4],  # 成交量
        m_fAmount = data[5]  # 成交额
    )
def generate_data_5MINUTE_EX(label, market, formatted_date,p5Min):
    return [label,market,formatted_date,p5Min.m_fOpen,p5Min.m_fHigh,p5Min.m_fLow,p5Min.m_fClose,p5Min.m_fVolume,p5Min.m_fAmount,p5Min.m_fActiveBuyVol ]
def generate_dat_data_5MINUTE_EX(data):
    return DAT_5MINUTE_EX(
        m_szLabel=data[0].encode('ascii'),  # 股票代码，ASCII 编码
        m_wMarket=data[1],  # 市场类型
        formatted_date=data[2].encode('utf-8'),  # 日期，UTF-8 编码
        m_fOpen = data[3],  # 开盘价
        m_fHigh = data[4],  # 最高价
        m_fLow = data[5],  # 最低价
        m_fClose = data[6],  # 收盘价
        m_fVolume = data[7],  # 成交量
        m_fAmount = data[8],  # 成交额
        m_fActiveBuyVol = data[9]  # 主动买入成交量
    )
def generate_data_DAY_EX(label, market, formatted_date,pDay):
    return [label,market,formatted_date,pDay.m_fOpen,pDay.m_fHigh,pDay.m_fLow,pDay.m_fClose,pDay.m_fVolume,pDay.m_fAmount,pDay.m_wAdvance,pDay.m_wDecline]
def generate_dat_data_DAY_EX(data):
    return DAT_DAY_EX(
        m_szLabel=data[0].encode('ascii'),  # 股票代码，ASCII 编码
        m_wMarket=data[1],  # 市场类型
        formatted_date=data[2].encode('utf-8'),  # 日期，UTF-8 编码
        m_fOpen = data[3],  # 开盘价
        m_fHigh = data[4],  # 最高价
        m_fLow = data[5],  # 最低价
        m_fClose = data[6],  # 收盘价
        m_fVolume = data[7],  # 成交量
        m_fAmount = data[8],  # 成交额
        m_wAdvance = data[9],  # 上涨天数
        m_wDecline = data[10]  # 下跌天数
    )