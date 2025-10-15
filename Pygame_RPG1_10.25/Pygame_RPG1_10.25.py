## Pygame 2D RPG game I made over the past month 09/25-10/25
# Free assets borrowed/modified from itch.io
# audio modified using Audacity
# Some fixes needed but works for the most part! 

# Organized the code the best i could, enjoy reading!

## -*- coding: utf-8 -*-
import os
import random
import sys
import math
import pygame
import json
import pygame.mixer

# --- CONSTANTS ---
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 50
PLAYER_SIZE = 40
PLAYER_SPEED = 5
COLS = 4
BORDER_THICKNESS = 6
CRAFTING_TIME_MS = 3000
ICON_SIZE = 30
CHOPPING_DURATION = 3000
RESPAWN_TIME = 120000  # 2 mins
MINING_DURATION = 2000  # ms
SFX_VOLUME = 0.3

# Combat constants
COMBAT_RANGE = 80
COMBAT_COOLDOWN = 2000  # ms between attacks (slower)
ENEMY_SPAWN_RATE = 0.02  # chance per frame in dungeon
MAX_ENEMIES = 8
ENEMY_SPEED = 2
ENEMY_AGGRO_RANGE = 150
ENEMY_ATTACK_RANGE = 60
ENEMY_ATTACK_COOLDOWN = 1500

# Attack animation state
is_attacking = False
attack_timer = 0

# Player constants
PLAYER_SIZE_INDOOR = 80
PLAYER_MAX_HEALTH = 100
PLAYER_BASE_DAMAGE = 15
PLAYER_BASE_DEFENSE = 0

# Inventory GUI constants
INVENTORY_SLOT_SIZE = 40
INVENTORY_GAP = 5
INVENTORY_WIDTH = 4 * INVENTORY_SLOT_SIZE + 5 * INVENTORY_GAP
INVENTORY_HEIGHT = 4 * INVENTORY_SLOT_SIZE + 5 * INVENTORY_GAP
INVENTORY_X = (WIDTH - INVENTORY_WIDTH) // 2
INVENTORY_Y = (HEIGHT - INVENTORY_HEIGHT) // 2

# Crafting GUI constants
CRAFTING_PANEL_WIDTH = 420
CRAFTING_PANEL_HEIGHT = 300
CRAFTING_X = (WIDTH - CRAFTING_PANEL_WIDTH) // 2
CRAFTING_Y = (HEIGHT - CRAFTING_PANEL_HEIGHT) // 2

# Equipment GUI constants
EQUIPMENT_SLOT_SIZE = 40
EQUIPMENT_GAP = 20
EQUIPMENT_ROWS = 2
EQUIPMENT_COLS = 4
EQUIPMENT_PANEL_WIDTH = 4 * EQUIPMENT_SLOT_SIZE + 4 * EQUIPMENT_GAP + 20
EQUIPMENT_PANEL_HEIGHT = 2 * EQUIPMENT_SLOT_SIZE + 4 * EQUIPMENT_GAP + 100  # Extra space for stats
EQUIPMENT_X = (WIDTH - EQUIPMENT_PANEL_WIDTH) // 2
EQUIPMENT_Y = (HEIGHT - EQUIPMENT_PANEL_HEIGHT) // 2

# Inventory drag-and-drop
dragging_item = None
dragging_from_slot = None
drag_offset = (0, 0)

# Dungeon constants
DUNGEON_SIZE = 30
DUNGEON_SPAWN_X = 5 * TILE_SIZE
DUNGEON_SPAWN_Y = 5 * TILE_SIZE
player_movement_history = []
is_dashing = False
dash_cooldown = 0
is_game_over = False
chop_sound_played = False
mine_sound_played = False
cooking_tab_rect = None
shop_scroll_offset = 0
crystal_rects = []
water_tiles = []
path_tiles = []
path2_tiles = []

# not currently used but some functionality
zone2_merchant_rect = None
zone2_return_portal = None

# Music constants
MUSIC_FILES = {
    "main_menu": "Audio/main.mp3",   
    "forest": "Audio/forest.mp3",        
    "dungeon": "Audio/dungeon_theme.mp3",
    "boss_room": "Audio/boss_battle.mp3", # no .mp3, not in use
    "walk_sound": "Audio/walk.mp3" # have .mp3, also not in use
}
walk_sound = None

# --- GAME STATE GLOBALS ---
player_pos = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
map_offset_x = 0
map_offset_y = 0
current_level = "world"  # "world", "house", or "dungeon"
current_house_index = None
current_music = None

# Player animation state
last_direction = "down"
current_direction = "idle"
player_frame_index = 0
player_frame_timer = 0
player_frame_delay = 120

# Player action state
is_chopping = False
chopping_timer = 0
chopping_target_tree = None
is_swinging = False
swing_delay = 150
idle_chop_delay = 0
enemy_frames = None

# Stone specific state
is_mining = False
mining_timer = 0
mining_target_stone = None

# Pause menu state
show_pause_menu = False
pause_menu_selected_option = 0
pause_button_rects = {}

# UI state
show_inventory = False
show_crafting = False
show_equipment = False
show_quests = False
is_crafting = False
crafting_timer = 0
item_to_craft = None
crafting_tab = "smithing"

# NPC and Quest state
show_npc_dialog = False
npc_quest_active = False
npc_quest_completed = False
potions_needed = 3
potions_delivered = 0
npc_idle_timer = 0
npc_idle_offset_y = 0
npc_idle_direction = 1

# Vendor system
show_vendor_gui = False
vendor_tab = "buy"  # "buy" or "sell"
buy_button_rects = {}
sell_button_rects = {}

# Miner NPC state
show_miner_dialog = False
miner_quest_active = False
miner_quest_completed = False
ore_needed = 10
miner_idle_timer = 0
miner_idle_offset_y = 0
miner_idle_direction = 1

# Game objects
inventory = [[None for _ in range(4)] for _ in range(4)]
equipment_slots = {
    "weapon": None,
    "helmet": None,
    "armor": None,
    "boots": None,
    "ring1": None,
    "ring2": None,
    "amulet": None,
    "shield": None,
}
tree_rects = []
house_list = []
stone_rects = []
chopped_trees = {}
chopped_stones = {}
picked_flowers = {}
indoor_colliders = []
flower_tiles = []
carrot_tiles = []
picked_carrots = []
leaf_tiles = []
npc_rect = None
miner_npc_rect = None
gold_coins = []
last_enemy_spawn = 0
loot_drops = []

# Level up visual feedback
level_up_timer = 0
level_up_text = ""
show_level_up = False

# Dungeon objects
boss1_portal = None
dungeon_portal = None
zone2_portal = None
dungeon_walls = []
enemies = []
dungeon_exit = None
boss_room_walls = []
enemy_spawn_points = []
floating_texts = []
boss_door_rect = None

# Crafting button rects
axe_button_rect = None
sword_button_rect = None
pickaxe_button_rect = None
potion_button_rect = None
smithing_tab_rect = None
alchemy_tab_rect = None
chest_button_rect = None
helmet_button_rect = None
boots_button_rect = None

# Game state management
game_state = "main_menu"
selected_save_slot = 1
save_slots = [None, None, None, None]  # 4 save slots
menu_selected_option = 0
boss_enemy = None
music_volume = 0.5

# ----------------------------------------CLASSES -------------------------------------------------------------

class ActionBar:
    def __init__(self, x, y, slot_size=40, num_slots=5):
        self.x = x
        self.y = y
        self.slot_size = slot_size
        self.num_slots = num_slots
        self.slots = [None] * num_slots  # each slot holds an Item or None

    def draw(self, screen, font=None):
        for i in range(self.num_slots):
            rect = pygame.Rect(self.x + i * (self.slot_size + 5), self.y, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, (60, 60, 60), rect)  # background
            pygame.draw.rect(screen, (200, 200, 200), rect, 2)  # border

            item = self.slots[i]
            if item:
                screen.blit(item.image, rect.topleft)
                if item.count > 1 and font:
                    count_surf = font.render(str(item.count), True, (255, 255, 255))
                    screen.blit(count_surf, (rect.right - count_surf.get_width() - 2,
                                             rect.bottom - count_surf.get_height() - 2))

    def handle_event(self, event, player):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # right click
            mx, my = event.pos
            for i in range(self.num_slots):
                rect = pygame.Rect(self.x + i * (self.slot_size + 5), self.y, self.slot_size, self.slot_size)
                if rect.collidepoint(mx, my):
                    item = self.slots[i]
                    if item and item.name.lower() == "potion":
                        player.heal(25)  # or item-specific heal
                        item.count -= 1
                        if item.count <= 0:
                            self.slots[i] = None

class Item:
    def __init__(self, name, image=None, count=1, category=None, damage=0, defense=0):
        if image is None:
            # fallback magenta box if image is missing
            image = pygame.Surface((32, 32))
            image.fill((255, 0, 255))
        self.name = name
        self.image = image
        self.count = count
        self.category = category
        self.damage = damage
        self.defense = defense

class FloatingText:
    def __init__(self, text, pos, color=(255, 0, 0), lifetime=1000):
        """
        text: string to display
        pos: (x, y) world coordinates where the text starts
        color: RGB color of the text
        lifetime: how long (ms) the text stays visible
        """
        self.text = text
        self.x, self.y = pos
        self.color = color
        self.lifetime = lifetime
        self.start_time = pygame.time.get_ticks()
        self.alpha = 255  # start fully opaque

    def update(self):
        elapsed = pygame.time.get_ticks() - self.start_time
        if elapsed < self.lifetime:
            # Move upward
            self.y -= 0.5  
            # Fade out
            self.alpha = max(0, 255 - int((elapsed / self.lifetime) * 255))
        else:
            self.alpha = 0  # invisible

    def is_alive(self):
        return self.alpha > 0

    def draw(self, surface, font, camera_x=0, camera_y=0):
        if self.alpha <= 0:
            return
        text_surf = font.render(self.text, True, self.color)
        text_surf.set_alpha(self.alpha)
        surface.blit(text_surf, (self.x - camera_x, self.y - camera_y))

import pygame

class Player:
    def __init__(self):
        # Core stats
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100

        # Base stats
        self.base_max_health = PLAYER_MAX_HEALTH
        self.base_damage = PLAYER_BASE_DAMAGE
        self.base_defense = PLAYER_BASE_DEFENSE
        self.base_speed = PLAYER_SPEED
        # Dynamic stats
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.damage = self.base_damage
        self.defense = self.base_defense
        # Combat & state
        self.last_attack_time = 0
        self.is_invulnerable = False
        self.invulnerability_timer = 0
        self.invulnerability_duration = 1000  # ms
        # Health regeneration
        self.health_regen_rate = 0.5  # HP per second
        self.health_regen_delay = 5000  # 5 seconds after last damage
        self.out_of_combat = True
        self.last_damage_time = 0
        # Position & hitbox
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.hitbox = self.rect.inflate(-PLAYER_SIZE // 4, -PLAYER_SIZE // 4)

        # Status effects (buffs/debuffs)
        self.status_effects = {}  # {"poison": {"duration": 3000, "timer": 0, "tick_damage": 2}}

    # ------------------------
    # Combat
    # ------------------------
    def take_damage(self, damage_amount, current_time):
        """Apply damage, respecting invulnerability, defense, and effects."""
        if self.is_invulnerable:
            return False

        # Track damage time for regen
        self.last_damage_time = current_time
        self.out_of_combat = False
        # FIXED: Calculate damage reduction from defense
        total_defense = self.get_total_defense()
    
        # Defense reduces damage by a percentage (diminishing returns formula)
        damage_reduction = total_defense / (total_defense + 100)
    
        # Apply damage reduction
        reduced_damage = damage_amount * (1 - damage_reduction)
        final_damage = max(1, int(reduced_damage))
    
        self.health -= final_damage
        self.is_invulnerable = True
        self.invulnerability_timer = current_time

        # Show damage feedback with defense info
        if total_defense > 0:
            floating_texts.append(FloatingText(
                f"-{final_damage} ({int(damage_reduction*100)}% blocked)",
                (self.rect.x, self.rect.y - 15),
                color=(255, 150, 0)
            ))
        else:
            floating_texts.append(FloatingText(
                f"-{final_damage}",
                (self.rect.x, self.rect.y - 15),
                color=(255, 0, 0)
            ))

        if self.health <= 0:
            self.die()
            return True
        return False
    def regenerate_health(self, dt, current_time):
        if current_time - self.last_damage_time >= self.health_regen_delay:
            self.out_of_combat = True
        
            # Regenerate health
            if self.health < self.max_health:
                regen_amount = (self.health_regen_rate * dt) / 1000
                self.health = min(self.max_health, self.health + regen_amount)

    def heal(self, heal_amount):
        """Heal with feedback, no overheal beyond max_health."""
        old_health = self.health
        self.health = min(self.max_health, self.health + heal_amount)
        actual_heal = self.health - old_health

        if actual_heal > 0:
            floating_texts.append(FloatingText(
                f"+{actual_heal}",
                (self.rect.x, self.rect.y - 15),
                color=(0, 255, 0)
            ))

    def die(self):
        """Handle player death (game over, respawn, etc.)."""
        global is_game_over
        print("💀 Player has died!")

        # Trigger game over state
        is_game_over = True

        floating_texts.append(FloatingText(
            "You Died",
            (self.rect.centerx, self.rect.centery - 50),
            color=(255, 0, 0),
            lifetime=3000
        ))

        pygame.mixer.music.stop()

    # ------------------------
    # Leveling
    # ------------------------
    def gain_experience(self, exp_amount):
        self.experience += exp_amount
        while self.experience >= self.experience_to_next:
            self.experience -= self.experience_to_next
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * 1.25)

        # Growth formulas
        health_bonus = 10 + self.level * 5
        damage_bonus = 2 + self.level // 2
        defense_bonus = 1 + self.level // 3 

        self.max_health += health_bonus
        self.health = self.max_health
        self.damage += damage_bonus
        self.base_defense += defense_bonus 

        # Popup feedback
        global show_level_up, level_up_timer, level_up_text
        show_level_up = True
        level_up_timer = 0
        level_up_text = f"Level {self.level}!"

        print(f"⬆️ Level {self.level} | HP: {self.max_health} | Defense: {self.get_total_defense()}")


    # ------------------------
    # Combat Actions
    # ------------------------

    def can_attack(self, current_time):
        """Check if player can attack (cooldown check)."""
        return current_time - self.last_attack_time >= COMBAT_COOLDOWN 

    def attack(self, current_time):
        if self.can_attack(current_time):
            self.last_attack_time = current_time
            return True
        return False

    def get_total_damage(self, equipped_weapon=None):
        """Return base + weapon + buffs damage."""
        weapon_damage = equipped_weapon.damage if equipped_weapon else 0
        buff_bonus = sum(buff.get("damage", 0) for buff in self.status_effects.values())
        return self.damage + weapon_damage + buff_bonus

    # ------------------------
    # Status Effects
    # ------------------------
    def add_status_effect(self, name, duration, **kwargs):
        """Apply a buff/debuff (ex: poison, regen)."""
        self.status_effects[name] = {"duration": duration, "timer": 0, **kwargs}
    def get_total_defense(self):
        total_defense = self.base_defense
   
        for slot_name, equipped_item in equipment_slots.items():
            if equipped_item and hasattr(equipped_item, 'defense'):
                total_defense += equipped_item.defense
    
        buff_bonus = sum(buff.get("defense", 0) for buff in self.status_effects.values())
        total_defense += buff_bonus
    
        return total_defense

    def update_status_effects(self, dt):
        expired = []
        for effect, data in self.status_effects.items():
            data["timer"] += dt
            if effect == "poison" and data["timer"] >= 1000:
                self.take_damage(data.get("tick_damage", 1), pygame.time.get_ticks())
                data["timer"] = 0
            if data["duration"] <= 0:
                expired.append(effect)
            else:
                data["duration"] -= dt
        for effect in expired:
            del self.status_effects[effect]

    def get_current_speed(self):
        """Return current movement speed, including buffs/debuffs."""
        speed = self.base_speed
        for effect, data in self.status_effects.items():
            if effect == "speed":
                speed += data.get("speed_bonus", 0)
        return speed

    # ------------------------
    # Update Loop
    # ------------------------
    def update(self, dt, current_time):
        if self.is_invulnerable and current_time - self.invulnerability_timer >= self.invulnerability_duration:
            self.is_invulnerable = False
        self.update_status_effects(dt)
        self.regenerate_health(dt, current_time)
        self.hitbox.center = self.rect.center
player = Player()

class Enemy:
    def __init__(self, x, y, enemy_type="orc", frames=None, enemy_frames=None):
        # Animation frames (prefer passed frames, then global)
        if frames is None and 'enemy_frames' in globals():
            frames = enemy_frames
        self.frames = (frames.get(enemy_type, []) if frames else [])

        # Visible sprite
        if self.frames:
            self.image = self.frames[0].copy()
            self.rect = self.image.get_rect(topleft=(x, y))
        else:
            self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            self.image.fill((180, 60, 60))
            self.rect = self.image.get_rect(topleft=(x, y))

        # Much smaller, tighter hitbox for better collision detection
        self.hitbox = self.rect.inflate(-PLAYER_SIZE * 2, -PLAYER_SIZE * 2)
        
        # Track facing direction for flipping sprite
        self.facing_right = True
        self.last_dx = 0  # Track last horizontal movement

        # Stats
        self.type = enemy_type
        if enemy_type == "orc":
            self.health = 100
            self.damage = 30
            base_xp = 10
        else:
            self.health = 100
            self.damage = 30
            base_xp = 10

        self.max_health = self.health
        self.speed = ENEMY_SPEED
        self.last_attack_time = 0
        self.state = "idle"   # idle, chasing, attacking
        self.target = None

        # XP reward
        self.experience_reward = base_xp 

        # Loot table
        self.loot_table = self._generate_loot_table(enemy_type)

        # Animation
        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 200

        # Idle wandering
        self.path_timer = 0
        self.random_direction = random.choice(
            [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
        )

    # ------------------------
    # Combat
    # ------------------------
    def take_damage(self, damage_amount):
            old_health = self.health
            self.health -= damage_amount

            floating_texts.append(FloatingText(
                f"-{damage_amount}",
                (self.rect.x, self.rect.y - 15),
                color=(255, 50, 50)
            ))

            # Boss-specific damage feedback
            if self.health > 0:
                # Show percentage of health remaining
                health_percent = int((self.health / self.max_health) * 100)
                floating_texts.append(FloatingText(
                    f"{health_percent}%",
                    (self.rect.centerx + 30, self.rect.y - 10),
                    color=(255, 255, 100),
                    lifetime=800
                ))

                # Special reactions to taking damage
                if self.health < self.max_health * 0.5 and old_health >= self.max_health * 0.5:
                    floating_texts.append(FloatingText(
                        "You will pay for that!",
                        (self.rect.centerx, self.rect.y - 60),
                        color=(255, 100, 100),
                        lifetime=2000
                    ))
            else:
                # Boss death message
                floating_texts.append(FloatingText(
                    "The Ancient Guardian falls!",
                    (self.rect.centerx, self.rect.y - 50),
                    color=(255, 215, 0),
                    lifetime=3000
                ))

            return self.health <= 0

    def attack_player(self, player, current_time):
        """Attack player if in range and cooldown passed."""
        if self.hitbox.colliderect(player.rect):
            # Use custom cooldown if defined
            attack_cd = getattr(self, "attack_cooldown", ENEMY_ATTACK_COOLDOWN)
            if current_time - self.last_attack_time >= attack_cd:
                self.last_attack_time = current_time
                player.take_damage(self.damage, current_time)
                floating_texts.append(FloatingText(
                    f"-{self.damage}",
                    (player.rect.x, player.rect.y - 20),
                    color=(255, 0, 0)
                ))
                print(f"{self.type} attacked player for {self.damage} damage")
                return True
        return False


    # Loot table generation
    def _generate_loot_table(self, enemy_type):
        """Define what items this enemy type can drop."""
        if enemy_type == "orc":
            return [
                {"item_name": "Coin", "chance": 0.5, "min_count": 1, "max_count": 3},
                {"item_name": "Potion", "chance": 0.15, "min_count": 1, "max_count": 1},
                {"item_name": "Ore", "chance": 0.25, "min_count": 1, "max_count": 2},
            ]
        elif enemy_type == "goblin":
            return [
                {"item_name": "Coin", "chance": 0.6, "min_count": 1, "max_count": 2},
                {"item_name": "Flower", "chance": 0.3, "min_count": 1, "max_count": 1},
            ]
        else:
            return [
                {"item_name": "Coin", "chance": 0.5, "min_count": 1, "max_count": 1},
            ]
    
    def drop_loot(self, assets):
        """Generate loot drops when enemy dies."""
        drops = []
        for loot_entry in self.loot_table:
            if random.random() < loot_entry["chance"]:
                count = random.randint(loot_entry["min_count"], loot_entry["max_count"])
                item_name = loot_entry["item_name"]
                
                # Get the actual item object from assets
                item_key = f"{item_name.lower()}_item"
                if item_key in assets:
                    for _ in range(count):
                        drops.append(assets[item_key])
        
        return drops
    # ------------------------
    # Sprite Handling
    # ------------------------
    def update_sprite(self):
        """Update the current sprite based on animation frame and facing direction."""
        # Safety check - need frames to update sprite
        if not self.frames or len(self.frames) == 0:
            return
        
        # Get current animation frame
        frame_idx = self.frame_index % len(self.frames)
        base_frame = self.frames[frame_idx]
        
        # Create the sprite image based on facing direction
        # When facing_right is True: use original sprite (faces right)
        # When facing_right is False: flip sprite horizontally (faces left)
        if self.facing_right:
            self.image = base_frame.copy()
        else:
            # Flip the sprite horizontally to face left
            self.image = pygame.transform.flip(base_frame.copy(), True, False)

    # ------------------------
    # AI + Movement
    # ------------------------
    def update(self, dt, current_time, player_world_rect, obstacles):
        # Animate frames
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % 4
            self.frame_timer = 0

        # Calculate distance and direction to player
        dx = player_world_rect.centerx - self.hitbox.centerx
        dy = player_world_rect.centery - self.hitbox.centery
        distance_to_player = math.hypot(dx, dy)

        # Determine AI state based on distance
        if distance_to_player <= ENEMY_AGGRO_RANGE:
            self.state = "chasing"
            self.target = player_world_rect
        elif distance_to_player > ENEMY_AGGRO_RANGE * 1.5:
            self.state = "idle"
            self.target = None

        # Movement logic
        old_rect = self.rect.copy()
        actual_movement_x = 0  # Track actual horizontal movement this frame

        if self.state == "chasing" and self.target:
            if distance_to_player > ENEMY_ATTACK_RANGE * 0.8:
                # Update facing based on direction to player BEFORE normalizing
                if abs(dx) > 1:
                    new_facing = dx > 0
                    if new_facing != self.facing_right:
                        self.facing_right = new_facing
                
                # Normalize and move
                dx /= distance_to_player
                dy /= distance_to_player
                
                # Apply movement
                move_x = dx * self.speed
                move_y = dy * self.speed
                
                self.rect.x += move_x
                self._resolve_collisions(obstacles, "x", old_rect)
                actual_movement_x = self.rect.x - old_rect.x
                
                self.rect.y += move_y
                self._resolve_collisions(obstacles, "y", old_rect)

        elif self.state == "idle":
            # Change direction periodically
            self.path_timer += dt
            if self.path_timer >= 2000:
                self.random_direction = random.choice(
                    [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
                )
                self.path_timer = 0

            # Get movement direction
            dir_x, dir_y = self.random_direction
            
            # Update facing based on movement direction
            if dir_x != 0:
                new_facing = dir_x > 0
                if new_facing != self.facing_right:
                    self.facing_right = new_facing
            
            # Apply idle movement (slower)
            move_x = dir_x * self.speed * 0.5
            move_y = dir_y * self.speed * 0.5
            
            self.rect.x += move_x
            self._resolve_collisions(obstacles, "x", old_rect)
            actual_movement_x = self.rect.x - old_rect.x
            
            self.rect.y += move_y
            self._resolve_collisions(obstacles, "y", old_rect)

        # Sync hitbox with sprite rect
        self.hitbox.center = self.rect.center
        
        # Update sprite to match current facing direction
        self.update_sprite()

    # ------------------------
    # Collision Helper
    # ------------------------
    def _resolve_collisions(self, obstacles, axis, old_rect):
        """Resolve collisions separately per axis — allows sliding along walls."""
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if axis == "x":
                    if self.rect.centerx > obstacle.centerx:  
                        self.rect.left = obstacle.right
                    else:  
                        self.rect.right = obstacle.left
                elif axis == "y":
                    if self.rect.centery > obstacle.centery:
                        self.rect.top = obstacle.bottom
                    else: 
                        self.rect.bottom = obstacle.top

class EnemySpawnPoint:
    def __init__(self, x, y, enemy_type, respawn_time=25000, check_radius=80):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.respawn_time = respawn_time
        self.last_spawn_time = 0
        self.current_enemy = None
        self.enemy_id = None
        self.check_radius = check_radius

    def can_spawn(self, current_time):
        if self.current_enemy is not None:
            if self.current_enemy in enemies and getattr(self.current_enemy, "is_alive", False):
                return False
            self.current_enemy = None
        return (current_time - self.last_spawn_time) >= self.respawn_time

    def _find_safe_spawn_position(self, obstacles):
        """Find a nearby open tile that doesn't collide with walls or stones."""
        import random
        test_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)

        for _ in range(40):  # Try up to 40 random nearby spots
            dx = random.randint(-self.check_radius, self.check_radius)
            dy = random.randint(-self.check_radius, self.check_radius)
            test_rect.center = (self.x + dx, self.y + dy)

            # Skip if colliding with any obstacle
            if not any(test_rect.colliderect(o) for o in obstacles):
                return test_rect.center

        # No valid open space found
        return None

    def spawn_enemy(self, current_time, obstacles, force=False):
        if not force and not self.can_spawn(current_time):
            return None

        safe_pos = self._find_safe_spawn_position(obstacles)
        if safe_pos is None:
            # couldn't find a safe place — skip spawn for now
            return None

        x, y = safe_pos
        enemy = Enemy(x, y, self.enemy_type, frames=enemy_frames)
        enemy.spawn_point = self
        enemy.is_alive = True

        self.last_spawn_time = current_time
        self.current_enemy = enemy
        self.enemy_id = id(enemy)

        return enemy

    def notify_enemy_death(self, current_time):
        self.current_enemy = None
        self.enemy_id = None
        self.last_spawn_time = current_time


class Boss(Enemy):
    def __init__(self, x, y, boss_data=None):
        # Call Enemy constructor with type "boss"
        super().__init__(x, y, enemy_type="boss")
        
        # Load boss sprite
        try:
            self.image = pygame.image.load("NPC/boss1.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (PLAYER_SIZE * 4, PLAYER_SIZE * 4))
        except Exception as e:
            print("Error loading boss1.png:", e)
            self.image = pygame.Surface((PLAYER_SIZE * 4, PLAYER_SIZE * 4))
            self.image.fill((200, 0, 0))  # Red boss

        # Update rect size to match the larger sprite
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.inflate(-PLAYER_SIZE // 2, -PLAYER_SIZE // 2)

        # Boss stats: can be set from boss_data or use defaults
        if boss_data:
            self.health = int(boss_data.get("health", 300))
            self.max_health = self.health
            self.damage = int(boss_data.get("damage", 40))
            self.name = boss_data.get("name", "Boss")
        else:
            self.health = 300
            self.max_health = 300
            self.damage = 40
            self.name = "Ancient Guardian"

        # Boss-specific stats
        self.experience_reward = 500  # More XP than regular enemies
        self.speed = ENEMY_SPEED * 0.8  # Slightly slower than regular enemies
        
        # Boss phases based on health
        self.phase = 1  # 1, 2, or 3
        self.last_phase_change = 0
        
        # Enhanced aggro range for boss
        self.aggro_range = ENEMY_AGGRO_RANGE * 2
        self.attack_range = ENEMY_ATTACK_RANGE * 1.5
        
        # Boss movement patterns
        self.movement_pattern = "chase"
        self.pattern_timer = 0
        self.circle_angle = 0
        self.retreat_timer = 0

        # Loot table
        self.loot_table = [
                {"item_name": "Coin", "chance": .3, "min_count": 20, "max_count": 30},
                {"item_name": "Potion", "chance": 0.1, "min_count": 2, "max_count": 4},
                {"item_name": "Ore", "chance": 0.1, "min_count": 5, "max_count": 8},
            ]
    def get_current_phase(self):
        """Determine boss phase based on health percentage."""
        health_percent = self.health / self.max_health
        if health_percent > 0.66:
            return 1
        elif health_percent > 0.33:
            return 2
        else:
            return 3

    def change_phase(self, new_phase, current_time):
        """Handle phase transitions with special effects."""
        if new_phase != self.phase:
            old_phase = self.phase
            self.phase = new_phase
            self.last_phase_change = current_time
        
            # Visual feedback for phase change
            floating_texts.append(FloatingText(
                f"Phase {self.phase}!",
                (self.rect.centerx, self.rect.y - 50),
                color=(255, 215, 0), 
                lifetime=2000
            ))
        
            # Phase-specific changes
            if self.phase == 2:
                self.speed = ENEMY_SPEED * 1.0  # Normal speed
                self.special_ability_cooldown = 4000 
                print(f"{self.name} enters Phase 2 - Enhanced Aggression!")
            
            elif self.phase == 3:
                self.speed = ENEMY_SPEED * 1.2 
                self.special_ability_cooldown = 3000  
                self.charge_cooldown = 6000 
                print(f"{self.name} enters Phase 3 - Enraged!")




    def update_movement_pattern(self, dt, current_time, player_world_rect):
        """Enemy AI: idle until player is close, then chase."""
        self.pattern_timer += dt

        # --- Distance check (aggro range) ---
        dx = player_world_rect.centerx - self.rect.centerx
        dy = player_world_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        AGGRO_RADIUS = 250   
        DEAGGRO_RADIUS = 400 

        # Initialize flag if not set
        if not hasattr(self, "is_chasing"):
            self.is_chasing = False

        # Aggro / deaggro logic
        if self.is_chasing:
            if dist > DEAGGRO_RADIUS:
                self.is_chasing = False
        else:
            if dist < AGGRO_RADIUS:
                self.is_chasing = True

        # --- Movement behavior ---
        if self.is_chasing and dist > 0:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = 0
            self.vy = 0

        # --- Apply velocity ---
        self.rect.x += int(self.vx * dt / 16)
        self.rect.y += int(self.vy * dt / 16)



    def update(self, dt, current_time, player_world_rect, obstacles):
        # Update phase based on health
        current_phase = self.get_current_phase()
        if current_phase != self.phase:
            self.change_phase(current_phase, current_time)
    
        # Animate
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % 4
            self.frame_timer = 0

        # Distance and direction to player
        dx = player_world_rect.centerx - self.hitbox.centerx
        dy = player_world_rect.centery - self.hitbox.centery
        distance_to_player = math.hypot(dx, dy)

        # AI state logic
        if distance_to_player <= self.aggro_range:
            self.state = "chasing"
            self.target = player_world_rect
        elif distance_to_player > self.aggro_range * 1.5:
            self.state = "idle"
            self.target = None

        # Movement
        old_rect = self.rect.copy()
    
        if self.state == "chasing" and self.target:
            # Chase the player if not in attack range
            if distance_to_player > self.attack_range * 0.8:
                # Normalize direction
                dx /= distance_to_player
                dy /= distance_to_player
            
                # Move toward player
                self.rect.x += dx * self.speed
                self._resolve_collisions(obstacles, axis="x", old_rect=old_rect)
                self.rect.y += dy * self.speed
                self._resolve_collisions(obstacles, axis="y", old_rect=old_rect)

        elif self.state == "idle":
            # Idle wandering
            self.path_timer += dt
            if self.path_timer >= 3000:
                self.random_direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)])
                self.path_timer = 0

            dx, dy = self.random_direction
            self.rect.x += dx * self.speed * 0.3
            self._resolve_collisions(obstacles, axis="x", old_rect=old_rect)
            self.rect.y += dy * self.speed * 0.3
            self._resolve_collisions(obstacles, axis="y", old_rect=old_rect)

        # Sync hitbox with sprite
        self.hitbox.center = self.rect.center
        
    def attack_player(self, player, current_time):
        """Attack player if in range and cooldown passed."""
        # Handle both Player objects and Rect objects
        if isinstance(player, pygame.Rect):
            player_rect = player
        else:
            player_rect = player.rect
    
        if self.hitbox.colliderect(player_rect):
            if current_time - self.last_attack_time >= ENEMY_ATTACK_COOLDOWN:
                self.last_attack_time = current_time
            
                # If player is a Player object, use its take_damage method
                if hasattr(player, 'take_damage'):
                    player.take_damage(self.damage, current_time)
            
                floating_texts.append(FloatingText(
                    f"-{self.damage}",
                    (player_rect.x, player_rect.y - 20),
                    color=(255, 0, 0)
                ))
                print(f"{self.type} attacked player for {self.damage} damage")
                return True
        return False

    # In your Boss class, move this method to the proper level
    def take_damage(self, damage_amount):
        """Override to add boss-specific damage feedback."""
        old_health = self.health
        self.health -= damage_amount

        floating_texts.append(FloatingText(
            f"-{damage_amount}",
            (self.rect.x, self.rect.y - 15),
            color=(255, 50, 50)
        ))

        # Boss-specific damage feedback
        if self.health > 0:
            # Show percentage of health remaining
            health_percent = int((self.health / self.max_health) * 100)
            floating_texts.append(FloatingText(
                f"{health_percent}%",
                (self.rect.centerx + 30, self.rect.y - 10),
                color=(255, 255, 100),
                lifetime=800
            ))

            # Special reactions to taking damage
            if self.health < self.max_health * 0.5 and old_health >= self.max_health * 0.5:
                floating_texts.append(FloatingText(
                    "You will pay for that!",
                    (self.rect.centerx, self.rect.y - 60),
                    color=(255, 100, 100),
                    lifetime=2000
                ))
        else:
            # Boss death message
            floating_texts.append(FloatingText(
                "The Ancient Guardian falls!",
                (self.rect.centerx, self.rect.y - 50),
                color=(255, 215, 0),
                lifetime=3000
            ))

        return self.health <= 0


