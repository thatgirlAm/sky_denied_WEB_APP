import pandas as pd
import os
import datetime
import pytz
import airportsdata

AIRPORT_ICAO = airportsdata.load()
AIRPORT_IATA = airportsdata.load("IATA")


def to_local(utc_str, icao_code, fmt="%Y-%m-%d %H:%M"):
    if pd.isna(utc_str) or utc_str == '' or pd.isna(icao_code) or icao_code == '':
        return None
    
    airport_info = AIRPORT_ICAO.get(icao_code)
    if not airport_info or 'tz' not in airport_info:
        # Safe fallback if airport code not found
        return None

    tz_name = airport_info['tz']
    try:
        naive_utc_dt = datetime.datetime.strptime(utc_str, fmt)
        utc_dt = pytz.utc.localize(naive_utc_dt)
        local_tz = pytz.timezone(tz_name)
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime(fmt)
    except Exception:
        return None


def to_icao(iata_code,output_column='icao'):
    if pd.isna(iata_code) or iata_code == '':
        return None
    return AIRPORT_IATA[iata_code][output_column]

def to_utc(dt_input, iata_code, fmt="%Y-%m-%d %H:%M"):
    if pd.isna(dt_input) or dt_input == '' or pd.isna(iata_code) or iata_code == '':
        return None
    tz_name = AIRPORT_IATA[iata_code]['tz']
    if not tz_name:
        return None
        # If dt_input is a string, parse it; if it’s already a datetime, use it directly.
    if isinstance(dt_input, str):
        try:
            naive_local_dt = datetime.datetime.strptime(dt_input, fmt)
        except Exception:
            return None
    else:
        naive_local_dt = dt_input
    local_tz = pytz.timezone(tz_name)
    local_aware_dt = local_tz.localize(naive_local_dt)
    return local_aware_dt.astimezone(pytz.utc).strftime(fmt)


def to_iata(icao_code,output_column='iata'):
    if pd.isna(icao_code) or icao_code == '':
        return None
    return AIRPORT_ICAO[icao_code][output_column]
    
def get_flight_status(row):
    if row["Cancelled"] == 1:
        return "Cancelled"
    elif row["Diverted"] == 1:
        return "Diverted"
    else:
        return "Landed"
    
