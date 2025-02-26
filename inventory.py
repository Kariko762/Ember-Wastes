# inventory.py
from text_style import TextStyle

def show_inventory(ship_inventory, home_inventory):
    TextStyle.print_class("Information", "\n=== Inventory ===")
    TextStyle.print_class("Information", "Ship Inventory:")
    if not ship_inventory:
        TextStyle.print_class("Warning", "- Empty")
    else:
        for item in ship_inventory:
            TextStyle.print_class("Information", f"- {item['name']}: {item['quantity']}")
    TextStyle.print_class("Information", "Home Inventory:")
    if not home_inventory:
        TextStyle.print_class("Warning", "- Empty")
    else:
        for item in home_inventory:
            TextStyle.print_class("Information", f"- {item['name']}: {item['quantity']}")
    input("Press Enter to continue...")

def show_ship_inventory(ship_inventory):
    TextStyle.print_class("Information", "\n=== Ship Inventory ===")
    if not ship_inventory:
        TextStyle.print_class("Warning", "- Empty")
    else:
        for item in ship_inventory:
            TextStyle.print_class("Information", f"- {item['name']}: {item['quantity']}")
    input("Press Enter to continue...")

def transfer_items(ship_inventory, home_inventory):
    TextStyle.print_class("Information", "\n=== Transfer Items ===")
    TextStyle.print_class("Information", "1) Transfer from Ship to Home")
    TextStyle.print_class("Information", "2) Transfer from Home to Ship")
    TextStyle.print_class("Information", "0) Return to Home Menu")
    
    choice = input("\nSelect an option (0-2): ")
    if choice == "0":
        return
    
    try:
        option = int(choice)
        if option not in [1, 2]:
            TextStyle.print_class("Warning", "\nInvalid option! Please select 0, 1, or 2.")
            input("Press Enter to continue...")
            return
        
        source = ship_inventory if option == 1 else home_inventory
        destination = home_inventory if option == 1 else ship_inventory
        source_name = "Ship" if option == 1 else "Home"
        dest_name = "Home" if option == 1 else "Ship"
        
        if not source:
            TextStyle.print_class("Warning", f"\n{source_name} Inventory is empty! Nothing to transfer.")
            input("Press Enter to continue...")
            return
        
        TextStyle.print_class("Information", f"\n{source_name} Inventory:")
        for i, item in enumerate(source, 1):
            TextStyle.print_class("Information", f"{i}) {item['name']} ({item['quantity']})")
        
        item_choice = int(input(TextStyle.print_class("Information", f"Select an item to transfer (1-{len(source)}): ", delay_to_display=0, display_mode="instant", print_output=False)))
        if item_choice < 1 or item_choice > len(source):
            TextStyle.print_class("Warning", "\nInvalid item selection!")
            input("Press Enter to continue...")
            return
        
        item = source[item_choice - 1]
        qty = int(input(TextStyle.print_class("Information", f"How many {item['name']} to transfer (1-{item['quantity']})? ", delay_to_display=0, display_mode="instant", print_output=False)))
        if qty < 1 or qty > item["quantity"]:
            TextStyle.print_class("Warning", f"\nInvalid quantity! Must be between 1 and {item['quantity']}.")
            input("Press Enter to continue...")
            return
        
        item["quantity"] -= qty
        if item["quantity"] <= 0:
            source.remove(item)
        
        found = False
        for dest_item in destination:
            if dest_item["name"] == item["name"]:
                dest_item["quantity"] += qty
                found = True
                break
        if not found:
            destination.append({"name": item["name"], "quantity": qty})
        
        TextStyle.print_class("Information", f"\nTransferred {qty} {item['name']} from {source_name} to {dest_name} Inventory.")
        
    except ValueError:
        TextStyle.print_class("Warning", "\nInvalid input! Please enter a number.")
    input("Press Enter to continue...")