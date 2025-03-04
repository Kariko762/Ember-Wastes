# game_logic.py
import save_game
import ships.shipsNewShip as ships
import combat.combat_main as combat
import combat.combat_trigger as combat_trigger
import os
import json
import random
import time
from text_style import TextStyle
from utils import load_new_game_variables, load_space_classification, roll_percentile
from menus import display_experimental_menu, display_create_ship_menu, display_combat_menu, display_create_enemy_npc_menu, display_create_player_menu

def new_game(ship_inventory, home_inventory, current_save_file, explored, current_system, player_data):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, "savedata")
    os.makedirs(save_dir, exist_ok=True)
    
    variables = load_new_game_variables()
    if not variables:
        return False
    
    TextStyle.print_class("Information", "\nSelect Difficulty:")
    TextStyle.print_class("Information", "1) Easy")
    TextStyle.print_class("Information", "2) Medium")
    TextStyle.print_class("Information", "3) Hard")
    difficulty_choice = input("Enter your choice (1-3): ").strip()
    
    difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
    if difficulty_choice not in difficulty_map:
        TextStyle.print_class("Warning", "\nInvalid choice! Defaulting to Medium.")
        difficulty = "medium"
    else:
        difficulty = difficulty_map[difficulty_choice]
    
    while True:
        game_name = input(TextStyle.print_class("Information", "\nEnter a name for your new game: ", delay_to_display=0, display_mode="instant", print_output=False)).strip()
        if not game_name:
            TextStyle.print_class("Warning", "Game name cannot be empty!")
            continue
        
        save_file = os.path.join(save_dir, f"{game_name}.json")
        if os.path.exists(save_file):
            TextStyle.print_class("Warning", f"A game with the name '{game_name}' already exists!")
            choice = input("Enter a different name? (y/n): ").lower()
            if choice != 'y':
                return False
        else:
            ship_inventory.clear()
            home_inventory[:] = variables["difficulty_levels"][difficulty]["startingHomeInventory"]
            explored = False
            current_system.clear()
            
            player_data.clear()
            player_data.update(ships.create_ship(alignment="Player"))
            player_data["location"] = "Home"
            player_data["universal_signature"] = 0
            player_data["security_zone"] = 1.0
            
            game_data = {
                "player": player_data,
                "shipInventory": ship_inventory,
                "homeInventory": home_inventory,
                "explored": explored,
                "current_system": current_system,
                "game_started": "2025-03-03",
                "last_updated": "2025-03-03"
            }
            with open(save_file, 'w') as file:
                json.dump(game_data, file, indent=4)
            
            if isinstance(current_save_file, list):
                current_save_file.clear()
                current_save_file.append(save_file)
            elif isinstance(current_save_file, dict):
                current_save_file["path"] = save_file
            else:
                current_save_file = save_file
            
            TextStyle.print_class("Information", f"New game '{game_name}' created successfully on {difficulty.capitalize()} difficulty!")
            return current_save_file

