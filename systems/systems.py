import json
import random
import os
import time
from text_style import TextStyle
import systems.systemsCreateAsteroids

def load_system_data():
    json_file = "systems.json"
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
        TextStyle.print_class("Warning", f"\nError: Invalid JSON format in systems.json!")
        input("Press Enter to continue...")
        return None
    except Exception as e:
        TextStyle.print_class("Warning", f"\nAn error occurred: {str(e)}")
        input("Press Enter to continue...")
        return None

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def roll_dice(min_val, max_val, die_name):
    roll = random.randint(min_val + 1, max_val + 1)
    result = roll - 1
    return result, f"[{die_name}({roll}) - 1]"

def create_system():
    system_data = load_system_data()
    if not system_data:
        return None
    
    system_id = f"SYS{random.randint(1000, 9999)}"
    current_system = {
        "star": None,
        "system_id": system_id,
        "children": []
    }
    
    stars = system_data["celestial_objects"]["stars"]
    star_names = [s["name"] for s in stars]
    star_chances = [s["chance"] for s in stars]
    roll, roll_str = roll_percentile()
    star = random.choices(star_names, weights=star_chances, k=1)[0]
    current_system["star"] = star
    TextStyle.print_class("Information", f"Scanning for Star Type {roll_str} ({roll}%): {star} detected")
    time.sleep(0.2)  # Matches "Information" delay
    
    return current_system

def create_planets(system_data, star_data):
    planets_info = system_data["celestial_objects"]["planets"]
    moons_info = system_data["celestial_objects"]["moons"]
    man_made_info = system_data["man_made_objects"]
    vars = system_data["systemVariables"]
    
    planets = []
    num_planets, planet_die = roll_dice(vars["planetCount"]["min"], vars["planetCount"]["max"], "d5")
    color = "Success_Mode_Line" if num_planets > 0 else "Warning_Mode_Line"
    TextStyle.print_class(color, f"Searching for Planets {planet_die}: {num_planets} Detected")
    time.sleep(0.2)
    TextStyle.print_class("Information", "= = =")
    time.sleep(0.2)
    
    planet_names = [p["name"] for p in planets_info]
    planet_chances = [p["chance"] for p in planets_info]
    moon_names = [m["name"] for m in moons_info]
    moon_chances = [m["chance"] for m in moons_info]
    man_made_types = {m["name"]: m["chance"] for m in man_made_info}
    
    for i in range(num_planets):
        roll, roll_str = roll_percentile()
        planet = random.choices(planet_names, weights=planet_chances, k=1)[0]
        type_code = ''.join(word[0].upper() for word in planet.split())
        unique_id = f"P-{type_code}{random.randint(1000, 9999)}"
        planet_obj = {"type": "Planet", "name": f"{planet} {unique_id}", "children": []}
        TextStyle.print_class("Information", f"Scanning Planet {roll_str} ({roll}%): {planet_obj['name']} Identified")
        time.sleep(0.2)
        TextStyle.print_class("Information", f"- Surveying {planet_obj['name']}:")
        time.sleep(0.2)
        
        moon_roll, moon_roll_str = roll_percentile()
        if moon_roll <= vars["moonChance"] * 100:
            num_moons, moon_die = roll_dice(vars["moonCount"]["min"], vars["moonCount"]["max"], "d5")
            TextStyle.print_class("Success_Mode_Line", f"- - Searching for Moons {moon_roll_str} ({moon_roll}%): {num_moons} Detected")
            time.sleep(0.2)
            for j in range(num_moons):
                moon = random.choices(moon_names, weights=moon_chances, k=1)[0]
                moon_code = ''.join(word[0].upper() for word in moon.split())
                moon_obj = {"type": "Moon", "name": f"{moon} {unique_id}[MN-{j+1}-{moon_code}]"}
                planet_obj["children"].append(moon_obj)
                TextStyle.print_class("Information", f"- - - {moon_obj['name']} Located")
                time.sleep(0.2)
        else:
            TextStyle.print_class("Scavenged", f"- - Searching for Moons {moon_roll_str} ({moon_roll}%): No Moons Detected")
            time.sleep(0.2)
        
        TextStyle.print_class("Information", "- - Surveying for Signs of Life:")
        time.sleep(0.2)
        for man_made_name, chance in man_made_types.items():
            roll, roll_str = roll_percentile()
            if roll <= chance * 100:
                mm_code = {'Space Station': 'SS', 'Moon Outpost': 'MO', 'Orbital Platform': 'OP', 
                           'Abandoned Settlement': 'AS', 'Mining Station': 'MS', 'Research Post': 'RP'}[man_made_name]
                man_made_obj = {"type": "Man-Made", "name": f"{man_made_name} {unique_id}[{mm_code}]"}
                planet_obj["children"].append(man_made_obj)
                TextStyle.print_class("Success_Mode_Line", f"- - - Searching of {man_made_name}s {roll_str} ({roll}%): {man_made_obj['name']} Detected")
            else:
                TextStyle.print_class("Scavenged", f"- - - Searching of {man_made_name}s {roll_str} ({roll}%): No {man_made_name}s Detected")
            time.sleep(0.2)
        
        planets.append(planet_obj)
        TextStyle.print_class("Information", "= = =")
        time.sleep(0.2)
    
    return planets

