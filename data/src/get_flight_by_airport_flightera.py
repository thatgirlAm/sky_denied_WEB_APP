"""
get_flight_by_airport_flightera.py

Scrapes Flightera for arrival or departure flights for a given airport.
Uses parse_flightera from parse_flight_data.py to transform the HTML content.
"""

import time
import bs4
import random
import datetime
import re
import os
import pandas as pd
from urllib.parse import urljoin
# import seleniumwire.undetected_chromedriver as uc


from .parse_flight_data import parse_flightera
from .selenium_utility import gen_driver, driver_wait

# Define a DATA_DIR that points to ../data relative to this file.
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def construct_airport_url(base_url, airport_city, airport_code_icao, flight_type, date_str, time_str):
    # Ensure spaces are URL-encoded for the city
    airport_city_encoded = airport_city.replace(" ", "+")
    return f"{base_url}/en/airport/{airport_city_encoded}/{airport_code_icao}/{flight_type}/{date_str}%20{time_str}?"

def deduct_flight_schedule_date_time_by_one_minute(date_str, time_str):
    dt = datetime.datetime.strptime(f"{date_str} {time_str.replace('_', ':')}", "%Y-%m-%d %H:%M")
    dt -= datetime.timedelta(minutes=1)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H_%M")

def extract_datetime_from_url(href):
    match = re.search(r"/(\d{4}-\d{2}-\d{2}) (\d{2}_\d{2})", href)
    if match:
        return match.group(1), match.group(2)
    return None, None

def crawl_airport_flights(
    base_url="https://www.flightera.net",
    airport_city=None,
    airport_code_iata=None,
    airport_code_icao=None, 
    flight_type=None,
    start_date_str=None,
    time_str="23_59",
    save_every=5,
    end_date=None
):
    # chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # driver = uc.Chrome(version_main=134, options=chrome_options)
    driver = gen_driver()
    today = datetime.datetime.now().date()
    if end_date:
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

    visited_urls = []
    errors = []
    all_data = pd.DataFrame()

    # Store the "last URL" file inside data/ so it doesn't clutter up src/
    backup_file = os.path.join(DATA_DIR, f"{flight_type}_last_url.txt")

    # Check if there's a previously saved URL
    if os.path.exists(backup_file):
        with open(backup_file, "r") as f:
            url = f.read().strip()
        print(f"Resuming from last saved URL: {url}")
    else:
        url = construct_airport_url(base_url, airport_city, airport_code_icao, flight_type, start_date_str, time_str)
        print(f"Starting fresh from: {url}")

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
                print("No more earlier flights link.")
                break

            href = earlier_tag.get("href")
            if not href:
                print("No href in earlier flights link.")
                break

            earlier_date, earlier_time = extract_datetime_from_url(href)
            if not earlier_date:
                print("Couldn't extract date from earlier flights link.")
                break

            print(f"[{flight_type.upper()}] {earlier_date} {earlier_time}")
            visited_urls.append(url)

            flight_date_obj = datetime.datetime.strptime(earlier_date, "%Y-%m-%d").date()

            if end_date:
                # Stop if we reach or pass end_date
                if flight_date_obj <= end_date:
                    print("Reached end_date. Exiting.")
                    break
            else:
                # If no end_date was provided, we default to 'today'
                if flight_date_obj <= today:
                    print("Reached today's date. Exiting.")
                    break

            # Load next page
            full_url = urljoin(base_url, href)
            driver.requests.clear()
            driver.get(full_url)
            driver_wait(driver,"//a[contains(text(), 'Earlier Flights')]", 2, 4)

            new_html = driver.page_source
            if html == new_html:
                print("Page content did not change. Trying manual -1 minute fallback.")
                date_str, time_str = deduct_flight_schedule_date_time_by_one_minute(earlier_date, earlier_time)
                url = construct_airport_url(base_url, airport_city, airport_code_icao, flight_type, date_str, time_str)
                driver.get(url)
            else:
                url = full_url

    except Exception as e:
        print(f"Error occurred: {e}")
        errors.append((url, str(e)))
    finally:
        if earlier_date:
            flight_date_obj = datetime.datetime.strptime(earlier_date, "%Y-%m-%d").date()
            if flight_date_obj > today or (end_date and flight_date_obj > end_date):
                with open(backup_file, "w") as f:
                    f.write(url)
            else:
                if os.path.exists(backup_file):
                    os.remove(backup_file)

        driver.quit()

        # Save CSVs to data/<flight_type>_flightera folder
        output_dir = os.path.join(DATA_DIR, f"{flight_type}_flightera")
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{flight_type}_{airport_code_iata}_{today}.csv"
        output_path = os.path.join(output_dir, filename)
        all_data.drop_duplicates()
        all_data.to_csv(output_path, index=False)
        print(f"Saved {flight_type} data to: {output_path}")

    return visited_urls, errors