# core.py
import save_game
import systems.systems as systems_module
import fabrication.fabrication
import ships.shipsNewShip as ships
import combat.combat_main as combat
import combat.combat_trigger as combat_trigger
import os
import json
import random
import time
import sys
from text_style import TextStyle
#from utils import load_new_game_variables, load_space_classification, roll_percentile, load_general_data
from game_logic import new_game, load_game, travel_home, travel_to_new_system, experimental_menu
from menus import display_initial_menu, display_game_menu, display_home_menu
from inventory import show_inventory, show_ship_inventory, transfer_items
from drydock import repair_ship, fit_components, display_drydock_menu
from scavenge import scavenge_location
from fabrication.fabrication import fabrication_menu
from vaults import vault_menu

# Initialize global state
ship_inventory = []
home_inventory = []
current_save_file = None
explored = False
current_system = {}
player_data = {"location": "Home", "energy": 100, "universal_signature": 0}
enemy_npc = None

def main_game_loop():
    global ship_inventory, home_inventory, current_save_file, explored, current_system, player_data, enemy_npc
    while True:
        if player_data["location"] == "Home":
            display_home_menu(player_data)
            choice = input("\nEnter your choice (1-5, 9, 0): ")
            
            if choice == "1":
                explored = travel_to_new_system(player_data, explored)
            elif choice == "2":
                show_inventory(ship_inventory, home_inventory)
            elif choice == "3":
                transfer_items(ship_inventory, home_inventory)
            elif choice == "4":
                while True:
                    display_drydock_menu(player_data)
                    sub_choice = input("\nEnter your choice (0-2): ")
                    if sub_choice == "0":
                        break
                    elif sub_choice == "1":
                        repair_ship(player_data, ship_inventory, home_inventory)
                    elif sub_choice == "2":
                        fit_components(player_data, ship_inventory)
                    else:
                        TextStyle.print_class("Warning", "\nInvalid choice! Please select 0-2.")
                        input("Press Enter to continue...")
            elif choice == "5":
                fabrication_menu(player_data, ship_inventory, home_inventory)
            elif choice == "6":
                vault_menu(player_data, ship_inventory, home_inventory)
            elif choice == "9":
                if current_save_file:
                    save_game.save_game(ship_inventory, home_inventory, current_save_file, explored, current_system, player_data)
                else:
                    TextStyle.print_class("Warning", "\nNo game file selected to save to!")
                    input("Press Enter to continue...")
            elif choice == "0":
                TextStyle.print_class("Information", "\nReturning to main menu...")
                return
            else:
                TextStyle.print_class("Warning", "\nInvalid choice! Please select 1-5, 9, or 0.")
                input("Press Enter to continue...")
        
        else:
            combat_trigger.combatCheck(player_data,current_system,"main_game_loop")
            display_game_menu(player_data, explored)
            choice = input("\nEnter your choice (1, 2, 3, 4, 5, 8, 9, 0): ")
            
            if choice == "1":
                player_data, current_system, explored = systems_module.explore_system(player_data, current_system, explored)
            elif choice == "2":
                systems_module.show_system(current_system, explored)
            elif choice == "3":
                show_ship_inventory(ship_inventory)
            elif choice == "4":
                scavenge_location(current_system, player_data, ship_inventory)
            elif choice == "5":
                fabrication_menu(player_data, ship_inventory, home_inventory)
            elif choice == "8":
                explored = travel_home(explored, player_data, current_system)
            elif choice == "9":
                if current_save_file:
                    save_game.save_game(ship_inventory, home_inventory, current_save_file, explored, current_system, player_data)
                else:
                    TextStyle.print_class("Warning", "\nNo game file selected to save to!")
                    input("Press Enter to continue...")
            elif choice == "0":
                TextStyle.print_class("Information", "\nReturning to main menu...")
                return
            else:
                TextStyle.print_class("Warning", "\nInvalid choice! Please select 1, 2, 3, 4, 5, 8, 9, or 0.")
                input("Press Enter to continue...")

def main():
    global current_save_file, ship_inventory, home_inventory, explored, current_system, player_data, enemy_npc
    while True:
        display_initial_menu()
        choice = input("\nEnter your choice (1-3, 9): ")
        
        if choice == "1":
            current_save_file = new_game(ship_inventory, home_inventory, current_save_file, explored, current_system, player_data)
            if current_save_file:
                main_game_loop()
        elif choice == "2":
            success, loaded_explored, loaded_save_file, loaded_system, loaded_ship_inv, loaded_home_inv, loaded_player = load_game(
                ship_inventory, home_inventory, current_save_file, explored, current_system, player_data
            )
            if success:
                explored = loaded_explored
                current_save_file = loaded_save_file
                current_system = loaded_system
                ship_inventory = loaded_ship_inv
                home_inventory = loaded_home_inv
                player_data = loaded_player
                main_game_loop()
        elif choice == "3":
            experimental_menu(enemy_npc, player_data, ship_inventory)
        elif choice == "9":
            TextStyle.print_class("Information", "\nGoodbye!")
            break
        else:
            TextStyle.print_class("Warning", "\nInvalid choice! Please select 1-3, or 9.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()