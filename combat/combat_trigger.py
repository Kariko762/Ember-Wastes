# scavenge/combat_trigger.py
import json
import random
import os
from text_style import TextStyle
import combat.combat_main as combat_main
import ships.shipsNewShip as ships

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def load_combat_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "combat.json")
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except:
        return {
            "combatChanceMultiplier": 1.0,
            "securityZones": {
                "Secure Space": {"min": 0.9, "max": 1.0, "baseChance": 10},
                "Moderately Secure Space": {"min": 0.6, "max": 0.89, "baseChance": 20},
                "Risky Space": {"min": 0.3, "max": 0.59, "baseChance": 30},
                "Unsecure Space": {"min": 0.0, "max": 0.29, "baseChance": 40}
            },
            "npcs": [
                {"type": "Pirate", "chance": 0.5, "taunts": ["Prepare to be boarded, weakling!", "Your cargo is mine!"], "alignment": "Bad", "stats": {"hull": 50, "shield": 20, "energy": 50, "weapons": [{"name": "Laser", "damage": "d6"}]}},
                {"type": "Raider", "chance": 0.3, "taunts": ["No escape for you!", "Surrender or be dust!"], "alignment": "Bad", "stats": {"hull": 40, "shield": 25, "energy": 40, "weapons": [{"name": "Blaster", "damage": "d8"}]}},
                {"type": "Mercenary", "chance": 0.2, "taunts": ["You’re worth more dead!", "This is just business!"], "alignment": "Bad", "stats": {"hull": 60, "shield": 30, "energy": 60, "weapons": [{"name": "Cannon", "damage": "d10"}]}}
            ]
        }

def combatCheck(player_data, current_system, return_point):
    config = load_combat_config()
    security_zone = player_data.get("security_zone", 1.0)
    universal_signature = player_data.get("universal_signature", 0)
    
    # Determine base chance from security zone
    base_chance = 0
    for zone, data in config["securityZones"].items():
        if data["min"] <= security_zone <= data["max"]:
            base_chance = data["baseChance"]
            break
    
    # Calculate combat chance
    combat_chance = int((1 - security_zone) * universal_signature * config["combatChanceMultiplier"]) + base_chance
    roll, roll_str = roll_percentile()
    
    #TextStyle.print_class("Information", f"Combat Check {roll_str} ({roll}%): Chance {combat_chance}%")
    if roll <= combat_chance:
        # Select NPC
        npcs = config["npcs"]
        total_chance = sum(npc["chance"] for npc in npcs)
        roll = random.uniform(0, total_chance)
        cumulative = 0
        for npc in npcs:
            cumulative += npc["chance"]
            if roll <= cumulative:
                selected_npc = npc
                break
        
        # Create NPC ship
        enemy_ship = ships.create_ship(alignment=selected_npc["alignment"])
        enemy_ship.update(selected_npc["stats"])
        enemy_ship["name"] = f"{selected_npc['type']} {random.randint(100, 999)}"
        
        # Display taunt
        taunt = random.choice(selected_npc["taunts"])
        TextStyle.print_class("Warning", f"\nHostile {selected_npc['type']} detected: '{taunt}'")
        input("Press Enter to engage in combat...")
        
        # Trigger combat
        combat_result = combat_main.initiate_combat(player_data, enemy_ship)
        TextStyle.print_class("Information", f"Combat resolved. Returning to {return_point}.")
        return True  # Combat occurred
    else:
        #TextStyle.print_class("Information", "No hostile encounter detected.")
        return False  # No combat

if __name__ == "__main__":
    # Test
    player_data = {"security_zone": 0.3, "universal_signature": 50}
    current_system = {}
    result = combatCheck(player_data, current_system, "main_game_loop")
    print(f"Combat triggered: {result}")