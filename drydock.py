# drydock.py
from text_style import TextStyle
from utils import load_general_data

def repair_ship(player_data, ship_inventory, home_inventory):
    general_data = load_general_data()
    if not general_data:
        return
    
    repair_ratios = general_data["repair_ratios"]
    
    TextStyle.print_class("Information", "\n=== Repair Menu ===")
    TextStyle.print_class("Information", f"Hull: {player_data['hull']}/{player_data['max_hull']} | Shield: {player_data['shield']}/{player_data['max_shield']} | Energy: {player_data['energy']}")
    
    if player_data["hull"] >= player_data["max_hull"] and player_data["shield"] >= player_data["max_shield"]:
        TextStyle.print_class("Information", "No repairs required.")
        input("Press Enter to continue...")
        return
    
    all_items = ship_inventory + home_inventory
    repair_items = [item for item in all_items if item["name"] in repair_ratios and item["quantity"] > 0]
    
    if not repair_items:
        TextStyle.print_class("Warning", "No items available to use for repairs!")
        input("Press Enter to continue...")
        return
    
    TextStyle.print_class("Information", "\nAvailable Items:")
    for i, item in enumerate(repair_items, 1):
        ratio_text = ""
        if "hull" in repair_ratios[item["name"]]:
            ratio_text += f"1 x {item['name']} = {repair_ratios[item['name']]['hull']} Hull"
        if "shield" in repair_ratios[item["name"]]:
            ratio_text += f"{' | ' if ratio_text else ''}1 x {item['name']} = {repair_ratios[item['name']]['shield']} Shield"
        TextStyle.print_class("Information", f"{i}) {item['name']} ({item['quantity']}) [{ratio_text}]")
    TextStyle.print_class("Information", "0) Cancel")
    
    try:
        choice = int(input(TextStyle.print_class("Information", "\nSelect an item to use for repairs (0-{}): ".format(len(repair_items)), delay_to_display=0, display_mode="instant", print_output=False)))
        if choice == 0:
            return
        
        if choice < 1 or choice > len(repair_items):
            TextStyle.print_class("Warning", "\nInvalid choice!")
            input("Press Enter to continue...")
            return
        
        item = repair_items[choice - 1]
        qty = int(input(TextStyle.print_class("Information", f"How many {item['name']} to use (1-{item['quantity']})? ", delay_to_display=0, display_mode="instant", print_output=False)))
        if qty < 1 or qty > item["quantity"]:
            TextStyle.print_class("Warning", f"\nInvalid quantity! Must be between 1 and {item['quantity']}.")
            input("Press Enter to continue...")
            return
        
        hull_repair = repair_ratios[item["name"]].get("hull", 0) * qty
        shield_repair = repair_ratios[item["name"]].get("shield", 0) * qty
        
        hull_restored = min(hull_repair, player_data["max_hull"] - player_data["hull"])
        shield_restored = min(shield_repair, player_data["max_shield"] - player_data["shield"])
        
        if hull_restored > 0:
            player_data["hull"] += hull_restored
            TextStyle.print_class("Information", f"\nRepaired {hull_restored} hull using {qty} {item['name']}.")
        if shield_restored > 0:
            player_data["shield"] += shield_restored
            TextStyle.print_class("Information", f"\nRepaired {shield_restored} shield using {qty} {item['name']}.")
        if hull_restored == 0 and shield_restored == 0:
            TextStyle.print_class("Warning", "\nNo repairs needed for this item!")
            input("Press Enter to continue...")
            return
        
        item["quantity"] -= qty
        if item["quantity"] <= 0:
            if item in ship_inventory:
                ship_inventory.remove(item)
            elif item in home_inventory:
                home_inventory.remove(item)
        
        if shield_restored > 0:
            player_data["armor_class"] = 10 + int(player_data["hull"] / 10) + int(player_data["shield"] / 10)
            TextStyle.print_class("Information", f"Armor Class updated to {player_data['armor_class']}.")
        
    except ValueError:
        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
    input("Press Enter to continue...")

def fit_components(player_data, ship_inventory):
    TextStyle.print_class("Information", "\n=== Fitting Menu ===")
    TextStyle.print_class("Information", f"Equipped Weapons: {', '.join([w['name'] for w in player_data['weapons']])}")
    TextStyle.print_class("Information", f"Hull: {player_data['hull']}/{player_data['max_hull']} | AC: {player_data['armor_class']}")
    
    TextStyle.print_class("Information", "\nAvailable Components:")
    components = [item for item in ship_inventory if item["name"] in ["Laser", "Plasma Cannon", "Shield Generator"]]
    if not components:
        TextStyle.print_class("Warning", "No components available to fit!")
    else:
        for i, item in enumerate(components, 1):
            TextStyle.print_class("Information", f"{i}) {item['name']} ({item['quantity']})")
    TextStyle.print_class("Information", "0) Return to Drydock Menu")
    
    try:
        choice = int(input(TextStyle.print_class("Information", "\nSelect a component to equip (0-{}): ".format(len(components)), delay_to_display=0, display_mode="instant", print_output=False)))
        if choice == 0:
            return
        
        if choice < 1 or choice > len(components):
            TextStyle.print_class("Warning", "\nInvalid choice!")
            input("Press Enter to continue...")
            return
        
        item = components[choice - 1]
        if item["name"] == "Laser":
            player_data["weapons"] = [{"name": "Laser", "damage": "d8"}]
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                ship_inventory.remove(item)
            TextStyle.print_class("Information", "\nEquipped Laser (d8 damage).")
        elif item["name"] == "Plasma Cannon":
            player_data["weapons"] = [{"name": "Plasma Cannon", "damage": "2d6"}]
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                ship_inventory.remove(item)
            TextStyle.print_class("Information", "\nEquipped Plasma Cannon (2d6 damage).")
        elif item["name"] == "Shield Generator":
            player_data["shield"] += 20
            player_data["max_shield"] += 20
            player_data["armor_class"] = 10 + int(player_data["hull"] / 10) + int(player_data["shield"] / 10)
            item["quantity"] -= 1
            if item["quantity"] <= 0:
                ship_inventory.remove(item)
            TextStyle.print_class("Information", "\nEquipped Shield Generator (+20 shield, updated AC).")
        
    except ValueError:
        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
    input("Press Enter to continue...")

def display_drydock_menu(player_data):
    TextStyle.print_class("Information", "\n=== Drydock Menu ===")
    TextStyle.print_class("Information", f"Hull: {player_data['hull']}/{player_data['max_hull']} | Energy: {player_data['energy']} | Shield: {player_data['shield']}/{player_data['max_shield']}")
    TextStyle.print_class("Information", "1) Repair Ship")
    TextStyle.print_class("Information", "2) Fit Components")
    TextStyle.print_class("Information", "0) Return to Home Menu")
    TextStyle.print_class("Information", "================")