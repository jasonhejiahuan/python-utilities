import requests
import os
import hashlib
import shutil
import random
import string
import sys
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm

print("JASON Studio")
print("made by Jason")

dev_mode = False  # 设置这里，打开开发模式，避免自动覆盖开发版

disalow_update = False

if dev_mode:
    disalow_update = True
    print()
    print("\033[96mHello, world!\033[0m")
    print()
    print("\033[96m当前处于开发模式！！！\033[0m")

def calculate_self_hash():
    # 获取当前脚本的文件名
    script_filename = os.path.abspath(__file__)

    # 读取文件内容
    with open(script_filename, 'rb') as f:
        file_content = f.read()

    # 计算MD5哈希值
    md5_hash = hashlib.md5(file_content).hexdigest()

    return md5_hash
    print(f"这个程序的MD5哈希值为: {calculate_self_hash()}")


if disalow_update:
    print("\033[95m已跳过自动更新\033[0m")
    print(f"当前脚本的MD5哈希值为：{calculate_self_hash()}")
else:
    def generate_random_prefix(length=8):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    def update_self():
        script_filename = os.path.abspath(__file__)

        backup_folder = "ota_backup"
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        random_prefix = generate_random_prefix()
        backup_filename = os.path.join(backup_folder, f"{random_prefix}_{os.path.basename(script_filename)}")

        shutil.copy(script_filename, backup_filename)

        url = "https://raw.githubusercontent.com/jasonhejiahuan/python-utilities/main/image_download_test.py"
        requests.head = {
            'Cache-Control': "no-cache"
        }
        response = requests.get(url)
        with open(script_filename, 'wb') as f:
            f.write(response.content)

        hash_url = "https://raw.githubusercontent.com/jasonhejiahuan/studying-python/main/image_download_test.py-md5.txt"
        requests.head = {
            'Cache-Control': "no-cache"
        }
        hash_response = requests.get(hash_url)
        if hash_response.status_code == 200:
            print("成功获取线上版本的MD5哈希值")
        else:
            print("\033[1;31m获取线上版本的MD5哈希值失败\033[0m")
        expected_hash = hash_response.text.strip()
        print(f"线上版本的MD5哈希值为：{expected_hash}")

        if calculate_self_hash() != expected_hash:
            print("有新版本可用，正在更新脚本...")
            os.system(f"python3 {script_filename}")
        else:
            print("\033[1;42m现在是最新版本\033[0m")


    update_self()

print("================================")
print("Image Downloader")
print("·Made By Jason")
print("""
          @                                                 
          @                                                 
          @                                                 
          @                                                 
          @                                                 
          @                                                 
          @@@@@@@@@       @@@@@@@@@@@@@@@@@@@@@@@@@         
          @       @       @               @       @         
          @       @       @@@@@@@@        @       @@@@@@@@@ 
          @       @              @        @       @       @ 
 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@        @@@@@@@@@       @
""")
print("================================")

# 检查当前目录下是否存在saves文件夹，如果不存在则创建
if not os.path.exists('saves'):
    os.makedirs('saves')
# 切换到saves文件夹
os.chdir('saves')
print("请在" + "saves" + "目录查看下载好的图片")

# 让用户输入
global_image_url = input("""请输入图片的URL
（如果是下载单张图片，则直接填入全部链接，如果是多张，则填入图片前的链接，包括最后一个/）：""")
name_prefix = input("请输入图片的前缀(否则随机生成)：")

# 检查如果name_prefix为空则生成随机前缀
if not name_prefix:
    # 随机生成前缀函数
    def generate_random_name_prefix(length=8):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))
    name_prefix = generate_random_name_prefix()
    print(f"未输入前缀，已生成随机前缀：{name_prefix}")

# 检查当前目录下是否存在name_prefix文件夹，如果不存在则创建
if not os.path.exists(name_prefix):
    os.makedirs(name_prefix)

# 切换到name_prefix文件夹
os.chdir(name_prefix)

