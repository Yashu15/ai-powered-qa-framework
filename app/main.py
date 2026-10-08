"""Sample business logic for the separate AI-generated unit-test demo."""

def calculate_discount(price: float, discount_percent: float) -> float:
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not (0 <= discount_percent <= 100):
        raise ValueError("Discount must be between 0 and 100")

    return round(price * (1 - discount_percent / 100), 2)

def format_user_name(first_name: str, last_name: str) -> str:
    if not first_name or not last_name:
        raise ValueError("First and last name are required")
    return f"{first_name.strip().title()} {last_name.strip().title()}"