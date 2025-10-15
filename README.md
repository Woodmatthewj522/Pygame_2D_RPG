# 🗡️ My first 2D Pygame RPG  
*A handcrafted 2D RPG built in Python & Pygame (09/25 – Currently in development)*  

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?logo=pygame&logoColor=white)
![Status](https://img.shields.io/badge/Status-Playable-orange)

---

## 🎮 Overview
A feature-rich single-player RPG developed entirely in **Pygame**, featuring exploration, combat, crafting, and interactive environments.  
Every system — from NPC dialogue to resource gathering — was coded manually over one month.

Free assets were sourced from **itch.io**, and audio was edited using **Audacity**.  
Although some parts need polishing, the game is **fully playable and stable**.

---

## 🧭 Features

### 🌍 Exploration
- Multiple zones: **World**, **Dungeon**, **Boss Room**, and **Zone 2**
- Camera follow & tile-based world maps  
- Environmental interaction (trees, ores, crystals, flowers)

### ⚔️ Combat
- Directional attacks with cooldowns  
- Floating text feedback (damage, XP, healing)  
- Enemies with aggro range, AI, and loot tables  
- Boss battles with multiple phases  

### 🧪 Crafting & Equipment
- Smithing and alchemy systems  
- Full drag-and-drop inventory  
- Equipment slots that affect stats dynamically  

### 🗣️ NPCs & Quests
- Dialogue windows and quest tracking  
- Miner and merchant NPCs  
- Quest objectives saved between sessions  

### 🎵 Audio
- Contextual background music per zone  
- Sound effects for chopping, mining, and combat  

---

## 📁 Folder Structure

```plaintext
├── Audio/                     # Sound effects and background music  
├── GUI/                       # GUI elements (buttons, menus, HUDs)  
├── Items/                     # Item data and related 
├── JSON/                      # Configuration and game data (JSON format)  
├── Maps/                      # Map layouts, tilesets, and level data  
├── NPC/                       # NPC Sprite Sheets and related
├── Pygame_RPG1_10.25/         # Main game directory  
│   ├── Pygame_RPG1_10.25.py       # Main game script (entry point)  
│   └── Pygame_RPG1_10.25.pyproj   # IDE project configuration (optional)  
│
├── Tiles/                     # Tile images/sheets and related map assets
│
├── .gitattributes             # Git text and diff settings  
├── .gitignore                 # ignored future assets that aren't used
└── README.md                  # Project documentation  

```
# ⚙️ Setup & Requirements
🐍 Python

Version 3.10+ recommended

# 📦 Dependencies

- Install via pip:

pip install pygame

# ▶️ Running the Game

Run the main Python file:

python Pygame_RPG1_10.25.py


Once launched, the main menu will appear.
Use the arrow keys or mouse to navigate and start a new game.

# 💾 Saving & Loading

The game auto-creates up to 4 save slots, located in the JSON/ folder.

You can manually save using the pause menu (ESC → Save Game).

Saves include player stats, position, inventory, and quest progress.

# 🧱 Key Systems
System	Description
Player	Tracks stats, level-ups, combat, and regeneration
Enemy / Boss	Handles AI, aggression, and loot
ActionBar	Quick-use slots for potions or tools
Item	Generic class for any collectible or equippable item
FloatingText	Displays visual damage/healing indicators
EnemySpawnPoint	Manages respawn timers for dungeon mobs
LootDrop	Handles visual item drops with animation
load_text_map()	Loads ASCII-style text maps for each level
save_game_data()	Saves game state to JSON
play_music()	Handles music transitions per area
#
# 🎨 Gameplay Tips

ESC → Pause, Save, or Exit

Right-click potions on the Action Bar to heal

Equip a Pickaxe to mine ores and crystals

Explore portals to unlock Zone 2 and Boss Rooms

Enemies respawn over time — grind for XP and loot

# 🔊 Credits
Category	Credit
Art & Tiles	Free/modified assets from itch.io

Audio	Edited and remixed in Audacity
Programming	Designed & coded by MW
Engine	Built entirely on Pygame
#
# 🚧 Known Issues / Future Plans
🔧 Known Issues

- Rare wall collision overlaps in tight areas

- Some placeholder code (e.g., unused constants)

- Occasional audio desync when looping music

# 💡 Planned Features

Improved dialogue system with branching options

More detailed inventory UI

Skill tree and ability cooldowns

Weather/day-night system

# 🏁 Development Notes

This RPG was created as a personal learning project to explore game design patterns, state management, and object-oriented architecture in Pygame.
All systems — from combat to saving — were designed modularly for future expansion.

# 🐉 License

This project is open for learning, and I will add changes as I go!
