import pygame

class MapManager:
    """
    Manages the Map Selection Screen.
    Ports logic from:
    - obj_map_dtector
    - obj_map_swap_dtector
    - fun_map_area_funtions_dtector
    """
    def __init__(self, game):
        self.game = game
        self.control = game.state
        
        # State: "SELECT", "SWAP_ANIM", "AREA_DISPLAY"
        self.state = "SELECT"
        
        # Map variables
        self.map = 0
        self.aux_area = self.control.game_progress["current_area"]
        self.pos_x = 0
        self.pos_y = 0
        self.current_menu = 0
        self.display = False
        self.change = 0 # 0=Select, 1=Confirm/Anim
        
        # Initialize map based on current area
        self._init_map_from_area()
        
        # Animation timer
        self.alarm_timer = 12
        self.blink_timer = 0
        self.swap_timer = 0
        
    def _init_map_from_area(self):
        # Logic from obj_map_dtector Create
        area = self.control.game_progress["current_area"]
        self.aux_area = area
        self.map = self._find_current_map(area)
        
    def _find_current_map(self, area):
        # Ports fun_find_current_map
        if 0 <= area <= 2: return 0
        elif 3 <= area <= 5: return 1
        elif 6 <= area <= 8: return 2
        elif 9 <= area <= 11: return 3
        elif area >= 12: return 4 # Map 5
        return 0

    def check_progression(self):
        """
        Checks if the current area is complete and handles transitions.
        Called after a boss victory.
        Ports logic from obj_map_swap_dtector Create event.
        """
        progress = self.control.game_progress
        current_area = progress["current_area"]
        
        # Mark current area as complete
        if current_area < len(progress["area_status"]):
            progress["area_status"][current_area] = True
            
        # Check if all maps are complete (0-11)
        all_maps_complete = True
        for i in range(12): # Check first 12 areas
            if i < len(progress["area_status"]) and not progress["area_status"][i]:
                all_maps_complete = False
                break
                
        if all_maps_complete:
            # Transition to Map 5 (Dark Area)
            # In GML this triggers obj_map5_swap_dtector animation
            # For now, we'll just transition directly or set a flag
            print("All maps complete! Unlocking Dark Area...")
            progress["current_area"] = 12
            # Reset distance for new area (needs area_distance array in state)
            # progress["distance"] = self.control.area_distance[12] 
            return "MAP_5_UNLOCK"
            
        # Check for map change (e.g. Map 0 -> Map 1)
        change_map = self._is_change_map(current_area, progress["area_status"])
        
        if change_map["change"]:
            # Switch to new map
            print(f"Map Complete! Moving to Area {change_map['new_area']}")
            progress["current_area"] = change_map["new_area"]
            # progress["distance"] = self.control.area_distance[change_map['new_area']]
            return "MAP_CHANGE"
        else:
            # Switch to next area in current map
            new_area = self._change_area(current_area, progress["area_status"])
            if new_area != -1:
                print(f"Area Complete! Moving to Area {new_area}")
                progress["current_area"] = new_area
                # progress["distance"] = self.control.area_distance[new_area]
                return "AREA_CHANGE"
                
        return "NONE"

    def _is_change_map(self, area, status):
        # Ports fun_is_change_map
        # Returns dict: {"change": bool, "new_area": int}
        result = {"change": False, "new_area": 0}
        
        # Helper to check range
        def check_range(start, end):
            for i in range(start, end + 1):
                if i >= len(status) or not status[i]:
                    return False
            return True

        if area <= 2 and check_range(0, 2):
            return {"change": True, "new_area": 3}
        elif area <= 5 and check_range(3, 5):
            return {"change": True, "new_area": 6}
        elif area <= 8 and check_range(6, 8):
            return {"change": True, "new_area": 9}
        elif area <= 11 and check_range(9, 11):
            return {"change": True, "new_area": 0} # Loop or special handling?
            
        return result

    def _change_area(self, area, status):
        # Ports fun_change_area
        # Finds next incomplete area in the current map group
        total = len(status)
        if total <= 0: return -1
        
        # Ensure area is within bounds
        area = ((area % total) + total) % total
        
        # Find group (0-2, 3-5, etc.)
        group_start = (area // 3) * 3
        group_end = min(group_start + 2, total - 1)
        group_size = (group_end - group_start) + 1
        
        for offset in range(1, group_size):
            candidate = group_start + (((area - group_start) + offset) % group_size)
            if candidate < len(status) and not status[candidate]:
                return candidate
                
        return -1

    def update(self, delta_time):
        # Blink timer for display
        self.alarm_timer -= delta_time * 60
        if self.alarm_timer <= 0:
            self.display = not self.display
            self.alarm_timer = 12
            
        # Map Swap Animation
        if self.state == "SWAP_ANIM":
            speed = 60 * delta_time # 1 pixel per frame at 60fps
            # GML increments by 1 every 6 frames? No, alarm[0]=6 then pos++, so very slow?
            # Wait, Alarm 0 is set to 6. Then inside it sets alarm[0]=6.
            # So it updates every 6 frames (10fps).
            # pos increments by 1.
            # So speed is 1 pixel every 0.1 seconds.
            # That's slow. Let's speed it up for Python or match it.
            # Let's try 5 pixels per second (30 * delta).
            
            # Actually, let's just use a timer to match GML frame logic
            self.swap_timer += delta_time * 60
            if self.swap_timer >= 6:
                self.swap_timer = 0
                self.pos_x += 1
                self.pos_y += 1
                
                scale = 6 # Used for threshold check logic
                # Thresholds from GML (33 and 31) are in pixels.
                # Our draw uses pos_x/pos_y directly subtracted from coords.
                # So we just track the raw GML value.
                
                if self.map == 0 and self.pos_y >= 33:
                    self.pos_y = 0
                    self.pos_x = 0
                    self.map = 1
                    self.state = "SELECT"
                elif self.map == 1 and self.pos_x >= 31:
                    self.pos_y = 0
                    self.pos_x = 0
                    self.map = 2
                    self.state = "SELECT"
                elif self.map == 2 and self.pos_y >= 33:
                    self.pos_y = 0
                    self.pos_x = 0
                    self.map = 3
                    self.state = "SELECT"
                elif self.map == 3 and self.pos_x >= 31:
                    self.pos_y = 0
                    self.pos_x = 0
                    self.map = 0
                    self.state = "SELECT"
            
        return None

    def handle_input(self, event):
        if self.state == "SELECT":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    # Cancel / Exit
                    if self.change == 1:
                        self.change = 0
                        # Play cancel sound
                    else:
                        # Exit to Main Menu
                        self.game.menu_manager.pop_menu()
                        
                elif event.key == pygame.K_RIGHT:
                    if self.map == 4:
                        # Map 5 Logic
                        if self.current_menu == 0:
                            self.current_menu = 1
                            # Play sound
                        elif self.current_menu == 1:
                            self.aux_area = 12
                            return "MAP_SELECTED"
                    else:
                        # Logic from KeyPress_39 for Maps 0-3
                        if self.change == 0:
                            self.change = 1
                            self.aux_area = self.control.game_progress["current_area"]
                            
                            # If current area is not in this map, default to start of map
                            current_map_of_area = self._find_current_map(self.aux_area)
                            if self.map != current_map_of_area:
                                if self.map == 0: self.aux_area = 0
                                elif self.map == 1: self.aux_area = 3
                                elif self.map == 2: self.aux_area = 6
                                elif self.map == 3: self.aux_area = 9
                            
                            # Play select sound
                        elif self.change == 1:
                            # Confirm selection
                            # Play select sound
                            return "MAP_SELECTED"
                        
                elif event.key == pygame.K_DOWN:
                    if self.map == 4:
                        pass # No vertical nav in Map 5?
                    else:
                        if self.change == 0:
                            # Cycle Map
                            self.state = "SWAP_ANIM"
                            self.swap_timer = 0
                            # Play select sound
                        elif self.change == 1:
                            # Cycle Area
                            self.aux_area += 1
                            
                            # Wrap around based on map
                            if self.map == 0:
                                if self.aux_area > 2: self.aux_area = 0
                            elif self.map == 1:
                                if self.aux_area > 5: self.aux_area = 3
                            elif self.map == 2:
                                if self.aux_area > 8: self.aux_area = 6
                            elif self.map == 3:
                                if self.aux_area > 11: self.aux_area = 9
                            
                            # Play select sound
                            
                elif event.key == pygame.K_LEFT:
                    # Cancel selection (Alternative to UP?)
                    # GML doesn't seem to use LEFT for cancel in KeyPress_38/40/39 logic directly?
                    # But user might expect it.
                    if self.map == 4:
                        if self.current_menu == 1:
                            self.current_menu = 0
                    else:
                        if self.change == 1:
                            self.change = 0
                        
        return None

    def draw(self, screen):
        # Logic from obj_map_dtector Draw
        frames = self.game.assets.get_animation("map_dtector")
        cover_frames = self.game.assets.get_animation("map_cover_dtector")
        area_frames = self.game.assets.get_animation("area_dtector")
        
        if not (frames and cover_frames):
            return
            
        scale = 6
        map_w = frames[0].get_width() * scale
        map_h = frames[0].get_height() * scale
        
        # Create a viewport surface for clipping
        viewport = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
        
        # Draw relative to viewport (0, 0)
        # Offsets (pos_x, pos_y) shift the map content within the viewport
        
        # Draw Map Background
        if self.map == 0:
            self._draw_scaled(viewport, frames[0], 0, 0 - (self.pos_y * scale), scale)
            self._draw_scaled(viewport, frames[1], 0, (32*scale) - (self.pos_y * scale), scale)
            
            offset_y = self.pos_y * scale
            self._draw_area_indicator(viewport, 0, 15*scale, 20*scale - offset_y, scale)
            self._draw_area_indicator(viewport, 1, 3*scale, 26*scale - offset_y, scale)
            self._draw_area_indicator(viewport, 2, 23*scale, 26*scale - offset_y, scale)
            
        elif self.map == 1:
            offset_x = self.pos_x * scale
            self._draw_scaled(viewport, frames[1], 0 - offset_x, 0, scale)
            self._draw_scaled(viewport, frames[2], (30*scale) - offset_x, 0, scale)
            
            self._draw_area_indicator(viewport, 3, 11*scale - offset_x, 6*scale, scale)
            self._draw_area_indicator(viewport, 4, 25*scale - offset_x, 8*scale, scale)
            self._draw_area_indicator(viewport, 5, 23*scale - offset_x, 18*scale, scale)

        elif self.map == 2:
            offset_y = self.pos_y * scale
            self._draw_scaled(viewport, frames[2], 0, 0 + offset_y, scale)
            self._draw_scaled(viewport, frames[3], 0, (-32*scale) + offset_y, scale)
            
            self._draw_area_indicator(viewport, 6, 2*scale, 12*scale + offset_y, scale)
            self._draw_area_indicator(viewport, 7, 8*scale, 2*scale + offset_y, scale)
            self._draw_area_indicator(viewport, 8, 20*scale, 9*scale + offset_y, scale)
            
        elif self.map == 3:
            offset_x = self.pos_x * scale
            self._draw_scaled(viewport, frames[3], 0 + offset_x, 0, scale)
            self._draw_scaled(viewport, frames[0], (-30*scale) + offset_x, 0, scale)
            
            self._draw_area_indicator(viewport, 9, 24*scale + offset_x, 26*scale, scale)
            self._draw_area_indicator(viewport, 10, 5*scale + offset_x, 23*scale, scale)
            self._draw_area_indicator(viewport, 11, 12*scale + offset_x, 17*scale, scale)

        elif self.map == 4:
            # Map 5 (Dark Area / Final)
            map5_frames = self.game.assets.get_animation("map_5")
            if map5_frames:
                frame_idx = self.current_menu + 1
                if frame_idx < len(map5_frames):
                    self._draw_scaled(viewport, map5_frames[frame_idx], 0, 0, scale)
                    
                if self.display:
                    self._draw_scaled(viewport, cover_frames[0], 11*scale, 17*scale, scale)

        # Draw Area Name/Icon if confirming change
        if self.change == 1 and area_frames:
            aux_area_y = 0
            if self.map == 1 or self.map == 2:
                aux_area_y = 24 * scale
            
            if self.aux_area < len(area_frames):
                self._draw_scaled(viewport, area_frames[self.aux_area], 0, 0 + aux_area_y, scale)

        # Draw Confirm Screen (Distance)
        if self.state == "CONFIRM":
            change_frames = self.game.assets.get_animation("change_map_dtector")
            if change_frames:
                # Draw change map background (likely covers everything)
                self._draw_scaled(viewport, change_frames[0], 0, 0, scale)
                
                # Calculate distance
                progress = self.control.game_progress
                dist = self.control.area_distance[self.aux_area]
                
                if progress["area_status"][self.aux_area]:
                    dist = dist // 2
                    
                if progress["current_area"] == self.aux_area:
                    dist = progress["distance"]
                    
                # Draw distance number
                # GML: draw_number_with_sprite(new_distance, x + 26, y + 24, spr_numbers);
                # Our viewport is 30x32. x+26 is right edge.
                # We need to draw it relative to viewport.
                # TextRenderer draws to screen, but we want to draw to viewport?
                # Actually TextRenderer takes a surface.
                
                # Position: x=26, y=24 relative to viewport (0,0)
                # Scale is 6. So 26*6, 24*6.
                self.game.text_renderer.draw_number(viewport, dist, 26*scale, 24*scale, align="right", scale=scale)

        # Blit viewport to center of screen
        x = (screen.get_width() - map_w) // 2
        y = (screen.get_height() - map_h) // 2
        screen.blit(viewport, (x, y))

    def handle_input(self, event):
        if self.state == "SELECT":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    # Cancel / Exit
                    if self.change == 1:
                        self.change = 0
                        # Play cancel sound
                    else:
                        # Exit to Main Menu
                        self.game.menu_manager.pop_menu()
                        
                elif event.key == pygame.K_RIGHT:
                    if self.map == 4:
                        # Map 5 Logic
                        if self.current_menu == 0:
                            self.current_menu = 1
                            # Play sound
                        elif self.current_menu == 1:
                            self.aux_area = 12
                            return "MAP_SELECTED"
                    else:
                        # Logic from KeyPress_39 for Maps 0-3
                        if self.change == 0:
                            self.change = 1
                            self.aux_area = self.control.game_progress["current_area"]
                            
                            # If current area is not in this map, default to start of map
                            current_map_of_area = self._find_current_map(self.aux_area)
                            if self.map != current_map_of_area:
                                if self.map == 0: self.aux_area = 0
                                elif self.map == 1: self.aux_area = 3
                                elif self.map == 2: self.aux_area = 6
                                elif self.map == 3: self.aux_area = 9
                            
                            # Play select sound
                        elif self.change == 1:
                            # Go to Confirm State
                            self.state = "CONFIRM"
                            # Play select sound
                        
                elif event.key == pygame.K_DOWN:
                    if self.map == 4:
                        pass # No vertical nav in Map 5?
                    else:
                        if self.change == 0:
                            # Cycle Map
                            self.state = "SWAP_ANIM"
                            self.swap_timer = 0
                            # Play select sound
                        elif self.change == 1:
                            # Cycle Area
                            self.aux_area += 1
                            
                            # Wrap around based on map
                            if self.map == 0:
                                if self.aux_area > 2: self.aux_area = 0
                            elif self.map == 1:
                                if self.aux_area > 5: self.aux_area = 3
                            elif self.map == 2:
                                if self.aux_area > 8: self.aux_area = 6
                            elif self.map == 3:
                                if self.aux_area > 11: self.aux_area = 9
                            
                            # Play select sound
                            
                elif event.key == pygame.K_LEFT:
                    # Cancel selection
                    if self.map == 4:
                        if self.current_menu == 1:
                            self.current_menu = 0
                    else:
                        if self.change == 1:
                            self.change = 0
                            
        elif self.state == "CONFIRM":
             if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    # Confirm Selection
                    progress = self.control.game_progress
                    
                    # Update current area
                    progress["current_area"] = self.aux_area
                    
                    # Update distance
                    dist = self.control.area_distance[self.aux_area]
                    if progress["area_status"][self.aux_area]:
                        dist = dist // 2
                    
                    # If it was already current area, keep remaining distance?
                    # GML logic: if (control.game_progress.current_area == aux_area) new_distance = control.game_progress.distance;
                    # But we just set current_area = aux_area above.
                    # So we should check BEFORE setting.
                    # Wait, if I select a NEW area, I want full distance.
                    # If I select CURRENT area, I want remaining distance.
                    # But I just overwrote current_area.
                    
                    # Let's fix logic:
                    if progress["current_area"] != self.aux_area:
                         progress["distance"] = dist
                         progress["current_area"] = self.aux_area
                    else:
                         # Already current area, keep distance (don't reset)
                         pass
                         
                    return "MAP_SELECTED"
                    
                elif event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    # Cancel back to selection
                    self.state = "SELECT"
                        
        return None

    def _draw_area_indicator(self, screen, area_idx, x, y, scale):
        # Note: 'screen' here is now the viewport surface
        cover_frames = self.game.assets.get_animation("map_cover_dtector")
        if area_idx >= len(self.control.game_progress["area_status"]):
            return

        status = self.control.game_progress["area_status"][area_idx]
        current_area = self.control.game_progress["current_area"]
        
        should_draw = False
        frame_idx = 0
        
        if self.change != 1:
            if current_area == area_idx:
                if self.display:
                    should_draw = True
                    frame_idx = 1 if status else 0
            elif status:
                should_draw = True
                frame_idx = 0
        else:
            if self.aux_area == area_idx:
                if self.display:
                    should_draw = True
                    frame_idx = 1 if status else 0
        
        if should_draw and cover_frames:
            self._draw_scaled(screen, cover_frames[frame_idx], x, y, scale)
    def _draw_scaled(self, screen, sprite, x, y, scale):
        scaled = pygame.transform.scale(sprite, 
            (sprite.get_width() * scale, sprite.get_height() * scale))
        screen.blit(scaled, (x, y))