def load_game(ship_inventory, home_inventory, current_save_file, explored, current_system, player_data):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    save_dir = os.path.join(script_dir, "savedata")
    os.makedirs(save_dir, exist_ok=True)
    
    save_files = [f for f in os.listdir(save_dir) if f.endswith('.json')]
    if not save_files:
        TextStyle.print_class("Warning", "\nNo saved games found!")
        input("Press Enter to continue...")
        return False, explored, current_save_file, current_system, ship_inventory, home_inventory, player_data
    
    TextStyle.print_class("Information", "\n=== Available Save Files ===")
    for i, save_file in enumerate(save_files, 1):
        file_path = os.path.join(save_dir, save_file)
        game_data = save_game.load_game_data(file_path)
        if game_data:
            last_updated = game_data.get("last_updated", "Unknown")
            TextStyle.print_class("Information", f"{i}) {save_file[:-5]} (Last Saved: {last_updated})")
    
    choice = input("\nEnter the number of the game to load (or 0 to cancel): ").strip()
    if choice == "0":
        return False, explored, current_save_file, current_system, ship_inventory, home_inventory, player_data
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(save_files):
            current_save_file = os.path.join(save_dir, save_files[index])
            game_data = save_game.load_game_data(current_save_file)
            if game_data:
                ship_inventory[:] = game_data["shipInventory"]
                home_inventory[:] = game_data["homeInventory"]
                explored = game_data.get("explored", False)
                current_system.clear()
                current_system.update(game_data.get("current_system", {}))
                
                player_data.clear()
                player_data.update(game_data["player"])
                
                defaults = {
                    "location": "Home",
                    "energy": 100,
                    "max_energy": 100,
                    "hull": 100,
                    "max_hull": 100,
                    "shield": 50,
                    "max_shield": 50,
                    "power": 100,
                    "max_power": 100,
                    "storage": 50,
                    "max_storage": 50,
                    "level": 1,
                    "universal_signature": 0,
                    "security_zone": 1.0,
                    "initiative_modifier": player_data.get("power", 100) // 10,
                    "armor_class": 10 + (player_data.get("hull", 100) // 10) + (player_data.get("shield", 50) // 10),
                    "disengage": 10,
                    "hardPoints": 1,
                    "defensiveSlots": 1,
                    "offensiveSlots": 1,
                    "systemSlots": 1,
                    "powerSlots": 1,
                    "equippedWeapons": [{"name": "Laser", "damage": "d8", "ammoType": "Power"}],
                    "defensiveComponents": [],
                    "offensiveComponents": [],
                    "systemComponents": [],
                    "powerComponents": []
                }
                for key, value in defaults.items():
                    player_data.setdefault(key, value)
                
                if "weapons" in player_data:
                    if not player_data["equippedWeapons"] and player_data["weapons"]:
                        player_data["equippedWeapons"] = player_data["weapons"]
                    del player_data["weapons"]
                
                TextStyle.print_class("Information", f"\nGame '{save_files[index][:-5]}' loaded successfully!")
                return True, explored, current_save_file, current_system, ship_inventory, home_inventory, player_data
            else:
                TextStyle.print_class("Warning", "\nFailed to load game data!")
                return False, explored, current_save_file, current_system, ship_inventory, home_inventory, player_data
        else:
            TextStyle.print_class("Warning", "\nInvalid selection!")
            return False, explored, current_save_file, current_system, ship_inventory, home_inventory, player_data
    except ValueError:
        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
        return False, explored, current_save_file, current_system, ship_inventory, home_inventory, player_data

def travel_home(explored, player_data, current_system):
    if player_data["location"] == "Home":
        TextStyle.print_class("Warning", "\nYou are already at Home!")
        input("Press Enter to continue...")
        return explored
    if player_data["energy"] >= 20:
        player_data["energy"] -= 20
        player_data["location"] = "Home"
        explored = False
        current_system.clear()
        player_data["universal_signature"] = 0
        TextStyle.print_class("Information", "\nTraveled back to Home. Energy consumed: 20")
        TextStyle.print_class("Information", "Universal Signature reset to 0.")
        input("Press Enter to continue...")
        return explored
    else:
        TextStyle.print_class("Warning", "\nNot enough energy to travel home! Need at least 20 energy.")
        input("Press Enter to continue...")
        return explored

def travel_to_new_system(player_data, explored):
    max_energy = player_data["max_energy"]
    energy_available = player_data["energy"]
    while True:
        TextStyle.print_class("Information", f"\nCurrent Energy: {energy_available}/{max_energy}")
        TextStyle.print_class("Information", "Select Security Zone to travel to:")
        TextStyle.print_class("Information", "1) Secure Space - 10 Energy")
        TextStyle.print_class("Information", "2) Moderately Secure - 20 Energy")
        TextStyle.print_class("Information", "3) Risky - 30 Energy")
        TextStyle.print_class("Information", "4) Unsecure - 40 Energy")
        TextStyle.print_class("Information", "5) Space Classification Details")
        TextStyle.print_class("Information", "0) Cancel")
        
        choice = input("Enter your choice (0-5): ")
        
        if choice == "5":
            details = load_space_classification()
            if details:
                TextStyle.print_class("Information", "\n=== Space Classification Details ===")
                for zone, desc in details["classifications"].items():
                    TextStyle.print_class("Information", f"{zone}:")
                    TextStyle.print_class("Information", f"  {desc}")
                TextStyle.print_class("Information", "==================================")
            input("Press Enter to continue...")
            continue
        
        if choice == "0":
            return explored
        
        try:
            zone_map = {
                "1": {"cost": 10, "zone": 0.9, "name": "Secure Space"},
                "2": {"cost": 20, "zone": 0.6, "name": "Moderately Secure Space"},
                "3": {"cost": 30, "zone": 0.3, "name": "Risky Space"},
                "4": {"cost": 40, "zone": 0.05, "name": "Unsecure Space"}
            }
            
            if choice not in zone_map:
                TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-5.")
                input("Press Enter to continue...")
                continue
            
            energy_cost = zone_map[choice]["cost"]
            security_zone = zone_map[choice]["zone"]
            zone_name = zone_map[choice]["name"]
            
            if energy_cost > energy_available:
                TextStyle.print_class("Warning", f"\nNot enough energy! Need at least {energy_cost} energy.")
                input("Press Enter to continue...")
                continue
            
            if explored and player_data["location"] != "Home":
                TextStyle.print_class("Information", f"\nYou are already in {player_data['location']}. Returning to Home first is required to explore a new system.")
                input("Press Enter to continue...")
                return explored
            
            player_data["energy"] -= energy_cost
            player_data["universal_signature"] = min(player_data["universal_signature"] + energy_cost, 100)
            player_data["security_zone"] = security_zone
            explored = False
            player_data["location"] = "Unknown System"
            TextStyle.print_class("Information", f"\nTraveled to a new system in {zone_name}. Energy consumed: {energy_cost}")
            TextStyle.print_class("Information", f"Universal Signature increased to {player_data['universal_signature']}")
            
            input("Press Enter to continue...")
            return explored
        
        except ValueError:
            TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
            input("Press Enter to continue...")

def experimental_menu(enemy_npc, player_data, ship_inventory=None):
    if enemy_npc is None:
        enemy_npc = {}
    if ship_inventory is None:
        ship_inventory = []
    
    while True:
        display_experimental_menu()
        choice = input("\nEnter your choice (0-3): ").strip()
        
        if choice == "0":
            TextStyle.print_class("Information", "\nReturning to main menu...")
            return
        
        try:
            choice_int = int(choice)
            if choice_int < 0 or choice_int > 3:
                TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-3.")
                input("Press Enter to continue...")
                continue
            
            if choice_int == 1:
                while True:
                    display_create_ship_menu()
                    sub_choice = input("\nEnter your choice (0-3): ").strip()
                    if sub_choice == "0":
                        break
                    try:
                        sub_choice_int = int(sub_choice)
                        if sub_choice_int < 0 or sub_choice_int > 3:
                            TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-3.")
                            input("Press Enter to continue...")
                        elif sub_choice_int == 1:
                            enemy_npc.clear()
                            enemy_npc.update(ships.create_ship(alignment="Bad", ship_inventory=ship_inventory))
                        elif sub_choice_int == 2:
                            ships.create_ship(alignment="Good", ship_inventory=ship_inventory)
                        elif sub_choice_int == 3:
                            TextStyle.print_class("Information", "\nCreating Trader NPC... (Feature under development)")
                        input("Press Enter to continue...")
                    except ValueError:
                        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
                        input("Press Enter to continue...")
            elif choice_int == 2:
                TextStyle.print_class("Information", "\nGenerating Mission... (Feature under development)")
                input("Press Enter to continue...")
            elif choice_int == 3:
                while True:
                    display_combat_menu()
                    sub_choice = input("\nEnter your choice (0-3): ").strip()
                    if sub_choice == "0":
                        break
                    try:
                        sub_choice_int = int(sub_choice)
                        if sub_choice_int < 0 or sub_choice_int > 3:
                            TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-3.")
                            input("Press Enter to continue...")
                            continue
                        
                        ship_classes = ships.load_ship_data()["shipCustomization"]["classes"]
                        class_names = [cls["name"] for cls in ship_classes]
                        
                        if sub_choice_int == 1:  # Create Enemy NPC
                            display_create_enemy_npc_menu()
                            npc_choice = input("\nSelect a ship class (0-4): ").strip()
                            try:
                                npc_idx = int(npc_choice)
                                if npc_idx == 0:
                                    continue
                                if 1 <= npc_idx <= len(class_names):
                                    enemy_npc.clear()
                                    enemy_npc.update(ships.create_ship(alignment="Bad", ship_type=class_names[npc_idx - 1], ship_inventory=ship_inventory))
                                    TextStyle.print_class("Success_Mode_Line", f"Created {enemy_npc['name']}!")
                            except ValueError:
                                TextStyle.print_class("Warning", "Invalid input! Please enter a number.")
                        
                        elif sub_choice_int == 2:  # Create Player
                            display_create_player_menu()
                            player_choice = input("\nSelect a ship class (0-4): ").strip()
                            try:
                                player_idx = int(player_choice)
                                if player_idx == 0:
                                    continue
                                if 1 <= player_idx <= len(class_names):
                                    player_data.clear()
                                    player_data.update(ships.create_ship(alignment="Player", ship_type=class_names[player_idx - 1], ship_inventory=ship_inventory))
                                    ships.print_ship_details(player_data)
                                    TextStyle.print_class("Success_Mode_Line", f"Created {player_data['name']}!")
                            except ValueError:
                                TextStyle.print_class("Warning", "Invalid input! Please enter a number.")
                        
                        elif sub_choice_int == 3:  # Initiate Combat
                            if not enemy_npc:
                                TextStyle.print_class("Warning", "\nNo Enemy Created! Please create an Enemy NPC first.")
                            elif not all(key in player_data for key in ["initiative_modifier", "hull", "max_hull", "equippedWeapons", "energy"]):
                                TextStyle.print_class("Warning", "\nNo Player Created! Please create a Test Player first.")
                            else:
                                combat.initiate_combat(player_data, enemy_npc, ship_inventory)
                                TextStyle.print_class("Information", "\nCombat concluded. Player and Enemy entities destroyed.")
                                player_data.clear()
                                enemy_npc.clear()
                                ship_inventory.clear()
                        
                        input("Press Enter to continue...")
                    except ValueError:
                        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
                        input("Press Enter to continue...")
        except ValueError:
            TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
            input("Press Enter to continue...")