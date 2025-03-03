# vaults.py
import json
import random
import os
import time
from text_style import TextStyle
from utils import inventoryRemove

def load_items():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "items.json")
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        TextStyle.print_class("Warning_Mode_Line", f"Error loading items.json: {str(e)}")
        return {}

def vaultCheck(player_data, ship_inventory):
    """Check if a vault is found and add it to ship_inventory."""
    items_data = load_items()
    vaults = items_data.get("vaults", {})
    if not vaults:
        return
    
    total_chance = sum(vault["chance"] for vault in vaults.values())
    roll = random.uniform(0, total_chance)
    cumulative = 0
    for vault_name, vault_data in vaults.items():
        cumulative += vault_data["chance"]
        if roll <= cumulative:
            TextStyle.print_class("Success_Mode_Line", f"Found a {vault_name}!")
            vault_entry = {"name": vault_name, "type": "vault", "quantity": 1}
            for inv_item in ship_inventory:
                if inv_item["name"] == vault_name and inv_item.get("type") == "vault":
                    inv_item["quantity"] = inv_item.get("quantity", 1) + 1
                    break
            else:
                ship_inventory.append(vault_entry)
            break

def open_vault(vault, ship_inventory, home_inventory, location):
    """Open a vault at home, adding items to home_inventory from lootTable and setItems."""
    if location != "Home":
        TextStyle.print_class("Warning_Mode_Line", "Vaults can only be opened at Home!")
        return False
    
    items_data = load_items()
    vaults = items_data.get("vaults", {})
    vault_name = vault["name"]
    if vault_name not in vaults:
        TextStyle.print_class("Warning_Mode_Line", f"Unknown vault type: {vault_name}")
        return False
    
    vault_data = vaults[vault_name]
    loot_table = vault_data["lootTable"]
    set_items = vault_data.get("setItems", [])
    
    TextStyle.print_class("Information", f"\nOpening {vault_name}...")
    time.sleep(0.5)
    found_items = []
    
    for row in loot_table:
        if random.random() <= row["weight"]:
            items_count = random.randint(row["minItems"], row["maxItems"])
            loot_section = items_data.get(row["name"], [])
            if not loot_section:
                continue
            total_chance = sum(item["chance"] for item in loot_section)
            for _ in range(items_count):
                roll = random.uniform(0, total_chance)
                cumulative = 0
                for item in loot_section:
                    cumulative += item["chance"]
                    if roll <= cumulative:
                        qty = random.randint(row["minQty"], row["maxQty"])
                        loot_entry = {"name": item["name"], "quantity": qty}
                        if "ammoType" in item:
                            loot_entry["ammoType"] = item["ammoType"]
                        found_items.append(loot_entry)
                        break
    
    for set_item in set_items:
        if random.random() <= set_item["weight"]:
            qty = random.randint(set_item["minQty"], set_item["maxQty"])
            loot_entry = {"name": set_item["name"], "quantity": qty}
            found_items.append(loot_entry)
    
    if found_items:
        TextStyle.print_class("Information", f"Found {len(found_items)} items:")
        for item in found_items:
            display_str = f"- {item['name']} x{item['quantity']}"
            if "ammoType" in item:
                display_str += f" (Ammo: {item['ammoType']})"
            TextStyle.print_class("Success_Mode_Line", display_str)
            for inv_item in home_inventory:
                if inv_item["name"] == item["name"]:
                    inv_item["quantity"] += item["quantity"]
                    break
            else:
                home_inventory.append(item)
    else:
        TextStyle.print_class("Warning_Mode_Line", "Vault was empty!")
    
    return True

def vault_menu(player_data, ship_inventory, home_inventory):
    """Menu to view and open vaults in ship_inventory when at home."""
    if player_data["location"] != "Home":
        TextStyle.print_class("Warning_Mode_Line", "Vaults can only be managed at Home!")
        return
    
    while True:
        vaults = [item for item in ship_inventory if item.get("type") == "vault"]  # Refresh list each loop
        if not vaults:
            TextStyle.print_class("Information", "\nNo vaults in ship inventory!")
            input("Press Enter to continue...")
            return
        
        TextStyle.print_class("Information", "\n=== Vault Menu ===")
        for i, vault in enumerate(vaults, 1):
            qty = vault.get("quantity", 1)
            TextStyle.print_class("Information", f"{i}) {vault['name']} (Qty: {qty})")
        TextStyle.print_class("Information", "0) Exit")
        
        choice_input = input("Select a vault to open (0-9): ").strip()
        try:
            choice = int(choice_input)
            if choice == 0:
                TextStyle.print_class("Information", "Exiting Vault Menu...")
                break
            if 1 <= choice <= len(vaults):
                selected_vault = vaults[choice - 1]
                if open_vault(selected_vault, ship_inventory, home_inventory, player_data["location"]):
                    inventoryRemove(ship_inventory, selected_vault)
            else:
                TextStyle.print_class("Warning_Mode_Line", "Invalid selection!")
        except ValueError:
            TextStyle.print_class("Warning_Mode_Line", "Invalid input! Please enter a number.")
        input("Press Enter to continue...")  # Moved outside try to always prompt

if __name__ == "__main__":
    test_player = {"location": "Home", "energy": 100}
    test_ship_inventory = [{"name": "Small Basic Vault", "type": "vault", "quantity": 1}]
    test_home_inventory = []
    vault_menu(test_player, test_ship_inventory, test_home_inventory)