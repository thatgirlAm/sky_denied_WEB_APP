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
import datetime

# Where the data folders and final CSV will be stored
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def read_all_csv_from_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return pd.DataFrame()
    
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    dataframes = []
    for file in all_files:
        file_path = os.path.join(folder_path, file)
        try:
            df = pd.read_csv(file_path)
            dataframes.append(df)
        except Exception as e:
            print(f"Failed to read {file}: {e}")

    if not dataframes:
        print(f"No valid CSV files found in {folder_path}")
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)

def to_utc(local_str, iata_code, fmt="%Y-%m-%d %H:%M"):
    if pd.isna(local_str) or local_str == '' or pd.isna(iata_code) or iata_code == '':
        return ""
    airports = airportsdata.load('IATA')
    tz_name = airports[iata_code]['tz']
    naive_local_dt = datetime.datetime.strptime(local_str, fmt)
    local_tz = pytz.timezone(tz_name)
    local_aware_dt = local_tz.localize(naive_local_dt)
    return local_aware_dt.astimezone(pytz.utc).strftime(fmt)

def clean_and_merge():
    """
    Merges arrivals & departures from Flightera,
    merges with Flightradar24 data, 
    outputs final flight_schedule.csv in the data folder.
    """
    # Read from data/arrival_flightera
    arrival_folder = os.path.join(DATA_DIR, "arrival_flightera")
    # Read from data/departure_flightera
    departure_folder = os.path.join(DATA_DIR, "departure_flightera")
    # Read from data/arrivals_flightradar24
    arrivals_fr24_folder = os.path.join(DATA_DIR, "arrivals_flightradar24")

    print(f"Reading arrival_flightera CSVs from {arrival_folder}...")
    arrival_df = read_all_csv_from_folder(arrival_folder)

    print(f"Reading departure_flightera CSVs from {departure_folder}...")
    departure_df = read_all_csv_from_folder(departure_folder)

    print(f"Reading arrivals_flightradar24 CSVs from {arrivals_fr24_folder}...")
    arrival_flightradar24_df = read_all_csv_from_folder(arrivals_fr24_folder)

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
    flight_schedule["scheduled_arrival_date_local"] = flight_schedule["scheduled_arrival_local"].astype(str).str[:10]
    # Merge with FR24
    flight_schedule = flight_schedule.merge(
        arrival_flightradar24_df_dedup,
        left_on=["scheduled_arrival_date_local","flight_number_iata", "depart_from_iata"],
        right_on=["scheduled_arrival_date_local", "flight_number_iata", "depart_from_iata"],
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
    today = datetime.datetime.now().date()
    # Write the final merged CSV
    output_csv = os.path.join(DATA_DIR, f"flight_schedule_{today}.csv")
    flight_schedule.to_csv(output_csv, index=False)
    return flight_schedule

# def clean_and_merge():
#     arrival_folder = os.path.join(DATA_DIR, "arrival_flightera")
#     departure_folder = os.path.join(DATA_DIR, "departure_flightera")
#     arrivals_fr24_folder = os.path.join(DATA_DIR, "arrivals_flightradar24")

#     print(f"Reading arrival_flightera CSVs from {arrival_folder}...")
#     arrival_df = read_all_csv_from_folder(arrival_folder)

#     print(f"Reading departure_flightera CSVs from {departure_folder}...")
#     departure_df = read_all_csv_from_folder(departure_folder)

#     print(f"Reading arrivals_flightradar24 CSVs from {arrivals_fr24_folder}...")
#     arrival_flightradar24_df = read_all_csv_from_folder(arrivals_fr24_folder)

#     arrival_df = arrival_df.drop_duplicates()
#     departure_df = departure_df.drop_duplicates()
#     arrival_flightradar24_df = arrival_flightradar24_df.drop_duplicates()

#     # Check duplicates in individual datasets
#     for name, df in [("arrivals", arrival_df), ("departures", departure_df), ("flightradar24", arrival_flightradar24_df)]:
#         dups = df.duplicated(subset=["flight_date", "flight_number_iata"], keep=False)
#         if dups.any():
#             print(f"[DUPLICATES] Found in {name}:")
#             print(df[dups][["flight_date", "flight_number_iata"]].sort_values(by=["flight_date", "flight_number_iata"]))

#     # Merge 1: Arrivals + Departures
#     flight_schedule = arrival_df.merge(
#         departure_df,
#         on=["flight_date", "flight_number_iata", "airline"],
#         how="inner",
#         suffixes=("", "_dep")
#     )

#     flight_schedule = flight_schedule[flight_schedule["depart_from_iata"] != flight_schedule["arrive_at_iata"]]


#     dups_merge1 = flight_schedule.duplicated(subset=["flight_date", "flight_number_iata"], keep=False)
#     if dups_merge1.any():
#         print("[DUPLICATES AFTER MERGE 1] Arrivals + Departures:")
#         print(flight_schedule[dups_merge1][["flight_date", "flight_number_iata"]].sort_values(by=["flight_date", "flight_number_iata"]))

#     cols_to_drop = [
#         col for col in flight_schedule.columns
#         if col.endswith("_dep") and col[:-4] in arrival_df.columns
#     ]
#     flight_schedule.drop(columns=cols_to_drop, inplace=True)

#     # Merge 2: With Flightradar24
#     flight_schedule = flight_schedule.merge(
#         arrival_flightradar24_df,
#         on=["flight_date", "flight_number_iata", "depart_from_iata"],
#         how="left",
#         suffixes=("", "_fr24")
#     )

#     dups_merge2 = flight_schedule.duplicated(subset=["flight_date", "flight_number_iata"], keep=False)
#     if dups_merge2.any():
#         print("[DUPLICATES AFTER MERGE 2] + Flightradar24:")
#         print(flight_schedule[dups_merge2][["flight_date", "flight_number_iata"]].sort_values(by=["flight_date", "flight_number_iata"]))

#     cols_to_drop = [
#         col for col in flight_schedule.columns
#         if col.endswith("_fr24") and col[:-5] in flight_schedule.columns
#     ]
#     flight_schedule.drop(columns=cols_to_drop, inplace=True)

#     if "tail_number_fr24" in flight_schedule.columns:
#         flight_schedule.rename(columns={"tail_number_fr24": "tail_number"}, inplace=True)

#     # Continue with time conversions
#     flight_schedule["actual_departure_utc"] = flight_schedule.apply(
#         lambda row: to_utc(row.get("actual_departure_local", ""), row.get("depart_from_iata", "")), axis=1
#     )
#     flight_schedule["actual_arrival_utc"] = flight_schedule.apply(
#         lambda row: to_utc(row.get("actual_arrival_local", ""), row.get("arrive_at_iata", "")), axis=1
#     )

#     if "scheduled_departure_utc" in flight_schedule.columns:
#         flight_schedule["scheduled_departure_utc"] = pd.to_datetime(
#             flight_schedule["scheduled_departure_utc"], errors="coerce"
#         )
#         flight_schedule["flight_date_utc"] = flight_schedule["scheduled_departure_utc"].dt.strftime("%Y-%m-%d")

#     # desired_columns = [c for c in DESIRED_COLUMNS if c in flight_schedule.columns]
#     # flight_schedule = flight_schedule[desired_columns]

#     # # Final duplicate check
#     # final_dups = flight_schedule.duplicated(subset=["flight_date", "flight_number_iata"], keep=False)
#     # if final_dups.any():
#     #     print("[FINAL DUPLICATES] In final merged data:")
#     #     print(flight_schedule[final_dups][["flight_date", "flight_number_iata"]].sort_values(by=["flight_date", "flight_number_iata"]))

#     # today = datetime.datetime.now().date()
#     # output_csv = os.path.join(DATA_DIR, f"flight_schedule_{today}.csv")
#     # flight_schedule.to_csv(output_csv, index=False)
#     return flight_schedule

# clean_and_merge()