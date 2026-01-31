#!/usr/bin/env python3
import time
import random
import argparse
import json
import requests
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from jason_telemetry import pipeline_telemetry
from contextlib import contextmanager


# 辅助函数：无操作的上下文管理器（当没有遥测对象时使用）
@contextmanager
def contextlib_dummy_step():
    """无操作的上下文管理器"""
    try:
        yield
    except Exception:
        raise


def create_chrome_driver(options):
    try:
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    except Exception as exc:
        logger.warning(f'⚠ ChromeDriver 更新失败，改用系统驱动: {exc}')
        return webdriver.Chrome(options=options)

# 配置日志
logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('submit_wjx.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


# User-Agent 列表（精简版保留常见系统）
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
]

# 语言列表
LANGUAGES = [
    "zh-CN,zh;q=0.9,en;q=0.8",
    "en-US,en;q=0.9",
    "zh-CN,zh;q=0.9",
    "en-US,en;q=0.9,zh;q=0.8",
]

# 浏览器窗口大小列表
WINDOW_SIZES = [
    (1920, 1080),  # 标准桌面
    (1366, 768),   # 笔记本常见
    (1440, 900),   # MacBook Air
    (1280, 720),   # 小屏幕
    (2560, 1440),  # 高分屏
    (1024, 768),   # 老旧设备
]

# Referer 列表（常见网站）
REFERRERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.baidu.com/",
    "https://www.sogou.com/",
    "",  # 直接访问
]

# Accept-Encoding 列表
ACCEPT_ENCODINGS = [
    "gzip, deflate, br",
    "gzip, deflate",
    "gzip",
]

# User-Agent 客户端提示
CLIENT_HINTS = [
    ("sec-ch-ua", '"Chromium";v="121", "Not A(Brand";v="99"'),
    ("sec-ch-ua", '"Google Chrome";v="121", "Chromium";v="121", "Not A(Brand";v="99"'),
    ("sec-ch-ua", '"Microsoft Edge";v="121", "Chromium";v="121", "Not A(Brand";v="99"'),
]


# === ClashX API 配置与代理节点 ===
CLASH_API_HOST = '127.0.0.1'
CLASH_API_PORT = 51237
CLASH_API_KEY = 'Z9P-9p7-A62-dcq'

# 前21个代理节点（从YAML提取的前21个）
PROXY_NODES = [
    '🇭🇰 香港W01',
    '🇯🇵 日本W01',
    '🇭🇰 香港W02 | IEPL',
    '🇯🇵 日本W02 | IEPL',
    '🇭🇰 香港W03 | IEPL',
    '🇯🇵 日本W03 | IEPL',
    '🇭🇰 香港W04 | IEPL',
    '🇯🇵 日本W04 | IEPL',
    '🇭🇰 香港W05 | IEPL',
    '🇯🇵 日本W05 | 下载专用 | x0.01',
    '🇭🇰 香港W06 | x0.8',
    '🇯🇵 日本W06 | 下载专用 | x0.01',
    '🇭🇰 香港W07 | x0.8',
    '🇯🇵 日本W07 | x0.8',
    '🇭🇰 香港W08 | x0.8',
    '🇯🇵 日本W08 | x0.8',
    '🇭🇰 香港W09 | IEPL',
    '🇯🇵 日本W09 | IEPL',
    '🇭🇰 香港W10 | IEPL',
    '🇯🇵 日本W10 | IEPL',
    '🇭🇰 香港W11 | IEPL',
]


def get_random_user_agent():
    """随机获取 User-Agent"""
    return random.choice(USER_AGENTS)


def get_random_language():
    """随机获取语言设置"""
    return random.choice(LANGUAGES)


def get_random_window_size():
    """随机获取浏览器窗口大小"""
    return random.choice(WINDOW_SIZES)


def get_random_referer():
    """随机获取 Referer"""
    return random.choice(REFERRERS)


