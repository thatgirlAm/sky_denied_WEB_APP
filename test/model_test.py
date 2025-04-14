from model import predict_delay

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
print(result)
