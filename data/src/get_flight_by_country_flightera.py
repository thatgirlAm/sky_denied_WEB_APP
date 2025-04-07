# import time
# import bs4
# import random
# import datetime
# import re
# import json
# import pandas as pd
# from urllib.parse import urljoin
# import seleniumwire.undetected_chromedriver as uc
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from dateutil import parser
# import os

# def parse_flight_table(soup, mode="arrival"):
#     rows = soup.find_all("tr", class_=lambda c: c and ("bg-white" in c or "bg-gray-50" in c))
#     flight_data = []

#     for row in rows:
#         tds = row.find_all("td")
#         if len(tds) < 7:
#             continue

#         # --- Flight Date + Status ---
#         flight_date = ""
#         date_links = tds[0].find_all("a")
#         if len(date_links) > 1:
#             href = date_links[1].get("href", "")
#             match = re.search(r'/(\d{4}-\d{2}-\d{2})$', href)
#             flight_date = match.group(1) if match else ""
#         status_tag = tds[0].find("span", class_=lambda c: c and "bg-" in c)
#         status = status_tag.get_text(strip=True) if status_tag else ""

#         # --- Flight Numbers and Airline ---
#         a_tags = tds[1].find_all("a")
#         flight_number_iata = a_tags[0].get_text(strip=True) if a_tags else ""
#         icao_span = tds[1].find_all("span", class_="text-gray-700")
#         flight_number_icao = icao_span[0].get_text(strip=True) if icao_span else ""
#         airline = a_tags[1].get_text(strip=True) if len(a_tags) > 1 else ""

#         # --- Location Data ---
#         location_span = tds[2].find("span", class_=lambda c: c and "text-xs" in c)
#         location_text = location_span.get_text(strip=True) if location_span else ""

#         code_span = tds[2].find("span", class_=lambda c: c and "whitespace-nowrap" in c)
#         code_text = code_span.get_text(strip=True) if code_span else ""
#         code_text = code_text.replace("(", "").replace(")", "") if code_text else ""
#         code_parts = code_text.split("/") if code_text else ["", ""]
#         code_iata = code_parts[0].strip()
#         code_icao = code_parts[1].strip() if len(code_parts) > 1 else ""

#         # --- Scheduled Time (Local + UTC) ---
#         scheduled_local = ""
#         scheduled_utc = ""
#         schedule_local_tz=""
#         local_span = tds[3].find("span", class_="whitespace-nowrap")
#         if local_span:
#             tz_span = local_span.find("span", class_="text-xs")
#             schedule_local_tz = tz_span.get_text(strip=True) if tz_span else ""
#             if tz_span:
#                 tz_span.decompose()
#             local_time = local_span.get_text(strip=True)
#             scheduled_local = parser.parse(local_time, dayfirst=True).strftime("%Y-%m-%d %H:%M")

#         utc_spans = tds[3].find_all("span", class_="text-xs")
#         if utc_spans:
#             scheduled_utc = utc_spans[-1].get_text(strip=True).replace("UTC", "").strip()
#             scheduled_utc = parser.parse(scheduled_utc, dayfirst=True).strftime("%Y-%m-%d %H:%M")

#         # --- Actual Departure ---
#         actual_departure_local = ""
#         actual_departure_local_tz=""
#         actual_dep_span = tds[4].find("span", class_="whitespace-nowrap")
#         if actual_dep_span:
#             tz_span = actual_dep_span.find("span", class_="text-xs")
#             actual_departure_local_tz = tz_span.get_text(strip=True) if tz_span else ""
#             if tz_span:
#                 tz_span.decompose()
#             actual_time = actual_dep_span.get_text(strip=True)
#             actual_departure_local = parser.parse(actual_time, dayfirst=True).strftime("%Y-%m-%d %H:%M")

#         # --- Actual Departure Delay ---
#         departure_delay = ""
#         departure_delay_span = tds[4].find("span", class_=lambda c: c and "inline-flex" in c)
#         if departure_delay_span:
#             departure_delay = departure_delay_span.get_text(strip=True)

