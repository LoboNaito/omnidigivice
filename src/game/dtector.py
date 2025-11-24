import pygame
import os
from src.game.state import GameState
from src.game.character import CharacterManager
from src.engine.assets import AssetManager
from src.game.menu import MenuManager
from src.game.battle import BattleManager
from src.game.map import MapManager
from src.game.events import EventManager
from src.engine.graphics import TextRenderer

class DtectorGame:
    def __init__(self):
        self.state = GameState()
        self.character_manager = CharacterManager(self.state)
        self.assets = AssetManager(os.getcwd()) # Assuming running from root
        self.assets.load_all_character_sprites()
        self.assets.load_ui_sprites()
        
        # Preload Digimon Sprites
        for digimon in self.state.digimon_database:
            if not digimon["name"].startswith("digimon_"):
                self.assets.load_digimon_sprite(digimon["name"])
        
        self.font = pygame.font.SysFont("Arial", 16)
        self.text_renderer = TextRenderer(self.assets)
        
        # Managers
        self.menu_manager = MenuManager(self)
        self.battle_manager = None 
        self.map_manager = MapManager(self)
        self.event_manager = EventManager(self)
        
        # Game State: "WALKING", "MENU", "BATTLE", "MAP", "EVENT"
        self.current_state = "WALKING"
        
        # Animation state
        self.animation_timer = 0
        self.animation_interval = 0.5 # 30 frames approx
        self.animation_toggle = False
        self.animation_base = 0
        
        self.is_walking = False
        self.walk_timer = 0
        self.walk_duration = 0.2 # How long to show walk anim after a step
        
    def switch_to_map(self):
        self.current_state = "MAP"
        self.map_manager._init_map_from_area() # Refresh map state
        
    def switch_to_battle(self):
        self.current_state = "BATTLE"
        self.battle_manager = BattleManager(self) # Create new battle instance
        
    def switch_to_walking(self):
        self.current_state = "WALKING"
        
    def switch_to_event(self):
        self.current_state = "EVENT"
        self.event_manager.start_event()

    def handle_input(self, event):
        if self.current_state == "MENU":
            # Pass input to menu manager
            if self.menu_manager.handle_input(event):
                return
            # If menu returns false (e.g. closed), check if we should go back to walking
            if self.menu_manager.current_menu is None:
                self.current_state = "WALKING"
                
        elif self.current_state == "BATTLE":
            if self.battle_manager:
                result = self.battle_manager.handle_input(event)
                if result == "VICTORY" or result == "GAME_OVER" or result == "BATTLE_END":
                    self.switch_to_walking()
                    
        elif self.current_state == "MAP":
            result = self.map_manager.handle_input(event)
            if result == "MAP_SELECTED":
                self.switch_to_walking()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT and self.map_manager.change == 0:
                # Exit map
                self.switch_to_walking()
                
        elif self.current_state == "EVENT":
            # Event input handling if needed
            pass
            
        elif self.current_state == "WALKING":
            # Menu access
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.current_state = "MENU"
                    self.menu_manager.current_menu = "main"
                    self.menu_manager.current_index = 0
                    return

                if event.key == pygame.K_SPACE:
                    self.increment_steps()

    def increment_steps(self):
        # Trigger walk animation
        self.is_walking = True
        self.walk_timer = self.walk_duration
        
        progress = self.state.game_progress
        
        progress["steps"] += 1
        if progress["steps"] > 999999:
            progress["steps"] = 0
            
        if progress["distance"] > 0:
            progress["distance"] -= 1
            
        # D-Power increase every 100 steps
        if progress["steps"] % 100 == 0 and progress["dpower"] < 99:
            progress["dpower"] += 1
            print(f"D-Power increased to: {progress['dpower']}")
            
        # Encounter logic
        import random
        
        if progress["distance"] == 0:
            progress["battle_start"] = True
            print("Boss Battle Triggered!")
            self.switch_to_battle()
        elif progress["steps"] % 100 == 0: # Reduced for testing, was 500
            # 2/3 chance for battle, 1/3 for event
            is_battle = random.choice([True, True, False])
            
            if not progress["last_encounter_is_battle"]:
                is_battle = True
                
            if is_battle:
                progress["battle_start"] = True
                print(f"Battle started at step {progress['steps']}!")
                self.switch_to_battle()
            else:
                progress["event_start"] = True
                print(f"Event started at step {progress['steps']}!")
                self.switch_to_event()
                
            progress["last_encounter_is_battle"] = is_battle

    def update(self, delta_time):
        import random
        
        if self.current_state == "MENU":
            self.menu_manager.update(delta_time)
            return

        if self.current_state == "BATTLE":
            if self.battle_manager:
                result = self.battle_manager.update(delta_time)
                if result == "VICTORY" or result == "GAME_OVER" or result == "BATTLE_END":
                    self.switch_to_walking()
            return
            
        elif self.current_state == "MAP":
            self.map_manager.update(delta_time)
            return
            
        elif self.current_state == "EVENT":
            result = self.event_manager.update(delta_time)
            if result == "EVENT_COMPLETE":
                self.switch_to_walking()
            return
            
        # Animation timer (Alarm 1 logic)
        self.animation_timer += delta_time
        if self.animation_timer >= self.animation_interval:
            self.animation_timer = 0
            self.animation_toggle = not self.animation_toggle
            self.animation_base = random.randint(0, 3)
            
        # Walk timer (Alarm 0 logic)
        if self.is_walking:
            self.walk_timer -= delta_time
            if self.walk_timer <= 0:
                self.is_walking = False
        
    def draw(self, screen):
        screen.fill((255, 255, 255)) # Clear screen to white
        
        if self.current_state == "MENU":
            self.menu_manager.draw(screen)
            return
            
        elif self.current_state == "BATTLE":
            if self.battle_manager:
                self.battle_manager.draw(screen)
            return
            
        elif self.current_state == "MAP":
            self.map_manager.draw(screen)
            return
            
        elif self.current_state == "EVENT":
            self.event_manager.draw(screen)
            return
            
        # Draw Background (Map/Walking)
        # The walking screen should be clean (white background)
        # spr_map_dtector is the Map UI and should not be drawn here.
            
        # Draw Character (WALKING state)
        char_name = self.character_manager.get_current_character_name().lower()
        
        sprite = None
        flip_x = False
        
        if self.is_walking:
            # Walking Animation
            anim_frames = self.assets.get_animation(f"{char_name}_walk")
            if anim_frames:
                frame_idx = 0 if self.animation_toggle else 1
                sprite = anim_frames[frame_idx % len(anim_frames)]
        else:
            # Idle Animation (Random Base)
            anim_frames = self.assets.get_animation(f"{char_name}_idle")
            if anim_frames:
                # animation_base: 0=frame0, 1=frame1, 2=frame0_flip, 3=frame1_flip
                frame_idx = self.animation_base % 2
                flip_x = (self.animation_base >= 2)
                sprite = anim_frames[frame_idx % len(anim_frames)]
        
        if sprite:
            # Scale sprite (6x size as requested)
            scale_factor = 6
            scaled_size = (sprite.get_width() * scale_factor, sprite.get_height() * scale_factor)
            sprite = pygame.transform.scale(sprite, scaled_size)
            
            if flip_x:
                sprite = pygame.transform.flip(sprite, True, False)
            
            cx = screen.get_width() // 2 - sprite.get_width() // 2
            cy = screen.get_height() // 2 - sprite.get_height() // 2
            screen.blit(sprite, (cx, cy))
        
        # Draw UI Overlay (Steps/Dist) - Replaced with graphical numbers if possible
        # For now, just remove the ugly debug text.
        # If we want to show steps, we should use spr_numbers_white
        
        if self.state.game_progress["battle_start"]:
            # Draw Battle Alert
            alert_anim = self.assets.get_animation("battle_call") # Or similar
            if alert_anim:
                 # Draw alert
                 pass
            
        if self.state.game_progress["event_start"]:
            # Draw Event Alert
            pass
