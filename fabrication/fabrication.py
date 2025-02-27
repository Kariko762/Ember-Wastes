# fabrication/fabrication.py
import json
import os
from text_style import TextStyle

def load_fabrication_recipes():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "fabrication.json")
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            # Flatten the nested tier structure into a single list
            all_recipes = []
            tier_names = {
                "tier1_raw": "Raw",
                "tier2_components": "Components",
                "tier3_composites": "Composites",
                "tier4_ship_components": "Ship Components"
            }
            for tier_key, tier_data in data.get("recipes", {}).items():
                tier_num = int(tier_key.split("tier")[1][0])  # Extract tier number (e.g., 1 from "tier1_raw")
                tier_desc = tier_names.get(tier_key, "Unknown")
                for recipe_name, recipe_details in tier_data.items():
                    recipe = {
                        "name": recipe_name,
                        "tier": tier_num,
                        "tier_desc": tier_desc,
                        "inputs": recipe_details.get("inputs", {}),
                        "outputs": recipe_details.get("outputs", {}),
                        "energyCost": recipe_details.get("energyCost", 0),
                        "successChance": recipe_details.get("successChance", 100),
                        "desc": recipe_details.get("desc", "")
                    }
                    all_recipes.append(recipe)
            return all_recipes
    except Exception as e:
        TextStyle.print_class("Warning", f"Failed to load fabrication.json: {str(e)}. Using default recipes.")
        return [
            {"name": "Iron Ore", "tier": 1, "tier_desc": "Raw", "inputs": {}, "outputs": {"Iron Ore": 5}, "energyCost": 2, "successChance": 90, "desc": "Default Iron Ore"},
            {"name": "Steel Ingot", "tier": 2, "tier_desc": "Components", "inputs": {"Scrap Metal": 2, "Iron Ore": 3}, "outputs": {"Steel Ingot": 1}, "energyCost": 3, "successChance": 85, "desc": "Default Steel Ingot"}
        ]

def fabricate_item(ship_inventory, recipe):
    if not isinstance(recipe, dict):
        TextStyle.print_class("Warning", f"Invalid recipe format: {recipe}")
        return
    
    inputs = recipe.get("inputs", {})
    energy_cost = recipe.get("energyCost", 0)
    can_fabricate = True
    
    # Check inventory for inputs
    for item_name, qty_needed in inputs.items():
        found = False
        for inv_item in ship_inventory:
            if inv_item["name"] == item_name and inv_item["quantity"] >= qty_needed:
                found = True
                break
        if not found:
            can_fabricate = False
            TextStyle.print_class("Warning", f"Insufficient {item_name}! Need {qty_needed}.")
    
    if can_fabricate:
        # Deduct inputs
        for item_name, qty_needed in inputs.items():
            for inv_item in ship_inventory:
                if inv_item["name"] == item_name:
                    inv_item["quantity"] -= qty_needed
                    if inv_item["quantity"] <= 0:
                        ship_inventory.remove(inv_item)
                    break
        
        # Add outputs
        for output_name, qty in recipe.get("outputs", {}).items():
            fabricated_item = {"name": output_name, "quantity": qty}
            for inv_item in ship_inventory:
                if inv_item["name"] == fabricated_item["name"]:
                    inv_item["quantity"] += fabricated_item["quantity"]
                    break
            else:
                ship_inventory.append(fabricated_item)
        
        TextStyle.print_class("Success", f"Fabricated {qty} {output_name} successfully!")
    else:
        TextStyle.print_class("Warning", "Fabrication failed due to insufficient materials!")

