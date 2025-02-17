#Example
#TARGET_URL = 'https://live.photoplus.cn/live/pc/75588420/#/live' (Our School Winter Concert Live Photos)
TARGET_URL = '###########INPUT YOUR TARGET URL HERE###########'
if TARGET_URL == '###########INPUT YOUR TARGET URL HERE###########':
    print("\033[91mPlease input your live photo album target url in the variable TARGET_URL!!!!!!!!!\033[0m")

    exit()





print("================================")
print("PlusPhoto Downloader v7")
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



import os
import time
import requests
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import concurrent.futures
from tqdm import tqdm

def setup_logging():
    """
    设置日志记录。
    """
    logging.basicConfig(
        filename='download.log',
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def setup_webdriver(headless=False):
    """
    设置Selenium WebDriver。
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # 启用无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    
    # 使用webdriver-manager自动管理ChromeDriver

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def scroll_within_container(driver, container, pause_time=1, max_scrolls=100):
    """
    模拟在特定容器内滚动页面，以加载所有动态内容。
    """
    last_height = driver.execute_script("return arguments[0].scrollHeight", container)
    
    for scroll in range(max_scrolls):
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", container)
        logging.info(f"在容器内滚动到底部，尝试第 {scroll + 1} 次")
        
        time.sleep(pause_time)
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == last_height:
            logging.info("已经滚动到容器底部，停止滚动。")
            break
        last_height = new_height

def extract_thumbnail_elements(driver):
    """
    从页面中提取所有缩略图的WebElement元素。
    """
    thumbnails = driver.find_elements(By.CSS_SELECTOR, '.photo-content.container ul li span div img')
    logging.info(f"共找到 {len(thumbnails)} 个缩略图元素。")
    return thumbnails

def click_and_get_original_image_url(driver, thumbnail):
    """
    点击缩略图，获取弹出界面中“查看原图”按钮的 href URL。
    """
    try:
        # 滚动到缩略图可见的位置
        driver.execute_script("arguments[0].scrollIntoView();", thumbnail)
        
        # 使用ActionChains模拟点击，避免被遮挡
        actions = ActionChains(driver)
        actions.move_to_element(thumbnail).click().perform()
        logging.info("点击缩略图，等待详细视图弹出。")
        
        wait = WebDriverWait(driver, 20)  # 增加等待时间
        
        try:
            # 等待包含 'iconImg chakan' 的 'row-all-center' 按钮出现，并找到其中的 <a> 标签
            view_original_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//li[contains(@class, 'row-all-center') and .//i[contains(@class, 'iconImg') and contains(@class, 'chakan')]]//a")
            ))
            original_image_url = view_original_button.get_attribute('href')
            logging.info(f"提取到原图URL: {original_image_url}")
            
            # 关闭弹出窗口
            try:
                close_button = driver.find_element(By.XPATH, "//button[contains(@class, 'mu-dialog-close') or contains(@class, 'close')]")
                close_button.click()
                logging.info("关闭弹出窗口。")
                time.sleep(1)  # 等待关闭动画完成
            except NoSuchElementException:
                # 如果没有找到关闭按钮，尝试按 Esc 键
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                logging.info("尝试通过按 Esc 键关闭弹出窗口。")
                time.sleep(1)
            
            return original_image_url

        except TimeoutException:
            logging.warning("等待查看原图按钮超时，跳过此缩略图。")
            return None

    except TimeoutException:
        logging.warning("等待元素超时，跳过此缩略图。")
        return None
    except NoSuchElementException:
        logging.warning("未找到必要的元素，跳过此缩略图。")
        return None
    except ElementClickInterceptedException:
        logging.warning("元素被拦截，尝试再次点击。")
        try:
            thumbnail.click()
            wait = WebDriverWait(driver, 5)
            # 使用相同的XPath定位
            view_original_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//li[contains(@class, 'row-all-center') and .//i[contains(@class, 'iconImg') and contains(@class, 'chakan')]]//a")
            ))
            original_image_url = view_original_button.get_attribute('href')
            logging.info(f"提取到原图URL: {original_image_url}")
            
            # 关闭弹出窗口
            try:
                close_button = driver.find_element(By.XPATH, "//button[contains(@class, 'mu-dialog-close') or contains(@class, 'close')]")
                close_button.click()
                logging.info("关闭弹出窗口。")
                time.sleep(1)
            except NoSuchElementException:
                # 如果没有找到关闭按钮，尝试按 Esc 键
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                logging.info("尝试通过按 Esc 键关闭弹出窗口。")
                time.sleep(1)
            
            return original_image_url
        except Exception as e:
            logging.error(f"重试点击时出错: {e}", exc_info=True)
            return None

def extract_original_image_urls(driver, thumbnails):
    """
    遍历所有缩略图，点击并提取原图URL。
    """
    original_image_urls = set()
    total = len(thumbnails)
    logging.info(f"共找到 {total} 个缩略图。开始提取原图URL。")
    
    for idx, thumbnail in enumerate(tqdm(thumbnails, desc="提取原图URL")):
        try:
            logging.info(f"处理缩略图 {idx + 1}/{total}")
            original_src = click_and_get_original_image_url(driver, thumbnail)
            if original_src:
                if original_src not in original_image_urls:
                    original_image_urls.add(original_src)
                    logging.info(f"已添加 URL: {original_src}")
                else:
                    logging.info(f"重复的 URL，已跳过: {original_src}")
            time.sleep(1)  # 防止过快点击导致问题
        except Exception as e:
            logging.error(f"处理缩略图索引 {idx} 时出错: {e}", exc_info=True)
            continue
    return list(original_image_urls)

def download_image(url, folder, idx):
    """
    下载单个图片并保存到指定文件夹。
    """
    try:
        response = requests.get(url, stream=True, timeout=15)
        if response.status_code == 200:
            img_extension = os.path.splitext(url.split('?')[0])[1]
            if img_extension.lower() not in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.avif']:
                img_extension = '.jpg'
            img_path = os.path.join(folder, f'image_{idx + 1}{img_extension}')
            with open(img_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logging.info(f"下载成功: {img_path}")
        else:
            logging.warning(f"无法下载图片 (状态码 {response.status_code}): {url}")
    except Exception as e:
        logging.error(f"下载图片时出错 ({url}): {e}", exc_info=True)

def main():
    setup_logging()
    
    # 目标URL
    url = TARGET_URL
    
    # 设置下载文件夹
    download_folder = 'downloaded_images'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # 初始化WebDriver（有头模式）
    driver = setup_webdriver(headless=False)
    
    try:
        logging.info(f"打开网页: {url}")
        driver.get(url)
        
        wait = WebDriverWait(driver, 20)
        container = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.photo-content.container')))
        logging.info("已找到容器元素：.photo-content.container")
        
        scroll_within_container(driver, container, pause_time=2, max_scrolls=100)
        
        thumbnails = extract_thumbnail_elements(driver)
        
        original_image_urls = extract_original_image_urls(driver, thumbnails)
        logging.info(f"共提取到 {len(original_image_urls)} 张原图URL。")
        
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        
        # 下载图片（多线程）
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(download_image, img_url, download_folder, idx)
                for idx, img_url in enumerate(original_image_urls)
            ]
            for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="下载图片"):
                pass
    
    except Exception as e:
        logging.error(f"运行脚本时出错: {e}", exc_info=True)
    
    finally:
        driver.quit()
        logging.info("脚本结束，WebDriver已关闭。")

if __name__ == "__main__":
    main()