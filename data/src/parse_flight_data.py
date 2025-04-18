"""
parse_flight_data.py

Centralizes functions for parsing HTML flight data
from Flightera and Flightradar24.
"""

# from bs4 import BeautifulSoup
import re
import pandas as pd
from dateutil import parser
from datetime import datetime


def parse_flightera(soup, mode="arrival"):
    rows = soup.find_all("tr", class_=lambda c: c and ("bg-white" in c or "bg-gray-50" in c))
    flight_data = []

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 7:
            continue

        # --- Flight Date + Status ---
        flight_date = ""
        date_links = tds[0].find_all("a")
        if len(date_links) > 1:
            href = date_links[1].get("href", "")
            match = re.search(r'/(\d{4}-\d{2}-\d{2})$', href)
            flight_date = match.group(1) if match else ""
        status_tag = tds[0].find("span", class_=lambda c: c and "bg-" in c)
        status = status_tag.get_text(strip=True) if status_tag else ""

        # --- Flight Numbers and Airline ---
        a_tags = tds[1].find_all("a")
        flight_number_iata = a_tags[0].get_text(strip=True) if a_tags else ""
        icao_span = tds[1].find_all("span", class_="text-gray-700")
        flight_number_icao = icao_span[0].get_text(strip=True) if icao_span else ""
        airline = a_tags[1].get_text(strip=True) if len(a_tags) > 1 else ""

        # --- Location Data ---
        location_span = tds[2].find("span", class_=lambda c: c and "text-xs" in c)
        location_text = location_span.get_text(strip=True) if location_span else ""

        code_span = tds[2].find("span", class_=lambda c: c and "whitespace-nowrap" in c)
        code_text = code_span.get_text(strip=True) if code_span else ""
        code_text = code_text.replace("(", "").replace(")", "") if code_text else ""
        code_parts = code_text.split("/") if code_text else ["", ""]
        code_iata = code_parts[0].strip()
        code_icao = code_parts[1].strip() if len(code_parts) > 1 else ""

        # --- Scheduled Time (Local + UTC) ---
        schedule_local_tz = ""
        scheduled_local = ""
        scheduled_utc = ""
        local_span = tds[3].find("span", class_="whitespace-nowrap")
        if local_span:
            tz_span = local_span.find("span", class_="text-xs")
            schedule_local_tz = tz_span.get_text(strip=True) if tz_span else ""
            if tz_span:
                tz_span.decompose()
            local_time = local_span.get_text(strip=True)
            scheduled_local = parser.parse(local_time, dayfirst=True).strftime("%Y-%m-%d %H:%M")

        utc_spans = tds[3].find_all("span", class_="text-xs")
        if utc_spans:
            scheduled_utc = utc_spans[-1].get_text(strip=True).replace("UTC", "").strip()
            scheduled_utc = parser.parse(scheduled_utc, dayfirst=True).strftime("%Y-%m-%d %H:%M")

        # --- Actual Departure ---
        actual_departure_local_tz = ""
        actual_departure_local = ""
        actual_dep_span = tds[4].find("span", class_="whitespace-nowrap")
        if actual_dep_span:
            tz_span = actual_dep_span.find("span", class_="text-xs")
            actual_departure_local_tz = tz_span.get_text(strip=True) if tz_span else ""
            if tz_span:
                tz_span.decompose()
            actual_time = actual_dep_span.get_text(strip=True)
            actual_departure_local = parser.parse(actual_time, dayfirst=True).strftime("%Y-%m-%d %H:%M")

        # --- Actual Departure Delay ---
        departure_delay = ""
        departure_delay_span = tds[4].find("span", class_=lambda c: c and "inline-flex" in c)
        if departure_delay_span:
            departure_delay = departure_delay_span.get_text(strip=True)

        # --- Actual Arrival ---
        actual_arrival_local_tz = ""
        actual_arrival_local = ""
        actual_arrival_span = tds[5].find("span", class_="whitespace-nowrap")
        if actual_arrival_span:
            tz_span = actual_arrival_span.find("span", class_="text-xs")
            if tz_span:
                actual_arrival_local_tz = tz_span.get_text(strip=True)
                tz_span.decompose()
            actual_time = actual_arrival_span.get_text(strip=True)
            actual_arrival_local = parser.parse(actual_time, dayfirst=True).strftime("%Y-%m-%d %H:%M")

        # --- Actual Arrival Delay ---
        arrival_delay = ""
        arrival_delay_span = tds[5].find("span", class_=lambda c: c and "inline-flex" in c)
        if arrival_delay_span:
            arrival_delay = arrival_delay_span.get_text(strip=True)

        # --- Duration ---
        duration_text = tds[6].get_text(strip=True)

        # --- Build Flight Record ---
        flight_record = {
            "flight_date": flight_date,
            "status": status,
            "flight_number_iata": flight_number_iata,
            "flight_number_icao": flight_number_icao,
            "airline": airline
        }

        if mode == "arrival":
            flight_record["depart_from"] = location_text
            flight_record["depart_from_iata"] = code_iata
            flight_record["depart_from_icao"] = code_icao
            flight_record["scheduled_arrival_local"] = scheduled_local
            flight_record["scheduled_arrival_local_tz"] = schedule_local_tz
            flight_record["scheduled_arrival_utc"] = scheduled_utc
        else:  # mode == "departure"
            flight_record["arrive_at"] = location_text
            flight_record["arrive_at_iata"] = code_iata
            flight_record["arrive_at_icao"] = code_icao
            flight_record["scheduled_departure_local"] = scheduled_local
            flight_record["scheduled_departure_local_tz"] = schedule_local_tz
            flight_record["scheduled_departure_utc"] = scheduled_utc

        flight_record["actual_departure_local"] = actual_departure_local
        flight_record["actual_departure_local_tz"] = actual_departure_local_tz
        flight_record["departure_delay"] = departure_delay
        flight_record["actual_arrival_local"] = actual_arrival_local
        flight_record["actual_arrival_local_tz"] = actual_arrival_local_tz
        flight_record["arrival_delay"] = arrival_delay
        flight_record["duration"] = duration_text

        flight_data.append(flight_record)

    return pd.DataFrame(flight_data)

