import pygame

class BattleMenu:
    """
    Battle menu for attack/call/escape options.
    Ports obj_menu_battle_dtector logic.
    """
    def __init__(self, game, battle_manager):
        self.game = game
        self.battle = battle_manager
        self.control = game.state
        self.current_index = 0  # 0=Attack, 1=Spirit, 2=Call, 3=Escape
        
    def has_spirits(self):
        """Check if player has any spirits available"""
        for spirit in self.battle.copy_spirits:
            if spirit:
                return True
        return False
    
    def handle_input(self, event):
        """Handle battle menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.current_index = (self.current_index - 1) % 4
                return True
            elif event.key == pygame.K_RIGHT:
                self.current_index = (self.current_index + 1) % 4
                return True
            elif event.key == pygame.K_DOWN:
                # Select option
                if self.current_index == 0:
                    # Attack - go to scan/attack screen
                    return "scan_attack"
                elif self.current_index == 1:
                    # Spirit - check if spirits available
                    if self.has_spirits():
                        return "spirit_check"
                    # else: play cancel sound, do nothing
                elif self.current_index == 2:
                    # Call - go to spirit check for calling
                    return "spirit_call"
                elif self.current_index == 3:
                    # Escape
                    return self._attempt_escape()
                return True
        return False
    
    def _attempt_escape(self):
        """Attempt to escape from battle"""
        import random
        
        # Can't escape from boss battles
        if self.control.game_progress["distance"] == 0:
            escape_chance = 0
        else:
            escape_chance = 30
        
        roll = random.randint(0, 100)
        
        if roll < escape_chance:
            # Successful escape
            return "escape_success"
        else:
            # Failed escape - lose distance
            self.control.game_progress["distance"] += 500
            return "escape_fail"
    
    def draw(self, screen):
        """Draw battle menu"""
        # Draw battle menu sprite
        frames = self.game.assets.get_animation("battle_menu_dtector")
        if frames and self.current_index < len(frames):
            sprite = frames[self.current_index]
            scale_factor = 6
            scaled = pygame.transform.scale(sprite,
                (sprite.get_width() * scale_factor, sprite.get_height() * scale_factor))
            x = (screen.get_width() - scaled.get_width()) // 2
            y = (screen.get_height() - scaled.get_height()) // 2
            screen.blit(scaled, (x, y))
        
        # Draw hint
        font = self.game.font
        options = ["Attack", "Spirit", "Call", "Escape"]
        hint = font.render(f"LEFT/RIGHT: Navigate | DOWN: {options[self.current_index]}", 
                          True, (200, 200, 200))
        screen.blit(hint, (10, screen.get_height() - 30))


class ScanAttackScreen:
    """
    Screen for scanning enemy and selecting attack.
    Ports obj_scan_dtector logic.
    """
    def __init__(self, game, battle_manager):
        self.game = game
        self.battle = battle_manager
        self.control = game.state
        self.showing_scan = True
        self.scan_timer = 60  # Show scan for 1 second
    
    def update(self, delta_time):
        """Update scan timer"""
        if self.showing_scan:
            self.scan_timer -= delta_time * 60
            if self.scan_timer <= 0:
                self.showing_scan = False
                return "attack_menu"
        return None
    
    def draw(self, screen):
        """Draw scan information"""
        enemy = self.control.digimon_database[self.battle.enemy_digimon]
        
        # Display enemy info
        font = self.game.font
        y = 50
        scale = 4
        
        self.game.text_renderer.draw_text(screen, f"Name {enemy['name']}", 20, y, scale=scale)
        y += 30
        self.game.text_renderer.draw_text(screen, "Level", 20, y, scale=scale)
        self.game.text_renderer.draw_number(screen, enemy['level'], 120, y, scale=scale)
        y += 30
        self.game.text_renderer.draw_text(screen, "HP", 20, y, scale=scale)
        self.game.text_renderer.draw_number(screen, self.battle.current_enemy_hp, 80, y, scale=scale)
        self.game.text_renderer.draw_text(screen, "/", 140, y, scale=scale)
        self.game.text_renderer.draw_number(screen, enemy['hp'], 160, y, scale=scale)
        y += 30
        self.game.text_renderer.draw_text(screen, f"Elm {enemy['element']}", 20, y, scale=scale)
        y += 30
        self.game.text_renderer.draw_text(screen, f"Type {enemy['type']}", 20, y, scale=scale)
        
        if self.showing_scan:
            hint = font.render("Scanning...", True, (50, 50, 50))
            screen.blit(hint, (10, screen.get_height() - 30))
