#!/usr/bin/env python3
"""
Fake prediction script for Laravel model_trigger testing.
"""

import json
import random
import datetime
import sys
import time

def generate_fake_prediction(flight_info, weather_info):
    """
    Generate a fake prediction for flight delays.
    
    Args:
        flight_info: Dictionary with flight information.
        weather_info: Dictionary with weather information.
        
    Returns:
        Dictionary with prediction data.
    """
    flight_id = flight_info.get("id", random.randint(1000, 9999))
    delay_probability = random.random()
    is_delayed = delay_probability > 0.5

    prediction = {
        "id": flight_id,
        "status": "delayed" if is_delayed else "on_time",
        "prediction": {
            "id": flight_id,
            "flight_id": flight_info.get("id", None),
            "delayed": 1 if is_delayed else 0,
            "previous_prediction": 1 if random.random() > 0.7 else 0,
            "accuracy": round(random.uniform(0.65, 0.95), 2),
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "confidence": round(abs(delay_probability - 0.5) * 2, 2),
            "delay_minutes": random.randint(15, 180) if is_delayed else 0,
            "factors": [
                f"Airline: {flight_info.get('airline', 'Unknown')}",
                f"Departure airport: {flight_info.get('depart_from_iata', 'Unknown')}",
                f"Arrival airport: {flight_info.get('arrive_at_iata', 'Unknown')}",
                f"Weather conditions: {weather_info.get('conditions', 'Unknown')}"
            ]
        }
    }
    return prediction

def main():
    # Check for JSON input from command-line arguments
    if len(sys.argv) < 2:
        print(json.dumps({"status": 400, "message": "No input data provided"}))
        return

    try:
        # Parse input JSON
        input_data = json.loads(sys.argv[1])
        flight_data = input_data.get("flight_information", [])
        weather_data = input_data.get("weather_information", [])
        
        # Simulate processing time
        time.sleep(1)

        # Generate predictions for each flight
        predictions = []
        for i in range(len(flight_data)):
            flight_info = flight_data[i]
            weather_info = weather_data[i] if i < len(weather_data) else {}
            predictions.append(generate_fake_prediction(flight_info, weather_info))

        # Output predictions as JSON
        print(json.dumps(predictions, indent=4))
    except json.JSONDecodeError:
        print(json.dumps({"status": 400, "message": "Invalid JSON input"}))
    except Exception as e:
        print(json.dumps({"status": 500, "message": f"Error processing data: {str(e)}"}))

if __name__ == "__main__":
    main()
