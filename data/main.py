# 




"""
run_all.py

High-level orchestrator that:
1) Runs Flightera arrivals & departures for each airport in a list.
2) Runs Flightradar24 arrivals for each airport.
3) Calls 'clean_and_merge()' to produce the final CSV.
"""

from datetime import datetime, timedelta
import airportsdata
import pandas as pd
import json
import sys
import os

# Import scraping functions
from src.get_flight_by_airport_flightera import crawl_flighttera_airport_flights
from src.get_flight_by_airport_flightradar24 import crawl_flightradar24_airport_flights
from src.get_flight_by_aircraft_flightradar24 import crawl_flightradar24_aircraft_flight
# Import the cleaning function
from src.clean_flight_data import clean_and_merge, clean_aircraft
# Import database insert function
from src.push_to_postgres import push_fligth_schedule_to_postgres

# Import the logger creation function
from src.logger import create_logger

def run_flightera_scrapes(logger, airport_city, airport_iata, airport_icao, start_date, end_date=None):
    base_url = "https://www.flightera.net"
    # Your crawl function returns df plus optional extras
    flightera_arrival_df = crawl_flighttera_airport_flights(
        base_url=base_url,
        airport_city=airport_city,
        airport_code_iata=airport_iata,
        airport_code_icao=airport_icao,
        flight_type="arrival",
        start_date_str=start_date,
        end_date=end_date
    )
    flightera_departure_df = crawl_flighttera_airport_flights(
        base_url=base_url,
        airport_city=airport_city,
        airport_code_iata=airport_iata,
        airport_code_icao=airport_icao,
        flight_type="departure",
        start_date_str=start_date,
        end_date=end_date
    )
    logger.info("Flightera scrapes done for %s: arrivals=%d rows, departures=%d rows",
                airport_iata, len(flightera_arrival_df), len(flightera_departure_df))
    return flightera_arrival_df, flightera_departure_df

def run_flightradar24_scrape(logger, airport_code_iata):
    base_url = "https://www.flightradar24.com"
    df = crawl_flightradar24_airport_flights(base_url, airport_code_iata, flight_type="arrivals")
    return df

def run_flightradar24_aircraft_scrape(logger, aircraft):
    base_url = "https://www.flightradar24.com"
    df = crawl_flightradar24_aircraft_flight(base_url, aircraft)
    return df

def run_schedule_mode(airport_list_iata):
    # Create or get the schedule logger
    logger = create_logger("schedule", "schedule.log")
    logger.info("SCHEDULE mode started with airports: %s", airport_list_iata)

    airports = airportsdata.load("IATA")

    start_date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    # Use today's date as end date (or adjust as needed)
    end_date_str = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    flightera_arrival_dfs = []
    flightera_departure_dfs = []
    flightradar24_dfs = []

    for iata in airport_list_iata:
        if iata not in airports:
            logger.warning("Airport '%s' not found in GLOBAL_AIRPORTS.", iata)
            continue

        city = airports[iata]["city"]
        icao = airports[iata]["icao"]
        logger.info("--- SCRAPING %s (%s), city=%s ---", iata, icao, city)

        flightera_arrival_df, flightera_departure_df = run_flightera_scrapes(
            logger, city, iata, icao, start_date_str, end_date_str
        )
        flightera_arrival_dfs.append(flightera_arrival_df)
        flightera_departure_dfs.append(flightera_departure_df)

        fr24_df = run_flightradar24_scrape(logger, iata)
        flightradar24_dfs.append(fr24_df)

    logger.info("All schedule scraping done. Cleaning data...")
    df = clean_and_merge(flightera_arrival_dfs, flightera_departure_dfs, flightradar24_dfs)
    logger.info("Data merged successfully with %d total rows.", len(df))

    push_fligth_schedule_to_postgres(df)
    logger.info("SCHEDULE mode completed.")

def run_realtime_mode(aircraft):
    logger = create_logger("realtime", "realtime.log")
    logger.info("REALTIME mode started for aircraft: %s", aircraft)

    df = run_flightradar24_aircraft_scrape(logger, aircraft)
    
    if df.empty:
        logger.warning(f"No data found for aircraft: {aircraft}")
        # Make sure to output valid JSON even when empty
        print('[]')  # This is critical
        logger.info("REALTIME mode completed with no data.")
        return
    
    # For non-empty dataframes
    df_cleaned = clean_aircraft(df)
    logger.info("Realtime aircraft data cleaned: %d rows", len(df_cleaned))

    # Ensure proper JSON formatting and print to stdout
    json_array = df_cleaned.to_dict(orient="records")
    json_string = json.dumps(json_array)
    logger.info(f"Outputting JSON data: {json_string[:100]}...")  # Log the start of the output
    print(json_string)  # This is critical - must print to stdout

    logger.info("REALTIME mode completed.")
'''
def run_realtime_mode(aircraft):
    logger = create_logger("realtime", "realtime.log")
    logger.info("REALTIME mode started for aircraft: %s", aircraft)

    df = run_flightradar24_aircraft_scrape(logger, aircraft)
    
    if df.empty:
        logger.warning(f"No data found for aircraft: {aircraft}")
        # Return an empty array as JSON
        print(json.dumps([]))
        logger.info("REALTIME mode completed with no data.")
        return
    
    df_cleaned = clean_aircraft(df)
    logger.info("Realtime aircraft data cleaned: %d rows", len(df_cleaned))

    # Output to console
    json_array = df_cleaned.to_dict(orient="records")
    json_string = json.dumps(json_array)
    logger.info(json_string)
    print(json_string)

    logger.info("REALTIME mode completed.")

def run_realtime_mode(aircraft):
    # Create or get the realtime logger
    logger = create_logger("realtime", "realtime.log")
    logger.info("REALTIME mode started for aircraft: %s", aircraft)

    df = run_flightradar24_aircraft_scrape(logger, aircraft)
    df_cleaned = clean_aircraft(df)
    logger.info("Realtime aircraft data cleaned: %d rows", len(df_cleaned))

    # Output to console if you like
    json_array = df_cleaned.to_dict(orient="records")
    json_string = json.dumps(json_array)
    logger.info(json_string)

    print(json_string)

    logger.info("REALTIME mode completed.")
'''
def main():
    if len(sys.argv) < 2:
        print("Usage: run_all.py '[{...}]'")
        sys.exit(1)

    try:
        input_arg = sys.argv[1]
        commands = json.loads(input_arg)
    except Exception as e:
        print(f"Error parsing input JSON: {e}")
        sys.exit(1)

    for command in commands:
        mode = command.get("mode", "").lower()
        if mode == "schedule":
            airport_list = command.get("airport_list_iata", [])
            if not airport_list:
                print("No airports provided for schedule mode.")
                continue
            run_schedule_mode(airport_list)
        elif mode == "realtime":
            aircraft = command.get("aircraft", None)
            if not aircraft:
                print("No aircraft provided for realtime mode.")
                continue
            run_realtime_mode(aircraft)
        else:
            print(f"Unrecognized mode: {mode}. Valid modes are 'schedule' or 'realtime'.")

if __name__ == "__main__":
    main()
