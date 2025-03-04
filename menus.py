# menus.py
from text_style import TextStyle

def display_initial_menu():
    TextStyle.print_class("Information", "\n=== Welcome to Space Scavenger ===")
    TextStyle.print_class("Information", "1) New Game")
    TextStyle.print_class("Information", "2) Load Game")
    TextStyle.print_class("Information", "3) Experimental")
    TextStyle.print_class("Information", "9) Exit")
    TextStyle.print_class("Information", "==============================")

def display_experimental_menu():
    TextStyle.print_class("Information", "\n=== Experimental Menu ===")
    TextStyle.print_class("Information", "1) Create Ship")
    TextStyle.print_class("Information", "2) Generate Mission")
    TextStyle.print_class("Information", "3) Combat")
    TextStyle.print_class("Information", "0) Return to Main Menu")
    TextStyle.print_class("Information", "================")

def display_create_ship_menu():
    TextStyle.print_class("Information", "\n=== Create Ship Menu ===")
    TextStyle.print_class("Information", "1) Create Enemy NPC")
    TextStyle.print_class("Information", "2) Create Neutral NPC")
    TextStyle.print_class("Information", "3) Create Trader NPC")
    TextStyle.print_class("Information", "0) Return to Experimental Menu")
    TextStyle.print_class("Information", "================")

def display_combat_menu():
    TextStyle.print_class("Information", "\n=== Combat Menu ===")
    TextStyle.print_class("Information", "1) Create Enemy NPC")
    TextStyle.print_class("Information", "2) Create Player")
    TextStyle.print_class("Information", "3) Initiate Combat")
    TextStyle.print_class("Information", "0) Return to Experimental Menu")
    TextStyle.print_class("Information", "================")

def display_create_enemy_npc_menu():
    TextStyle.print_class("Information", "\n=== Create Enemy NPC ===")
    TextStyle.print_class("Information", "1) Scout")
    TextStyle.print_class("Information", "2) Fighter")
    TextStyle.print_class("Information", "3) Freighter")
    TextStyle.print_class("Information", "4) Cruiser")
    TextStyle.print_class("Information", "0) Return to Combat Menu")
    TextStyle.print_class("Information", "================")

def display_create_player_menu():
    TextStyle.print_class("Information", "\n=== Create Player ===")
    TextStyle.print_class("Information", "1) Scout")
    TextStyle.print_class("Information", "2) Fighter")
    TextStyle.print_class("Information", "3) Freighter")
    TextStyle.print_class("Information", "4) Cruiser")
    TextStyle.print_class("Information", "0) Return to Combat Menu")
    TextStyle.print_class("Information", "================")

def display_game_menu(player_data, explored):
    TextStyle.print_class("Information", "\n=== Main Menu ===")
    TextStyle.print_class("Information", f"Location: {player_data['location']} | Energy: {player_data['energy']} | Security Zone: {player_data.get('security_zone', 1.0):.1f} | Universal Signature: {player_data['universal_signature']}")
    TextStyle.print_class("Information", "1) " + ("[System Already Explored]" if explored else "Explore System"))
    TextStyle.print_class("Information", "2) Show System")
    TextStyle.print_class("Information", "3) Show Ship Inventory")
    TextStyle.print_class("Information", "4) Scavenge")
    TextStyle.print_class("Information", "5) Fabrication")
    TextStyle.print_class("Information", "8) Travel Home")
    TextStyle.print_class("Information", "9) Save Game")
    TextStyle.print_class("Information", "0) Exit")
    TextStyle.print_class("Information", "================")

def display_home_menu(player_data):
    TextStyle.print_class("Information", "\n=== Home Menu ===")
    TextStyle.print_class("Information", f"Location: {player_data['location']} | Energy: {player_data['energy']} | Security Zone: {player_data.get('security_zone', 1.0):.1f} | Universal Signature: {player_data['universal_signature']}")
    TextStyle.print_class("Information", "1) Travel to New System")
    TextStyle.print_class("Information", "2) Show Inventory")
    TextStyle.print_class("Information", "3) Transfer Items")
    TextStyle.print_class("Information", "4) Drydock")
    TextStyle.print_class("Information", "5) Fabrication")
    TextStyle.print_class("Information", "6) Vaults")
    TextStyle.print_class("Information", "9) Save Game")
    TextStyle.print_class("Information", "0) Exit")
    TextStyle.print_class("Information", "================")

def display_drydock_menu(player_data):
    TextStyle.print_class("Information", "\n=== Drydock Menu ===")
    TextStyle.print_class("Information", f"Hull: {player_data['hull']}/{player_data['max_hull']} | Energy: {player_data['energy']} | Shield: {player_data['shield']}/{player_data['max_shield']}")
    TextStyle.print_class("Information", "1) Repair Ship")
    TextStyle.print_class("Information", "2) Fit Components")
    TextStyle.print_class("Information", "0) Return to Home Menu")
    TextStyle.print_class("Information", "================")