class LootDrop:
    def __init__(self, x, y, item, lifetime=10000):
        """
        x, y: world coordinates where loot spawns
        item: Item object
        lifetime: how long (ms) before loot disappears
        """
        self.item = item
        self.rect = pygame.Rect(x, y, 30, 30)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime
        self.bobbing_offset = 0
        self.bobbing_timer = 0
    
    def update(self, dt):
        """Make the loot bob up and down."""
        self.bobbing_timer += dt
        self.bobbing_offset = int(5 * math.sin(self.bobbing_timer / 200.0))
    
    def is_expired(self, current_time):
        return current_time - self.spawn_time > self.lifetime
    
    def draw(self, screen, camera_x, camera_y):
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y + self.bobbing_offset
        
        item_image = pygame.transform.scale(self.item.image, (30, 30))
        screen.blit(item_image, (screen_x, screen_y))
# END OF CLASSES ---------------------------------------------------------------
# ------------------------------------------------------------------------------
# --- HELPERS FOR COORDINATES ---
def get_player_world_rect():
    """Return the player's rectangle in world coordinates."""
    return player_pos.move(map_offset_x, map_offset_y)

def world_to_screen_rect(world_rect):
    """Convert a world rect to screen coordinates."""
    return pygame.Rect(world_rect.x - map_offset_x, world_rect.y - map_offset_y, world_rect.width, world_rect.height)

def find_safe_spawn_position(avoid_rects, spawn_area_rect, entity_size=(PLAYER_SIZE, PLAYER_SIZE)):
    """Find a safe position to spawn an entity avoiding obstacles."""
    for attempt in range(100):
        x = random.randint(spawn_area_rect.x, spawn_area_rect.x + spawn_area_rect.width - entity_size[0])
        y = random.randint(spawn_area_rect.y, spawn_area_rect.y + spawn_area_rect.height - entity_size[1])
        
        test_rect = pygame.Rect(x, y, entity_size[0], entity_size[1])
        
        collision = False
        for obstacle in avoid_rects:
            if test_rect.colliderect(obstacle):
                collision = True
                break
        
        if not collision:
            return (x, y)
    
    # If no safe position found, return center of spawn area
    return (spawn_area_rect.centerx - entity_size[0]//2, spawn_area_rect.centery - entity_size[1]//2)

# MUSIC __________________________________________________________________________
def init_music():
    """Initialize pygame mixer for music playback."""
    try:
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)
        music_volume = 0.5
        pygame.mixer.music.set_volume(music_volume)
        print("Music system initialized successfully")
        return True
    except pygame.error as e:
        print(f"Could not initialize music system: {e}")
        return False

def play_music(music_key, loop=True):
    """Play background music for a specific game area."""
    global current_music
    
    # Don't restart the same music
    if current_music == music_key and pygame.mixer.music.get_busy():
        return
    
    try:
        # Stop current music
        pygame.mixer.music.stop()
        
        # Load and play new music
        if music_key in MUSIC_FILES:
            pygame.mixer.music.load(MUSIC_FILES[music_key])
            loops = -1 if loop else 0
            pygame.mixer.music.play(loops)
            current_music = music_key
            print(f"Playing music: {music_key}")
        else:
            print(f"Music key '{music_key}' not found")
            current_music = None
            
    except pygame.error as e:
        print(f"Could not play music '{music_key}': {e}")
        current_music = None

def stop_music():
    """Stop all background music."""
    global current_music
    pygame.mixer.music.stop()
    current_music = None

def fade_out_music(fade_time_ms=1000):
    """Fade out current music over specified time."""
    global current_music
    pygame.mixer.music.fadeout(fade_time_ms)
    current_music = None

def set_music_volume(volume):
    """Set music volume (0.0 to 1.0)."""
    global music_volume
    music_volume = max(0.0, min(1.0, volume))
    pygame.mixer.music.set_volume(music_volume)
# _______________________________________________________________________________________


def update_camera():
    global map_offset_x, map_offset_y
    margin_x = WIDTH // 4
    margin_y = HEIGHT // 4

    player_world_rect = get_player_world_rect()
    player_world_x = player_world_rect.centerx
    player_world_y = player_world_rect.centery

    if player_world_x - map_offset_x < margin_x:
        map_offset_x = player_world_x - margin_x
    elif player_world_x - map_offset_x > WIDTH - margin_x:
        map_offset_x = player_world_x - (WIDTH - margin_x)
    if player_world_y - map_offset_y < margin_y:
        map_offset_y = player_world_y - margin_y
    elif player_world_y - map_offset_y > HEIGHT - margin_y:
        map_offset_y = player_world_y - (HEIGHT - margin_y)
    if current_level == "zone2":
        clamp_camera_to_zone2()

def handle_pause_menu_input(event, assets, dt):
    """Handle input for the pause menu."""
    global show_pause_menu, pause_menu_selected_option, game_state
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            show_pause_menu = False
        elif event.key == pygame.K_UP:
            pause_menu_selected_option = (pause_menu_selected_option - 1) % 4
        elif event.key == pygame.K_DOWN:
            pause_menu_selected_option = (pause_menu_selected_option + 1) % 4
        elif event.key == pygame.K_RETURN:
            execute_pause_menu_option(assets)
    
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Handle mouse clicks
        for option, rect in pause_button_rects.items():
            if rect.collidepoint(event.pos):
                # Set selection and execute
                if option == "resume":
                    pause_menu_selected_option = 0
                elif option == "save_game":
                    pause_menu_selected_option = 1
                elif option == "main_menu":
                    pause_menu_selected_option = 2
                elif option == "exit_game":
                    pause_menu_selected_option = 3
                execute_pause_menu_option(assets)
                break
    
    elif event.type == pygame.MOUSEMOTION:
        # Handle mouse hover
        for i, (option, rect) in enumerate(pause_button_rects.items()):
            if rect.collidepoint(event.pos):
                if option == "resume":
                    pause_menu_selected_option = 0
                elif option == "save_game":
                    pause_menu_selected_option = 1
                elif option == "main_menu":
                    pause_menu_selected_option = 2
                elif option == "exit_game":
                    pause_menu_selected_option = 3
                break

def execute_pause_menu_option(assets):
    """Execute the selected pause menu option."""
    global show_pause_menu, game_state
    
    if pause_menu_selected_option == 0:
        show_pause_menu = False
    elif pause_menu_selected_option == 1:  # Save Game
        # You can implement save slot selection here or quick save
        if save_game_data(1):  # Quick save to slot 1
            print("Game saved!")
        show_pause_menu = False
    elif pause_menu_selected_option == 2:  # Main Menu
        show_pause_menu = False
        game_state = "main_menu"
    elif pause_menu_selected_option == 3:  # Exit Game
        pygame.quit()
        sys.exit()
def find_nearest_enemy(player_world_rect):
    """Find enemies in the direction the player was moving."""
    attack_range = COMBAT_RANGE * 1.5
    nearest_enemy = None
    min_distance = float('inf')
    
    # Get attack direction from recent movement
    attack_direction = "down" 
    if player_movement_history:
        attack_direction = player_movement_history[-1][0]
    
    # Direction vectors
    direction_map = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0)
    }
    
    if attack_direction not in direction_map:
        attack_direction = "down"
    
    dx, dy = direction_map[attack_direction]
    
    for enemy in enemies:
        # Get distance and direction to enemy
        to_enemy_x = enemy.rect.centerx - player_world_rect.centerx
        to_enemy_y = enemy.rect.centery - player_world_rect.centery
        distance = math.sqrt(to_enemy_x**2 + to_enemy_y**2)
        
        if distance > attack_range:
            continue
            
        # Check if enemy is in the attack direction
        if distance > 0:
            to_enemy_x /= distance
            to_enemy_y /= distance
            
            # Check if enemy is in attack direction (dot product)
            direction_match = (dx * to_enemy_x) + (dy * to_enemy_y)
            
            # Enemy must be somewhat in attack direction
            if direction_match > 0.3 and distance < min_distance:
                nearest_enemy = enemy
                min_distance = distance
    
    return nearest_enemy

