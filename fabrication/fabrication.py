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
            all_recipes = []
            tier_names = {
                "tier1_raw": "Raw",
                "tier2_components": "Components",
                "tier3_composites": "Composites",
                "tier4_ship_components": "Ship Components"
            }
            for tier_key, tier_data in data.get("recipes", {}).items():
                tier_num = int(tier_key.split("tier")[1][0])
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
                        "desc": recipe_details.get("desc", ""),
                        "ammoType": recipe_details.get("ammoType")
                    }
                    all_recipes.append(recipe)
            return all_recipes
    except Exception as e:
        TextStyle.print_class("Warning", f"Failed to load fabrication.json: {str(e)}. Using default recipes.")
        return [
            {"name": "Iron Ore", "tier": 1, "tier_desc": "Raw", "inputs": {}, "outputs": {"Iron Ore": 5}, "energyCost": 2, "successChance": 90, "desc": "Default Iron Ore"}
        ]

def fabricate_item(player_data, ship_inventory, home_inventory, recipe, qty=1):
    if not isinstance(recipe, dict):
        TextStyle.print_class("Warning", f"Invalid recipe format: {recipe}")
        return False
    
    inputs = recipe.get("inputs", {})
    energy_cost = recipe.get("energyCost", 0) * qty
    output_qty = sum(recipe.get("outputs", {}).values()) * qty
    
    # Check availability across both inventories
    for item_name, qty_needed in inputs.items():
        total_needed = qty_needed * qty
        total_available = 0
        for inv_item in ship_inventory + home_inventory:
            if inv_item["name"] == item_name:
                total_available += inv_item["quantity"]
        if total_available < total_needed:
            TextStyle.print_class("Warning", f"Insufficient {item_name}! Need {total_needed}, have {total_available}.")
            return False
    
    if player_data["energy"] < energy_cost:
        TextStyle.print_class("Warning", f"Insufficient energy! Need {energy_cost}, have {player_data['energy']}.")
        return False
    
    # Deduct from inventories (prefer ship_inventory first)
    for item_name, qty_needed in inputs.items():
        remaining = qty_needed * qty
        for inv_item in ship_inventory:
            if inv_item["name"] == item_name and remaining > 0:
                qty_to_use = min(remaining, inv_item["quantity"])
                inv_item["quantity"] -= qty_to_use
                remaining -= qty_to_use
                if inv_item["quantity"] <= 0:
                    ship_inventory.remove(inv_item)
        for inv_item in home_inventory:
            if inv_item["name"] == item_name and remaining > 0:
                qty_to_use = min(remaining, inv_item["quantity"])
                inv_item["quantity"] -= qty_to_use
                remaining -= qty_to_use
                if inv_item["quantity"] <= 0:
                    home_inventory.remove(inv_item)
    
    # Deduct energy
    player_data["energy"] -= energy_cost
    
    # Add outputs
    for output_name, single_qty in recipe.get("outputs", {}).items():
        fabricated_item = {"name": output_name, "quantity": single_qty * qty}
        if recipe.get("ammoType"):
            fabricated_item["ammoType"] = recipe["ammoType"]
        for inv_item in ship_inventory:
            if inv_item["name"] == fabricated_item["name"]:
                inv_item["quantity"] += fabricated_item["quantity"]
                break
        else:
            ship_inventory.append(fabricated_item)
        
        TextStyle.print_class("Success_Mode_Line", f"Fabricated {single_qty * qty} {output_name} successfully! (-{energy_cost} Energy)")
        TextStyle.print_class("Energy", f"Remaining Energy [{player_data['energy']}/{player_data['max_energy']}]")
    
    return True

