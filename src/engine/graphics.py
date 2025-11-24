import pygame

class TextRenderer:
    def __init__(self, asset_manager):
        self.assets = asset_manager
        
    def draw_text(self, screen, text, x, y, scale=1, spacing=6):
        """
        Draws text using spr_font_dtector.
        Replicates fun_text_to_sprites GML logic.
        """
        font_frames = self.assets.get_animation("font_dtector")
        if not font_frames:
            return
            
        text = text.lower()
        current_x = x
        
        for char in text:
            char_code = ord(char)
            frame_index = -1
            
            # a-z: 97-122 -> 0-25
            if 97 <= char_code <= 122:
                frame_index = char_code - 97
            # 0-9: 48-57 -> 26-35
            elif 48 <= char_code <= 57:
                frame_index = (char_code - 48) + 26
            # Space: 32 -> skip
            elif char_code == 32:
                current_x += spacing * scale
                continue
                
            if frame_index != -1 and frame_index < len(font_frames):
                sprite = font_frames[frame_index]
                if scale != 1:
                    sprite = pygame.transform.scale(sprite, 
                        (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
import pygame

class TextRenderer:
    def __init__(self, asset_manager):
        self.assets = asset_manager
        
    def draw_text(self, screen, text, x, y, scale=1, spacing=6):
        """
        Draws text using spr_font_dtector.
        Replicates fun_text_to_sprites GML logic.
        """
        font_frames = self.assets.get_animation("font_dtector")
        if not font_frames:
            return
            
        text = text.lower()
        current_x = x
        
        for char in text:
            char_code = ord(char)
            frame_index = -1
            
            # a-z: 97-122 -> 0-25
            if 97 <= char_code <= 122:
                frame_index = char_code - 97
            # 0-9: 48-57 -> 26-35
            elif 48 <= char_code <= 57:
                frame_index = (char_code - 48) + 26
            # Space: 32 -> skip
            elif char_code == 32:
                current_x += spacing * scale
                continue
                
            if frame_index != -1 and frame_index < len(font_frames):
                sprite = font_frames[frame_index]
                if scale != 1:
                    sprite = pygame.transform.scale(sprite, 
                        (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
                screen.blit(sprite, (current_x, y))
                
            current_x += spacing * scale

    def draw_number(self, screen, number, x, y, sprite_name="numbers", scale=1, spacing=1, align="left"):
        """
        Draws a number using sprite digits.
        """
        s_num = str(number)
        frames = self.assets.get_animation(sprite_name)
        
        if not frames:
            return
            
        total_width = 0
        digit_width = frames[0].get_width() * scale
        
        # Calculate total width first for alignment
        total_width = len(s_num) * (digit_width + spacing * scale) - (spacing * scale)
        
        start_x = x
        if align == "center":
            start_x = x - total_width // 2
        elif align == "right":
            start_x = x - total_width
            
        current_x = start_x
        
        for char in s_num:
            if char.isdigit():
                digit = int(char)
                if digit < len(frames):
                    sprite = frames[digit]
                    scaled = pygame.transform.scale(sprite, 
                        (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
                    screen.blit(scaled, (current_x, y))
                    current_x += scaled.get_width() + spacing * scale
            else:
                # Handle non-digits if necessary (e.g. / or :)
                pass

    def draw_text_scrolling(self, screen, text, x, y, width, height, scroll_offset, scale=1, spacing=6):
        """
        Draws text with scrolling and clipping.
        x, y, width, height define the visible box.
        scroll_offset is the pixel amount to shift left.
        """
        # Create a surface for the text box
        box_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw text onto the surface at -scroll_offset
        # We use the existing draw_text logic but adapted for the surface
        text = str(text).lower()
        frames = self.assets.get_animation("font_dtector")
        
        if not frames:
            return

        char_width = 5 * scale # Approx width of font sprite (most are 5x7)
        current_x = -scroll_offset
        
        # Mapping from char to frame index (same as draw_text)
        # a-z: 0-25
        # 0-9: 26-35
        # space: -1 (skip)
        # .: 36
        # !: 37
        
        for char in text:
            frame_idx = -1
            code = ord(char)
            
            if 97 <= code <= 122: # a-z
                frame_idx = code - 97
            elif 48 <= code <= 57: # 0-9
                frame_idx = code - 48 + 26
            elif char == ".":
                frame_idx = 36
            elif char == "!":
                frame_idx = 37
            elif char == " ":
                current_x += spacing * scale # Advance for space
                continue
                
            if frame_idx != -1 and frame_idx < len(frames):
                sprite = frames[frame_idx]
                scaled = pygame.transform.scale(sprite, 
                    (int(sprite.get_width() * scale), int(sprite.get_height() * scale)))
                
                # Only draw if visible
                if current_x + scaled.get_width() > 0 and current_x < width:
                    box_surf.blit(scaled, (current_x, 0)) # y is 0 relative to box
                
            current_x += spacing * scale
                
        # Blit the box surface to the screen
        screen.blit(box_surf, (x, y))
