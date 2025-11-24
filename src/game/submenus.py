import pygame

class BaseMenu:
    """Base class for all menu screens"""
    def __init__(self, game, menu_manager):
        self.game = game
        self.menu_manager = menu_manager
        
    def handle_input(self, event):
        """Handle input for this menu. Return True if handled."""
        return False
        
    def update(self, delta_time):
        """Update menu state"""
        pass
        
    def draw(self, screen):
        """Draw this menu"""
        pass

class StatusSelectMenu(BaseMenu):
    """Character selection for status"""
    def __init__(self, game, menu_manager):
        super().__init__(game, menu_manager)
        self.current_char_index = game.state.game_progress["current_char"]
        self.scroll_offset = 0
        self.scroll_timer = 0
        
    def update(self, delta_time):
        # Scroll text
        self.scroll_timer += delta_time
        if self.scroll_timer >= 0.05: # Speed control
            self.scroll_timer = 0
            self.scroll_offset += 1
            
            # Reset if too far (approx length of text)
            # For now, just reset after some arbitrary large number or calculate text width
            if self.scroll_offset > 200: 
                self.scroll_offset = -50 # Start from right side a bit? Or just 0
                
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                # Return to main menu
                self.menu_manager.pop_menu()
                return True
            elif event.key == pygame.K_DOWN:
                # Navigate to next character in party
                char_party = self.game.state.char_party
                self.current_char_index = (self.current_char_index + 1) % len(char_party)
                # Skip locked characters
                while self.current_char_index < len(char_party) and not char_party[self.current_char_index]:
                    self.current_char_index = (self.current_char_index + 1) % len(char_party)
                self.scroll_offset = 0 # Reset scroll on change
                return True
            elif event.key == pygame.K_RIGHT:
                # Open View Menu
                self.menu_manager.push_menu(StatusViewMenu(self.game, self.menu_manager, self.current_char_index))
                return True
        return False
        
    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        # Draw selection background
        # GML: draw_sprite(spr_sel_dtector, 1, x, y);
        frames = self.game.assets.get_animation("status_select")
        scale_factor = 6
        
        if frames and len(frames) > 1:
            sprite = frames[1] # Frame 1 as per GML
            scaled_sprite = pygame.transform.scale(sprite, 
                (sprite.get_width() * scale_factor, sprite.get_height() * scale_factor))
            x = (screen.get_width() - scaled_sprite.get_width()) // 2
            y = (screen.get_height() - scaled_sprite.get_height()) // 2
            screen.blit(scaled_sprite, (x, y))
            
            # Draw Character Sprite
            # GML: draw_sprite(char.base, 0, x + 3, y + 4);
            char_names = ["Takuya", "Koji", "JP", "Zoe", "Tommy", "Koichi"]
            char_name = char_names[self.current_char_index] if self.current_char_index < len(char_names) else "Unknown"
            
            char_anim = self.game.assets.get_animation(f"{char_name.lower()}_idle")
            if char_anim:
                c_sprite = char_anim[0]
                c_scaled = pygame.transform.scale(c_sprite, (c_sprite.get_width()*scale_factor, c_sprite.get_height()*scale_factor))
                screen.blit(c_scaled, (x + 3 * scale_factor, y + 4 * scale_factor))
            
            # Draw Name Scrolling - REMOVED as per user request
            # "Quita el nombre que aparece en los personajes"
            pass
                
        font = self.game.font
        hint = font.render("DOWN: Change | RIGHT: View | UP: Back", True, (50, 50, 50))
        screen.blit(hint, (10, screen.get_height() - 30))

