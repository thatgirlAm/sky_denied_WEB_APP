# SkyDenied

## Installation Guide

### Setting Up the Environment

To set up your environment for running `main.py`:
Make sure to have python version 3.9 or above installed.

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install necessary packages
pip install -r requirements.txt

# Prepare input for main
# Structure for scheudle mode: '[{"mode": "schedule", "airport_list_iata": ["NCL", "DUB"]}]'
## Structure for realtime mode: '[{"mode": "realtime", "aircraft": "n688sl"}]' 

# Run your Python scripts in schedule mode
python main.py '[{"mode": "schedule", "airport_list_iata": ["NCL", "DUB"]}]'
# Or realtime mode
python3 main.py  '[{"mode": "realtime", "aircraft": "n688sl"}]' 

# Expected output from main
# Scheudle mode: Direct push to database
# Realtime mode: A json data structure printed into the cli
# Exmaple:
[
  {
    "flight_date": "2025-04-12",
    "flight_date_utc": "2025-04-12",
    "flight_number_iata": "P9411",
    "tail_number": " N688SL",
    "airline": "Asia Pacific Airlines",
    "status": "Landed",
    "depart_from": "Chuuk",
    "depart_from_iata": "TKK",
    "depart_from_icao": "PTKK",
    "scheduled_departure_local": "2025-04-12 18:00",
    "scheduled_departure_local_tz": "Pacific/Chuuk",
    "scheduled_departure_utc": "2025-04-12 08:00",
    "actual_departure_local": "2025-04-12 18:10",
    "actual_departure_local_tz": "Pacific/Guam",
    "actual_departure_utc": "2025-04-12 08:10",
    "arrive_at": "Guam",
    "arrive_at_iata": "GUM",
    "arrive_at_icao": "Pacific/Guam",
    "scheduled_arrival_local": "2025-04-12 19:45",
    "scheduled_arrival_local_tz": "Pacific/Guam",
    "scheduled_arrival_utc": "2025-04-12 09:45",
    "actual_arrival_local": "2025-04-12 18:41",
    "actual_arrival_utc": "2025-04-12 08:41",
    "schedule_duration": "1h 45m",
    "actual_duration": "31m"
  }
]


# Deactivate the environment
deactivate
```

## Project Structure
### Data Cleaning & Utilities
- `main.py` - High-level entry point. Orchestrates the pipeline based on command-line input
- `clean_flight_data.py` - Cleans and merges flight datasets.
- `logger.py` - Loss function implementation
- `push_to_postgres.py` - Handles database interaction.
- `selenium_utility.py` - Sets up stealth Selenium drivers systems. 
### Data Scrapers
- `get_flight_by_airport_flightera.py` - Scrapes Flightera for airport-level flights (arrivals or departures) over time.

- `get_flight_by_airport_flightradar24.py` - Scrapes Flightradar24 airport arrivals.

- `get_flight_by_aircraft_flightradar24.py` - Scrapes Flightradar24 for a specific aircraft’s recent flight history.

- `get_flight_by_country_flightera.py` - Scraper for retrieving flight data by country from Flightera. (Currently not used)

- `parse_flight_data.py` - Centralized HTML parsers for Flightera and Flightradar24 pages. Transforms raw HTML into structured Pandas DataFrames.

## Important Note
- Make sure to setup .env file for database connection
POSTGRES_HOST= ""
POSTGRES_PORT= ""
POSTGRES_DB= ""
POSTGRES_USER= ""
POSTGRES_PASSWORD= ""
- Check log file if there are any issues.
- Potentially have to handel SSL certificate
