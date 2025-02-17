# -*- coding: utf-8 -*-
import os
import base64
from dotenv import load_dotenv, set_key
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from datetime import datetime



print("================================")
print("CIE Auto Check Score V5.0")
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







# 配置 .env 文件路径
env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

#设置固定的密钥和 Base64 嵌套次数
#在这里配置程序！！！！
XOR_KEY = "mysecretkey"
BASE64_LAYERS = 30  # 定义多层 Base64 的嵌套次数

# 多层 Base64 加密函数
def multi_base64_encode(data, layers):
    """对数据进行多层 Base64 编码"""
    for _ in range(layers):
        data = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    return data

# 多层 Base64 解密函数
def multi_base64_decode(data, layers):
    """对数据进行多层 Base64 解码"""
    for _ in range(layers):
        data = base64.b64decode(data).decode('utf-8')
    return data

# XOR 加密函数，生成多层 Base64 编码的结果
def xor_encrypt(data, key):
    xor_result = ''.join(
        chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data)
    )
    return multi_base64_encode(xor_result, BASE64_LAYERS)

# XOR 解密函数，解码多层 Base64 并进行 XOR 解密
def xor_decrypt(data, key):
    decoded_data = multi_base64_decode(data, BASE64_LAYERS)
    return ''.join(
        chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(decoded_data)
    )

# 获取或设置加密后的用户名
encoded_username = os.getenv("GLOBAL_ENCODED_CIE_USERNAME")
if encoded_username:
    # 解密用户名
    try:
        username = xor_decrypt(encoded_username, XOR_KEY)
        print("解密成功，用户名:", username)
    except Exception as e:
        print("解密用户名失败:", e)
        username = None
else:
    # 输入用户名并加密
    username = input("请输入用户名：")
    encoded_username = xor_encrypt(username, XOR_KEY)
    set_key(env_path, key_to_set="GLOBAL_ENCODED_CIE_USERNAME", value_to_set=encoded_username)
    print("用户名已加密并存储到 .env 文件中")

# 获取或设置加密后的密码
encoded_password = os.getenv("GLOBAL_ENCODED_CIE_PASSWORD")
if encoded_password:
    # 解密密码
    try:
        password = xor_decrypt(encoded_password, XOR_KEY)
        print("解密成功，密码:", password)
    except Exception as e:
        print("解密密码失败:", e)
        password = None
else:
    # 输入密码并加密
    password = input("请输入密码：")
    encoded_password = xor_encrypt(password, XOR_KEY)
    set_key(env_path, key_to_set="GLOBAL_ENCODED_CIE_PASSWORD", value_to_set=encoded_password)
    print("密码已加密并存储到 .env 文件中")

# 设置 ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# 打开登录页面
login_url = "https://myresults.cie.org.uk/cie-candidate-results/login"
driver.get(login_url)

# 填写用户名和密码
username_input = driver.find_element(By.ID, "username")
username_input.send_keys(username) # type: ignore

password_input = driver.find_element(By.ID, "password")
password_input.send_keys(password) # type: ignore

# 提交登录表单
login_button = driver.find_element(By.ID, "submit")
login_button.click()

# 等待页面加载
time.sleep(1)

# 登录成功后，打开成绩页面
results_url = "https://myresults.cie.org.uk/cie-candidate-results/results#"
driver.get(results_url)

# 定时检查成绩是否发布
while True:
    try:
        # 查找是否显示“Results to be released”
        result_text = driver.find_element(By.XPATH, "//td[@class='result']//strong[contains(text(), 'Results to be released')]")
        print("成绩尚未发布，提示：", result_text.text)
        wait_time = random.uniform(1, 3)  # 随机等待时间
        print(f"等待 {wait_time:.2f} 秒后再试...")
        time.sleep(wait_time)
        driver.refresh()  # 刷新页面
    except Exception:
        try:
            # 查找成绩信息
            result_tag = driver.find_element(By.CSS_SELECTOR, "td.result strong")
            print("成绩信息:", result_tag.text)
            
            # 记录当前时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"成绩查询成功，时间: {current_time}")
            
            break  # 成绩已发布，退出循环
        except Exception as inner_e:
            print("无法获取成绩信息:", inner_e)
            break

# 关闭浏览器
driver.quit()