SCHEMA = {
    "type": "function",
    "function": {
        "name": "generate_travel_itinerary",
        "description": "Compile all flight and accommodation bookings into a structured travel itinerary document.",
        "parameters": {
            "type": "object",
            "properties": {
                "bookings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "description": "A booking dictionary."
                    },
                    "description": "The list of flight and hotel bookings."
                }
            },
            "required": ["bookings"]
        }
    }
}

from logger import log_info, log_error

def handler(bookings: list, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Generating travel itinerary for {len(bookings)} bookings...")
        
        # Build clean visual layout
        lines = []
        lines.append("=========================================")
        lines.append("           YOUR TRAVEL ITINERARY         ")
        lines.append("=========================================")
        for i, b in enumerate(bookings, 1):
            b_type = b.get("booking_type", "Booking").upper()
            lines.append(f"{i}. [{b_type}]")
            if b_type == "FLIGHT":
                lines.append(f"   - Flight ID: {b.get('flight_id', 'N/A')}")
                lines.append(f"   - Confirmation Code: {b.get('booking_code', 'N/A')}")
            elif b_type == "HOTEL":
                lines.append(f"   - Hotel: {b.get('hotel_name', 'N/A')}")
                lines.append(f"   - Stay: {b.get('nights', 1)} nights")
                lines.append(f"   - Reservation Code: {b.get('reservation_code', 'N/A')}")
            elif b_type == "CAR_RENTAL":
                lines.append(f"   - City: {b.get('city', 'N/A')}")
                lines.append(f"   - Vehicle: {b.get('car_type', 'N/A')}")
                lines.append(f"   - Rental Code: {b.get('rental_code', 'N/A')}")
            elif b_type == "ATTRACTION":
                lines.append(f"   - City: {b.get('city', 'N/A')}")
                lines.append(f"   - Activity: {b.get('activity', 'N/A')}")
                lines.append(f"   - Ticket Code: {b.get('ticket_code', 'N/A')}")
            lines.append(f"   - Status: {b.get('status', 'Confirmed')}")
            lines.append("-----------------------------------------")
        lines.append("Wish you a safe and wonderful trip!")
        lines.append("=========================================")
        
        itinerary = "\n".join(lines)
        log_info(session_name, "Itinerary generated successfully.")
        return {
            "content": itinerary,
            "itinerary_text": itinerary
        }
    except Exception as e:
        log_error(session_name, f"Error in generate_travel_itinerary: {e}")
        return {"error": str(e)}
