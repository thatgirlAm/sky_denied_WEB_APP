# """
# get_flight_by_aircraft_flightradar24.py

# Scrapes Flightradar24 for a given aircraft.
# """

# import bs4
# import datetime
# import os
# import pandas as pd
# # import seleniumwire.undetected_chromedriver as uc

# from .parse_flight_data import parse_flightradar24_aircraft
# from .selenium_utility import gen_driver
# import logging

# # Point to ../data
# DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

# def construct_airport_url(base_url, aircraft):
#     return f"{base_url}/data/aircraft/{aircraft}"

# def crawl_flightradar24_aircraft_flight(base_url, aircraft):
#     logger = logging.getLogger("realtime")
#     """
#     Main crawling logic for Flightradar24 arrivals (or departures if extended).
#     """
#     df = pd.DataFrame()
#     errors = []
#     # chrome_options = uc.ChromeOptions()
#     # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     driver = gen_driver()
#     url = construct_airport_url(base_url, aircraft)
#     try:
#         print(url)
#         driver.get(url)
#         # Attempt to click any cookie reject button
#         # click_button(driver, '//*[@id="onetrust-reject-all-handler"]', wait_time=5)
#         html = driver.page_source
#         soup = bs4.BeautifulSoup(html, "html.parser")
#         df = parse_flightradar24_aircraft(soup)

#     except Exception as e:
#         print(f"Error occurred: {e}")
#         errors.append((url, str(e)))
#     finally:
#         driver.quit()
#         logger.info("Flightradar24 aircraft scrape done for %s: %d rows", aircraft, len(df))
#     return df, errors



"""
get_flight_by_aircraft_flightradar24.py

Scrapes Flightradar24 for a given aircraft.
"""

import bs4
import os
import pandas as pd
import logging

from .parse_flight_data import parse_flightradar24_aircraft
from .selenium_utility import gen_driver

# Point to ../data
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def construct_airport_url(base_url, aircraft):
    return f"{base_url}/data/aircraft/{aircraft}"

'''
def crawl_flightradar24_aircraft_flight(base_url, aircraft):
    # Logger for realtime mode
    logger = logging.getLogger("realtime")
    """
    Crawls Flightradar24 aircraft history page and parses data.
    """
    df = pd.DataFrame()
    driver = gen_driver()
    url = construct_airport_url(base_url, aircraft)

    try:
        logger.info("Opening Flightradar24 aircraft URL: %s", url)
        driver.get(url)

        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")
        df = parse_flightradar24_aircraft(soup)

        logger.info("Successfully scraped aircraft %s: %d rows", aircraft, len(df))

    except Exception as e:
        logger.exception("Error scraping aircraft %s from Flightradar24", aircraft)

    finally:
        driver.quit()
        logger.info("Flightradar24 aircraft scrape done for %s: %d rows", aircraft, len(df))
    return df
'''
def crawl_flightradar24_aircraft_flight(base_url, aircraft):
    # Logger setup
    logger = logging.getLogger("realtime")
    
    df = pd.DataFrame()
    driver = gen_driver(headless=True)  # Set to True for production
    url = construct_airport_url(base_url, aircraft)

    try:
        logger.info("Opening Flightradar24 aircraft URL: %s", url)
        driver.get(url)
        
        # Add explicit wait for content to load
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # Wait for a key element that indicates the page has loaded properly
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.data-table"))
            )
            logger.info("Flight data table found, page loaded successfully")
        except:
            logger.warning("Timed out waiting for flight data table to appear")
        
        # Get page source after JavaScript has loaded the data
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")
        df = parse_flightradar24_aircraft(soup)

    except Exception as e:
        logger.exception("Error scraping aircraft %s from Flightradar24: %s", aircraft, str(e))

    finally:
        driver.quit()
        logger.info("Flightradar24 aircraft scrape done for %s: %d rows", aircraft, len(df))
    return df
   

def gen_driver(headless=True):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    
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
    
    # Create driver with options
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Execute CDP commands to bypass detection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })
    
    driver.implicitly_wait(10)
    return driver