class StatusViewMenu(BaseMenu):
    """Detailed status view"""
    def __init__(self, game, menu_manager, char_index):
        super().__init__(game, menu_manager)
        self.char_index = char_index
        self.current_page = 0 # 0: HP/Lvl, 1: Spirit, 2: Stamina, 3: Skill
        self.scroll_offset = 0
        self.scroll_timer = 0
        
    def update(self, delta_time):
        self.scroll_timer += delta_time
        # Update scroll offset
        # Slower speed: 15 * 4 (was 30 * 4)
        self.scroll_offset += delta_time * 15 * 4 
                
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_manager.pop_menu()
                return True
            elif event.key == pygame.K_LEFT:
                self.current_page = (self.current_page - 1) % 4
                return True
            elif event.key == pygame.K_RIGHT:
                self.current_page = (self.current_page + 1) % 4
                return True
        return False
        
    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        # Draw status background sprite (Page based)
        frames = self.game.assets.get_animation("status_detail")
        scale_factor = 6
        
        x = 0
        y = 0
        
        if frames and self.current_page < len(frames):
            sprite = frames[self.current_page]
            scaled_sprite = pygame.transform.scale(sprite, 
                (sprite.get_width() * scale_factor, sprite.get_height() * scale_factor))
            x = (screen.get_width() - scaled_sprite.get_width()) // 2
            y = (screen.get_height() - scaled_sprite.get_height()) // 2
            screen.blit(scaled_sprite, (x, y))
        
        # Get character stats
        char_stats = self.game.state.char_stats[self.char_index]

        # Draw Name Scrolling
        text_scale = 4
        spacing = 6 # Reverted to 6 as per GML
        
        box_width = sprite.get_width() * scale_factor
        box_height = 20 * scale_factor
        
        # Calculate total width of text
        # Now that spacing is stride, width is len * spacing * scale
        text_pixel_width = len(char_stats['name']) * spacing * text_scale
        
        # Loop limit: Text width + Box width (so it fully scrolls out)
        # We start drawing at box_width (Right edge)
        start_pos = box_width
        
        # We want it to scroll until it's fully gone to the left.
        # It's gone when (start_pos - offset) + text_width < 0
        # So offset > start_pos + text_width
        
        limit = start_pos + text_pixel_width + (box_width * 0.5) # Add buffer
        
        current_scroll = int(self.scroll_offset) % limit
        final_offset = current_scroll - start_pos
        
        name_x = x
        name_y = y
        
        self.game.text_renderer.draw_text_scrolling(screen, char_stats['name'], name_x, name_y, box_width, box_height, final_offset, scale=text_scale, spacing=6)
        
        # Draw specific stat based on page
        stat_x = x + 24 * scale_factor
        stat_y = y + 23 * scale_factor
        
        if self.current_page == 0:
            # Level and HP
            # Level
            self.game.text_renderer.draw_number(screen, self.game.state.game_progress['level'], 
                                              stat_x, y + 10 * scale_factor, scale=scale_factor)
            # HP
            self.game.text_renderer.draw_number(screen, char_stats['hp'], 
                                              stat_x, stat_y, scale=scale_factor)
        elif self.current_page == 1:
            # Spirit
            self.game.text_renderer.draw_number(screen, char_stats['spirit'], 
                                              stat_x, stat_y, scale=scale_factor)
        elif self.current_page == 2:
            # Stamina
            self.game.text_renderer.draw_number(screen, char_stats['stamina'], 
                                              stat_x, stat_y, scale=scale_factor)
        elif self.current_page == 3:
            # Skill
            self.game.text_renderer.draw_number(screen, char_stats['skill'], 
                                              stat_x, stat_y, scale=scale_factor)
            
        hint = self.game.font.render("LEFT/RIGHT: Page | UP: Back", True, (50, 50, 50))
        screen.blit(hint, (10, screen.get_height() - 30))