def parse_flightradar24(soup, mode="arrival"):
    table = soup.find("table", class_="table table-condensed table-hover data-table m-n-t-15")
    if table is None:
        return pd.DataFrame()  # Return empty DataFrame if table is not found

    rows = table.find_all("tr")
    flight_data = []
    flight_date = None  # We'll update this whenever we see a row-date-separator

    for row in rows:
        classes = row.get("class", [])
        # --- Flight Date Separator ---
        if "row-date-separator" in classes:
            # Extract date text from: <td colspan="7">Tuesday, Apr 01</td>
            date_td = row.find("td", colspan="7")
            if date_td:
                flight_date_raw = date_td.get_text(strip=True)  # e.g. "Tuesday, Apr 01"
                # remove weekday
                flight_date_no_days = flight_date_raw.split(", ")[1]  # "Apr 01"
                current_year = datetime.now().year
                full_date_str = f"{flight_date_no_days} {current_year}"
                parsed_date = datetime.strptime(full_date_str, "%b %d %Y")
                flight_date = parsed_date.strftime("%Y-%m-%d")
            continue

        # --- Process Only Flight Rows ---
        if "hidden-xs" in classes and "ng-scope" in classes:
            cols = row.find_all("td")
            if len(cols) < 7:
                continue
        else:
            continue  # skip non-flight rows

        # --- Flight Numbers ---
        flight_number_iata = cols[1].get_text(strip=True)  # e.g. "FR461"

        # --- Airport Code ---
        airport_location = cols[2].get_text(" ", strip=True)  # e.g. "Milan (BGY)"
        try:
            code_iata = airport_location.split("(")[1].split(")")[0]  # "BGY"
        except IndexError:
            code_iata = None

        # --- Tail Number (Optional) ---
        aircraft_info = cols[4].get_text(" ", strip=True)  # e.g. "B38M (9H-VUE)"
        if "(" in aircraft_info and ")" in aircraft_info:
            tail_number = aircraft_info.split("(")[1].split(")")[0]
        else:
            tail_number = aircraft_info

        # --- Build Flight Record ---
        flight_record = {
            "flight_number_iata": flight_number_iata,
            "tail_number": tail_number
        }

        if mode == "arrival":
            flight_record["scheduled_arrival_date_local"] = flight_date
            flight_record["depart_from_iata"] = code_iata
        else:
            flight_record["scheduled_departure_date_local"] = flight_date
            flight_record["arrive_at_iata"] = code_iata

        flight_data.append(flight_record)

    return pd.DataFrame(flight_data)

