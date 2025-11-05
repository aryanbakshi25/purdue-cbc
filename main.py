#!/usr/bin/env python3
"""Purdue Dining Hall Recommender - Mini Hackathon Prototype"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Food category mapping - maps user input to standardized categories
# Add more mappings here as needed (e.g., "cake" -> "Desserts", "burger" -> "Burgers")
FOOD_CATEGORY_MAP = {
    # Desserts
    "cake": "Desserts",
    "cakes": "Desserts",
    "cookie": "Desserts",
    "cookies": "Desserts",
    "ice cream": "Desserts",
    "icecream": "Desserts",
    "pie": "Desserts",
    "pies": "Desserts",
    "brownie": "Desserts",
    "brownies": "Desserts",
    "sweet": "Desserts",
    "sweets": "Desserts",
    "dessert": "Desserts",
    "desserts": "Desserts",
    # Burgers
    "burger": "Burgers",
    "burgers": "Burgers",
    "hamburger": "Burgers",
    "cheeseburger": "Burgers",
    # Pizza
    "pizza": "Pizza",
    "pizzas": "Pizza",
    "slice": "Pizza",
    # Salad
    "salad": "Salad",
    "salads": "Salad",
    # Vegan/Vegetarian
    "vegan": "Vegan",
    "vegetarian": "Vegetarian",
    "veggie": "Vegetarian",
    # Wings
    "wing": "Wings",
    "wings": "Wings",
    "chicken wings": "Wings",
    # Tacos
    "taco": "Tacos",
    "tacos": "Tacos",
    # Pasta
    "pasta": "Pasta",
    "spaghetti": "Pasta",
    "noodles": "Pasta",
    # Soup
    "soup": "Soup",
    "soups": "Soup",
    # Stir Fry
    "stir fry": "Stir Fry",
    "stirfry": "Stir Fry",
    "stir-fry": "Stir Fry",
    # Grill
    "grill": "Grill",
    "grilled": "Grill",
}

# Step 1: Define Dining Hall Data Structure
# To update food options, modify the "foods" list for each dining hall
# Note: All dining halls automatically serve "Desserts" when open
dining_halls = {
    "Earhart": {
        "foods": ["Pizza", "Burgers", "Salad", "Pasta"],
        "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "open_time": 700,
        "close_time": 2100
    },
    "Ford": {
        "foods": ["Vegan", "Vegetarian", "Stir Fry", "Soup"],
        "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "open_time": 1100,
        "close_time": 2000
    },
    "Wiley": {
        "foods": ["Pizza", "Wings", "Grill"],
        "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "open_time": 1700,
        "close_time": 2200
    },
    "Windsor": {
        "foods": ["Burgers", "Tacos", "Salad", "Vegan"],
        "open_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "open_time": 730,
        "close_time": 1930
    }
}

# Helper functions for time conversion
def time_24h_to_12h(time_24h):
    """Convert 24-hour format (e.g., 1830) to 12-hour format (e.g., '6:30 PM')"""
    hours = time_24h // 100
    minutes = time_24h % 100
    
    period = "AM" if hours < 12 else "PM"
    if hours == 0:
        hours = 12
    elif hours > 12:
        hours -= 12
    
    return f"{hours}:{minutes:02d} {period}"

def time_12h_to_24h(time_str):
    """Convert 12-hour format (e.g., '6:30 PM') to 24-hour format integer (e.g., 1830)"""
    try:
        # Parse format like "6:30 PM" or "11:00 AM"
        time_part, period = time_str.strip().rsplit(' ', 1)
        period = period.upper()
        
        hours, minutes = map(int, time_part.split(':'))
        
        if period == "PM" and hours != 12:
            hours += 12
        elif period == "AM" and hours == 12:
            hours = 0
        
        return hours * 100 + minutes
    except:
        # If parsing fails, try to get current time
        now = datetime.now()
        return now.hour * 100 + now.minute

def normalize_food_input(user_input):
    """
    Convert user input to standardized food category.
    Maps things like "cake" to "Desserts", "burger" to "Burgers", etc.
    
    Args:
        user_input (str): User's food input
    
    Returns:
        str: Normalized food category
    """
    user_input_lower = user_input.lower().strip()
    
    # Check if it's already a category (case-insensitive match)
    all_categories = set()
    for hall in dining_halls.values():
        all_categories.update(f.lower() for f in hall["foods"])
    all_categories.add("desserts")  # Always include desserts
    
    # If input matches a category directly, return it capitalized
    for category in all_categories:
        if category == user_input_lower:
            return category.capitalize()
    
    # Check food category mapping
    if user_input_lower in FOOD_CATEGORY_MAP:
        return FOOD_CATEGORY_MAP[user_input_lower]
    
    # If no mapping found, return the original input (capitalized)
    return user_input.capitalize()

# Step 3: Real-Time Filtering Logic
def find_recommendations(preferred_food, current_time):
    """
    Filter dining halls based on food preference and operating hours.
    
    Args:
        preferred_food (str): User's preferred food type
        current_time (int): Current time in 24-hour format (e.g., 1830)
    
    Returns:
        list: Dictionary with hall info and formatted times
    """
    recommendations = []
    
    # Normalize the food input (e.g., "cake" -> "Desserts")
    normalized_food = normalize_food_input(preferred_food)
    
    for hall_name, hall_info in dining_halls.items():
        # Check if hall is currently open
        is_open = hall_info["open_time"] <= current_time <= hall_info["close_time"]
        
        if not is_open:
            continue
        
        # Get all foods served at this hall (including desserts if open)
        available_foods = list(hall_info["foods"])
        if is_open:
            available_foods.append("Desserts")
        
        # Check if hall serves preferred food (case-insensitive)
        serves_food = any(food.lower() == normalized_food.lower() for food in available_foods)
        
        # Add to recommendations if criteria met
        if serves_food:
            recommendations.append({
                "name": hall_name,
                "open_time": time_24h_to_12h(hall_info["open_time"]),
                "close_time": time_24h_to_12h(hall_info["close_time"]),
                "foods": available_foods
            })
    
    return recommendations

@app.route('/')
def index():
    """Render the main page"""
    all_foods = set()
    for hall in dining_halls.values():
        all_foods.update(hall["foods"])
    # Always include Desserts since all open halls serve it
    all_foods.add("Desserts")
    return render_template('index.html', foods=sorted(all_foods))

@app.route('/recommend', methods=['POST'])
def recommend():
    """API endpoint to get dining hall recommendations"""
    data = request.get_json()
    preferred_food = data.get('food', '').strip()
    time_input = data.get('time', '').strip()
    
    # Convert 12-hour time to 24-hour for internal calculation
    current_time = time_12h_to_24h(time_input)
    
    recommendations = find_recommendations(preferred_food, current_time)
    
    return jsonify({
        "success": True,
        "recommendations": recommendations,
        "count": len(recommendations)
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)