def get_random_accept_encoding():
    """随机获取 Accept-Encoding"""
    return random.choice(ACCEPT_ENCODINGS)


def get_random_client_hint():
    """随机获取 Client Hint"""
    return random.choice(CLIENT_HINTS)


def get_random_proxy():
    """随机选择一个代理节点"""
    return random.choice(PROXY_NODES)


def set_clash_mode(mode='GLOBAL'):
    """设置 Clash 工作模式"""
    try:
        headers = {'Authorization': f'Bearer {CLASH_API_KEY}'}
        url = f'http://{CLASH_API_HOST}:{CLASH_API_PORT}/configs'
        response = requests.patch(url, json={'mode': mode}, headers=headers, timeout=5)
        return response.status_code in [200, 204]
    except Exception as e:
        logger.warning(f'设置 Clash 模式失败: {e}')
        return False


def select_clash_proxy(proxy_name):
    """选择指定代理节点"""
    try:
        headers = {'Authorization': f'Bearer {CLASH_API_KEY}'}
        url = f'http://{CLASH_API_HOST}:{CLASH_API_PORT}/proxies/GLOBAL'
        response = requests.put(url, json={'name': proxy_name}, headers=headers, timeout=5)
        return response.status_code in [200, 204]
    except Exception as e:
        logger.warning(f'选择代理失败: {e}')
        return False


def get_current_ip(timeout=10, wait_before_request=2):
    """获取当前外网 IP"""
    ip_apis = [
        'https://api.ipify.org?format=json',
        'https://ifconfig.me/',
        'https://icanhazip.com/',
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
    }
    
    time.sleep(wait_before_request)
    
    for api_url in ip_apis:
        try:
            session = requests.Session()
            response = session.get(api_url, headers=headers, timeout=timeout, allow_redirects=False)
            session.close()
            
            if response.status_code == 200:
                if 'json' in api_url:
                    ip = response.json().get('ip', '').strip()
                else:
                    ip = response.text.strip()
                return ip if ip else None
        except Exception:
            continue
    return None


def get_clash_current_proxy():
    """获取当前选中的代理"""
    try:
        headers = {'Authorization': f'Bearer {CLASH_API_KEY}'}
        response = requests.get(f'http://{CLASH_API_HOST}:{CLASH_API_PORT}/proxies/GLOBAL', 
                               headers=headers, timeout=5)
        return response.json().get('now', '') if response.status_code == 200 else None
    except Exception:
        return None


def test_clash_connection():
    """测试 Clash API 连接"""
    try:
        headers = {'Authorization': f'Bearer {CLASH_API_KEY}'}
        response = requests.get(f'http://{CLASH_API_HOST}:{CLASH_API_PORT}/version', 
                               headers=headers, timeout=5)
        if response.status_code == 200:
            logger.info(f'✓ Clash API 连接成功: {response.json()}')
            return True
        else:
            logger.error(f'✗ Clash API 连接失败: {response.status_code}')
            return False
    except Exception as e:
        logger.error(f'✗ Clash API 连接失败: {e}')
        logger.info(f'请确保 ClashX 已启动，API 地址: {CLASH_API_HOST}:{CLASH_API_PORT}')
        return False


def test_proxy_ip(proxy_name, test_count=3):
    """测试代理是否能改变 IP"""
    logger.info(f'测试代理: {proxy_name}')
    
    if not select_clash_proxy(proxy_name):
        logger.error(f'无法切换到代理 {proxy_name}')
        return False
    
    time.sleep(1)
    current = get_clash_current_proxy()
    if current and current != proxy_name:
        logger.warning(f'代理名称不匹配: {current} != {proxy_name}')
    
    ips = []
    for i in range(test_count):
        try:
            wait_time = 3 if i == 0 else 2
            ip = get_current_ip(wait_before_request=wait_time)
            if ip:
                logger.info(f'  {i+1}. IP: {ip}')
                ips.append(ip)
            else:
                logger.warning(f'  {i+1}. 获取 IP 失败')
        except Exception as e:
            logger.error(f'  {i+1}. 错误: {e}')
        
        if i < test_count - 1:
            time.sleep(1)
    
    if ips:
        unique_ips = set(ips)
        if len(unique_ips) == 1:
            logger.warning(f'⚠ 获取到 {len(ips)} 个相同 IP: {ips[0]}')
            logger.info('💡 这可能是代理缓存或节点出口 IP 固定')
        else:
            logger.info(f'✓ 获取到 {len(unique_ips)} 个不同 IP')
        return True
    else:
        logger.error('无法通过代理获取 IP')
        return False


