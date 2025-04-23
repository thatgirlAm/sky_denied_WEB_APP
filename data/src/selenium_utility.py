import random
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

import logging
import shutil
import platform
import os
import platform

logger_realtime = logging.getLogger("realtime")
logger_schedule = logging.getLogger("schedule")

def get_chrome_path():
    system = platform.system()

    if system == "Windows":
        paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google\\Chrome\\Application\\chrome.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google\\Chrome\\Application\\chrome.exe"),
        ]
    elif system == "Darwin":  # macOS
        paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
    elif system == "Linux":
        paths = ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chrome"]

    for path in paths:
        if path and os.path.exists(path):
            return path
        
    fallback = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium")
    return fallback

def gen_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")  # Use the newer headless mode
        
        # Add these to better mimic a real browser
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    # Common options for both headless and non-headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    
    # Add experimental options to avoid detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    system = platform.system()
    
    if system == "Linux":
        # Linux container: use preinstalled chromedriver
        service = Service("/usr/bin/chromedriver")
    else:
        # Local macOS or Windows: use webdriver-manager
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=chrome_options)

def driver_wait(driver, xpath, random_start=1, random_end=2, wait_time=30):
    try:
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        time.sleep(random.uniform(random_start, random_end))
        logger_realtime.info("Element at xpath '%s' is present.", xpath)
        logger_schedule.info("Element at xpath '%s' is present.", xpath)
    except Exception as e:
        logger_schedule.warning("Timeout waiting for element at xpath '%s': %s", xpath, e)

def click_button(driver, xpath, wait_time=10, scroll=True):
    try:
        button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        if scroll:
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                button
            )
            time.sleep(random.uniform(0.8, 1.5))
        actions = ActionChains(driver)
        actions.move_to_element(button).pause(random.uniform(0.4, 1.2)).click().perform()
        logger_realtime.info("Button at xpath '%s' clicked successfully.", xpath)
        logger_schedule.info("Button at xpath '%s' clicked successfully.", xpath)
        return True
    except Exception as e:
        logger_schedule.warning("Failed to click button at xpath '%s': %s", xpath, e)
        return False

def click_all_buttons(driver, xpath):
    click_count = 0
    while True:
        logger_schedule.info("Attempting to click button #%d at xpath '%s'...", click_count + 1, xpath)
        if not click_button(driver, xpath):
            logger_schedule.info("No more buttons found after %d clicks.", click_count)
            break
        click_count += 1
        time.sleep(random.uniform(1.0, 3.0))  # simulate load time