def clean_us(df, df_airlines,filter_list):
    df = df[df['Origin'].isin(filter_list)]
    df = df[df['Dest'].isin(filter_list)]
    df_merge = df.merge(df_airlines, left_on='DOT_ID_Reporting_Airline', right_on='Code', how='left')
    df_merge.rename(columns={"FlightDate":"flight_date","Tail_Number": "tail_number","WeatherDelay":"weather_delay"}, inplace=True)
    df_merge["flight_date"].astype(str)
    df_merge["scheduled_departure_local"] = df_merge["flight_date"] + " " + df_merge["CRSDepTime"].astype(str).str.zfill(4).str[:2] + df_merge["CRSDepTime"].astype(str).str.zfill(4).str[2:]
    df_merge["scheduled_departure_local"] = pd.to_datetime(df_merge["scheduled_departure_local"])
    df_merge["flight_date_utc"] = df_merge.apply(lambda row: to_utc(row["scheduled_departure_local"], row["Origin"]), axis=1)
    
    df_merge["airline"] = df_merge["Description"].str.split(":").str[0]
    df_merge['status'] = df_merge.apply(get_flight_status, axis=1)

    df_merge["depart_from"] = df_merge["OriginCityName"].str.split(",").str[0]
    df_merge["depart_from_iata"] = df_merge["Origin"]
    df_merge["depart_from_icao"] = df_merge.apply(lambda row: to_icao(row["Origin"],"icao"), axis=1)
    df_merge["scheduled_departure_local_tz"] = df_merge.apply(lambda row: to_icao(row["Origin"],'tz'), axis=1)
    df_merge["scheduled_departure_utc"] = df_merge.apply(lambda row: to_utc(row["scheduled_departure_local"], row["Origin"]), axis=1)
    df_merge["DepTime"] = pd.to_numeric(df_merge["DepTime"], errors="coerce").astype('Int64')
    df_merge["actual_departure_local"] = df_merge["scheduled_departure_local"] + pd.to_timedelta(df_merge["DepDelay"], unit='m')
    df_merge["actual_departure_local"] = pd.to_datetime(df_merge["actual_departure_local"] , format="%Y-%m-%d %H:%M", errors='coerce')
    df_merge["actual_departure_local_tz"] = df_merge.apply(lambda row: to_icao(row["Origin"],'tz'), axis=1)
    df_merge["actual_departure_utc"] = df_merge.apply(lambda row: to_utc(row["actual_departure_local"].strftime("%Y-%m-%d %H:%M") if pd.notna(row["actual_departure_local"]) else "", row["Origin"]), axis=1)

    df_merge["arrive_at"] = df_merge["DestCityName"].str.split(",").str[0]
    df_merge["arrive_at_iata"] = df_merge["Dest"]
    df_merge["arrive_at_icao"] = df_merge.apply(lambda row: to_icao(row["Dest"],"icao"), axis=1)
    df_merge["scheduled_arrival_local_tz"] = df_merge.apply(lambda row: to_icao(row["Dest"],'tz'), axis=1)
    df_merge["scheduled_arrival_local"] = df_merge["scheduled_departure_local"] + pd.to_timedelta(df_merge["CRSElapsedTime"], unit='m')
    df_merge["scheduled_arrival_utc"] = df_merge.apply(lambda row: to_utc(row["scheduled_arrival_local"], row["Dest"]), axis=1)
    df_merge["actual_arrival_local"] = df_merge["scheduled_arrival_local"] + pd.to_timedelta(df_merge["ArrDelay"], unit='m')
    df_merge["actual_arrival_local_tz"] = df_merge.apply(lambda row: to_icao(row["Dest"],'tz'), axis=1)
    df_merge["actual_arrival_utc"] = df_merge.apply(lambda row: to_utc(row["actual_arrival_local"], row["Dest"]), axis=1)
    df_merge["scheduled_duration"] = pd.to_timedelta(df_merge["CRSElapsedTime"], unit='m')
    df_merge["actual_duration"] = pd.to_timedelta(df_merge["ActualElapsedTime"], unit='m')
    df_merge["scheduled_departure_local"] = df_merge["scheduled_departure_local"].dt.strftime("%Y-%m-%d %H:%M")
    df_merge["actual_arrival_local"] = df_merge["actual_arrival_local"].dt.strftime("%Y-%m-%d %H:%M")
    df_merge["actual_departure_local"] = df_merge["actual_departure_local"].dt.strftime("%Y-%m-%d %H:%M")
    df_merge["distance"] = (df_merge["Distance"]).astype("int")
    df_merge["arrival_delay"] = df_merge["ArrDelay"]
    df_merge["departure_delay"] = df_merge["DepDelay"]


    desired_columns = [
        "flight_date",
        "flight_date_utc",
        "flight_number_iata",
        "flight_number_icao",
        "tail_number",
        "airline",
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
        "departure_delay",
        "arrive_at",
        "arrive_at_iata",
        "arrive_at_icao",
        "scheduled_arrival_local",
        "scheduled_arrival_local_tz",
        "scheduled_arrival_utc",
        "actual_arrival_local",
        "actual_arrival_local_tz",
        "actual_arrival_utc",
        "arrival_delay",
        "actual_duration",
        "scheduled_duration",
        "distance",
        "weather_delay"
    ]

    # Create a new DataFrame with only the desired columns, in the desired order
    df_reorganized = df_merge[[col for col in desired_columns if col in df_merge.columns]]
    return df_reorganized

