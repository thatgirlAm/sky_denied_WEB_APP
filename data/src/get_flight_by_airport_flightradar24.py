"""
get_flight_by_airport_flightradar24.py

Scrapes Flightradar24 arrivals for a given airport.
Uses parse_flightradar24 from parse_flight_data.py
to handle the HTML transformation.
"""

import bs4
import os
import pandas as pd
import logging
from datetime import datetime

from .parse_flight_data import parse_flightradar24
from .selenium_utility import gen_driver, click_button, click_all_buttons

# Logger setup

# Point to ../data
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def construct_airport_url(base_url, airport, flight_type):
    return f"{base_url}/data/airports/{airport}/{flight_type}"

def crawl_flightradar24_airport_flights(base_url, airport_code_iata, flight_type="arrivals"):
    logger = logging.getLogger("schedule")
    """
    Main crawling logic for Flightradar24 arrivals (or departures if extended).
    """
    df = pd.DataFrame()
    driver = gen_driver()
    url = construct_airport_url(base_url, airport_code_iata, flight_type)

    try:
        logger.info("Navigating to Flightradar24 URL: %s", url)
        driver.get(url)

        # Attempt to click any cookie reject button
        if click_button(driver, '//*[@id="onetrust-reject-all-handler"]', wait_time=5):
            logger.info("Cookie rejection button clicked.")

        # Load earlier & later flights
        click_all_buttons(driver, '//button[contains(@class, "btn-flights-load") and contains(text(), "Load earlier flights")]')
        click_all_buttons(driver, '//button[contains(@class, "btn-flights-load") and contains(text(), "Load later flights")]')

        html = driver.page_source
        soup = bs4.BeautifulSoup(html, "html.parser")

        df = parse_flightradar24(soup, mode="arrival")
        logger.info("Parsed %d rows from Flightradar24 HTML.", len(df))

    except Exception as e:
        logger.exception("Error occurred while scraping Flightradar24 for %s: %s", airport_code_iata, str(e))

    finally:
        driver.quit()
        # today = datetime.now().strftime("%Y-%m-%d")
        # output_dir = os.path.join(DATA_DIR, f"{flight_type}_flightradar24")
        # os.makedirs(output_dir, exist_ok=True)

        # csv_name = f"{flight_type}_{airport_code_iata}_{today}.csv"
        # output_path = os.path.join(output_dir, csv_name)
        df = df.drop_duplicates()
        # df.to_csv(output_path, index=False)

        # logger.info(f"Saved Flightradar24 {flight_type} data to: {output_path}")
        logger.info(f"Flightradar24 {flight_type} scraping complete for {airport_code_iata}: {len(df)} rows")

    return df
