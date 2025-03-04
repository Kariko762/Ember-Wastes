# combat/combat_utils.py
import random
from text_style import TextStyle

def roll_d20():
    roll = random.randint(1, 20)
    return roll, f"[d20({roll})]"

def roll_damage(damage_die):
    """Roll damage based on dice string (e.g., 'NdM' for N dice of M sides)."""
    if not damage_die or not isinstance(damage_die, str):
        return 0, "[d0(0)]"
    
    try:
        # Parse NdM format (e.g., "3d6" -> 3 dice, 6 sides)
        if "d" in damage_die:
            num_dice, die_size = damage_die.split("d")
            num_dice = int(num_dice) if num_dice else 1  # Default to 1 die if no number
            die_size = int(die_size)
        else:
            # Handle plain numbers or invalid formats
            return 0, "[d0(0)]"
        
        rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        total = sum(rolls)
        roll_str = " + ".join(f"d{die_size}({roll})" for roll in rolls)
        return total, f"[{roll_str}]"
    except (ValueError, IndexError):
        TextStyle.print_class("Warning", f"Invalid damage die format: {damage_die}")
        return 0, "[d0(0)]"

def calculate_initiative(ship):
    roll, roll_str = roll_d20()
    total = roll + ship["initiative_modifier"]
    return total, f"{roll_str}+{ship['initiative_modifier']}"

def apply_damage(attacker, defender, damage):
    if defender["shield"] > 0:
        if damage <= defender["shield"]:
            defender["shield"] -= damage
        else:
            excess = damage - defender["shield"]
            defender["shield"] = 0
            defender["hull"] -= excess
    else:
        defender["hull"] -= damage