import hashlib
from cryptography.fernet import Fernet
import base64
import json

# 加密密码并保存密钥
def encrypt_password(password, hint, encryption_algorithm='fernet'):
    # 使用hint生成32字节的密钥
    key = hashlib.sha256(hint.encode()).digest()

    # 创建URL安全的Base64编码密钥，Fernet需要32字节的密钥
    fernet_key = base64.urlsafe_b64encode(key)  # 固定32字节的密钥
    fernet = Fernet(fernet_key)
    encrypted_password = fernet.encrypt(password.encode())
    
    # 保存密钥和加密方式
    key_file_path = input("请输入密钥保存路径（默认key.key）：") or "key.key"
    with open(key_file_path, "wb") as key_file:
        key_data = {
            'key': fernet_key.decode(),  # 保存URL安全Base64编码的密钥
            'algorithm': encryption_algorithm
        }
        key_file.write(json.dumps(key_data).encode())  # 将加密方式和密钥一起保存
    
    # 返回加密后的密码
    return encrypted_password, key_file_path

# 通过hint恢复密码
def decrypt_password(hint, key_file_path="key.key"):
    try:
        # 读取保存的密钥
        with open(key_file_path, "rb") as key_file:
            key_data = json.loads(key_file.read().decode())  # 读取加密方式和密钥
            saved_key = base64.urlsafe_b64decode(key_data['key'])  # 解码Base64密钥
            encryption_algorithm = key_data['algorithm']
        
        # 使用hint生成32字节的密钥并进行Base64编码
        key = hashlib.sha256(hint.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key)

        # 根据选择的加密算法解密
        if encryption_algorithm == 'fernet':
            fernet = Fernet(fernet_key)
        else:
            raise ValueError("Unsupported decryption algorithm")
        
        # 读取原始的加密密码
        password_file_path = input("请输入加密密码文件路径（默认encrypted-password.enc）：") or "encrypted-password.enc"
        with open(password_file_path, "rb") as password_file:
            encrypted_password = password_file.read()

        # 解密密码
        decrypted_password = fernet.decrypt(encrypted_password).decode()
        return decrypted_password
    except Exception as e:
        return f"Error: {e}"

# 主程序
def main():
    print("密码加密系统")

    action = input("请选择操作：1. 加密密码 2. 恢复密码\n")

    if action == "1":
        password = input("请输入密码：")
        hint = input("请输入密码提示（hint）：")
        
        # 加密密码并保存
        encrypted_password, key_file_path = encrypt_password(password, hint)

        # 将加密后的密码保存到文件
        password_file_path = input("请输入加密密码保存路径（默认encrypted-password.enc）：") or "encrypted-password.enc"
        with open(password_file_path, "wb") as password_file:
            password_file.write(encrypted_password)

        print(f"密码加密完成，并保存密钥到 {key_file_path}，密码保存到 {password_file_path}。")
    
    elif action == "2":
        hint = input("请输入密码提示（hint）：")
        
        # 提供更多自定义选项
        key_file_path = input("请输入密钥文件路径（默认key.key）：") or "key.key"

        # 尝试恢复密码
        decrypted_password = decrypt_password(hint, key_file_path)

        if decrypted_password.startswith("Error"):
            print(decrypted_password)
        else:
            print(f"恢复的密码为: {decrypted_password}")
    else:
        print("无效选择，程序结束。")

if __name__ == "__main__":
    main()