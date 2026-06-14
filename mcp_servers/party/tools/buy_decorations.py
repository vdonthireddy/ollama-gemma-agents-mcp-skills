SCHEMA = {
    "type": "function",
    "function": {
        "name": "buy_decorations",
        "description": "Purchase themed decorations (balloons, plates, streamers) based on party theme.",
        "parameters": {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "description": "The theme of the decorations (e.g. Superhero, Retro 80s, Cyberpunk, Neon, Tropical)."
                }
            },
            "required": ["theme"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(theme: str, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Purchasing party decorations for theme: '{theme}'...")
        
        # Mock order details
        receipt_num = "DEC-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        booking = {
            "booking_type": "decorations",
            "theme": theme,
            "receipt_number": receipt_num,
            "items_included": ["Balloons", "Tablecloths", "Paper Plates", "Happy Birthday Banner", "LED Lights"],
            "status": "purchased"
        }
        
        log_info(session_name, f"Decorations purchased. Receipt: {receipt_num}")
        return {
            "content": f"Decorations ordered successfully! Receipt Number: {receipt_num} for '{theme}' theme pack. Items: {', '.join(booking['items_included'])}.",
            "booking": booking
        }
    except Exception as e:
        log_error(session_name, f"Error in buy_decorations: {e}")
        return {"error": str(e)}
