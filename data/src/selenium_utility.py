import random
import time
import seleniumwire.undetected_chromedriver as uc
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import logging
import shutil
import platform
import os

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


def gen_driver():
    try:
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36"
        )

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument(f"user-agent={user_agent}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Set Chrome binary path explicitly
        chrome_binary = shutil.which("google-chrome") or shutil.which("chrome") or shutil.which("chromium") 
        chrome_binary = get_chrome_path()
        if chrome_binary:
            chrome_options.binary_location = chrome_binary
            logger_realtime.info(f"Using Chrome binary at: {chrome_binary}")
            logger_schedule.info(f"Using Chrome binary at: {chrome_binary}")
        else:
            logger_realtime.warning("Could not find Chrome binary. Relying on default path.")
            logger_schedule.warning("Could not find Chrome binary. Relying on default path.")

        driver = uc.Chrome(version_main=134, options=chrome_options)
       

        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        logger_realtime.info("Chrome driver initialized successfully.")
        logger_schedule.info("Chrome driver initialized successfully.")
        return driver

    except Exception as e:
        logger_realtime.exception("Error initializing Chrome driver: %s", e)
        logger_schedule.exception("Error initializing Chrome driver: %s", e)
        return None

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