def split_status(val):
    if " " in val:
        parts = val.split(" ", 1)
        return pd.Series([parts[1], parts[0]])
    return pd.Series(["", val])

def parse_flightradar24_aircraft(soup):
    info_rows = soup.select("#cnt-aircraft-info .row")
    airline = ""
    for row in info_rows:
        label = row.find("label")
        if label and label.get_text(strip=True).upper() == "AIRLINE":
            airline_span = row.find("span", class_="details")
            if airline_span:
                airline = airline_span.get_text(strip=True)
    
    tail_number = soup.find_all("h1")[0].get_text(strip=True).split("-",1)[1].strip()
    # Find all rows in the flight history table
    rows = soup.find_all("tr", class_="data-row")
    flight_history = []

    def convert_to_24h(time_str):
        if not time_str or not any(char.isdigit() for char in time_str):
            return None  # No numbers in the string — probably not a time
        try:
           # Try parsing it as 12-hour format to validate
            if "AM" in time_str.upper() or "PM" in time_str.upper():
                return datetime.strptime(time_str.strip(), "%I:%M %p").strftime("%H:%M")
            else:
                # Try parsing it as 24-hour format to validate
                datetime.strptime(time_str.strip(), "%H:%M")
                return time_str.strip()
        except ValueError:
            return None

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 13:
            continue
        flight_date = cells[2].get_text(strip=True)
        flight_date = pd.to_datetime(flight_date, format="%d %b %Y").strftime("%Y-%m-%d")
        depart_from = cells[3].get_text(strip=True).rsplit("(", 1)[0].strip()
        depart_from_iata = cells[3].find("a")
        depart_from_iata = depart_from_iata.get_text(strip=True).strip("()") if depart_from_iata else ""

        arrive_at = cells[4].get_text(strip=True).rsplit("(", 1)[0].strip()
        arrive_at_iata = cells[4].find("a")
        arrive_at_iata = arrive_at_iata.get_text(strip=True).strip("()") if arrive_at_iata else ""

        flight_number_iata = cells[5].get_text(strip=True)
        duration = cells[6].get_text(strip=True)
        scheduled_departure_local = convert_to_24h(cells[7].get_text(strip=True))
        actual_departure_local = convert_to_24h(cells[8].get_text(strip=True))
        scheduled_arrival_local = convert_to_24h(cells[9].get_text(strip=True))

        status = cells[11].get_text(strip=True)
        parts = status.split(" ", 1)
        status = parts[0]
        actual_arrival_local = convert_to_24h(parts[1]) if len(parts) > 1 else ""

        flight_history.append({
            "flight_date": flight_date,
            "airline": airline,
            "tail_number": tail_number,
            "depart_from": depart_from,
            "depart_from_iata": depart_from_iata,
            "arrive_at": arrive_at,
            "arrive_at_iata": arrive_at_iata,
            "flight_number_iata": flight_number_iata,
            "duration": duration,
            "scheduled_departure_local": f"{flight_date} {scheduled_departure_local}" if scheduled_departure_local else "",
            "actual_departure_local": actual_departure_local,
            "scheduled_arrival_local": scheduled_arrival_local,
            "actual_arrival_local": actual_arrival_local,
            "status": status
        })
    
    return pd.DataFrame(flight_history)
