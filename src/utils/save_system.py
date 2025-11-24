import json
import os
from src.game.state import GameState

class SaveSystem:
    SAVE_FILE = "dtector_eu.dat"
    KEY = "D1g1W0rld_S4v3_K3y_2025"
    
    @staticmethod
    def encrypt_value(value_str):
        key_length = len(SaveSystem.KEY)
        str_length = len(value_str)
        
        if str_length == 0:
            return ""
            
        result = []
        for i in range(str_length):
            char_code = ord(value_str[i])
            key_char_code = ord(SaveSystem.KEY[i % key_length])
            encrypted_char = char_code ^ key_char_code
            result.append(str(encrypted_char))
            
        return "-".join(result)

    @staticmethod
    def decrypt_value(encrypted_str):
        if not encrypted_str:
            return ""
            
        parts = encrypted_str.split("-")
        key_length = len(SaveSystem.KEY)
        result = []
        
        for i, part in enumerate(parts):
            try:
                char_code = int(part)
                key_char_code = ord(SaveSystem.KEY[i % key_length])
                decrypted_char = char_code ^ key_char_code
                result.append(chr(decrypted_char))
            except ValueError:
                continue
                
        return "".join(result)

    @staticmethod
    def save_game(state: GameState):
        data = state.to_dict()
        # In the original GML, individual fields are encrypted.
        # For this port, we can replicate that or just encrypt the whole JSON.
        # Replicating GML behavior:
        
        encrypted_data = {}
        for key, value in data.items():
            json_str = json.dumps(value)
            encrypted_data[key] = SaveSystem.encrypt_value(json_str)
            
        with open(SaveSystem.SAVE_FILE, "w") as f:
            json.dump(encrypted_data, f)
            
    @staticmethod
    def load_game(state: GameState):
        if not os.path.exists(SaveSystem.SAVE_FILE):
            return False
            
        try:
            with open(SaveSystem.SAVE_FILE, "r") as f:
                encrypted_data = json.load(f)
                
            decrypted_data = {}
            for key, value in encrypted_data.items():
                decrypted_str = SaveSystem.decrypt_value(value)
                decrypted_data[key] = json.loads(decrypted_str)
                
            state.from_dict(decrypted_data)
            return True
        except Exception as e:
            print(f"Failed to load save: {e}")
            return False
