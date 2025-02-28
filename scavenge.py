# scavenge.py
import json
import random
import os
import time
from text_style import TextStyle
#import systems.systemsCreateAsteroids
import scavenge_energy_siphon as energy_siphon
import combat.combat_trigger as combat_trigger
import vaults

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val, max_val)
    return roll, f"[{die_name}({roll})]"

def scavenge_items(num_items_to_find, location_type):
    items = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "items.json")
    
    try:
        with open(file_path, 'r') as file:
            all_items = json.load(file)
        
        available_items = all_items.get(location_type, [])
        if not available_items:
            return []
        
        item_names = [item["name"] for item in available_items]
        chances = [item["chance"] for item in available_items]
        ammo_types = [item.get("ammoType") for item in available_items]
        cumulative = []
        running_total = 0
        for chance in chances:
            running_total += chance * 100
            cumulative.append(running_total)
        
        for _ in range(num_items_to_find):
            roll, roll_str = roll_percentile()
            for i, upper_bound in enumerate(cumulative):
                if roll <= upper_bound:
                    item_name = item_names[i]
                    ammo_type = ammo_types[i] if i < len(ammo_types) and ammo_types[i] else None
                    break
            quantity = random.randint(1, 3)
            items.append((roll_str, roll, item_name, quantity, ammo_type))
    except Exception as e:
        TextStyle.print_class("Warning_Mode_Line", f"Error scavenging items: {str(e)}")
    
    return items

def load_scavenge_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "scavenge.json")
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except:
        return {
            "energyThreshold": 40,
            "minEnergy": 20,
            "successThreshold": 40,
            "stages": [
                {"percent": 0, "message": "Plotting Coordinates", "energy": 0},
                {"percent": 10, "message": "Approaching Site", "energy": 0},
                {"percent": 20, "message": "Approaching Site", "energy": 10},
                {"percent": 30, "message": "Scanning Location", "energy": 0},
                {"percent": 40, "message": "Scanning Location", "energy": 2},
                {"percent": 50, "message": "Analysing Find", "energy": 0},
                {"percent": 60, "message": "Analysing Find", "energy": 0},
                {"percent": 70, "message": "Analysing Find", "energy": 3},
                {"percent": 80, "message": "Salvaging Item(s)", "energy": 0},
                {"percent": 90, "message": "Salvaging Item(s)", "energy": 5},
                {"percent": 100, "message": "Salvage Operation Concluded", "energy": 0}
            ],
            "securityZones": {
                "moderate": {"min": 0.3, "max": 0.6, "extraItems": {"min": 0, "max": 1, "die": "d2"}},
                "unsecure": {"min": 0.0, "max": 0.2, "extraItems": {"min": 0, "max": 2, "die": "d3"}}
            },
            "itemCountRange": {"min": 1, "max": 3}
        }