#         # --- Actual Arrival ---
#         actual_arrival_local = ""
#         actual_arrival_local_tz=""
#         actual_arrival_span = tds[5].find("span", class_="whitespace-nowrap")
#         if actual_arrival_span:
#             tz_span = actual_arrival_span.find("span", class_="text-xs")
#             actual_arrival_local_tz = tz_span.get_text(strip=True) if tz_span else ""
#             if tz_span:
#                 tz_span.decompose()
#             actual_time = actual_arrival_span.get_text(strip=True)
#             actual_arrival_local = parser.parse(actual_time, dayfirst=True).strftime("%Y-%m-%d %H:%M")

#         # --- Actual Arrival Delay ---
#         arrival_delay = ""
#         arrival_delay_span = tds[5].find("span", class_=lambda c: c and "inline-flex" in c)
#         if arrival_delay_span:
#             arrival_delay = arrival_delay_span.get_text(strip=True)

#         # --- Duration ---
#         duration_text = tds[6].get_text(strip=True)

#         # --- Build Flight Record ---
#         flight_record = {
#             "flight_date": flight_date,
#             "status": status,
#             "flight_number_iata": flight_number_iata,
#             "flight_number_icao": flight_number_icao,
#             "airline": airline,

#         }

#         if mode == "arrival":
#             flight_record["depart_from"] = location_text
#             flight_record["depart_from_iata"] = code_iata
#             flight_record["depart_from_icao"] = code_icao
#             flight_record["scheduled_arrival_local"] = scheduled_local
#             flight_record["schedule_local_tz"] = schedule_local_tz
#             flight_record["scheduled_arrival_utc"] = scheduled_utc
#         else:  # mode == "departure"
#             flight_record["arrive_at"] = location_text
#             flight_record["arrive_at_iata"] = code_iata
#             flight_record["arrive_at_icao"] = code_icao
#             flight_record["scheduled_departure_local"] = scheduled_local
#             flight_record["schedule_local_tz"] = schedule_local_tz
#             flight_record["scheduled_departure_utc"] = scheduled_utc

#         flight_record["actual_departure_local"] = actual_departure_local
#         flight_record["actual_departure_local_tz"] = actual_departure_local_tz
#         flight_record["departure_delay"] = departure_delay
#         flight_record["actual_arrival_local"] = actual_arrival_local
#         flight_record["actual_arrival_local_tz"] = actual_arrival_local_tz
#         flight_record["arrival_delay"] = arrival_delay
#         flight_record["duration"] = duration_text

#         flight_data.append(flight_record)

#     return pd.DataFrame(flight_data)

# # Utility functions
# def construct_flight_url(base_url, country, flight_type, date, time_str):
#     return f"{base_url}/en/country/{country}/{flight_type}/{date}%20{time_str}?"

# def deduct_flight_schedule_date_time_by_one_minute(date_str, time_str):
#     dt = datetime.datetime.strptime(f"{date_str} {time_str.replace('_', ':')}", "%Y-%m-%d %H:%M")
#     dt -= datetime.timedelta(minutes=1)
#     return dt.strftime("%Y-%m-%d"), dt.strftime("%H_%M")

# def extract_datetime_from_url(href):
#     match = re.search(r"/(\d{4}-\d{2}-\d{2}) (\d{2}_\d{2})", href)
#     if match:
#         return match.group(1), match.group(2)
#     return None, None

# def driver_wait(driver, random_start=1, random_end=2, wait_time=10):
#     WebDriverWait(driver, wait_time).until(
#         EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Earlier Flights')]"))
#     )
#     time.sleep(random.uniform(random_start, random_end))

# # Main crawling logic with resume + transform + batch DB push
# def crawl_flight_type(base_url="https://www.flightera.net", country=None, flight_type=None, start_date_str=None, time_str="23_59", save_every=5, end_date=None):
#     # Setup browser
#     chrome_options = uc.ChromeOptions()
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     driver = uc.Chrome(version_main=134,options=chrome_options)

