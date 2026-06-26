SCHEMA = {
    "type": "function",
    "function": {
        "name": "book_flight",
        "description": "Book a selected flight by ID and get a confirmation code.",
        "parameters": {
            "type": "object",
            "properties": {
                "flight_id": {
                    "type": "string",
                    "description": "The ID of the flight to book."
                }
            },
            "required": ["flight_id"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(flight_id: str, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Booking flight ID: {flight_id}...")
        
        # Mock booking details
        confirm_code = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        booking = {
            "booking_type": "flight",
            "flight_id": flight_id,
            "booking_code": confirm_code,
            "status": "confirmed"
        }
        
        log_info(session_name, f"Flight booked. Code: {confirm_code}")
        return {
            "content": f"Flight booking confirmed! Confirmation code: {confirm_code} for Flight ID {flight_id}.",
            "booking": booking
        }
    except Exception as e:
        log_error(session_name, f"Error in book_flight: {e}")
        return {"error": str(e)}