def is_driver_alive(driver):
    """检查 WebDriver 是否还活着（浏览器窗口是否还打开）"""
    try:
        # 尝试获取窗口句柄，如果浏览器被关闭会抛出异常
        _ = driver.window_handles
        # 尝试执行一个简单命令以确保连接还活着
        driver.execute_script('return 1')
        return True
    except (NoSuchWindowException, WebDriverException):
        return False
    except Exception:
        return False


def read_template(path):
    """
    读取答案模板（JSON 格式）
    格式: {"answers": ["A(0.7),B(0.3)", "5", "1;2(0.6),1;3(0.4)"]}
    返回答案列表
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 支持多种格式
    if isinstance(data, dict):
        if 'answers' in data:
            answers = data['answers']
            if isinstance(answers, list):
                return answers
        # 兼容旧格式：{"Q1": "A", "Q2": "B"}
        elif all(k.startswith('Q') or k.isdigit() for k in data.keys()):
            return [data.get(str(i+1), data.get(f'Q{i+1}', '')) for i in range(len(data))]
    
    # 如果是列表，直接返回
    if isinstance(data, list):
        return data
    
    return []


def letter_to_index(letter):
    """字母转索引：A->0, B->1, ..."""
    if not letter:
        return 0
    letter = letter.strip().upper()
    if letter and ord(letter[0]) >= ord('A'):
        return ord(letter[0]) - ord('A')
    return 0


def parse_weighted_answer(answer_str):
    """
    解析带权重的答案格式: "A(0.7),B(0.3)" 或 "1(0.5),2(0.5)"
    返回: (选中值, 原始字符串) - 选中值为根据权重随机选择的结果
    如果没有权重或解析失败，返回 (原始答案, 原始字符串)
    """
    if not answer_str or '(' not in answer_str:
        return answer_str, answer_str
    
    try:
        choices = []
        weights = []
        parts = answer_str.split(',')
        
        for part in parts:
            part = part.strip()
            if '(' in part and ')' in part:
                # 格式: A(0.7) 或 1(0.5)
                choice = part[:part.index('(')].strip()
                weight_str = part[part.index('(')+1:part.index(')')].strip()
                weight = float(weight_str)
                choices.append(choice)
                weights.append(weight)
        
        if choices and len(choices) == len(weights):
            # 根据权重进行随机选择
            selected = random.choices(choices, weights=weights, k=1)[0]
            return selected, answer_str
    except Exception:
        pass
    
    return answer_str, answer_str


def parse_answer(answer_str, question_type):
    """
    解析答案字符串，根据题型返回处理后的值
    支持权重格式: "A(0.7),B(0.3)" 将随机选择一个答案
    - type 3 (单选): 返回字母对应的索引
    - type 4 (多选): 返回数字列表 [0,1,2,...] 或对应的索引
    - type 8 (评分): 返回数字字符串
    """
    # 先检查是否有权重格式
    selected_answer, _ = parse_weighted_answer(answer_str)
    
    if question_type == '3':  # 单选题
        return letter_to_index(selected_answer)
    elif question_type == '4':  # 多选题
        # 答案格式：1;2;3 或 A;B;C
        if not selected_answer:
            return []
        parts = selected_answer.split(';')
        indices = []
        for p in parts:
            p = p.strip()
            if p.isdigit():
                indices.append(int(p) - 1)  # 1-based -> 0-based
            else:
                indices.append(letter_to_index(p))
        return indices
    elif question_type == '8':  # 评分题
        try:
            return float(selected_answer.strip())
        except ValueError:
            return 0.0
    else:
        return selected_answer


def find_questions(driver):
    """
    查找所有题目容器，返回 [(container_element, question_id, question_type), ...]
    根据 topic 属性和 type 属性来识别
    """
    fields = driver.find_elements(By.CSS_SELECTOR, "div.field[topic]")
    questions = []
    for field in fields:
        try:
            topic_id = field.get_attribute('topic')
            q_type = field.get_attribute('type')
            if topic_id and q_type:
                questions.append((field, int(topic_id), q_type))
        except Exception:
            continue
    return questions


def answer_single_choice(container, choice_index):
    """
    单选题：点击第 choice_index 个选项
    """
    inputs = container.find_elements(By.XPATH, './/input[@type="radio"]')
    if not inputs:
        return False
    
    if choice_index < 0:
        choice_index = 0
    if choice_index >= len(inputs):
        choice_index = len(inputs) - 1
    
    try:
        inputs[choice_index].click()
        return True
    except Exception:
        try:
            parent = inputs[choice_index].find_element(By.XPATH, './..')
            parent.click()
            return True
        except Exception:
            return False


def answer_multiple_choice(container, indices):
    """
    多选题：点击指定索引的选项（indices 是列表）
    """
    checkboxes = container.find_elements(By.XPATH, './/input[@type="checkbox"]')
    if not checkboxes:
        return False
    
    success_count = 0
    for idx in indices:
        if 0 <= idx < len(checkboxes):
            try:
                checkboxes[idx].click()
                success_count += 1
            except Exception:
                try:
                    parent = checkboxes[idx].find_element(By.XPATH, './..')
                    parent.click()
                    success_count += 1
                except Exception:
                    pass
    
    return success_count > 0


def answer_slider(driver, container, value):
    """
    评分题（滑块）：设置数值到输入框或滑块
    """
    # 方式1：直接设置 input 的值
    input_elem = container.find_element(By.CSS_SELECTOR, 'input[type="text"].ui-slider-input')
    if input_elem:
        try:
            # 清空并输入值
            input_elem.clear()
            input_elem.send_keys(str(value))
            # 触发 change 事件
            driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }))", input_elem)
            return True
        except Exception:
            pass
    
    return False


def wait_for_success_page(driver, timeout=15):
    """等待成功页面（URL 包含 completemobile2.aspx）"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            current_url = driver.current_url
            if 'completemobile2.aspx' in current_url:
                parsed = urlparse(current_url)
                params = parse_qs(parsed.query)
                params_dict = {k: v[0] if isinstance(v, list) else v for k, v in params.items()}
                return True, params_dict, current_url
        except Exception as e:
            logger.debug(f'检查成功页面出错: {e}')
        time.sleep(0.5)
    
    return False, {}, driver.current_url


