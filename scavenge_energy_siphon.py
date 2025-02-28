# scavenge/scavenge_energy_siphon.py
import json
import random
import os
from text_style import TextStyle

def roll_percentile():
    tens = random.randint(0, 9)
    ones = random.randint(1, 9)
    roll = tens * 10 + ones
    return roll, f"[d10({tens}) + {ones}]"

def roll_2d20():
    roll1 = random.randint(1, 20)
    roll2 = random.randint(1, 20)
    return roll1 + roll2, f"[d20({roll1}) + d20({roll2})]"

def load_energy_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "scavenge_energy.json")
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except:
        return {
            "siphoning": {
                "Man-Made": {
                    "minEnergy": 5,
                    "scanCost": 2,
                    "successChance": 70,
                    "dockCost": 2,
                    "dockChance": 70,
                    "dockPenalty": 0.8,
                    "dockFailEnergyLoss": 2,
                    "dockFailHullLoss": 2,
                    "siphonCost": 1,
                    "energyYield": {
                        "Secure Space": 0.5,
                        "Moderately Secure Space": 0.6,
                        "Risky Space": 0.7,
                        "Unsecure Space": 0.8
                    }
                }
            },
            "wreckSalvage": {
                "Unknown": {
                    "minEnergy": 5,
                    "successChance": 50,
                    "dockCost": 2,
                    "dockChance": 60,
                    "dockPenalty": 0.8,
                    "dockFailEnergyLoss": 2,
                    "dockFailHullLoss": 2,
                    "siphonCost": 1,
                    "energyYield": {
                        "Secure Space": 0.4,
                        "Moderately Secure Space": 0.5,
                        "Risky Space": 0.6,
                        "Unsecure Space": 0.7
                    }
                }
            }
        }

def zone_key(security_zone):
    if security_zone >= 0.9:
        return "Secure Space"
    elif security_zone >= 0.6:
        return "Moderately Secure Space"
    elif security_zone >= 0.3:
        return "Risky Space"
    else:
        return "Unsecure Space"

