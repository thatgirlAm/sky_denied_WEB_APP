#!/usr/bin/env python3
"""
main.py - Flight information extraction script for testing Laravel app.
Returns fake flight data in JSON format matching the Flight model structure.
"""

import json
import random
import datetime
import sys
import time
import pytz

def generate_flight_data(tail_number):
    """Generate realistic flight data for a given tail number"""
    # Constant data for random selection
    airlines = ["American Airlines", "Delta Air Lines", "United Airlines", "Southwest Airlines"]
    airport_codes = {
        "ATL": {"name": "Hartsfield-Jackson Atlanta International Airport", "icao": "KATL"},
        "LAX": {"name": "Los Angeles International Airport", "icao": "KLAX"},
        "ORD": {"name": "O'Hare International Airport", "icao": "KORD"},
        "DFW": {"name": "Dallas/Fort Worth International Airport", "icao": "KDFW"},
        "DEN": {"name": "Denver International Airport", "icao": "KDEN"},
        "JFK": {"name": "John F. Kennedy International Airport", "icao": "KJFK"},
        "SFO": {"name": "San Francisco International Airport", "icao": "KSFO"},
        "SEA": {"name": "Seattle-Tacoma International Airport", "icao": "KSEA"}
    }
    
    # Current time as baseline
    now = datetime.datetime.now()
    
    # Generate a flight sequence with multiple flights
    flights = []
    flight_count = random.randint(5, 10)  # Generate several flights
    
    # The flagged flight will always be the one at position 3 (so we have enough preceding flights)
    flagged_position = 3
    
    for i in range(flight_count):
        # Select random airports
        depart_iata, arrive_iata = random.sample(list(airport_codes.keys()), 2)
        depart_info = airport_codes[depart_iata]
        arrive_info = airport_codes[arrive_iata]
        
        # Create random dates (older flights first, newer flights later)
        days_ago = flight_count - i + random.randint(0, 2)
        flight_date = now - datetime.timedelta(days=days_ago)
        flight_date_str = flight_date.strftime("%Y-%m-%d")
        
        # Create times
        scheduled_departure = flight_date.replace(
            hour=random.randint(6, 22), 
            minute=random.choice([0, 15, 30, 45])
        )
        
        # Flight duration between 1-6 hours
        duration_minutes = random.randint(60, 360)
        duration_str = f"{duration_minutes // 60}h {duration_minutes % 60}m"
        
        scheduled_arrival = scheduled_departure + datetime.timedelta(minutes=duration_minutes)
        
        # For completed flights, create actual times with potential delays
        if i < flight_count - 1:  # All but the last flight are completed
            delay_departure = random.randint(0, 45)  # 0-45 minutes delay
            delay_arrival = random.randint(0, 45)   # 0-45 minutes delay
            
            actual_departure = scheduled_departure + datetime.timedelta(minutes=delay_departure)
            actual_arrival = scheduled_arrival + datetime.timedelta(minutes=delay_arrival)
            
            # Flight status
            status = "completed"
        else:
            # For the upcoming flight, no actual times yet
            actual_departure = None
            actual_arrival = None
            status = "scheduled"
        
        # Generate flight numbers
        airline = random.choice(airlines)
        airline_code = ''.join([word[0] for word in airline.split()[:2]])
        flight_number = random.randint(1000, 9999)
        flight_number_iata = f"{airline_code}{flight_number}"
        flight_number_icao = f"{airline_code}{flight_number}"
        
        # Timezone for departure and arrival
        depart_tz = "America/New_York"  # Just example timezones
        arrive_tz = "America/Los_Angeles"
        
        # Generate flight record
        flight = {
            "id": random.randint(10000, 99999),
            "flight_date": flight_date_str,
            "flight_date_utc": flight_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "flight_number_iata": flight_number_iata,
            "flight_number_icao": flight_number_icao,
            "tail_number": tail_number,
            "airline": airline,
            "status": status,
            "depart_from": depart_info["name"],
            "depart_from_iata": depart_iata,
            "depart_from_icao": depart_info["icao"],
            "scheduled_departure_local": scheduled_departure.strftime("%Y-%m-%d %H:%M:%S"),
            "scheduled_departure_local_tz": depart_tz,
            "scheduled_departure_utc": scheduled_departure.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actual_departure_local": actual_departure.strftime("%Y-%m-%d %H:%M:%S") if actual_departure else None,
            "actual_departure_local_tz": depart_tz if actual_departure else None,
            "actual_departure_utc": actual_departure.strftime("%Y-%m-%dT%H:%M:%SZ") if actual_departure else None,
            "arrive_at": arrive_info["name"],
            "arrive_at_iata": arrive_iata,
            "arrive_at_icao": arrive_info["icao"],
            "scheduled_arrival_local": scheduled_arrival.strftime("%Y-%m-%d %H:%M:%S"),
            "scheduled_arrival_local_tz": arrive_tz,
            "scheduled_arrival_utc": scheduled_arrival.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "actual_arrival_local": actual_arrival.strftime("%Y-%m-%d %H:%M:%S") if actual_arrival else None,
            "actual_arrival_local_tz": arrive_tz if actual_arrival else None,
            "actual_arrival_utc": actual_arrival.strftime("%Y-%m-%dT%H:%M:%SZ") if actual_arrival else None,
            "duration": duration_str,
            "flag": "1" if i == flagged_position else "0"  # Flag the flight we want to predict
        }
        
        flights.append(flight)
    
    # Weather data - simplified for testing
    weather_data = [
        {
            "station": airport_codes[flights[flagged_position]["depart_from_iata"]]["icao"],
            "timestamp": flights[flagged_position]["scheduled_departure_utc"],
            "temperature": random.randint(-10, 40),
            "humidity": random.randint(20, 100),
            "wind_speed": random.randint(0, 50),
            "wind_direction": random.randint(0, 359),
            "pressure": random.randint(980, 1030),
            "visibility": random.randint(1, 10),
            "conditions": random.choice(["Clear", "Partly Cloudy", "Cloudy", "Rain", "Snow", "Fog"])
        }
    ]
    
    # Simulate processing time
    time.sleep(0.5)
    
    # Return the complete data structure
    return {
        "status": 200,
        "message": "Flight data retrieved successfully",
        "flights": flights,
        "weather": weather_data
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tail_number = sys.argv[1]
    else:
        tail_number = "N12345"  # Default tail number for testing
    
    result = generate_flight_data(tail_number)
    print(json.dumps(result, indent=2))