class SpiritsMenu(BaseMenu):
    """Spirits collection screen"""
    def __init__(self, game, menu_manager):
        super().__init__(game, menu_manager)
        self.current_index = 0
        self._init_selection()
        
    def _init_selection(self):
        # Start at current character's spirit
        char_map = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 10}
        start_idx = char_map.get(self.game.state.game_progress["current_char"], 0)
        
        self.current_index = start_idx
        
        # Find first obtained spirit starting from there
        obtained = self.game.state.spirits_obtained
        for i in range(len(obtained)):
            idx = (start_idx + i) % len(obtained)
            if obtained[idx]:
                self.current_index = idx
                return
                
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_manager.pop_menu()
                return True
                
            elif event.key == pygame.K_DOWN:
                # Cycle to next obtained spirit
                obtained = self.game.state.spirits_obtained
                for i in range(1, len(obtained)):
                    idx = (self.current_index + i) % len(obtained)
                    if obtained[idx]:
                        self.current_index = idx
                        # Play select sound
                        break
                return True
                
        return False
        
    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        # Draw Background
        bg_frames = self.game.assets.get_animation("status_select")
        if bg_frames:
            bg = bg_frames[0]
            scale = 6
            scaled_bg = pygame.transform.scale(bg, (bg.get_width()*scale, bg.get_height()*scale))
            x = (screen.get_width() - scaled_bg.get_width()) // 2
            y = (screen.get_height() - scaled_bg.get_height()) // 2
            screen.blit(scaled_bg, (x, y))
            
        # Draw Spirit Sprite
        frames = self.game.assets.get_animation("spirits_display")
        if frames and self.current_index < len(frames):
            sprite = frames[self.current_index]
            scale_factor = 6
            scaled_sprite = pygame.transform.scale(sprite, 
                (sprite.get_width() * scale_factor, sprite.get_height() * scale_factor))
            x = (screen.get_width() - scaled_sprite.get_width()) // 2
            y = (screen.get_height() - scaled_sprite.get_height()) // 2
            screen.blit(scaled_sprite, (x + 18, y))
        
        # Draw Spirit Name
        spirit_names = ["Agunimon", "Lobomon", "Beetlemon", "Kazemon", "Kumamon", "Lowemon",
                       "BurningGreymon", "KendoGarurumon", "MetalKabuterimon", "Zephyrmon", "Korikakumon", "JagerLowemon"]
        
        if self.current_index < len(spirit_names):
            spirit_name = spirit_names[self.current_index]
            self.game.text_renderer.draw_text(screen, spirit_name, 20, 50, scale=4)
            
        hint = self.game.font.render("DOWN: Next | UP: Back", True, (50, 50, 50))
        screen.blit(hint, (10, screen.get_height() - 30))

class PlaceholderMenu(BaseMenu):
    """Placeholder for unimplemented menus"""
    def __init__(self, game, menu_manager, title, sprite_name=None):
        super().__init__(game, menu_manager)
        self.title = title
        self.sprite_name = sprite_name
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_manager.pop_menu()
                return True
        return False
        
    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        # Draw sprite if available
        if self.sprite_name:
            frames = self.game.assets.get_animation(self.sprite_name)
            if frames:
                sprite = frames[0]
                scale_factor = 6
                scaled_sprite = pygame.transform.scale(sprite, 
                    (sprite.get_width() * scale_factor, sprite.get_height() * scale_factor))
                x = (screen.get_width() - scaled_sprite.get_width()) // 2
                y = (screen.get_height() - scaled_sprite.get_height()) // 2
                screen.blit(scaled_sprite, (x, y))
        
        font = self.game.font
        
        title = font.render(self.title, True, (0, 0, 0))
        screen.blit(title, (10, 10))
        
