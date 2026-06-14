SCHEMA = {
    "type": "function",
    "function": {
        "name": "hire_entertainment",
        "description": "Book event entertainment service (e.g. DJ, Magician, Photobooth).",
        "parameters": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "description": "The type of entertainment service to hire (e.g. DJ, Magician, Photobooth)."
                }
            },
            "required": ["type"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(type: str, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Booking entertainment service: '{type}'...")
        
        # Mock booking details
        contract_code = "ENT-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        booking = {
            "booking_type": "entertainment",
            "type": type,
            "contract_code": contract_code,
            "status": "booked"
        }
        
        log_info(session_name, f"Entertainment service booked. Contract: {contract_code}")
        return {
            "content": f"Entertainment booked successfully! Contract ID: {contract_code} for '{type}' service.",
            "booking": booking
        }
    except Exception as e:
        log_error(session_name, f"Error in hire_entertainment: {e}")
        return {"error": str(e)}
