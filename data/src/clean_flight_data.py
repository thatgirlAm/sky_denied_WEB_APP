"""
clean_flight_data.py

Reads the scraped CSVs from their respective folders,
merges arrival & departure data from Flightera, 
merges with Flightradar24 data, 
and performs additional cleaning/UTC conversion steps.
"""

import pandas as pd
import os
import airportsdata
import pytz
from datetime import datetime, time, timedelta

# Where the data folders and final CSV will be stored
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
GLOBAL_AIRPORTS = airportsdata.load('IATA')

# def read_all_csv_from_folder(folder_path):
#     if not os.path.exists(folder_path):
#         print(f"Folder does not exist: {folder_path}")
#         return pd.DataFrame()
    
#     all_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
#     dataframes = []
#     for file in all_files:
#         file_path = os.path.join(folder_path, file)
#         try:
#             df = pd.read_csv(file_path)
#             dataframes.append(df)
#         except Exception as e:
#             print(f"Failed to read {file}: {e}")

#     if not dataframes:
#         print(f"No valid CSV files found in {folder_path}")
#         return pd.DataFrame()

#     return pd.concat(dataframes, ignore_index=True)

def to_utc(local_str, iata_code, fmt="%Y-%m-%d %H:%M"):
    if pd.isna(local_str) or local_str == '' or pd.isna(iata_code) or iata_code == '':
        return None
    tz_name = GLOBAL_AIRPORTS[iata_code]['tz']
    naive_local_dt = datetime.strptime(local_str, fmt)
    local_tz = pytz.timezone(tz_name)
    local_aware_dt = local_tz.localize(naive_local_dt)
    return local_aware_dt.astimezone(pytz.utc).strftime(fmt)

def infer_different_tz_date(departure_date, depart_from_iata, arrival_time_str, arrive_at_iata):
    if not departure_date or not arrival_time_str or pd.isna(departure_date) or pd.isna(arrival_time_str):
            return None
    departure_date = datetime.strptime(departure_date.strip(), "%Y-%m-%d %H:%M")

    if depart_from_iata not in GLOBAL_AIRPORTS or arrive_at_iata not in GLOBAL_AIRPORTS:
            return None
    
    schedule_departure_local_tz_str = GLOBAL_AIRPORTS[depart_from_iata]['tz']
    schedule_departure_local_tz = pytz.timezone(schedule_departure_local_tz_str)
    departure_date = schedule_departure_local_tz.localize(departure_date)

    schedule_arrival_local_tz = GLOBAL_AIRPORTS[arrive_at_iata]['tz']


    # 1) Convert the departure moment to the arrival tz
    schedule_arrival_local_tz = pytz.timezone(schedule_arrival_local_tz)
    departure_in_arrival_tz = departure_date.astimezone(schedule_arrival_local_tz)
    
    # 2) Parse the "HH:MM" arrival time
    hh, mm = arrival_time_str.split(":")
    arrival_time_only = time(int(hh), int(mm))
    
    # 3) Combine that time with the *departure date (in arrival tz)*
    #    to make a tentative arrival datetime (still in arrival tz).
    candidate_date = departure_in_arrival_tz.date()
    # Naive datetime for the candidate arrival day + time
    naive_arrival_dt = datetime.combine(candidate_date, arrival_time_only)
    # Localize it to the arrival tz with pytz
    candidate_arrival_dt = schedule_arrival_local_tz.localize(naive_arrival_dt)
    
    # 4) If candidate_arr_dt is before (or equal to) dep_in_arr_tz,
    #    assume the actual arrival is the *next* day in that time zone.
    if candidate_arrival_dt <= departure_in_arrival_tz:
        candidate_arrival_dt += timedelta(days=1)
    
    return candidate_arrival_dt.strftime("%Y-%m-%d %H:%M")

