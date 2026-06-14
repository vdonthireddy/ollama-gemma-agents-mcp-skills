SCHEMA = {
    "type": "function",
    "function": {
        "name": "book_hotel",
        "description": "Book a room at a hotel for a specified number of nights.",
        "parameters": {
            "type": "object",
            "properties": {
                "hotel_name": {
                    "type": "string",
                    "description": "Name of the hotel to book."
                },
                "nights": {
                    "type": "integer",
                    "description": "Number of nights to stay."
                }
            },
            "required": ["hotel_name", "nights"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(hotel_name: str, nights: int, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Booking hotel '{hotel_name}' for {nights} nights...")
        
        # Mock reservation details
        reserve_code = "HTL-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        booking = {
            "booking_type": "hotel",
            "hotel_name": hotel_name,
            "nights": nights,
            "reservation_code": reserve_code,
            "status": "confirmed"
        }
        
        log_info(session_name, f"Hotel booked. Code: {reserve_code}")
        return {
            "content": f"Hotel booking confirmed! Reservation code: {reserve_code} for hotel '{hotel_name}' ({nights} nights).",
            "booking": booking
        }
    except Exception as e:
        log_error(session_name, f"Error in book_hotel: {e}")
        return {"error": str(e)}