class CampMenu(BaseMenu):
    """Camp screen with animation and character selection"""
    def __init__(self, game, menu_manager):
        super().__init__(game, menu_manager)
        self.state = 0 # 0: WalkOut, 1: CampIn, 2: CampLoop, 3: CampOut, 4: WalkIn, 5: Happy
        self.timer = 6
        self.pos_x = 0
        self.animation = False
        self.anim_timer = 0
        
    def update(self, delta_time):
        self.anim_timer += delta_time
        if self.anim_timer >= 0.5:
            self.anim_timer = 0
            self.animation = not self.animation
            
        if self.timer > 0:
            self.timer -= delta_time * 60
            if self.timer <= 0:
                self._handle_timer()
                
    def _handle_timer(self):
        if self.state == 0: # Walk Out
            self.timer = 6
            self.pos_x -= 1
            if self.pos_x <= -27:
                self.state = 1
                
        elif self.state == 1: # Camp In
            self.timer = 6
            self.pos_x += 1
            if self.pos_x >= 0:
                self.timer = 30
                self.state = 2
                
        elif self.state == 2: # Camp Loop (Wait for input)
            self.timer = 30
            
        elif self.state == 3: # Camp Out
            self.timer = 6
            self.pos_x -= 1
            if self.pos_x <= -27:
                self.state = 4
                
        elif self.state == 4: # Walk In
            self.timer = 6
            self.pos_x += 1
            if self.pos_x >= 0:
                self.timer = 240 # 4 seconds for Happy state
                self.state = 5
                self.animation = False
                
        elif self.state == 5: # Happy
            # Logic from obj_char_dtector Step/Alarm 2
            # Wait 4 seconds (set in State 4 transition)
            # Toggle animation every 0.5s (handled in update)
            
            # If timer ends, exit
            if self.timer <= 0: # Handled in _handle_timer but we need to pop
                self.menu_manager.pop_menu()
            
    def handle_input(self, event):
        if self.state == 2: # Only accept input during loop
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    self.state = 3 # Exit camp
                    return True
        return False
        
    def draw(self, screen):
        screen.fill((255, 255, 255)) # White background for visibility
        
        scale = 6
        x = screen.get_width() // 2 - (24 * scale) // 2 # Center 24px sprite
        y = screen.get_height() // 2 - (16 * scale) // 2
        
        char_name = self.game.character_manager.get_current_character_name().lower()
        walk_anim = self.game.assets.get_animation(f"{char_name}_walk")
        camp_anim = self.game.assets.get_animation("camp_screen")
        
        if not walk_anim or not camp_anim: return
        
        # Helper to draw scaled
        def draw_s(sprite, offset_x, offset_y, flip=False):
            if flip: sprite = pygame.transform.flip(sprite, True, False)
            scaled = pygame.transform.scale(sprite, (sprite.get_width()*scale, sprite.get_height()*scale))
            # Apply pos_x to x coordinate for movement
            screen.blit(scaled, (x + (offset_x + self.pos_x)*scale, y + offset_y*scale))

        if self.state == 0:
            idx = 0 if self.animation else 1
            draw_s(walk_anim[idx], 3, 4)
            
        elif self.state == 1:
            draw_s(camp_anim[0], 3, 4)
            
        elif self.state == 2:
            idx = 1 if self.animation else 0
            draw_s(camp_anim[idx], 3, 4)
            
        elif self.state == 3:
            draw_s(camp_anim[0], 3, 4)
            
        elif self.state == 4:
            idx = 0 if self.animation else 1
            # Walk in from right. Removed flip as it looked backwards.
            draw_s(walk_anim[idx], 3, 4)
            
        elif self.state == 5:
            # Happy animation
            # GML: if (animation) draw_sprite(char.base...) else draw_sprite(char.happy...)
            
            if self.animation:
                base_anim = self.game.assets.get_animation(f"{char_name}_idle")
                if base_anim:
                    draw_s(base_anim[0], 3, 4)
            else:
                happy_char = self.game.assets.get_sprite(f"{char_name}_happy")
                if happy_char:
                    draw_s(happy_char, 3, 4)
                
                happy_sprite = self.game.assets.get_sprite("happy")
                if happy_sprite:
                    draw_s(happy_sprite, 23, 0)
                    draw_s(happy_sprite, 0, 0)

