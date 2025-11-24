import pygame
import random

class EventManager:
    """
    Manages random events and story events.
    Placeholder for Phase 6.
    """
    def __init__(self, game):
        self.game = game
        self.state = "IDLE"
        self.timer = 0
        
    def start_event(self):
        """Start a random event"""
        self.state = "EVENT_ACTIVE"
        self.timer = 60 # 1 second placeholder
        print("Event Started!")
        
    def update(self, delta_time):
        if self.state == "EVENT_ACTIVE":
            self.timer -= delta_time * 60
            if self.timer <= 0:
                self.state = "IDLE"
                return "EVENT_COMPLETE"
        return None
        
    def draw(self, screen):
        if self.state == "EVENT_ACTIVE":
            # Draw event sprite
            sprite = self.game.assets.get_sprite("event_alert")
            if sprite:
                scale = 6
                scaled = pygame.transform.scale(sprite, 
                    (sprite.get_width() * scale, sprite.get_height() * scale))
                
                x = screen.get_width() // 2 - scaled.get_width() // 2
                y = screen.get_height() // 2 - scaled.get_height() // 2
                screen.blit(scaled, (x, y))
