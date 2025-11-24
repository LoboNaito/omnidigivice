import pygame
from src.game.dtector import DtectorGame

class Engine:
    def __init__(self, screen):
        self.screen = screen
        self.game = DtectorGame()
        
    def handle_input(self, event):
        self.game.handle_input(event)
        
    def update(self, delta_time):
        self.game.update(delta_time)
        
    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear screen with black
        self.game.draw(self.screen)
