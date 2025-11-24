import pygame
import random

class LevelManager:
    """
    Manages level up/down logic and post-battle transitions.
    Ports obj_change_level_dtector and obj_position_dtector logic.
    """
    def __init__(self, game):
        self.game = game
        self.control = game.state
        self.counter = 0
        self.alarm_timer = 0
        self.state = "IDLE" # IDLE, LEVEL_CHANGE, POSITION
        self.is_level_up = 2 # 0=Up, 1=Down, 2=None
        self.happy = False
        self.sad = False
        
    def start_level_check(self, win):
        """Start level check sequence after battle"""
        self.state = "LEVEL_CHANGE"
        self.counter = 0
        self.alarm_timer = 12
        self.is_level_up = 2
        
        progress = self.control.game_progress
        
        if win:
            progress["next_level_up"] -= 1
            if progress["next_level_up"] <= 0 and progress["level"] < 99:
                self._level_up()
                self.is_level_up = 0
                # Play level up sound
            else:
                pass
        else:
            progress["next_level_down"] -= 1
            if progress["next_level_down"] <= 0 and progress["level"] > 1:
                self._level_down()
                self.is_level_up = 1
                # Play level down sound
                
        if self.is_level_up == 2:
            # Skip directly to position
            self.start_position(win, not win)

    def _level_up(self):
        progress = self.control.game_progress
        progress["level"] += 1
        progress["next_level_up"] = 5
        progress["next_level_down"] = 5
        
        # Increase stats
        for i, char_stats in enumerate(self.game.state.char_stats):
            char_stats["hp"] += random.randint(1, 4)
            char_stats["spirit"] += random.randint(1, 4)
            char_stats["stamina"] += random.randint(1, 4)
            char_stats["skill"] += random.randint(1, 4)
            
            # Caps (from GML)
            if i == 0: # Takuya
                char_stats["hp"] = min(char_stats["hp"], 210)
                char_stats["spirit"] = min(char_stats["spirit"], 175)
                char_stats["stamina"] = min(char_stats["stamina"], 160)
                char_stats["skill"] = min(char_stats["skill"], 170)
            elif i == 1: # Koji
                char_stats["hp"] = min(char_stats["hp"], 210)
                char_stats["spirit"] = min(char_stats["spirit"], 160)
                char_stats["stamina"] = min(char_stats["stamina"], 160)
                char_stats["skill"] = min(char_stats["skill"], 185)
            elif i == 2: # JP
                char_stats["hp"] = min(char_stats["hp"], 240)
                char_stats["spirit"] = min(char_stats["spirit"], 195)
                char_stats["stamina"] = min(char_stats["stamina"], 150)
                char_stats["skill"] = min(char_stats["skill"], 180)
            elif i == 3: # Zoe
                char_stats["hp"] = min(char_stats["hp"], 185)
                char_stats["spirit"] = min(char_stats["spirit"], 150)
                char_stats["stamina"] = min(char_stats["stamina"], 190)
                char_stats["skill"] = min(char_stats["skill"], 165)
            elif i == 4: # Tommy
                char_stats["hp"] = min(char_stats["hp"], 100)
                char_stats["spirit"] = min(char_stats["spirit"], 180)
                char_stats["stamina"] = min(char_stats["stamina"], 140)
                char_stats["skill"] = min(char_stats["skill"], 180)
            elif i == 5: # Koichi
                char_stats["hp"] = min(char_stats["hp"], 110)
                char_stats["spirit"] = min(char_stats["spirit"], 185)
                char_stats["stamina"] = min(char_stats["stamina"], 160)
                char_stats["skill"] = min(char_stats["skill"], 160)

    def _level_down(self):
        progress = self.control.game_progress
        progress["level"] -= 1
        progress["next_level_up"] = 5
        progress["next_level_down"] = 5
        
        # Decrease stats
        for char_stats in self.game.state.char_stats:
            char_stats["hp"] = max(0, char_stats["hp"] - random.randint(1, 4))
            char_stats["spirit"] = max(0, char_stats["spirit"] - random.randint(1, 4))
            char_stats["stamina"] = max(0, char_stats["stamina"] - random.randint(1, 4))
            char_stats["skill"] = max(0, char_stats["skill"] - random.randint(1, 4))

    def start_position(self, happy, sad):
        """Start position transition (walking back to map)"""
        self.state = "POSITION"
        self.counter = 0
        self.alarm_timer = 6
        self.happy = happy
        self.sad = sad

    def update(self, delta_time):
        if self.state == "LEVEL_CHANGE":
            self.alarm_timer -= delta_time * 60
            if self.alarm_timer <= 0:
                self.counter += 1
                self.alarm_timer = 12
                # Wait for animation to finish
                if self.counter > 14: # Arbitrary wait
                    self.start_position(self.is_level_up == 0, self.is_level_up == 1)
                    
        elif self.state == "POSITION":
            self.alarm_timer -= delta_time * 60
            if self.alarm_timer <= 0:
                self.counter += 1
                self.alarm_timer = 6
                if self.counter == 24:
                    return "TRANSITION_COMPLETE"
        
        return None
        
    def draw(self, screen):
        if self.state == "LEVEL_CHANGE":
            if self.is_level_up != 2:
                frames = self.game.assets.get_animation("change_level")
                if frames:
                    # 0: Up, 1: Down
                    idx = 0 if self.is_level_up == 0 else 1
                    if idx < len(frames):
                        sprite = frames[idx]
                        scale = 6
                        scaled = pygame.transform.scale(sprite, 
                            (sprite.get_width() * scale, sprite.get_height() * scale))
                        
                        x = (screen.get_width() - scaled.get_width()) // 2
                        y = (screen.get_height() - scaled.get_height()) // 2
                        screen.blit(scaled, (x, y))
                        
        elif self.state == "POSITION":
            # Draw walking animation
            # This replicates obj_position_dtector which shows character walking
            # For now, maybe just show character?
            pass
