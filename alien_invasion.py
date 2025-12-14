import sys 
from time import sleep
import pygame
import random
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from alien_bullet import AlienBullet
from powerup import Powerup


class AlienEnvasion:
    """Overall class to manage game assets and behavior"""
    
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
        
        # Create an instance to store game statistics,
        #and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self._create_fleet()
        self.bg_color = (0, 0, 0)
        # Start Alien Invasion in an active state.
        self.game_active = False
        
        # Make the difficulty buttons.
        center_x = self.screen.get_rect().centerx
        center_y = self.screen.get_rect().centery
        self.play_button = Button(self, "Play", (center_x, center_y))
        self.easy_button = Button(self, "Easy", (center_x - 250, center_y))
        self.hard_button = Button(self, "Hard", (center_x + 250, center_y))


    def _create_fleet(self):
        """Create the fleet of aliens"""
        # Create an alien and determine the number of aliens in a row.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        # Determine the number of rows of aliens that fit on the screen.
        number_rows = min(self.stats.level + 1, 5)
        
        for row_number in range(number_rows):
            current_y = alien_height + 2 * alien_height * row_number
            current_x = alien_width
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)    
        
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                if self.ship.firing:
                    self._fire_bullet()
                self._update_bullets()
                self._update_alien_bullets()
                self._update_aliens()
                if random.randint(0, 1000) == 1:
                    self._create_powerup()
                self._update_powerups()
            self._update_screen()
            self.clock.tick(60)

    def _create_powerup(self):
        """Create a powerup and add it to the group."""
        new_powerup = Powerup(self)
        self.powerups.add(new_powerup)

    def _update_powerups(self):
        """Update powerups and check for collisions with the ship."""
        self.powerups.update()
        
        # Remove powerups that have gone off screen
        for powerup in self.powerups.copy():
            if powerup.rect.top > self.settings.screen_height:
                self.powerups.remove(powerup)

        # Check for collisions with the ship
        collided_powerup = pygame.sprite.spritecollideany(self.ship, self.powerups)
        if collided_powerup:
            self.ship.has_super_bullet = True
            self.powerups.remove(collided_powerup)
    
    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()
        
        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

        # Randomly fire alien bullets
        if self.game_active and len(self.aliens) > 0:
            if random.randint(0, self.settings.alien_fire_rate) == 0:
                self._fire_alien_bullet()

    def _check_events(self):
        #Respond to keybpresses and mouse events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)    
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_buttons(mouse_pos)

    def _check_buttons(self, mouse_pos):
        """Start a new game when the player clicks a difficulty button."""
        play_clicked = self.play_button.rect.collidepoint(mouse_pos)
        easy_clicked = self.easy_button.rect.collidepoint(mouse_pos)
        hard_clicked = self.hard_button.rect.collidepoint(mouse_pos)

        if play_clicked and not self.game_active:
            self.settings.set_difficulty('medium')
            self._start_game()
        elif easy_clicked and not self.game_active:
            self.settings.set_difficulty('easy')
            self._start_game()
        elif hard_clicked and not self.game_active:
            self.settings.set_difficulty('hard')
            self._start_game()

    def _start_game(self):
        """Starts a new game with the selected difficulty."""
        # Reset the game settings.
        self.settings.initialize_dynamic_settings()
        # Reset the game statistics.
        self.stats.reset_stats()
        self.stats.game_over = False
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()
        self.game_active = True
        
        # Get rid of any remaining bullets and aliens.
        self.bullets.empty()
        self.aliens.empty()
        self.alien_bullets.empty()
        
        # Create a new fleet and center the ship.
        self._create_fleet()
        self.ship.center_ship()
        
        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)
            
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1        

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self.ship.firing = True
            
    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_SPACE:
            self.ship.firing = False
            self._fire_bullet()
            
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group"""
        if self.ship.has_super_bullet:
            new_bullet = Bullet(self, is_super=True)
            new_bullet.rect.height = self.settings.screen_height
            new_bullet.rect.top = 0
            self.bullets.add(new_bullet)
            self.ship.has_super_bullet = False
        elif len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _fire_alien_bullet(self):
        """Create a new alien bullet and add it to the alien bullets group"""
        if len(self.aliens) > 0:
            bottom_row_y = 0
            for alien in self.aliens.sprites():
                if alien.rect.y > bottom_row_y:
                    bottom_row_y = alien.rect.y
            
            bottom_aliens = []
            for alien in self.aliens.sprites():
                if alien.rect.y == bottom_row_y:
                    bottom_aliens.append(alien)

            if bottom_aliens:
                random_alien = random.choice(bottom_aliens)
                new_bullet = AlienBullet(self, random_alien)
                self.alien_bullets.add(new_bullet)
    
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        # Get rid of the bullets that have disappeared 
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()

    def _update_alien_bullets(self):
        """Update position of alien bullets and get rid of old bullets."""
        # Update bullet positions.
        self.alien_bullets.update()
        # Get rid of the bullets that have disappeared 
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()
    
    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Regular collisions
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            for aliens_hit in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens_hit)
                self.sb.prep_score()
            self.sb.check_high_score()
        
        # Check for super bullet collisions
        for bullet in self.bullets.copy():
            if bullet.is_super:
                aliens_hit = pygame.sprite.spritecollide(bullet, self.aliens, True)
                if aliens_hit:
                    self.stats.score += self.settings.alien_points * len(aliens_hit)
                    self.sb.prep_score()
                    self.sb.check_high_score()
                self.bullets.remove(bullet) # Remove super bullet after one frame

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self.alien_bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()
        
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        #Redraw the screen during each pass through the loop
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)
        self.powerups.draw(self.screen)
        
        # Draw the score information.
        self.sb.show_score()
        
        # Draw the difficulty buttons if the game is inactive.
        if not self.game_active:
            self._draw_title_screen()
            self.play_button.draw_button()
            self.easy_button.draw_button()
            self.hard_button.draw_button()
        
        #Make the most recently drawn screen visible
        pygame.display.flip()

    def _draw_title_screen(self):
        """Draws the title screen with title and instructions."""
        if self.stats.game_over:
            game_over_image = self.settings.game_over_font.render(
                self.settings.game_over_text, True, self.settings.game_over_color, self.settings.bg_color)
            game_over_rect = game_over_image.get_rect()
            game_over_rect.centerx = self.screen.get_rect().centerx
            game_over_rect.centery = self.screen.get_rect().centery - 100
            self.screen.blit(game_over_image, game_over_rect)
        else:
            title_image = self.settings.title_font.render(
                self.settings.title_text, True, self.settings.title_color, self.settings.bg_color)
            title_rect = title_image.get_rect()
            title_rect.centerx = self.screen.get_rect().centerx
            title_rect.centery = self.screen.get_rect().centery - 100
            self.screen.blit(title_image, title_rect)
        
        instructions_image = self.settings.instructions_font.render(
            self.settings.instructions_text, True, self.settings.instructions_color, self.settings.bg_color)
        instructions_rect = instructions_image.get_rect()
        instructions_rect.centerx = self.screen.get_rect().centerx
        instructions_rect.centery = self.screen.get_rect().centery - 75
        self.screen.blit(instructions_image, instructions_rect)
    
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()
            
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause.
            sleep(0.5)
        else:
            self.game_active = False
            self.stats.game_over = True
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break
if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienEnvasion()
    ai.run_game()