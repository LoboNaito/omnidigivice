import pygame
import random

class EvolutionManager:
    """
    Manages Evolution Animations and Logic.
    Ports:
    - obj_ancient_evo_dtector
    - fun_unlock_spirit_dtector
    """
    def __init__(self, game, battle_manager):
        self.game = game
        self.battle = battle_manager
        self.control = game.state
        
        # State: "IDLE", "ANCIENT_ANIM"
        self.state = "IDLE"
        
        # Animation variables
        self.counter = 0
        self.alarm_timer = 0
        self.ancient_digimon_id = -1
        self.required_spirits = [0, 1] # Default
        self.current_char = 0
        
    def start_ancient_evolution(self):
        """Start Ancient Evolution Animation"""
        self.state = "ANCIENT_ANIM"
        self.counter = 0
        self.alarm_timer = 3
        self.ancient_digimon_id = self.battle.mine_digimon
        self.current_char = self.control.game_progress["current_char"]
        
        # Determine required spirits based on digimon ID (Simplified logic)
        # In GML it seems hardcoded or based on ID.
        # For now using default [0, 1] (Fire/Light)
        if self.ancient_digimon_id == 100: # Example ID
            self.required_spirits = [0, 1]
        
        # Play sound
        # self.game.assets.play_sound("evo_ancient")

    def update(self, delta_time):
        if self.state == "ANCIENT_ANIM":
            self.alarm_timer -= delta_time * 60
            if self.alarm_timer <= 0:
                self.counter += 1
                self.alarm_timer = 3
                
                if self.counter > 170: # End of animation
                    self.state = "IDLE"
                    return "EVO_COMPLETE"
                    
        return None

    def draw(self, screen):
        if self.state == "ANCIENT_ANIM":
            self._draw_ancient_anim(screen)

    def _draw_ancient_anim(self, screen):
        # Logic from obj_ancient_evo_dtector Draw
        x = screen.get_width() // 2 - 24 # Center (approx sprite width 48)
        y = screen.get_height() // 2 - 16 # Center (approx sprite height 32)
        scale = 6
        
        # Get Sprites
        spirits = self.game.assets.get_animation("spirits_dtector")
        summon = self.game.assets.get_animation("summon_dtector")
        ancient = self.game.assets.get_animation("ancient_dtector")
        cover = self.game.assets.get_animation("ancient_cover_dtector")
        
        # Character sprites
        char_name = self.game.character_manager.get_character_name(self.current_char).lower()
        char_idle = self.game.assets.get_animation(f"{char_name}_idle")
        
        # Digimon sprite
        digimon_name = self.control.digimon_database[self.ancient_digimon_id]["name"] if self.ancient_digimon_id < len(self.control.digimon_database) else "agumon"
        digimon_sprite = self.game.assets.get_digimon_sprite(digimon_name)
        
        if not (spirits and summon and ancient and cover):
            return

        cnt = self.counter
        
        # Drawing logic based on counter ranges
        if 0 <= cnt <= 28:
            self._draw_sprite(screen, spirits[self.required_spirits[0]], x + 3*scale, (y + 32*scale) - cnt*scale, scale)
        elif 29 <= cnt <= 35:
            self._draw_sprite(screen, spirits[self.required_spirits[0]], x + 3*scale, y + 4*scale, scale)
            if cnt % 2:
                self._draw_sprite(screen, summon[5], x, y, scale)
        elif 36 <= cnt <= 64:
            self._draw_sprite(screen, spirits[self.required_spirits[0]], x + 3*scale, (y + 4*scale) - (cnt - 36)*scale, scale)
        elif 65 <= cnt <= 93:
            self._draw_sprite(screen, spirits[self.required_spirits[1]], x + 3*scale, (y + 32*scale) - (cnt - 65)*scale, scale)
        elif 94 <= cnt <= 100:
            self._draw_sprite(screen, spirits[self.required_spirits[1]], x + 3*scale, y + 4*scale, scale)
            if cnt % 2:
                self._draw_sprite(screen, summon[5], x, y, scale)
        elif 101 <= cnt <= 129:
            self._draw_sprite(screen, spirits[self.required_spirits[1]], x + 3*scale, (y + 4*scale) - (cnt - 101)*scale, scale)
        elif 130 <= cnt <= 136:
            idx = 0 if cnt % 2 else 1
            self._draw_sprite(screen, ancient[idx], x, y, scale)
            self._draw_sprite(screen, cover[0], x, y, scale)
        elif cnt == 137:
            if char_idle: self._draw_sprite(screen, char_idle[0], x + 3*scale, y + 4*scale, scale)
        elif 138 <= cnt <= 144:
            idx = 0 if cnt % 2 else 1
            self._draw_sprite(screen, ancient[idx], x, y, scale)
            self._draw_sprite(screen, cover[0], x, y, scale)
        elif cnt == 145:
            if char_idle: self._draw_sprite(screen, char_idle[0], x + 3*scale, y + 4*scale, scale)
        elif 146:
             # Spirit form of char? Using idle for now
            if char_idle: self._draw_sprite(screen, char_idle[0], x + 3*scale, y + 4*scale, scale)
        elif 147 <= cnt <= 154:
            idx = 0 if cnt % 2 else 1
            self._draw_sprite(screen, ancient[idx], x, y, scale)
            cover_idx = (cnt - 147) // 2
            if cover_idx < len(cover):
                self._draw_sprite(screen, cover[cover_idx], x, y, scale)
        elif 155 <= cnt <= 161:
            if cnt % 2:
                self._draw_sprite(screen, cover[3], x, y, scale)
        elif 162 <= cnt <= 166:
            if cnt % 2 and digimon_sprite:
                self._draw_sprite(screen, digimon_sprite, x + 3*scale, y + 4*scale, scale)
        elif cnt >= 167:
            if digimon_sprite:
                self._draw_sprite(screen, digimon_sprite, x + 3*scale, y + 4*scale, scale)

    def _draw_sprite(self, screen, sprite, x, y, scale):
        scaled = pygame.transform.scale(sprite, 
            (sprite.get_width() * scale, sprite.get_height() * scale))
        screen.blit(scaled, (x, y))

    def unlock_spirit(self, boss_id):
        """
        Unlock spirit based on boss ID.
        Ports fun_unlock_spirit_dtector.
        """
        spirit_id = self._get_spirit_to_unlock(boss_id)
        if spirit_id != -1:
            self.control.spirits_obtained[spirit_id] = True
            return spirit_id
        return -1

    def _get_spirit_to_unlock(self, boss_id):
        # Mapping from GML
        mapping = {
            112: 4, 113: 5, 114: 8, 115: 9, 116: 2, 117: 0, 118: 6, 119: 7,
            96: 1, 99: 3, 98: 1, 97: 3
        }
        return mapping.get(boss_id, -1)
