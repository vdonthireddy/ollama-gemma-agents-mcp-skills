SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_hotels",
        "description": "Find hotels in a city matching the specified maximum budget.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to search for hotels (e.g. Paris, Tokyo)."
                },
                "budget": {
                    "type": "number",
                    "description": "Maximum price per night in USD."
                }
            },
            "required": ["city", "budget"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(city: str, budget: float, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Searching hotels in {city} under budget ${budget}...")
        
        # Mock hotels matching budget
        hotels = [
            {"hotel_name": "Grand Central Stay", "price_per_night": int(budget * 0.9), "rating": 4.6},
            {"hotel_name": "Cozy Corner Inn", "price_per_night": int(budget * 0.7), "rating": 4.2}
        ]
        
        log_info(session_name, f"Found {len(hotels)} hotels.")
        return {
            "content": f"Found {len(hotels)} hotels in {city} within budget:\n" + 
                       "\n".join([f"- {h['hotel_name']}: ${h['price_per_night']}/night (Rating: {h['rating']})" for h in hotels]),
            "hotels": hotels
        }
    except Exception as e:
        log_error(session_name, f"Error in search_hotels: {e}")
        return {"error": str(e)}
