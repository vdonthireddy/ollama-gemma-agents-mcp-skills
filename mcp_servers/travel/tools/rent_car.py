SCHEMA = {
    "type": "function",
    "function": {
        "name": "rent_car",
        "description": "Reserve a rental car of a specific type (e.g. SUV, Sedan) in a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to rent the car in."
                },
                "car_type": {
                    "type": "string",
                    "description": "Type of car (e.g. Economy, Compact, Sedan, SUV)."
                }
            },
            "required": ["city", "car_type"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(city: str, car_type: str, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Booking rental {car_type} in {city}...")
        
        # Mock rental details
        rental_code = "CAR-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        booking = {
            "booking_type": "car_rental",
            "city": city,
            "car_type": car_type,
            "rental_code": rental_code,
            "status": "confirmed"
        }
        
        log_info(session_name, f"Car rental booked. Code: {rental_code}")
        return {
            "content": f"Car rental reservation confirmed! Code: {rental_code} for a {car_type} in {city}.",
            "booking": booking
        }
    except Exception as e:
        log_error(session_name, f"Error in rent_car: {e}")
        return {"error": str(e)}
