from src.game.state import GameState

class CharacterManager:
    def __init__(self, state: GameState):
        self.state = state

    def calculate_spirit_stats(self):
        """
        Updates the Digimon database stats based on the human character stats.
        Ported from gml_GlobalScript_fun_calculate_spirit_stats_dtector.gml
        """
        db = self.state.digimon_database
        stats = self.state.char_stats
        
        # Helper to safely get/set digimon stats if they exist
        # In the full game, we'd ensure all IDs exist. For now, we check.
        def update_spirit(spirit_id, char_idx, hp_add, spirit_add, stamina_add, skill_add):
            # Find the digimon with the given number/ID
            # Note: GML used array indices [100], [101] etc. 
            # We need to map these to our list or use a dictionary for faster lookup.
            # For now, let's assume we might not have them all populated.
            pass 

        # Since we haven't fully populated the DB, I'll implement the logic structure
        # but comment it out or make it safe until we have the full DB.
        # The GML code modifies specific indices of digimon_database.
        # We need to ensure our digimon_database is large enough or use a dict keyed by ID.
        
        # Example implementation for Takuya (Index 0) -> Agunimon (ID 100 approx?)
        # The GML uses hardcoded indices like 100, 101. We need to know what those map to.
        # Assuming 100 is Agunimon, 101 is BurningGreymon, etc.
        
        # For this port, we will implement a simplified version that updates
        # the current active spirit if applicable.
        pass

    def get_current_character_name(self):
        idx = self.state.game_progress["current_char"]
        if 0 <= idx < len(self.state.char_stats):
            return self.state.char_stats[idx]["name"]
        return "Unknown"

    def get_current_character_stats(self):
        idx = self.state.game_progress["current_char"]
        if 0 <= idx < len(self.state.char_stats):
            return self.state.char_stats[idx]
        return None
