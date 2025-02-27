# ships/shipsNewShip.py
import json
import random
import os
from text_style import TextStyle

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

def create_ship(alignment=None):
    ship_data = load_ship_data()
    if not ship_data:
        return None
    
    vars = ship_data["shipVariables"]
    custom = ship_data["shipCustomization"]
    
    # Base stats
    hull = random.randint(vars["hullRange"]["min"], vars["hullRange"]["max"])
    shield = random.randint(vars["shieldRange"]["min"], vars["shieldRange"]["max"])
    power = random.randint(vars["powerRange"]["min"], vars["powerRange"]["max"])
    energy = random.randint(vars["energyRange"]["min"], vars["energyRange"]["max"])
    storage = random.randint(vars["storageRange"]["min"], vars["storageRange"]["max"])
    level = random.randint(vars["levelRange"]["min"], vars["levelRange"]["max"])
    
    # Customization
    ship_class = weighted_roll(custom["classes"], "chance")
    weapon = weighted_roll(custom["weapons"], "chance")
    if alignment:
        align = next((a for a in custom["alignments"] if a["name"] == alignment), None)
        if not align:
            TextStyle.print_class("Warning", f"\nInvalid alignment '{alignment}' specified! Using random alignment.")
            align = weighted_roll([a for a in custom["alignments"] if a["chance"] > 0], "chance")
    else:
        align = weighted_roll([a for a in custom["alignments"] if a["chance"] > 0], "chance")
    
    # Apply class bonuses
    hull += ship_class["hullBonus"]
    shield += ship_class["shieldBonus"]
    power += ship_class["powerBonus"]
    energy += ship_class["energyBonus"]
    storage += ship_class["storageBonus"]
    
    # Calculate derived stats
    max_hull = hull
    max_shield = shield
    max_energy = energy
    max_power = power  # Add max_power for consistency
    initiative_modifier = power // 10
    armor_class = random.randint(ship_class["armorClassRange"]["min"], ship_class["armorClassRange"]["max"])
    disengage = random.randint(ship_class["disengageRange"]["min"], ship_class["disengageRange"]["max"])
    
    # Construct ship entity with new slots
    ship = {
        "name": f"{align['name']} {ship_class['name']} {random.randint(1, 999)}" if align["name"] != "Player" else f"Player {ship_class['name']}",
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
        "weapons": [{"name": weapon["name"], "damage": weapon["damage"]}],
        "hardPoints": ship_class.get("hardPoints", 1),           # New: Weapon slots
        "defensiveSlots": ship_class.get("defensiveSlots", 1),   # New: Defensive slots
        "offensiveSlots": ship_class.get("offensiveSlots", 1),   # New: Offensive slots
        "systemSlots": ship_class.get("systemSlots", 1),         # New: System slots
        "powerSlots": ship_class.get("powerSlots", 1),           # New: Power slots
        "equippedWeapons": [],                                   # New: List for equipped weapons
        "defensiveComponents": [],                               # New: List for defensive components
        "offensiveComponents": [],                               # New: List for offensive components
        "systemComponents": [],                                  # New: List for system components
        "powerComponents": []                                    # New: List for power components
    }
    
    # Display creation (optional, suppressed for player in main game)
    if align["name"] != "Player":
        TextStyle.print_class("Information", f"\nCreated NPC Ship: {ship['name']}")
        TextStyle.print_class("Information", f"Class: {ship['class']} | Alignment: {ship['alignment']}")
        TextStyle.print_class("Information", f"Hull: {ship['hull']}/{ship['max_hull']} | Shield: {ship['shield']}/{ship['max_shield']} | Energy: {ship['energy']}/{ship['max_energy']}")
        TextStyle.print_class("Information", f"Power: {ship['power']}/{ship['max_power']} | Storage: {ship['storage']} | Level: {ship['level']}")
        TextStyle.print_class("Information", f"Initiative Modifier: +{ship['initiative_modifier']} | Armor Class: {ship['armor_class']} | Disengage: {ship['disengage']}")
        TextStyle.print_class("Information", f"Weapon: {ship['weapons'][0]['name']} ({ship['weapons'][0]['damage']})")
        TextStyle.print_class("Information", f"Slots: HardPoints: {ship['hardPoints']}, Defensive: {ship['defensiveSlots']}, Offensive: {ship['offensiveSlots']}, System: {ship['systemSlots']}, Power: {ship['powerSlots']}")
    
    return ship

if __name__ == "__main__":
    new_ship = create_ship()