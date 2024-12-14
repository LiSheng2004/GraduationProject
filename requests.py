# requests.py
from extended_api import *

try:
    stock_data = ask_stock_day("000001", 1)
    print("接收到的数据:", stock_data)
except ValueError as e:
    print(e)