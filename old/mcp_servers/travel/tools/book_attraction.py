SCHEMA = {
    "type": "function",
    "function": {
        "name": "book_attraction",
        "description": "Book a ticket for an attraction or activity in a target city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City where the attraction is located."
                },
                "activity": {
                    "type": "string",
                    "description": "Name of the activity or attraction (e.g. Museum ticket, City Tour)."
                }
            },
            "required": ["city", "activity"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(city: str, activity: str, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Booking attraction tickets for '{activity}' in {city}...")
        
        # Mock reservation details
        ticket_code = "TKT-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        booking = {
            "booking_type": "attraction",
            "city": city,
            "activity": activity,
            "ticket_code": ticket_code,
            "status": "confirmed"
        }
        
        log_info(session_name, f"Attraction booked. Ticket Code: {ticket_code}")
        return {
            "content": f"Attraction ticket booked successfully! Code: {ticket_code} for '{activity}' in {city}.",
            "booking": booking
        }
    except Exception as e:
        log_error(session_name, f"Error in book_attraction: {e}")
        return {"error": str(e)}