def log_submission(log_file, success, url_params, current_url, submission_number=1, answers=None, user_agent=None, language=None, window_size=None, referer=None, accept_encoding=None):
    """记录提交到 JSON 文件"""
    log_path = Path(log_file)
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'submission_number': submission_number,
        'success': success,
        'url': current_url,
        'parameters': url_params,
        'answers': answers or [],
        'browser_fingerprint': {
            'user_agent': user_agent,
            'language': language,
            'window_size': window_size,
            'referer': referer,
            'accept_encoding': accept_encoding
        }
    }
    
    logs = []
    if log_path.exists():
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except Exception:
            logs = []
    
    logs.append(log_data)
    
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
    
    if success:
        logger.info(f'✓ 提交 #{submission_number} 成功')
        for key in ['activityid', 'joinactivity', 'comsign', 'jqnonce']:
            if key in url_params:
                logger.info(f'  {key}: {url_params[key]}')
    else:
        logger.warning(f'✗ 提交 #{submission_number} 失败')


def submit_once(driver, url, answers, wait_seconds=10, log_file=None, submission_number=1, user_agent=None, language=None, window_size=None, referer=None, accept_encoding=None, telemetry=None):
    """
    填答并提交一份问卷
    answers: list 与 questions 对应，每个元素格式根据题型而定
    log_file: 可选的日志文件路径
    user_agent: 使用的 User-Agent
    language: 使用的语言
    window_size: 浏览器窗口大小 (width, height)
    referer: Referer 头
    accept_encoding: Accept-Encoding 头
    telemetry: 可选的遥测对象
    """
    # 加载页面
    try:
        with (telemetry.step("load_page") if telemetry else contextlib_dummy_step()):
            driver.get(url)
            WebDriverWait(driver, wait_seconds).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(0.5 + random.random() * 0.8)
    except Exception as e:
        # 如果页面加载失败（网络错误等），记录并抛出异常让主循环处理
        error_msg = str(e)
        if 'Could not reach host' in error_msg or 'timeout' in error_msg.lower():
            if log_file:
                log_submission(log_file, False, {}, url, submission_number, answers=answers, user_agent=user_agent, language=language, window_size=window_size, referer=referer, accept_encoding=accept_encoding)
            raise  # 将异常抛给主循环处理
        else:
            if log_file:
                log_submission(log_file, False, {}, url, submission_number, answers=answers, user_agent=user_agent, language=language, window_size=window_size, referer=referer, accept_encoding=accept_encoding)
            return False

    # 查找所有题目
    try:
        with (telemetry.step("find_questions") if telemetry else contextlib_dummy_step()):
            questions = find_questions(driver)
            if not questions:
                print('未找到题目容器，放弃此次提交')
                if log_file:
                    log_submission(log_file, False, {}, driver.current_url, submission_number, answers=answers, user_agent=user_agent, language=language, window_size=window_size, referer=referer, accept_encoding=accept_encoding)
                return False
    except Exception as e:
        if log_file:
            log_submission(log_file, False, {}, driver.current_url, submission_number, answers=answers, user_agent=user_agent, language=language, window_size=window_size, referer=referer, accept_encoding=accept_encoding)
        raise

    # 记录实际应用的答案（考虑权重随机选择）
    applied_answers = []
    
    # 遍历题目并根据题型填答
    try:
        with (telemetry.step("fill_answers") if telemetry else contextlib_dummy_step()):
            for idx, (container, topic_id, q_type) in enumerate(questions):
                if idx >= len(answers):
                    break
                
                ans = answers[idx]
                # 获取实际选中的答案（如果有权重会随机选择）
                actual_ans, _ = parse_weighted_answer(ans)
                applied_answers.append(actual_ans)
                
                try:
                    if q_type == '3':  # 单选题
                        choice_idx = parse_answer(ans, '3')
                        answer_single_choice(container, choice_idx)
                    elif q_type == '4':  # 多选题
                        indices = parse_answer(ans, '4')
                        answer_multiple_choice(container, indices)
                    elif q_type == '8':  # 评分题
                        value = parse_answer(ans, '8')
                        answer_slider(driver, container, value)
                    else:
                        print(f'题目 {topic_id}：未知题型 {q_type}')
                except Exception as e:
                    print(f'题目 {topic_id} 填答出错：{e}')
                
                time.sleep(0.08 + random.random() * 0.12)
    except Exception as e:
        if log_file:
            log_submission(log_file, False, {}, driver.current_url, submission_number, answers=answers, user_agent=user_agent, language=language, window_size=window_size, referer=referer, accept_encoding=accept_encoding)
        raise

    # 点击提交按钮
    try:
        with (telemetry.step("submit") if telemetry else contextlib_dummy_step()):
            submit_selectors = [
                "button:xpath-contains('提交')",
                "#ctlNext",
                "div#ctlNext",
                "button[type='submit']",
            ]
            clicked = False
            for sel in submit_selectors:
                try:
                    if sel == "button:xpath-contains('提交')":
                        btns = driver.find_elements(By.XPATH, "//button[contains(text(),'提交')]")
                        if btns:
                            btns[0].click()
                            clicked = True
                            break
                    else:
                        el = driver.find_element(By.CSS_SELECTOR, sel)
                        el.click()
                        clicked = True
                        break
                except Exception:
                    continue

            if not clicked:
                try:
                    btns = driver.find_elements(By.XPATH, "//div[@id='ctlNext' or contains(text(),'提交')]")
                    if btns:
                        btns[0].click()
                        clicked = True
                except Exception:
                    pass
    except Exception as e:
        if log_file:
            log_submission(log_file, False, {}, driver.current_url, submission_number, answers=answers, user_agent=user_agent, language=language, window_size=window_size, referer=referer, accept_encoding=accept_encoding)
        raise

    # 等待成功页面
    try:
        with (telemetry.step("wait_success") if telemetry else contextlib_dummy_step()):
            success, url_params, final_url = wait_for_success_page(driver, timeout=15)
    except Exception as e:
        if log_file:
            log_submission(log_file, False, {}, driver.current_url, submission_number, answers=answers, user_agent=user_agent, language=language, window_size=window_size, referer=referer, accept_encoding=accept_encoding)
        raise
    
    # 记录日志
    if log_file:
        log_submission(log_file, success, url_params, final_url, submission_number, answers=applied_answers, user_agent=user_agent, language=language, window_size=window_size, referer=referer, accept_encoding=accept_encoding)
    
    time.sleep(0.8 + random.random() * 1.2)
    return success


