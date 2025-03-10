# utils.py
import os
import json
import random
from text_style import TextStyle

def load_new_game_variables():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "functions", "newGameVariables.json")
    if not os.path.exists(file_path):
        TextStyle.print_class("Warning", f"\nError: 'newGameVariables.json' not found in {script_dir}/functions")
        input("Press Enter to continue...")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        TextStyle.print_class("Warning", "\nError: Invalid JSON format in newGameVariables.json!")
        input("Press Enter to continue...")
        return None

def load_space_classification():
    json_file = "space_classification.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        TextStyle.print_class("Warning", f"\nError: '{json_file}' not found in {script_dir}")
        input("Press Enter to continue...")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        TextStyle.print_class("Warning", "\nError: Invalid JSON format in space_classification.json!")
        input("Press Enter to continue...")
        return None

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def load_general_data():
    json_file = "general.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        TextStyle.print_class("Warning", f"\nError: '{json_file}' not found in {script_dir}")
        input("Press Enter to continue...")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        TextStyle.print_class("Warning", "\nError: Invalid JSON format in general.json!")
        input("Press Enter to continue...")
        return None
    
 #Remove or decrement an item from inventory based on quantity.
def inventoryRemove(inventory, item_to_remove):
    """Remove or decrement an item from inventory based on quantity."""
    for i, inv_item in enumerate(inventory):
        if inv_item["name"] == item_to_remove["name"] and inv_item.get("type") == item_to_remove.get("type"):
            qty = inv_item.get("quantity", 1)  # Default to 1 if no quantity
            if qty > 1:
                inv_item["quantity"] = qty - 1  # Decrement
            else:
                inventory.pop(i)  # Remove if qty would hit 0
            return True
    return False  # Item not found