SCHEMA = {
    "type": "function",
    "function": {
        "name": "budget_expenses",
        "description": "Estimate venues, catering, cake, and decoration costs based on RSVP count.",
        "parameters": {
            "type": "object",
            "properties": {
                "rsvp_count": {
                    "type": "integer",
                    "description": "The number of confirmed guests (RSVPs)."
                }
            },
            "required": ["rsvp_count"]
        }
    }
}

from logger import log_info, log_error

def handler(rsvp_count: int, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Estimating costs for {rsvp_count} guests...")
        
        # Calculate cost breakdown
        venue_cost = 150
        food_per_person = 15
        food_cost = rsvp_count * food_per_person
        cake_cost = 60
        decorations_cost = 40
        total_cost = venue_cost + food_cost + cake_cost + decorations_cost
        
        budget = {
            "rsvp_count": rsvp_count,
            "venue_cost": venue_cost,
            "catering_cost": food_cost,
            "cake_cost": cake_cost,
            "decorations_cost": decorations_cost,
            "total_estimated_cost": total_cost
        }
        
        log_info(session_name, f"Total estimated budget: ${total_cost}")
        return {
            "content": f"Estimated budget breakdown for {rsvp_count} guests:\n- Venue: ${venue_cost}\n- Catering: ${food_cost} (${food_per_person}/head)\n- Cake: ${cake_cost}\n- Decorations: ${decorations_cost}\nTotal Estimated Cost: ${total_cost}.",
            "budget": budget
        }
    except Exception as e:
        log_error(session_name, f"Error in budget_expenses: {e}")
        return {"error": str(e)}
