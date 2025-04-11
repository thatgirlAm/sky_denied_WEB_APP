#!/usr/bin/env python3
"""
model_path.py - Flight delay prediction model for testing Laravel app.
Takes flight and weather data and returns delay predictions matching the Prediction model.
"""

import json
import random
import datetime
import sys
import time

def predict_delay(data):
    """
    Generate a delay prediction based on flight and weather data
    
    Args:
        data: Dictionary containing flight_information and weather_information
        
    Returns:
        Dictionary with prediction results
    """
    # Simulate model processing time
    time.sleep(1.0)
    
    # Extract flight and weather information
    flight_data = data.get("flight_information", [])[0] if "flight_information" in data and data["flight_information"] else {}
    weather_data = data.get("weather_information", [])[0] if "weather_information" in data and data["weather_information"] else {}
    
    # Basic validation
    if not flight_data:
        return {
            "status": 400,
            "message": "Invalid input: No flight data provided"
        }
    
    # Extract factors that might influence delay
    airline = flight_data.get("airline", "")
    origin = flight_data.get("depart_from_iata", "")
    destination = flight_data.get("arrive_at_iata", "")
    
    # Weather factors if available
    weather_condition = "Unknown"
    if weather_data:
        weather_condition = weather_data.get("conditions", "Unknown")
    
    # Calculate delay probability based on factors
    delay_probability = random.random()  # Base probability
    
    # Adjust based on airline (example rules)
    if "Delta" in airline:
        delay_probability *= 0.8  # Lower probability for some airlines
    elif "United" in airline:
        delay_probability *= 1.2  # Higher probability for others
    
    # Adjust based on airports
    if origin in ["JFK", "LAX", "ORD"] or destination in ["JFK", "LAX", "ORD"]:
        delay_probability *= 1.3  # Busier airports have higher delay probability
    
    # Adjust based on weather
    if weather_condition in ["Rain", "Snow", "Fog"]:
        delay_probability *= 1.5  # Bad weather increases delays
    
    # Determine if flight will be delayed
    is_delayed = delay_probability > 0.5
    
    # Previous prediction value (for tracking changes)
    previous_prediction = random.random() > 0.7  # 30% chance the previous prediction was different
    
    # Create prediction ID (would normally be handled by the database)
    prediction_id = flight_data.get("id", random.randint(1000, 9999))
    
    # Generate prediction data matching your model
    prediction = {
        "id": prediction_id,
        "status": "delayed" if is_delayed else "on_time",  # This matches what your controller expects
        "prediction": {
            "id": prediction_id,
            "flight_id": flight_data.get("id"),
            "delayed": 1 if is_delayed else 0,  # 1 for delayed, 0 for on time
            "previous_prediction": 1 if previous_prediction else 0,
            "accuracy": round(random.uniform(0.65, 0.95), 2),  # Random accuracy between 65-95%
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "confidence": round(abs(delay_probability - 0.5) * 2, 2),  # Convert to 0-1 confidence score
            "delay_minutes": random.randint(15, 180) if is_delayed else 0,
            "factors": [
                f"Airline: {airline}" + (" (historically punctual)" if "Delta" in airline else " (often delayed)" if "United" in airline else ""),
                f"Departure airport: {origin}" + (" (high congestion)" if origin in ["JFK", "LAX", "ORD"] else ""),
                f"Arrival airport: {destination}" + (" (high congestion)" if destination in ["JFK", "LAX", "ORD"] else ""),
                f"Weather conditions: {weather_condition}" + (" (adverse)" if weather_condition in ["Rain", "Snow", "Fog"] else "")
            ]
        }
    }
    
    return prediction

if __name__ == "__main__":
    # Check if input is provided as a command-line argument
    if len(sys.argv) > 1:
        try:
            input_data = json.loads(sys.argv[1])
            result = predict_delay(input_data)
        except json.JSONDecodeError:
            result = {
                "status": 400,
                "message": "Invalid JSON input"
            }
        except Exception as e:
            result = {
                "status": 500,
                "message": f"Error processing request: {str(e)}"
            }
    else:
        # Example data for testing
        example_data = {
            "flight_information": [
                {
                    "id": 12345,
                    "flight_number_iata": "DL1234",
                    "airline": "Delta Air Lines",
                    "depart_from_iata": "ATL",
                    "arrive_at_iata": "LAX",
                    "scheduled_departure_utc": "2025-04-10T14:30:00Z"
                }
            ],
            "weather_information": [
                {
                    "station": "KATL",
                    "timestamp": "2025-04-10T14:30:00Z",
                    "temperature": 22,
                    "conditions": "Clear"
                }
            ]
        }
        result = predict_delay(example_data)
    
    # Output as JSON
    print(json.dumps(result, indent=2))