def clean_eu(df, df_airlines, filter_list):
    df = df[df['ADEP'].isin(filter_list)]
    df = df[df['ADES'].isin(filter_list)]
    df_merge = df.merge(df_airlines, left_on='AC Operator', right_on='ICAO', how='left')
    df_merge["flight_date_utc"] = pd.to_datetime(df_merge["FILED OFF BLOCK TIME"], format="%d-%m-%Y %H:%M:%S", errors='coerce')
    df_merge["flight_date"] = df_merge.apply(
            lambda row: to_local(row["flight_date_utc"].strftime("%Y-%m-%d %H:%M"), row["ADEP"]), axis=1
        )
    df_merge["flight_date"] = pd.to_datetime(df_merge["flight_date"]).dt.strftime("%Y-%m-%d")
    df_merge.rename(columns={"AC Registration": "tail_number",
                            "Name":"airline"
                            }, inplace=True)
    df_merge['status'] = ''
    df_merge["depart_from_icao"] = df_merge["ADEP"]
    df_merge['depart_from'] = df_merge.apply(lambda row: to_iata(row["depart_from_icao"],"city"), axis=1)
    df_merge['depart_from_iata'] = df_merge.apply(lambda row: to_iata(row["depart_from_icao"]), axis=1)
    df_merge['scheduled_departure_utc'] = pd.to_datetime(df_merge["FILED OFF BLOCK TIME"], format="%d-%m-%Y %H:%M:%S", errors='coerce')
    df_merge['scheduled_departure_local'] = df_merge.apply(
            lambda row: to_local(row["scheduled_departure_utc"].strftime("%Y-%m-%d %H:%M"), row["ADEP"]), axis=1
        )
    df_merge['scheduled_departure_utc'] = df_merge['scheduled_departure_utc'].dt.strftime("%Y-%m-%d %H:%M")
    df_merge['scheduled_departure_local_tz'] = df_merge.apply(lambda row: to_iata(row["ADEP"],'tz'), axis=1)
    df_merge['actual_departure_utc'] = pd.to_datetime(df_merge["ACTUAL OFF BLOCK TIME"],format="%d-%m-%Y %H:%M:%S")
    df_merge['actual_departure_local'] = df_merge.apply(
            lambda row: to_local(row["actual_departure_utc"].strftime("%Y-%m-%d %H:%M"), row["ADEP"]), axis=1
        )
    df_merge['actual_departure_utc'] = df_merge['actual_departure_utc'].dt.strftime("%Y-%m-%d %H:%M")
    df_merge['actual_departure_local_tz'] = df_merge.apply(lambda row: to_iata(row["ADEP"],'tz'), axis=1)
    df_merge["arrive_at_icao"] = df_merge["ADES"]
    df_merge["arrive_at"] = df_merge.apply(lambda row: to_iata(row["arrive_at_icao"],"city"), axis=1)
    df_merge["arrive_at_iata"] = df_merge.apply(lambda row: to_iata(row["arrive_at_icao"]), axis=1)
    df_merge["scheduled_arrival_utc"] = pd.to_datetime(df_merge["FILED ARRIVAL TIME"],format="%d-%m-%Y %H:%M:%S")
    df_merge["scheduled_arrival_local"] = df_merge.apply(
            lambda row: to_local(row["scheduled_arrival_utc"].strftime("%Y-%m-%d %H:%M"), row["ADES"]), axis=1
        )
    df_merge['scheduled_arrival_utc'] = df_merge['scheduled_arrival_utc'].dt.strftime("%Y-%m-%d %H:%M")

    df_merge["scheduled_arrival_local_tz"] = df_merge.apply(lambda row: to_iata(row["ADES"],'tz'), axis=1)
    df_merge["actual_arrival_utc"] = pd.to_datetime(df_merge["ACTUAL ARRIVAL TIME"],format="%d-%m-%Y %H:%M:%S")
    df_merge["actual_arrival_local"] = df_merge.apply(
            lambda row: to_local(row["actual_arrival_utc"].strftime("%Y-%m-%d %H:%M"), row["ADES"]), axis=1
        )
    df_merge["actual_arrival_utc"] = df_merge["actual_arrival_utc"].dt.strftime("%Y-%m-%d %H:%M")
    df_merge["actual_arrival_local_tz"] = df_merge.apply(lambda row: to_iata(row["ADES"],'tz'), axis=1)
    df_merge["scheduled_duration"] = pd.to_datetime(df_merge["FILED ARRIVAL TIME"],format="%d-%m-%Y %H:%M:%S") - pd.to_datetime(df_merge["FILED OFF BLOCK TIME"],format="%d-%m-%Y %H:%M:%S")
    df_merge["actual_duration"] = pd.to_datetime(df_merge["ACTUAL ARRIVAL TIME"],format="%d-%m-%Y %H:%M:%S") - pd.to_datetime(df_merge["ACTUAL OFF BLOCK TIME"],format="%d-%m-%Y %H:%M:%S")
    df_merge["distance"] = (df_merge["Actual Distance Flown (nm)"] * 1.15078).astype("int")
    df_merge["scheduled_arrival_utc_dt"] = pd.to_datetime(df_merge["scheduled_arrival_utc"], format="%Y-%m-%d %H:%M", errors="coerce")
    df_merge["actual_arrival_utc_dt"] = pd.to_datetime(df_merge["actual_arrival_utc"], format="%Y-%m-%d %H:%M", errors="coerce")
    df_merge["scheduled_departure_utc_dt"] = pd.to_datetime(df_merge["scheduled_departure_utc"], format="%Y-%m-%d %H:%M", errors="coerce")
    df_merge["actual_departure_utc_dt"] = pd.to_datetime(df_merge["actual_departure_utc"], format="%Y-%m-%d %H:%M", errors="coerce")
    df_merge["arrival_delay"] = (
        (df_merge["actual_arrival_utc_dt"] - df_merge["scheduled_arrival_utc_dt"])
        .dt.total_seconds() / 60
    ).round().astype("Int64")

    df_merge["departure_delay"] = (
        (df_merge["actual_departure_utc_dt"] - df_merge["scheduled_departure_utc_dt"])
        .dt.total_seconds() / 60
    ).round().astype("Int64")
    desired_columns = [
        "flight_date",
        "flight_date_utc",
        "flight_number_iata",
        "flight_number_icao",
        "tail_number",
        "airline",
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
        "departure_delay",
        "arrive_at",
        "arrive_at_iata",
        "arrive_at_icao",
        "scheduled_arrival_local",
        "scheduled_arrival_local_tz",
        "scheduled_arrival_utc",
        "actual_arrival_local",
        "actual_arrival_local_tz",
        "actual_arrival_utc",
        "arrival_delay",
        "actual_duration",
        "scheduled_duration",
        "distance",
        "weather_delay"

    ]

    # Create a new DataFrame with only the desired columns, in the desired order
    df_reorganized = df_merge[[col for col in desired_columns if col in df_merge.columns]]

    return df_reorganized