def main():
    p = argparse.ArgumentParser(description='Auto submit WJX survey using a JSON answers config')
    p.add_argument('--answers', '-a', default='answers.json', help='JSON answers config file path')
    p.add_argument('--count', '-n', type=int, default=1, help='Number of submissions')
    p.add_argument('--url', default='https://v.wjx.cn/vm/wTfKoMR.aspx', help='WJX survey URL')
    p.add_argument('--headless', action='store_true', help='Run Chrome headless')
    p.add_argument('--wait', type=int, default=10, help='Page load wait seconds')
    p.add_argument('--log', default='submission_log.json', help='Log file path for submissions')
    p.add_argument('--random-fingerprint', action='store_true', help='Use random browser fingerprint (User-Agent, language, window size, referer, etc)')
    p.add_argument('--use-clash', action='store_true', help='Use Clash API to rotate proxies')
    
    # 测试相关参数
    p.add_argument('--test-clash', action='store_true', help='Test Clash API connection')
    p.add_argument('--test-proxy', type=str, help='Test specific proxy node (e.g., "🇭🇰 香港W01")')
    p.add_argument('--test-ip', action='store_true', help='Get current IP address')
    
    args = p.parse_args()

    # 处理测试命令
    if args.test_clash:
        test_clash_connection()
        return
    
    if args.test_ip:
        logger.info('获取当前 IP...')
        ip = get_current_ip()
        logger.info(f'当前 IP: {ip}' if ip else '无法获取 IP')
        return
    
    if args.test_proxy:
        test_proxy_ip(args.test_proxy)
        return

    answers = read_template(args.answers)
    if not answers:
        logger.error(f'未读取到答案: {args.answers}')
        logger.info('期望格式: {"answers": ["A", "B", "5", ...]}')
        return

    if args.use_clash:
        logger.info('初始化 Clash API...')
        if set_clash_mode('GLOBAL'):
            logger.info('✓ Clash 模式设置为 GLOBAL')
        else:
            logger.warning('⚠ 无法连接 Clash API，不使用代理轮换')

    logger.info(f'开始提交 {args.count} 份问卷')
    
    try:
        with pipeline_telemetry(
            "wjx.submission.batch",
            options={
                "total_count": args.count,
                "use_random_fingerprint": args.random_fingerprint,
                "use_clash": args.use_clash,
                "headless": args.headless,
            }
        ) as batch_telemetry:
            for i in range(args.count):
                logger.info(f'提交 {i+1}/{args.count}')
                
                options = webdriver.ChromeOptions()
                if args.headless:
                    options.add_argument('--headless=new')
                    options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                user_agent = language = window_size = referer = accept_encoding = proxy_name = None
                
                if args.random_fingerprint:
                    user_agent = get_random_user_agent()
                    options.add_argument(f'user-agent={user_agent}')
                    logger.debug(f'UA: {user_agent[:50]}...')
                    
                    language = get_random_language()
                    options.add_argument(f'accept-language={language}')
                    logger.debug(f'Language: {language}')
                    
                    window_size = get_random_window_size()
                    referer = get_random_referer()
                    accept_encoding = get_random_accept_encoding()
                    logger.debug(f'Window: {window_size[0]}x{window_size[1]} | Referer: {referer if referer else "direct"}')
                
                if args.use_clash:
                    proxy_name = get_random_proxy()
                    if select_clash_proxy(proxy_name):
                        logger.debug(f'代理: {proxy_name}')
                    else:
                        logger.warning(f'⚠ 无法切换到代理: {proxy_name}')
                
                driver = create_chrome_driver(options)
                
                if window_size:
                    driver.set_window_size(window_size[0], window_size[1])
                
                try:
                    if not is_driver_alive(driver):
                        logger.warning('浏览器窗口已关闭，停止')
                        break
                    
                    # 为单个提交创建遥测跟踪
                    with pipeline_telemetry(
                        "wjx.submission.single",
                        options={
                            "submission_number": i+1,
                            "use_random_fingerprint": bool(user_agent),
                            "proxy_node": proxy_name or "none",
                        }
                    ) as submission_telemetry:
                        ok = submit_once(driver, args.url, answers, wait_seconds=args.wait, log_file=args.log, 
                                       submission_number=i+1, user_agent=user_agent, language=language, 
                                       window_size=window_size, referer=referer, accept_encoding=accept_encoding,
                                       telemetry=submission_telemetry)
                        if ok:
                            logger.info('✓ 提交成功')
                            submission_telemetry.set_option("success", True)
                        else:
                            logger.warning('✗ 提交失败或未检测到成功页面')
                            submission_telemetry.set_option("success", False)
                    
                    if not is_driver_alive(driver):
                        logger.warning('浏览器窗口已关闭，停止')
                        break
                        
                except Exception as e:
                    error_msg = str(e)
                    if isinstance(e, (NoSuchWindowException, WebDriverException)) and ('no such window' in error_msg.lower() or 'disconnected' in error_msg.lower()):
                        logger.warning('浏览器窗口已关闭，停止')
                        break
                    elif 'Could not reach host' in error_msg or 'Network is unreachable' in error_msg:
                        logger.warning(f'网络错误: {error_msg[:60]}')
                        if args.log:
                            log_submission(args.log, False, {}, driver.current_url if driver else 'unknown', i+1, 
                                         answers=answers, user_agent=user_agent, language=language, 
                                         window_size=window_size, referer=referer, accept_encoding=accept_encoding)
                    else:
                        logger.error(f'提交错误: {error_msg[:80]}')
                        if args.log:
                            log_submission(args.log, False, {}, driver.current_url if driver else 'unknown', i+1, 
                                         answers=answers, user_agent=user_agent, language=language, 
                                         window_size=window_size, referer=referer, accept_encoding=accept_encoding)
                finally:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                
                if i < args.count - 1:
                    time.sleep(1 + random.random() * 2)
            
            logger.info(f'✓ 全部完成，日志保存到: {args.log}')
            batch_telemetry.add_extra(log_file=args.log, submitted_count=i+1)
    except KeyboardInterrupt:
        logger.warning('用户中止')
    except Exception as e:
        logger.error(f'严重错误: {e}')


if __name__ == '__main__':
    main()
