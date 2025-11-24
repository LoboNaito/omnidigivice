import pygame
import sys
from src.engine.core import Engine

def main():
    pygame.init()
    pygame.display.set_caption("Digivice D-Tector Emulator")
    
    # Screen dimensions based on original or reasonable scale
    # Original D-Tector screen is small (likely 30x32), we'll scale it up by 6
    SCREEN_WIDTH = 180
    SCREEN_HEIGHT = 192
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    
    engine = Engine(screen)
    
    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0  # 60 FPS
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                engine.handle_input(event)
        
        engine.update(delta_time)
        engine.draw()
        
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
