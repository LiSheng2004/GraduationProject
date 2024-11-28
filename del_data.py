import os

def delete_all_files_in_folder(folder_path):
    try:
        # 获取文件夹中的所有文件和子文件夹
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            # 判断是文件还是文件夹
            if os.path.isfile(file_path):
                os.remove(file_path)  # 删除文件
            elif os.path.isdir(file_path):
                # 递归删除子文件夹中的内容
                delete_all_files_in_folder(file_path)
                os.rmdir(file_path)  # 删除空文件夹
        print(f"成功清空文件夹: {folder_path}")
    except Exception as e:
        print(f"删除文件夹内容时出错: {e}")

# 示例用法
folder_path = "./data"
delete_all_files_in_folder(folder_path)
