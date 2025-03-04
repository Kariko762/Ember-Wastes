# combat/combat_main.py
from combat.combat_utils import roll_d20, roll_damage, calculate_initiative, apply_damage
from text_style import TextStyle
import sys

def print_combat_stats(player, enemy):
    TextStyle.print_class("Information", "Stats")
    TextStyle.print_class("Information", "=====")
    TextStyle.print_class("Information", f"{player['name']} (Hull: {player['hull']}/{player['max_hull']}, Shield: {player['shield']}/{player['max_shield']})")
    TextStyle.print_class("Information", f"{enemy['name']} (Hull: {enemy['hull']}/{enemy['max_hull']}, Shield: {enemy['shield']}/{enemy['max_shield']})")
    TextStyle.print_class("Information", "=====")

def get_ammo_quantity(ship_inventory, ammo_type):
    """Get the quantity of ammo from ship inventory."""
    for item in ship_inventory:
        if item["name"] == ammo_type and "quantity" in item:
            return item["quantity"]
    return 0

def deduct_ammo(ship_inventory, ammo_type):
    """Deduct 1 ammo from ship inventory if available."""
    for item in ship_inventory:
        if item["name"] == ammo_type and "quantity" in item:
            if item["quantity"] > 0:
                item["quantity"] -= 1
                return True
            return False
    return False

def select_player_action(attacker, ship_inventory):
    """Handle player action selection with retry on invalid/no ammo."""
    while True:
        TextStyle.print_class("Information", "Select what action to take:")
        for i, weapon in enumerate(attacker["equippedWeapons"], 1):
            ammo_str = ""
            if "ammoType" in weapon and weapon["ammoType"] != "Power":
                ammo_qty = get_ammo_quantity(ship_inventory, weapon["ammoType"])
                ammo_str = f" [Qty {ammo_qty}]"
            TextStyle.print_class("Information", f"{i} - Attack with {weapon['name']}{ammo_str} ({weapon['damage']})")
        TextStyle.print_class("Information", "9 - Disengage")
        
        prompt = "Enter your choice: "
        styled_prompt = TextStyle.print_class("Information", prompt, delay_to_display=0, display_mode="instant", print_output=False)
        sys.stdout.write(styled_prompt)
        sys.stdout.flush()
        action = input().strip()
        full_line = TextStyle.print_class("Information", f"{prompt}{action}", delay_to_display=0, display_mode="instant", print_output=False)
        sys.stdout.flush()
        
        try:
            action_int = int(action)
            if 1 <= action_int <= len(attacker["equippedWeapons"]):
                selected_weapon = attacker["equippedWeapons"][action_int - 1]
                if "ammoType" in selected_weapon and selected_weapon["ammoType"] != "Power":
                    ammo_qty = get_ammo_quantity(ship_inventory, selected_weapon["ammoType"])
                    if ammo_qty <= 0:
                        TextStyle.print_class("Warning", f"No {selected_weapon['ammoType']} left for {selected_weapon['name']}!")
                        continue  # Retry selection
                    if not deduct_ammo(ship_inventory, selected_weapon["ammoType"]):
                        TextStyle.print_class("Warning", f"Failed to deduct {selected_weapon['ammoType']} for {selected_weapon['name']}!")
                        continue
                    TextStyle.print_class("Information", f"Used 1 {selected_weapon['ammoType']}. Remaining: {ammo_qty - 1}")
                return selected_weapon, False  # Success, no disengage
            elif action_int == 9:
                return None, True  # Disengage
            else:
                TextStyle.print_class("Warning", "Invalid action!")
        except ValueError:
            TextStyle.print_class("Warning", "Invalid input! Please enter a number.")
        # Loop continues until valid action

