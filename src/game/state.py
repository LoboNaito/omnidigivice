import json
from datetime import datetime

class GameState:
    def __init__(self):
        self.default_colors = [
            [14408667, 2500134, 2565288], 
            [14408667, 16775667, 6039324], 
            [14408667, 9128478, 3125989], 
            [13691844, 12616357, 16045548], 
            [14408667, 15589559, 814640], 
            [14408667, 1907997, 6908265]
        ]
        
        self.config = {
            "start_game": True,
            "enable_logs": False,
            "debug": False,
            "enable_touch": True,
            "enable_shake": True,
            "scan": False,
            "sound_enabled": True,
            "shake_sound": False,
            "grid_enabled": True,
            "autorun": False,
            "resolution": 0,
            "colors": self.default_colors
        }
        
        self.game_progress = {
            "distance": 6000,
            "steps": 0,
            "dpower": 99,
            "battles": 0,
            "wins": 0,
            "current_char": 0,
            "level": 1,
            "next_level_up": 5,
            "next_level_down": 5,
            "docks": [0, -1, -1, -1],
            "new_game": False,
            "current_area": 0,
            "area_status": [False] * 13,
            "defeat": False,
            "battle_start": False,
            "event_start": False,
            "last_encounter_is_battle": False,
            "finish_battle_event": False,
            "last_boss_unlocked": False,
            "current_char_digimon": 0, # Default to first digimon (Agumon)
            "current_char_hp": 100     # Default HP
        }
        
        self.area_distance = [6000, 8000, 7000, 9000, 10000, 11000, 9000, 7000, 10000, 11000, 10000, 10000, 12000]
        
        self.char_stats = [
            {"hp": 6, "spirit": 5, "stamina": 5, "skill": 7, "name": "takuya"},
            {"hp": 6, "spirit": 7, "stamina": 5, "skill": 5, "name": "koji"},
            {"hp": 8, "spirit": 4, "stamina": 8, "skill": 5, "name": "jp"},
            {"hp": 5, "spirit": 5, "stamina": 4, "skill": 7, "name": "zoe"},
            {"hp": 5, "spirit": 7, "stamina": 5, "skill": 4, "name": "tommy"},
            {"hp": 6, "spirit": 5, "stamina": 5, "skill": 7, "name": "koichi"}
        ]
        
        self.spirits_unlocked = [False] * 12
        self.spirits_obtained = [False] * 12
        self.char_unlocked = [True, True, True, True, True, False]
        self.char_party = [True, True, True, True, True, False]
        
        # Simplified Digimon Database (Porting a few examples)
        # Simplified Digimon Database (Porting a few examples)
        self.digimon_database = []
        
        # Fill with placeholders first
        for i in range(200):
            self.digimon_database.append({
                "number": i, "name": f"digimon_{i}", "level": 1, "hp": 100, "element": 0, 
                "energy": 10, "crunch": 10, "ability": 10, "code": "00000", 
                "type": "rookie", "evolution": -1, "unlock": False, "sprite": "agumon" # Default sprite
            })
            
        # Update specific entries
        self.digimon_database[8] = {
            "number": 8, "name": "agumon", "level": 4, "hp": 40, "element": 0, 
            "energy": 25, "crunch": 15, "ability": 20, "code": "VSJK1", 
            "type": "rookie", "evolution": 17, "unlock": False, "sprite": "agumon"
        }
        self.digimon_database[9] = {
            "number": 9, "name": "gabumon", "level": 4, "hp": 40, "element": 4, 
            "energy": 20, "crunch": 25, "ability": 15, "code": "20LJY", 
            "type": "rookie", "evolution": 18, "unlock": False, "sprite": "gabumon"
        }
        self.digimon_database[32] = { # Fallback enemy
             "number": 32, "name": "candlemon", "level": 5, "hp": 50, "element": 2,
             "energy": 15, "crunch": 15, "ability": 15, "code": "xxxxx",
             "type": "champion", "evolution": -1, "unlock": False, "sprite": "agumon" # Placeholder sprite
        }

        # Ensure list is long enough for 234
        while len(self.digimon_database) <= 234:
             self.digimon_database.append(self.digimon_database[0].copy())
             
        self.digimon_database[234] = {
            "number": 234, "name": "veemon", "level": 4, "hp": 40, "element": 2, 
            "energy": 10, "crunch": 30, "ability": 20, "code": "4143F", 
            "type": "rookie", "evolution": 19, "unlock": False, "sprite": "veemon"
        }

    def to_dict(self):
        return {
            "config": self.config,
            "game_progress": self.game_progress,
            "char_stats": self.char_stats,
            "spirits_unlocked": self.spirits_unlocked,
            "spirits_obtained": self.spirits_obtained,
            "char_unlocked": self.char_unlocked,
            "char_party": self.char_party
        }

    def from_dict(self, data):
        if "config" in data: self.config = data["config"]
        if "game_progress" in data: self.game_progress = data["game_progress"]
        if "char_stats" in data: self.char_stats = data["char_stats"]
        if "spirits_unlocked" in data: self.spirits_unlocked = data["spirits_unlocked"]
        if "spirits_obtained" in data: self.spirits_obtained = data["spirits_obtained"]
        if "char_unlocked" in data: self.char_unlocked = data["char_unlocked"]
        if "char_party" in data: self.char_party = data["char_party"]
