import os

ROOT_PATH = r"\\10.68.1.151\tj07166_001\Etornado-data"
print(ROOT_PATH)
if not os.path.exists(f'{ROOT_PATH}'):
    os.makedirs(f'{ROOT_PATH}', exist_ok=True)
    print(f'{ROOT_PATH}')