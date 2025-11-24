import pygame
import os

def main():
    pygame.init()
    try:
        path = os.path.join("Sprites", "spr_map_dtector_0.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            print(f"spr_map_dtector size: {img.get_width()}x{img.get_height()}")
        else:
            print("Sprite not found")
            
        path = os.path.join("Sprites", "spr_main_menu_dtector_0.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            print(f"spr_main_menu_dtector size: {img.get_width()}x{img.get_height()}")
            
        path = os.path.join("Sprites", "spr_area_dtector_0.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            print(f"spr_area_dtector size: {img.get_width()}x{img.get_height()}")
            
        path = os.path.join("Sprites", "spr_map_cover_dtector_0.png")
        if os.path.exists(path):
            img = pygame.image.load(path)
            print(f"spr_map_cover_dtector size: {img.get_width()}x{img.get_height()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
