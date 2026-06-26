SCHEMA = {
    "type": "function",
    "function": {
        "name": "invite_guests",
        "description": "Send invitations to a list of guests and receive confirmation count (RSVPs).",
        "parameters": {
            "type": "object",
            "properties": {
                "guest_names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of guest names to invite."
                }
            },
            "required": ["guest_names"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(guest_names: list, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Sending party invitations to {len(guest_names)} guests...")
        
        # Mock RSVP details
        # Assume around 70-90% of guests accept
        rsvp_rate = random.uniform(0.7, 0.9)
        rsvp_count = max(1, int(len(guest_names) * rsvp_rate))
        
        log_info(session_name, f"RSVP count received: {rsvp_count}/{len(guest_names)}")
        return {
            "content": f"Invitations sent! Received {rsvp_count} positive RSVPs out of {len(guest_names)} invited guests.",
            "rsvp_count": rsvp_count,
            "guest_names": guest_names
        }
    except Exception as e:
        log_error(session_name, f"Error in invite_guests: {e}")
        return {"error": str(e)}
