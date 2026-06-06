import db

class GameStats:
    """Track statistics for Alien Invasion."""
    def __init__(self, ai_game, loaded_stats=None):
        """Initialize statistics."""
        self.settings = ai_game.settings
        if loaded_stats:
            self.load_stats(loaded_stats)
        else:
            self.reset_stats()
        # High score should never be reset.
        self.high_score = db.get_highscore()
        self.game_over = False

    def load_stats(self, loaded_stats):
        """Load stats from a dictionary."""
        self.level = loaded_stats['level']
        self.score = loaded_stats['score']
        self.ships_left = loaded_stats['lives']
        
    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1