def show_recipes(recipes, tier=None):
    if not recipes:
        TextStyle.print_class("Warning", "No recipes available!")
        return
    
    if tier is None:
        # Show all recipes, grouped by tier
        TextStyle.print_class("Information", "\n=== All Fabrication Recipes ===")
        current_tier = None
        for recipe in sorted(recipes, key=lambda x: (x["tier"], x["name"])):  # Sort by tier, then name
            if not isinstance(recipe, dict):
                TextStyle.print_class("Warning", f"Skipping invalid recipe: {recipe}")
                continue
            if current_tier != recipe["tier"]:
                current_tier = recipe["tier"]
                TextStyle.print_class("Information", f"- Tier {current_tier} - {recipe['tier_desc']}")
            input_str = ", ".join(f"{name} x{qty}" for name, qty in recipe.get("inputs", {}).items())
            output_str = ", ".join(f"{name} x{qty}" for name, qty in recipe.get("outputs", {}).items())
            cost_str = f"{input_str}, Energy x{recipe['energyCost']}" if input_str else f"Energy x{recipe['energyCost']}"
            TextStyle.print_class("Information", f"- - {output_str} [Cost: {cost_str}]")
    else:
        # Show tier-specific recipes
        TextStyle.print_class("Information", f"\n=== Tier {tier} Fabrication Recipes ===")
        tier_recipes = [r for r in recipes if isinstance(r, dict) and r.get("tier") == tier]
        if not tier_recipes:
            TextStyle.print_class("Warning", "No recipes available for this tier!")
            return
        for i, recipe in enumerate(tier_recipes, 1):
            input_str = ", ".join(f"{name} x{qty}" for name, qty in recipe.get("inputs", {}).items())
            output_str = ", ".join(f"{name} x{qty}" for name, qty in recipe.get("outputs", {}).items())
            cost_str = f"{input_str}, Energy x{recipe['energyCost']}" if input_str else f"Energy x{recipe['energyCost']}"
            TextStyle.print_class("Information", f"{i}) {output_str} [Cost: {cost_str}]")

def fabrication_menu(player_data, ship_inventory):
    recipes = load_fabrication_recipes()
    while True:
        TextStyle.print_class("Information", "\n=== Fabrication Menu ===")
        TextStyle.print_class("Information", "1) Raw Materials (Tier 1)")
        TextStyle.print_class("Information", "2) Metals & Alloys (Tier 2)")
        TextStyle.print_class("Information", "3) Composites (Tier 3)")
        TextStyle.print_class("Information", "4) Ship Components (Tier 4)")
        TextStyle.print_class("Information", "9) Print Recipe List")
        TextStyle.print_class("Information", "0) Exit")
        
        choice = input("Enter your choice (0-4, 9): ")
        
        if choice == "0":
            TextStyle.print_class("Information", "\nExiting Fabrication Menu...")
            return
        elif choice == "9":
            show_recipes(recipes)  # Show all recipes with tiered format
            input("Press Enter to continue...")
        elif choice in {"1", "2", "3", "4"}:
            tier = int(choice)
            TextStyle.print_class("Information", f"\n=== Tier {tier} Fabrication ===")
            tier_recipes = [r for r in recipes if isinstance(r, dict) and r.get("tier") == tier]
            if not tier_recipes:
                TextStyle.print_class("Warning", "No recipes available for this tier!")
                input("Press Enter to continue...")
                continue
            
            show_recipes(tier_recipes, tier)
            sub_choice = input(f"Select a recipe to fabricate (1-{len(tier_recipes)} or 0 to cancel): ")
            
            if sub_choice == "0":
                continue
            
            try:
                index = int(sub_choice) - 1
                if 0 <= index < len(tier_recipes):
                    selected_recipe = tier_recipes[index]
                    fabricate_item(ship_inventory, selected_recipe)
                else:
                    TextStyle.print_class("Warning", "\nInvalid recipe selection!")
            except ValueError:
                TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
            
            input("Press Enter to continue...")
        else:
            TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-4 or 9.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    test_inventory = [{"name": "Scrap Metal", "quantity": 10}, {"name": "Iron Ore", "quantity": 5}, {"name": "Circuit Board", "quantity": 3}]
    test_player = {"energy": 100}
    fabrication_menu(test_player, test_inventory)
