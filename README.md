# Ember Wastes (WIP)

## Overview
*Ember Wastes* is a text-based space exploration game built in Python, where players captain a ship through a procedurally generated universe fraught with danger and opportunity. Survive by scavenging resources, repairing and upgrading your vessel, engaging in turn-based combat with hostile ships, and managing energy reserves to explore distant systems. Whether you're a scavenger hunting for loot in chaotic nebulae or a strategist outfitting your ship in the safety of your home base, *Ember Wastes* offers a gritty, immersive experience of survival and discovery in a vast, unforgiving cosmos.

## Features
- **Dynamic Systems:** Travel to procedurally generated systems with varying security levels (1.0 safe to 0.0 lawless), each offering unique loot tables and risks.
- **Ship Management:** Repair hull damage, fit new components, and craft items like power cells to keep your ship operational.
- **Combat:** Face off against enemy ships in turn-based battles, triggered by travel into low-security zones, with outcomes based on ship stats and tactics.
- **Scavenging:** Explore systems to gather resources like Scrap Metal or siphon energy, with random yields driven by percentile rolls.
- **Persistent Progress:** Save and load your game state, preserving inventory, ship condition, and explored systems.
- **Modular Design:** Built with an additive, function-based architecture—new features slot in as standalone files with minimal integration.

## How It Works
- Start at your **Home** base, where you repair, craft, and manage inventory.
- Travel to **new systems** (25 energy cost), risking combat encounters based on security status (e.g., 0.0 = 100% chance).
- **Explore** systems (10 energy) to reveal details, **scavenge** for loot, or **fight** enemies like Pirate Scouts.
- Refuel via **fabrication** (convert Power Cells to energy) or **energy siphoning** from rich systems.
- Return home to regroup, or press deeper into the wastes.

## Project Structure
- `core.py`: Main game loop and menu hub.
- `game_logic.py`: New game setup, travel, and exploration logic.
- `combat/`: Turn-based combat system and enemy triggers.
- `ships/`: Ship definitions (player and NPCs).
- `systems/`: System generation and classification.
- `scavenge/`: Resource gathering mechanics.
- `fabrication/`: Crafting system.
- `drydock/`: Ship repair and upgrades.
- Plus utilities, menus, and JSON data files for extensibility.

## Current State
As of February 2025, *Ember Wastes* is a playable prototype with a solid foundation:
- Core mechanics (travel, combat, scavenging) are functional.
- Combat triggers on travel, scaled by system security.
- Energy management balances exploration and survival.
- Next steps include expanding system types (e.g., Trader Hubs, Junkers Graveyards) with unique encounters and loot.

## Getting Started
1. Clone the repo: `git clone https://github.com/Kariko762/Ember-Wastes.git`
2. Run `core.py`: `python core.py`
3. Choose "New Game" and begin your journey!

## Contributing
This project is built additively—new features are welcome as standalone files with light integration. Want to add a new ship, system type, or mechanic? Fork the repo, code it up, and submit a pull request. Check the issues tab for current priorities like combat trigger expansion or new "unknown" system types.

## License
[Pending—add your preferred license here, e.g., MIT, GPL]  
Created by Kariko762.
