import pygame
import os

class AssetManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.sprites = {}
        self.sounds = {}
        
    def load_sprite(self, name, filename):
        """
        Loads a sprite from the Sprites directory.
        """
        if name in self.sprites:
            return self.sprites[name]
            
        path = os.path.join(self.base_path, "Sprites", filename)
        if not os.path.exists(path):
            print(f"Warning: Sprite file not found: {path}")
            return None
            
        try:
            image = pygame.image.load(path).convert_alpha()
            self.sprites[name] = image
            return image
        except Exception as e:
            print(f"Error loading sprite {filename}: {e}")
            return None

    def get_sprite(self, name):
        return self.sprites.get(name)
        
    def load_animation(self, name_prefix, filename_prefix, frame_count):
        """
        Loads a sequence of sprites for an animation.
        e.g. load_animation("takuya_walk", "spr_takuya_step", 2)
        will load spr_takuya_step_0.png and spr_takuya_step_1.png
        """
        frames = []
        for i in range(frame_count):
            filename = f"{filename_prefix}_{i}.png"
            path = os.path.join(self.base_path, "Sprites", filename)
            
            if not os.path.exists(path):
                print(f"Warning: Sprite file not found: {path}")
                continue
                
            try:
                image = pygame.image.load(path).convert_alpha()
                frames.append(image)
            except Exception as e:
                print(f"Error loading sprite {filename}: {e}")
        
        if frames:
            self.sprites[name_prefix] = frames
            return frames
        return None

    def get_animation(self, name):
        return self.sprites.get(name)
        
    def load_all_character_sprites(self):
        """
        Preloads common character sprites.
        """
        # Takuya
        self.load_animation("takuya_idle", "spr_takuya", 2)
        self.load_animation("takuya_walk", "spr_takuya_step", 2)
        self.load_sprite("takuya_happy", "spr_takuya_happy_0.png")
        self.load_sprite("takuya_defeat", "spr_takuya_defeat_0.png")
        
        # Koji
        self.load_animation("koji_idle", "spr_koji", 2)
        self.load_animation("koji_walk", "spr_koji_step", 2)
        self.load_sprite("koji_happy", "spr_koji_happy_0.png")
        self.load_sprite("koji_defeat", "spr_koji_defeat_0.png")
        
        # JP
        self.load_animation("jp_idle", "spr_jp", 2)
        self.load_animation("jp_walk", "spr_jp_step", 2)
        self.load_sprite("jp_happy", "spr_jp_happy_0.png")
        self.load_sprite("jp_defeat", "spr_jp_defeat_0.png")
        
        # Zoe
        self.load_animation("zoe_idle", "spr_zoe", 2)
        self.load_animation("zoe_walk", "spr_zoe_step", 2)
        self.load_sprite("zoe_happy", "spr_zoe_happy_0.png")
        self.load_sprite("zoe_defeat", "spr_zoe_defeat_0.png")
        
        # Tommy
        self.load_animation("tommy_idle", "spr_tommy", 2)
        self.load_animation("tommy_walk", "spr_tommy_step", 2)
        self.load_sprite("tommy_happy", "spr_tommy_happy_0.png")
        self.load_sprite("tommy_defeat", "spr_tommy_defeat_0.png")
        
        # Koichi
        self.load_animation("koichi_idle", "spr_koichi", 2)
        self.load_animation("koichi_walk", "spr_koichi_step", 2)
        self.load_sprite("koichi_happy", "spr_koichi_happy_0.png")
        self.load_sprite("koichi_defeat", "spr_koichi_defeat_0.png")

    def load_digimon_sprite(self, digimon_name):
        """
        Loads a specific Digimon's sprite.
        Assumes naming convention: spr_{name}_dtector_0.png or spr_{name}_0.png
        """
        # Try dtector specific sprite first
        filename = f"spr_{digimon_name}_dtector_0.png"
        path = os.path.join(self.base_path, "Sprites", filename)
        
        if not os.path.exists(path):
            # Try generic sprite
            filename = f"spr_{digimon_name}_0.png"
            path = os.path.join(self.base_path, "Sprites", filename)
            
        if os.path.exists(path):
            # Load as a single-frame animation for consistency with battle code
            try:
                image = pygame.image.load(path).convert_alpha()
                self.sprites[f"digimon_{digimon_name}"] = [image]
            except Exception as e:
                print(f"Error loading digimon sprite {filename}: {e}")
        else:
            print(f"Warning: Could not find sprite for Digimon: {digimon_name}")

    def load_ui_sprites(self):
        """
        Loads UI elements, backgrounds, and menu icons.
        """
        # Main Menu Sprite (5 frames: 0-4 for Map/Status/Spirits/Camp/Connect)
        self.load_animation("menu_main", "spr_main_menu_dtector", 5)
        
        # Extra Menu Sprites (4 frames: 0-3)
        self.load_animation("menu_extra", "spr_menu_extra_dtector", 4)
        
        # Connection Menu
        self.load_animation("menu_connect", "spr_menu_con_dtector", 2)
        
        # Submenu Sprites
        # Status screen
        self.load_animation("status_select", "spr_sel_dtector", 4)
        self.load_animation("status_detail", "spr_status_detail_dtector", 4)
        
        # Map screen
        self.load_animation("map_screen", "spr_map_dtector", 4)
        self.load_animation("map_5", "spr_map_5_dtector", 3)
        
        # Camp screen
        self.load_animation("camp_screen", "spr_camp_dtector", 2)
        
        # Database screen
        self.load_animation("database_screen", "spr_database_dtector", 6)
        self.load_animation("database_stats", "spr_database_stats_dtector", 2)
        
        # Spirits screen
        self.load_animation("spirits_display", "spr_spirits_dtector", 12)
        
        # Battle sprites
        self.load_animation("battle_menu_dtector", "spr_battle_menu_dtector", 4)
        self.load_animation("summon_dtector", "spr_summon_dtector", 6)
        self.load_animation("battle_call", "spr_battle_call_dtector", 9)
        self.load_animation("energy_dtector", "spr_energy_dtector", 12)
        self.load_animation("collision_dtector", "spr_collision_dtector", 1)
        self.load_animation("scan_dtector", "spr_scan_dtector", 5)
        self.load_animation("hit_dtector", "spr_hit_dtector", 2)
        self.load_sprite("life_dtector", "spr_life_dtector_0.png")
        self.load_animation("numbers_white", "spr_numbers_white", 10)
        
        # Spirit Evolution Sprites
        self.load_animation("spirits_dtector", "spr_spirits_dtector", 12)
        self.load_animation("catch_dtector", "spr_catch_dtector", 2)
        
        # Map Sprites
        self.load_animation("map_dtector", "spr_map_dtector", 4)
        self.load_animation("map_cover_dtector", "spr_map_cover_dtector", 2)
        self.load_animation("area_dtector", "spr_area_dtector", 12)
        self.load_animation("change_map_dtector", "spr_change_map_dtector", 1)
        
        # Evolution Sprites
        self.load_animation("ancient_dtector", "spr_ancient_dtector", 2)
        self.load_animation("ancient_cover_dtector", "spr_ancient_cover_dtector", 4)
        
        # Event Sprites
        self.load_sprite("event_alert", "spr_event_0.png")
        
        # Generic UI
        self.load_sprite("menu_cursor", "spr_menu_sel_0.png")
        self.load_sprite("happy", "spr_happy_0.png")
        self.load_sprite("defeat_dtector", "spr_defeat_dtector_0.png")
        
        # Fonts
        self.load_animation("font_dtector", "spr_font_dtector", 38)
        self.load_animation("numbers", "spr_numbers", 10)
        
        # Level Up
        self.load_animation("change_level", "spr_change_level_dtector", 2)
