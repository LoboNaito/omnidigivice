import pygame
import random
import math

class AttackManager:
    """
    Manages the attack sequence, collision, and damage resolution.
    Ports logic from:
    - obj_attack_dtector
    - obj_collision_dtector
    - obj_hit_dtector
    """
    def __init__(self, game, battle_manager):
        self.game = game
        self.battle = battle_manager
        self.active = False
        
        # State
        self.phase = "IDLE" # IDLE, ATTACK_ANIM, PROJECTILE, COLLISION, HIT, END
        self.timer = 0
        self.counter = 0
        
        # Combat Data
        self.mine_move = 0
        self.enemy_move = 0
        self.move_position = 0
        self.is_your_digimon_hit = False # Who takes damage
        self.is_draw = False
        
        # Animation
        self.anim_stage = 0
        self.collision_sound_played = False
        self.damage_numbers = []
        
    def start_scan(self):
        """Start the scan phase (called from BattleManager)"""
        # This is actually handled by ScanManager now, but BattleManager calls this
        # to initiate the sequence.
        # BattleManager transitions to SCAN_SEQ, then calls start_attack with result.
        pass

    def start_attack(self, scan_pattern):
        """Start the attack sequence with the scanned pattern"""
        self.active = True
        self.phase = "ATTACK_ANIM"
        self.anim_stage = 0
        self.timer = 15
        self.move_position = 0
        self.collision_sound_played = False
        
        # Determine Player Move
        # [1, 0, 1] -> 1
        # [1, 1, 0] -> 2
        # [1, 1, 1] -> 0
        # [1, 0, 0] -> 1
        # Default -> Random(0, 2, 1)
        
        self.mine_move = random.choice([0, 2, 1])
        
        if scan_pattern == [1, 0, 1]: self.mine_move = 1
        elif scan_pattern == [1, 1, 0]: self.mine_move = 2
        elif scan_pattern == [1, 1, 1]: self.mine_move = 0
        elif scan_pattern == [1, 0, 0]: self.mine_move = 1
        
        # Level difference check
        mine_level = self.game.state.game_progress["level"]
        # Enemy level isn't directly stored, but we can infer or ignore for now.
        # GML: if ((digimon_level - mine_level) > 19) move = -1;
        # digimon_level is global.control_level (enemy level?)
        enemy_data = self.game.state.digimon_database[self.battle.enemy_digimon]
        enemy_level = enemy_data["level"]
        
        if (enemy_level - mine_level) > 19:
            self.mine_move = -1
            
        # Determine Enemy Move (AI)
        # GML: global.enemy_move = filter_enemy_attack_dtector(global.enemy_move);
        # For now use random choice set in BattleManager or here
        self.enemy_move = random.choice([0, 2, 1])
        
        # Play launch sound
        # audio_play_sound(sound_launch_attack, 0, false);
        pass

    def update(self, delta_time):
        # Update damage numbers independent of active state (so they float up even if battle ends/continues)
        self.damage_numbers = [dn for dn in self.damage_numbers if dn.update(delta_time)]

        if not self.active:
            return None
            
        if self.timer > 0:
            self.timer -= delta_time * 60
            
        if self.phase == "ATTACK_ANIM":
            if self.timer <= 0:
                self.anim_stage += 1
                if self.anim_stage == 1:
                    self.timer = 30
                elif self.anim_stage == 2:
                    self.timer = 3
                    # Play sound
                elif self.anim_stage >= 3:
                    self.phase = "PROJECTILE"
                    self.timer = 3
                    self.move_position = 0
                    
        elif self.phase == "PROJECTILE":
            if self.timer <= 0:
                self.timer = 3
                # Move projectiles
                # GML: if is_your_digimon move_pos-- else move_pos++
                # But here we simulate both at once?
                # obj_attack_dtector logic handles ONE side.
                # But obj_collision_dtector handles the clash.
                # Let's simulate the convergence.
                self.move_position += 1
                
                if self.move_position >= 32:
                    self.phase = "COLLISION"
                    self.move_position = 0
                    self.timer = 3
                    # Play collision sound
                    
        elif self.phase == "COLLISION":
            if self.timer <= 0:
                self.timer = 3
                self.move_position += 1
                
                # Check resolution at specific frames
                if self.move_position == 30:
                    self._resolve_combat_step_1()
                elif self.move_position == 60:
                    result = self._resolve_combat_final()
                    if result == "HIT":
                        self.phase = "HIT"
                        self.timer = 60 # Long wait for hit anim
                        self.anim_stage = 0
                    elif result == "DRAW":
                        self.active = False
                        return "BATTLE_CONTINUE"
                        
        elif self.phase == "HIT":
            # Hit animation sequence
            # GML: anim 0->1->2->3->4(damage)->5(end)
            if self.timer <= 0:
                self.anim_stage += 1
                if self.anim_stage == 4:
                    self._apply_damage()
                    self.timer = 60
                elif self.anim_stage == 5:
                    self.active = False
                    return "BATTLE_CONTINUE"
                else:
                    self.timer = 30 # Default step
                    
        return None

    def _resolve_combat_step_1(self):
        # Check for Draw condition
        # If stats equal and same move type -> Draw
        pass

    def _resolve_combat_final(self):
        # Determine winner
        # Returns "HIT" or "DRAW"
        
        mine_stats = self._get_stats(True)
        enemy_stats = self._get_stats(False)
        
        mine_val = 0
        enemy_val = 0
        
        # Get relevant stat based on move
        if self.mine_move == 0: mine_val = mine_stats["energy"]
        elif self.mine_move == 1: mine_val = mine_stats["crunch"]
        elif self.mine_move == 2: mine_val = mine_stats["ability"]
        
        if self.enemy_move == 0: enemy_val = enemy_stats["energy"]
        elif self.enemy_move == 1: enemy_val = enemy_stats["crunch"]
        elif self.enemy_move == 2: enemy_val = enemy_stats["ability"]
        
        # Rock Paper Scissors
        # 2 > 1 > 0 > 2
        
        if self.mine_move == -1:
            self.is_your_digimon_hit = True
            return "HIT"
            
        if self.mine_move == self.enemy_move:
            if mine_val == enemy_val:
                return "DRAW"
            elif mine_val > enemy_val:
                self.is_your_digimon_hit = False
                return "HIT"
            else:
                self.is_your_digimon_hit = True
                return "HIT"
        
        # Different moves
        if (self.mine_move == 2 and self.enemy_move == 1) or \
           (self.mine_move == 1 and self.enemy_move == 0) or \
           (self.mine_move == 0 and self.enemy_move == 2):
            self.is_your_digimon_hit = False
            return "HIT"
        else:
            self.is_your_digimon_hit = True
            return "HIT"

    def _apply_damage(self):
        mine_stats = self._get_stats(True)
        enemy_stats = self._get_stats(False)
        
        damage = 0
        if self.is_your_digimon_hit:
            # Enemy hitting Player
            if self.enemy_move == 0: damage = enemy_stats["energy"]
            elif self.enemy_move == 1: damage = enemy_stats["crunch"]
            elif self.enemy_move == 2: damage = enemy_stats["ability"]
            
            # Special logic (Ancient/Boss) would go here
            
            self.battle.current_mine_hp = max(0, self.battle.current_mine_hp - damage)
            # Update global HP
            self.game.state.game_progress["current_char_hp"] = self.battle.current_mine_hp
            
            # Spawn Damage Number (Player Side)
            cx = self.game.screen.get_width() // 2 - 50
            cy = self.game.screen.get_height() // 2
            self.damage_numbers.append(DamageNumber(damage, cx, cy))
            
        else:
            # Player hitting Enemy
            if self.mine_move == 0: damage = mine_stats["energy"]
            elif self.mine_move == 1: damage = mine_stats["crunch"]
            elif self.mine_move == 2: damage = mine_stats["ability"]
            
            self.battle.current_enemy_hp = max(0, self.battle.current_enemy_hp - damage)
            
            # Spawn Damage Number (Enemy Side)
            cx = self.game.screen.get_width() // 2 + 50
            cy = self.game.screen.get_height() // 2
            self.damage_numbers.append(DamageNumber(damage, cx, cy))

    def _get_stats(self, is_player):
        if is_player:
            digimon = self.game.state.digimon_database[self.battle.mine_digimon]
            # Add buffs
            return {
                "energy": digimon["energy"] + 0, # TODO: Add global.increase_energy
                "crunch": digimon["crunch"] + 0,
                "ability": digimon["ability"] + 0
            }
        else:
            digimon = self.game.state.digimon_database[self.battle.enemy_digimon]
            return {
                "energy": digimon["energy"],
                "crunch": digimon["crunch"],
                "ability": digimon["ability"]
            }

    def handle_input(self, event):
        pass # No input during attack sequence

    def draw(self, screen):
        if not self.active: return
        
        scale = 6
        # Center coordinates
        base_x = screen.get_width() // 2
        base_y = screen.get_height() // 2
        
        # GML offsets relative to "x, y".
        # Let's define a scene center similar to BattleManager.
        scene_x = base_x - (15 * scale)
        scene_y = base_y - (16 * scale)
        
        # Helper to draw sprite
        def draw_sprite(sprite, x_offset, y_offset, flip=False, alpha=255):
            if flip: sprite = pygame.transform.flip(sprite, True, False)
            scaled = pygame.transform.scale(sprite, 
                (sprite.get_width() * scale, sprite.get_height() * scale))
            
            pos_x = scene_x + (x_offset * scale)
            pos_y = scene_y + (y_offset * scale)
            
            # Adjust for centering if needed, but GML uses top-left usually.
            # If we assume sprite origin is top-left.
            
            screen.blit(scaled, (pos_x, pos_y))

        # Get Sprites
        mine_anim = self.game.assets.get_animation(f"digimon_{self.game.state.digimon_database[self.battle.mine_digimon]['sprite']}")
        enemy_anim = self.game.assets.get_animation(f"digimon_{self.game.state.digimon_database[self.battle.enemy_digimon]['sprite']}")
        
        energy_anim = self.game.assets.get_animation("energy_dtector")
        collision_anim = self.game.assets.get_animation("collision_dtector")
        
        if not mine_anim or not enemy_anim: return

        # --- Draw Logic based on Phase and Animation Stage ---
        
        # Determine current animation frame for Digimon
        # GML: current_animation 0 (Idle), 1 (Prep), 2 (Fire)
        
        # Player Draw
        if self.phase == "ATTACK_ANIM":
            if self.anim_stage == 0:
                draw_sprite(mine_anim[0], 3, 4)
            elif self.anim_stage == 1:
                # Frame 0 but maybe offset? GML: if move==-1 draw normal, else draw frame 0 at x+3+4?
                if self.mine_move == -1:
                     draw_sprite(mine_anim[0], 3 + 24, 4) # Wait, this is enemy pos?
                     # Logic check:
                     # if is_your_digimon:
                     #   if move == -1: draw at x+3+24 (Enemy side? No, maybe retreat?)
                     #   else: draw at x+3+4 (Forward)
                     draw_sprite(mine_anim[0], 3 + 4, 4)
                else:
                    draw_sprite(mine_anim[0], 3 + 4, 4)
            elif self.anim_stage >= 2:
                # Attack Frame
                if self.mine_move == 0: # Energy
                    # Draw Energy Ball
                    # fun_calculate_energy_dtector logic: returns index based on energy value.
                    # For now use frame 0.
                    if energy_anim:
                        draw_sprite(energy_anim[0], 3 + 4 + self.move_position, 4)
                    draw_sprite(mine_anim[1], 3 + 4, 4)
                elif self.mine_move == 2: # Ability
                    draw_sprite(mine_anim[3], 3 + 4 + self.move_position, 4)
                    draw_sprite(mine_anim[1], 3 + 4, 4)
                elif self.mine_move == 1: # Crunch
                    draw_sprite(mine_anim[2], 3 + 4, 4)
                    # Trail effect
                    for pos in range(0, int(self.move_position * 4) + 1, 4):
                         draw_sprite(mine_anim[2], 3 + 4 + pos, 4)

        elif self.phase == "PROJECTILE" or self.phase == "COLLISION":
             # Similar to anim_stage 2 but moving
             # Player
             if self.mine_move == 0:
                 if energy_anim:
                     draw_sprite(energy_anim[0], 3 + 4 + self.move_position, 4)
                 draw_sprite(mine_anim[1], 3 + 4, 4)
             elif self.mine_move == 2:
                 draw_sprite(mine_anim[3], 3 + 4 + self.move_position, 4)
                 draw_sprite(mine_anim[1], 3 + 4, 4)
             elif self.mine_move == 1:
                 draw_sprite(mine_anim[2], 3 + 4, 4)
                 # Trail logic simplified
                 draw_sprite(mine_anim[2], 3 + 4 + self.move_position, 4)

        # Enemy Draw (Mirrored logic)
        # Enemy base x is x + 3 + 24 (27)
        # Flip sprites
        
        if self.phase == "ATTACK_ANIM":
            if self.anim_stage == 0:
                draw_sprite(enemy_anim[0], 27, 4, True)
            elif self.anim_stage == 1:
                 draw_sprite(enemy_anim[0], 27 - 4, 4, True)
            elif self.anim_stage >= 2:
                if self.enemy_move == 0:
                    if energy_anim:
                        draw_sprite(energy_anim[0], 27 - 4 - self.move_position, 4, True)
                    draw_sprite(enemy_anim[1], 27 - 4, 4, True)
                elif self.enemy_move == 2:
                    draw_sprite(enemy_anim[3], 27 - 4 - self.move_position, 4, True)
                    draw_sprite(enemy_anim[1], 27 - 4, 4, True)
                elif self.enemy_move == 1:
                    draw_sprite(enemy_anim[2], 27 - 4, 4, True)
                    draw_sprite(enemy_anim[2], 27 - 4 - self.move_position, 4, True)

        elif self.phase == "PROJECTILE" or self.phase == "COLLISION":
             if self.enemy_move == 0:
                 if energy_anim:
                     draw_sprite(energy_anim[0], 27 - 4 - self.move_position, 4, True)
                 draw_sprite(enemy_anim[1], 27 - 4, 4, True)
             elif self.enemy_move == 2:
                 draw_sprite(enemy_anim[3], 27 - 4 - self.move_position, 4, True)
                 draw_sprite(enemy_anim[1], 27 - 4, 4, True)
             elif self.enemy_move == 1:
                 draw_sprite(enemy_anim[2], 27 - 4, 4, True)
                 draw_sprite(enemy_anim[2], 27 - 4 - self.move_position, 4, True)

        # Collision Effect
        if self.phase == "COLLISION":
            if self.move_position >= 15 and self.move_position <= 16:
                # Draw collision spark
                if collision_anim:
                    draw_sprite(collision_anim[0], 15, 8) # Center-ish?
                    
        # Hit Effect
        if self.phase == "HIT":
            # Draw hit animation (Flash the hit digimon)
            if self.timer % 10 < 5: # Blink effect
                if self.is_your_digimon_hit:
                    # Player hit - draw Player normally? Or skip to blink?
                    # Skip drawing player to blink
                    pass
                else:
                    # Enemy hit - skip drawing enemy
                    pass
            else:
                # Draw normally (already drawn above? No, we need to redraw or rely on above)
                # The above draw logic depends on phase.
                # We need to ensure the sprites are drawn in HIT phase too.
                pass
                
        # We need to consolidate the draw calls.
        # The above logic handles ATTACK_ANIM, PROJECTILE, COLLISION.
        # HIT phase needs to draw the digimon too.
        
        if self.phase == "HIT":
             # Draw Player
            if not (self.is_your_digimon_hit and self.timer % 10 < 5):
                draw_sprite(mine_anim[0], 3 + 4, 4) # Return to idle/stand
            
            # Draw Enemy
            if not (not self.is_your_digimon_hit and self.timer % 10 < 5):
                draw_sprite(enemy_anim[0], 27 - 4, 4, True) # Return to idle/stand

        # Draw Damage Numbers
        for dn in self.damage_numbers:
            # dn.x, dn.y are relative to screen center or absolute?
            # Let's make them absolute for simplicity in draw_number
            self.game.text_renderer.draw_number(screen, dn.value, dn.x, dn.y, scale=scale)

class DamageNumber:
    def __init__(self, value, x, y):
        self.value = value
        self.x = x
        self.y = y
        self.timer = 60 # 1 second duration
        self.vy = -1 # Float up speed
        
    def update(self, delta_time):
        self.timer -= delta_time * 60
        self.y += self.vy * (delta_time * 60)
        return self.timer > 0