def initiate_combat(player_data, enemy_npc, ship_inventory=None):
    if ship_inventory is None:
        ship_inventory = []
    
    TextStyle.print_class("Information", "\n=== Combat Initiated ===")
    
    player_init, player_init_str = calculate_initiative(player_data)
    enemy_init, enemy_init_str = calculate_initiative(enemy_npc)
    TextStyle.print_class("Information", f"- {player_data['name']} Rolling Initiative: {player_init_str} = {player_init}")
    TextStyle.print_class("Information", f"- {enemy_npc['name']} Rolling Initiative: {enemy_init_str} = {enemy_init}")
    TextStyle.print_class("Information", "=====")
    
    turn_order = [(player_data, "Player"), (enemy_npc, "Enemy")] if player_init >= enemy_init else [(enemy_npc, "Enemy"), (player_data, "Player")]
    
    round_num = 1
    while player_data["hull"] > 0 and enemy_npc["hull"] > 0:
        print_combat_stats(player_data, enemy_npc)
        TextStyle.print_class("Information", f"\nRound {round_num}")
        TextStyle.print_class("Information", "=====")
        
        for attacker, attacker_type in turn_order:
            defender = enemy_npc if attacker_type == "Player" else player_data
            if attacker["hull"] <= 0:
                continue
            
            if attacker_type == "Player":
                selected_weapon, disengage = select_player_action(attacker, ship_inventory)
                if disengage:
                    if player_data["energy"] < 20:
                        TextStyle.print_class("Warning", "Not enough energy to disengage (Need 20 Energy)!")
                        continue
                    disengage_roll, disengage_str = roll_d20()
                    disengage_status = "Success" if disengage_roll > defender["disengage"] else "Warning"
                    disengage_line = f"{attacker['name']} Rolling Disengage (> {defender['disengage']}): {disengage_str} - {'Success!' if disengage_roll > defender['disengage'] else 'Failed to Disengage'}"
                    TextStyle.print_class(disengage_status, disengage_line)
                    if disengage_roll > defender["disengage"]:
                        TextStyle.print_class("Information", f"{attacker['name']} successfully disengages! Returning to Home...")
                        player_data["energy"] -= 20
                        player_data["location"] = "Home"
                        return
                    continue  # Retry if disengage fails
                if selected_weapon:  # Valid weapon selected
                    attack_roll, attack_str = roll_d20()
                    hit_status = "Success" if attack_roll >= defender["armor_class"] else "Warning"
                    attack_line = f"{attacker['name']} Rolling Attack (> {defender['armor_class']}): {attack_str} - {'Hit!' if attack_roll >= defender['armor_class'] else 'Miss!'}"
                    TextStyle.print_class(hit_status, attack_line)
                    if attack_roll >= defender["armor_class"]:
                        damage, damage_str = roll_damage(selected_weapon["damage"])
                        TextStyle.print_class("Information", f"{attacker['name']} Rolling Damage : {damage_str} - {attacker['name']} Deals {damage} Damage.")
                        apply_damage(attacker, defender, damage)
            else:
                attack_roll, attack_str = roll_d20()
                hit_status = "Success" if attack_roll >= defender["armor_class"] else "Warning"
                attack_line = f"{attacker['name']} Rolling Attack (> {defender['armor_class']}): {attack_str} - {'Hit!' if attack_roll >= defender['armor_class'] else 'Miss!'}"
                TextStyle.print_class(hit_status, attack_line)
                if attack_roll >= defender["armor_class"]:
                    damage, damage_str = roll_damage(attacker["equippedWeapons"][0]["damage"])
                    TextStyle.print_class("Information", f"{attacker['name']} Rolling Damage : {damage_str} - {attacker['name']} Deals {damage} Damage.")
                    apply_damage(attacker, defender, damage)
        
        TextStyle.print_class("Information", "- - -")
        
        if player_data["hull"] <= 0:
            TextStyle.print_class("Warning", "\nYour ship has been destroyed! Game Over.")
            return
        if enemy_npc["hull"] <= 0:
            TextStyle.print_class("Information", f"\n{enemy_npc['name']} has been destroyed! Victory!")
            return
        
        round_num += 1