def explore_system(player_data, current_system, explored):
    if explored:
        TextStyle.print_class("Warning_Mode_Line", "\nThis system has already been explored! Travel home to reset.")
        input("Press Enter to continue...")
        return player_data, current_system, explored
    
    system_data = load_system_data()
    if not system_data:
        return player_data, current_system, explored
    
    current_system = create_system()
    if not current_system:
        return player_data, current_system, explored
    
    planets = create_planets(system_data, current_system)
    current_system["children"].extend(planets)
    
    security_zone = 0.5  # Hardcoded for now
    zone_data = {"security_zone": security_zone, "system_id": current_system["system_id"]}
    asteroid_data = systems.systemsCreateAsteroids.create_asteroids(system_data, zone_data)
    asteroids = asteroid_data["asteroids"]
    asteroid_messages = asteroid_data["messages"]
    current_system["children"].extend(asteroids)
    
    unknown = system_data["unknown_objects"]
    unknown_types = {u["name"]: u["chance"] for u in unknown}
    for unknown_name, chance in unknown_types.items():
        roll, roll_str = roll_percentile()
        color = "Success_Mode_Line" if roll <= chance * 100 else "Scavenged"
        if roll <= chance * 100:
            event_obj = {"type": "Unknown", "name": f"{unknown_name} {random.randint(system_data['systemVariables']['objectIdRange']['min'], system_data['systemVariables']['objectIdRange']['max'])}"}
            for u in unknown:
                if u["name"] == unknown_name and "wreckage" in u:
                    event_obj["wreckage"] = u["wreckage"]
            current_system["children"].append(event_obj)
            TextStyle.print_class(color, f"Scanning for Anomalies ({unknown_name}s) {roll_str} ({roll}%): {event_obj['name']} Detected")
        else:
            TextStyle.print_class(color, f"Scanning for Anomalies ({unknown_name}s) {roll_str} ({roll}%): No {unknown_name}s Found")
        time.sleep(0.2)
    
    TextStyle.print_class("Information", "= = =")
    time.sleep(0.2)
    for msg in asteroid_messages:
        if "No Belts Found" in msg:
            TextStyle.print_class("Warning_Mode_Line", msg)
        elif "Belts Found" in msg:
            TextStyle.print_class("Success_Mode_Line", msg)
        else:
            TextStyle.print_class("Information", msg)
        time.sleep(0.2)
    
    explored = True
    player_data["location"] = f"{current_system['star']} System"
    TextStyle.print_class("Success", f"\nExplored new system: {current_system['star']} System (ID: {current_system['system_id']})")
    print_system(current_system)
    input("Press Enter to continue...")
    
    return player_data, current_system, explored

def print_system(current_system):
    TextStyle.print_class("Information", f"- {current_system['star']} (ID: {current_system['system_id']})")
    
    for obj in current_system["children"]:
        if obj["type"] == "Asteroid Belt":
            display_name = f"Asteroid Belt {obj['name']}"
        else:
            display_name = obj['name']
        TextStyle.print_class("Information", f"- - {display_name} ({obj['type']})")
        if "children" in obj:
            for child in obj["children"]:
                if "wreckage" in child:
                    TextStyle.print_class("Information", f"- - - {child['name']} ({child['type']}, {child['wreckage']} wrecks)")
                else:
                    TextStyle.print_class("Information", f"- - - {child['name']} ({child['type']})")

def show_system(current_system, explored):
    if not current_system or not explored:
        TextStyle.print_class("Warning", "\nNo system explored yet! Use 'Explore System' first.")
    else:
        TextStyle.print_class("Success", f"\nCurrent System: {current_system['star']} System (ID: {current_system['system_id']})")
        print_system(current_system)
    input("Press Enter to continue...")

if __name__ == "__main__":
    test_player = {"location": "Home", "energy": 100}
    test_system = {}
    test_explored = False
    test_player, test_system, test_explored = explore_system(test_player, test_system, test_explored)
    show_system(test_system, test_explored)