def scavenge_energy(obj, player_data, ship_inventory):
    config = load_energy_config()
    security_zone = player_data.get("security_zone", 1.0)
    
    if obj["type"] == "Man-Made":
        manmade_config = config["siphoning"]["Man-Made"]
        if player_data["energy"] >= manmade_config["minEnergy"]:
            TextStyle.print_class("Information", f"\nWould you like to attempt to extract residual energy from the facility?")
            TextStyle.print_class("Warning", f"[Damage Risk]: Docking failure can cause hull damage! (Cost: Energy {manmade_config['minEnergy']})")
            TextStyle.print_class("Information", "1) Accept Risk - Attempt to Dock.")
            TextStyle.print_class("Information", "2) Do not attempt Energy Siphoning.")
            try:
                choice = int(input("Enter your choice (1, 2): "))
                if choice == 1:
                    # Step 1: Scanning for Residual Energy
                    scan_cost = manmade_config["scanCost"]
                    if player_data["energy"] < scan_cost:
                        TextStyle.print_class("Warning", "Not enough energy to scan for residual energy!")
                        return
                    player_data["energy"] -= scan_cost
                    scan_roll, scan_str = roll_percentile()
                    siphon_chance = manmade_config["successChance"]
                    if scan_roll > siphon_chance:
                        TextStyle.print_class("Success", f"Scanning for Residual Energy (-{scan_cost} Energy) {scan_str} ({scan_roll}%): Successfully identified residual energy.")
                        
                        # Step 2: Docking
                        dock_cost = manmade_config["dockCost"]
                        if player_data["energy"] < dock_cost:
                            TextStyle.print_class("Warning", "Not enough energy to attempt docking!")
                            return
                        player_data["energy"] -= dock_cost
                        dock_roll, dock_str = roll_percentile()
                        dock_chance = manmade_config["dockChance"]
                        if dock_roll > dock_chance:
                            dock_penalty = 1.0
                            TextStyle.print_class("Success", f"- Attempting to dock with facility (-{dock_cost} Energy) {dock_str} ({dock_roll}%): Stable Dock established.")
                        else:
                            dock_penalty = manmade_config["dockPenalty"]
                            player_data["energy"] -= manmade_config["dockFailEnergyLoss"]
                            player_data["hull"] -= manmade_config["dockFailHullLoss"]
                            TextStyle.print_class("Warning", f"- Attempting to dock with facility (-{dock_cost} Energy) {dock_str} ({dock_roll}%): Unstable Dock established. (-{manmade_config['dockFailEnergyLoss']} Energy / -{manmade_config['dockFailHullLoss']} Hull / Energy Waste * {dock_penalty})")
                        
                        # Step 3: Siphoning
                        siphon_cost = manmade_config["siphonCost"]
                        if player_data["energy"] < siphon_cost:
                            TextStyle.print_class("Warning", "Not enough energy to siphon residual energy!")
                            return
                        player_data["energy"] -= siphon_cost
                        siphon_roll, siphon_str = roll_2d20()
                        siphon_yield = int(siphon_roll * dock_penalty)
                        TextStyle.print_class("Success", f"- Siphoning Energy from Facility (-{siphon_cost} Energy) {siphon_str} ({siphon_roll} * {dock_penalty} = {siphon_yield}): {siphon_yield} Energy Siphoned")
                        player_data["energy"] += siphon_yield
                    else:
                        TextStyle.print_class("Information", f"Scanning for Residual Energy (-{scan_cost} Energy) {scan_str} ({scan_roll}%): No residual energy found.")
                elif choice == 2:
                    TextStyle.print_class("Information", "Energy siphon attempt skipped.")
                else:
                    TextStyle.print_class("Warning", "Invalid choice! Please enter 1 or 2.")
            except ValueError:
                TextStyle.print_class("Warning", "Invalid input! Please enter a number (1 or 2).")
    
    elif obj["type"] == "Unknown" and "wreckage" in obj:
        wreck_config = config["wreckSalvage"]["Unknown"]
        if player_data["energy"] >= wreck_config["minEnergy"]:
            wreck_roll, wreck_str = roll_percentile()
            wreck_chance = wreck_config["successChance"]
            if wreck_roll > wreck_chance:
                TextStyle.print_class("Success", f"\nScanning for Universal Signatures {wreck_str} ({wreck_roll}%): Colonial Frigate Wreckage located")
                TextStyle.print_class("Information", f"Would you like to attempt to salvage from the wreckage (y/n) (Energy {wreck_config['minEnergy']})? ")
                choice = input().lower().strip() == "y"
                if choice:
                    # Step 1: Docking
                    dock_cost = wreck_config["dockCost"]
                    if player_data["energy"] < dock_cost:
                        TextStyle.print_class("Warning", "Not enough energy to attempt docking!")
                        return
                    player_data["energy"] -= dock_cost
                    dock_roll, dock_str = roll_percentile()
                    dock_chance = wreck_config["dockChance"]
                    if dock_roll > dock_chance:
                        dock_penalty = 1.0
                        TextStyle.print_class("Success", f"- Attempting to dock with the wreckage (-{dock_cost} Energy) {dock_str} ({dock_roll}%): Stable Dock established.")
                    else:
                        dock_penalty = wreck_config["dockPenalty"]
                        player_data["energy"] -= wreck_config["dockFailEnergyLoss"]
                        player_data["hull"] -= wreck_config["dockFailHullLoss"]
                        TextStyle.print_class("Warning", f"- Attempting to dock with the wreckage (-{dock_cost} Energy) {dock_str} ({dock_roll}%): Unstable Dock established. (-{wreck_config['dockFailEnergyLoss']} Energy / -{wreck_config['dockFailHullLoss']} Hull / Docking-Penalty {dock_penalty})")
                    
                    # Step 2: Siphoning Energy
                    siphon_cost = wreck_config["siphonCost"]
                    if player_data["energy"] < siphon_cost:
                        TextStyle.print_class("Warning", "Not enough energy to siphon residual energy!")
                        return
                    player_data["energy"] -= siphon_cost
                    siphon_roll, siphon_str = roll_2d20()
                    siphon_yield = int(siphon_roll * wreck_config["energyYield"][zone_key(security_zone)] * dock_penalty)
                    TextStyle.print_class("Success", f"- Siphoning Energy from Wreckage (-{siphon_cost} Energy) {siphon_str} ({siphon_roll} * {dock_penalty} = {siphon_yield}): {siphon_yield} Energy Siphoned")
                    player_data["energy"] += siphon_yield
                else:
                    TextStyle.print_class("Information", "Salvage attempt skipped.")
            else:
                TextStyle.print_class("Information", f"\nScanning for Universal Signatures {wreck_str} ({wreck_roll}%): No viable wreckage located")