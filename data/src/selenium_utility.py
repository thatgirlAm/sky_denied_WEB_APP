import random
import time
import seleniumwire.undetected_chromedriver as uc
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

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

        return driver

    except Exception as e:
        print("Error initializing Chrome driver:", e)
        return None

def driver_wait(driver, xpath, random_start=1, random_end=2, wait_time=30):
    WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )
    time.sleep(random.uniform(random_start, random_end))

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
        print("Button clicked successfully!")
        return True
    except Exception as e:
        print(f"Failed to click button at {xpath}: {e}")
        return False

def click_all_buttons(driver, xpath):
    click_count = 0
    while True:
        print(f"Clicking button ({click_count + 1})...")
        if not click_button(driver, xpath):
            print("No more buttons found.")
            break
        click_count += 1
        time.sleep(random.uniform(1.0, 3.0))  # simulate load time




