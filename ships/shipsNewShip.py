# ships/shipsNewShip.py
import json
import random
import os
from text_style import TextStyle
from utils import roll_percentile

def load_ship_data():
    json_file = "ships.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        TextStyle.print_class("Warning", f"\nError: '{json_file}' not found in {script_dir}")
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        TextStyle.print_class("Warning", "\nError: Invalid JSON format in ships.json!")
        return None

def weighted_roll(options, chance_key):
    roll = random.uniform(0, 1)
    cumulative = 0
    for option in options:
        cumulative += option[chance_key]
        if roll <= cumulative:
            return option
    return options[-1]

def create_ship(alignment=None, ship_type=None, ship_inventory=None):
    ship_data = load_ship_data()
    if not ship_data:
        return None
    
    if ship_inventory is None:
        ship_inventory = []  # Default to empty list if not provided
    
    vars = ship_data["shipVariables"]
    custom = ship_data["shipCustomization"]
    
    hull = random.randint(vars["hullRange"]["min"], vars["hullRange"]["max"])
    shield = random.randint(vars["shieldRange"]["min"], vars["shieldRange"]["max"])
    power = random.randint(vars["powerRange"]["min"], vars["powerRange"]["max"])
    energy = random.randint(vars["energyRange"]["min"], vars["energyRange"]["max"])
    storage = random.randint(vars["storageRange"]["min"], vars["storageRange"]["max"])
    level = random.randint(vars["levelRange"]["min"], vars["levelRange"]["max"])
    
    if ship_type:
        ship_class = next((cls for cls in custom["classes"] if cls["name"] == ship_type), None)
        if not ship_class:
            TextStyle.print_class("Warning", f"Invalid ship type '{ship_type}'! Using random class.")
            ship_class = weighted_roll(custom["classes"], "chance")
    else:
        ship_class = weighted_roll(custom["classes"], "chance")
    
    if alignment:
        align = next((a for a in custom["alignments"] if a["name"] == alignment), None)
        if not align:
            TextStyle.print_class("Warning", f"\nInvalid alignment '{alignment}' specified! Using random alignment.")
            align = weighted_roll([a for a in custom["alignments"] if a["chance"] > 0], "chance")
    else:
        align = weighted_roll([a for a in custom["alignments"] if a["chance"] > 0], "chance")
    
    hull += ship_class["hullBonus"]
    shield += ship_class["shieldBonus"]
    power += ship_class["powerBonus"]
    energy += ship_class["energyBonus"]
    storage += ship_class["storageBonus"]
    
    max_hull = hull
    max_shield = shield
    max_energy = energy
    max_power = power
    initiative_modifier = power // 10
    armor_class = random.randint(ship_class["armorClassRange"]["min"], ship_class["armorClassRange"]["max"])
    disengage = random.randint(ship_class["disengageRange"]["min"], ship_class["disengageRange"]["max"])
    
    # Assign weapons based on hardPoints and percentile chances
    hard_points = ship_class.get("hardPoints", 1)
    weapon_chances = vars["weaponChancePerHardpoint"]
    equipped_weapons = []
    
    for i in range(hard_points):
        chance_entry = next((wc for wc in weapon_chances if wc["weapons"] == i + 1), weapon_chances[0])
        chance = chance_entry["chance"]
        roll, roll_str = roll_percentile()
        if roll <= chance:
            weapon = weighted_roll(custom["weapons"], "chance")
            if len(equipped_weapons) < len(custom["weapons"]) and not any(w["name"] == weapon["name"] for w in equipped_weapons):
                equipped_weapons.append({"name": weapon["name"], "damage": weapon["damage"], "ammoType": weapon.get("ammoType")})
                # Add ammo if weapon has an ammoType (not Power)
                if "ammoType" in weapon and weapon["ammoType"] != "Power":
                    ammo_type = weapon["ammoType"]
                    # Check if ammo already exists in inventory
                    for item in ship_inventory:
                        if item["name"] == ammo_type:
                            item["quantity"] = item.get("quantity", 0) + 10  # Add 10 more
                            break
                    else:
                        ship_inventory.append({"name": ammo_type, "quantity": 10})  # Start with 10
        else:
            break
    
    if not equipped_weapons:
        weapon = weighted_roll(custom["weapons"], "chance")
        equipped_weapons.append({"name": weapon["name"], "damage": weapon["damage"], "ammoType": weapon.get("ammoType")})
        if "ammoType" in weapon and weapon["ammoType"] != "Power":
            ammo_type = weapon["ammoType"]
            for item in ship_inventory:
                if item["name"] == ammo_type:
                    item["quantity"] = item.get("quantity", 0) + 10
                    break
            else:
                ship_inventory.append({"name": ammo_type, "quantity": 10})
    
    ship = {
        "name": f"{align['name']} {ship_class['name']} {random.randint(1, 999)}" if align['name'] != "Player" else f"Player {ship_class['name']}",
        "class": ship_class["name"],
        "alignment": align["name"],
        "hull": hull,
        "max_hull": max_hull,
        "shield": shield,
        "max_shield": max_shield,
        "power": power,
        "max_power": max_power,
        "energy": energy,
        "max_energy": max_energy,
        "storage": storage,
        "max_storage": storage,
        "level": level,
        "initiative_modifier": initiative_modifier,
        "armor_class": armor_class,
        "disengage": disengage,
        "weapons": [],
        "hardPoints": hard_points,
        "defensiveSlots": ship_class.get("defensiveSlots", 1),
        "offensiveSlots": ship_class.get("offensiveSlots", 1),
        "systemSlots": ship_class.get("systemSlots", 1),
        "powerSlots": ship_class.get("powerSlots", 1),
        "equippedWeapons": equipped_weapons,
        "defensiveComponents": [],
        "offensiveComponents": [],
        "systemComponents": [],
        "powerComponents": []
    }
    
    if align["name"] != "Player":
        print_ship_details(ship)
    
    return ship

def print_ship_details(ship):
    TextStyle.print_class("Information", f"\nCreated Ship: {ship['name']}")
    TextStyle.print_class("Information", f"Class: {ship['class']} | Alignment: {ship['alignment']}")
    TextStyle.print_class("Information", f"Hull: {ship['hull']}/{ship['max_hull']} | Shield: {ship['shield']}/{ship['max_shield']} | Energy: {ship['energy']}/{ship['max_energy']}")
    TextStyle.print_class("Information", f"Power: {ship['power']}/{ship['max_power']} | Storage: {ship['storage']} | Level: {ship['level']}")
    TextStyle.print_class("Information", f"Initiative Modifier: +{ship['initiative_modifier']} | Armor Class: {ship['armor_class']} | Disengage: {ship['disengage']}")
    if ship["equippedWeapons"]:
        weapon_str = ", ".join(f"{w['name']} ({w['damage']})" for w in ship["equippedWeapons"])
        TextStyle.print_class("Information", f"Weapons: {weapon_str}")
    TextStyle.print_class("Information", f"Slots: HardPoints: {ship['hardPoints']}, Defensive: {ship['defensiveSlots']}, Offensive: {ship['offensiveSlots']}, System: {ship['systemSlots']}, Power: {ship['powerSlots']}")

if __name__ == "__main__":
    ship_inventory = []
    new_ship = create_ship(ship_inventory=ship_inventory)
    print("Ship Inventory:", ship_inventory)