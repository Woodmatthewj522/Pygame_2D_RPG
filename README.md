# 2D MINI RPG - Adventure Game

A 2D top-down action RPG built with Python and Pygame featuring combat, crafting, quests, and dungeon exploration.

## Overview

Embark on an epic adventure through a dangerous world filled with enemies, resources to gather, and mysteries to uncover. Battle monsters, craft powerful equipment, complete quests for NPCs, and face off against mighty bosses in challenging dungeons.

## Features

### Core Gameplay
- **Top-Down Movement**: WASD controls with smooth camera following
- **Combat System**: Real-time action combat with weapons and attack animations
- **Leveling & Progression**: Gain experience, level up, and grow stronger
- **Health Regeneration**: Out-of-combat health recovery system
- **Equipment System**: Equip weapons, armor, helmets, boots, and accessories
- **Inventory Management**: 4x4 grid with drag-and-drop functionality

### Crafting & Resources
- **Smithing**: Craft weapons (Axe, Pickaxe, Sword) and armor pieces
- **Alchemy**: Brew healing potions and speed-enhancing elixirs
- **Resource Gathering**: Chop trees, mine stones/ore, pick flowers and carrots
- **Dynamic World**: Resources respawn over time

### World & Exploration
- **Multiple Zones**: 
  - Overworld with forests, paths, and villages
  - Dangerous dungeons with enemy spawns
  - Mystical Zone 2 with unique resources
  - Boss rooms for epic encounters
- **Interactive NPCs**: Quest givers and merchants
- **Houses**: Enter buildings for shelter
- **Portals**: Travel between different areas

### Quests & NPCs
- **Soldier Marcus**: Supply quest for healing potions, unlocks trading post
- **Miner Gareth**: Ore gathering quest with coin rewards
- **Dynamic Dialog**: Quest tracking with progress indicators
- **Vendor System**: Buy and sell items after completing quests

### Combat & Enemies
- **Enemy Types**: Orcs, goblins, and other creatures
- **Enemy AI**: Patrol, chase, and attack behaviors
- **Boss Battles**: Challenging multi-phase boss encounters
- **Loot Drops**: Enemies drop coins, resources, and items
- **Combat Stats**: Damage and defense calculations with equipment bonuses

### UI & Systems
- **Pause Menu**: Save, quit, or return to main menu
- **HUD Icons**: Quick access to inventory, crafting, equipment, and quests
- **Save/Load System**: Multiple save slots (4 available)
- **Music & Sound**: Dynamic music for different areas, sound effects for actions
- **Floating Damage Text**: Visual feedback for damage and healing
- **Tooltips**: Hover information for interactive objects

## Requirements

- Python 3.x
- Pygame library

## Installation

- Current Installation and gameplay is a bit tricky, future updates on repository and containerize to fix this
## Controls

### Movement
- `W` / `↑` - Move up
- `A` / `←` - Move left
- `S` / `↓` - Move down  
- `D` / `→` - Move right

### Actions
- `E` - Interact (talk to NPCs, gather resources, enter buildings)
- `SPACE` or `1` - Attack (when weapon equipped)
- `H` - Use health potion

### UI Controls
- `B` - Toggle Inventory
- `C` - Toggle Crafting menu
- `R` - Toggle Equipment screen
- `I` - Toggle Quest log
- `ESC` - Pause menu / Close dialogs

### Mouse Controls
- Left Click - Select items, craft, interact with UI
- Right Click - Quick equip/use items in inventory
- Drag & Drop - Move items between inventory slots

## Game Mechanics

### Combat
- Equip weapons to deal damage
- Different weapons have different damage values
- Armor provides defense, reducing incoming damage
- Attack cooldown prevents spam
- Invulnerability frames after taking damage

### Crafting Recipes

#### Smithing
- **Axe**: 5 Logs
- **Pickaxe**: 2 Logs (for mining)
- **Sword**: 2 Ore
- **Helmet**: 8 Stone (+5 Defense)
- **Chest Armor**: 15 Stone (+10 Defense)
- **Boots**: 6 Stone (+5 Defense)

#### Alchemy
- **Health Potion**: 3 Flowers (heals 25 HP)
- **Speed Potion**: 5 Flowers (temporary speed boost)

### Resource Gathering
- **Trees**: Requires Axe, drops Logs
- **Stones**: Requires Pickaxe, drops Stone
- **Ore Deposits**: Found in dungeons, drops Ore
- **Flowers**: Hand-picked, used for potions
- **Carrots**: Hand-picked, food item
- **Crystals**: Found in Zone 2, rare resource

### Leveling System
- Gain experience by defeating enemies
- Level up increases health, damage, and defense
- Experience requirement increases with each level
- Boss enemies grant bonus experience

## Map Files

The game loads maps from text files:
- `forest.txt` - Main overworld
- `dungeon1.txt` - First dungeon with enemies
- `boss_room.txt` - Boss encounter area
- `zone2.txt` - Mystical realm

### Map Legend
- `G` - Grass
- `T` - Tree
- `S` - Stone/Ore
- `H` - House
- `P` - Portal/Cave entrance
- `N` - NPC (Soldier Marcus)
- `M` - Miner NPC (Gareth)
- `F` - Flower
- `C` - Carrot
- `W` - Water
- `R` - Path
- `@` - Player spawn point

## Save System

- 4 save slots available
- Saves player stats, inventory, equipment, and quest progress
- Auto-saves at checkpoints (feature in development)
- Load game from main menu

## Tips & Tricks

1. **Early Game**: Focus on crafting an Axe first to gather logs efficiently
2. **Combat**: Keep your distance from enemies until you have good armor
3. **Quests**: Complete NPC quests early to unlock the trading post
4. **Resource Management**: Don't sell everything - keep materials for crafting
5. **Dungeon Prep**: Stock up on potions before entering dungeons
6. **Boss Fights**: Learn attack patterns and dodge during invulnerability
7. **Zone 2**: Requires good equipment due to tougher enemies

## Current Known Issues

- Cooking system is work-in-progress
- Save/load system needs additional polish
- Some placeholder graphics may be present
- Boss AI needs further balancing

## Future Enhancements

- [ ] Expanded crafting recipes (cooking system)
- [ ] More enemy varieties
- [ ] Additional zones and dungeons
- [ ] Magic/spell system
- [ ] More quest lines
- [ ] Achievement system
- [ ] Improved boss mechanics
- [ ] Controller support

## Technical Details

### Architecture
- **Main Game Loop**: State-based system (main menu, playing, pause, etc.)
- **Entity System**: Player, Enemy, Boss classes with inheritance
- **Combat Engine**: Cooldown-based with damage/defense calculations
- **Animation System**: Frame-based sprite animation
- **Camera System**: Follows player with margins
- **Collision Detection**: Rectangle-based collision

### Performance
- Targets 60 FPS
- Efficient tile-based rendering
- Sprite batching for better performance
- Enemy spawning system with limits

## Credits

**Developer**: Matthew Wood  
**Contact**: Woodmatthewj522@aol.com

### Assets
- Character sprites: Custom/Modified
- Music: Various sources
- Sound effects: Custom/Free resources

## License

This project is open source for educational purposes.

---

**Note**: This is an ongoing project and may receive updates. Check the repository for the latest version!

🎮 *Enjoy the adventure and good luck, brave hero!*
