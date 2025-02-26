# Ember Wastes JSON Configuration Options

## scavenge.json
- **energyThreshold**: Min energy to warn about returning home (default: 40).
- **minEnergy**: Min energy to scavenge (default: 20).
- **successThreshold**: Chance to find items (default: 40).
- **stages**: List of scavenging stages:
  - `percent`: Progress percentage (0-100).
  - `message`: Display text.
  - `energy`: Energy cost.
- **securityZones**: Extra item rolls by zone:
  - `moderate`: `{min: 0.3, max: 0.6, extraItems: {min: 0, max: 1, die: "d2"}}`.
  - `unsecure`: `{min: 0.0, max: 0.2, extraItems: {min: 0, max: 2, die: "d3"}}`.
- **itemCountRange**: Base items found `{min: 1, max: 3}`.

## scavenge_energy.json
- **siphoning.Man-Made**:
  - `minEnergy`: Min energy to attempt (5).
  - `scanCost`: Energy to scan (2).
  - `successChance`: Chance to find energy (70).
  - `dockCost`: Energy to dock (2).
  - `dockChance`: Chance for stable dock (70).
  - `dockPenalty`: Yield multiplier on failure (0.8).
  - `dockFailEnergyLoss`: Energy lost (2).
  - `dockFailHullLoss`: Hull lost (2).
  - `siphonCost`: Energy to siphon (1).
  - `energyYield`: `{Secure Space: 0.5, Moderately Secure Space: 0.6, Risky Space: 0.7, Unsecure Space: 0.8}`.
- **wreckSalvage.Unknown**: Similar structure for wrecks.

## combat.json
- **combatChanceMultiplier**: Scales combat chance (1.0).
- **securityZones**: Base combat chance by zone (e.g., `"Secure Space": {"min": 0.9, "max": 1.0, "baseChance": 10}`).
- **npcs**: List of NPCs:
  - `type`: Name (e.g., "Pirate").
  - `chance`: Spawn weight (0.0-1.0).
  - `taunts`: List of messages.
  - `alignment`: "Bad".
  - `stats`: `{hull, shield, energy, weapons}`.

## items.json
- **location_type**: (e.g., `"natural.planet"`) → List of `{name, chance}` for items.

## TODO: travel.json (Suggested)
- **homeCost**: Energy to travel home (20).
- **zones**: `{choice: {cost, zone, name}}` (e.g., `"1": {"cost": 10, "zone": 0.9, "name": "Secure Space"}`).
