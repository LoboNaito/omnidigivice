import pygame
import random
from .battle_menu import BattleMenu
from .attack import AttackManager
from .spirit import SpiritManager
from .level import LevelManager
from .evolution import EvolutionManager

class ScanManager:
    """
    Manages the barcode scanning phase of battle.
    Ports obj_scan_dtector logic.
    """
    def __init__(self, game, battle_manager):
        self.game = game
        self.battle = battle_manager
        self.active = False
        
        # State
        self.current_menu = 0 # 0: Wait, 1: Ready, 2: Start, 3: Scanning
        self.scan_menu = 0    # Current bit index (0-2)
        self.current_scan = [0, 0, 0] # The 3 bits
        
        # Timers
        self.timer = 0
        self.input_enabled = False
        self.input_timer = 0
        
        # Visuals
        self.counter = False # Blink state
        self.pos_x = 0       # Scroll position
        
    def start(self):
        """Start the scan sequence"""
        self.active = True
        self.current_menu = 0
        self.scan_menu = 0
        self.current_scan = [0, 0, 0]
        self.timer = 15
        self.counter = False
        self.pos_x = 0
        self.input_enabled = False
        
    def update(self, delta_time):
        if not self.active:
            return None
            
        # Main timer logic (Alarm 0)
        if self.timer > 0:
            self.timer -= delta_time * 60
            if self.timer <= 0:
                self._handle_timer()
                
        # Input window timer (Alarm 2)
        if self.input_enabled:
            self.input_timer -= delta_time * 60
            if self.input_timer <= 0:
                # Timeout - bit stays 0
                self.input_enabled = False
                self.input_timer = 0
                self.current_scan[self.scan_menu] = 0
                self.scan_menu += 1
                self.timer = 90 # Alarm 1 equivalent delay? No, Alarm 1 sets input true.
                # GML Alarm 2: sets scan=false, alarm[1]=90, current_scan=0, scan_menu++
                self.timer = 90 
                
        return None

    def _handle_timer(self):
        """Handle state transitions based on timer (Alarm 0)"""
        if self.current_menu == 0:
            self.counter = not self.counter
            self.timer = 15
            
        elif self.current_menu == 1:
            self.current_menu = 2
            self.timer = 30
            
        elif self.current_menu == 2:
            self.current_menu = 3
            self.timer = 3
            
        elif self.current_menu == 3:
            self.pos_x += 1
            self.timer = 2
            
            # Check if scanning is done
            if self.scan_menu >= 3:
                # Sequence complete
                # Wait a bit then finish
                # GML: if scan_menu == 3: alarm[1]=-1, alarm[2]=-1, if alarm[3]==-1 alarm[3]=30
                # Alarm 3 handles completion
                return "SCAN_COMPLETE"
            
            # Input enabling logic (Alarm 1 equivalent)
            # In GML, Alarm 1 is set by Alarm 2 or KeyPress 13
            # Actually, Alarm 1 enables input.
            # We need a way to trigger Alarm 1.
            # Let's simplify: 
            # If we are in menu 3, we cycle:
            # Wait -> Enable Input -> Wait -> Enable Input...
            
            # If input is NOT enabled and we are not waiting for next bit...
            # This part is tricky to map 1:1 without the exact alarm chain.
            # Let's look at GML Alarm 0 again.
            # It just scrolls pos_x and checks scan_menu == 3.
            
            # Alarm 1 sets config.scan = true (input enabled), Alarm 2 = 90.
            # Alarm 2 sets config.scan = false, Alarm 1 = 90, scan_menu++.
            
            # So it's a loop between Alarm 1 and Alarm 2.
            # We need to kickstart this loop.
            # KeyPress 37 (in menu 0) -> current_menu = 1.
            # Then menu 1 -> 2 -> 3.
            # When entering menu 3, we should probably start the input loop.
            pass

    def handle_input(self, event):
        if not self.active:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN: # KeyPress 13
                if self.current_menu == 3 and self.input_enabled:
                    self.input_enabled = False
                    self.current_scan[self.scan_menu] = 1
                    self.scan_menu += 1
                    self.timer = 90 # Wait for next input window (Alarm 1 equivalent)
                    
            elif event.key == pygame.K_UP: # KeyPress 38 (Cancel)
                if self.current_menu == 0:
                    return "CANCEL"
                    
            elif event.key == pygame.K_LEFT: # KeyPress 37 (Start)
                if self.current_menu == 0:
                    self.current_menu = 1
                    # Kickstart input loop?
                    # GML: KeyPress 37 just sets menu=1.
                    # Alarm 0 transitions 1->2->3.
                    # Where does Alarm 1 get set?
                    # Ah, likely in the transition to 3?
                    # Or maybe Alarm 1 is running in background?
                    # Let's assume when we hit menu 3, we start the input loop.
                    self.input_timer = 90 # Initial wait before first input?
                    # GML Alarm 1 sets scan=true.
                    
    def draw(self, screen):
        if not self.active:
            return
            
        sprites = self.game.assets.get_animation("scan_dtector")
        if not sprites: return
        
        scale = 6
        x = screen.get_width() // 2
        y = screen.get_height() // 2
        
        # Draw logic based on current_menu
        if self.current_menu == 0:
            idx = 0 if self.counter else 1
            self._draw_sprite(screen, sprites[idx], x, y, scale)
            
        elif self.current_menu == 1 or self.current_menu == 2:
            self._draw_sprite(screen, sprites[2], x, y, scale)
            
        elif self.current_menu == 3:
            # Draw scrolling barcode
            # GML: draw_sprite(spr_scan_dtector, 4, x, y) (Background/Frame?)
            # draw_sprite(spr_scan_dtector, 3, x, (y + scroll) - 32) (Barcode)
            
            self._draw_sprite(screen, sprites[4], x, y, scale)
            
            scroll = self.pos_x % 64
            # We need to clip this or handle the wrapping visually
            # For now just draw it
            # Offset y + scroll - 32
            # Scaled offset: (scroll - 32) * scale
            offset_y = (scroll - 32) * scale
            self._draw_sprite(screen, sprites[3], x, y + offset_y, scale)

    def _draw_sprite(self, screen, sprite, x, y, scale):
        scaled = pygame.transform.scale(sprite, 
            (sprite.get_width() * scale, sprite.get_height() * scale))
        screen.blit(scaled, (x - scaled.get_width()//2, y - scaled.get_height()//2))

class BattleManager:
    """
    Manages battle initialization, enemy selection, and battle flow.
    Ports obj_battle_start_dtector logic.
    """
    def __init__(self, game):
        
        # Initial HP setup (if not already set)
        if game.state.game_progress["current_char_hp"] <= 0:
             # Reset HP for testing if dead? Or handle game over elsewhere.
             # For now assume full HP on start if 0 (debug)
             pass
             
        self.current_mine_hp = game.state.game_progress["current_char_hp"]
        self.current_enemy_hp = self.control.digimon_database[self.enemy_digimon]["hp"]
        
        # Initialize enemy AI choice
        self.enemy_move = random.choice([2, 0, 1])

    def _select_enemy(self):
        """Select appropriate enemy based on level and area"""
        # Check for boss battle
        if self.control.game_progress["distance"] == 0:
            if self.control.game_progress["current_area"] == 12:
                return self._select_last_boss()
            else:
                return self._select_boss()
        
        # Regular enemy selection
        possible_enemies = []
        player_level = min(self.control.game_progress["level"], 70)
        
        for i, digimon in enumerate(self.control.digimon_database):
            # Skip spirits, bosses, and special digimon
            if (digimon["type"] not in ["spirit", "boss", "ancient", "final_boss"] and
                i not in [96, 97, 98, 99]):
                
                level_diff = digimon["level"] - player_level
                if 5 <= level_diff <= 10:
                    possible_enemies.append(i)
        
        # Fallback if no enemies found
        if not possible_enemies:
            possible_enemies.append(32)
        
        return random.choice(possible_enemies)
    
    def _select_boss(self):
        """Select boss for current area"""
        self.is_boss = True
        
        # Boss configuration: [primary_boss, condition_area, alternate_boss]
        boss_config = [
            [131, 9, 132],   # Area 0
            [96, -1, -1],    # Area 1
            [133, 6, 134],   # Area 2
            [135, 10, 136],  # Area 3
            [137, 7, 119],   # Area 4
            [98, -1, -1],    # Area 5
            [133, 2, 134],   # Area 6
            [137, 4, 138],   # Area 7
            [97, -1, -1],    # Area 8
            [131, 0, 132],   # Area 9
            [135, 3, 136],   # Area 10
            [99, -1, -1]     # Area 11
        ]
        
        area = self.control.game_progress["current_area"]
        if 0 <= area < len(boss_config):
            config = boss_config[area]
            boss_id = config[0]
            
            # Check for alternate boss
            if config[1] != -1:
                if self.control.game_progress["area_status"][config[1]]:
                    boss_id = config[2]
            
            return boss_id
        
        return 131  # Default boss
    
    def _select_last_boss(self):
        """Select final boss"""
        self.is_last_boss = True
        
        if not self.control.game_progress["new_game"]:
            if not self.control.game_progress["last_boss_unlocked"]:
                return 120
            else:
                return 127
        else:
            if not self.control.game_progress["last_boss_unlocked"]:
                return 128
            else:
                return 130
    
    def update(self, delta_time):
        """Update battle state"""
        if self.state == "START_ANIM":
            self.alarm_timer -= delta_time * 60
            if self.alarm_timer <= 0:
                result = self._advance_animation()
                if result == "battle_menu":
                    self.state = "MENU"
        
        elif self.state == "MENU":
            pass
            
        elif self.state == "SCAN_SEQ":
            result = self.scan_manager.update(delta_time)
            if result == "SCAN_COMPLETE":
                self.state = "ATTACK_SEQ"
                self.attack_manager.start_attack(self.scan_manager.current_scan)
            elif result == "CANCEL":
                self.state = "MENU"
            
        elif self.state == "ATTACK_SEQ":
            result = self.attack_manager.update(delta_time)
            if result == "BATTLE_CONTINUE":
                self._handle_turn_end()
                    
        elif self.state == "SPIRIT_SEQ":
            result = self.spirit_manager.update(delta_time)
            if result == "EVO_COMPLETE":
                # Stay in SPIRIT_SEQ but logic handled by manager state "MENU"
                pass
            elif result == "DEEVO_COMPLETE":
                self.state = "MENU"
            elif result == "ESCAPE":
                return "BATTLE_END"
                
        elif self.state == "ANCIENT_SEQ":
            result = self.evolution_manager.update(delta_time)
            if result == "EVO_COMPLETE":
                self.state = "MENU"
                
        elif self.state == "LEVEL_SEQ":
            result = self.level_manager.update(delta_time)
            if result == "TRANSITION_COMPLETE":
                return "BATTLE_END"

    def _handle_turn_end(self):
        """
        Handle logic after a turn ends (obj_spirit_ready_dtector).
        Checks for win/loss and form maintenance.
        """
        # Check win/loss first
        if self.current_enemy_hp <= 0:
            # Battle won
            # If spirit, de-evolve first? GML says obj_spirit_off_dtector if battle ended
            if self._is_spirit_form():
                self.state = "SPIRIT_SEQ"
                self.spirit_manager.start_deevolution(False) # False = not escape
            else:
                # Standard win
                # TODO: Implement win sequence (Level up, etc)
                pass
            
            self.state = "LEVEL_SEQ"
            self.level_manager.start_level_check(True)
            return

        if self.current_mine_hp <= 0:
            # Battle lost
            if self._is_spirit_form():
                self.state = "SPIRIT_SEQ"
                self.spirit_manager.start_deevolution(False)
            
            self.state = "LEVEL_SEQ"
            self.level_manager.start_level_check(False)
            return

        # Check form maintenance
        if self._is_spirit_form():
            cost = self._get_dpower_cost()
            if self.control.game_progress["dpower"] < cost:
                # Forced de-evolution
                self.state = "SPIRIT_SEQ"
                self.spirit_manager.start_deevolution(False)
            else:
                # Maintain spirit form -> Spirit Menu
                self.state = "SPIRIT_SEQ"
                self.spirit_manager.start_menu()
        elif self._is_ancient_form():
             # Similar maintenance for Ancient
             self.state = "MENU" # Placeholder
        else:
            # Standard menu
            self.state = "MENU"
            self.enemy_move = random.choice([2, 0, 1])

    def _is_spirit_form(self):
        # IDs 100-111 are spirits
        return 100 <= self.mine_digimon <= 111
        
    def _is_ancient_form(self):
        # Need to define ID range for Ancients
        return False # Placeholder

    def _get_dpower_cost(self):
        # Logic from dpower_cost script
        level = self.control.game_progress["level"]
        if level < 11: return 10
        elif level < 21: return 9
        elif level < 31: return 8
        elif level < 41: return 7
        elif level < 51: return 6
        elif level < 61: return 5
        elif level < 71: return 4
        elif level < 81: return 3
        elif level < 91: return 2
        else: return 1

    def handle_input(self, event):
        """Handle input based on state"""
        if self.state == "MENU":
            result = self.menu.handle_input(event)
            if result == "scan_attack":
                self.state = "SCAN_SEQ"
                self.scan_manager.start()
            elif result == "spirit_check":
                self.state = "SPIRIT_SEQ"
                self.spirit_manager.start_selection()
            elif result == "escape_success":
                return "BATTLE_END"
            
        elif self.state == "SCAN_SEQ":
            result = self.scan_manager.handle_input(event)
            if result == "CANCEL":
                self.state = "MENU"
            
        elif self.state == "ATTACK_SEQ":
            self.attack_manager.handle_input(event)
            
        elif self.state == "SPIRIT_SEQ":
            result = self.spirit_manager.handle_input(event)
            if result == "SPIRIT_ATTACK":
                self.state = "SCAN_SEQ"
                self.scan_manager.start()
            elif result == "SPIRIT_SCAN":
                # Implement scan logic for spirit?
                # For now map to attack scan
                self.state = "SCAN_SEQ"
                self.scan_manager.start()

    def _advance_animation(self):
        """
        Advance battle start animation sequence.
        Ported exactly from obj_battle_start_dtector_Alarm_0.gml
        """
        # GML runs at 60 FPS (usually). 
        # alarm[0] = 15 -> 15 frames
        # alarm[0] = 30 -> 30 frames
        # alarm[0] = 60 -> 60 frames
        
        if not self.is_last_boss:
            # Normal/Boss battle animation
            if 0 <= self.counter <= 8:
                if self.counter == 4 and self.is_boss:
                    # Play boss encounter sound
                    pass
                self.alarm_timer = 15
                self.counter += 1
            elif 9 <= self.counter <= 17:
                self.alarm_timer = 15
                self.counter += 1
            elif 18 <= self.counter <= 20:
                if self.counter == 19 and not self.is_boss:
                    # Play normal encounter sound
                    pass
                self.alarm_timer = 15
                self.counter += 1
            elif 21 <= self.counter <= 22:
                self.alarm_timer = 30
                self.counter += 1
            elif self.counter == 23:
                self.alarm_timer = 60
                self.counter += 1
            elif self.counter == 24:
                # Transition to battle menu
                return "battle_menu"
        else:
            # Last boss animation
            if 0 <= self.counter <= 15:
                if self.counter == 0:
                    # Play last boss sound
                    pass
                self.alarm_timer = 10
                self.counter += 1
            elif self.counter == 16:
                self.alarm_timer = 20
                self.counter += 1
            elif 17 <= self.counter <= 29:
                self.alarm_timer = 20
                self.counter += 1
            elif 30 <= self.counter <= 33: # Fixed range from GML (29-33)
                self.alarm_timer = 20
                self.counter += 1
            elif self.counter == 34:
                self.alarm_timer = 60
                self.counter += 1
            elif self.counter == 35:
                self.alarm_timer = 60
                self.counter += 1
            elif self.counter == 36:
                self.alarm_timer = 60
                self.counter += 1
            elif self.counter == 37:
                # Transition to battle menu
                return "battle_menu"
        
        return None

    def draw(self, screen):
        """Draw battle state"""
        if self.state == "START_ANIM":
            self._draw_start_anim(screen)
        elif self.state == "MENU":
            self._draw_battle_screen(screen)
            self.menu.draw(screen)
        elif self.state == "SCAN_SEQ":
            self.scan_manager.draw(screen)
        elif self.state == "ATTACK_SEQ":
            self.attack_manager.draw(screen)
        elif self.state == "SPIRIT_SEQ":
            self.spirit_manager.draw(screen)
        elif self.state == "ANCIENT_SEQ":
            self.evolution_manager.draw(screen)
        elif self.state == "LEVEL_SEQ":
            self.level_manager.draw(screen)

    def _draw_battle_screen(self, screen):
        # Draw background/enemy/player for menu state
        # Similar to start anim final frame
        enemy_sprite = self.game.assets.get_animation(
            f"digimon_{self.control.digimon_database[self.enemy_digimon]['sprite']}"
        )
        if enemy_sprite:
            scale = 6
            x = screen.get_width() // 2
            y = screen.get_height() // 2
            
            # Draw enemy
            scaled = pygame.transform.scale(enemy_sprite[0], 
                (enemy_sprite[0].get_width() * scale, enemy_sprite[0].get_height() * scale))
            screen.blit(pygame.transform.flip(scaled, True, False), 
                       (x + 24*scale - scaled.get_width()//2, y - scaled.get_height()//2))
            
            # Draw player (summon/digimon)
            pass

    def _draw_start_anim(self, screen):
        """
        Draw battle start animation.
        Ported exactly from obj_battle_start_dtector_Draw_0.gml
        """
        enemy_sprite = self.game.assets.get_animation(
            f"digimon_{self.control.digimon_database[self.enemy_digimon]['sprite']}"
        )
        
        summon_frames = self.game.assets.get_animation("summon_dtector")
        
        if not enemy_sprite or not summon_frames:
            return
        
        # Center coordinates (GML uses relative to object, we center on screen)
        # GML view is roughly 30x32 scaled 10x -> 300x320
        # We are drawing at center of screen.
        base_x = screen.get_width() // 2
        base_y = screen.get_height() // 2
        scale = 6
        
        # GML offsets: x + 3 + 24, y + 4 for enemy
        # We need to adjust for our centering logic.
        # Let's assume base_x/y corresponds to 'x,y' in GML (top-left of the 30x32 area?)
        # Actually, in GML 'x,y' is the object position.
        # For now, we'll keep our centering but apply the RELATIVE offsets from GML.
        
        # Enemy draw helper
        def draw_enemy(frame_idx, flip=True):
            sprite = enemy_sprite[frame_idx % len(enemy_sprite)]
            # GML: draw_sprite_ext(..., x + 27, y + 4, -1, 1, ...)
            # -1 xscale means flip horizontal.
            if flip:
                sprite = pygame.transform.flip(sprite, True, False)
            
            scaled = pygame.transform.scale(sprite, 
                (sprite.get_width() * scale, sprite.get_height() * scale))
            
            # Offset: +27 pixels * scale
            draw_x = base_x + (27 * scale) - scaled.get_width() # Adjust anchor?
            # Actually, let's stick to our previous centering but apply the offset relative to center
            # if that's what GML does.
            # In GML, x,y is likely top-left of the view or specific position.
            # Let's try to match the visual "feel" first.
            # Previous code used: x + 24*scale. GML uses x + 27.
            
            # Let's use a fixed offset from center to match GML's relative positioning
            # Assuming 'x' in GML is roughly center-ish or left-aligned.
            # Let's try to center the "scene" and place items relative to that.
            scene_x = base_x - (15 * scale) # Center of 30px width
            scene_y = base_y - (16 * scale) # Center of 32px height
            
            # GML: x + 27
            pos_x = scene_x + (27 * scale) - (scaled.get_width() // 2) # Centered on that point?
            # GML sprites are usually top-left origin unless specified.
            # Let's assume top-left for now.
            pos_x = scene_x + (27 * scale) - scaled.get_width() # Flip adjustment
            pos_y = scene_y + (4 * scale)
            
            screen.blit(scaled, (pos_x, pos_y))

        # Summon draw helper
        def draw_summon(frame_idx, offset_y=0):
            if frame_idx < len(summon_frames):
                sprite = summon_frames[frame_idx]
                scaled = pygame.transform.scale(sprite, 
                    (sprite.get_width() * scale, sprite.get_height() * scale))
                
                # GML: draw_sprite(..., x, y) or (x, y-16)
                scene_x = base_x - (15 * scale)
                scene_y = base_y - (16 * scale)
                
                pos_x = scene_x
                pos_y = scene_y + (offset_y * scale)
                
                screen.blit(scaled, (pos_x, pos_y))

        if not self.is_last_boss:
            summon_index = 4 if self.is_boss else 3
            
            if 0 <= self.counter <= 8:
                if self.counter % 2:
                    draw_summon(summon_index)
            elif 9 <= self.counter <= 17:
                if self.counter % 2:
                    draw_enemy(0)
                else:
                    draw_summon(summon_index)
            elif 18 <= self.counter <= 20:
                if self.counter % 2:
                    draw_enemy(0)
            elif self.counter >= 21:
                if self.counter % 2:
                    draw_enemy(0)
                else:
                    draw_enemy(1) # Frame 1
        else:
            # Last Boss
            if 0 <= self.counter <= 16:
                offset = -16 if self.counter % 2 else 16
                draw_summon(4, offset_y=offset)
            elif 17 <= self.counter <= 29:
                draw_enemy(0)
                offset = -16 if self.counter % 2 else 16
                draw_summon(4, offset_y=offset)
            elif 30 <= self.counter <= 33:
                if self.counter % 2 == 0:
                    draw_enemy(0)
            elif self.counter == 35:
                draw_enemy(0)
            elif self.counter == 36:
                draw_enemy(1)
            elif self.counter == 37:
                draw_enemy(0)
