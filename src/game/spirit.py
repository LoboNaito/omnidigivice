import pygame
import math

class SpiritManager:
    """
    Manages spirit evolution, de-evolution, and spirit battle menu.
    Ports logic from:
    - obj_spirit_select_dtector
    - obj_spirit_dtector
    - obj_menu_spirit_dtector
    - obj_spirit_off_dtector
    """
    def __init__(self, game, battle_manager):
        self.game = game
        self.battle = battle_manager
        self.control = game.state
        
        # State: "SELECT", "EVO_ANIM", "MENU", "DEEVO_ANIM"
        self.state = "SELECT"
        
        # Selection variables
        self.current_selection = 0
        self.available_spirits = []
        
        # Animation variables
        self.counter = 0
        self.anim_timer = 0
        self.selected_spirit = 0
        self.new_char = 0
        self.selected_evo = 100
        
        # Menu variables
        self.menu_index = 0 # 0=Attack, 1=Scan, 2=Off, 3=Escape
        
        # De-evolution variables
        self.is_escape = False
        
    def start_selection(self):
        """Initialize spirit selection"""
        self.state = "SELECT"
        self.current_selection = 0
        self._refresh_available_spirits()
        
        # Set initial selection based on current character
        char_idx = self.control.game_progress["current_char"]
        start_indices = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 10}
        if char_idx in start_indices:
            self.current_selection = start_indices[char_idx]
            
        # Ensure selection is valid
        self._validate_selection()

    def _refresh_available_spirits(self):
        self.available_spirits = []
        for i, obtained in enumerate(self.battle.copy_spirits):
            if obtained:
                self.available_spirits.append(i)

    def _validate_selection(self):
        # Ensure current_selection points to an obtained spirit
        # Logic from obj_spirit_select_dtector Create
        if not self.battle.copy_spirits[self.current_selection]:
            # Find next available
            for i in range(12):
                idx = (self.current_selection + i) % 12
                if self.battle.copy_spirits[idx]:
                    self.current_selection = idx
                    break

    def update(self, delta_time):
        if self.state == "EVO_ANIM":
            return self._update_evo_anim(delta_time)
        elif self.state == "DEEVO_ANIM":
            return self._update_deevo_anim(delta_time)
        return None

    def handle_input(self, event):
        if self.state == "SELECT":
            return self._handle_select_input(event)
        elif self.state == "MENU":
            return self._handle_menu_input(event)
        return None

    def _handle_select_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.current_selection = (self.current_selection - 1) % 12
                self._validate_selection()
            elif event.key == pygame.K_RIGHT:
                self.current_selection = (self.current_selection + 1) % 12
                self._validate_selection()
            elif event.key == pygame.K_DOWN: # Select
                # Check if swap is possible (character matches spirit element)
                # Logic from KeyPress_39
                if self._can_evolve(self.current_selection):
                    self._start_evolution(self.current_selection)
                else:
                    # Play cancel sound
                    pass
        return None

    def _can_evolve(self, spirit_idx):
        # Logic from obj_spirit_select_dtector KeyPress_39
        # Checks if current character party member corresponds to spirit element
        # 0,1 -> char 0; 2,3 -> char 1; etc.
        char_idx = spirit_idx // 2
        return self.control.char_party[char_idx]

    def _start_evolution(self, spirit_idx):
        self.state = "EVO_ANIM"
        self.selected_spirit = spirit_idx
        self.counter = 0
        self.anim_timer = 30
        
        # Determine new char and evo ID
        # Logic from obj_spirit_dtector Alarm 0
        self.new_char = spirit_idx // 2
        self.selected_evo = 100 + spirit_idx
        
        # Update game state
        self.battle.copy_spirits[spirit_idx] = False
        self.battle.mine_digimon = self.selected_evo
        
        digimon = self.control.digimon_database[self.selected_evo]
        self.battle.current_mine_hp = digimon["hp"]
        self.battle.control_level = digimon["level"]
        
        # Skip animation part if same character (logic from GML)
        if self.new_char == self.control.game_progress["current_char"]:
            self.counter = 61

    def _update_evo_anim(self, delta_time):
        # Logic from obj_spirit_dtector Alarm 0
        self.anim_timer -= delta_time * 60
        
        if self.anim_timer <= 0:
            if self.counter == 61:
                # Play evo sound
                self.counter += 1
                self.anim_timer = 15
            elif self.counter == 199:
                self.state = "MENU"
                self.menu_index = 0
                return "EVO_COMPLETE"
            else:
                self.counter += 1
                # Set next timer based on counter ranges (simplified)
                if 0 <= self.counter <= 60: self.anim_timer = 3
                elif 62 <= self.counter <= 68: self.anim_timer = 15
                elif 69 <= self.counter <= 72: self.anim_timer = 15 # 45 at 72
                elif 73 <= self.counter <= 76: self.anim_timer = 15
                elif self.counter == 77: self.anim_timer = 30
                elif 78 <= self.counter <= 109: self.anim_timer = 6
                elif self.counter == 110: self.anim_timer = 3
                elif 111 <= self.counter <= 142: self.anim_timer = 3
                elif 143 <= self.counter <= 161: self.anim_timer = 15
                elif self.counter == 162: self.anim_timer = 60
                elif 163 <= self.counter <= 194: self.anim_timer = 6
                elif 195 <= self.counter <= 198: self.anim_timer = 30
                else: self.anim_timer = 30
                
        return None

    def start_menu(self):
        """Start spirit battle menu"""
        self.state = "MENU"
        self.menu_index = 0

    def start_deevolution(self, is_escape):
        """Start de-evolution sequence"""
        self._start_deevolution(is_escape)

    def _handle_menu_input(self, event):
        # Logic from obj_menu_spirit_dtector
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.menu_index = (self.menu_index - 1) % 4
            elif event.key == pygame.K_RIGHT:
                self.menu_index = (self.menu_index + 1) % 4
            elif event.key == pygame.K_DOWN:
                if self.menu_index == 0: # Attack
                    return "SPIRIT_ATTACK"
                elif self.menu_index == 1: # Scan
                    return "SPIRIT_SCAN"
                elif self.menu_index == 2: # Off
                    self._start_deevolution(False)
                elif self.menu_index == 3: # Escape
                    self._start_deevolution(True)
        return None

    def _start_deevolution(self, is_escape):
        self.state = "DEEVO_ANIM"
        self.is_escape = is_escape
        self.counter = 0
        self.anim_timer = 6
        # Logic from obj_spirit_off_dtector
        # Determine current_char to revert to based on mine_digimon ID
        evo_id = self.battle.mine_digimon
        if 100 <= evo_id <= 111:
            self.new_char = (evo_id - 100) // 2
        else:
            self.new_char = 0 # Default

    def _update_deevo_anim(self, delta_time):
        # Logic from obj_spirit_off_dtector Alarm 0
        self.anim_timer -= delta_time * 60
        
        if self.anim_timer <= 0:
            if self.counter == 34:
                # Restore original character
                self.control.game_progress["current_char"] = self.new_char
                self.counter += 1
                self.anim_timer = 60
            elif self.counter == 35:
                # End logic
                if self.is_escape:
                    return "ESCAPE"
                else:
                    return "DEEVO_COMPLETE"
            else:
                self.counter += 1
                if 0 <= self.counter <= 16: self.anim_timer = 6
                elif 17 <= self.counter <= 30: self.anim_timer = 15
                elif 31 <= self.counter <= 33: self.anim_timer = 60
                else: self.anim_timer = 60
                
        return None

    def draw(self, screen):
        if self.state == "SELECT":
            self._draw_selection(screen)
        elif self.state == "EVO_ANIM":
            self._draw_evo_anim(screen)
        elif self.state == "MENU":
            self._draw_menu(screen)
        elif self.state == "DEEVO_ANIM":
            self._draw_deevo_anim(screen)

    def _draw_selection(self, screen):
        # Draw spirit selection UI
        frames = self.game.assets.get_animation("spirits_dtector")
        if frames:
            scale = 6
            sprite = frames[self.current_selection]
            self._draw_scaled(screen, sprite, 
                screen.get_width()//2 - sprite.get_width()*scale//2, 
                screen.get_height()//2 - sprite.get_height()*scale//2, scale)
            
            # Draw hint
            font = self.game.font
            hint = font.render("LEFT/RIGHT: Select | DOWN: Evolve", True, (200, 200, 200))
            screen.blit(hint, (10, screen.get_height() - 30))

    def _draw_evo_anim(self, screen):
        # Logic from obj_spirit_dtector Draw
        scale = 6
        x = screen.get_width() // 2
        y = screen.get_height() // 2
        
        # Get sprites
        char_db = self.game.character_manager.characters
        old_char_sprite = self.game.assets.get_animation(char_db[self.control.game_progress["current_char"]]["base"])
        new_char_sprite = self.game.assets.get_animation(char_db[self.new_char]["base"])
        new_char_spirit = self.game.assets.get_animation(char_db[self.new_char]["spirit"])
        spirit_frames = self.game.assets.get_animation("spirits_dtector")
        summon_frames = self.game.assets.get_animation("summon_dtector")
        catch_frames = self.game.assets.get_animation("catch_dtector")
        
        evo_digimon = self.control.digimon_database[self.selected_evo]
        evo_sprite = self.game.assets.get_animation(evo_digimon["sprite"])
        
        if not (old_char_sprite and new_char_sprite and spirit_frames and evo_sprite):
            return

        # Draw logic based on counter
        if self.counter == 0:
            self._draw_scaled(screen, old_char_sprite[0], x, y, scale)
            
        elif 0 <= self.counter <= 30:
            # Slide out old char
            offset = self.counter
            self._draw_scaled(screen, old_char_sprite[0], x + 24*scale - offset*scale, y, scale)
            
        elif 31 <= self.counter <= 61:
            # Slide in new char
            offset = self.counter - 31
            self._draw_scaled(screen, new_char_sprite[0], x + 30*scale - offset*scale, y, scale)
            
        elif 62 <= self.counter <= 68:
            self._draw_scaled(screen, new_char_sprite[0], x, y, scale)
            if self.counter % 2 == 0:
                self._draw_scaled(screen, summon_frames[5], x, y, scale)
                
        elif 69 <= self.counter <= 72:
            if new_char_spirit:
                self._draw_scaled(screen, new_char_spirit[0], x, y, scale)
            if self.counter % 2 == 0:
                self._draw_scaled(screen, summon_frames[5], x, y, scale)
                
        elif 73 <= self.counter <= 77:
            if self.counter % 2:
                self._draw_scaled(screen, spirit_frames[self.selected_spirit], x, y, scale)
                
        elif 78 <= self.counter <= 110:
            # Spirit flash effect (simplified)
            offset = self.counter - 78
            sprite = spirit_frames[self.selected_spirit]
            # Draw 4 copies moving out
            self._draw_scaled(screen, sprite, x - offset*scale, y, scale)
            self._draw_scaled(screen, sprite, x + offset*scale, y, scale)
            self._draw_scaled(screen, sprite, x, y - offset*scale, scale)
            self._draw_scaled(screen, sprite, x, y + offset*scale, scale)
            
        elif 111 <= self.counter <= 143:
            # Character rising
            offset = (self.counter - 111) * 2
            self._draw_scaled(screen, new_char_sprite[0], x, y + 32*scale - offset*scale, scale)
            
        elif 144 <= self.counter <= 150:
            idx = 0 if self.counter % 2 else 2
            self._draw_scaled(screen, summon_frames[idx], x, y, scale)
            
        elif 151 <= self.counter <= 162:
            if self.counter % 2:
                self._draw_scaled(screen, summon_frames[0], x, y, scale)
            else:
                self._draw_scaled(screen, summon_frames[0], x, y, scale)
                if len(evo_sprite) > 4:
                    self._draw_scaled(screen, evo_sprite[4], x, y, scale)
                else:
                    self._draw_scaled(screen, evo_sprite[0], x, y, scale)
                    
        elif 163 <= self.counter <= 196:
            self._draw_scaled(screen, evo_sprite[0], x, y, scale)
            # Catch effect
            if catch_frames:
                offset = (self.counter - 163) * 2
                self._draw_scaled(screen, catch_frames[0], x, y + 32*scale - offset*scale, scale)
                
        elif self.counter == 197:
            if len(evo_sprite) > 1:
                self._draw_scaled(screen, evo_sprite[1], x, y, scale)
            else:
                self._draw_scaled(screen, evo_sprite[0], x, y, scale)
                
        elif self.counter >= 198:
            self._draw_scaled(screen, evo_sprite[0], x, y, scale)

    def _draw_menu(self, screen):
        # Draw spirit battle menu
        # Use battle menu sprite but maybe different text?
        # Actually obj_menu_spirit_dtector uses spr_battle_menu_dtector?
        # No, it seems to use text or maybe I missed the sprite loading for it.
        # Let's assume it uses the standard battle menu sprite for now.
        frames = self.game.assets.get_animation("battle_menu_dtector")
        if frames and self.menu_index < len(frames):
            sprite = frames[self.menu_index]
            scale = 6
            self._draw_scaled(screen, sprite, 
                screen.get_width()//2 - sprite.get_width()*scale//2, 
                screen.get_height()//2 - sprite.get_height()*scale//2, scale)
        
        # Draw hint
        font = self.game.font
        options = ["Attack", "Scan", "Off", "Escape"]
        hint = font.render(f"LEFT/RIGHT: Navigate | DOWN: {options[self.menu_index]}", 
                          True, (200, 200, 200))
        screen.blit(hint, (10, screen.get_height() - 30))

    def _draw_deevo_anim(self, screen):
        # Logic from obj_spirit_off_dtector Draw
        # It seems to just reverse or show character appearing?
        # For now, just show character
        scale = 6
        x = screen.get_width() // 2
        y = screen.get_height() // 2
        
        char_db = self.game.character_manager.characters
        char_sprite = self.game.assets.get_animation(char_db[self.new_char]["base"])
        
        if char_sprite:
            self._draw_scaled(screen, char_sprite[0], x, y, scale)

    def _draw_scaled(self, screen, sprite, x, y, scale, flip_x=False):
        if flip_x:
            sprite = pygame.transform.flip(sprite, True, False)
        
        # Center the sprite at x,y if not already calculated
        # But my logic above calculates top-left.
        # Let's assume x,y passed are top-left.
        
        scaled = pygame.transform.scale(sprite, 
            (sprite.get_width() * scale, sprite.get_height() * scale))
        screen.blit(scaled, (x, y))
