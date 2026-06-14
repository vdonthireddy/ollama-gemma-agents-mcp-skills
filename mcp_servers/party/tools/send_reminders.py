SCHEMA = {
    "type": "function",
    "function": {
        "name": "send_reminders",
        "description": "Send email/SMS party reminder updates to all confirmed guests with location details.",
        "parameters": {
            "type": "object",
            "properties": {
                "guest_emails": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of guest email addresses."
                },
                "location": {
                    "type": "string",
                    "description": "The venue address or location."
                }
            },
            "required": ["guest_emails", "location"]
        }
    }
}

from logger import log_info, log_error

def handler(guest_emails: list, location: str, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Sending reminders to {len(guest_emails)} emails for location '{location}'...")
        
        return {
            "content": f"Reminders successfully dispatched to {len(guest_emails)} guests! Details sent: Location: {location}.",
            "emails_sent_count": len(guest_emails),
            "location": location,
            "status": "reminders_sent"
        }
    except Exception as e:
        log_error(session_name, f"Error in send_reminders: {e}")
        return {"error": str(e)}