def infer_same_tz_date(scheduled_date_local, actual_time_str):
    """
    Infers the local date/time for actual departure/arrival,
    accounting for crossing midnight in *either* direction.
    """
    if not scheduled_date_local or not actual_time_str:
                return None
    # 1) Parse scheduled date/time
    #    e.g. "YYYY-MM-DD" + "HH:MM" in 24-hour format
    scheduled_date_local = datetime.strptime(
        scheduled_date_local, "%Y-%m-%d %H:%M"
    )

    # 2) Parse the actual clock time
    actual_time_obj = datetime.strptime(actual_time_str, "%H:%M").time()

    # 3) Combine the scheduled date with actual clock time
    candidate_dt = datetime.combine(scheduled_date_local.date(), actual_time_obj)
    
    # 4) If candidate is "far before" scheduled, it might be next day
    if candidate_dt < scheduled_date_local and (scheduled_date_local - candidate_dt) > timedelta(hours=12):
        # e.g. we require a threshold (2 hours, 6 hours, etc.) depending on your flights
        candidate_dt += timedelta(days=1)

    # 5) If candidate is "far after" scheduled, it might be previous day
    elif candidate_dt > scheduled_date_local and (candidate_dt - scheduled_date_local) > timedelta(hours=12):
        candidate_dt -= timedelta(days=1)

    return candidate_dt.strftime("%Y-%m-%d %H:%M")

def airport_info_look_up(iata_code,output_column='icao'):
    if pd.isna(iata_code) or iata_code == '':
        return ""
    return GLOBAL_AIRPORTS[iata_code][output_column]

def format_duration(td):
    if pd.isna(td):
        return None
    td = pd.to_timedelta(td)
    parts = []
    if td.days:
        parts.append(f"{td.days}d")
    if td.components.hours:
        parts.append(f"{td.components.hours}h")
    if td.components.minutes:
        parts.append(f"{td.components.minutes}m")
    return " ".join(parts)

def infer_arrival_datetime(departure_date, arr_time_str, arr_tz_str):
    # 1) Convert the departure moment to the arrival tz
    arr_tz = pytz.timezone(arr_tz_str)
    dep_in_arr_tz = departure_date.astimezone(arr_tz)
    
    # 2) Parse the "HH:MM" arrival time
    hh, mm = arr_time_str.split(":")
    arr_time_only = time(int(hh), int(mm))
    
    # 3) Combine that time with the *departure date (in arrival tz)*
    #    to make a tentative arrival datetime (still in arrival tz).
    candidate_date = dep_in_arr_tz.date()
    # Naive datetime for the candidate arrival day + time
    naive_arrival_dt = datetime.combine(candidate_date, arr_time_only)
    # Localize it to the arrival tz with pytz
    candidate_arr_dt = arr_tz.localize(naive_arrival_dt)
    
    # 4) If candidate_arr_dt is before (or equal to) dep_in_arr_tz,
    #    assume the actual arrival is the *next* day in that time zone.
    if candidate_arr_dt <= dep_in_arr_tz:
        candidate_arr_dt += timedelta(days=1)
    
    return candidate_arr_dt


