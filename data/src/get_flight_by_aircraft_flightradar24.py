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
        logger.info("Start parsing aircraft %s", aircraft)
        df = parse_flightradar24_aircraft(soup)

        logger.info("Successfully scraped aircraft %s: %d rows", aircraft, len(df))

    except Exception as e:
        logger.exception("Error scraping aircraft %s from Flightradar24", aircraft)

    finally:
        driver.quit()
        logger.info("Flightradar24 aircraft scrape done for %s: %d rows", aircraft, len(df))
    return df
