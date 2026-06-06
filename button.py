import pygame.font

class Button:
    """A class to build buttons for the game."""
    def __init__(self, ai_game, msg, position=None, is_disabled=False, width=250, height=60):
        """Initialize button attributes."""
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        # Set the dimensions and properties of the button.
        self.width, self.height = width, height
        self.button_color = (0, 100, 0) # Muted green
        self.hover_color = (0, 135, 0)
        self.text_color = (255, 255, 255)
        self.disabled_button_color = (50, 50, 50)
        self.disabled_text_color = (200, 200, 200)
        self.font = pygame.font.SysFont(None, 48)
        self.is_disabled = is_disabled
        self.msg = msg
        
        # Build the button's rect object and set its position.
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        if position:
            self.rect.center = position
        else:
            self.rect.center = self.screen_rect.center
            
        # The button message needs to be prepped.
        self._prep_msg(msg)
        
    def _prep_msg(self, msg, text_color=None):
        """Turn msg into a rendered image and center text on the button."""
        if not text_color:
            text_color = self.disabled_text_color if self.is_disabled else self.text_color
            
        self.msg_image = self.font.render(msg, True, text_color, None)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def set_message(self, msg):
        """Set the button's message and re-prep it."""
        self.msg = msg
        self._prep_msg(msg)
        
    def draw_button(self):
        """Draw blank button and then draw message."""
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        if self.is_disabled:
            button_color = self.disabled_button_color
            self._prep_msg(self.msg, self.disabled_text_color)
        elif is_hovered:
            button_color = self.hover_color
        else:
            button_color = self.button_color
            
        self.screen.fill(button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)