#     today = datetime.datetime.now().date()
#     if end_date:
#         end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

#     visited_urls = []
#     errors = []
#     all_data = pd.DataFrame()
#     backup_file = f"{flight_type}_last_url.txt"

#     if os.path.exists(backup_file):
#         with open(backup_file, "r") as f:
#             url = f.read().strip()
#         print(f"Resuming from last saved URL: {url}")
#     else:
#         url = construct_flight_url(base_url, country, flight_type, start_date_str, time_str)
#         print(f"Starting fresh from: {url}")

#     try:
#         driver.get(url)
#         driver_wait(driver)

#         while True:
#             html = driver.page_source
#             soup = bs4.BeautifulSoup(html, "html.parser")
#             # Extract and transform the current page data here
#             df = parse_flight_table(soup, flight_type)
#             all_data = pd.concat([all_data, df], ignore_index=True)

#             earlier_tag = soup.find("a", string=lambda text: text and "Earlier Flights" in text)
#             if not earlier_tag:
#                 print("No more earlier flights link.")
#                 break

#             href = earlier_tag.get("href")
#             if not href:
#                 print("No href in earlier flights link.")
#                 break

#             earlier_date, earlier_time = extract_datetime_from_url(href)
#             if not earlier_date:
#                 print("Couldn't extract date from earlier flights link.")
#                 break

#             print(f"[{flight_type.upper()}] {earlier_date} {earlier_time}")
#             url.replace(" ","%20")
#             visited_urls.append(url)

#             # # Push to DB every `save_every` batches
#             # if len(visited_urls) % save_every == 0:
#             #     with open(backup_file, "w") as f:
#             #         f.write(url)

#             #     # TODO: Push `all_data` to your database here
#             #     # Example: push_to_db(all_data)
#             #     # Reset batch
#             #     all_data = pd.DataFrame()

#             # Stop if reached today or specified end date
#             flight_date = datetime.datetime.strptime(earlier_date, "%Y-%m-%d").date()
#             if flight_date <= today or (end_date and flight_date <= end_date):
#                 print("Reached stopping date. Exiting.")
#                 break

#             # Load next page
#             full_url = urljoin(base_url, href)
#             driver.requests.clear()
#             driver.get(full_url)
#             driver_wait(driver, 1, 3)

#             new_html = driver.page_source
#             if html == new_html:
#                 print("Page content did not change. Trying manual -1 minute fallback.")
#                 date_str, time_str = deduct_flight_schedule_date_time_by_one_minute(earlier_date, earlier_time)
#                 url = construct_flight_url(base_url, country, flight_type, date_str, time_str)
#                 driver.get(url)
#                 driver_wait(driver)
#             else:
#                 url = full_url

#     except Exception as e:
#         print(f"Error occurred: {e}")
#         errors.append((url, str(e)))

#     finally:
#         flight_date = datetime.datetime.strptime(earlier_date, "%Y-%m-%d").date()
#         if flight_date > today or (end_date and flight_date > end_date):
#             with open(backup_file, "w") as f:
#                 f.write(url)
#         else:
#             if os.path.exists(backup_file):
#                 os.remove(backup_file)

#         # Optionally close the browser
#         driver.quit()
#         # Create 'arrival' folder if it doesn't exist
#         os.makedirs(f"{flight_type}", exist_ok=True)
#         all_data.to_csv(f"{flight_type}/{flight_type}_{country}_{start_date_str}.csv",index=False)


#     return visited_urls, errors


# # base_url = "https://www.flightera.net"
# # country = "United+Kingdom"
# # start_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
# # time_str = "23_59"
# # end_date = "2025-04-01"

# # arrival_urls, arrival_errors = crawl_flight_type(base_url, country, "arrival", start_date,time_str)
# # departure_urls, departure_errors = crawl_flight_type(base_url, country, "departure", start_date, time_str)