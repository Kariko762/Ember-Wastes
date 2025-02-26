import json
import os
import random
from text_style import TextStyle

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val, max_val)
    return roll, f"[{die_name}({roll})]"

def load_systems_data():
    json_file = "systems.json"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, json_file)
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        return None

def create_asteroids(system_data, zone_data):
    systems_data = load_systems_data()
    if not systems_data:
        return {"asteroids": [], "messages": []}
    
    system_id = zone_data.get("system_id", "X0000")
    vars = systems_data["systemVariables"]
    asteroid_fields = systems_data["asteroid_fields"]
    security_zone = zone_data.get("security_zone", 1.0)
    messages = []
    belts = []
    
    roll, roll_str = roll_percentile()
    chance_modifier = 0
    belt_min = 0
    belt_max = 0
    belt_die = "d3"
    asteroid_max = 0
    yield_advantage = False
    extra_asteroids_range = {"min": 0, "max": 0}
    for zone, params in systems_data["securityZoneRolls"].items():
        if params["min"] <= security_zone <= params["max"]:
            chance_modifier = params["belt_chance_modifier"]
            belt_min = params["belt_min"]
            belt_max = params["belt_max"]
            belt_die = params["belt_die"]
            asteroid_max = params["asteroid_max"]
            yield_advantage = params["yield_advantage"]
            extra_asteroids_range = {"min": params["extra_asteroids_min"], "max": params["extra_asteroids_max"]}
            break
    adjusted_chance = vars["asteroidChance"] + chance_modifier
    if roll > (100 - adjusted_chance):
        messages.append(f"Scanning for Asteroid Belts {roll_str} ({roll}%): Belts Found (Chance {adjusted_chance}%)")
    else:
        messages.append(f"Scanning for Asteroid Belts {roll_str} ({roll}%): No Belts Found (Chance {adjusted_chance}%)")
        return {"asteroids": belts, "messages": messages}
    
    num_belts, belts_die = roll_dice(belt_min, belt_max, belt_die)
    messages.append(f"Rolling Asteroid Belt Count {belts_die}: {num_belts} Asteroid Belts Detected")
    messages.append("= = =")
    
    yield_types = asteroid_fields["types"]
    type_names = [t["name"] for t in yield_types]
    type_chances = [t["chance"] for t in yield_types]
    asteroid_names = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliett", "Zulu", "Tango"]
    yield_codes = {"Barren": "BA", "Sparse": "SP", "Moderate": "MO", "Rich": "RI"}
    for i in range(num_belts):
        unique_id = f"AB{random.randint(1000, 9999)}"
        
        roll1, roll_str1 = roll_percentile()
        if yield_advantage:
            roll2, roll_str2 = roll_percentile()
            roll = max(roll1, roll2)
            roll_str = f"[Max({roll_str1}, {roll_str2})]"
        else:
            roll = roll1
            roll_str = roll_str1
        cumulative = 0
        for t in yield_types:
            cumulative += t["chance"] * 100
            if roll <= cumulative:
                yield_type = t["name"]
                break
        belt_name = f"{unique_id}[{yield_codes[yield_type]}]"
        messages.append(f"Scanning Asteroid Belt {belt_name}  {roll_str} ({roll}%): Identified as {yield_type} Belt")
        
        # Moved num_asteroids roll inside the loop
        for t in yield_types:
            if t["name"] == yield_type:
                min_val = min(t["min_objects"], asteroid_max)
                max_val = min(t["max_objects"], asteroid_max)
                num_asteroids, asteroids_die = roll_dice(min_val, max_val, "d3")
                break
        messages.append(f"- Surveying Belt Yield {asteroids_die}: {num_asteroids} Viable Asteroids Found")
        
        extra_asteroids = 0
        if security_zone < 0.3:
            extra_asteroids, extra_die = roll_dice(extra_asteroids_range["min"], extra_asteroids_range["max"], "d3")
            if extra_asteroids > 0:
                messages.append(f"- - Security Zone Extra Roll {extra_die}: {extra_asteroids} Additional Asteroids Found")
        
        belt = {
            "name": belt_name,
            "type": "Asteroid Belt",
            "yield": yield_type,
            "children": []
        }
        total_asteroids = num_asteroids + extra_asteroids
        for j in range(total_asteroids):
            asteroid_name = f"Asteroid-{belt_name}-{asteroid_names[j % len(asteroid_names)]}"
            belt["children"].append({
                "name": asteroid_name,
                "type": "Asteroid",
                "resources": []
            })
            messages.append(f"- - {asteroid_name} Located")
        belts.append(belt)
        messages.append("= = =")
    
    return {"asteroids": belts, "messages": messages}

if __name__ == "__main__":
    system_data = {}
    zone_data = {"security_zone": 0.1, "system_id": "X7781"}
    result = create_asteroids(system_data, zone_data)
    for msg in result["messages"]:
        print(msg)
    print(result["asteroids"])