# ----------------
# TEXT MAPS/LEVEL DRAW
# ----------------
def load_text_map(filename):
    """Load a map from a text file (supports P2 for zone2 portal)."""
    map_data = {
        'tiles': [],
        'entities': [],
        'spawn_point': (WIDTH // 2, HEIGHT // 2),
        'borders': []
    }

    tile_mapping = {
        'G': 'grass',
        'T': 'tree',
        'S': 'stone',
        'H': 'house',
        'P': 'portal',
        'N': 'npc',
        'M': 'miner',
        'F': 'flower',
        'C': 'carrot', 
        'L': 'leaf',
        '@': 'player_spawn',
        '.': 'grass',
        'B': 'boss1_portal',
        'L': 'lava',
        'W': 'water',     
        'R': 'path',
        'U': 'path2'
    }

    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            for row, line in enumerate(lines):
                line = line.rstrip("\n")

                col = 0
                while col < len(line):
                    # Handle 2-character tokens like "P2"
                    if col + 1 < len(line) and line[col:col+2] == "P2":
                        char = "P2"
                        col += 2
                    else:
                        char = line[col]
                        col += 1

                    x, y = (col - 1) * TILE_SIZE, row * TILE_SIZE

                    if char == '@':
                        map_data['spawn_point'] = (x, y)
                    elif char in ['N', 'M', 'P', 'H']:
                        map_data['entities'].append({
                            'type': tile_mapping[char],
                            'pos': (x, y)
                        })
                    elif char == 'P2':
                        map_data['entities'].append({
                            'type': 'zone2_portal',
                            'pos': (x, y)
                        })
                    elif char == 'T':
                        map_data['borders'].append(pygame.Rect(x + 5, y + 5, TILE_SIZE - 10, TILE_SIZE - 10))
                    elif char == 'S':
                        offset = (TILE_SIZE - (TILE_SIZE // 2)) // 2
                        map_data['tiles'].append({
                            'type': 'stone',
                            'rect': pygame.Rect(x + offset, y + offset, TILE_SIZE // 2, TILE_SIZE // 2)
                        })
                    elif char == 'F':
                        map_data['tiles'].append({
                            'type': 'flower',
                            'pos': (x + 10, y + 10, random.randint(0, 1))
                        })
                    elif char == 'L':
                        map_data['tiles'].append({
                            'type': 'leaf',
                            'pos': (x + random.randint(8, 14), y + random.randint(8, 14))
                        })
                    elif char == 'C':
                        map_data['tiles'].append({
                            'type': 'carrot',
                            'pos': (x + 10, y + 10, random.randint(0, 1))
                        })
                    elif char == 'W':
                        map_data['tiles'].append({
                            'type': 'water',
                            'rect': pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                        })
                    elif char == 'R':
                        map_data['tiles'].append({
                            'type': 'path',
                            'rect': pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                        })
                    elif char == 'U':
                        map_data['tiles'].append({
                            'type': 'path2',
                            'rect': pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                        })
    except FileNotFoundError:
        print(f"Could not load map: {filename}")

    return map_data
def load_zone2_map(filename="Maps/zone2.txt"):
    """Load Zone 2 map from text file."""
    map_data = {
        'tiles': [],
        'entities': [],
        'spawn_point': (5 * TILE_SIZE, 5 * TILE_SIZE),
        'borders': [],
        'crystals': [],
        'water': [],
        'return_portal': None,
        'width': 0,
        'height': 0
    }

    try:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\n') for line in f if not line.startswith('#')]
            map_data['width'] = len(lines[0]) * TILE_SIZE if lines else 0
            map_data['height'] = len(lines) * TILE_SIZE

            for row, line in enumerate(lines):
                for col, char in enumerate(line):
                    x, y = col * TILE_SIZE, row * TILE_SIZE

                    if char == '@':
                        map_data['spawn_point'] = (x, y)
                    elif char == 'P':
                        map_data['return_portal'] = pygame.Rect(x, y, 50, 50)
                    elif char == 'T':
                        map_data['borders'].append(pygame.Rect(x + 5, y + 5, TILE_SIZE - 10, TILE_SIZE - 10))
                    elif char == 'S':
                        offset = (TILE_SIZE - (TILE_SIZE // 2)) // 2
                        map_data['tiles'].append({
                            'type': 'stone',
                            'rect': pygame.Rect(x + offset, y + offset, TILE_SIZE // 2, TILE_SIZE // 2)
                        })
                    elif char == 'C':
                        map_data['crystals'].append(pygame.Rect(x + 10, y + 10, 30, 30))
                    elif char == 'W':
                        map_data['water'].append((x, y))
                    elif char == 'F':
                        map_data['tiles'].append({
                            'type': 'flower',
                            'pos': (x + 10, y + 10, random.randint(0, 1))
                        })
                    elif char == 'L':
                        map_data['tiles'].append({
                            'type': 'leaf',
                            'pos': (x + random.randint(8, 14), y + random.randint(8, 14))
                        })
                    elif char == 'M':
                        map_data['entities'].append({
                            'type': 'merchant',
                            'pos': (x, y)})
    except FileNotFoundError:
        print(f"Could not load zone2 map: {filename}")
        
    return map_data

def handle_zone2_portal_interaction(player_world_rect):
    """Handle entering zone2 from world."""
    global current_level, map_offset_x, map_offset_y, player_pos
    
    if zone2_portal and player_world_rect.colliderect(zone2_portal.inflate(20, 20)):
        current_level = "zone2"
        spawn_point = setup_zone2()
        map_offset_x = spawn_point[0] - WIDTH // 2
        map_offset_y = spawn_point[1] - HEIGHT // 2
        player_pos.center = (WIDTH // 2, HEIGHT // 2)
        print("Entered Zone 2 - The Mystical Realm!")
        return True
    return False
def handle_zone2_return_portal(player_world_rect):
    """Handle returning from zone2 to world."""
    global current_level, map_offset_x, map_offset_y
    
    if zone2_return_portal and player_world_rect.colliderect(zone2_return_portal.inflate(20, 20)):
        current_level = "world"
        # Reload world map
        setup_colliders()
        
        # Spawn near zone2 portal in world
        if zone2_portal:
            spawn_x = zone2_portal.centerx
            spawn_y = zone2_portal.bottom + 50
        else:
            spawn_x = 5 * TILE_SIZE
            spawn_y = 5 * TILE_SIZE
            
        map_offset_x = spawn_x - WIDTH // 2
        map_offset_y = spawn_y - HEIGHT // 2
        player_pos.center = (WIDTH // 2, HEIGHT // 2)
        print("Returned to the main world.")
        return True
    return False

def handle_crystal_mining(player_world_rect, assets):
    """Handle mining crystals in zone2."""
    global is_mining, mining_timer, mining_target_stone
    
    if equipment_slots["weapon"] and equipment_slots["weapon"].name == "Pickaxe":
        for crystal in list(crystal_rects):
            if player_world_rect.colliderect(crystal.inflate(20, 20)):
                is_mining = True
                mining_target_stone = crystal  # Reuse mining system
                mining_timer = 0
                current_direction = "idle"
                return True
    return False


def setup_zone2():
    """Setup Zone 2 with its unique resources and NPCs."""
    global crystal_rects, water_tiles, zone2_merchant_rect, zone2_return_portal
    global tree_rects, stone_rects, flower_tiles, leaf_tiles
    global zone2_width, zone2_height

    map_data = load_zone2_map("Maps/zone2.txt")

    # Clear old data
    tree_rects.clear()
    stone_rects.clear()
    flower_tiles.clear()
    leaf_tiles.clear()
    crystal_rects.clear()
    water_tiles.clear()

    # Apply map data
    tree_rects.extend(map_data['borders'])
    crystal_rects.extend(map_data['crystals'])
    water_tiles.extend(map_data['water'])
    zone2_return_portal = map_data['return_portal']
    zone2_width = map_data['width']
    zone2_height = map_data['height']

    for tile in map_data['tiles']:
        if tile['type'] == 'stone':
            stone_rects.append(tile['rect'])
        elif tile['type'] == 'flower':
            flower_tiles.append(tile['pos'])
        elif tile['type'] == 'leaf':
            leaf_tiles.append(tile['pos'])

    for entity in map_data['entities']:
        if entity['type'] == 'merchant':
            zone2_merchant_rect = pygame.Rect(entity['pos'][0], entity['pos'][1], PLAYER_SIZE, PLAYER_SIZE)

    return map_data['spawn_point']
def load_boss_room_map(boss_room):
    data = {
        "walls": [],
        "ore_deposits": [],
        "boss_portal": None,
        "exit_point": None,
        "spawn_point": (5 * TILE_SIZE, 5 * TILE_SIZE),
        "boss_spawn": None 
    }
    with open(boss_room, "r") as f:
        lines = [line.rstrip("\n") for line in f]
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            world_x = x * TILE_SIZE
            world_y = y * TILE_SIZE
            if char == "#":
                data["walls"].append(pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE))
            elif char == "O":
                data["ore_deposits"].append(pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE))
            elif char == "B":
                data["boss_portal"] = pygame.Rect(world_x, world_y, TILE_SIZE * 2, TILE_SIZE * 2)
            elif char == "P":
                data["exit_point"] = pygame.Rect(world_x, world_y, TILE_SIZE, TILE_SIZE)
            elif char == "S":
                data["spawn_point"] = (world_x, world_y)
            elif char == "b": 
                data["boss_spawn"] = (world_x, world_y)
    return data

def setup_boss_room(filename="Maps/boss_room.txt"):
    global boss_room_walls, stone_rects, boss1_portal, dungeon_exit, enemies, boss_enemy

    boss_room_walls.clear()
    stone_rects.clear()
    enemies.clear()
    boss1_portal = None
    dungeon_exit = None
    boss_enemy = None

    map_data = load_boss_room_map(filename)

    boss_room_walls.extend(map_data["walls"])
    stone_rects.extend(map_data["ore_deposits"])
    boss1_portal = map_data["boss_portal"]
    dungeon_exit = map_data["exit_point"]

    # Spawn boss if marker exists
    if map_data["boss_spawn"]:
        spawn_x, spawn_y = map_data["boss_spawn"]
        boss_enemy = Boss(spawn_x, spawn_y)
        enemies.append(boss_enemy)
        print("Boss created at:", spawn_x, spawn_y)
        print("Enemies list:", enemies)

    # Return player spawn point
    spawn_x, spawn_y = map_data["spawn_point"]
    return (spawn_x, spawn_y)

def update_enemy_spawns(obstacles=None):
    """Handles enemy respawning for the current dungeon level, ensuring no wall clipping."""
    if current_level != "dungeon":
        return

    current_time = pygame.time.get_ticks()
    total_before = len(enemies)
    spawned_count = 0

    for sp in enemy_spawn_points:
        # Clean up invalid or dead enemy references
        if sp.current_enemy and sp.current_enemy not in enemies:
            print(f"[CLEANUP] Removed dead {sp.enemy_type} from spawn ({sp.x}, {sp.y})")
            sp.current_enemy = None

        # Try respawning if the slot is empty
        if sp.current_enemy is None:
            # Pass obstacle list if available (prevents wall clipping)
            enemy = sp.spawn_enemy(current_time, obstacles or [])
            if enemy:
                enemies.append(enemy)
                sp.current_enemy = enemy
                spawned_count += 1
                print(f"[SPAWN] {enemy.type} at {enemy.rect.topleft}")

    total_after = len(enemies)
    if spawned_count > 0:
        print(f"[ENEMY SPAWNS] +{spawned_count} (Total: {total_after})")

    return spawned_count

def load_dungeon_map_with_enemies(dungeon1):
    global enemy_spawn_points  

    map_data = {
        'walls': [],
        'ore_deposits': [],
        'spawn_point': (5 * TILE_SIZE, 5 * TILE_SIZE),
        'exit_point': None,
        'boss_portal': None,
        'enemy_spawns': []
    }

    tile_mapping = {
        '#': 'wall',
        'O': 'ore',
        '@': 'player_spawn',
        'B': 'boss_portal',
        'E': 'exit',
        '.': 'floor',
        'e': 'enemy_orc',
        'g': 'enemy_goblin',
        's': 'enemy_strong',
    }
    with open(dungeon1, 'r') as f:
        lines = [line.rstrip("\n") for line in f]  # ✅ keep spacing

    for row, line in enumerate(lines):
        for col, char in enumerate(line):
            x, y = col * TILE_SIZE, row * TILE_SIZE

            if char == '@':
                map_data['spawn_point'] = (x, y)

            elif char == 'E':
                map_data['exit_point'] = pygame.Rect(x, y, TILE_SIZE * 2, TILE_SIZE * 2)

            elif char == '#':
                map_data['walls'].append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))

            elif char == 'O':
                map_data['ore_deposits'].append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))  # ✅ full tile

            elif char == 'B':
                map_data['boss_portal'] = pygame.Rect(x, y, TILE_SIZE * 2, TILE_SIZE * 2)

            # === Enemy spawns (only valid on non-wall tiles) ===
            elif char == 'e':
                sp = EnemySpawnPoint(x, y, "orc", respawn_time=30000)
                map_data['enemy_spawns'].append(sp)


            elif char == 's':
                sp = EnemySpawnPoint(x, y, "orc_strong", respawn_time=45000)
                map_data['enemy_spawns'].append(sp)

            elif char == 'g':
                sp = EnemySpawnPoint(x, y, "goblin", respawn_time=20000)
                map_data['enemy_spawns'].append(sp)


    return map_data


def apply_map_data(map_data):
    """Apply loaded map data to game globals."""
    global tree_rects, house_list, stone_rects, flower_tiles, leaf_tiles, carrot_tiles
    global npc_rect, miner_npc_rect, dungeon_portal, player_pos, map_offset_x, map_offset_y
    global boss1_portal
    global zone2_portal

    # Clear existing data
    tree_rects.clear()
    house_list.clear() 
    stone_rects.clear()
    flower_tiles.clear()
    leaf_tiles.clear()
    carrot_tiles.clear()
    # Apply borders (trees)
    tree_rects.extend(map_data['borders'])
    
    # Apply tiles
    for tile in map_data['tiles']:
        if tile['type'] == 'stone':
            stone_rects.append(tile['rect'])
        elif tile['type'] == 'flower':
            flower_tiles.append(tile['pos'])
        elif tile['type'] == 'leaf':
            leaf_tiles.append(tile['pos'])
        elif tile['type'] == 'water':  
            water_tiles.append(tile['rect'])
        elif tile['type'] == 'path': 
            path_tiles.append(tile['rect'])
        elif tile['type'] == 'carrot':
            carrot_tiles.append(tile['pos'])
        elif tile['type'] == 'path2':
            path2_tiles.append(tile['rect'])
    # Apply entities
    for entity in map_data['entities']:
        x, y = entity['pos']
        if entity['type'] == 'house':
            house_rect = pygame.Rect(x, y, TILE_SIZE * 2, TILE_SIZE * 2)
            house_list.append(house_rect)
            tree_rects.append(house_rect)  # Houses are also collision objects
        elif entity['type'] == 'portal':
            dungeon_portal = pygame.Rect(x, y, 50, 50)
            tree_rects.append(dungeon_portal)
        elif entity['type'] == 'zone2_portal':
            zone2_portal = pygame.Rect(x, y, 50, 50)
            tree_rects.append(zone2_portal)
        elif entity['type'] == 'boss1_portal':
            boss1_portal = pygame.Rect(x, y, 50, 50)
            tree_rects.append(boss1_portal)
        elif entity['type'] == 'npc':
            npc_rect = pygame.Rect(x, y, PLAYER_SIZE * 4, PLAYER_SIZE * 4)
        elif entity['type'] == 'miner':
            miner_npc_rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
    
    # Set player spawn position
    spawn_x, spawn_y = map_data['spawn_point']
    map_offset_x = spawn_x - WIDTH // 2
    map_offset_y = spawn_y - HEIGHT // 2
    player_pos.center = (WIDTH // 2, HEIGHT // 2)
def create_default_map_data():
    """Create default map if file loading fails."""
    return {
        'tiles': [],
        'entities': [],
        'spawn_point': (WIDTH // 2, HEIGHT // 2),
        'borders': []
    }
# --- INIT ---
def init():
    """Initializes Pygame and sets up the screen."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("First RPG - MW 09/25")
    
    # Initialize music system
    init_music()
    
    return screen, pygame.time.Clock()  

def load_player_frames():
    """Loads and scales the player character frames."""
    try:
        sheet = pygame.image.load("NPC/Player.PNG").convert_alpha()
    except pygame.error:
        # Create fallback player frames
        sheet = pygame.Surface((128, 128))
        sheet.fill((0, 100, 200))
    
    frames = {}
    try:
        right_frames = [pygame.transform.scale(sheet.subsurface(pygame.Rect(col * 32, 32, 32, 32)), (PLAYER_SIZE, PLAYER_SIZE)) for col in range(COLS)]
        frames["right"] = right_frames
        frames["left"] = [pygame.transform.flip(frame, True, False) for frame in right_frames]
        frames["up"] = [pygame.transform.scale(sheet.subsurface(pygame.Rect(col * 32, 64, 32, 32)), (PLAYER_SIZE, PLAYER_SIZE)) for col in range(COLS)]
        frames["down"] = [pygame.transform.scale(sheet.subsurface(pygame.Rect(col * 32, 96, 32, 32)), (PLAYER_SIZE, PLAYER_SIZE)) for col in range(COLS)]
        frames["idle"] = [pygame.transform.scale(sheet.subsurface(pygame.Rect(0, 0, 32, 32)), (PLAYER_SIZE, PLAYER_SIZE))]
    except:
        # Fallback frames
        fallback_frame = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        fallback_frame.fill((0, 100, 200))
        frames = {
            "right": [fallback_frame],
            "left": [fallback_frame],
            "up": [fallback_frame],
            "down": [fallback_frame],
            "idle": [fallback_frame]
        }
    return frames

# NEEDS WORK
def save_game_data(slot_number):
    """Save current game state to a file."""
    save_data = {
        'player': {
            'level': player.level,
            'health': player.health,
            'max_health': player.max_health,
            'damage': player.damage,
            'experience': player.experience,
            'experience_to_next': player.experience_to_next,
            'position': {'x': player_pos.x, 'y': player_pos.y}
        },
        'world': {
            'current_level': current_level,
            'map_offset_x': map_offset_x,
            'map_offset_y': map_offset_y
        },
        'inventory': [[{'name': item.name, 'count': item.count, 'category': item.category, 'damage': item.damage} if item else None 
                      for item in row] for row in inventory],
        'equipment': {
            'weapon': {'name': equipment_slots['weapon'].name, 'category': equipment_slots['weapon'].category, 'damage': equipment_slots['weapon'].damage} if equipment_slots['weapon'] else None
        },
        'quests': {
            'npc_quest_active': npc_quest_active,
            'npc_quest_completed': npc_quest_completed,
            'miner_quest_active': miner_quest_active,
            'miner_quest_completed': miner_quest_completed
        },
        'timestamp': pygame.time.get_ticks()
    }
    
    try:
        with open(f"save_slot_{slot_number}.json", 'w') as f:
            json.dump(save_data, f, indent=2)
        print(f"Game saved to slot {slot_number}")
        return True
    except Exception as e:
        print(f"Failed to save: {e}")
        return False

# NEEDS WORK
def load_game_data(slot_number):
    """Load game state from a file."""
    try:
        with open(f"save_slot_{slot_number}.json", 'r') as f:
            save_data = json.load(f)
        
        # Restore player data
        player.level = save_data['player']['level']
        player.health = save_data['player']['health']
        player.max_health = save_data['player']['max_health']
        player.damage = save_data['player']['damage']
        player.experience = save_data['player']['experience']
        player.experience_to_next = save_data['player']['experience_to_next']
        
        # Restore world state
        global current_level, map_offset_x, map_offset_y, player_pos
        current_level = save_data['world']['current_level']
        map_offset_x = save_data['world']['map_offset_x']
        map_offset_y = save_data['world']['map_offset_y']
        player_pos.x = save_data['player']['position']['x']
        player_pos.y = save_data['player']['position']['y']
        
        # Restore inventory
        global inventory
        for row in range(4):
            for col in range(4):
                item_data = save_data['inventory'][row][col]
                if item_data:
                    # You'll need to recreate the item with proper image
                    inventory[row][col] = recreate_item_from_data(item_data)
                else:
                    inventory[row][col] = None
        
        # Restore equipment
        weapon_data = save_data['equipment']['weapon']
        if weapon_data:
            equipment_slots['weapon'] = recreate_item_from_data(weapon_data)
        else:
            equipment_slots['weapon'] = None
            
        # Restore quest states
        global npc_quest_active, npc_quest_completed, miner_quest_active, miner_quest_completed
        npc_quest_active = save_data['quests']['npc_quest_active']
        npc_quest_completed = save_data['quests']['npc_quest_completed']
        miner_quest_active = save_data['quests']['miner_quest_active']
        miner_quest_completed = save_data['quests']['miner_quest_completed']
        
        print(f"Game loaded from slot {slot_number}")
        return True
        
    except FileNotFoundError:
        print(f"No save file found in slot {slot_number}")
        return False
    except Exception as e:
        print(f"Failed to load save: {e}")
        return False

# NEEDS WORK
def recreate_item_from_data(item_data):
    """Recreate an Item object from saved data."""
    # need access to access assets to get the proper image
    return Item(item_data['name'], None, item_data['count'], item_data['category'], item_data['damage'])

# NEEDS WORK
def load_save_slots():
    """Check which save slots have data."""
    global save_slots
    for i in range(4):
        try:
            with open(f"save_slot_{i+1}.json", 'r') as f:
                save_data = json.load(f)
                save_slots[i] = {
                    'level': save_data['player']['level'],
                    'timestamp': save_data['timestamp']
                }
        except:
            save_slots[i] = None

def start_new_game():
    """Initialize a new game with default values."""
    global current_level, map_offset_x, map_offset_y, player_pos
    global inventory, equipment_slots, npc_quest_active, npc_quest_completed
    global miner_quest_active, miner_quest_completed
    
    # Reset player
    player.level = 1
    player.health = PLAYER_MAX_HEALTH
    player.max_health = PLAYER_MAX_HEALTH
    player.damage = PLAYER_BASE_DAMAGE
    player.defense = PLAYER_BASE_DEFENSE
    player.experience = 0
    player.experience_to_next = 100
    
    # Reset world
    current_level = "world"
    map_offset_x = 0
    map_offset_y = 0
    player_pos.center = (WIDTH // 2, HEIGHT // 2)
    
    # Reset inventory and equipment
    inventory = [[None for _ in range(4)] for _ in range(4)]
    equipment_slots = {
    "weapon": None,
    "helmet": None, 
    "armor": None,
    "boots": None,
    "ring1": None,
    "ring2": None,
    "amulet": None,
    "shield": None
}
    
    # Reset quests
    npc_quest_active = False
    npc_quest_completed = False
    miner_quest_active = False
    miner_quest_completed = False

def load_chopping_frames():
    """Loads and scales the chopping animation frames."""
    try:
        sheet = pygame.image.load("NPC/Player.PNG").convert_alpha()
        chopping_frames = {}
        chopping_frames["right"] = [pygame.transform.scale(sheet.subsurface(pygame.Rect(col * 32, 224, 32, 32)), (PLAYER_SIZE, PLAYER_SIZE)) for col in range(4)]
        chopping_frames["left"] = [pygame.transform.flip(frame, True, False) for frame in chopping_frames["right"]]
        chopping_frames["up"] = [pygame.transform.scale(sheet.subsurface(pygame.Rect(col * 32, 255, 32, 32)), (PLAYER_SIZE, PLAYER_SIZE)) for col in range(4)]
        chopping_frames["down"] = [pygame.transform.scale(sheet.subsurface(pygame.Rect(col * 32, 190, 32, 32)), (PLAYER_SIZE, PLAYER_SIZE)) for col in range(4)]
    except:
        # Fallback chopping frames
        fallback_frame = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        fallback_frame.fill((200, 100, 0))
        chopping_frames = {
            "right": [fallback_frame],
            "left": [fallback_frame],
            "up": [fallback_frame],
            "down": [fallback_frame]
        }
    return chopping_frames

def load_attack_frames():
    """Loads attack frames from Player_action.png sheet."""
    try:
        sheet = pygame.image.load("NPC/Player_action.png").convert_alpha()
        cell_size = 32
        attack_frames = {"down": [], "right": [], "left": [], "up": []}

        # --- Down attack (row 0, col 1) ---
        rect = pygame.Rect(1 * cell_size, 0 * cell_size, cell_size, cell_size)
        down = sheet.subsurface(rect)
        attack_frames["down"].append(pygame.transform.scale(down, (PLAYER_SIZE, PLAYER_SIZE)))

        # --- Right attack (row 1, col 1) ---
        rect = pygame.Rect(1 * cell_size, 1 * cell_size, cell_size, cell_size)
        right = sheet.subsurface(rect)
        right_scaled = pygame.transform.scale(right, (PLAYER_SIZE, PLAYER_SIZE))
        left_scaled = pygame.transform.flip(right_scaled, True, False)
        attack_frames["right"].append(right_scaled)
        attack_frames["left"].append(left_scaled)

        # --- Up attack (row 2, col 1) ---
        rect = pygame.Rect(1 * cell_size, 2 * cell_size, cell_size, cell_size)
        up = sheet.subsurface(rect)
        attack_frames["up"].append(pygame.transform.scale(up, (PLAYER_SIZE, PLAYER_SIZE)))

        # Pad each with duplicates so you can animate smoother
        for key in attack_frames:
            attack_frames[key] = attack_frames[key] * 4  # repeat to make 4 frames

    except Exception as e:
        print("Error loading attack frames:", e)
        fallback = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        fallback.fill((255, 0, 0))
        attack_frames = {
            "down": [fallback] * 4,
            "right": [fallback] * 4,
            "left": [fallback] * 4,
            "up": [fallback] * 4
        }

    return attack_frames




def load_enemy_frames():
    """Load and scale all enemy animation frames."""
    frames = {}

    try:
        # --- ORC FRAMES ---
        orc_sheet = pygame.image.load("NPC/orc-attack01.png").convert_alpha()
        total_frames = 6
        frame_width = orc_sheet.get_width() // total_frames
        frame_height = orc_sheet.get_height()

        orc_frames = []
        for i in range(total_frames):
            frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
            frame_surface = frame_rect_to_surface(orc_sheet, frame_rect)
            frame_surface = pygame.transform.scale(frame_surface, (PLAYER_SIZE * 4, PLAYER_SIZE * 4))
            orc_frames.append(frame_surface)

        frames["orc"] = orc_frames

    except Exception as e:
        print("Error loading orc frames:", e)
        # Fallback brown squares if sprite sheet fails
        fallback_frame = pygame.Surface((PLAYER_SIZE * 4, PLAYER_SIZE * 4))
        fallback_frame.fill((139, 69, 19))
        frames["orc"] = [fallback_frame] * 4


    print("Enemy frames loaded:", {etype: len(flist) for etype, flist in frames.items()})
    return frames

def frame_rect_to_surface(sheet, rect):
    """Helper to extract a subsurface safely."""
    return sheet.subsurface(rect).copy()

# LOAD ASSETS --------------------------------------------------------------------
def load_assets():
    """Loads all game assets, items, NPCs, UI icons, tiles, and boss room assets."""

    # --- Utility ---
    def create_fallback_surface(size, color):
        surf = pygame.Surface(size)
        surf.fill(color)
        return surf

    def try_load_image(path, size=None, color=(255, 0, 255)):
        """Tries to load an image; falls back to colored surface if missing."""
        try:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        except:
            return create_fallback_surface(size if size else (32, 32), color)

    # --- Tiles ---
    grass_image = try_load_image(os.path.join("Tiles", "grass_middle.png"), (TILE_SIZE, TILE_SIZE), (34, 139, 34))
    tree_image = try_load_image(os.path.join("Tiles", "tree.png"), (TILE_SIZE + 5, TILE_SIZE + 5), (101, 67, 33))
    water_image = try_load_image(os.path.join("water_middle.png"), (TILE_SIZE, TILE_SIZE), (50, 100, 200))
    path_image = try_load_image(os.path.join("Tiles", "path_middle.png"), (TILE_SIZE, TILE_SIZE), (139, 90, 43))
    path2_image = try_load_image(os.path.join("Tiles", "path2_middle.png"), (TILE_SIZE, TILE_SIZE), (160, 82, 45))
    house_image = try_load_image(os.path.join("Tiles", "house.png"), (TILE_SIZE * 2, TILE_SIZE * 2), (139, 69, 19))
    house1_image = try_load_image(os.path.join("Tiles", "house1.png"), (TILE_SIZE * 2, TILE_SIZE * 2), (160, 82, 45))
    house2_image = try_load_image(os.path.join("Tiles", "house2.png"), (TILE_SIZE * 2, TILE_SIZE * 2), (205, 133, 63))
    backofhouse_image = try_load_image(os.path.join("Tiles", "backofhouse1.png"), (TILE_SIZE * 2, TILE_SIZE * 2), (139, 69, 19))
    # --- Outdoor Stuff (sheet) ---
    try:
        sheet = pygame.image.load("Items/OutdoorStuff.PNG").convert_alpha()
        flower_positions = [(0, 144), (16, 144)]
        flower_images = [
            pygame.transform.scale(sheet.subsurface(pygame.Rect(x, y, 16, 16)), (30, 30))
            for (x, y) in flower_positions
        ]
        leaf_image = pygame.transform.scale(sheet.subsurface(pygame.Rect(0, 0, 16, 16)), (25, 25))
        log_image = pygame.transform.scale(sheet.subsurface(pygame.Rect(4, 110, 24, 24)), (TILE_SIZE, TILE_SIZE))
    except:
        flower_images = [
            create_fallback_surface((30, 30), (255, 192, 203)),
            create_fallback_surface((30, 30), (255, 20, 147))
        ]
        leaf_image = create_fallback_surface((25, 25), (34, 139, 34))
        log_image = create_fallback_surface((TILE_SIZE, TILE_SIZE), (139, 69, 19))

    # --- Items ---
    potion_image = try_load_image(os.path.join("Items", "PotionR.png"), (TILE_SIZE, TILE_SIZE), (150, 0, 150))
    potion2_image = try_load_image(os.path.join("Items", "PotionB.png"), (TILE_SIZE, TILE_SIZE), (0, 0, 255))
    coin_image = try_load_image(os.path.join("Items", "Coin.png"), (TILE_SIZE, TILE_SIZE), (255, 215, 0))
    sword_image = try_load_image(os.path.join("Items", "sword1.png"), (TILE_SIZE, TILE_SIZE), (192, 192, 192))
    axe_image = try_load_image(os.path.join("Items", "axe.png"), (TILE_SIZE, TILE_SIZE), (139, 69, 19))
    pickaxe_image = try_load_image(os.path.join("Items", "pickaxe.png"), (TILE_SIZE, TILE_SIZE), (105, 105, 105))
    stone_image = try_load_image(os.path.join("Items", "stone.png"), (TILE_SIZE // 2, TILE_SIZE // 2), (150, 150, 150))
    ore_image = try_load_image(os.path.join("Items", "ore.png"), (TILE_SIZE // 2, TILE_SIZE // 2), (139, 69, 19))
    chest_image = try_load_image(os.path.join("Items", "chest.png"), (TILE_SIZE, TILE_SIZE), (139, 69, 19))
    helmet_image = try_load_image(os.path.join("Items", "helmet.png"), (TILE_SIZE, TILE_SIZE), (105, 105, 105))
    boots_image = try_load_image(os.path.join("Items", "boots.png"), (TILE_SIZE, TILE_SIZE), (101, 67, 33))
    carrot_tile_image = try_load_image(os.path.join("Tiles", "carrot.png"), (30, 30), (255, 140, 0))  # For world tiles
    carrot_item_image = try_load_image(os.path.join("Items", "carrot_item.png"), (TILE_SIZE, TILE_SIZE), (255, 140, 0))  # For inventory
    crystal_image = try_load_image(os.path.join("Items", "crystal.png"), (TILE_SIZE, TILE_SIZE), (0, 255, 255))
    # --- UI Icons ---
    backpack_icon = try_load_image(os.path.join("GUI/bag.png"), (ICON_SIZE, ICON_SIZE), (101, 67, 33))
    crafting_icon = try_load_image(os.path.join("GUI/craft.png"), (ICON_SIZE, ICON_SIZE), (160, 82, 45))
    equipment_icon = try_load_image(os.path.join("GUI/equipped.png"), (ICON_SIZE, ICON_SIZE), (105, 105, 105))
    quest_icon = try_load_image(os.path.join("GUI/quest.png"), (ICON_SIZE, ICON_SIZE), (255, 215, 0))


    # --- NPCs ---
    try:
        soldier_sheet = pygame.image.load(os.path.join("NPC/soldier.png")).convert_alpha()
        npc_image = pygame.transform.scale(
            soldier_sheet.subsurface(pygame.Rect(0, 0, 100, 100)),
            (PLAYER_SIZE * 4, PLAYER_SIZE * 4)
        )
    except:
        npc_image = create_fallback_surface((PLAYER_SIZE * 4, PLAYER_SIZE * 4), (255, 255, 0))

    try:
        miner_sheet = pygame.image.load("NPC/npc1.png").convert_alpha()
        frame_width = miner_sheet.get_width() // 8
        frame_height = miner_sheet.get_height()
        miner_image = pygame.transform.scale(
            miner_sheet.subsurface(pygame.Rect(0, 0, frame_width, frame_height)),
            (PLAYER_SIZE, PLAYER_SIZE)
        )
    except:
        miner_image = create_fallback_surface((PLAYER_SIZE, PLAYER_SIZE), (160, 82, 45))

    # --- Portal & Dungeon ---
    boss1_portal = try_load_image("Tiles/boss1_portal.png", (50, 50), (128, 0, 128))
    portal_image = try_load_image("Tiles/cave.png", (50, 50), (64, 0, 128))
    zone2_portal = try_load_image("Tiles/zone2_portal.png", (50, 50), (0, 128, 128))
    dungeon_wall_image = try_load_image("Tiles/wall.png", (TILE_SIZE, TILE_SIZE), (64, 64, 64))
    dungeon_floor_image = try_load_image("Tiles/caveFloor.png", (TILE_SIZE, TILE_SIZE), (32, 32, 32))

    # --- Interiors ---
    try:
        interiors = [
            pygame.transform.scale(pygame.image.load("Maps/indoor2.png").convert_alpha(), (WIDTH, HEIGHT)),
            pygame.transform.scale(pygame.image.load("Maps/indoor3.png").convert_alpha(), (WIDTH, HEIGHT))
        ]
    except:
        interiors = [
            create_fallback_surface((WIDTH, HEIGHT), (101, 67, 33)),
            create_fallback_surface((WIDTH, HEIGHT), (139, 69, 19))
        ]

    # --- Items as objects ---
    log_item = Item("Log", log_image)
    axe_item = Item("Axe", axe_image, category="Weapon", damage=20)
    pickaxe_item = Item("Pickaxe", pickaxe_image, category="Weapon", damage=15)
    sword_item = Item("Sword", sword_image, category="Weapon", damage=30)
    stone_item = Item("Stone", stone_image)
    ore_item = Item("Ore", ore_image)
    flower_item = Item("Flower", flower_images[0])
    potion2_item = Item("Speed Potion", potion2_image)
    potion_item = Item("Potion", potion_image)
    coin_item = Item("Coin", coin_image)
    chest_item = Item("Chest Armor", chest_image, category="Armor", damage=0, defense=10)
    helmet_item = Item("Helmet", helmet_image, category="Helmet", damage=0, defense=5)
    boots_item = Item("Boots", boots_image, category="Boots", damage=0, defense=5)
    carrot_item = Item("Carrot", carrot_item_image)
    crystal_item = Item("Crystal", crystal_image)
    # --- Boss Door Frames ---
    boss_door_frames = load_boss_door_frames()

    # --- Build dictionary ---
    assets = {
        # Tiles
        "grass": grass_image,
        "tree": tree_image,
        "house": house_image,
        "house1": house1_image,
        "house2": house2_image,
        "backofhouse": backofhouse_image,
        "interiors": interiors,
        "flowers": flower_images,
        "leaf": leaf_image,
        "water": water_image,
        "path": path_image,
        "path2": path2_image,
        "carrot_tile": carrot_tile_image,
        # Portal / Dungeon
        "boss1_portal": boss1_portal,
        "portal": portal_image,
        "dungeon_wall": dungeon_wall_image,
        "dungeon_floor": dungeon_floor_image,
        "zone2_portal": zone2_portal,
        # Fonts
        "font": pygame.font.SysFont(None, 36),
        "small_font": pygame.font.SysFont(None, 24),
        "large_font": pygame.font.SysFont(None, 48),

        # UI
        "backpack_icon": backpack_icon,
        "crafting_icon": crafting_icon,
        "equipment_icon": equipment_icon,
        "quest_icon": quest_icon,
        # Items
        "log_item": log_item,
        "axe_item": axe_item,
        "pickaxe_item": pickaxe_item,
        "stone_item": stone_item,
        "ore_item": ore_item,
        "stone_img": stone_image,
        "ore_img": ore_image,
        "flower_item": flower_item,
        "potion_item": potion_item,
        "potion2_item": potion2_item,
        "coin_item": coin_item,
        "sword_item": sword_item,
        "chest_item": chest_item,
        "helmet_item": helmet_item,
        "boots_item": boots_item,
        "carrot_item": carrot_item,
        "crystal_item": crystal_item,   
        # NPCs
        "npc_image": npc_image,
        "miner_image": miner_image,

        # Boss
        "boss_door_frames": boss_door_frames,
    }
    try:
        chop_sound = pygame.mixer.Sound("audio/chop.mp3")
        chop_sound.set_volume(SFX_VOLUME)
        print("Loaded chop.mp3 successfully")
    except pygame.error as e:
        print(f"Could not load chop.mp3: {e}")
        chop_sound = None

    try:
        mine_sound = pygame.mixer.Sound("audio/mine.mp3")
        mine_sound.set_volume(SFX_VOLUME)
        print("Loaded mine.mp3 successfully")
    except pygame.error as e:
        print(f"Could not load mine.mp3: {e}")
        mine_sound = None

    assets["chop_sound"] = chop_sound
    assets["mine_sound"] = mine_sound

    return assets
def load_boss_door_frames():
    """Load the boss door frames from the sprite sheet."""
    try:
        door_sheet = pygame.image.load("Tiles/boss1_portal.png").convert_alpha()
        frame_width = door_sheet.get_width() // 12
        frame_height = door_sheet.get_height()

        closed_door_rect = pygame.Rect(0, 0, frame_width, frame_height)
        closed_door_frame = door_sheet.subsurface(closed_door_rect).copy()

        door_size = (TILE_SIZE * 2, TILE_SIZE * 2)
        closed_door_scaled = pygame.transform.scale(closed_door_frame, door_size)

        return {
            "closed": closed_door_scaled,
            "frame_width": frame_width,
            "frame_height": frame_height
        }
    except:
        fallback_door = pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2))
        fallback_door.fill((100, 50, 150))
        return {
            "closed": fallback_door,
            "frame_width": 64,
            "frame_height": 64
        }



    # Interior images
    try:
        interiors = [
            pygame.transform.scale(pygame.image.load("Maps/indoor2.png").convert_alpha(), (WIDTH, HEIGHT)),
            pygame.transform.scale(pygame.image.load("Maps/indoor3.png").convert_alpha(), (WIDTH, HEIGHT))
        ]
    except:
        interior1 = create_fallback_surface((WIDTH, HEIGHT), (101, 67, 33))
        interior2 = create_fallback_surface((WIDTH, HEIGHT), (139, 69, 19))
        interiors = [interior1, interior2]
def setup_indoor_colliders():
    """Set up collision boundaries for indoor areas."""
    global indoor_colliders
    indoor_colliders[:] = [
        pygame.Rect(0, 0, WIDTH, 100),           # top
        pygame.Rect(0, HEIGHT-10, WIDTH, 10),   # bottom
        pygame.Rect(0, 0, 10, HEIGHT),          # left
        pygame.Rect(WIDTH-10, 0, 10, HEIGHT)    # right
    ]

def setup_dungeon_with_enemy_spawns(filename="Maps/dungeon1.txt"):
    global dungeon_walls, stone_rects, boss1_portal, dungeon_exit, enemies, enemy_spawn_points, enemy_frames

    print(f"Setting up dungeon: {filename}")

    map_data = load_dungeon_map_with_enemies(filename)

    dungeon_walls.clear()
    stone_rects.clear()
    enemy_spawn_points.clear()
    enemies.clear()

    dungeon_walls.extend(map_data['walls'])
    stone_rects.extend(map_data['ore_deposits'])
    dungeon_exit = map_data['exit_point']
    enemy_spawn_points.extend(map_data['enemy_spawns'])
    boss1_portal = map_data.get('boss_portal')

    print(f"Dungeon setup complete: {len(enemy_spawn_points)} enemy spawn points found")

    # ✅ Spawn enemies with animation frames
    for sp in enemy_spawn_points:
        try:
            enemy = Enemy(sp.x, sp.y, sp.enemy_type, enemy_frames)

            # Skip if no valid sprite frames (red square fallback)
            if not enemy.frames or len(enemy.frames) == 0:
                print(f"[SKIPPED] No frames for '{sp.enemy_type}' at ({sp.x}, {sp.y})")
                continue

            enemies.append(enemy)
            sp.current_enemy = enemy
            print(f"[SPAWNED] {enemy.type} at ({sp.x}, {sp.y})")

        except Exception as e:
            print(f"[ERROR] Could not spawn enemy at spawn point: {e}")


    spawn_x, spawn_y = map_data['spawn_point']
    spawn_x += 100
    spawn_x = max(2 * TILE_SIZE, min(spawn_x, (DUNGEON_SIZE - 3) * TILE_SIZE))
    spawn_y = max(2 * TILE_SIZE, min(spawn_y, (DUNGEON_SIZE - 3) * TILE_SIZE))

    return (spawn_x, spawn_y)




def setup_colliders():
    """Generates the world colliders for the current level."""
    global tree_rects, house_list, indoor_colliders, flower_tiles, leaf_tiles, stone_rects
    global npc_rect, dungeon_portal, miner_npc_rect
    global zone2_portal

    if current_level == "world":
        # Try to load current map, fallback to procedural generation
        if hasattr(setup_colliders, 'current_map'):
            map_data = load_text_map(setup_colliders.current_map)
            apply_map_data(map_data)
        else:
            # Try to load default map, fallback to generated world
            try:
                map_data = load_text_map("Maps/forest.txt")
                if map_data and (map_data['tiles'] or map_data['entities'] or map_data['borders']):
                    apply_map_data(map_data)
                else:
                    generate_default_world()  # Use the function we defined above
            except: 
                generate_default_world()  # Use the function we defined above
                
    # Setup indoor colliders for houses
    setup_indoor_colliders()
    
    # Setup dungeon if needed (but don't clear existing dungeon setup)
    if current_level == "dungeon" and not dungeon_walls:
        setup_dungeon_with_enemy_spawns()

def handle_boss_room_state(screen, assets):
    """Handle boss room game state."""
    # For now, redirect to playing state with a fixed dt
    dt = 16  # Approximately 60 FPS
    handle_playing_state(screen, assets, dt)
def generate_default_world():
    """Generate a basic world if map loading fails."""
    global tree_rects, house_list, stone_rects, flower_tiles, leaf_tiles
    global npc_rect, miner_npc_rect, dungeon_portal, zone2_portal
    
    # Clear existing
    tree_rects.clear()
    house_list.clear()
    stone_rects.clear()
    flower_tiles.clear()
    leaf_tiles.clear()
    
    # Create basic world layout
    # Trees around border
    for x in range(0, 40):
        tree_rects.append(pygame.Rect(x * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))  # Top
        tree_rects.append(pygame.Rect(x * TILE_SIZE, 39 * TILE_SIZE, TILE_SIZE, TILE_SIZE))  # Bottom
    
    for y in range(1, 39):
        tree_rects.append(pygame.Rect(0, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))  # Left
        tree_rects.append(pygame.Rect(39 * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))  # Right
    
    # Add Trees
    for _ in range(20):
        x = random.randint(3, 36) * TILE_SIZE
        y = random.randint(3, 36) * TILE_SIZE
        tree_rects.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
    
    # Add stones
    for _ in range(15):
        x = random.randint(2, 37) * TILE_SIZE
        y = random.randint(2, 37) * TILE_SIZE
        stone_rects.append(pygame.Rect(x, y, TILE_SIZE//2, TILE_SIZE//2))
    
    # Add houses
    house_list.append(pygame.Rect(10 * TILE_SIZE, 10 * TILE_SIZE, TILE_SIZE * 2, TILE_SIZE * 2))
    house_list.append(pygame.Rect(30 * TILE_SIZE, 15 * TILE_SIZE, TILE_SIZE * 2, TILE_SIZE * 2))
    
    # Add NPCs
    npc_rect = pygame.Rect(15 * TILE_SIZE, 20 * TILE_SIZE, PLAYER_SIZE * 4, PLAYER_SIZE * 4)
    miner_npc_rect = pygame.Rect(25 * TILE_SIZE, 25 * TILE_SIZE, PLAYER_SIZE, PLAYER_SIZE)
    
    # Add dungeon portal
    dungeon_portal = pygame.Rect(20 * TILE_SIZE, 30 * TILE_SIZE, 50, 50)
    
    # Next zone portal
    zone2_portal = pygame.Rect(5 * TILE_SIZE, 5 * TILE_SIZE, 50, 50)

    # Add flowers
    for _ in range(10):
        fx = random.randint(2, 37) * TILE_SIZE + 10
        fy = random.randint(2, 37) * TILE_SIZE + 10
        flower_tiles.append((fx, fy, random.randint(0, 1)))
    
    print("Generated default world")

# Starting Items
def give_starting_items(assets):
    
    add_item_to_inventory(assets["axe_item"])
    add_item_to_inventory(assets["pickaxe_item"])

# ------------------
# Handle functions
# ------------------
def spawn_enemy_in_dungeon():
    """Spawn an enemy in a valid location in the dungeon."""
    global last_enemy_spawn, enemies

    current_time = pygame.time.get_ticks()
    if current_time - last_enemy_spawn < 3000:
        return

    if len(enemies) >= MAX_ENEMIES:
        return

    for attempt in range(50):
        spawn_x = random.randint(5 * TILE_SIZE, (DUNGEON_SIZE - 5) * TILE_SIZE)
        spawn_y = random.randint(5 * TILE_SIZE, (DUNGEON_SIZE - 5) * TILE_SIZE)
        
        test_rect = pygame.Rect(spawn_x, spawn_y, PLAYER_SIZE, PLAYER_SIZE)
        
        collision = False
        player_world_rect = get_player_world_rect()
        
        # Check walls
        for wall in dungeon_walls:
            if test_rect.colliderect(wall):
                collision = True
                break
        
        # Check stones
        if not collision:
            for stone in stone_rects:
                if test_rect.colliderect(stone):
                    collision = True
                    break
        
        # Check other enemies
        if not collision:
            for other in enemies:
                if test_rect.colliderect(other.rect):
                    collision = True
                    break
        
        # Keep away from player
        if not collision:
            distance = math.hypot(
                spawn_x - player_world_rect.centerx, 
                spawn_y - player_world_rect.centery
            )
            if distance < 150:
                collision = True
        
        if not collision:
            enemy = Enemy(spawn_x, spawn_y, "orc")
            enemies.append(enemy)
            last_enemy_spawn = current_time
            print(f"Spawned orc at ({spawn_x}, {spawn_y})")
            return
    
    print("❌ Could not find safe spawn position for enemy")


def handle_combat(current_time):
    """Enhanced combat system that handles boss fights and regular enemies."""
    global current_level, map_offset_x, map_offset_y, player_pos
    
    player_world_rect = get_player_world_rect()
    player.rect = player_world_rect

    # Enemies attacking player
    for enemy in enemies[:]:  # Create a copy to avoid modification during iteration
        if isinstance(enemy, Boss):
            # Special boss attack handling
            if enemy.attack_player(player, current_time):
                # Boss attacks can have different damage multipliers based on phase
                base_damage = enemy.damage
                
                # Phase-based damage scaling
                if enemy.phase == 2:
                    if "Double Strike" in [text.text for text in floating_texts]:
                        base_damage = int(base_damage * 1.5)  # Double strike bonus
                elif enemy.phase == 3:
                    if "Berserker Strike" in [text.text for text in floating_texts]:
                        base_damage = int(base_damage * 1.8)  # Berserker bonus
                
                # Apply damage
                if player.take_damage(base_damage, current_time):
                    handle_player_death()
                    return
        else:
            # Regular enemy attack
            if enemy.attack_player(player, current_time):
                if player.take_damage(enemy.damage, current_time):
                    handle_player_death()
                    return

def handle_player_death():
    """Handle what happens when player dies."""
    global is_game_over
    print("💀 Player has died!")
    is_game_over = True  # This line is already there, good!

def handle_boss_combat_feedback():
    """Add special visual effects and feedback for boss fights."""
    for enemy in enemies:
        if isinstance(enemy, Boss):
            # Screen shake effect during boss phase changes
            if hasattr(enemy, 'last_phase_change'):
                time_since_phase_change = pygame.time.get_ticks() - enemy.last_phase_change
                if time_since_phase_change < 500:  # Screen shake for 0.5 seconds
                    shake_intensity = max(0, 10 - (time_since_phase_change / 25))
                    # You can implement screen shake by slightly offsetting the camera
                    # This is just a placeholder for the concept
                    pass

def update_boss_room_enemies(dt, current_time, player_world_rect, obstacles):
    """Special update function for boss room enemies."""
    for enemy in enemies[:]:  # Create copy for safe iteration
        if isinstance(enemy, Boss):
            # Update boss with enhanced AI
            enemy.update(dt, current_time, player_world_rect, obstacles)
            
            # Check if boss is defeated
            if enemy.health <= 0:
                # Boss victory!
                floating_texts.append(FloatingText(
                    "VICTORY!",
                    (WIDTH // 2, HEIGHT // 2),
                    color=(255, 215, 0),
                    lifetime=5000
                ))
                
                # Give boss rewards
                player.gain_experience(enemy.experience_reward)
                
                # Maybe spawn some treasure or unlock something
                print(f"Boss defeated! Gained {enemy.experience_reward} experience!")
                
                # Remove boss from enemies list
                enemies.remove(enemy)
                
                # Could trigger end-game sequence or unlock new areas
                
        else:
            # Regular enemy update
            enemy.update(dt, current_time, player_world_rect, obstacles)


def handle_boss_room_interactions(event, player_pos, assets):
    """Handle interactions specific to the boss room."""
    global current_level, map_offset_x, map_offset_y
    
    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
        # Exit door
        exit_door = pygame.Rect(WIDTH // 2 - 40, HEIGHT - 50, 80, 40)
        if player_pos.colliderect(exit_door.inflate(20, 20)):
            # Return to dungeon
            current_level = "dungeon"
            
            # Spawn back at boss door location in dungeon
            if boss1_portal:
                spawn_x = boss1_portal.centerx
                spawn_y = boss1_portal.centery + 100  # Slightly below the door
            else:
                spawn_x = 20 * TILE_SIZE
                spawn_y = 15 * TILE_SIZE
            
            map_offset_x = spawn_x - WIDTH // 2
            map_offset_y = spawn_y - HEIGHT // 2
            player_pos.center = (WIDTH // 2, HEIGHT // 2)
            
            print("Returned to dungeon from boss room")
# --- INVENTORY/CRAFTING/EQUIPMENT LOGIC ---
def add_item_to_inventory(item_to_add):
    """Adds an item to the first available slot in the inventory (stack up to 20)."""
    for row in range(4):
        for col in range(4):
            slot = inventory[row][col]
            if slot and slot.name == item_to_add.name and slot.count < 20:
                slot.count += 1
                return True
    for row in range(4):
        for col in range(4):
            if inventory[row][col] is None:
                new_item = Item(
                    item_to_add.name, 
                    item_to_add.image, 
                    count=1,
                    category=item_to_add.category, 
                    damage=item_to_add.damage,
                    defense=item_to_add.defense 
                )
                inventory[row][col] = new_item
                return True
    return False

def get_item_count(item_name):
    """Returns the total count of an item in the inventory."""
    count = 0
    for row in range(4):
        for col in range(4):
            slot = inventory[row][col]
            if slot and slot.name == item_name:
                count += slot.count
    return count

def remove_item_from_inventory(item_name, quantity):
    """Removes a specified quantity of an item from the inventory."""
    removed_count = 0
    for row in range(4):
        for col in range(4):
            slot = inventory[row][col]
            if slot and slot.name == item_name:
                to_remove = min(slot.count, quantity - removed_count)
                slot.count -= to_remove
                removed_count += to_remove
                if slot.count <= 0:
                    inventory[row][col] = None
                if removed_count >= quantity:
                    return True
    return False

def equip_item(item_to_equip):
    """Enhanced equip function that handles different equipment types."""
    global equipment_slots
    
    if not item_to_equip:
        return False
        
    slot_mapping = {
        # Weapons
        "Weapon": "weapon",
        "Axe": "weapon", 
        "Pickaxe": "weapon",
        "Sword": "weapon",

        # Armor 
        "Helmet": "helmet",
        "Chest Armor": "armor", 
        "Armor": "armor",   
        "Boots": "boots",

        # Accessories
        "Ring": "ring1",
        "Amulet": "amulet",
        "Shield": "shield"
    }

    # Find appropriate slot
    target_slot = None
    if hasattr(item_to_equip, 'category') and item_to_equip.category in slot_mapping:
        target_slot = slot_mapping[item_to_equip.category]
    elif item_to_equip.name in slot_mapping:
        target_slot = slot_mapping[item_to_equip.name]
    
    if not target_slot:
        print(f"Cannot equip {item_to_equip.name} - no suitable slot found")
        print(f"Item category: {getattr(item_to_equip, 'category', 'None')}")  # Debug info
        return False
    
    # Handle rings specially
    if target_slot.startswith("ring"):
        if equipment_slots["ring1"] is None:
            target_slot = "ring1"
        elif equipment_slots["ring2"] is None:
            target_slot = "ring2"
        else:
            print("Both ring slots are occupied")
            return False
    
    # If slot is occupied, return old item to inventory first
    if equipment_slots[target_slot] is not None:
        old_item = equipment_slots[target_slot]
        if not add_item_to_inventory(old_item):
            print("Inventory is full, cannot swap equipment")
            return False
    
    # Equip the new item
    equipment_slots[target_slot] = item_to_equip
    return True

def unequip_item_from_slot(slot_name):
    """Unequip item from a specific slot."""
    global equipment_slots
    
    item_to_unequip = equipment_slots.get(slot_name)
    if item_to_unequip:
        if add_item_to_inventory(item_to_unequip):
            equipment_slots[slot_name] = None
            print(f"{item_to_unequip.name} unequipped from {slot_name}!")
            return True
        else:
            print("Inventory is full, cannot unequip.")
    return False

def handle_inventory_mouse_down(mouse_pos, button=1):
    """Handle starting to drag an item from inventory, or right-click to equip/use."""
    global dragging_item, dragging_from_slot, drag_offset, inventory

    if not show_inventory:
        return False

    for row in range(4):
        for col in range(4):
            slot_x = INVENTORY_X + INVENTORY_GAP + col * (INVENTORY_SLOT_SIZE + INVENTORY_GAP)
            slot_y = INVENTORY_Y + 40 + INVENTORY_GAP + row * (INVENTORY_SLOT_SIZE + INVENTORY_GAP)
            slot_rect = pygame.Rect(slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)

            if slot_rect.collidepoint(mouse_pos):
                item = inventory[row][col]
                if not item:
                    return False

                # Left click = drag
                if button == 1:
                    dragging_item = item
                    dragging_from_slot = (row, col)
                    drag_offset = (mouse_pos[0] - slot_rect.centerx,
                                   mouse_pos[1] - slot_rect.centery)
                    return True

                # Right click = equip OR use
                elif button == 3:
                    # --- Equipment ---
                    if (hasattr(item, 'category') and item.category in
                        ["Weapon", "Armor", "Helmet", "Boots"]) or \
                       item.name in ["Axe", "Pickaxe", "Sword", "Helmet", "Chest Armor", "Boots"]:
                        if equip_item(item):
                            inventory[row][col] = None
                            print(f"Equipped {item.name}")
                            return True

                    # --- Consumables (potions, food, etc.) ---
                    elif item.name.lower().endswith("potion"):
                        if item.name.lower() == "speed potion":
                            # Apply a temporary speed buff
                            player.add_status_effect("speed", duration=10000, speed_bonus=4)
                            print("Speed boosted!")
                        else:
                            # Default potion effect = heal
                            player.heal(25)

                        # Decrement stack count
                        item.count -= 1
                        if item.count <= 0:
                            inventory[row][col] = None

                        return True

                    return False



def handle_inventory_mouse_up(mouse_pos):
    """Handle dropping an item in inventory or equipping it."""
    global dragging_item, dragging_from_slot, drag_offset, inventory
    
    if not show_inventory or not dragging_item:
        return False
    
    drop_slot = None
    for row in range(4):
        for col in range(4):
            slot_x = INVENTORY_X + INVENTORY_GAP + col * (INVENTORY_SLOT_SIZE + INVENTORY_GAP)
            slot_y = INVENTORY_Y + 40 + INVENTORY_GAP + row * (INVENTORY_SLOT_SIZE + INVENTORY_GAP)
            slot_rect = pygame.Rect(slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)
            
            if slot_rect.collidepoint(mouse_pos):
                drop_slot = (row, col)
                break
        if drop_slot:
            break
    
    if drop_slot:
        from_row, from_col = dragging_from_slot
        to_row, to_col = drop_slot
        
        # Swap items
        inventory[from_row][from_col], inventory[to_row][to_col] = \
            inventory[to_row][to_col], inventory[from_row][from_col]
        
        print(f"Moved item from ({from_row},{from_col}) to ({to_row},{to_col})")
    else:
        # Check if dropping outside inventory = equip attempt
        if (hasattr(dragging_item, 'category') and dragging_item.category in ["Weapon", "Armor", "Helmet", "Boots"]) or \
           dragging_item.name in ["Axe", "Pickaxe", "Sword", "Helmet", "Chest Armor", "Boots"]:
            if equip_item(dragging_item):
                from_row, from_col = dragging_from_slot
                inventory[from_row][from_col] = None
                print(f"Equipped {dragging_item.name}")
    
    # Clear drag state
    dragging_item = None
    dragging_from_slot = None
    drag_offset = (0, 0)
    return True


def handle_equipment_click(mouse_pos, slot_rects):
    """Handle clicking on equipment slots to unequip items."""
    if not show_equipment:
        return
        
    for slot_name, slot_rect in slot_rects.items():
        if slot_rect.collidepoint(mouse_pos):
            unequip_item_from_slot(slot_name)
            return True
    return False
def unequip_item():
    """Unequips the currently held weapon."""
    item_to_unequip = equipment_slots.get("weapon")
    if item_to_unequip:
        if add_item_to_inventory(item_to_unequip):
            equipment_slots["weapon"] = None
            print(f"{item_to_unequip.name} unequipped!")
            return True
        else:
            print("Inventory is full, cannot unequip.")
    return False

# -------------------------
# --- DRAWING FUNCTIONS ---
# -------------------------
def draw_boss_health_bar(screen, assets, boss):
    """Draw a special health bar for the boss at the top of the screen."""
    if not isinstance(boss, Boss):
        return
        
    # Boss health bar at top of screen
    bar_width = WIDTH - 100
    bar_height = 20
    bar_x = 50
    bar_y = 50
    
    # Background
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(screen, (60, 0, 0), bg_rect)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 3)
    
    # Health bar with phase-based colors
    health_ratio = boss.health / boss.max_health
    health_width = int(bar_width * health_ratio)
    
    # Color based on phase
    if boss.phase == 1:
        health_color = (200, 100, 100)  # Light red
    elif boss.phase == 2:
        health_color = (255, 150, 0)    # Orange
    else:  # Phase 3
        health_color = (255, 50, 50)    # Bright red
    
    health_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
    pygame.draw.rect(screen, health_color, health_rect)
    
    # Boss name and phase
    name_text = f"{boss.name} - Phase {boss.phase}"
    text_surf = assets["font"].render(name_text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(WIDTH // 2, bar_y - 15))
    screen.blit(text_surf, text_rect)
    
    # Health numbers
    health_text = f"{boss.health}/{boss.max_health}"
    health_surf = assets["small_font"].render(health_text, True, (255, 255, 255))
    health_text_rect = health_surf.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2))
    screen.blit(health_surf, health_text_rect)
def draw_boss_room(screen, assets):
    """Draw the boss room including floor, walls, ore, portals, and enemies."""
    # Draw black floor for boss room
    screen.fill((20, 20, 20))  # Dark floor
    
    # Draw boss room walls
    for wall in boss_room_walls:
        screen.blit(assets["dungeon_wall"], (wall.x - map_offset_x, wall.y - map_offset_y))
    
    # Draw ore deposits in boss room
    for ore in stone_rects:
        screen.blit(assets["ore_img"], (ore.x - map_offset_x, ore.y - map_offset_y))
    
    # Draw boss portal if it exists
    if boss1_portal:
        screen.blit(assets["boss1_portal"], (boss1_portal.x - map_offset_x, boss1_portal.y - map_offset_y))
    
    # Draw exit portal
    if dungeon_exit:
        screen.blit(assets["portal"], (dungeon_exit.x - map_offset_x, dungeon_exit.y - map_offset_y))
    
    # Draw enemies (including boss)
    for enemy in enemies:
        enemy_screen_rect = world_to_screen_rect(enemy.rect)
        if -100 <= enemy_screen_rect.x <= WIDTH + 100 and -100 <= enemy_screen_rect.y <= HEIGHT + 100:
            screen.blit(enemy.image, enemy_screen_rect)
            
            # Draw boss health bar at top of screen
            if isinstance(enemy, Boss):
                draw_boss_health_bar(screen, assets, enemy)
            
            # Draw regular enemy health bar if damaged
            elif enemy.health < enemy.max_health:
                bar_y = enemy_screen_rect.y - 15
                draw_health_bar(screen, enemy_screen_rect.x, bar_y, enemy.health, enemy.max_health, enemy.rect.width, 8)

    # Update and draw floating texts
    for text in floating_texts[:]:
        text.update()
        if not text.is_alive():
            floating_texts.remove(text)
        else:
            text.draw(screen, assets["small_font"], map_offset_x, map_offset_y)

def draw_pause_menu(screen, assets):
    """Draw the in-game pause/options menu."""
    if not show_pause_menu:
        return
    
    global pause_button_rects
    pause_button_rects = {}
    
    # Semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Main panel
    panel_width = 400
    panel_height = 350
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    
    pygame.draw.rect(screen, (40, 40, 60), panel_rect)
    pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)
    
    # Title
    title_text = assets["large_font"].render("Game Paused", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WIDTH // 2, panel_y + 40))
    screen.blit(title_text, title_rect)
    
    # Menu options
    menu_options = ["Resume", "Save Game", "Main Menu", "Exit Game"]
    button_height = 50
    button_width = 300
    start_y = panel_y + 80
    
    mouse_pos = pygame.mouse.get_pos()
    
    for i, option in enumerate(menu_options):
        button_y = start_y + i * (button_height + 10)
        button_rect = pygame.Rect((WIDTH - button_width) // 2, button_y, button_width, button_height)
        
        # Check for hover
        is_hovered = button_rect.collidepoint(mouse_pos)
        is_selected = i == pause_menu_selected_option
        
        # Button colors
        if is_selected or is_hovered:
            button_color = (70, 70, 100)
            text_color = (255, 255, 0)
        else:
            button_color = (50, 50, 70)
            text_color = (255, 255, 255)
        
        # Draw button
        pygame.draw.rect(screen, button_color, button_rect)
        pygame.draw.rect(screen, (200, 200, 200), button_rect, 2)
        
        # Button text
        text_surf = assets["font"].render(option, True, text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        screen.blit(text_surf, text_rect)
        
        # Store rect for clicking
        pause_button_rects[option.lower().replace(" ", "_")] = button_rect
def draw_main_menu(screen, assets):
    """Draw the main menu screen with enhanced mouse hover effects."""
    if "main_bg" not in assets:
        bg = pygame.image.load("GUI/main.png").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))  # scale to fit window
        assets["main_bg"] = bg

    screen.blit(assets["main_bg"], (0, 0))

    # Get mouse position for hover effects
    mouse_pos = pygame.mouse.get_pos()
    
    # Title
    title_text = assets["large_font"].render("Adventure Game", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    # Menu options with enhanced hover effects
    menu_options = ["New Game", "Load Game", "Exit"]
    
    for i, option in enumerate(menu_options):
        # Determine colors based on selection and hover
        if i == menu_selected_option:
            text_color = (255, 255, 0)  # Yellow when selected
            bg_color = (50, 50, 100)   # Blue background
        else:
            text_color = (255, 255, 255)  # White when not selected
            bg_color = None
        
        option_text = assets["font"].render(option, True, text_color)
        option_rect = option_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
        
        # Draw background for selected option
        if bg_color:
            bg_rect = option_rect.inflate(40, 20)
            pygame.draw.rect(screen, bg_color, bg_rect, border_radius=10)
        
        screen.blit(option_text, option_rect)
        
        # Draw selection border
        if i == menu_selected_option:
            pygame.draw.rect(screen, (255, 255, 0), option_rect.inflate(20, 10), 2, border_radius=5)

def draw_save_select_menu(screen, assets):
    """Draw the save slot selection screen."""
    screen.fill((30, 20, 40))  # Different background
    
    # Title
    title_text = assets["large_font"].render("Select Save Slot", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    # Save slots
    for i in range(4):
        slot_y = HEIGHT // 2 + i * 60 - 120
        slot_rect = pygame.Rect(WIDTH // 2 - 200, slot_y, 400, 50)
        
        # Highlight selected slot
        color = (100, 100, 100) if i == selected_save_slot - 1 else (50, 50, 50)
        pygame.draw.rect(screen, color, slot_rect)
        pygame.draw.rect(screen, (255, 255, 255), slot_rect, 2)
        
        # Slot content
        if save_slots[i]:
            slot_text = f"Slot {i+1}: Level {save_slots[i]['level']}"
        else:
            slot_text = f"Slot {i+1}: Empty"
            
        text_surf = assets["font"].render(slot_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=slot_rect.center)
        screen.blit(text_surf, text_rect)
    
    # Instructions
    instruction_text = assets["small_font"].render("Press ENTER to select, ESC to go back", True, (200, 200, 200))
    instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(instruction_text, instruction_rect)
    # --- Indoor colliders ---
    setup_indoor_colliders()

    # --- Setup dungeon if needed ---
    if not dungeon_walls:
        setup_dungeon_with_enemy_spawns()
        boss_door_rect = boss1_portal
def draw_dungeon(screen, assets, enemy_frames):
    """Draws the dungeon level with enemies and boss door."""
    dungeon_width = 30
    dungeon_height = 16
    
    # Draw floor tiles
    for x in range(dungeon_width):
        for y in range(dungeon_height):
            screen.blit(assets["dungeon_floor"], (x * TILE_SIZE - map_offset_x, y * TILE_SIZE - map_offset_y))
    
    # Draw dungeon walls
    for wall in dungeon_walls:
        screen.blit(assets["dungeon_wall"], (wall.x - map_offset_x, wall.y - map_offset_y))
    
    # Draw ore deposits
    for ore in stone_rects:
        screen.blit(assets["ore_img"], (ore.x - map_offset_x, ore.y - map_offset_y))
    
    # Draw boss door if it exists
    if boss1_portal and current_level == "dungeon":
        boss_door_image = assets["boss_door_frames"]["closed"]
        screen.blit(boss_door_image, (boss1_portal.x - map_offset_x, boss1_portal.y - map_offset_y))
    
    # Draw enemies
    for enemy in enemies:
        enemy_screen_rect = world_to_screen_rect(enemy.rect)
        if -100 <= enemy_screen_rect.x <= WIDTH + 100 and -100 <= enemy_screen_rect.y <= HEIGHT + 100:
            screen.blit(enemy.image, enemy_screen_rect)
        
            # Draw enemy health bar if damaged
            if enemy.health < enemy.max_health:
                bar_y = enemy_screen_rect.y - 10
                draw_health_bar(screen, enemy_screen_rect.x, bar_y, enemy.health, enemy.max_health, enemy.rect.width, 5)
    # Draw loot drops
    for loot in loot_drops:
        loot.draw(screen, map_offset_x, map_offset_y)
    # Draw exit portal
    if dungeon_exit:
        screen.blit(assets["portal"], (dungeon_exit.x - map_offset_x, dungeon_exit.y - map_offset_y))
    
    # Update and draw floating texts
    for text in floating_texts[:]:
        text.update()
        if not text.is_alive():
            floating_texts.remove(text)
        else:
            text.draw(screen, assets["small_font"], map_offset_x, map_offset_y)
def draw_zone2(screen, assets):
    """Draw Zone 2 with its unique features."""
    # Draw grass base 
    start_col = map_offset_x // TILE_SIZE
    start_row = map_offset_y // TILE_SIZE
    cols_to_draw = (WIDTH // TILE_SIZE) + 3
    rows_to_draw = (HEIGHT // TILE_SIZE) + 3
    
    for row in range(start_row, start_row + rows_to_draw):
        for col in range(start_col, start_col + cols_to_draw):
            x, y = col * TILE_SIZE, row * TILE_SIZE
            grass_tinted = assets["grass"].copy()
            grass_tinted.fill((180, 255, 180), special_flags=pygame.BLEND_MULT)
            screen.blit(grass_tinted, (x - map_offset_x, y - map_offset_y))
    
    # Draw water tiles
    for wx, wy in water_tiles:
        water_rect = pygame.Rect(wx - map_offset_x, wy - map_offset_y, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (50, 100, 200), water_rect)  # Blue water
        # Add some wave effect
        pygame.draw.rect(screen, (100, 150, 255), water_rect, 2)
    
    # Draw trees (mystical purple tint)
    for tree in tree_rects:
        tree_image = assets["tree"].copy()
        tree_image.fill((200, 150, 255), special_flags=pygame.BLEND_MULT)
        screen.blit(tree_image, (tree.x - map_offset_x - 2, tree.y - map_offset_y - 2))
    
    # Draw crystals
    for crystal in crystal_rects:
        # Draw glowing effect
        glow_rect = crystal.inflate(10, 10)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (100, 200, 255, 50), glow_surf.get_rect())
        screen.blit(glow_surf, (glow_rect.x - map_offset_x, glow_rect.y - map_offset_y))
        
        # Draw crystal
        if "crystal_item" in assets:
            screen.blit(assets["crystal_item"].image, 
                       (crystal.x - map_offset_x, crystal.y - map_offset_y))
    
    # Draw stones
    for stone in stone_rects:
        screen.blit(assets["stone_img"], (stone.x - map_offset_x, stone.y - map_offset_y))
    
    # Draw flowers with magical glow
    for fx, fy, idx in flower_tiles:
        flower_image = assets["flowers"][idx].copy()
        flower_image.fill((255, 200, 255), special_flags=pygame.BLEND_ADD)
        screen.blit(flower_image, (fx - map_offset_x, fy - map_offset_y))
    
    # Draw leaves
    for lx, ly in leaf_tiles:
        screen.blit(assets["leaf"], (lx - map_offset_x, ly - map_offset_y))
    
    # Draw return portal
    if zone2_return_portal:
        # Portal with purple tint
        portal_image = assets["portal"].copy()
        portal_image.fill((200, 100, 255), special_flags=pygame.BLEND_MULT)
        screen.blit(portal_image, 
                   (zone2_return_portal.x - map_offset_x, zone2_return_portal.y - map_offset_y))
    
    # Draw merchant NPC if exists
    if zone2_merchant_rect:
        merchant_image = assets.get("miner_image", assets["npc_image"])
        merchant_image = pygame.transform.scale(merchant_image, (PLAYER_SIZE, PLAYER_SIZE))
        screen.blit(merchant_image, 
                   (zone2_merchant_rect.x - map_offset_x, zone2_merchant_rect.y - map_offset_y))

#-----------------------
# More draw functions
# -----------------------
def draw_health_bar(screen, x, y, current_health, max_health, width=100, height=10):
    """Draws a health bar at the specified position."""
    # Background (red)
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, (139, 0, 0), bg_rect)
    
    # Health (green)
    health_ratio = max(0, current_health / max_health)
    health_width = int(width * health_ratio)
    health_rect = pygame.Rect(x, y, health_width, height)
    pygame.draw.rect(screen, (0, 139, 0), health_rect)
    
    # Border
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 1)

def draw_player_stats(screen, assets, player_frames, attack_frames, chopping_frames):
    """Draws player stats in the top-left corner with player portrait."""
    y_offset = 10
    
    portrait_size = 32
    portrait_rect = pygame.Rect(10, y_offset, portrait_size, portrait_size)
    
    # Get current player frame with bounds checking
    if is_attacking:
        frames = attack_frames[last_direction]
        frame_index = min(player_frame_index, len(frames) - 1)  # Clamp to valid range
        current_frame = frames[frame_index]

    elif is_chopping or is_mining:
        chop_direction = last_direction if last_direction in chopping_frames else "down"
        frames = chopping_frames[chop_direction]
        frame_index = min(player_frame_index, len(frames) - 1)  # Clamp to valid range
        current_frame = frames[frame_index]
    else:
        frame_set = player_frames.get(current_direction, player_frames["idle"])
        frame_index = min(player_frame_index, len(frame_set) - 1)  # Clamp to valid range
        current_frame = frame_set[frame_index]
    
    # Scale and draw portrait
    portrait_frame = pygame.transform.scale(current_frame, (portrait_size, portrait_size))
    screen.blit(portrait_frame, portrait_rect)
    
    # Draw border around portrait
    pygame.draw.rect(screen, (255, 255, 255), portrait_rect, 2)
    
    # Health bar (moved right to make room for portrait)
    health_bar_x = portrait_rect.right + 10
    draw_health_bar(screen, health_bar_x, y_offset, player.health, player.max_health, 120, 15)
    
    regen_text = ""
    if player.out_of_combat and player.health < player.max_health:
        regen_text = " +HP"
        health_color = (100, 255, 100)  # Green when regenerating
    else:
        health_color = (255, 255, 255)
    
    health_text = f"Health: {int(player.health)}/{player.max_health}{regen_text}"
    text_surf = assets["small_font"].render(health_text, True, health_color)
    screen.blit(text_surf, (health_bar_x + 130, y_offset))
    y_offset += 25
    equipped_weapon = equipment_slots.get("weapon")
    total_damage = player.get_total_damage(equipped_weapon)
    total_defense = player.get_total_defense()
    
    stats_text = f"Level {player.level} | Damage: {total_damage} | Defense: {total_defense}"
    text_surf = assets["small_font"].render(stats_text, True, (255, 255, 255))
    screen.blit(text_surf, (health_bar_x, y_offset))

def draw_level_up_notification(screen, assets):
    """Draws level up notification in the center of screen."""
    if not show_level_up:
        return
    
    # Create pulsing effect based on timer
    pulse = math.sin(level_up_timer / 200.0) * 0.3 + 1.0
    
    # Level up text
    level_text = assets["large_font"].render(level_up_text, True, (255, 215, 0))  # Gold
    text_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    
    # Scale text for pulse effect
    scaled_width = int(text_rect.width * pulse)
    scaled_height = int(text_rect.height * pulse)
    scaled_text = pygame.transform.scale(level_text, (scaled_width, scaled_height))
    scaled_rect = scaled_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    
    # Background glow effect
    glow_rect = scaled_rect.inflate(40, 20)
    glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
    glow_surf.fill((255, 215, 0, 50))
    screen.blit(glow_surf, glow_rect)
    
    screen.blit(scaled_text, scaled_rect)
    
    # Stats increase text
    stats_text = f"Health +{15 + (player.level * 2)} | Damage +{3 + (player.level // 2)}"
    stats_surf = assets["small_font"].render(stats_text, True, (200, 255, 200))
    stats_rect = stats_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    screen.blit(stats_surf, stats_rect)

# ----------------------------------------------
# Helper functions to clean up the main function
# ----------------------------------------------
def _handle_other_resources(player_world_rect, assets):
    """Handle mining and flower picking when player has axe."""
    global equipment_slots, is_mining, mining_target_stone, mining_timer, current_direction
    
    if equipment_slots["weapon"] and equipment_slots["weapon"].name == "Pickaxe":
        for stone in list(stone_rects):
            if player_world_rect.colliderect(stone.inflate(20, 20)):
                is_mining = True
                mining_target_stone = stone
                mining_timer = 0
                current_direction = "idle"
                break
        else:
            _handle_flower_picking(player_world_rect, assets)
    else:
        _handle_flower_picking(player_world_rect, assets)
def _handle_carrot_picking(player_world_rect, assets):
    """Handle carrot picking."""
    for cx, cy, idx in list(carrot_tiles):
        carrot_rect = pygame.Rect(cx, cy, 30, 30)
        if player_world_rect.colliderect(carrot_rect.inflate(10, 10)):
            add_item_to_inventory(assets["carrot_item"])
            carrot_tiles.remove((cx, cy, idx))
            print("Picked a carrot!")
            break

def _handle_flower_picking(player_world_rect, assets):
    """Handle flower picking."""
    for fx, fy, idx in list(flower_tiles):
        flower_rect = pygame.Rect(fx, fy, 30, 30)
        if player_world_rect.colliderect(flower_rect.inflate(10, 10)):
            add_item_to_inventory(assets["flower_item"])
            flower_tiles.remove((fx, fy, idx))
            print("Picked a flower!")
            break

def _handle_mouse_clicks(event, assets, screen):
    """Handle all mouse click events."""
    if show_vendor_gui:
        _handle_vendor_clicks(event, assets)
    elif show_crafting and not is_crafting:
        _handle_crafting_clicks(event, assets)
    elif show_equipment:
        equipment_slot_rects = draw_equipment_panel(screen, assets)
        handle_equipment_click(event.pos, equipment_slot_rects)
    elif show_inventory:
        draw_inventory(screen, assets)

def _handle_vendor_clicks(event, assets):
    """Handle vendor GUI clicks."""
    global vendor_tab
    
    if "buy_tab" in buy_button_rects and buy_button_rects["buy_tab"].collidepoint(event.pos):
        vendor_tab = "buy"
    elif "sell_tab" in buy_button_rects and buy_button_rects["sell_tab"].collidepoint(event.pos):
        vendor_tab = "sell"
    elif vendor_tab == "buy":
        _handle_buy_transactions(event, assets)
    elif vendor_tab == "sell":
        _handle_sell_transactions(event, assets)

def _handle_buy_transactions(event, assets):
    """Handle buying items from vendor."""
    shop_items = get_shop_items(assets)
    coin_count = get_item_count("Coin")
    
    for item_name, button_rect in buy_button_rects.items():
        if item_name in ["buy_tab", "sell_tab"]:
            continue
        if button_rect.collidepoint(event.pos):
            item_data = shop_items[item_name]
            if coin_count >= item_data["buy_price"]:
                remove_item_from_inventory("Coin", item_data["buy_price"])
                add_item_to_inventory(item_data["item"])
                print(f"Bought {item_name} for {item_data['buy_price']} coins!")
            else:
                print("Not enough coins!")
            break

def _handle_sell_transactions(event, assets):
    """Handle selling items to vendor."""
    shop_items = get_shop_items(assets)
    
    for item_name, button_rect in sell_button_rects.items():
        if button_rect.collidepoint(event.pos):
            if get_item_count(item_name) > 0:
                remove_item_from_inventory(item_name, 1)
                item_data = shop_items[item_name]
                for _ in range(item_data["sell_price"]):
                    add_item_to_inventory(assets["coin_item"])
                print(f"Sold {item_name} for {item_data['sell_price']} coins!")
            break

def _handle_crafting_clicks(event, assets):
    """Handle crafting GUI clicks."""
    global crafting_tab, is_crafting, crafting_timer, item_to_craft

    # 1) Tab switching (use event.pos, not mouse_pos)
    if smithing_tab_rect and smithing_tab_rect.collidepoint(event.pos):
        crafting_tab = "smithing"
        return
    if alchemy_tab_rect and alchemy_tab_rect.collidepoint(event.pos):
        crafting_tab = "alchemy"
        return
    if cooking_tab_rect and cooking_tab_rect.collidepoint(event.pos):
        crafting_tab = "cooking"
        return

    # 2) Within the active tab, handle recipe button clicks
    if crafting_tab == "smithing":
        _handle_smithing_crafting(event, assets)
    elif crafting_tab == "alchemy":
        _handle_alchemy_crafting(event, assets)
    elif crafting_tab == "cooking":
        _handle_cooking_crafting(event, assets)

# CURRENTLY NEEDS WORK
def _handle_cooking_crafting(dt, assets, play_sound):
    """
    Handle the cooking process — starts when the player interacts with a campfire, stove, or cooking tile.
    Works similarly to crafting or smithing but focused on food-related items.
    """
    global is_crafting, crafting_timer, item_to_craft, cooking_tab_rect

    # --- Only run if cooking is active ---
    if not is_crafting or item_to_craft is None:
        return

    # --- Update the timer ---
    crafting_timer += dt

    # --- Display cooking progress (optional floating text or GUI bar) ---
    progress_ratio = crafting_timer / CRAFTING_TIME_MS
    progress_ratio = min(1.0, progress_ratio)

    # Optional: Draw progress bar if you have a cooking tab rect
    if cooking_tab_rect:
        bar_width = int(200 * progress_ratio)
        bar_height = 12
        bar_x = cooking_tab_rect.x + 30
        bar_y = cooking_tab_rect.y + cooking_tab_rect.height - 40
        pygame.draw.rect(assets["screen"], (100, 100, 100), (bar_x, bar_y, 200, bar_height))
        pygame.draw.rect(assets["screen"], (255, 180, 80), (bar_x, bar_y, bar_width, bar_height))

    # --- Check for completion ---
    if crafting_timer >= CRAFTING_TIME_MS:
        is_crafting = False
        crafting_timer = 0

        # Example: turn raw meat into cooked meat
        if item_to_craft.name == "Raw Meat":
            cooked_item = Item("Cooked Meat", assets.get("cooked_meat_img"), 1, category="food")
            add_item_to_inventory(cooked_item)
            floating_texts.append(FloatingText("+1 Cooked Meat", (player.rect.x, player.rect.y - 20), color=(255, 200, 100)))
            play_sound("cooking_done", assets)

        # Example: other recipes
        elif item_to_craft.name == "Fish":
            cooked_item = Item("Grilled Fish", assets.get("grilled_fish_img"), 1, category="food")
            add_item_to_inventory(cooked_item)
            floating_texts.append(FloatingText("+1 Grilled Fish", (player.rect.x, player.rect.y - 20), color=(255, 220, 150)))
            play_sound("cooking_done", assets)

        else:
            # Unknown recipe → fail or just return item
            floating_texts.append(FloatingText("Cooking failed", (player.rect.x, player.rect.y - 20), color=(255, 80, 80)))

        item_to_craft = None

def _handle_smithing_crafting(event, assets):
    """Handle clicks on smithing crafting buttons."""
    global is_crafting, crafting_timer, item_to_craft

    crafting_recipes = [
        (axe_button_rect,   "Log",   5,  assets["axe_item"],     "Axe"),
        (pickaxe_button_rect,"Log",  10, assets["pickaxe_item"], "Pickaxe"),
        (helmet_button_rect, "Stone",8,  assets["helmet_item"],  "Helmet"),
        (chest_button_rect,  "Stone",15, assets["chest_item"],   "Chest Armor"),
        (boots_button_rect,  "Stone",6,  assets["boots_item"],   "Boots"),
        (sword_button_rect,  "Ore",  2,  assets["sword_item"],   "Sword"), 
    ]

    for button_rect, material, cost, item_obj, item_name in crafting_recipes:
        if button_rect and button_rect.collidepoint(event.pos):
            if get_item_count(material) >= cost:
                remove_item_from_inventory(material, cost)
                is_crafting = True
                crafting_timer = 0
                item_to_craft = item_obj
                print(f"⚒️ Crafting {item_name}...")
            else:
                print(f"❌ Not enough {material.lower()} to craft {item_name}!")
            break



def _handle_alchemy_crafting(event, assets):
    """Handle alchemy crafting clicks."""
    global is_crafting, crafting_timer, item_to_craft

    # --- Potion (Health) ---
    if potion_button_rect and potion_button_rect.collidepoint(event.pos):
        if get_item_count("Flower") >= 3:
            is_crafting = True
            crafting_timer = 0
            item_to_craft = assets["potion_item"]
            remove_item_from_inventory("Flower", 3)
            print("Brewing a Potion...")
        else:
            print("Not enough flowers for Potion!")

    # --- Potion 2 (Speed) ---
    elif potion2_button_rect and potion2_button_rect.collidepoint(event.pos):
        if get_item_count("Flower") >= 5:
            is_crafting = True
            crafting_timer = 0
            item_to_craft = assets["potion2_item"]
            remove_item_from_inventory("Flower", 5)
            print("Brewing a Speed Potion...")
        else:
            print("Not enough flowers for Speed Potion!")


def _update_npc_animations(dt):
    """Update NPC idle animations."""
    global npc_idle_timer, npc_idle_direction, npc_idle_offset_y
    global miner_idle_timer, miner_idle_direction, miner_idle_offset_y
    
    # NPC idle animation
    npc_idle_timer += dt
    if npc_idle_timer >= 2000:
        npc_idle_direction *= -1
        npc_idle_timer = 0
    
    idle_progress = npc_idle_timer / 2000.0
    npc_idle_offset_y = int(3 * math.sin(idle_progress * 3.14159) * npc_idle_direction)
    
    # Miner NPC idle animation
    miner_idle_timer += dt
    if miner_idle_timer >= 2200:
        miner_idle_direction *= -1
        miner_idle_timer = 0
    
    miner_idle_progress = miner_idle_timer / 2200.0
    miner_idle_offset_y = int(4 * math.sin(miner_idle_progress * 3.14159) * miner_idle_direction)

def _update_crafting(current_time, assets, dt):  
    """Update crafting progress."""
    global is_crafting, crafting_timer, item_to_craft
    
    if is_crafting:
        crafting_timer += dt
        
        if crafting_timer >= CRAFTING_TIME_MS:
            if add_item_to_inventory(item_to_craft):
                print(f"Crafting complete! {item_to_craft.name} added to inventory.")
            else:
                print("Crafting failed: Inventory is full.")
            is_crafting = False
            item_to_craft = None
            crafting_timer = 0

def _update_animations(dt, player_frames, attack_frames, chopping_frames, attack_animation_duration, assets):
    """Update player animations."""
    global is_attacking, attack_timer, player_frame_timer, player_frame_index, current_direction
    global is_chopping, chopping_timer, chopping_target_tree, is_swinging
    global is_mining, mining_timer, mining_target_stone
    global swing_delay, idle_chop_delay, player_frame_delay
    global chop_sound_played, mine_sound_played
    current_time = pygame.time.get_ticks()

    # Attack animation
    if is_attacking:
        attack_timer += dt
        player_frame_timer += dt
        if player_frame_timer >= swing_delay:
            attack_direction = last_direction if last_direction in attack_frames else "down"
            max_frames = len(attack_frames[attack_direction])
            player_frame_index = (player_frame_index + 1) % max_frames
            player_frame_timer = 0

        if attack_timer >= attack_animation_duration:
            is_attacking = False
            attack_timer = 0
            player_frame_index = 0
            current_direction = "idle"

    # Chopping animation
    elif is_chopping:
        chopping_timer += dt
        player_frame_timer += dt
        chop_sound = assets.get("chop_sound")

        if player_frame_timer > idle_chop_delay:
            is_swinging = True
            if player_frame_timer >= swing_delay:
                chop_direction = last_direction if last_direction in chopping_frames else "down"
                max_frames = len(chopping_frames[chop_direction])
                player_frame_index = (player_frame_index + 1) % max_frames
                player_frame_timer = 0

                # 🔊 Play sound only on the "impact" frame
                if chop_sound and player_frame_index == 1:  # adjust frame index as needed
                    try:
                        chop_sound.play()
                    except Exception as e:
                        print(f"Could not play chop sound: {e}")

        if chopping_timer >= CHOPPING_DURATION:
            _complete_chopping(current_time, assets)

    # Mining animation  
    elif is_mining:
        global mine_sound_played

        mining_timer += dt
        player_frame_timer += dt
        mine_sound = assets.get("mine_sound")

        if player_frame_timer > idle_chop_delay:
            is_swinging = True
            if player_frame_timer >= swing_delay:
                chop_direction = last_direction if last_direction in chopping_frames else "down"
                max_frames = len(chopping_frames[chop_direction])
                player_frame_index = (player_frame_index + 1) % max_frames
                player_frame_timer = 0

                # 🔊 Play sound only once per mining action
                if mine_sound and not mine_sound_played:
                    try:
                        mine_sound.play()
                        mine_sound_played = True
                    except Exception as e:
                        print(f"Could not play mine sound: {e}")

        if mining_timer >= MINING_DURATION:
            _complete_mining(current_time, assets)
            mine_sound.stop()
            mine_sound_played = False   # reset for the next mining action

    # Normal animation state update
    else:
        player_frame_timer += dt
        if current_direction == "idle":
            player_frame_index = 0
        elif player_frame_timer > player_frame_delay:
            frame_set = player_frames.get(current_direction, player_frames["idle"])
            max_frames = len(frame_set)
            player_frame_index = (player_frame_index + 1) % max_frames
            player_frame_timer = 0

def _complete_chopping(current_time, assets):
    global is_chopping, is_swinging, chopping_timer, chopping_target_tree, current_direction
    global chop_sound_played

    if chopping_target_tree and chopping_target_tree in tree_rects:
        # Remove the tree
        tree_rects.remove(chopping_target_tree)

        # Track chopped tree
        if 'chopped_trees' not in globals():
            globals()['chopped_trees'] = {}
        chopped_trees[(chopping_target_tree.x, chopping_target_tree.y,
                       chopping_target_tree.width, chopping_target_tree.height)] = current_time

        # Give reward
        if "log_item" in assets:
            add_item_to_inventory(assets["log_item"])
        else:
            print("⚠ log_item missing from assets!")

        print("🌲 Chopped a tree! Gained a log.")

    # Reset chopping state
    is_chopping = False
    is_swinging = False
    chopping_timer = 0
    chopping_target_tree = None
    current_direction = "idle"

def _complete_mining(current_time, assets):
    """Complete stone/ore/crystal mining action."""
    global is_mining, is_swinging, mining_timer, mining_target_stone, current_direction
    global mine_sound_played

    # 🪨 Handle normal stone/ore mining
    if mining_target_stone in stone_rects:
        stone_rects.remove(mining_target_stone)
        chopped_stones[(mining_target_stone.x, mining_target_stone.y,
                       mining_target_stone.width, mining_target_stone.height)] = current_time
        
        # Play mine sound
        if assets.get("mine_sound"):
            assets["mine_sound"].play()
        
        if current_level == "dungeon":
            add_item_to_inventory(assets["ore_item"])
            print("⛏️ Mined ore!")
        else:
            add_item_to_inventory(assets["stone_item"])
            print("🪨 Mined a stone!")

    # 💎 Handle crystal mining (Zone 2)
    elif mining_target_stone in crystal_rects:
        crystal_rects.remove(mining_target_stone)
        chopped_stones[(mining_target_stone.x, mining_target_stone.y,
                       mining_target_stone.width, mining_target_stone.height)] = current_time

        # Play mine sound
        if assets.get("mine_sound"):
            assets["mine_sound"].play()

        # Give crystal item if available
        if "crystal_item" in assets:
            add_item_to_inventory(assets["crystal_item"])
            print("💎 Mined a glowing crystal!")
        else:
            print("⚠ No crystal item found in assets!")

    # Reset mining state
    is_mining = False
    is_swinging = False
    mining_timer = 0
    mining_target_stone = None
    current_direction = "idle"
    mine_sound_played = False


def _is_ui_blocking_movement():
    """Check if any UI is blocking player movement."""
    return (show_inventory or show_crafting or show_equipment or 
            is_chopping or is_mining or is_attacking or 
            show_npc_dialog or show_miner_dialog)

def _handle_player_movement(dx, dy):
    """Handle player movement based on current level."""
    global map_offset_x, map_offset_y, player_pos, last_direction, current_direction
    
    if current_level in ["world", "dungeon", "zone2"]:
        new_player_world_rect = get_player_world_rect().move(dx, dy)
        if not handle_collision(new_player_world_rect):
            map_offset_x += dx
            map_offset_y += dy
            if dx != 0 or dy != 0:
                last_direction = current_direction

    else:  # current_level == "house" or "boss_room"
        new_player_pos = player_pos.move(dx, dy)
        if not handle_collision(new_player_pos):
            player_pos = new_player_pos
            if dx != 0 or dy != 0:
                last_direction = current_direction

def _draw_game_world(screen, assets, enemy_frames):
    """Draw the appropriate game world based on current level."""
    screen.fill((0, 0, 0))
    
    if current_level == "world":
        draw_world(screen, assets)
    elif current_level == "zone2":
        player.rect.topleft = player_pos.topleft
        draw_zone2(screen, assets)
    elif current_level == "dungeon":
        draw_dungeon(screen, assets, enemy_frames)
    elif current_level == "boss_room":
        draw_boss_room(screen, assets)
    else:  # house
        screen.blit(assets["interiors"][current_house_index], (0, 0))

def _draw_player(screen, player_frames, attack_frames, chopping_frames):
    """Draw the player with appropriate animations."""
    player_size_current = player_pos.width
    
    if is_attacking:
        attack_direction = last_direction if last_direction in attack_frames else "down"
        frame_index = min(player_frame_index, len(attack_frames[attack_direction]) - 1)
        scaled_frame = pygame.transform.scale(attack_frames[attack_direction][frame_index], 
                                            (player_size_current, player_size_current))
        screen.blit(scaled_frame, player_pos)
    elif is_chopping or is_mining:
        chop_direction = last_direction if last_direction in chopping_frames else "down"
        frame_index = min(player_frame_index, len(chopping_frames[chop_direction]) - 1)
        scaled_frame = pygame.transform.scale(chopping_frames[chop_direction][frame_index], 
                                            (player_size_current, player_size_current))
        screen.blit(scaled_frame, player_pos)
    else:
        frame_set = player_frames.get(current_direction, player_frames["idle"])
        frame_index = min(player_frame_index, len(frame_set) - 1)
        scaled_frame = pygame.transform.scale(frame_set[frame_index], 
                                            (player_size_current, player_size_current))
        screen.blit(scaled_frame, player_pos)

def _draw_ui_elements(screen, assets, player_frames, attack_frames, chopping_frames, is_hovering):
    """Draw all UI elements."""
    draw_player_stats(screen, assets, player_frames, attack_frames, chopping_frames)
    draw_experience_bar(screen, assets)
    draw_hud(screen, assets)
    draw_tooltip_for_nearby_objects(screen, assets["small_font"])
    draw_npc_dialog(screen, assets)
    draw_miner_dialog(screen, assets)
    if show_pause_menu:
        draw_pause_menu(screen, assets)
    if show_inventory:
        draw_inventory(screen, assets)
    if show_crafting:
        draw_crafting_panel(screen, assets, is_hovering)
    if show_equipment:
        draw_equipment_panel(screen, assets)
    if show_vendor_gui:
        draw_vendor_gui(screen, assets)
    if show_quests:
        draw_quests_panel(screen, assets)
    draw_level_up_notification(screen, assets)

# ----------------------------
# DRAW UI ELEMENTS
# ----------------------------
def draw_experience_bar(screen, assets):
    """Draws the experience/level progress bar at the bottom of the screen."""
    bar_height = 25
    bar_y = HEIGHT - bar_height - 5
    bar_width = WIDTH - 20
    bar_x = 10
    
    # Background
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(screen, (40, 40, 40), bg_rect)
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2)
    
    # Experience progress
    if player.experience_to_next > 0:
        exp_ratio = player.experience / player.experience_to_next
        exp_width = int(bar_width * exp_ratio)
        exp_rect = pygame.Rect(bar_x, bar_y, exp_width, bar_height)
        
        # Gradient effect for XP bar
        for i in range(bar_height):
            color_intensity = 100 + int(155 * (1 - i / bar_height))
            line_color = (0, 0, color_intensity)
            if exp_width > 0:
                pygame.draw.line(screen, line_color, 
                               (bar_x, bar_y + i), 
                               (bar_x + exp_width, bar_y + i))
    
    # Text overlay
    exp_text = f"Level {player.level} - XP: {player.experience}/{player.experience_to_next}"
    text_surf = assets["small_font"].render(exp_text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2))
    screen.blit(text_surf, text_rect)

def draw_world(screen, assets):
    """Draws the outdoor world and its objects."""
    start_col = map_offset_x // TILE_SIZE
    start_row = map_offset_y // TILE_SIZE
    cols_to_draw = (WIDTH // TILE_SIZE) + 3
    rows_to_draw = (HEIGHT // TILE_SIZE) + 3
    tree_size_diff = 5

    # Draw grass
    for row in range(start_row, start_row + rows_to_draw):
        for col in range(start_col, start_col + cols_to_draw):
            x, y = col * TILE_SIZE, row * TILE_SIZE
            screen.blit(assets["grass"], (x - map_offset_x, y - map_offset_y))
    # Draw path tiles
    for path in path_tiles:
        screen.blit(assets["path"], (path.x - map_offset_x, path.y - map_offset_y))
    # Draw path2 tiles
    for path in path2_tiles:
        screen.blit(assets["path2"], (path.x - map_offset_x, path.y - map_offset_y))
    # Draw water tiles  
    for water in water_tiles:
        screen.blit(assets["water"], (water.x - map_offset_x, water.y - map_offset_y))
    # Draw stones
    for stone in stone_rects:
        screen.blit(assets["stone_img"], (stone.x - map_offset_x, stone.y - map_offset_y))

    # Draw trees
    for tree in tree_rects:
        screen.blit(assets["tree"], (tree.x - map_offset_x - tree_size_diff // 6, tree.y - map_offset_y - tree_size_diff // 6))

    # Draw flowers
    for fx, fy, idx in flower_tiles:
        screen.blit(assets["flowers"][idx], (fx - map_offset_x, fy - map_offset_y))

    # Draw leaves
    for lx, ly in leaf_tiles:
        screen.blit(assets["leaf"], (lx - map_offset_x, ly - map_offset_y))
    # Draw carrots
    for cx, cy, idx in carrot_tiles:
        if "carrot_tile" in assets:
            carrot_img = pygame.transform.scale(assets["carrot_tile"], (30, 30))

            screen.blit(carrot_img, (cx - map_offset_x, cy - map_offset_y))
    # Draw the dungeon portal
    if dungeon_portal:
        screen.blit(assets["portal"], (dungeon_portal.x - map_offset_x, dungeon_portal.y - map_offset_y))

    # Draw zone2 portal
    if zone2_portal:
        screen.blit(assets["portal"], (zone2_portal.x - map_offset_x, zone2_portal.y - map_offset_y ))
    # Draw all houses
    for i, house in enumerate(house_list):
        # Cycle through the 3 house types
        house_type = i % 3
        if house_type == 0:
            screen.blit(assets["house"], (house.x - map_offset_x, house.y - map_offset_y))
        elif house_type == 1:
            screen.blit(assets["house1"], (house.x - map_offset_x, house.y - map_offset_y))
        else:
            screen.blit(assets["house2"], (house.x - map_offset_x, house.y - map_offset_y))

    # Draw NPC with idle animation
    if npc_rect:
        animated_y = npc_rect.y + npc_idle_offset_y
        screen.blit(assets["npc_image"], (npc_rect.x - map_offset_x, animated_y - map_offset_y))
    
    # Draw Miner NPC with idle animation
    if miner_npc_rect:
        miner_animated_y = miner_npc_rect.y + miner_idle_offset_y
        screen.blit(assets["miner_image"], (miner_npc_rect.x - map_offset_x, miner_animated_y - map_offset_y))


def get_shop_items(assets):
    """Returns the items available in the shop with their prices."""
    return {
        "Potion": {"item": assets["potion_item"], "buy_price": 15, "sell_price": 8},
        "Potion2": {"item": assets["potion2_item"], "buy_price": 30, "sell_price": 15},
        "Log": {"item": assets["log_item"], "buy_price": 5, "sell_price": 2},
        "Stone": {"item": assets["stone_item"], "buy_price": 8, "sell_price": 3},
        "Ore": {"item": assets["ore_item"], "buy_price": 20, "sell_price": 12},
        "Flower": {"item": assets["flower_item"], "buy_price": 10, "sell_price": 4},
        "Carrot": {"item": assets["carrot_item"], "buy_price": 12, "sell_price": 4},
        "Crystal": {"item": assets["crystal_item"], "buy_price": 50, "sell_price": 25},
    }

def draw_vendor_gui(screen, assets):
    """Draws the vendor/shop GUI with close button."""
    global buy_button_rects, sell_button_rects, show_vendor_gui

    if not show_vendor_gui:
        return

    buy_button_rects = {}
    sell_button_rects = {}

    # --- Main panel ---
    panel_width = 600
    panel_height = 550
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

    pygame.draw.rect(screen, (101, 67, 33), panel_rect)
    pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)

    # --- Header ---
    header_rect = pygame.Rect(panel_x, panel_y, panel_width, 40)
    pygame.draw.rect(screen, (50, 33, 16), header_rect)
    header_text = assets["font"].render("Marcus's Trading Post", True, (255, 215, 0))
    screen.blit(header_text, header_text.get_rect(center=header_rect.center))

    # --- Close button (top-right corner) ---
    close_btn_size = 30
    close_btn_x = panel_x + panel_width - close_btn_size - 8
    close_btn_y = panel_y + 5
    close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)

    pygame.draw.rect(screen, (200, 0, 0), close_rect)  # Red background
    pygame.draw.rect(screen, (255, 255, 255), close_rect, 2)  # White border
    x_text = assets["small_font"].render("X", True, (255, 255, 255))
    screen.blit(x_text, x_text.get_rect(center=close_rect.center))

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    if close_rect.collidepoint(mouse_pos) and mouse_click:
        pygame.time.wait(150)
        show_vendor_gui = False
        print("❌ Vendor GUI closed.")

    # --- Tab buttons ---
    tab_width = 80
    tab_height = 30
    tab_y = panel_y + 45

    buy_tab_rect = pygame.Rect(panel_x + 20, tab_y, tab_width, tab_height)
    sell_tab_rect = pygame.Rect(panel_x + 110, tab_y, tab_width, tab_height)

    buy_color = (0, 120, 0) if vendor_tab == "buy" else (60, 60, 60)
    pygame.draw.rect(screen, buy_color, buy_tab_rect)
    pygame.draw.rect(screen, (255, 255, 255), buy_tab_rect, 2)
    buy_text = assets["small_font"].render("Buy", True, (255, 255, 255))
    screen.blit(buy_text, buy_text.get_rect(center=buy_tab_rect.center))

    sell_color = (120, 0, 0) if vendor_tab == "sell" else (60, 60, 60)
    pygame.draw.rect(screen, sell_color, sell_tab_rect)
    pygame.draw.rect(screen, (255, 255, 255), sell_tab_rect, 2)
    sell_text = assets["small_font"].render("Sell", True, (255, 255, 255))
    screen.blit(sell_text, sell_text.get_rect(center=sell_tab_rect.center))

    # --- Player coins display ---
    coin_count = get_item_count("Coin")
    coin_text = f"Coins: {coin_count}"
    coin_surf = assets["small_font"].render(coin_text, True, (255, 215, 0))
    screen.blit(coin_surf, (panel_x + panel_width - 120, tab_y + 5))

    # --- Content area ---
    content_y = tab_y + tab_height + 10
    content_height = panel_height - (content_y - panel_y) - 10

    shop_items = get_shop_items(assets)

    if vendor_tab == "buy":
        draw_buy_content(screen, assets, panel_x, content_y, panel_width, shop_items, coin_count)
    else:
        draw_sell_content(screen, assets, panel_x, content_y, panel_width, shop_items)

    # --- Store tab rects for interaction ---
    buy_button_rects["buy_tab"] = buy_tab_rect
    buy_button_rects["sell_tab"] = sell_tab_rect

def draw_buy_content(screen, assets, panel_x, content_y, panel_width, shop_items, coin_count):
    """Draws the buy tab content."""
    global buy_button_rects
    
    y_offset = content_y + 10
    item_height = 50
    
    for item_name, item_data in shop_items.items():
        item_rect = pygame.Rect(panel_x + 20, y_offset, panel_width - 40, item_height)
        
        # Can afford check
        can_afford = coin_count >= item_data["buy_price"]
        
        # Item background
        bg_color = (0, 80, 0) if can_afford else (80, 40, 40)
        pygame.draw.rect(screen, bg_color, item_rect)
        pygame.draw.rect(screen, (255, 255, 255), item_rect, 1)
        
        # Item icon
        icon_rect = pygame.Rect(panel_x + 30, y_offset + 5, 40, 40)
        item_image = pygame.transform.scale(item_data["item"].image, (40, 40))
        screen.blit(item_image, icon_rect)
        
        # Item name and price
        name_text = assets["small_font"].render(item_name, True, (255, 255, 255))
        screen.blit(name_text, (panel_x + 80, y_offset + 10))
        
        price_text = assets["small_font"].render(f"Price: {item_data['buy_price']} coins", True, (255, 215, 0))
        screen.blit(price_text, (panel_x + 80, y_offset + 25))
        
        # Buy button
        buy_button = pygame.Rect(panel_x + panel_width - 120, y_offset + 10, 80, 30)
        button_color = (0, 150, 0) if can_afford else (100, 100, 100)
        pygame.draw.rect(screen, button_color, buy_button)
        pygame.draw.rect(screen, (255, 255, 255), buy_button, 1)
        
        button_text = "Buy" if can_afford else "X"
        text_surf = assets["small_font"].render(button_text, True, (255, 255, 255))
        screen.blit(text_surf, text_surf.get_rect(center=buy_button.center))
        
        buy_button_rects[item_name] = buy_button
        y_offset += item_height + 5

def draw_sell_content(screen, assets, panel_x, content_y, panel_width, shop_items):
    """Draws the sell tab content."""
    global sell_button_rects
    
    y_offset = content_y + 10
    item_height = 50
    
    for item_name, item_data in shop_items.items():
        player_count = get_item_count(item_name)
        if player_count == 0:
            continue  # Don't show items player doesn't have
        
        item_rect = pygame.Rect(panel_x + 20, y_offset, panel_width - 40, item_height)
        
        # Item background
        pygame.draw.rect(screen, (80, 0, 0), item_rect)
        pygame.draw.rect(screen, (255, 255, 255), item_rect, 1)
        
        # Item icon
        icon_rect = pygame.Rect(panel_x + 30, y_offset + 5, 40, 40)
        item_image = pygame.transform.scale(item_data["item"].image, (40, 40))
        screen.blit(item_image, icon_rect)
        
        # Item name, count, and sell price
        name_text = assets["small_font"].render(f"{item_name} (x{player_count})", True, (255, 255, 255))
        screen.blit(name_text, (panel_x + 80, y_offset + 10))
        
        price_text = assets["small_font"].render(f"Sell for: {item_data['sell_price']} coins each", True, (255, 215, 0))
        screen.blit(price_text, (panel_x + 80, y_offset + 25))
        
        # Sell button
        sell_button = pygame.Rect(panel_x + panel_width - 120, y_offset + 10, 80, 30)
        pygame.draw.rect(screen, (150, 0, 0), sell_button)
        pygame.draw.rect(screen, (255, 255, 255), sell_button, 1)
        
        button_text = "Sell"
        text_surf = assets["small_font"].render(button_text, True, (255, 255, 255))
        screen.blit(text_surf, text_surf.get_rect(center=sell_button.center))
        
        sell_button_rects[item_name] = sell_button
        y_offset += item_height + 5

def draw_button(screen, text, x, y, width, height, assets, hover_color=(100, 100, 100), normal_color=(60, 60, 60)):
    """Draws a simple clickable button and returns True if clicked."""
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    
    rect = pygame.Rect(x, y, width, height)
    is_hovered = rect.collidepoint(mouse_pos)
    
    # Draw background
    color = hover_color if is_hovered else normal_color
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=8)
    
    # Text
    label = assets["small_font"].render(text, True, (255, 255, 255))
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    
    return is_hovered and mouse_pressed


def draw_npc_dialog(screen, assets):
    """Draws the NPC dialog box for Soldier Marcus with clickable buttons."""
    global show_npc_dialog, npc_quest_active, npc_quest_completed
    global vendor_gui, show_vendor_gui
    if not show_npc_dialog:
        return

    dialog_width = 500
    dialog_height = 180
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = HEIGHT - dialog_height - 20
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

    # --- Draw dialog box ---
    pygame.draw.rect(screen, (40, 40, 40), dialog_rect, border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), dialog_rect, 3, border_radius=8)

    # --- Name label ---
    name_text = assets["small_font"].render("Soldier Marcus", True, (255, 215, 0))
    screen.blit(name_text, (dialog_x + 10, dialog_y + 5))

    # --- Determine dialog text ---
    if not npc_quest_active and not npc_quest_completed:
        dialog_lines = [
            f"Greetings, Traveler! I'm in need of healing potions.",
            f"Could you brew {potions_needed} potions for us? I'd be grateful!"
        ]
        show_buttons = True
        accept_label = "Accept"
        decline_label = "Decline"

    elif npc_quest_active:
        potions_current = get_item_count("Potion")
        if potions_current >= potions_needed:
            dialog_lines = [
                f"Excellent! You have the {potions_needed} potions I needed!",
                "Please deliver them to complete the quest."
            ]
            show_buttons = True
            accept_label = "Deliver"
            decline_label = "Close"
        else:
            dialog_lines = [
                f"You currently have {potions_current}/{potions_needed} potions.",
                "Return when you have brewed enough for my unit!"
            ]
            show_buttons = False  # no buttons, just info

    elif npc_quest_completed:
        dialog_lines = [
            "Thanks for the potions! I've set up a trading post here.",
            "I can buy and sell various goods you might need."
        ]
        show_buttons = True
        npc_quest_completed = True
        accept_label = "Shop"
        decline_label = "Close"

    # --- Draw text lines ---
    y_offset = 35
    for line in dialog_lines:
        line_text = assets["small_font"].render(line, True, (255, 255, 255))
        screen.blit(line_text, (dialog_x + 10, dialog_y + y_offset))
        y_offset += 25

    # --- Draw buttons (if needed) ---
    if show_buttons:
        btn_width = 120
        btn_height = 35
        btn_y = dialog_y + dialog_height - btn_height - 10
        accept_x = dialog_x + 80
        decline_x = dialog_x + dialog_width - btn_width - 80

        if draw_button(screen, accept_label, accept_x, btn_y, btn_width, btn_height, assets):
            pygame.time.wait(150)

            # --- Accepting the quest ---
            if not npc_quest_active and not npc_quest_completed:
                npc_quest_active = True
                show_npc_dialog = False
                print("📝 NPC quest accepted!")

            # --- Completing the quest ---
            elif npc_quest_active:
                potions_current = get_item_count("Potion")
                if potions_current >= potions_needed:
                    remove_item_from_inventory("Potion", potions_needed)
                    npc_quest_active = False
                    npc_quest_completed = True
                    show_npc_dialog = False
                    print("✅ NPC quest completed! Vendor unlocked.")
                else:
                    print(f"❌ You need {potions_needed} potions. You have {potions_current}.")

            # --- Opening the vendor GUI ---
            elif npc_quest_completed:
                show_npc_dialog = False
                vendor_tab = "buy"
                show_vendor_gui = True
                get_shop_items(assets)
                print("🛒 Vendor GUI opened.")

                





        if draw_button(screen, decline_label, decline_x, btn_y, btn_width, btn_height, assets):
            pygame.time.wait(150)
            show_npc_dialog = False
            print("Dialog closed.")


def draw_miner_dialog(screen, assets):
    """Draws the Miner Gareth NPC dialog box with quest buttons and red close button."""
    global miner_quest_active, miner_quest_completed, show_miner_dialog

    if not show_miner_dialog:
        return

    # --- Dialog box setup ---
    dialog_width = 500
    dialog_height = 180
    dialog_x = (WIDTH - dialog_width) // 2
    dialog_y = HEIGHT - dialog_height - 20
    dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)

    pygame.draw.rect(screen, (40, 40, 40), dialog_rect)
    pygame.draw.rect(screen, (255, 255, 255), dialog_rect, 3)

    name_text = assets["small_font"].render("Miner Gareth", True, (139, 69, 19))
    screen.blit(name_text, (dialog_x + 10, dialog_y + 5))

    # --- Dialog lines ---
    dialog_lines = []
    ore_current = get_item_count("Ore")
    show_buttons = False
    accept_label = ""
    decline_label = ""

    if not miner_quest_active and not miner_quest_completed:
        dialog_lines = [
            "Ho there, adventurer! The mines below are crawling with beasts.",
            f"We need {ore_needed} ore chunks to restart the forge.",
            "Will you help us?"
        ]
        show_buttons = True
        accept_label = "Accept Quest"
        decline_label = "Decline"

    elif miner_quest_active:
        if ore_current >= ore_needed:
            dialog_lines = [
                f"You've gathered all {ore_needed} ore chunks!",
                "Ready to deliver and complete the quest?"
            ]
            show_buttons = True
            accept_label = "Deliver Ore"
            decline_label = "Cancel"
        else:
            dialog_lines = [
                f"You currently have {ore_current}/{ore_needed} ore chunks.",
                "The dungeon below should have plenty. Be careful!",
                "Press [ESC] to close."
            ]

    elif miner_quest_completed:
        dialog_lines = [
            "Thank you for the ore! Our smiths can work again.",
            "You've earned 15 coins for your bravery.",
            "May fortune smile upon your future adventures!",
            "Press [ESC] to close."
        ]

    # --- Render dialog text ---
    y_offset = 35
    for line in dialog_lines:
        line_text = assets["small_font"].render(line, True, (255, 255, 255))
        screen.blit(line_text, (dialog_x + 10, dialog_y + y_offset))
        y_offset += 25

    # --- Close button (top-right corner, red background) ---
    close_btn_size = 30
    close_btn_x = dialog_x + dialog_width - close_btn_size - 8
    close_btn_y = dialog_y + 8
    close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)

    pygame.draw.rect(screen, (200, 0, 0), close_rect)  # Red background
    pygame.draw.rect(screen, (255, 255, 255), close_rect, 2)  # White border
    x_text = assets["small_font"].render("X", True, (255, 255, 255))
    text_rect = x_text.get_rect(center=close_rect.center)
    screen.blit(x_text, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    if close_rect.collidepoint(mouse_pos) and mouse_click:
        pygame.time.wait(150)
        show_miner_dialog = False
        print("❌ Miner dialog closed via top-right button.")

    # --- Accept/Decline buttons ---
    if show_buttons:
        btn_width = 140
        btn_height = 35
        btn_y = dialog_y + dialog_height - btn_height - 10
        accept_x = dialog_x + 60
        decline_x = dialog_x + dialog_width - btn_width - 60

        if draw_button(screen, accept_label, accept_x, btn_y, btn_width, btn_height, assets):
            pygame.time.wait(150)

            if not miner_quest_active and not miner_quest_completed:
                miner_quest_active = True
                show_miner_dialog = False
                print("🪓 Miner quest accepted!")

            elif miner_quest_active and ore_current >= ore_needed:
                remove_item_from_inventory("Ore", ore_needed)
                miner_quest_active = False
                miner_quest_completed = True
                add_item_to_inventory("Coin", 15)
                show_miner_dialog = False
                print("✅ Miner quest completed! 15 coins rewarded.")

        if draw_button(screen, decline_label, decline_x, btn_y, btn_width, btn_height, assets):
            pygame.time.wait(150)
            show_miner_dialog = False
            print("❌ Miner dialog declined or closed.")

def draw_tooltip(screen, font, text, position):
    # Render text
    tooltip_surface = font.render(text, True, (255, 255, 255))
    tooltip_rect = tooltip_surface.get_rect(topleft=position)

    # Draw background rectangle
    pygame.draw.rect(screen, (0, 0, 0), tooltip_rect.inflate(6, 6))
    
    # Blit text on top
    screen.blit(tooltip_surface, tooltip_rect)

def draw_tooltip_for_nearby_objects(screen, font):
    """Draw a tooltip for interactive objects."""
    tooltip_text = None
    tooltip_pos = None
    mouse_pos = pygame.mouse.get_pos()
    player_world_rect = get_player_world_rect()

    if current_level == "world":
        # Portal Entry: check if near dungeon portal
        if dungeon_portal and player_world_rect.colliderect(dungeon_portal.inflate(20, 20)):
            tooltip_text = "Enter Dungeon [e]"
            portal_screen = world_to_screen_rect(dungeon_portal)
            tooltip_pos = (portal_screen.x, portal_screen.y)
        if zone2_portal and player_world_rect.colliderect(zone2_portal.inflate(20, 20)):
            tooltip_text = "Enter [e]"
            portal_screen = world_to_screen_rect(zone2_portal)
            tooltip_pos = (portal_screen.x, portal_screen.y)

        # Houses: show tooltip if near the player
        elif tooltip_text is None:
            house_index = check_house_entry(player_world_rect)
            if house_index is not None:
                house_screen = world_to_screen_rect(house_list[house_index])
                tooltip_text = "Enter [e]"
                tooltip_pos = (house_screen.x, house_screen.y)

        # Mouse hover tooltips for other objects...
        if tooltip_text is None:
            # Flowers: show only on mouse hover
            for fx, fy, idx in flower_tiles:
                flower_rect = pygame.Rect(fx - map_offset_x, fy - map_offset_y, 30, 30)
                if flower_rect.collidepoint(mouse_pos):
                    tooltip_text = "Flower [e]"
                    tooltip_pos = (fx - map_offset_x, fy - map_offset_y)
                    break
            # Carrots: show only on mouse hover
            for cx, cy, idx in carrot_tiles:
                carrot_rect = pygame.Rect(cx - map_offset_x, cy - map_offset_y, 30, 30)
                if carrot_rect.collidepoint(mouse_pos):
                    tooltip_text = "Carrot [e]"
                    tooltip_pos = (cx - map_offset_x, cy - map_offset_y)
                    break
        if tooltip_text is None:
            # Trees: show only on mouse hover
            for tree in tree_rects:
                tree_screen = world_to_screen_rect(tree)
                if tree_screen.collidepoint(mouse_pos) and tree not in house_list and tree != dungeon_portal:
                    tooltip_text = "Tree [e]"
                    tooltip_pos = (tree_screen.x, tree_screen.y)
                    break

        if tooltip_text is None:
            # Stones: show only on mouse hover
            for stone in stone_rects:
                stone_screen = world_to_screen_rect(stone)
                if stone_screen.collidepoint(mouse_pos):
                    tooltip_text = "Stone [e]"
                    tooltip_pos = (stone_screen.x, stone_screen.y)
                    break

        if tooltip_text is None:
            # Marcus: show only on mouse hover
            if npc_rect:
                marcus_screen = pygame.Rect(
                    npc_rect.x - map_offset_x,
                    npc_rect.y - map_offset_y + npc_idle_offset_y,
                    npc_rect.width,
                    npc_rect.height
                )
                if marcus_screen.collidepoint(mouse_pos):
                    tooltip_text = "Marcus [e]"
                    tooltip_pos = (marcus_screen.x, marcus_screen.y)

        if tooltip_text is None:
            # Miner: show only on mouse hover
            if miner_npc_rect:
                miner_screen = pygame.Rect(
                    miner_npc_rect.x - map_offset_x,
                    miner_npc_rect.y - map_offset_y + miner_idle_offset_y,
                    miner_npc_rect.width,
                    miner_npc_rect.height
                )
                if miner_screen.collidepoint(mouse_pos):
                    tooltip_text = "Miner Gareth [e]"
                    tooltip_pos = (miner_screen.x, miner_screen.y)

    elif current_level == "house":
        # Inside house: Exit door tooltip if near
        door_zone = pygame.Rect(WIDTH // 2 - 40, HEIGHT - 100, 80, 80)
        if player_pos.colliderect(door_zone):
            tooltip_text = "Exit [e]"
            tooltip_pos = door_zone.topleft
    elif current_level == "zone2":
        # Exit portal (proximity-based)
        if zone2_return_portal and player_world_rect.colliderect(zone2_return_portal.inflate(20, 20)):
            portal_screen = world_to_screen_rect(zone2_return_portal)
            tooltip_text = "Exit [e]"
            tooltip_pos = (portal_screen.x, portal_screen.y)

        # Mouse hover tooltips if nothing else yet
        if tooltip_text is None:
            # Trees
            for tree in tree_rects:
                tree_screen = world_to_screen_rect(tree)
                if tree_screen.collidepoint(mouse_pos):
                    tooltip_text = "Tree [e]"
                    tooltip_pos = (tree_screen.x, tree_screen.y)
                    break

        if tooltip_text is None:
            # Stones
            for stone in stone_rects:
                stone_screen = world_to_screen_rect(stone)
                if stone_screen.collidepoint(mouse_pos):
                    tooltip_text = "Stone [e]"
                    tooltip_pos = (stone_screen.x, stone_screen.y)
                    break

        if tooltip_text is None:
            # Crystals
            for crystal in crystal_rects:
                crystal_screen = world_to_screen_rect(crystal)
                if crystal_screen.collidepoint(mouse_pos):
                    tooltip_text = "Crystal [e]"
                    tooltip_pos = (crystal_screen.x, crystal_screen.y)
                    break

        if tooltip_text is None:
            # Flowers
            for fx, fy, idx in flower_tiles:
                flower_rect = pygame.Rect(fx - map_offset_x, fy - map_offset_y, 30, 30)
                if flower_rect.collidepoint(mouse_pos):
                    tooltip_text = "Flower [e]"
                    tooltip_pos = (fx - map_offset_x, fy - map_offset_y)
                    break

        if tooltip_text is None:
            # Merchant
            if zone2_merchant_rect:
                merchant_screen = pygame.Rect(
                    zone2_merchant_rect.x - map_offset_x,
                    zone2_merchant_rect.y - map_offset_y,
                    zone2_merchant_rect.width,
                    zone2_merchant_rect.height
                )
                if merchant_screen.collidepoint(mouse_pos):
                    tooltip_text = "Merchant [e]"
                    tooltip_pos = (merchant_screen.x, merchant_screen.y)


    elif current_level == "dungeon":
        # Inside dungeon: Boss door check (proximity-based, not mouse hover)
        if boss1_portal and player_world_rect.colliderect(boss1_portal.inflate(30, 30)):
            boss_screen = world_to_screen_rect(boss1_portal)
            tooltip_text = "Boss Door [e]"
            tooltip_pos = (boss_screen.x, boss_screen.y)
        
        # Exit portal tooltip if near
        elif dungeon_exit and player_world_rect.colliderect(dungeon_exit.inflate(20, 20)):
            exit_screen = world_to_screen_rect(dungeon_exit)
            tooltip_text = "Exit Dungeon [e]"
            tooltip_pos = (exit_screen.x, exit_screen.y)
        
        # Dungeon ore: show only on mouse hover
        elif tooltip_text is None:
            for stone in stone_rects:
                stone_screen = world_to_screen_rect(stone)
                if stone_screen.collidepoint(mouse_pos):
                    tooltip_text = "Ore Deposit [e]"
                    tooltip_pos = (stone_screen.x, stone_screen.y)
                    break

        # Enemy tooltips on mouse hover
        if tooltip_text is None:
            for enemy in enemies:
                enemy_screen = world_to_screen_rect(enemy.rect)
                if enemy_screen.collidepoint(mouse_pos):
                    tooltip_text = f"{enemy.type.title()} [SPACE to attack]"
                    tooltip_pos = (enemy_screen.x, enemy_screen.y)
                    break

    # Draw the tooltip if we have text and position
    if tooltip_text and tooltip_pos:
        draw_tooltip(screen, font, tooltip_text, tooltip_pos)

def draw_inventory(screen, assets):
    """Draws the inventory GUI with a close button."""
    global show_inventory

    if not show_inventory:
        return

    # --- Panel background ---
    panel_rect = pygame.Rect(INVENTORY_X, INVENTORY_Y, INVENTORY_WIDTH, INVENTORY_HEIGHT + 50)
    pygame.draw.rect(screen, (101, 67, 33), panel_rect)
    pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2)

    # --- Header ---
    header_rect = pygame.Rect(INVENTORY_X, INVENTORY_Y, INVENTORY_WIDTH, 40)
    pygame.draw.rect(screen, (50, 33, 16), header_rect)
    header_text = assets["small_font"].render("Backpack", True, (255, 255, 255))
    screen.blit(header_text, header_text.get_rect(centerx=header_rect.centerx, top=INVENTORY_Y + 10))

    # --- Close button (top-right corner) ---
    close_btn_size = 30
    close_btn_x = INVENTORY_X + INVENTORY_WIDTH - close_btn_size - 8
    close_btn_y = INVENTORY_Y + 5
    close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)

    pygame.draw.rect(screen, (200, 0, 0), close_rect)  # red background
    pygame.draw.rect(screen, (255, 255, 255), close_rect, 2)  # white border
    x_text = assets["small_font"].render("X", True, (255, 255, 255))
    screen.blit(x_text, x_text.get_rect(center=close_rect.center))

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    if close_rect.collidepoint(mouse_pos) and mouse_click:
        pygame.time.wait(150)
        show_inventory = False
        print("❌ Inventory closed.")

    # --- Inventory slots ---
    for row in range(4):
        for col in range(4):
            slot_x = INVENTORY_X + INVENTORY_GAP + col * (INVENTORY_SLOT_SIZE + INVENTORY_GAP)
            slot_y = INVENTORY_Y + 40 + INVENTORY_GAP + row * (INVENTORY_SLOT_SIZE + INVENTORY_GAP)
            slot_rect = pygame.Rect(slot_x, slot_y, INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)

            pygame.draw.rect(screen, (70, 70, 70), slot_rect)
            pygame.draw.rect(screen, (150, 150, 150), slot_rect, 2)

            item = inventory[row][col]
            if item:
                screen.blit(
                    pygame.transform.scale(item.image, (INVENTORY_SLOT_SIZE, INVENTORY_SLOT_SIZE)),
                    slot_rect
                )
                if item.count > 1:
                    count_text = assets["small_font"].render(str(item.count), True, (255, 255, 255))
                    screen.blit(count_text, count_text.get_rect(bottomright=slot_rect.bottomright))

def draw_crafting_panel(screen, assets, is_hovering):
    """Draws the crafting GUI with tabs for smithing and alchemy, plus a close button."""
    global axe_button_rect, pickaxe_button_rect,potion2_button_rect, potion_button_rect, sword_button_rect
    global alchemy_tab_rect, smithing_tab_rect, cooking_tab_rect, show_crafting, crafting_tab

    if not show_crafting:
        return

    # --- Panel setup ---
    panel_rect = pygame.Rect(CRAFTING_X, CRAFTING_Y, CRAFTING_PANEL_WIDTH, CRAFTING_PANEL_HEIGHT)
    pygame.draw.rect(screen, (80, 50, 20), panel_rect, border_radius=10)
    pygame.draw.rect(screen, (220, 220, 220), panel_rect, 3, border_radius=10)

    # --- Header ---
    header_rect = pygame.Rect(CRAFTING_X, CRAFTING_Y, CRAFTING_PANEL_WIDTH, 35)
    pygame.draw.rect(screen, (50, 33, 16), header_rect)
    header_text = assets["small_font"].render("Crafting", True, (255, 255, 255))
    screen.blit(header_text, header_text.get_rect(centerx=header_rect.centerx, centery=header_rect.centery))

    # --- Close button (top-right corner) ---
    close_btn_size = 30
    close_btn_x = CRAFTING_X + CRAFTING_PANEL_WIDTH - close_btn_size - 8
    close_btn_y = CRAFTING_Y + 3
    close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)

    pygame.draw.rect(screen, (200, 0, 0), close_rect)  # red background
    pygame.draw.rect(screen, (255, 255, 255), close_rect, 2)  # white border
    x_text = assets["small_font"].render("X", True, (255, 255, 255))
    screen.blit(x_text, x_text.get_rect(center=close_rect.center))

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    if close_rect.collidepoint(mouse_pos) and mouse_click:
        pygame.time.wait(150)
        show_crafting = False
        print("❌ Crafting panel closed.")

    # --- Tab buttons ---
    tab_width = 90
    tab_height = 25
    tab_y = CRAFTING_Y + 40
    tab_spacing = 10

    smithing_tab_rect = pygame.Rect(CRAFTING_X + tab_spacing, tab_y, tab_width, tab_height)
    alchemy_tab_rect = pygame.Rect(CRAFTING_X + tab_spacing + tab_width + 5, tab_y, tab_width, tab_height)
    cooking_tab_rect = pygame.Rect(
        CRAFTING_X + tab_spacing + 2 * (tab_width + 5),
        tab_y,
        tab_width,
        tab_height
    )

    cooking_color = (150, 100, 50) if crafting_tab == "cooking" else (60, 60, 60)
    pygame.draw.rect(screen, cooking_color, cooking_tab_rect)
    pygame.draw.rect(screen, (255, 255, 255), cooking_tab_rect, 2)
    cooking_text = assets["small_font"].render("Cooking", True, (255, 255, 255))
    screen.blit(cooking_text, cooking_text.get_rect(center=cooking_tab_rect.center))


    smithing_color = (80, 150, 80) if crafting_tab == "smithing" else (60, 60, 60)
    pygame.draw.rect(screen, smithing_color, smithing_tab_rect)
    pygame.draw.rect(screen, (255, 255, 255), smithing_tab_rect, 2)
    smithing_text = assets["small_font"].render("Smithing", True, (255, 255, 255))
    screen.blit(smithing_text, smithing_text.get_rect(center=smithing_tab_rect.center))

    alchemy_color = (80, 80, 150) if crafting_tab == "alchemy" else (60, 60, 60)
    pygame.draw.rect(screen, alchemy_color, alchemy_tab_rect)
    pygame.draw.rect(screen, (255, 255, 255), alchemy_tab_rect, 2)
    alchemy_text = assets["small_font"].render("Alchemy", True, (255, 255, 255))
    screen.blit(alchemy_text, alchemy_text.get_rect(center=alchemy_tab_rect.center))

    # --- Content area ---
    content_y = tab_y + tab_height + 10
    content_height = CRAFTING_PANEL_HEIGHT - (content_y - CRAFTING_Y)

    if crafting_tab == "smithing":
        draw_smithing_content(screen, assets, content_y)
    elif crafting_tab == "alchemy":
        draw_alchemy_content(screen, assets, content_y)
def draw_cooking_content(screen, assets, content_y):
    """Draws the cooking crafting options (food recipes)."""
    global stew_button_rect, bread_button_rect

    button_width, button_height, gap = 180, 50, 20
    meat_count = get_item_count("Meat")
    herb_count = get_item_count("Herb")
    wheat_count = get_item_count("Wheat")

    # Example recipes
    stew_button_rect = pygame.Rect(CRAFTING_X + gap, content_y + gap, button_width, button_height)
    bread_button_rect = pygame.Rect(CRAFTING_X + gap, content_y + gap + (button_height + gap), button_width, button_height)

    recipes = [
        (stew_button_rect, "Stew", {"Meat": 2, "Herb": 1}),
        (bread_button_rect, "Bread", {"Wheat": 3}),
    ]

    mouse_pos = pygame.mouse.get_pos()

    for rect, name, reqs in recipes:
        can_craft = all(get_item_count(item) >= count for item, count in reqs.items())

        # Default text
        text_to_display = f"Cook {name}"
        color = (150, 100, 50) if can_craft else (70, 50, 30)

        # Hover shows requirements inside button
        if rect.collidepoint(mouse_pos):
            req_text = ", ".join(f"{item} {get_item_count(item)}/{count}" for item, count in reqs.items())
            text_to_display = f"{name}: {req_text}"
            color = (200, 120, 60) if can_craft else (80, 60, 40)

        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)

        text_surface = assets["small_font"].render(text_to_display, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
def draw_smithing_content(screen, assets, content_y):

    global axe_button_rect, pickaxe_button_rect, chest_button_rect, helmet_button_rect, boots_button_rect
    global sword_button_rect
    button_width, button_height, gap = 180, 50, 20
    log_count = get_item_count("Log")
    stone_count = get_item_count("Stone")
    ore_count = get_item_count("Ore")

    col1_x = CRAFTING_X + gap
    col2_x = CRAFTING_X + gap + button_width + gap
    
    axe_button_rect = pygame.Rect(col1_x, content_y + gap, button_width, button_height)
    pickaxe_button_rect = pygame.Rect(col1_x, content_y + gap + (button_height + gap), button_width, button_height)
    sword_button_rect = pygame.Rect(col1_x, content_y + gap + 2 * (button_height + gap), button_width, button_height)
    helmet_button_rect = pygame.Rect(col2_x, content_y + gap, button_width, button_height)
    chest_button_rect = pygame.Rect(col2_x, content_y + gap + (button_height + gap), button_width, button_height)
    boots_button_rect = pygame.Rect(col2_x, content_y + gap + 2 * (button_height + gap), button_width, button_height)
    
    buttons = [
        (axe_button_rect, "axe", 5, assets["axe_item"], "Log", log_count),
        (pickaxe_button_rect, "pickaxe", 2, assets["pickaxe_item"], "log", log_count),
        (sword_button_rect, "sword", 2, assets["sword_item"], "ore", ore_count),
        (helmet_button_rect, "helmet", 8, assets["helmet_item"], "Stone", stone_count),
        (chest_button_rect, "chest", 15, assets["chest_item"], "Stone", stone_count),
        (boots_button_rect, "boots", 6, assets["boots_item"], "Stone", stone_count),
    ]
    
    mouse_pos = pygame.mouse.get_pos()
    
    for rect, item_name, required_amount, item_obj, material_type, material_count in buttons:
        can_craft = material_count >= required_amount
        
        if is_crafting and item_to_craft and item_to_craft.name.lower().replace(" ", "") == item_name.replace("_", ""):
            progress = (crafting_timer / CRAFTING_TIME_MS) * 100
            text_to_display = f"Crafting... {int(progress)}%"
            color = (120, 120, 120)
        
        elif rect.collidepoint(mouse_pos):
            text_to_display = f"{item_obj.name}: {material_count}/{required_amount} {material_type}"
            color = (0, 100, 0) if can_craft else (50, 50, 50)
        
        else:
            text_to_display = f"Craft {item_obj.name}"
            color = (0, 150, 0) if can_craft else (70, 70, 70)
        
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (150, 150, 150), rect, 2)
        
        text_surface = assets["small_font"].render(text_to_display, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        if text_rect.width > rect.width - 10:
            scale_factor = (rect.width - 10) / text_rect.width
            new_width = int(text_rect.width * scale_factor)
            new_height = int(text_rect.height * scale_factor)
            text_surface = pygame.transform.scale(text_surface, (new_width, new_height))
        
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def draw_alchemy_content(screen, assets, content_y):
    """Draws the alchemy crafting options."""
    global potion_button_rect
    global potion2_button_rect

    button_width, button_height, gap = 180, 50, 20
    flower_count = get_item_count("Flower")

    mouse_pos = pygame.mouse.get_pos()

    # ===== Potion 1 =====
    potion_button_rect = pygame.Rect(CRAFTING_X + gap, content_y + gap, button_width, button_height)
    req_flowers = 3
    can_craft = flower_count >= req_flowers

    if is_crafting and item_to_craft and item_to_craft.name == "Potion":
        progress = (crafting_timer / CRAFTING_TIME_MS) * 100
        text_to_display = f"Brewing... {int(progress)}%"
        color = (120, 120, 120)
    elif potion_button_rect.collidepoint(mouse_pos):
        text_to_display = f"Req: {flower_count}/{req_flowers} Flowers"
        color = (100, 0, 100) if can_craft else (50, 50, 50)
    else:
        text_to_display = "Health Potion"
        color = (150, 0, 150) if can_craft else (70, 70, 70)

    pygame.draw.rect(screen, color, potion_button_rect)
    pygame.draw.rect(screen, (150, 150, 150), potion_button_rect, 2)

    text_surface = assets["small_font"].render(text_to_display, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=potion_button_rect.center)
    screen.blit(text_surface, text_rect)

    # ===== Potion 2 =====
    potion2_button_rect = pygame.Rect(
        CRAFTING_X + gap, potion_button_rect.bottom + gap, button_width, button_height
    )
    req_flowers2 = 5
    can_craft2 = flower_count >= req_flowers2

    if is_crafting and item_to_craft and item_to_craft.name == "Potion 2":
        progress = (crafting_timer / CRAFTING_TIME_MS) * 100
        text_to_display2 = f"Brewing... {int(progress)}%"
        color2 = (120, 120, 120)
    elif potion2_button_rect.collidepoint(mouse_pos):
        text_to_display2 = f"Req: {flower_count}/{req_flowers2} Flowers"
        color2 = (0, 100, 150) if can_craft2 else (50, 50, 50)
    else:
        text_to_display2 = "Speed Potion"
        color2 = (0, 150, 200) if can_craft2 else (70, 70, 70)

    pygame.draw.rect(screen, color2, potion2_button_rect)
    pygame.draw.rect(screen, (150, 150, 150), potion2_button_rect, 2)

    text_surface2 = assets["small_font"].render(text_to_display2, True, (255, 255, 255))
    text_rect2 = text_surface2.get_rect(center=potion2_button_rect.center)
    screen.blit(text_surface2, text_rect2)

def draw_equipment_panel(screen, assets):
    """Draws a polished equipment GUI with 2 rows, 4 columns, stats display, and a close button."""
    global equipment_slots, show_equipment

    if not show_equipment:
        return

    # --- Panel background ---
    panel_rect = pygame.Rect(
        EQUIPMENT_X, EQUIPMENT_Y,
        EQUIPMENT_PANEL_WIDTH + 100,
        EQUIPMENT_PANEL_HEIGHT + 60
    )
    pygame.draw.rect(screen, (80, 50, 20), panel_rect, border_radius=10)
    pygame.draw.rect(screen, (220, 220, 220), panel_rect, 3, border_radius=10)

    # --- Header ---
    header_rect = pygame.Rect(EQUIPMENT_X, EQUIPMENT_Y, panel_rect.width, 40)
    pygame.draw.rect(screen, (40, 25, 10), header_rect, border_radius=6)
    header_text = assets["font"].render("Equipment", True, (255, 215, 0))
    screen.blit(header_text, header_text.get_rect(center=header_rect.center))

    # --- Close button (top-right corner) ---
    close_btn_size = 30
    close_btn_x = EQUIPMENT_X + panel_rect.width - close_btn_size - 8
    close_btn_y = EQUIPMENT_Y + 5
    close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)

    pygame.draw.rect(screen, (200, 0, 0), close_rect)
    pygame.draw.rect(screen, (255, 255, 255), close_rect, 2)
    x_text = assets["small_font"].render("X", True, (255, 255, 255))
    screen.blit(x_text, x_text.get_rect(center=close_rect.center))

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    if close_rect.collidepoint(mouse_pos) and mouse_click:
        pygame.time.wait(150)
        show_equipment = False
        print("❌ Equipment panel closed.")
    
    # --- Slot layout ---
    slot_names = [
        ["weapon", "helmet", "armor", "boots"],
        ["ring1", "ring2", "amulet", "shield"]
    ]
    slot_labels = {
        "weapon": "Weapon", "helmet": "Helmet", "armor": "Chest", "boots": "Boots",
        "ring1": "Ring", "ring2": "Ring", "amulet": "Amulet", "shield": "Shield"
    }

    slot_rects = {}
    start_y = EQUIPMENT_Y + 55

    for row in range(EQUIPMENT_ROWS):
        for col in range(EQUIPMENT_COLS):
            slot_x = EQUIPMENT_X + EQUIPMENT_GAP + col * (EQUIPMENT_SLOT_SIZE + EQUIPMENT_GAP + 30)
            slot_y = start_y + row * (EQUIPMENT_SLOT_SIZE + EQUIPMENT_GAP + 35)

            slot_rect = pygame.Rect(slot_x, slot_y, EQUIPMENT_SLOT_SIZE, EQUIPMENT_SLOT_SIZE)
            slot_name = slot_names[row][col]

            pygame.draw.rect(screen, (70, 70, 70), slot_rect, border_radius=6)
            pygame.draw.rect(screen, (180, 180, 180), slot_rect, 2, border_radius=6)

            equipped_item = equipment_slots.get(slot_name)
            if equipped_item and equipped_item.image:
                item_image = pygame.transform.smoothscale(
                    equipped_item.image,
                    (EQUIPMENT_SLOT_SIZE - 4, EQUIPMENT_SLOT_SIZE - 4)
                )
                screen.blit(item_image, item_image.get_rect(center=slot_rect.center))

            label_text = assets["small_font"].render(slot_labels[slot_name], True, (230, 230, 230))
            label_rect = label_text.get_rect(centerx=slot_rect.centerx, top=slot_rect.bottom + 4)
            screen.blit(label_text, label_rect)

            slot_rects[slot_name] = slot_rect

    # --- Stats box ---
    stats_y = start_y + (EQUIPMENT_ROWS * (EQUIPMENT_SLOT_SIZE + EQUIPMENT_GAP + 35)) + 15
    stats_rect = pygame.Rect(EQUIPMENT_X + 10, stats_y, panel_rect.width - 20, 70)
    pygame.draw.rect(screen, (25, 25, 25), stats_rect, border_radius=8)
    pygame.draw.rect(screen, (160, 160, 160), stats_rect, 2, border_radius=8)

    total_damage_bonus = sum(getattr(item, 'damage', 0) for item in equipment_slots.values() if item)
    total_defense_bonus = sum(getattr(item, 'defense', 0) for item in equipment_slots.values() if item)

    player_total_defense = player.get_total_defense()
    equipped_weapon = equipment_slots.get("weapon")
    weapon_name = equipped_weapon.name if equipped_weapon else "None"

    stats_lines = [
        (assets.get("sword_icon"), f"Main Hand: {weapon_name}  |  +{total_damage_bonus} Damage"),
        (assets.get("shield_icon"), f"Defense: {player_total_defense} (+{total_defense_bonus})")
    ]

    line_height = assets["small_font"].get_height() + 6
    for i, (icon, line) in enumerate(stats_lines):
        y = stats_rect.top + 10 + i * line_height
        if icon:
            screen.blit(icon, (stats_rect.left + 10, y))
        text_surf = assets["small_font"].render(line, True, (240, 240, 240))
        text_rect = text_surf.get_rect(midleft=(stats_rect.left + 40, y + 10))
        screen.blit(text_surf, text_rect)

    return slot_rects

hud_buttons = {}
def draw_quests_panel(screen, assets):
    """Draws the player's active quests panel with close button."""
    global show_quests, npc_quest_active, npc_quest_completed, miner_quest_active, miner_quest_completed

    if not show_quests:
        return

    panel_width = 400
    panel_height = 250
    panel_x = WIDTH - panel_width - 20
    panel_y = 100
    panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
    pygame.draw.rect(screen, (35, 35, 45), panel_rect)
    pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2)

    title = assets["font"].render("Active Quests", True, (255, 215, 0))
    screen.blit(title, (panel_x + 20, panel_y + 15))

    # --- Close button ---
    close_btn_size = 30
    close_btn_x = panel_x + panel_width - close_btn_size - 8
    close_btn_y = panel_y + 8
    close_rect = pygame.Rect(close_btn_x, close_btn_y, close_btn_size, close_btn_size)

    pygame.draw.rect(screen, (200, 0, 0), close_rect)
    pygame.draw.rect(screen, (255, 255, 255), close_rect, 2)
    x_text = assets["small_font"].render("X", True, (255, 255, 255))
    screen.blit(x_text, x_text.get_rect(center=close_rect.center))

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()[0]
    if close_rect.collidepoint(mouse_pos) and mouse_click:
        pygame.time.wait(150)
        show_quests = False
        print("❌ Quests panel closed.")

    y_offset = 60
    lines = []

    if npc_quest_active:
        lines += [
            "Soldier Marcus:",
            f" • Gather {potions_needed} Healing Potions",
            f" • Progress: {get_item_count('Potion')}/{potions_needed}",
        ]
    elif npc_quest_completed:
        lines += ["Soldier Marcus:", " ✓ Quest completed!"]

    if miner_quest_active:
        lines += [
            "",
            "Miner Gareth:",
            f" • Collect {ore_needed} Ore Chunks",
            f" • Progress: {get_item_count('Ore')}/{ore_needed}",
        ]
    elif miner_quest_completed:
        lines += ["", "Miner Gareth:", " ✓ Quest completed!"]

    if not lines:
        lines = ["No active quests."]

    for line in lines:
        color = (255, 255, 255)
        if "✓" in line:
            color = (100, 255, 100)
        text = assets["small_font"].render(line, True, color)
        screen.blit(text, (panel_x + 20, panel_y + y_offset))
        y_offset += 25

def draw_hud(screen, assets):
    global hud_buttons
    hud_buttons = {}

    icons = [
        ("inventory", assets["backpack_icon"], "", "Inventory"),
        ("crafting", assets["crafting_icon"], "", "Crafting"),
        ("equipment", assets["equipment_icon"], "", "Equipment"),
        ("quests", assets["quest_icon"], "", "Quests")
    ]

    mouse_pos = pygame.mouse.get_pos()

    spacing = 60 
    start_x = WIDTH - 50
    y_pos = HEIGHT - 40

    for i, (name, icon, label, tooltip) in enumerate(icons):
        # --- Scale icon up slightly ---
        scale_factor = 1.3   # 30% bigger
        new_size = (int(icon.get_width() * scale_factor),
                    int(icon.get_height() * scale_factor))
        icon_scaled = pygame.transform.smoothscale(icon, new_size)

        x_pos = start_x - i * spacing
        icon_rect = icon_scaled.get_rect(centerx=x_pos, bottom=y_pos)

        # Draw icon and label
        screen.blit(icon_scaled, icon_rect)
        label_text = assets["small_font"].render(label, True, (255, 255, 255))
        label_rect = label_text.get_rect(centerx=icon_rect.centerx, top=icon_rect.bottom + 5)
        screen.blit(label_text, label_rect)

        hud_buttons[name] = icon_rect

        # Hover tooltip
        if icon_rect.collidepoint(mouse_pos):
            tooltip_text = assets["small_font"].render(tooltip, True, (255, 255, 0))
            tooltip_rect = tooltip_text.get_rect(centerx=icon_rect.centerx, bottom=icon_rect.top - 5)
            bg_rect = tooltip_rect.inflate(6, 4)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            screen.blit(tooltip_text, tooltip_rect)



# --- MAIN GAME LOGIC ---
def handle_movement(keys):
    global current_direction, last_direction, player_movement_history

    speed = player.get_current_speed()
    dx = dy = 0
    new_direction = None

    if keys[pygame.K_a]:
        dx -= speed
        new_direction = "left"
    if keys[pygame.K_d]:
        dx += speed
        new_direction = "right"
    if keys[pygame.K_w]:
        dy -= speed
        new_direction = "up"
    if keys[pygame.K_s]:
        dy += speed
        new_direction = "down"


    # Update directions and track movement
    if new_direction:

        current_direction = new_direction
        last_direction = new_direction

        current_time = pygame.time.get_ticks()
        player_movement_history.append((new_direction, current_time))

        # Keep only recent movement (last 500ms)
        player_movement_history = [
            (direction, timestamp) for direction, timestamp in player_movement_history
            if current_time - timestamp < 500
        ]
    else:
        current_direction = "idle"

    return dx, dy


def handle_collision(new_world_rect):
    """Checks for collision with world objects depending on current level."""
    if current_level == "world":
        if any(new_world_rect.colliderect(r) for r in tree_rects + stone_rects):
            return True
        return False
    elif current_level == "dungeon":
        if any(new_world_rect.colliderect(r) for r in dungeon_walls + stone_rects):
            return True
        return False
    elif current_level == "boss_room":
        # Allow free movement except for walls loaded from map
        if any(new_world_rect.colliderect(r) for r in boss_room_walls):
            return True
        return False
    elif current_level == "zone2":
        # Check collision with trees and water
        if any(new_world_rect.colliderect(r) for r in tree_rects + crystal_rects):
            return True
        # Check water collision (blocks movement)
        for wx, wy in water_tiles:
            water_rect = pygame.Rect(wx, wy, TILE_SIZE, TILE_SIZE)
            if new_world_rect.colliderect(water_rect):
                return True
        return False
    else:  # house
        return any(new_world_rect.colliderect(r) for r in indoor_colliders)


def check_house_entry(world_rect):
    """Checks if the player is near a house door in the world."""
    for i, h in enumerate(house_list):
        if world_rect.colliderect(h.inflate(20, 20)):
            return i
    return None


def use_potion():
    """Uses a potion from inventory to heal the player."""
    if get_item_count("Potion") > 0:
        remove_item_from_inventory("Potion", 1)
        heal_amount = 50
        player.heal(heal_amount)
        print(f"Used potion! Healed {heal_amount} HP. Current health: {player.health}/{player.max_health}")
        return True
    else:
        print("No potions available!")
        return False

def use_potion2():
    """Uses a speed potion from inventory to temporarily increase player speed."""
    if get_item_count("Potion 2") > 0:
        remove_item_from_inventory("Potion 2", 1)
        speed_boost = 2.0      # Speed multiplier
        boost_duration = 5000  # milliseconds (5 seconds)

        if not getattr(player, "speed_boost_active", False):
            player.speed *= speed_boost
            player.speed_boost_active = True
            player.speed_boost_end_time = pygame.time.get_ticks() + boost_duration

            print("Used Potion 2! Speed boosted temporarily.")
            return True
        else:
            print("Speed boost already active!")
            return False
    else:
        print("No speed potions available!")
        return False
def handle_main_menu_events(screen, assets, dt):
    global game_state, menu_selected_option
    
    # menu music
    play_music("main_menu")

    # Get mouse position for hover detection
    mouse_pos = pygame.mouse.get_pos()
    
    # Define menu option rectangles (you'll need these for click detection)
    menu_options = ["New Game", "Load Game", "Exit"]
    option_rects = []

    for i, option in enumerate(menu_options):
        option_text = assets["font"].render(option, True, (255, 255, 255))
        option_rect = option_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
        option_rects.append(option_rect)
    
    # Check for mouse hover to update selected option
    for i, rect in enumerate(option_rects):
        if rect.collidepoint(mouse_pos):
            menu_selected_option = i
            break
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # Keyboard navigation
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                menu_selected_option = (menu_selected_option - 1) % 3
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                menu_selected_option = (menu_selected_option + 1) % 3
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                execute_menu_option()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse click handling
            if event.button == 1:  # Left mouse button
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        menu_selected_option = i
                        execute_menu_option()
                        break
    
    draw_main_menu(screen, assets)
    pygame.display.flip()

def execute_save_slot_selection():
    """Execute the selected save slot."""
    global game_state
    
    if load_game_data(selected_save_slot):
        game_state = "playing"
        setup_colliders()
    else:
        start_new_game()
        game_state = "playing"
def clamp_camera_to_zone2():
    """Prevent camera from going beyond zone2 map boundaries."""
    global map_offset_x, map_offset_y
    ZONE2_MAP_WIDTH = 50 * TILE_SIZE  # Example: 50 tiles wide
    ZONE2_MAP_HEIGHT = 50 * TILE_SIZE  # Example: 50 tiles tall
    
    # Clamp horizontal offset
    max_offset_x = ZONE2_MAP_WIDTH - WIDTH
    map_offset_x = max(0, min(map_offset_x, max_offset_x))
    
    # Clamp vertical offset
    max_offset_y = ZONE2_MAP_HEIGHT - HEIGHT
    map_offset_y = max(0, min(map_offset_y, max_offset_y))

def execute_menu_option():
    """Execute the selected menu option."""
    global game_state
    
    if menu_selected_option == 0:  # New Game
        start_new_game()
        game_state = "playing"
    elif menu_selected_option == 1:  # Load Game
        game_state = "save_select"
    elif menu_selected_option == 2:  # Exit
        pygame.quit()
        sys.exit()

def handle_save_select_events(screen, assets, dt):
    global game_state, selected_save_slot
    
    # Get mouse position
    mouse_pos = pygame.mouse.get_pos()
    
    # Define save slot rectangles
    slot_rects = []
    for i in range(4):
        slot_y = HEIGHT // 2 + i * 60 - 120
        slot_rect = pygame.Rect(WIDTH // 2 - 200, slot_y, 400, 50)
        slot_rects.append(slot_rect)
    
    # Check for mouse hover
    for i, rect in enumerate(slot_rects):
        if rect.collidepoint(mouse_pos):
            selected_save_slot = i + 1
            break
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # Keyboard navigation
            if event.key == pygame.K_UP:
                selected_save_slot = max(1, selected_save_slot - 1)
            elif event.key == pygame.K_DOWN:
                selected_save_slot = min(4, selected_save_slot + 1)
            elif event.key == pygame.K_RETURN:
                execute_save_slot_selection()
            elif event.key == pygame.K_ESCAPE:
                game_state = "main_menu"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Mouse click handling
            if event.button == 1:  # Left mouse button
                for i, rect in enumerate(slot_rects):
                    if rect.collidepoint(event.pos):
                        selected_save_slot = i + 1
                        execute_save_slot_selection()
                        break
    
    draw_save_select_menu(screen, assets)
    pygame.display.flip()

def handle_boss_door(player_world_rect, assets):
    """Checks for boss door interaction inside dungeon."""
    global current_level
    global boss_door

    if boss_door and player_world_rect.colliderect(boss_door.inflate(20, 20)):
        # Show tooltip
        font = assets["small_font"]
        text = font.render("Press E to enter Boss Room", True, (255, 255, 255))
        screen = pygame.display.get_surface()
        screen.blit(text, (boss_door.x, boss_door.y - 30))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            # Switch to boss room
            spawn_point = setup_boss_room()
            player_pos.center = spawn_point
            current_level = "boss_room"
            print("Entered the Boss Room!")

# --------------------------------------------------------
# HANDLE PLAYING STATE
# --------------------------------------------------------
def handle_playing_state(screen, assets, dt):
    """Main gameplay loop handler (refactored and clearer)."""
    global map_offset_x, map_offset_y, current_level, current_house_index
    global player_frame_index, player_frame_timer, current_direction, last_direction
    global show_inventory, show_crafting, show_equipment, crafting_tab, show_quests
    global is_chopping, chopping_timer, chopping_target_tree, is_swinging
    global is_crafting, crafting_timer, item_to_craft
    global is_mining, mining_timer, mining_target_stone
    global is_attacking, attack_timer
    global player_pos
    global show_npc_dialog, npc_quest_active, npc_quest_completed
    global show_miner_dialog, miner_quest_active, miner_quest_completed
    global npc_idle_timer, npc_idle_offset_y, npc_idle_direction
    global miner_idle_timer, miner_idle_offset_y, miner_idle_direction
    global show_level_up, level_up_timer, level_up_text
    global show_vendor_gui, vendor_tab
    global enemies, enemy_spawn_points
    global equipment_slots
    global show_pause_menu, pause_menu_selected_option
    global walk_sound
    global is_game_over
    global enemy_frames 

    # -------------------------
    # Lazy frame/assets loading (first frame only)
    # -------------------------
    if not hasattr(handle_playing_state, 'frames_loaded'):
        handle_playing_state.player_frames = load_player_frames()
        handle_playing_state.chopping_frames = load_chopping_frames()
        handle_playing_state.attack_frames = load_attack_frames()
        handle_playing_state.enemy_frames = load_enemy_frames()
        enemy_frames = handle_playing_state.enemy_frames
        handle_playing_state.frames_loaded = True

        # initialize world once
        setup_colliders()
        give_starting_items(assets)

    # local references for easy use
    player_frames = handle_playing_state.player_frames
    chopping_frames = handle_playing_state.chopping_frames
    attack_frames = handle_playing_state.attack_frames
    enemy_frames = handle_playing_state.enemy_frames

    # -------------------------
    # Game over early return (draw minimal things, show game over dialog)
    # -------------------------
    if is_game_over:
        _draw_game_world(screen, assets, enemy_frames)
        _draw_player(screen, player_frames, attack_frames, chopping_frames)
        _handle_game_over(screen, assets)
        pygame.display.flip()
        return

    # -------------------------
    # Update timers + variables
    # -------------------------
    current_time = pygame.time.get_ticks()
    attack_animation_duration = 400

    # Update player and level-up timers
    player.update(dt, current_time)
    if show_level_up:
        level_up_timer += dt
        if level_up_timer > 3000:
            show_level_up = False
            level_up_timer = 0

    # -------------------------
    # Music management
    # -------------------------
    if current_level == "world":
        play_music("forest")
        pygame.mixer.music.set_volume(0.3)
    elif current_level == "dungeon":
        play_music("dungeon")
    elif current_level == "boss_room":
        play_music("boss_room")
    elif current_level == "house":
        if current_music not in ["forest", None]:
            fade_out_music(2000)

    # -------------------------
    # Enemy spawning & updates (level-specific)
    # -------------------------
    if current_level == "dungeon":
        obstacles = dungeon_walls + stone_rects
        update_enemy_spawns(obstacles)  # pass obstacles in
        player_world_rect = get_player_world_rect()

        # Update each enemy (Boss special-case handled inside update loops)
        for enemy in enemies[:]:
            if isinstance(enemy, Boss):
                enemy.update_movement_pattern(dt, current_time, player_world_rect)
            else:
                enemy.update(dt, current_time, player_world_rect, obstacles)

            if enemy.health <= 0:
                if getattr(enemy, "spawn_point", None):
                    enemy.spawn_point.notify_enemy_death(current_time)
                try:
                    enemies.remove(enemy)
                except ValueError:
                    pass

        handle_combat(current_time)

    elif current_level == "boss_room":
        player_world_rect = get_player_world_rect()
        obstacles = boss_room_walls + stone_rects
        update_boss_room_enemies(dt, current_time, player_world_rect, obstacles)
        handle_combat(current_time)

    # -------------------------
    # Loot pickup handling
    # -------------------------
    for loot in loot_drops[:]:
        loot.update(dt)
        if loot.is_expired(current_time):
            loot_drops.remove(loot)
            continue

        player_world_rect = get_player_world_rect()
        if player_world_rect.colliderect(loot.rect.inflate(20, 20)):
            if add_item_to_inventory(loot.item):
                loot_drops.remove(loot)
                floating_texts.append(FloatingText(
                    f"+{loot.item.name}",
                    (player_world_rect.centerx, player_world_rect.y - 20),
                    color=(255, 255, 100),
                    lifetime=1000
                ))
                print(f"Picked up {loot.item.name}")

    # -------------------------
    # Event handling (keyboard + mouse)
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Pause menu takes priority
        if show_pause_menu:
            handle_pause_menu_input(event, assets, dt)
            continue

        # Boss room input
        if current_level == "boss_room":
            handle_boss_room_interactions(event, player_pos, assets)

        # Keyboard events
        if event.type == pygame.KEYDOWN:
            # Combat controls
            if event.key in (pygame.K_1, pygame.K_SPACE):
                if player.can_attack(current_time) and not is_attacking:
                    is_attacking = True
                    attack_timer = 0
                    player_world_rect = get_player_world_rect()
                    ATTACK_RANGE = 48
                    attack_box = player_world_rect.inflate(ATTACK_RANGE, ATTACK_RANGE)
                    equipped_weapon = equipment_slots.get("weapon")
                    base_damage = player.get_total_damage(equipped_weapon)
                    hit_any = False

                    for enemy in enemies[:]:
                        if attack_box.colliderect(enemy.rect):
                            hit_any = True
                            if enemy.take_damage(base_damage):
                                # Enemy died - drop loot, XP and remove
                                drops = enemy.drop_loot(assets)
                                for drop_item in drops:
                                    loot = LootDrop(enemy.rect.centerx, enemy.rect.centery, drop_item)
                                    loot_drops.append(loot)
                                player.gain_experience(enemy.experience_reward)
                                try:
                                    enemies.remove(enemy)
                                except ValueError:
                                    pass
                                print(f"Defeated {enemy.type}! Gained {enemy.experience_reward} XP")
                                if drops:
                                    floating_texts.append(FloatingText(
                                        f"+{len(drops)} items!",
                                        (enemy.rect.centerx, enemy.rect.centery - 30),
                                        color=(255, 215, 0),
                                        lifetime=1500
                                    ))
                            print(f"Hit {enemy.type} for {base_damage} dmg!")

            # Movement/utility controls
            elif event.key == pygame.K_h:
                use_potion()
            # UI toggles (keep single-panel behavior)
            elif event.key == pygame.K_b:
                show_inventory = not show_inventory
                show_crafting = show_equipment = False
            elif event.key == pygame.K_c and not (is_chopping or is_crafting):
                show_crafting = not show_crafting
                show_inventory = show_equipment = False
            elif event.key == pygame.K_r and not (is_chopping or is_crafting):
                show_equipment = not show_equipment
                show_inventory = show_crafting = False
            elif event.key == pygame.K_i:
                show_quests = not show_quests
            # Interact / world context (E)
            elif event.key == pygame.K_e:
                player_world_rect = get_player_world_rect()

                # WORLD level interactions
                if current_level == "world":
                    if dungeon_portal and player_world_rect.colliderect(dungeon_portal.inflate(20, 20)):
                        spawn_point = setup_dungeon_with_enemy_spawns("Maps/dungeon1.txt")
                        current_level = "dungeon"
                        loot_drops.clear()
                        player_pos.center = (WIDTH // 2, HEIGHT // 2)
                        map_offset_x = spawn_point[0] - WIDTH // 2
                        map_offset_y = spawn_point[1] - HEIGHT // 2
                    elif zone2_portal and player_world_rect.colliderect(zone2_portal.inflate(20, 20)):
                        handle_zone2_portal_interaction(player_world_rect)
                    elif (house_index := check_house_entry(player_world_rect)) is not None:
                        current_level = "house"
                        current_house_index = house_index
                        player_pos.size = (PLAYER_SIZE_INDOOR, PLAYER_SIZE_INDOOR)
                        player_pos.center = (WIDTH // 2, HEIGHT // 2)
                        setup_indoor_colliders()

                    elif npc_rect and player_world_rect.colliderect(npc_rect.inflate(20, 20)):
                        show_npc_dialog = True
                    elif miner_npc_rect and player_world_rect.colliderect(miner_npc_rect.inflate(20, 20)):
                        show_miner_dialog = True

                    elif equipment_slots["weapon"] and equipment_slots["weapon"].name == "Axe":
                        for tree in list(tree_rects):
                            if (player_world_rect.colliderect(tree.inflate(20, 20))
                                    and tree not in house_list and tree != dungeon_portal):
                                is_chopping = True
                                chopping_target_tree = tree
                                chopping_timer = 0
                                current_direction = "idle"
                                break
                        else:
                            _handle_other_resources(player_world_rect, assets)

                    elif equipment_slots["weapon"] and equipment_slots["weapon"].name == "Pickaxe":
                        for stone in list(stone_rects):
                            if player_world_rect.colliderect(stone.inflate(20, 20)):
                                is_mining = True
                                mining_target_stone = stone
                                mining_timer = 0
                                current_direction = "idle"
                                break
                        else:
                            _handle_flower_picking(player_world_rect, assets)
                            _handle_carrot_picking(player_world_rect, assets)
                    else:
                        _handle_flower_picking(player_world_rect, assets)
                        _handle_carrot_picking(player_world_rect, assets)
                elif current_level == "zone2":
                    if handle_zone2_return_portal(player_world_rect):
                        pass  # Portal handled
                    elif handle_crystal_mining(player_world_rect, assets):
                        pass  # Crystal mining started
                    elif equipment_slots["weapon"] and equipment_slots["weapon"].name == "Axe":
                        for tree in list(tree_rects): 
                            if player_world_rect.colliderect(tree.inflate(20, 20)):
                                is_chopping = True
                                chopping_target_tree = tree
                                chopping_timer = 0
                                current_direction = "idle"
                                break
                        else:
                            _handle_flower_picking(player_world_rect, assets)

                    elif equipment_slots["weapon"] and equipment_slots["weapon"].name == "Pickaxe":
                        for stone in list(stone_rects):
                            if player_world_rect.colliderect(stone.inflate(20, 20)):
                                is_mining = True
                                mining_target_stone = stone
                                mining_timer = 0
                                current_direction = "idle"
                                break
                        else:
                            _handle_flower_picking(player_world_rect, assets)
                    else:
                        _handle_flower_picking(player_world_rect, assets)

                # DUNGEON level interactions
                elif current_level == "dungeon":
                    if dungeon_exit and player_world_rect.colliderect(dungeon_exit.inflate(20, 20)):
                        current_level = "world"
                        loot_drops.clear()
                        if dungeon_portal:
                            portal_x = dungeon_portal.centerx
                            portal_y = dungeon_portal.bottom + 50
                        else:
                            portal_x = 25 * TILE_SIZE
                            portal_y = 38 * TILE_SIZE
                        map_offset_x = portal_x - WIDTH // 2
                        map_offset_y = portal_y - HEIGHT // 2
                        player_pos.center = (WIDTH // 2, HEIGHT // 2)

                    elif boss1_portal and player_world_rect.colliderect(boss1_portal.inflate(20, 20)):
                        current_level = "boss_room"
                        enemies.clear()
                        loot_drops.clear()
                        spawn_point = setup_boss_room()
                        map_offset_x = 0
                        map_offset_y = 0
                        player_pos.center = spawn_point

                    elif equipment_slots["weapon"] and equipment_slots["weapon"].name == "Pickaxe":
                        for stone in list(stone_rects):
                            if player_world_rect.colliderect(stone.inflate(20, 20)):
                                is_mining = True
                                mining_target_stone = stone
                                mining_timer = 0
                                current_direction = "idle"
                                break

                # HOUSE exit handling
                elif current_level == "house":
                    door_zone = pygame.Rect(WIDTH // 2 - 40, HEIGHT - 100, 80, 80)
                    if door_zone.colliderect(player_pos.inflate(50, 50)):
                        current_level = "world"
                        loot_drops.clear()
                        player_pos.size = (PLAYER_SIZE, PLAYER_SIZE)
                        exit_rect = house_list[current_house_index]
                        player_world_x = exit_rect.centerx - 20
                        player_world_y = exit_rect.bottom + 20
                        map_offset_x = player_world_x - WIDTH // 2
                        map_offset_y = player_world_y - HEIGHT // 2
                        player_pos.center = (WIDTH // 2, HEIGHT // 2)
                        current_house_index = None

            # NPC dialog keyboard shortcuts
            elif event.key == pygame.K_SPACE and show_npc_dialog:
                if not npc_quest_active and not npc_quest_completed:
                    npc_quest_active = True
                    show_npc_dialog = False
                elif npc_quest_active and get_item_count("Potion") >= potions_needed:
                    remove_item_from_inventory("Potion", potions_needed)
                    for _ in range(10):
                        add_item_to_inventory(assets["coin_item"])
                    npc_quest_completed = True
                    npc_quest_active = False
                    show_npc_dialog = False
                elif npc_quest_completed:
                    show_npc_dialog = False
                    show_vendor_gui = True
                    vendor_tab = "buy"

            elif event.key == pygame.K_SPACE and show_miner_dialog:
                if not miner_quest_active and not miner_quest_completed:
                    miner_quest_active = True
                    show_miner_dialog = False
                elif miner_quest_active and get_item_count("Ore") >= ore_needed:
                    remove_item_from_inventory("Ore", ore_needed)
                    for _ in range(15):
                        add_item_to_inventory(assets["coin_item"])
                    miner_quest_completed = True
                    miner_quest_active = False
                    show_miner_dialog = False

            # Close dialogs / pause
            elif event.key == pygame.K_ESCAPE:
                if show_npc_dialog or show_miner_dialog:
                    show_npc_dialog = False
                    show_miner_dialog = False
                elif show_vendor_gui:
                    show_vendor_gui = False
                elif not (show_inventory or show_crafting or show_equipment):
                    show_pause_menu = True
                    pause_menu_selected_option = 0

        # Mouse clicks
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            # Handle inventory clicks first
            if show_inventory:
                if handle_inventory_mouse_down(mouse_pos, event.button):
                    continue  
    
            # general click handlers (crafting, vendor, etc.)
            if show_vendor_gui:
                _handle_vendor_clicks(event, assets)
            elif show_crafting and not is_crafting:
                _handle_crafting_clicks(event, assets)
            elif show_equipment:
                equipment_slot_rects = draw_equipment_panel(screen, assets)
                handle_equipment_click(event.pos, equipment_slot_rects)

            # HUD icon toggles (inventory, crafting, equipment, quests)
            for name, rect in hud_buttons.items():
                if rect.collidepoint(mouse_pos):
                    if name == "inventory":
                        show_inventory = not show_inventory
                        show_crafting = show_equipment = False
                    elif name == "crafting":
                        show_crafting = not show_crafting
                        show_inventory = show_equipment = False
                    elif name == "equipment":
                        show_equipment = not show_equipment
                        show_inventory = show_crafting = False
                    elif name == "quests":
                        show_quests = not globals().get("show_quests", False)
                        show_inventory = show_crafting = show_equipment = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if show_inventory and dragging_item:
                handle_inventory_mouse_up(event.pos)
            elif event.button == 3:
                handle_equipment_click(event.pos)

    # -------------------------
    # Per-frame state updates (animations, movement)
    # -------------------------
    _update_npc_animations(dt)
    _update_crafting(current_time, assets, dt)
    _update_animations(dt, player_frames, attack_frames, chopping_frames, attack_animation_duration, assets)

    # Player movement (blocked by UI)
    if not _is_ui_blocking_movement():
        keys = pygame.key.get_pressed()
        dx, dy = handle_movement(keys)
        _handle_player_movement(dx, dy)

    # -------------------------
    # Drawing (world, player, UI)
    # -------------------------
    _draw_game_world(screen, assets, enemy_frames)
    _draw_player(screen, player_frames, attack_frames, chopping_frames)
    _draw_ui_elements(screen, assets, player_frames, attack_frames, chopping_frames, None)

    # Draw dialogs / panels on top
    draw_npc_dialog(screen, assets)
    draw_miner_dialog(screen, assets)
    draw_quests_panel(screen, assets)
    if show_vendor_gui:
        draw_vendor_gui(screen, assets)

    if show_inventory:
        draw_inventory(screen, assets)
    if show_crafting:
        draw_crafting_panel(screen, assets, crafting_tab)
    if show_equipment:
        draw_equipment_panel(screen, assets)
    if show_quests:
        draw_quests_panel(screen, assets)

    pygame.display.flip()

# ----------------------------------------------------------------------
# GAME OVER
# -------------
def _handle_game_over(screen, assets):
    """Handle game over screen and respawn logic (no full reset)."""
    global current_level, map_offset_x, map_offset_y, player_pos, enemies
    global is_game_over

    # Draw semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Draw text
    game_over_text = assets["large_font"].render("GAME OVER", True, (255, 0, 0))
    restart_text = assets["font"].render("Press R to Respawn or ESC to Quit", True, (255, 255, 255))
    screen.blit(game_over_text, game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50)))
    screen.blit(restart_text, restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50)))

    # Handle input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                player.health = player.max_health
                current_level = "world"
                map_offset_x = 0
                map_offset_y = 0
                player_pos.center = (WIDTH // 2, HEIGHT // 2)
                
                enemies.clear()

                # Restore control and hide game over
                is_game_over = False
                print("Player respawned at world start (no reset).")

            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
# -----------
# MAIN
# -----------
def main():
    """Main game state manager."""
    global game_state, menu_selected_option, selected_save_slot
    screen, clock = init()
    assets = load_assets()
    load_save_slots()
    while True:
        dt = clock.tick(60)
        if game_state == "main_menu":
            handle_main_menu_events(screen, assets, dt)
        elif game_state == "save_select":
            handle_save_select_events(screen, assets, dt)
        elif game_state == "playing":
            handle_playing_state(screen, assets, dt)
        elif game_state == "boss_room":
            handle_boss_room_state(screen, assets)

if __name__ == "__main__":
    main()
