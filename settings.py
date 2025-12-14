import pygame.font

class Settings:
    """A class to store all settings for Alien Invasion"""
    def __init__(self):
        """Initialize the game's static settings."""
        #Screen Settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (0, 0, 0)
        
        #Ship settings
        self.ship_limit = 3
        self.ship_width = 50
        self.ship_height = 50
        
        # Bullet settings
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (230, 230, 230)
        self.bullets_allowed = 100
        
        # Alien settings
        self.alien_width = 50
        self.alien_height = 50
        self.alien_bullet_speed = 1.0
        self.alien_bullet_color = (255, 0, 0)
        self.alien_fire_rate = 100
        self.fleet_drop_speed = 10  
        # fleet_direction of 1 represents right; -1 represents left.
        
        # How quickly the alien point values increase
        self.score_scale = 1.5
        
        # Title Screen Settings
        self.title_text = "Alien Invasion"
        self.title_font_size = 72
        self.title_font = pygame.font.SysFont(None, self.title_font_size)
        self.title_color = (230, 230, 230)
        
        self.instructions_text = "Use Arrow Keys to Move, Spacebar to Fire"
        self.instructions_font_size = 36
        self.instructions_font = pygame.font.SysFont(None, self.instructions_font_size)
        self.instructions_color = (230, 230, 230)

        self.game_over_text = "Game Over"
        self.game_over_font_size = 72
        self.game_over_font = pygame.font.SysFont(None, self.game_over_font_size)
        self.game_over_color = (230, 230, 230)

        # Difficulty levels
        self.easy_settings = {
            'ship_speed': 1.5, 'bullet_speed': 2.5, 'alien_speed': 1.0, 
            'alien_points': 50, 'speedup_scale': 1.1
        }
        self.medium_settings = {
            'ship_speed': 2.0, 'bullet_speed': 3.0, 'alien_speed': 1.5, 
            'alien_points': 100, 'speedup_scale': 1.2
        }
        self.hard_settings = {
            'ship_speed': 2.5, 'bullet_speed': 3.5, 'alien_speed': 2.0, 
            'alien_points': 150, 'speedup_scale': 1.3
        }

        self.set_difficulty('medium') # Default difficulty
        self.initialize_dynamic_settings()

    def set_difficulty(self, level):
        """Set the difficulty level for the game."""
        if level == 'easy':
            self.current_difficulty_settings = self.easy_settings
        elif level == 'hard':
            self.current_difficulty_settings = self.hard_settings
        else: # medium
            self.current_difficulty_settings = self.medium_settings
    
    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = self.current_difficulty_settings['ship_speed']
        self.bullet_speed = self.current_difficulty_settings['bullet_speed']
        self.alien_speed = self.current_difficulty_settings['alien_speed']
        self.speedup_scale = self.current_difficulty_settings['speedup_scale']
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1
        # Scoring settings
        self.alien_points = self.current_difficulty_settings['alien_points']
        
    def increase_speed(self):
        """Increase speed settings and alien point values."""
        if self.ship_speed < 5.0:
            self.ship_speed *= self.speedup_scale
        if self.bullet_speed < 6.0:
            self.bullet_speed *= self.speedup_scale
        if self.alien_speed < 3.0:
            self.alien_speed *= self.speedup_scale
        if self.alien_points < 1000:
            self.alien_points = int(self.alien_points * self.score_scale)
        
    