def calculate_max_craftable(player_data, ship_inventory, home_inventory, recipe):
    inputs = recipe.get("inputs", {})
    energy_cost = recipe.get("energyCost", 0)
    output_qty = sum(recipe.get("outputs", {}).values())
    
    max_craftable = 9  # Default max limit
    if energy_cost > 0:
        max_craftable = min(max_craftable, player_data["energy"] // energy_cost)
    
    for item_name, qty_needed in inputs.items():
        total_available = 0
        for inv_item in ship_inventory + home_inventory:
            if inv_item["name"] == item_name:
                total_available += inv_item["quantity"]
        if qty_needed > 0:
            max_craftable = min(max_craftable, total_available // qty_needed)
    
    return max_craftable if max_craftable > 0 else 0

def show_recipes(recipes, tier, player_data, ship_inventory, home_inventory):
    if not recipes:
        TextStyle.print_class("Warning", "No recipes available!")
        return
    
    if tier is None:
        TextStyle.print_class("Energy", f"Current Energy [{player_data['energy']}/{player_data['max_energy']}]")
        TextStyle.print_class("Information", "\n=== All Fabrication Recipes ===")
        current_tier = None
        for recipe in sorted(recipes, key=lambda x: (x["tier"], x["name"])):
            if not isinstance(recipe, dict):
                TextStyle.print_class("Warning", f"Skipping invalid recipe: {recipe}")
                continue
            if current_tier != recipe["tier"]:
                current_tier = recipe["tier"]
                TextStyle.print_class("Information", f"- Tier {current_tier} - {recipe['tier_desc']}")
            input_str = ", ".join(f"{name} x{qty}" for name, qty in recipe.get("inputs", {}).items())
            output_str = ", ".join(f"{name} x{qty}" for name, qty in recipe.get("outputs", {}).items())
            cost_str = f"{input_str}, Energy x{recipe['energyCost']}" if input_str else f"Energy x{recipe['energyCost']}"
            ammo_str = f" (Ammo: {recipe['ammoType']})" if recipe.get("ammoType") else ""
            TextStyle.print_class("Information", f"- - {output_str}{ammo_str} [Cost: {cost_str}]")
    else:
        TextStyle.print_class("Energy", f"\nCurrent Energy [{player_data['energy']}/{player_data['max_energy']}]")
        TextStyle.print_class("Information", f"=== Tier {tier} Fabrication ===")
        tier_recipes = [r for r in recipes if isinstance(r, dict) and r.get("tier") == tier]
        if not tier_recipes:
            TextStyle.print_class("Warning_Mode_Line", "No recipes available for this tier!")
            return
        for i, recipe in enumerate(tier_recipes, 1):
            inputs = recipe.get("inputs", {})
            can_craft = True
            for item_name, qty_needed in inputs.items():
                total_available = 0
                for inv_item in ship_inventory + home_inventory:
                    if inv_item["name"] == item_name:
                        total_available += inv_item["quantity"]
                if total_available < qty_needed or player_data["energy"] < recipe["energyCost"]:
                    can_craft = False
                    break
            
            input_str = ", ".join(f"{name} x{qty}" for name, qty in inputs.items())
            output_str = ", ".join(f"{name} x{qty}" for name, qty in recipe.get("outputs", {}).items())
            cost_str = f"{input_str}, Energy x{recipe['energyCost']}" if input_str else f"Energy x{recipe['energyCost']}"
            ammo_str = f" (Ammo: {recipe['ammoType']})" if recipe.get("ammoType") else ""
            style = "Success_Mode_Line" if can_craft else "Scavenged"
            TextStyle.print_class(style, f"{i}) {output_str}{ammo_str} [Cost: {cost_str}]")

def collect_fabrication_dependencies(recipes, target_item, t3_items, t2_items, t1_items, raw_items, energy_total):
    def process_item(item_name, qty, multiplier=1):
        recipe = next((r for r in recipes if any(out_name.lower() == item_name.lower() for out_name in r.get("outputs", {}).keys())), None)
        if not recipe:
            raw_items[item_name] = raw_items.get(item_name, 0) + qty * multiplier
            return
        
        tier = recipe["tier"]
        output_qty = sum(recipe.get("outputs", {}).values())
        scale = qty / output_qty if output_qty > 0 else 1
        
        if tier == 3:
            t3_items[item_name] = t3_items.get(item_name, 0) + qty * multiplier
        elif tier == 2:
            t2_items[item_name] = t2_items.get(item_name, 0) + qty * multiplier
        elif tier == 1:
            t1_items[item_name] = t1_items.get(item_name, 0) + qty * multiplier
        
        energy_total[0] += recipe["energyCost"] * scale * multiplier
        
        for input_name, input_qty in recipe.get("inputs", {}).items():
            process_item(input_name, input_qty * scale, multiplier)
    
    target_recipe = next((r for r in recipes if any(out_name.lower() == target_item.lower() for out_name in r.get("outputs", {}).keys())), None)
    if not target_recipe:
        return None
    
    output_str = ", ".join(f"{name} x{qty}" for name, qty in target_recipe.get("outputs", {}).items())
    target_name = f"[T{target_recipe['tier']}] {target_recipe['tier_desc']} \"{output_str}\""
    
    for input_name, qty in target_recipe.get("inputs", {}).items():
        process_item(input_name, qty)
    energy_total[0] += target_recipe["energyCost"]
    
    return target_name

def find_fabrication_path(recipes, target_item):
    t3_items = {}
    t2_items = {}
    t1_items = {}
    raw_items = {}
    energy_total = [0]
    
    target_name = collect_fabrication_dependencies(recipes, target_item, t3_items, t2_items, t1_items, raw_items, energy_total)
    if not target_name:
        TextStyle.print_class("Warning", f"No recipe found for '{target_item}'!")
        return
    
    TextStyle.print_class("Information", f"\n{target_name} - Found")
    
    if t3_items:
        TextStyle.print_class("Information", "\n= = = [Tier 3 Items Required] = = =")
        for i, (item_name, qty) in enumerate(t3_items.items(), 1):
            TextStyle.print_class("Information", f"{i}) {item_name} x{int(qty)}")
    
    if t2_items:
        TextStyle.print_class("Information", "\n= = = [Tier 2 Items Required] = = =")
        for i, (item_name, qty) in enumerate(t2_items.items(), 1):
            TextStyle.print_class("Information", f"{i}) {item_name} x{int(qty)}")
    
    if t1_items:
        TextStyle.print_class("Information", "\n= = = [Tier 1 Items Required] = = =")
        for i, (item_name, qty) in enumerate(t1_items.items(), 1):
            TextStyle.print_class("Information", f"{i}) {item_name} x{int(qty)}")
    
    if raw_items:
        TextStyle.print_class("Information", "\n= = = [Raw Materials Required] = = =")
        for i, (item_name, qty) in enumerate(raw_items.items(), 1):
            TextStyle.print_class("Information", f"{i}) {item_name} x{int(qty)}")
    
    TextStyle.print_class("Information", f"\n= = = Energy x{int(energy_total[0])} = = =")

def fabrication_menu(player_data, ship_inventory, home_inventory):
    recipes = load_fabrication_recipes()
    while True:
        TextStyle.print_class("Information", "\n=== Fabrication Menu ===")
        TextStyle.print_class("Information", "1) Raw Materials (Tier 1)")
        TextStyle.print_class("Information", "2) Metals & Alloys (Tier 2)")
        TextStyle.print_class("Information", "3) Composites (Tier 3)")
        TextStyle.print_class("Information", "4) Ship Components (Tier 4)")
        TextStyle.print_class("Information", "8) Find Recipe Branch")
        TextStyle.print_class("Information", "9) Print Recipe List")
        TextStyle.print_class("Information", "0) Exit")
        
        choice = input("Enter your choice (0-4, 8, 9): ")
        
        if choice == "0":
            TextStyle.print_class("Information", "\nExiting Fabrication Menu...")
            return
        elif choice == "8":
            target_item = input("What Item are you trying to fabricate? : ").strip()
            find_fabrication_path(recipes, target_item)
            input("Press Enter to continue...")
        elif choice == "9":
            show_recipes(recipes, None, player_data, ship_inventory, home_inventory)
            input("Press Enter to continue...")
        elif choice in {"1", "2", "3", "4"}:
            tier = int(choice)
            tier_recipes = [r for r in recipes if isinstance(r, dict) and r.get("tier") == tier]
            if not tier_recipes:
                TextStyle.print_class("Warning", "No recipes available for this tier!")
                input("Press Enter to continue...")
                continue
            
            show_recipes(tier_recipes, tier, player_data, ship_inventory, home_inventory)
            sub_choice = input(f"Select a recipe to fabricate (1-{len(tier_recipes)} or 0 to cancel): ")
            
            if sub_choice == "0":
                continue
            
            try:
                index = int(sub_choice) - 1
                if 0 <= index < len(tier_recipes):
                    selected_recipe = tier_recipes[index]
                    max_craftable = calculate_max_craftable(player_data, ship_inventory, home_inventory, selected_recipe)
                    if max_craftable > 0:
                        qty = int(input(f"How many to craft (0-{max_craftable}): "))
                        if 0 <= qty <= max_craftable:
                            fabricate_item(player_data, ship_inventory, home_inventory, selected_recipe, qty)
                        else:
                            TextStyle.print_class("Warning", f"Invalid quantity! Must be between 0 and {max_craftable}.")
                    else:
                        TextStyle.print_class("Warning", "Cannot craft this item with current resources!")
                else:
                    TextStyle.print_class("Warning", "\nInvalid recipe selection!")
            except ValueError:
                TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
            
            input("Press Enter to continue...")
        else:
            TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-4, 8, or 9.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    test_ship_inventory = [{"name": "Scrap Metal", "quantity": 10}, {"name": "Iron Ore", "quantity": 5}, {"name": "Circuit Board", "quantity": 3}]
    test_home_inventory = [{"name": "Copper Ore", "quantity": 20}, {"name": "Organic Resin", "quantity": 15}]
    test_player = {"energy": 100, "max_energy": 250}
    fabrication_menu(test_player, test_ship_inventory, test_home_inventory)