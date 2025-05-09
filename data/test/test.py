# import pandas as pd
# import requests
# import time
# from datetime import datetime
# from airportsdata import load

# API_KEY = "7517e25b379441c8b66195214250304"

# def get_hourly_weather_history_wwo(airport_codes, start_date, end_date, airport_code_type='IATA', output_csv="wwo_history.csv"):
#     print(f"Fetching hourly historical weather from {start_date} to {end_date} using {airport_code_type} codes...")

#     airports_by_iata = load("IATA")
#     airports_by_icao = load("ICAO")

#     # Build full bidirectional mapping
#     iata_to_info = {iata: airports_by_iata[iata] for iata in airports_by_iata}
#     icao_to_info = {icao: airports_by_icao[icao] for icao in airports_by_icao}

#     # Build city mapping and cross-code references
#     if airport_code_type.upper() == "IATA":
#         code_to_city_mapper = {code: iata_to_info[code]["city"] for code in airport_codes}
#     else:
#         code_to_city_mapper = {code: icao_to_info[code]["city"] for code in airport_codes}

#     weather_data = []

#     for code, city in code_to_city_mapper.items():
#         # Get both ICAO and IATA codes
#         if airport_code_type.upper() == "IATA":
#             iata = code
#             icao = iata_to_info[code]["icao"]
#         else:
#             icao = code
#             iata = icao_to_info[code]["iata"]

#         print(f"📦 Fetching historical data for {city} ({iata}/{icao})")

#         url = "http://api.worldweatheronline.com/premium/v1/past-weather.ashx"
#         params = {
#             "key": API_KEY,
#             "q": city,
#             "format": "json",
#             "date": start_date,
#             "enddate": end_date,
#             "tp": "1",  # hourly
#             "includelocation": "yes"
#         }

#         response = requests.get(url, params=params)
#         if response.status_code == 200:
#             data = response.json()
#             for day in data["data"]["weather"]:
#                 date = day["date"]
#                 total_snow_cm = float(day.get("totalSnow_cm", 0.0))

#                 for hour in day["hourly"]:
#                     weather_data.append({
#                         "airport_code_iata": iata,
#                         "airport_code_icao": icao,
#                         "city": city,
#                         "timestamp": f"{date} {hour['time'].zfill(4)[:2]}:00",
#                         "temp_c": float(hour["tempC"]),
#                         "feels_like_c": int(hour["FeelsLikeC"]),
#                         "dew_point_c": int(hour["DewPointC"]),
#                         "heat_index_c": int(hour["HeatIndexC"]),
#                         "wind_chill_c": int(hour["WindChillC"]),
#                         "humidity_pct": int(hour["humidity"]),
#                         "pressure_mb": int(hour["pressure"]),
#                         "cloud_cover_pct": int(hour["cloudcover"]),
#                         "visibility_m": int(hour["visibility"]) * 1000,
#                         "wind_speed_kmph": float(hour["windspeedKmph"]),
#                         "wind_gust_kmph": int(hour["WindGustKmph"]),
#                         "wind_dir_deg": int(hour["winddirDegree"]),
#                         "precip_mm": float(hour["precipMM"]),
#                         "weather_desc": hour["weatherDesc"][0]["value"],
#                         "total_daily_snow_cm": total_snow_cm
#                     })
#         else:
#             print(f"[ERROR] {code}: {response.status_code} | {response.text}")

#         time.sleep(1.2)

#     df = pd.DataFrame(weather_data)
#     df["timestamp"] = pd.to_datetime(df["timestamp"])
#     df.to_csv(output_csv, index=False)
#     print(f"Historical weather saved to {output_csv}")
#     return df

# # ------------------
# # Example usage
# start = "2022-03-01"
# end = "2022-03-31"
# start_str = start.replace("-", "")
# end_str = end.replace("-", "")

# # For US airports (IATA)
# airport_codes_us_iata = ["ATL", "DFW", "DEN", "ORD", "CLT", "LAX", "LAS", "SEA", "PHX", "LGA"]
# get_hourly_weather_history_wwo(
#     airport_codes_us_iata,
#     start,
#     end,
#     airport_code_type="IATA",
#     output_csv=f"top10_us_airport_weather_{start_str}_{end_str}.csv"
# )

# # For EU airports (ICAO)
# airport_codes_eu_icao = ['LTFM', 'EHAM', 'LFPG', 'EGLL', 'EDDF', 'LEMD', 'LEBL', 'EDDM', 'LEPA', 'LTAI']
# ["IST", "AMS", "CDG", "LHR", "FRA", "MAD", "BCN", "MUC", "PMI", "AYT"]
# get_hourly_weather_history_wwo(
#     airport_codes_eu_icao,
#     start,
#     end,
#     airport_code_type="ICAO",
#     output_csv=f"top10_eu_airport_weather_{start_str}_{end_str}.csv"
# )

from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

def gen_driver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")  # Use the newer headless mode
        
        # Add these to better mimic a real browser
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    # Common options for both headless and non-headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    
    # Add experimental options to avoid detection
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    return webdriver.Chrome(options=chrome_options)

def test_cloudflare_block():
    driver = gen_driver()
    if not driver:
        print("Failed to start driver. Aborting test.")
        return
    
    try:
        print("Loading flightera.net ...")
        driver.get("https://www.airnavradar.com/data/registration/N957NN")

        time.sleep(5)  # Wait for the page to fully load

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Cloudflare detection
        if "Just a moment..." in soup.text or "Checking your browser" in soup.text:
            print("Cloudflare is blocking or challenging the request.")
        elif soup.title:
            print(f"Page loaded successfully. Title: {soup.title.string}")
        else:
            print("Could not detect a title. Something might be wrong.")
        
        # Save it to an HTML file
        with open("aircraft.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

    except Exception as e:
        print("Error during test:", e)

    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    test_cloudflare_block()

