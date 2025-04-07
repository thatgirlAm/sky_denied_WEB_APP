"""
run_all.py

High-level orchestrator that:
1) Runs Flightera arrivals & departures for each airport in a list.
2) Runs Flightradar24 arrivals for each airport.
3) Calls 'clean_and_merge()' to produce the final CSV.
"""

import datetime
import airportsdata
import os

# Import your scraping functions
from src.get_flight_by_airport_flightera import crawl_airport_flights
from src.get_flight_by_airport_flightradar24 import crawl_flight_type
# Import the cleaning function
from src.clean_flight_data import clean_and_merge
# Import database insert function
from src.push_to_postgres import push_fligth_schedule_to_postgres


def run_flightera_scrapes(airport_city, airport_iata, airport_icao, start_date, end_date=None):
    base_url = "https://www.flightera.net"
    crawl_airport_flights(
        base_url=base_url,
        airport_city=airport_city,
        airport_code_iata = airport_iata,
        airport_code_icao=airport_icao,
        flight_type="arrival",
        start_date_str=start_date,
        end_date=end_date
    )
    crawl_airport_flights(
        base_url=base_url,
        airport_city=airport_city,
        airport_code_iata = airport_iata,
        airport_code_icao=airport_icao,
        flight_type="departure",
        start_date_str=start_date,
        end_date=end_date
    )

def run_flightradar24_scrape(airport_code_iata):
    base_url = "https://www.flightradar24.com"
    crawl_flight_type(base_url, airport_code_iata, flight_type="arrivals")

def main():
    # airports_list = ["LAS","LAX"]
    # start_date_str = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    # end_date_str = (datetime.datetime.now() - datetime.timedelta(days=0)).strftime("%Y-%m-%d")

    # airports_info = airportsdata.load("IATA")

    # for iata in airports_list:
    #     city = airports_info[iata]["city"]
    #     icao = airports_info[iata]["icao"]
    #     print(f"--- SCRAPING {iata} => {icao}, city={city} ---")
    #     run_flightera_scrapes(city, iata ,icao, start_date_str, end_date_str)
    #     run_flightradar24_scrape(iata)

    # # Merge final data
    # print("All scraping done. Cleaning data now...")
    df = clean_and_merge()
    print("Data merged successfully.")
    today = datetime.datetime.now().date()
    # csv_file = os.path.abspath(os.path.join("data", f"flight_schedule_{today}.csv"))
    # # Now call push_to_postgres with the CSV path
    # push_fligth_schedule_to_postgres(csv_path=csv_file)
    
if __name__ == "__main__":
    main()