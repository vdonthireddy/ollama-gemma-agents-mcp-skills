SCHEMA = {
    "type": "function",
    "function": {
        "name": "order_cake",
        "description": "Order a customized birthday cake with choice of flavor, size, and custom inscription.",
        "parameters": {
            "type": "object",
            "properties": {
                "flavor": {
                    "type": "string",
                    "description": "Flavor of the cake (e.g. Chocolate, Vanilla, Strawberry, Red Velvet)."
                },
                "size": {
                    "type": "string",
                    "description": "Size of the cake (e.g. Small 8-inch, Medium 10-inch, Large Quarter-sheet)."
                },
                "inscription": {
                    "type": "string",
                    "description": "Text to write on the cake (e.g. 'Happy Birthday Alex!')."
                }
            },
            "required": ["flavor", "size", "inscription"]
        }
    }
}

import random
from logger import log_info, log_error

def handler(flavor: str, size: str, inscription: str, session_name: str = "default") -> dict:
    try:
        log_info(session_name, f"Placing order for custom '{flavor}' cake ({size}) with inscription: '{inscription}'...")
        
        # Mock cake order details
        order_num = "CKE-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
        booking = {
            "booking_type": "cake",
            "flavor": flavor,
            "size": size,
            "inscription": inscription,
            "order_number": order_num,
            "status": "ordered"
        }
        
        log_info(session_name, f"Cake ordered. Order Number: {order_num}")
        return {
            "content": f"Cake order placed successfully! Order Number: {order_num}. Description: {size} {flavor} cake with inscription '{inscription}'.",
            "booking": booking
        }
    except Exception as e:
        log_error(session_name, f"Error in order_cake: {e}")
        return {"error": str(e)}
