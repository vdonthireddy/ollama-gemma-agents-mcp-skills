SCHEMA = {
    "type": "function",
    "function": {
        "name": "book_venue",
        "description": "Reserve a party venue space for a specific guest count.",
        "parameters": {
            "type": "object",
            "properties": {
                "venue_name": {
                    "type": "string",
                    "description": "Name of the venue (e.g. Skyline Park, Cozy Club, Arcade Palace)."
                },
                "guest_count": {
                    "type": "integer",
                    "description": "Number of guests to accommodate."
                }
            },
            "required": ["venue_name", "guest_count"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(venue_name: str, guest_count: int, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Reserving venue '{venue_name}' for {guest_count} guests...")
        
        # Mock reservation
        confirm_id = "VNU-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        booking = {
            "booking_type": "venue",
            "venue_name": venue_name,
            "guest_count": guest_count,
            "confirmation_id": confirm_id,
            "address": f"{random.randint(100, 999)} Celebration Way, Suite {random.randint(1, 20)}",
            "status": "confirmed"
        }
        
        log_info(session_name, f"Venue booked successfully. Confirmation: {confirm_id}")
        return {
            "content": f"Venue reservation confirmed! Confirmation ID: {confirm_id} for '{venue_name}' accommodating {guest_count} guests. Address: {booking['address']}.",
            "booking": booking
        }
    except Exception as e:
        log_error(session_name, f"Error in book_venue: {e}")
        return {"error": str(e)}