class DatabaseMenu(BaseMenu):
    """Database category selection"""
    def __init__(self, game, menu_manager):
        super().__init__(game, menu_manager)
        self.current_category = 0 # 0: Rookie, 1: Champion, 2: Ultimate, 3: Mega, 4: Boss, 5: Ancient
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_manager.pop_menu()
                return True
            elif event.key == pygame.K_LEFT:
                self.current_category = (self.current_category - 1) % 6
                return True
            elif event.key == pygame.K_RIGHT:
                self.current_category = (self.current_category + 1) % 6
                return True
            elif event.key == pygame.K_DOWN:
                # Open view for category
                self.menu_manager.push_menu(DatabaseViewMenu(self.game, self.menu_manager, self.current_category))
                return True
        return False
        
    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        # Draw database sprite frame based on category
        frames = self.game.assets.get_animation("database_screen")
        if frames and self.current_category < len(frames):
            sprite = frames[self.current_category]
            scale = 6
            scaled = pygame.transform.scale(sprite, (sprite.get_width()*scale, sprite.get_height()*scale))
            x = (screen.get_width() - scaled.get_width()) // 2
            y = (screen.get_height() - scaled.get_height()) // 2
            screen.blit(scaled, (x, y))
            
        font = self.game.font
        hint = font.render("LEFT/RIGHT: Category | DOWN: Select | UP: Back", True, (50, 50, 50))
        screen.blit(hint, (10, screen.get_height() - 30))

class DatabaseViewMenu(BaseMenu):
    """View Digimon in a category"""
    def __init__(self, game, menu_manager, category_idx):
        super().__init__(game, menu_manager)
        self.category_idx = category_idx
        self.digimon_list = self._get_digimon_list()
        self.current_index = 0
        
    def _get_digimon_list(self):
        types = ["rookie", "champion", "ultimate", "mega", "boss", "ancient"]
        target_type = types[self.category_idx]
        
        found = []
        for digimon in self.game.state.digimon_database:
            # Check if type matches and is unlocked (assuming unlock flag exists)
            # For now, show all for testing or check "unlock" key
            if digimon.get("type") == target_type:
                 # if digimon.get("unlock", False):
                 found.append(digimon)
        return found
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_manager.pop_menu()
                return True
            elif event.key == pygame.K_LEFT:
                if self.digimon_list:
                    self.current_index = (self.current_index - 1) % len(self.digimon_list)
                return True
            elif event.key == pygame.K_RIGHT:
                if self.digimon_list:
                    self.current_index = (self.current_index + 1) % len(self.digimon_list)
                return True
        return False
        
    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        if not self.digimon_list:
            font = self.game.font
            text = font.render("No Digimon Unlocked", True, (0, 0, 0))
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, screen.get_height()//2))
            return

        digimon = self.digimon_list[self.current_index]
        
        # Draw Digimon Sprite
        sprite_name = digimon.get("sprite", "agumon")
        # Try dtector sprite first
        frames = self.game.assets.get_animation(f"digimon_{sprite_name}")
        if not frames:
             # Try generic
             frames = self.game.assets.get_animation(sprite_name)
             
        if frames:
            sprite = frames[0]
            scale = 6
            scaled = pygame.transform.scale(sprite, (sprite.get_width()*scale, sprite.get_height()*scale))
            x = (screen.get_width() - scaled.get_width()) // 2
            y = (screen.get_height() - scaled.get_height()) // 2
            screen.blit(scaled, (x, y))
            
        # Draw Info
        font = self.game.font
        # name_text = font.render(f"{digimon['name'].upper()}", True, (0, 0, 0))
        # screen.blit(name_text, (20, 20))
        self.game.text_renderer.draw_text(screen, digimon['name'], 20, 20, scale=4)
        
        # stats_text = f"HP:{digimon['hp']}  AP:{digimon['ability']}"
        # s_text = font.render(stats_text, True, (50, 50, 50))
        # screen.blit(s_text, (20, 50))
        
        self.game.text_renderer.draw_text(screen, "HP", 20, 60, scale=4)
        self.game.text_renderer.draw_number(screen, digimon['hp'], 80, 60, scale=4)
        
        self.game.text_renderer.draw_text(screen, "AP", 20, 90, scale=4)
        self.game.text_renderer.draw_number(screen, digimon['ability'], 80, 90, scale=4)
        
        hint = font.render("LEFT/RIGHT: Navigate | UP: Back", True, (50, 50, 50))
        screen.blit(hint, (10, screen.get_height() - 30))
