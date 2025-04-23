
"""
get_flight_by_airport_flightera.py

Scrapes Flightera for arrival or departure flights for a given airport.
Uses parse_flightera from parse_flight_data.py to transform the HTML content.
"""

import bs4
from datetime import datetime, timedelta
import re
import os
import pandas as pd
from urllib.parse import urljoin
import logging

from .parse_flight_data import parse_flightera
from .selenium_utility import gen_driver, driver_wait

# Define a DATA_DIR that points to ../data relative to this file.
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def construct_airport_url(base_url, airport_city, airport_code_icao, flight_type, date_str, time_str):
    airport_city_encoded = airport_city.replace(" ", "+")
    return f"{base_url}/en/airport/{airport_city_encoded}/{airport_code_icao}/{flight_type}/{date_str}%20{time_str}?"

def deduct_flight_schedule_date_time_by_one_minute(date_str, time_str):
    dt = datetime.strptime(f"{date_str} {time_str.replace('_', ':')}", "%Y-%m-%d %H:%M")
    dt -= timedelta(minutes=1)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H_%M")

def extract_datetime_from_url(href):
    match = re.search(r"/(\d{4}-\d{2}-\d{2}) (\d{2}_\d{2})", href)
    if match:
        return match.group(1), match.group(2)
    return None, None

def crawl_flighttera_airport_flights(
    base_url="https://www.flightera.net",
    airport_city=None,
    airport_code_iata=None, 
    airport_code_icao=None, 
    flight_type=None,
    start_date_str=None,
    time_str="23_59",
    end_date=None
):
    logger = logging.getLogger("schedule")
    driver = gen_driver()
    today = datetime.now().date()
    if end_date:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    all_data = pd.DataFrame()
    earlier_date = None

    url = construct_airport_url(base_url, airport_city, airport_code_icao, flight_type, start_date_str, time_str)
    logger.info("Starting Flightera scrape from: %s", url)

    try:
        driver.get(url)
        while True:
            driver_wait(driver,"//a[contains(text(), 'Earlier Flights')]")
            html = driver.page_source
            soup = bs4.BeautifulSoup(html, "html.parser")

            df = parse_flightera(soup, mode=flight_type)
            all_data = pd.concat([all_data, df], ignore_index=True)

            earlier_tag = soup.find("a", string=lambda text: text and "Earlier Flights" in text)
            if not earlier_tag:
                logger.info("No more 'Earlier Flights' link.")
                break

            href = earlier_tag.get("href")
            if not href:
                logger.warning("Missing href in earlier flights link.")
                break
            
            earlier_date, earlier_time = extract_datetime_from_url(href)
            if not earlier_date:
                logger.warning("Could not extract date from link: %s", href)
                break

            logger.info("Scraping earlier flights: %s %s", earlier_date, earlier_time)

            flight_date_obj = datetime.strptime(earlier_date, "%Y-%m-%d").date()

            if end_date and flight_date_obj <= end_date:
                logger.info("Reached end_date. Stopping scrape.")
                break
            elif not end_date and flight_date_obj <= today:
                logger.info("Reached today's date. Stopping scrape.")
                break

            full_url = urljoin(base_url, href)
            driver.get(full_url)

            new_html = driver.page_source
            if html == new_html:
                logger.warning("Page content did not change. Using -1 minute fallback.")
                date_str, time_str = deduct_flight_schedule_date_time_by_one_minute(earlier_date, earlier_time)
                url = construct_airport_url(base_url, airport_city, airport_code_icao, flight_type, date_str, time_str)
                driver.get(url)
            else:
                url = full_url

    except Exception as e:
        logger.exception("Flightera scrape failed: %s", e)

    finally:
        driver.quit()
        all_data.drop_duplicates(inplace=True)
        logger.info("Flightera scrape finished: %d rows", len(all_data))

    return all_data