def clean_and_merge(flightera_arrival_dfs, flightera_departure_dfs, flightradar24_dfs):
    """
    Merges arrivals & departures from Flightera,
    merges with Flightradar24 data, 
    outputs final flight_schedule.csv in the data folder.
    """
    # # Read from data/arrival_flightera
    # arrival_folder = os.path.join(DATA_DIR, "arrival_flightera")
    # # Read from data/departure_flightera
    # departure_folder = os.path.join(DATA_DIR, "departure_flightera")
    # # Read from data/arrivals_flightradar24
    # arrivals_fr24_folder = os.path.join(DATA_DIR, "arrivals_flightradar24")



    # print(f"Reading arrival_flightera CSVs from {arrival_folder}...")
    # arrival_df = read_all_csv_from_folder(arrival_folder)

    # print(f"Reading departure_flightera CSVs from {departure_folder}...")
    # departure_df = read_all_csv_from_folder(departure_folder)

    # print(f"Reading arrivals_flightradar24 CSVs from {arrivals_fr24_folder}...")
    # arrival_flightradar24_df = read_all_csv_from_folder(arrivals_fr24_folder)

    # Concatenate each group into a single DataFrame
    arrival_df = pd.concat(flightera_arrival_dfs, ignore_index=True)
    departure_df = pd.concat(flightera_departure_dfs, ignore_index=True)
    arrival_flightradar24_df = pd.concat(flightradar24_dfs, ignore_index=True)

    # Depuplicated
    arrival_df_dedup = arrival_df.drop_duplicates()
    departure_df_dedup = departure_df.drop_duplicates()
    arrival_flightradar24_df_dedup = arrival_flightradar24_df.drop_duplicates()

    flight_schedule = arrival_df_dedup.merge(
        departure_df_dedup,
        on=["flight_date", "flight_number_iata"],
        how="inner",
        suffixes=("", "_dep")
    )

    flight_schedule = flight_schedule[flight_schedule["depart_from_iata"] != flight_schedule["arrive_at_iata"]]
    flight_schedule = flight_schedule[flight_schedule["depart_from_iata"] != flight_schedule["arrive_at_iata"]]

    cols_to_drop = [
        col for col in flight_schedule.columns
        if col.endswith("_dep") and col[:-4] in arrival_df_dedup.columns
    ]
    flight_schedule.drop(columns=cols_to_drop, inplace=True)
    # flight_schedule["scheduled_arrival_date_local"] = flight_schedule["scheduled_arrival_local"].astype(str).str[:10]
    # Merge with FR24
    flight_schedule = flight_schedule.merge(
        arrival_flightradar24_df_dedup,
        left_on=["scheduled_arrival_local","flight_number_iata", "depart_from_iata"],
        right_on=["scheduled_arrival_local", "flight_number_iata", "depart_from_iata"],
        how="left",
        suffixes=("", "_fr24")
    )

    cols_to_drop = [
        col for col in flight_schedule.columns
        if col.endswith("_fr24") and col[:-5] in flight_schedule.columns
    ]
    flight_schedule.drop(columns=cols_to_drop, inplace=True)


    flight_schedule.rename(columns={"tail_number_fr24": "tail_number"}, inplace=True)

    flight_schedule["actual_departure_utc"] = flight_schedule.apply(
        lambda row: to_utc(
            row.get("actual_departure_local", ""),
            row.get("depart_from_iata", "")
        ),
        axis=1
    )
    flight_schedule["actual_arrival_utc"] = flight_schedule.apply(
        lambda row: to_utc(
            row.get("actual_arrival_local", ""),
            row.get("arrive_at_iata", "")
        ),
        axis=1
    )

    flight_schedule["scheduled_departure_utc"] = pd.to_datetime(
    flight_schedule["scheduled_departure_utc"], errors="coerce"
    )
    flight_schedule["scheduled_arrival_utc"] = pd.to_datetime(
        flight_schedule["scheduled_arrival_utc"], errors="coerce"
    )
    flight_schedule["flight_date_utc"] = flight_schedule["scheduled_departure_utc"].dt.date


    # Additional depulication logic
    flight_schedule = flight_schedule[flight_schedule["depart_from_iata"] != flight_schedule["arrive_at_iata"]] # Can not fly to the same airport
    flight_schedule = flight_schedule[flight_schedule["scheduled_departure_utc"] <= flight_schedule["scheduled_arrival_utc"]] # Departure time can not be bigger than arrival time
    # Since it's a many to many join there are possible duplication when the first departure flight joins with a future flight of the same day
    # We need to get rid of the edge case
    flight_schedule["last_scheduled_departure_utc"] = (
    flight_schedule
    .sort_values(by=["flight_date_utc", "flight_number_iata", "depart_from_iata" , "arrive_at_iata", "scheduled_departure_utc"])
    .groupby(["flight_date_utc", "flight_number_iata", "depart_from_iata" , "arrive_at_iata", "scheduled_departure_utc"])["scheduled_departure_utc"]
    .shift(1)
    )

    flight_schedule["last_scheduled_arrival_utc"] = (
    flight_schedule
    .sort_values(by=["flight_date_utc", "flight_number_iata", "depart_from_iata" , "arrive_at_iata"])
    .groupby(["flight_date_utc", "flight_number_iata", "depart_from_iata" , "arrive_at_iata"])["scheduled_arrival_utc"]
    .shift(1)
    )

    flight_schedule = flight_schedule[(flight_schedule["scheduled_departure_utc"] != flight_schedule["last_scheduled_departure_utc"]) &
                         (
                          (flight_schedule["scheduled_arrival_utc"] <= flight_schedule["last_scheduled_arrival_utc"]) |
                          (flight_schedule["last_scheduled_arrival_utc"].isnull())
                          )
                          ]
    flight_schedule["scheduled_departure_local"] = pd.to_datetime(flight_schedule["scheduled_departure_local"], format= "%Y-%m-%d %H:%M", errors="coerce")
    flight_schedule["scheduled_arrival_local"] = pd.to_datetime(flight_schedule["scheduled_arrival_local"], format= "%Y-%m-%d %H:%M", errors="coerce")
    flight_schedule["actual_departure_local"] = pd.to_datetime(flight_schedule["actual_departure_local"], format= "%Y-%m-%d %H:%M", errors="coerce")
    flight_schedule["actual_arrival_local"] = pd.to_datetime(flight_schedule["actual_arrival_local"], format= "%Y-%m-%d %H:%M", errors="coerce")

    flight_schedule["scheduled_departure_local_tz"] = flight_schedule.apply(lambda row: airport_info_look_up(row["depart_from_iata"],"tz"), axis=1)
    flight_schedule["actual_departure_local_tz"] = flight_schedule["scheduled_departure_local_tz"]
    flight_schedule["scheduled_arrival_local_tz"] = flight_schedule.apply(lambda row: airport_info_look_up(row["arrive_at_iata"],"tz"), axis=1)
    flight_schedule["actual_arrival_local_tz"] = flight_schedule["scheduled_departure_local_tz"]


    desired_columns = [
    "flight_date",
    "flight_date_utc",
    "flight_number_iata",
    "flight_number_icao",
    "tail_number",
    "airline",
    "status",
    
    # Departure info
    "depart_from",
    "depart_from_iata",
    "depart_from_icao",
    "scheduled_departure_local",
    "scheduled_departure_local_tz",
    "scheduled_departure_utc",
    "actual_departure_local",
    "actual_departure_local_tz",
    "actual_departure_utc",
    
    # Arrival info
    "arrive_at",
    "arrive_at_iata",
    "arrive_at_icao",
    "scheduled_arrival_local",
    "scheduled_arrival_local_tz",
    "scheduled_arrival_utc",
    "actual_arrival_local",
    "actual_arrival_local_tz",
    "actual_arrival_utc",
    
    # Duration
    "duration"
    ]   

    flight_schedule = flight_schedule[[c for c in desired_columns if c in flight_schedule.columns]]
    flight_schedule = flight_schedule.sort_values(by='scheduled_departure_utc', ascending=True)
    today = datetime.now().date()
    # Write the final merged CSV
    # output_csv = os.path.join(DATA_DIR, f"flight_schedule_{today}.csv")
    # flight_schedule.to_csv(output_csv, index=False)
    return flight_schedule



