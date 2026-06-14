SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_flights",
        "description": "Search for available flights between origin and destination on a specific date.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": "The airport code or city name of departure (e.g. New York, JFK)."
                },
                "destination": {
                    "type": "string",
                    "description": "The airport code or city name of arrival (e.g. Paris, CDG)."
                },
                "date": {
                    "type": "string",
                    "description": "The date of departure (YYYY-MM-DD)."
                }
            },
            "required": ["origin", "destination", "date"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(origin: str, destination: str, date: str, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Searching flights from {origin} to {destination} on {date}...")
        
        # Mock flight options
        flights = [
            {"flight_id": f"FL-{random.randint(100, 999)}", "airline": "Skyline Airways", "price": random.randint(450, 750), "duration": "8h 15m"},
            {"flight_id": f"FL-{random.randint(100, 999)}", "airline": "EcoJet", "price": random.randint(320, 520), "duration": "9h 45m"}
        ]
        
        log_info(session_name, f"Found {len(flights)} flight options.")
        return {
            "content": f"Found {len(flights)} flight options from {origin} to {destination} on {date}:\n" + 
                       "\n".join([f"- Flight {f['flight_id']} by {f['airline']}: ${f['price']} (Duration: {f['duration']})" for f in flights]),
            "flights": flights
        }
    except Exception as e:
        log_error(session_name, f"Error in search_flights: {e}")
        return {"error": str(e)}
