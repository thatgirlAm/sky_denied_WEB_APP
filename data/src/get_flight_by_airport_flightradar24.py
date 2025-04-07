"""
get_flight_by_airport_flightradar24.py

Scrapes Flightradar24 arrivals for a given airport.
Uses parse_flightradar24 from parse_flight_data.py
to handle the HTML transformation.
"""

import bs4
import datetime
import os
import pandas as pd
# import seleniumwire.undetected_chromedriver as uc

from .parse_flight_data import parse_flightradar24
from .selenium_utility import gen_driver, click_button, click_all_buttons


# Point to ../data
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def construct_airport_url(base_url, airport, flight_type):
    return f"{base_url}/data/airports/{airport}/{flight_type}"

def crawl_flight_type(base_url, airport_code_iata, flight_type="arrivals"):
    """
    Main crawling logic for Flightradar24 arrivals (or departures if extended).
    """
    df = pd.DataFrame()
    errors = []
    # chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    driver = gen_driver()
    url = construct_airport_url(base_url, airport_code_iata, flight_type)
    
    try:
        print(url)
        driver.get(url)
        # Attempt to click any cookie reject button
        click_button(driver, '//*[@id="onetrust-reject-all-handler"]', wait_time=5)

        # Load earlier & later flights
        click_all_buttons(driver, '//button[contains(@class, "btn-flights-load") and contains(text(), "Load earlier flights")]')
        click_all_buttons(driver, '//button[contains(@class, "btn-flights-load") and contains(text(), "Load later flights")]')

        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")

        df = parse_flightradar24(soup, mode="arrival")

    except Exception as e:
        print(f"Error occurred: {e}")
        errors.append((url, str(e)))
    finally:
        driver.quit()
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # Save to e.g. data/arrivals_flightradar24
        output_dir = os.path.join(DATA_DIR, f"{flight_type}_flightradar24")
        os.makedirs(output_dir, exist_ok=True)

        csv_name = f"{flight_type}_{airport_code_iata}_{today}.csv"
        output_path = os.path.join(output_dir, csv_name)
        df.drop_duplicates()
        df.to_csv(output_path, index=False)
        print(f"Saved Flightradar24 {flight_type} data to: {output_path}")

    return errors