def clean_aircraft(df):
    df["scheduled_arrival_local"] = df.apply(lambda row: infer_different_tz_date(row["scheduled_departure_local"],
                                                                  row["depart_from_iata"],
                                                                  row["scheduled_arrival_local"],
                                                                  row["arrive_at_iata"]
                                                                  ), axis=1
                                            )
    df["actual_departure_local"] = df.apply(lambda row: infer_same_tz_date(row["scheduled_departure_local"],
                                                                           row["actual_departure_local"]
                                                                           ), axis=1
                                            )
    df["actual_arrival_local"] = df.apply(lambda row: infer_different_tz_date(row["actual_departure_local"],
                                                                  row["depart_from_iata"],
                                                                  row["actual_arrival_local"],
                                                                  row["arrive_at_iata"]
                                                                  ), axis=1
                                            )
    df["flight_date_utc"] = df.apply(lambda row: to_utc(row["scheduled_departure_local"],
                                                        row["depart_from_iata"],
                                                        ), axis=1
                                                        )
    df["flight_date_utc"] = pd.to_datetime(df["flight_date_utc"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["depart_from_icao"] = df.apply(lambda row: airport_info_look_up(row["depart_from_iata"],"icao"), axis=1)
    df["scheduled_departure_local_tz"] = df.apply(lambda row: airport_info_look_up(row["depart_from_iata"],"tz"), axis=1)
    df["scheduled_departure_utc"] = df.apply(lambda row: to_utc(row["scheduled_departure_local"],row["depart_from_iata"]), axis=1)
    df["actual_departure_local_tz"] = df["scheduled_departure_local_tz"]
    df["actual_departure_utc"] =  df.apply(lambda row: to_utc(row["actual_departure_local"],row["depart_from_iata"]), axis=1)
    df["arrive_at_icao"] = df.apply(lambda row: airport_info_look_up(row["arrive_at_iata"],"tz"), axis=1)
    df["scheduled_arrival_local_tz"] = df.apply(lambda row: airport_info_look_up(row["arrive_at_iata"],"tz"), axis=1)
    df["scheduled_arrival_utc"] = df.apply(lambda row: to_utc(row["scheduled_arrival_local"],row["arrive_at_iata"]), axis=1)
    df["actual_departure_local_tz"] = df["scheduled_arrival_local_tz"]
    df["actual_arrival_utc"] = df.apply(lambda row: to_utc(row["actual_arrival_local"],row["arrive_at_iata"]), axis=1)
    df["schedule_duration"] = pd.to_datetime(df["scheduled_arrival_utc"],format="%Y-%m-%d %H:%M") - pd.to_datetime(df["scheduled_departure_utc"],format="%Y-%m-%d %H:%M")
    df["actual_duration"] = pd.to_datetime(df["actual_arrival_utc"],format="%Y-%m-%d %H:%M") - pd.to_datetime(df["actual_departure_utc"],format="%Y-%m-%d %H:%M")
    df["schedule_duration"] = pd.to_timedelta(df["schedule_duration"], errors="coerce").apply(format_duration)
    df["actual_duration"] = pd.to_timedelta(df["actual_duration"], errors="coerce").apply(format_duration)

    desired_columns = [
        "flight_date",
        "flight_date_utc",
        "flight_number_iata",
        "flight_number_icao",
        "tail_number",
        "airline",
        "airline_code",
        "status",
        "depart_from",
        "depart_from_iata",
        "depart_from_icao",
        "scheduled_departure_local",
        "scheduled_departure_local_tz",
        "scheduled_departure_utc",
        "actual_departure_local",
        "actual_departure_local_tz",
        "actual_departure_utc",
        "arrive_at",
        "arrive_at_iata",
        "arrive_at_icao",
        "scheduled_arrival_local",
        "scheduled_arrival_local_tz",
        "scheduled_arrival_utc",
        "actual_arrival_local",
        "actual_arrival_local_tz",
        "actual_arrival_utc",
        "schedule_duration",
        "actual_duration"
    ]

    # Create a new DataFrame with only the desired columns
    df_reorganized = df[[col for col in desired_columns if col in df.columns]]
    df_reorganized = df_reorganized.where(pd.notnull(df_reorganized), None)
    # df_reorganized = df_reorganized.sort_values(by='scheduled_departure_utc', ascending=True)

    return df_reorganized
