import pickle
import gzip

def load_from_binary_file(input_file):
    """
    从二进制文件中加载数据列表
    """
    data_list = []
    try:
        with open(input_file, 'rb') as binary_file:  # 以二进制读模式打开文件
            while True:
                try:
                    data = pickle.load(binary_file)  # 反序列化对象
                    data_list.append(data)
                except EOFError:
                    break  # 读到文件末尾时退出循环
    except FileNotFoundError:
        print(f"文件 {input_file} 不存在。")
    return data_list

if __name__ == "__main__":
    # 使用示例
    # 加载压缩的二进制文件
    with gzip.open(r'data\20241205_221410\20241205\22\raw\26补报告数据2214-19.533.pkl.gz', 'rb') as f:
        loaded_data = pickle.load(f)
    print(loaded_data)