# 选项1: 下载单张图片
def download_single_image():
    file_name = global_image_url.split('/')[-1]
    print("原始名称：" + file_name)
    
    save_folder = os.path.join('saves', name_prefix)
    os.makedirs(save_folder, exist_ok=True)
    save_path = os.path.join(save_folder, file_name)

    response = requests.get(global_image_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))  # 获取图片大小
    if response.status_code == 200:
        print("\033[32m成功下载图片\033[0m" + str(file_name))
        with open(save_path, 'wb') as f, tqdm(
            desc="正在下载图片",
            total=total_size,
            unit='B',
            unit_scale=True,
            leave=False
        ) as progress_bar:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)
                    progress_bar.update(len(chunk))

        img = Image.open(save_path)
        width, height = img.size
        print("\033[1m图片的宽度为：" + str(width) + "像素\033[0m")
        print("\033[1m图片的高度为：" + str(height) + "像素\033[0m")

        print("\033[1m图片名为：" + file_name + "\033[0m")
        print("\033[1m图片大小为：" + str(total_size) + "字节\033[0m")
        print("\033[1m图片格式为：" + file_name.split('.')[-1] + "\033[0m")

        plt.imshow(img, cmap="gray")
        plt.show()
    else:
        print("\033[31m下载失败，状态码:\033[0m", response.status_code)
        sys.exit(2)

# 选项2: 下载多张图片
def download_multiple_images():
    print("你输入的URL是" + global_image_url)
    print("请确保你输入的URL不包括图片本身，而是图片前面的路径")
    
    file_name_min = int(input("请输入图片名称NUMBER最小值："))
    file_name_max = int(input("请输入图片名称NUMBER最大值："))
    file_format = input("请输入图片格式，不包括点，比如png：")
    
    save_folder = os.path.join('saves', name_prefix)
    os.makedirs(save_folder, exist_ok=True)

    if dev_mode:
        print("\033[95m已阻止自动清屏\033[0m")  # 打印蓝色文字
        pass
    else:
        os.system("clear")  # 执行时清屏

    for file_name in range(file_name_min, file_name_max + 1):
        image_url = global_image_url + str(file_name) + "." + file_format
        # print(f"正在下载图片 {file_name}.{file_format}")

        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            save_path = os.path.join(save_folder, f"{name_prefix}{file_name}.{file_format}")

            with open(save_path, 'wb') as f, tqdm(
                desc=f"正在下载图片 {file_name}.{file_format}",
                total=total_size,
                unit='B',
                unit_scale=True,
                leave=False
            ) as progress_bar:
                for chunk in response.iter_content(1024):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))

            print(f"\033[32m成功下载图片 {file_name}.{file_format} ➡️ 状态码：{response.status_code}\033[0m")
        else:
            print(f"\033[31m下载图片失败 {file_name}.{file_format} ➡️ 状态码：{response.status_code}\033[0m")

    files = os.listdir(save_folder)
    print("\033[32m图片下载完成\033[0m")
    print("共下载了" + str(len(files)) + "张图片")
    print("正在清除无效图片...")

    for file_name in files:
        file_path = os.path.join(save_folder, file_name)
        if os.path.getsize(file_path) < 5000:  # 文件小于5KB认为是无效图片
            os.remove(file_path)
            print("已删除无效图片：" + file_name)

# 运行
run_mode = input("请输入运行模式（1:下载单张图片，2:下载多张图片）：")
if run_mode == "1":
        if dev_mode:
            print("\033[95m已阻止自动清屏\033[0m")  # 打印蓝色文字
            pass
        else:
            os.system("clear")  # 执行时清屏
        download_single_image()
elif run_mode == "2":
        if dev_mode:
            print("\033[95m已阻止自动清屏\033[0m")  # 打印蓝色文字
            pass
        else:
            os.system("clear")  # 执行时清屏
        download_multiple_images()

else:
    print("输入错误，请重新运行程序")
    sys.exit(1)

sys.exit(0)