if __name__ == "__main__":
    root_folder = 'data'
#     Run this for EU 
#     input_folder = f'{root_folder}/EU_Flights_20220301_20221231_3m_interval'
#     output_folder = f'{root_folder}/EU_Flights_Cleaned'
#     airline_file = f'{input_folder}/airlines.csv'

#     icao_airports_eu = [
#     "LTFM",  # Istanbul Airport (Turkey)
#     "EHAM",  # Amsterdam Schiphol (Netherlands)
#     "LFPG",  # Paris Charles de Gaulle (France)
#     "EGLL",  # London Heathrow (UK)
#     "EDDF",  # Frankfurt Airport (Germany)
#     "LEMD",  # Madrid Barajas (Spain)
#     "LEBL",  # Barcelona El Prat (Spain)
#     "EDDM",  # Munich Airport (Germany)
#     "LEPA",  # Palma de Mallorca (Spain)
#     "LTAI"   # Antalya Airport (Turkey)
# ]
    # Run this for EU 
    input_folder = f'{root_folder}/US_Flights_20220301_20221231_3m_interval'
    output_folder = f'{root_folder}/US_Flights_Cleaned'
    airline_file = f'{input_folder}/airlines.csv'
    iata_airports_us = [
    "ATL",  # Hartsfield–Jackson Atlanta International Airport
    "DFW",  # Dallas/Fort Worth International Airport
    "DEN",  # Denver International Airport
    "ORD",  # Chicago O’Hare International Airport
    "CLT",  # Charlotte Douglas International Airport
    "LAX",  # Los Angeles International Airport
    "LAS",  # Las Vegas Harry Reid International Airport
    "SEA",  # Seattle–Tacoma International Airport
    "MCO",  # Orlando International Airport
    "PHX"   # Phoenix Sky Harbor International Airport
]

    os.makedirs(output_folder, exist_ok=True)

    # Load airline data once
    df_airline = pd.read_csv(airline_file)

    # Process each CSV file in the folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv') and 'airlines' not in filename.lower():
            file_path = os.path.join(input_folder, filename)
            print(f"Processing: {file_path}")

            df = pd.read_csv(file_path)

            # Clean using your existing function
            # df_cleaned = clean_eu(df, df_airline, icao_airports_eu) # Uncomment/comment this when running EU
            df_cleaned = clean_us(df, df_airline, iata_airports_us)  # Uncomment/comment this when running US

            # Save to output folder
            cleaned_file_path = os.path.join(output_folder, f"cleaned_{filename}")
            df_cleaned.to_csv(cleaned_file_path, index=False)
            print(f"Saved to: {cleaned_file_path}")
    
    df_all = []
    
    for filename in os.listdir(output_folder):
        if filename.endswith('.csv') and 'airlines' not in filename.lower():
            file_path = os.path.join(output_folder, filename)
            print(f"Processing: {file_path}")
            
            df = pd.read_csv(file_path)
            df_all.append(df)

    # Assuming df_all is a list of DataFrames
    df_combined = pd.concat(df_all, ignore_index=True)
    # Clean using your existing function

    # Assuming your DataFrame is named df
    airline_traffic = df_combined["airline"].value_counts().reset_index()
    airline_traffic.columns = ["airline", "flight_count"]

    airline_traffic.to_csv('airline_traffic_us.csv')
                        