def scavenge_location(current_system, player_data, ship_inventory):
    config = load_scavenge_config()
    energy_threshold = config["energyThreshold"]
    min_energy = config["minEnergy"]
    success_threshold = config["successThreshold"]
    stages = config["stages"]
    security_zones = config["securityZones"]
    
    if player_data["energy"] < min_energy:
        TextStyle.print_class("Warning_Mode_Line", f"\nNot enough energy! Required: {min_energy}, Available: {player_data['energy']}")
        input("Press Enter to continue...")
        return
    elif player_data["energy"] < energy_threshold:
        TextStyle.print_class("Warning_Mode_Line", f"\nWarning: You won't have enough energy to get home. Continue to scavenge (y/n)?")
        choice = input().lower()
        if choice != "y":
            input("Press Enter to continue...")
            return
    
    locations_list = []
    for parent in current_system["children"]:
        if parent["type"] != "Asteroid Belt":
            locations_list.append({"obj": parent, "parent": None})
        if "children" in parent:
            for child in parent["children"]:
                locations_list.append({"obj": child, "parent": parent})
    
    if not locations_list:
        TextStyle.print_class("Warning_Mode_Line", "\nNo locations available to scavenge!")
        input("Press Enter to continue...")
        return
    
    print("\nAvailable locations:")
    for i, loc in enumerate(locations_list):
        obj = loc["obj"]
        parent = loc["parent"]
        name = obj["name"]
        scavenged_text = " (scavenged)" if obj.get("scavenged", False) else ""
        if parent and parent["type"] == "Asteroid Belt":
            if i == 0 or locations_list[i-1]["parent"] != parent:
                TextStyle.print_class("Information", f"- {parent['name']} (Asteroid Belt)")
            display_name = f"- {name}"
        else:
            display_name = name
        
        full_line = f"{i}) {display_name} ({obj['type']})"
        if scavenged_text:
            TextStyle.print_class("Warning_Mode_Line", f"{full_line}{scavenged_text}")
        else:
            TextStyle.print_class("Information", full_line)
    
    try:
        choice = int(input("Select a location to scavenge (0-9): "))
        if 0 <= choice < len(locations_list):
            loc = locations_list[choice]
            obj = loc["obj"]
            if obj.get("scavenged", False):
                TextStyle.print_class("Warning_Mode_Line", f"\n{obj['name']} has already been scavenged!")
                input("Press Enter to continue...")
                return
            
            location_name = obj["name"]
            # Updated location_type mapping to match new items.json
            location_type = "natural.planet" if obj["type"] == "Planet" else \
                            "asteroid" if obj["type"] == "Asteroid" else \
                            "natural.planet" if obj["type"] == "Moon" else \
                            "man-made" if obj["type"] == "Man-Made" else \
                            "wreckage" if obj["type"] == "Unknown" else "natural.planet"  # Default to natural.planet
            
            TextStyle.print_class("Information", "- - -")
            time.sleep(0.3)
            progress = 0
            energy_cost = 0
            
            success_roll, success_roll_str = roll_percentile()
            items_found = False
            num_items = 0
            yield_die = ""
            
            for stage in stages:
                percent = stage["percent"]
                message = stage["message"]
                energy = stage["energy"]
                bar = "#" * (percent // 10) + " " * (10 - percent // 10)
                extra = ""
                
                if percent == 40:
                    extra = f" {success_roll_str} ({success_roll}%): {'Success' if success_roll >= success_threshold else 'Failure'}"
                    items_found = success_roll >= success_threshold
                    color = "Success_Mode_Line" if success_roll >= success_threshold else "Warning_Mode_Line"
                elif percent == 70 and items_found:
                    num_items, yield_die = roll_dice(config["itemCountRange"]["min"], config["itemCountRange"]["max"], "d3")
                    extra = f" {yield_die}: {num_items} Item(s) Found"
                    color = "Success_Mode_Line"
                else:
                    color = "Information"
                
                TextStyle.print_class(color, f"Scavenging {location_name}: [{bar}] {percent}% - {message}{extra}{' (-' + str(energy) + ' Energy)' if energy > 0 else ''}")
                time.sleep(0.3)
                
                if energy > 0 and player_data["energy"] >= energy:
                    player_data["energy"] -= energy
                    energy_cost += energy
                elif energy > 0:
                    TextStyle.print_class("Warning_Mode_Line", f"Not enough energy! Required: {energy}, Available: {player_data['energy']}")
                    obj["scavenged"] = True
                    input("Press Enter to continue...")
                    return
                
                if percent == 50 and not items_found:
                    TextStyle.print_class("Warning_Mode_Line", "No resources found. Scavenging aborted.")
                    TextStyle.print_class("Information", f"Total Energy Used: {energy_cost}")
                    obj["scavenged"] = True
                    input("Press Enter to continue...")
                    combat_trigger.combatCheck(player_data, current_system, "main_game_loop")
                    return
            
            TextStyle.print_class("Information", "- - -")
            
            if items_found:
                security_zone = player_data.get("security_zone", 1.0)
                sec_roll = 0
                sec_roll_str = "[none]"
                
                for zone in security_zones.values():
                    if zone["min"] <= security_zone <= zone["max"]:
                        sec_roll, sec_roll_str = roll_dice(zone["extraItems"]["min"], zone["extraItems"]["max"], zone["extraItems"]["die"])
                        break
                
                if sec_roll_str != "[none]":
                    color = "Success_Mode_Line" if sec_roll > 0 else "Scavenged"
                    TextStyle.print_class(color, f"Rolling Security Zone Modifier {sec_roll_str}: {sec_roll} Additional Items Found")
                    TextStyle.print_class("Information", "- - -")
                
                total_items = num_items + sec_roll
                found_items = scavenge_items(total_items, location_type)
                
                TextStyle.print_class("Information", f"Total Energy Used: {energy_cost}")
                TextStyle.print_class("Information", f"Total Items Found: {total_items}")
                item_counter = 1
                for roll_str, roll, item_name, qty, ammo_type in found_items:
                    loot_entry = {"name": item_name, "quantity": qty}
                    if ammo_type:
                        loot_entry["ammoType"] = ammo_type
                    display_str = f"- Item {item_counter} {roll_str} ({roll}%): {item_name} ({qty})"
                    if ammo_type:
                        display_str += f" (Ammo: {ammo_type})"
                    TextStyle.print_class("Success_Mode_Line", display_str)
                    item_counter += 1
                    for inv_item in ship_inventory:
                        if inv_item["name"] == item_name:
                            inv_item["quantity"] += qty
                            break
                    else:
                        ship_inventory.append(loot_entry)
            
            if obj["type"] == "Man-Made" or (obj["type"] == "Unknown" and "wreckage" in obj):
                vaults.vaultCheck(player_data, ship_inventory)
                energy_siphon.scavenge_energy(obj, player_data, ship_inventory)
            
            obj["scavenged"] = True
            input("Press Enter to continue...")
            combat_trigger.combatCheck(player_data, current_system, "main_game_loop")
    except ValueError:
        TextStyle.print_class("Warning_Mode_Line", "Invalid choice! Please enter a number.")
        input("Press Enter to continue...")

if __name__ == "__main__":
    test_system = {
        "children": [
            {"name": "Rocky Planet", "type": "Planet", "children": [{"name": "Orbital Station", "type": "Man-Made"}]},
            {"name": "Wreckage", "type": "Unknown", "wreckage": True}
        ]
    }
    test_player = {"energy": 100, "universal_signature": 0, "security_zone": 0.3}
    test_inventory = []
    scavenge_location(test_system, test_player, test_inventory)