import pygame
from src.game.submenus import StatusSelectMenu, StatusViewMenu, SpiritsMenu, PlaceholderMenu, CampMenu, DatabaseMenu

class MenuManager:
    def __init__(self, game):
        self.game = game
        self.menu_stack = []  # Stack of active menus
        self.current_menu = None  # "main" or "extra"
        self.current_index = 0
        
        # Main menu options
        self.main_menu_options = {
            0: {"name": "Map", "action": self.action_map},
            1: {"name": "Status", "action": self.action_status},
            2: {"name": "Spirits", "action": self.action_spirits},
            3: {"name": "Camp", "action": self.action_camp},
            4: {"name": "Connect", "action": self.action_connect}
        }
        
        # Extra menu options
        self.extra_menu_options = {
            0: {"name": "Database", "action": self.action_database},
            1: {"name": "Text", "action": self.action_text},
            2: {"name": "Game", "action": self.action_game},
            3: {"name": "TV", "action": self.action_tv}
        }
        
    def push_menu(self, menu):
        """Push a submenu onto the stack"""
        self.menu_stack.append(menu)
        
    def pop_menu(self):
        """Pop current submenu and return to previous"""
        if self.menu_stack:
            self.menu_stack.pop()

    def update(self, delta_time):
        """Update active submenu"""
        if self.menu_stack:
            self.menu_stack[-1].update(delta_time)
            
    def handle_input(self, event):
        # If submenu is active, let it handle input first
        if self.menu_stack:
            if self.menu_stack[-1].handle_input(event):
                return True
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.current_menu is None:
                    # Open main menu
                    self.current_menu = "main"
                    self.current_index = 0
                    return True
                else:
                    # Navigate forward
                    max_index = self.get_max_index()
                    self.current_index = (self.current_index + 1) % (max_index + 1)
                    return True
                    
            if self.current_menu is None:
                return False
                
            if event.key == pygame.K_UP:
                # Return to game (close menu)
                self.current_menu = None
                self.menu_stack.clear()
                return True
                
            elif event.key == pygame.K_LEFT:
                # Switch menus
                if self.current_menu == "main":
                    self.current_menu = "extra"
                    self.current_index = 0
                else:
                    self.current_menu = "main"
                    self.current_index = 0
                return True
                
            elif event.key == pygame.K_RIGHT:
                # Select option
                self.select_option()
                return True
                
        return False

    def get_max_index(self):
        if self.current_menu == "main":
            return max(self.main_menu_options.keys())
        elif self.current_menu == "extra":
            return max(self.extra_menu_options.keys())
        return 0

    def select_option(self):
        if self.current_menu == "main":
            option = self.main_menu_options.get(self.current_index)
        elif self.current_menu == "extra":
            option = self.extra_menu_options.get(self.current_index)
        else:
            return
            
        if option:
            print(f"Selected: {option['name']}")
            option["action"]()


    # Action methods
    def action_map(self):
        self.game.switch_to_map()
        self.current_menu = None # Close menu
        self.menu_stack.clear()

    def action_status(self):
        self.push_menu(StatusSelectMenu(self.game, self))

    def action_spirits(self):
        self.push_menu(SpiritsMenu(self.game, self))

    def action_camp(self):
        self.push_menu(CampMenu(self.game, self))

    def action_connect(self):
        self.push_menu(PlaceholderMenu(self.game, self, "CONNECT - Connection Menu", "menu_connect"))

    def action_database(self):
        self.push_menu(DatabaseMenu(self.game, self))

    def action_text(self):
        self.push_menu(PlaceholderMenu(self.game, self, "TEXT - Story Viewer"))

    def action_game(self):
        self.push_menu(PlaceholderMenu(self.game, self, "GAME - Minigames"))

    def action_tv(self):
        self.push_menu(PlaceholderMenu(self.game, self, "TV - Video Viewer"))

    def draw(self, screen):
        # If submenu is active, draw it instead
        if self.menu_stack:
            self.menu_stack[-1].draw(screen)
            return
            
        if self.current_menu is None:
            return
            
        # Draw menu sprite
        sprite = None
        
        if self.current_menu == "main":
            frames = self.game.assets.get_animation("menu_main")
            if frames and self.current_index < len(frames):
                sprite = frames[self.current_index]
                
        elif self.current_menu == "extra":
            frames = self.game.assets.get_animation("menu_extra")
            if frames and self.current_index < len(frames):
                sprite = frames[self.current_index]
            elif frames:
                sprite = frames[0]
        
        if sprite:
            scale_factor = 6
            scaled_size = (sprite.get_width() * scale_factor, sprite.get_height() * scale_factor)
            scaled_sprite = pygame.transform.scale(sprite, scaled_size)
            
            x = (screen.get_width() - scaled_sprite.get_width()) // 2
            y = (screen.get_height() - scaled_sprite.get_height()) // 2
            screen.blit(scaled_sprite, (x, y))
        
        # Text overlay removed as per request
