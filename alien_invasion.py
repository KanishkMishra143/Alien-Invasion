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
import db


class AlienInvasion:
    """Overall class to manage game assets and behavior"""

    def __init__(self):
        pygame.init()
        db.init_db()

        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self._create_screen()

        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        self.bg_image = pygame.image.load('images/bg_img.png').convert()
        self.bg_image = pygame.transform.smoothscale(self.bg_image, (self.settings.screen_width, self.settings.screen_height))

        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.super_bullets = pygame.sprite.Group()
        self.FIRE_EVENT = pygame.USEREVENT + 1
        self._create_fleet()
        self.bg_color = (0, 0, 0)

        self.state = 'main_menu'
        self._setup_buttons()

    def _setup_buttons(self):
        center_x = self.screen.get_rect().centerx
        center_y = self.screen.get_rect().centery

        button_start_y = center_y - 150
        button_spacing = 60

        # Main Menu Buttons
        self.play_button = Button(self, "Play", (center_x, button_start_y + button_spacing))
        self.new_game_button = Button(self, "New Game", (center_x, button_start_y + button_spacing))
        self.resume_button = Button(self, "Resume", (center_x, button_start_y), is_disabled=not db.has_saved_game())
        self.settings_button = Button(self, "Settings", (center_x, button_start_y + 2 * button_spacing))
        self.quit_button = Button(self, "Quit", (center_x, button_start_y + 3 * button_spacing))

        # Difficulty Menu Buttons
        self.easy_button = Button(self, "Easy", (center_x, button_start_y))
        self.medium_button = Button(self, "Medium", (center_x, button_start_y + button_spacing))
        self.hard_button = Button(self, "Hard", (center_x, button_start_y + 2 * button_spacing))

        self.back_to_home_button = Button(self, "Back to Home", (center_x, center_y + 200))

        # Pause menu buttons
        self.pause_resume_button = Button(self, "Resume", (center_x, center_y - 40))
        self.pause_quit_button = Button(self, "Quit", (center_x, center_y + 40))

        # Settings menu UI
        label_x = center_x - 200
        value_x_offset = 0 # Center of value text relative to center_x
        decrease_x = center_x + 150
        increase_x = center_x + 230

        y_pos = button_start_y
        self.ship_speed_label = (label_x, y_pos, "Ship Speed")
        self.ship_speed_value_pos = (center_x, y_pos) # Storing pos for drawing value text
        self.ship_speed_decrease = Button(self, "-", (decrease_x, y_pos), width=50, height=50)
        self.ship_speed_increase = Button(self, "+", (increase_x, y_pos), width=50, height=50)

        y_pos += button_spacing
        self.bullet_speed_label = (label_x, y_pos, "Bullet Speed")
        self.bullet_speed_value_pos = (center_x, y_pos)
        self.bullet_speed_decrease = Button(self, "-", (decrease_x, y_pos), width=50, height=50)
        self.bullet_speed_increase = Button(self, "+", (increase_x, y_pos), width=50, height=50)

        y_pos += button_spacing
        self.alien_speed_label = (label_x, y_pos, "Alien Speed")
        self.alien_speed_value_pos = (center_x, y_pos)
        self.alien_speed_decrease = Button(self, "-", (decrease_x, y_pos), width=50, height=50)
        self.alien_speed_increase = Button(self, "+", (increase_x, y_pos), width=50, height=50)

        y_pos += button_spacing
        self.speedup_scale_label = (label_x, y_pos, "Speedup Scale")
        self.speedup_scale_value_pos = (center_x, y_pos)
        self.speedup_scale_decrease = Button(self, "-", (decrease_x, y_pos), width=50, height=50)
        self.speedup_scale_increase = Button(self, "+", (increase_x, y_pos), width=50, height=50)


    def _create_screen(self):
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))

        if hasattr(self, 'bg_image'):
             self.bg_image = pygame.transform.smoothscale(self.bg_image, self.screen.get_rect().size)

        self._setup_buttons()


    def _create_fleet(self):
        """Create the fleet of aliens"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
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

            if self.state == 'in_game':
                self.ship.update()

                self._update_bullets()
                self._update_alien_bullets()
                self._update_aliens()
                if random.randint(0, 1000) == 1:
                    self._create_powerup()
                self._update_powerups()
            self._update_screen()
            self.clock.tick(60)

    def _create_powerup(self):
        new_powerup = Powerup(self)
        self.powerups.add(new_powerup)

    def _update_powerups(self):
        self.powerups.update()
        for powerup in self.powerups.copy():
            if powerup.rect.top > self.settings.screen_height:
                self.powerups.remove(powerup)
        collided_powerup = pygame.sprite.spritecollideany(self.ship, self.powerups)
        if collided_powerup:
            self.ship.has_super_bullet = True
            self.powerups.remove(collided_powerup)

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        self._check_aliens_bottom()
        if self.state == 'in_game' and len(self.aliens) > 0:
            if random.randint(0, self.settings.alien_fire_rate) == 0:
                self._fire_alien_bullet()

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.state == 'in_game':
                    db.save_gamestate(self.stats.level, self.stats.score, self.stats.ships_left)
                sys.exit()
            elif event.type == self.FIRE_EVENT:
                self._fire_bullet()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.state == 'main_menu':
                    self._check_main_menu_buttons(mouse_pos)
                elif self.state == 'difficulty_select':
                    self._check_difficulty_buttons(mouse_pos)
                elif self.state == 'settings':
                    self._check_settings_buttons(mouse_pos)
                elif self.state == 'paused':
                    self._check_pause_menu_buttons(mouse_pos)
                elif self.state == 'game_over':
                    if self.back_to_home_button.rect.collidepoint(mouse_pos):
                        self.state = 'main_menu'

    def _check_main_menu_buttons(self, mouse_pos):
        if self.play_button.rect.collidepoint(mouse_pos) and not db.has_saved_game():
            self.state = 'difficulty_select'
        if self.new_game_button.rect.collidepoint(mouse_pos) and db.has_saved_game():
            self.state = 'difficulty_select'
        if self.resume_button.rect.collidepoint(mouse_pos) and not self.resume_button.is_disabled:
            self._resume_game()
        if self.settings_button.rect.collidepoint(mouse_pos):
            self.state = 'settings'
        if self.quit_button.rect.collidepoint(mouse_pos):
            sys.exit()

    def _check_difficulty_buttons(self, mouse_pos):
        if self.easy_button.rect.collidepoint(mouse_pos):
            self.settings.set_difficulty('easy')
            self._start_new_game()
        elif self.medium_button.rect.collidepoint(mouse_pos):
            self.settings.set_difficulty('medium')
            self._start_new_game()
        elif self.hard_button.rect.collidepoint(mouse_pos):
            self.settings.set_difficulty('hard')
            self._start_new_game()
        elif self.back_to_home_button.rect.collidepoint(mouse_pos):
            self.state = 'main_menu'

    def _check_settings_buttons(self, mouse_pos):
        # Ship speed controls
        if self.ship_speed_increase.rect.collidepoint(mouse_pos):
            self.settings.custom_settings['ship_speed'] = min(5.0, self.settings.ship_speed + 0.1)
            self.settings.ship_speed = self.settings.custom_settings['ship_speed']
        elif self.ship_speed_decrease.rect.collidepoint(mouse_pos):
            self.settings.custom_settings['ship_speed'] = max(0.5, self.settings.ship_speed - 0.1)
            self.settings.ship_speed = self.settings.custom_settings['ship_speed']

        # Bullet speed controls
        elif self.bullet_speed_increase.rect.collidepoint(mouse_pos):
            self.settings.custom_settings['bullet_speed'] = min(10.0, self.settings.bullet_speed + 0.1)
            self.settings.bullet_speed = self.settings.custom_settings['bullet_speed']
        elif self.bullet_speed_decrease.rect.collidepoint(mouse_pos):
            self.settings.custom_settings['bullet_speed'] = max(1.0, self.settings.bullet_speed - 0.1)
            self.settings.bullet_speed = self.settings.custom_settings['bullet_speed']

        # Alien speed controls
        elif self.alien_speed_increase.rect.collidepoint(mouse_pos):
            self.settings.custom_settings['alien_speed'] = min(5.0, self.settings.alien_speed + 0.1)
            self.settings.alien_speed = self.settings.custom_settings['alien_speed']
        elif self.alien_speed_decrease.rect.collidepoint(mouse_pos):
            self.settings.custom_settings['alien_speed'] = max(0.5, self.settings.alien_speed - 0.1)
            self.settings.alien_speed = self.settings.custom_settings['alien_speed']

        # Speedup scale controls
        elif self.speedup_scale_increase.rect.collidepoint(mouse_pos):
            self.settings.custom_settings['speedup_scale'] = min(2.0, self.settings.speedup_scale + 0.1)
            self.settings.speedup_scale = self.settings.custom_settings['speedup_scale']
        elif self.speedup_scale_decrease.rect.collidepoint(mouse_pos):
            self.settings.custom_settings['speedup_scale'] = max(1.1, self.settings.speedup_scale - 0.1)
            self.settings.speedup_scale = self.settings.custom_settings['speedup_scale']

        elif self.back_to_home_button.rect.collidepoint(mouse_pos):
            self.state = 'main_menu'

    def _check_pause_menu_buttons(self, mouse_pos):
        resume_clicked = self.pause_resume_button.rect.collidepoint(mouse_pos)
        quit_clicked = self.pause_quit_button.rect.collidepoint(mouse_pos)

        if resume_clicked:
            self.state = 'in_game'
            pygame.mouse.set_visible(False)
        elif quit_clicked:
            db.save_gamestate(self.stats.level, self.stats.score, self.stats.ships_left)
            self.state = 'main_menu'
            self.resume_button.is_disabled = False
            self.resume_button._prep_msg("Resume")


    def _start_new_game(self):
        db.delete_gamestate()
        self.settings.initialize_dynamic_settings()
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self._start_game()
        self.resume_button.is_disabled = True
        self.resume_button._prep_msg("Resume")


    def _resume_game(self):
        level, score, lives = db.load_gamestate()
        self.stats = GameStats(self, loaded_stats={'level': level, 'score': score, 'lives': lives})
        self.sb = Scoreboard(self)
        self._start_game()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

    def _start_game(self):
        self.settings.initialize_dynamic_settings()
        self.state = 'in_game'
        self.aliens.empty()
        self.bullets.empty()
        self.super_bullets.empty()
        self.alien_bullets.empty()
        self._create_fleet()
        self.ship.center_ship()
        pygame.mouse.set_visible(False)

        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()


    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_keydown_events(self, event):
        if event.key == pygame.K_q:
            if self.state == 'in_game':
                db.save_gamestate(self.stats.level, self.stats.score, self.stats.ships_left)
            sys.exit()

        if self.state == 'in_game':
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = True
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = True
            elif event.key == pygame.K_SPACE:
                self.ship.firing = True
                self._fire_bullet()
                pygame.time.set_timer(self.FIRE_EVENT, 150)
            elif event.key == pygame.K_ESCAPE:
                self.state = 'paused'
                pygame.mouse.set_visible(True)
        elif self.state == 'paused':
            if event.key == pygame.K_ESCAPE:
                self.state = 'in_game'
                pygame.mouse.set_visible(False)

    def _check_keyup_events(self, event):
        if self.state == 'in_game':
            if event.key == pygame.K_RIGHT:
                self.ship.moving_right = False
            elif event.key == pygame.K_LEFT:
                self.ship.moving_left = False
            elif event.key == pygame.K_SPACE:
                self.ship.firing = False
                pygame.time.set_timer(self.FIRE_EVENT, 0)

    def _fire_bullet(self):
        if self.ship.has_super_bullet:
            new_bullet = Bullet(self, is_super=True)
            new_bullet.rect.width = 100
            new_bullet.rect.centerx = self.ship.rect.centerx
            new_bullet.rect.height = self.settings.screen_height
            new_bullet.y = 0
            new_bullet.rect.top = 0
            new_bullet.y = 0
            self.super_bullets.add(new_bullet)
            self.ship.has_super_bullet = False
        elif len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _fire_alien_bullet(self):
        if len(self.aliens) > 0:
            bottom_row_y = 0
            for alien in self.aliens.sprites():
                if alien.rect.y > bottom_row_y:
                    bottom_row_y = alien.rect.y
            bottom_aliens = [alien for alien in self.aliens.sprites() if alien.rect.y == bottom_row_y]
            if bottom_aliens:
                random_alien = random.choice(bottom_aliens)
                new_bullet = AlienBullet(self, random_alien)
                self.alien_bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._update_super_bullets()
        self._check_bullet_alien_collisions()

    def _update_super_bullets(self):
        self.super_bullets.update()
        for bullet in self.super_bullets.copy():
            if bullet.rect.bottom <= 0:
                self.super_bullets.remove(bullet)

    def _update_alien_bullets(self):
        self.alien_bullets.update()
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)
        if pygame.sprite.spritecollideany(self.ship, self.alien_bullets):
            self._ship_hit()

    def _check_bullet_alien_collisions(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens_hit in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens_hit)
            self.sb.prep_score()
            self.sb.check_high_score()

        for bullet in self.super_bullets.copy():
            aliens_hit = pygame.sprite.spritecollide(bullet, self.aliens, True)
            if aliens_hit:
                self.stats.score += self.settings.alien_points * len(aliens_hit)
                self.sb.prep_score()
                self.sb.check_high_score()
            # Super bullet is removed once it clears its path (goes off screen)
            # or we can keep the one-frame logic but make it visible.
            # Let's try letting it travel normally but being much bigger.

        if not self.aliens:
            self.bullets.empty()
            self.super_bullets.empty()
            self.alien_bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()
            db.save_gamestate(self.stats.level, self.stats.score, self.stats.ships_left)


    def _update_screen(self):
        if self.state in ('in_game', 'paused'):
            self.screen.blit(self.bg_image, (0, 0))
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            for bullet in self.alien_bullets.sprites():
                bullet.draw_bullet()
            for bullet in self.super_bullets.sprites():
                bullet.draw_bullet()
            self.ship.blitme()
            self.aliens.draw(self.screen)
            self.powerups.draw(self.screen)
            self.sb.show_score()
        else:
            self.screen.blit(self.bg_image, (0, 0))

        if self.state == 'paused':
            self.pause_resume_button.draw_button()
            self.pause_quit_button.draw_button()
        elif self.state == 'main_menu':
            self._draw_main_menu()
        elif self.state == 'difficulty_select':
            self._draw_difficulty_select_screen()
        elif self.state == 'settings':
            self._draw_settings_screen()
        elif self.state == 'game_over':
            self._draw_game_over_screen()

        pygame.display.flip()

    def _draw_main_menu(self):
        self._draw_title()
        self.resume_button.draw_button()

        has_saved_game = db.has_saved_game()
        if has_saved_game:
            self.new_game_button.draw_button()
        else:
            self.play_button.draw_button()

        self.settings_button.draw_button()
        self.quit_button.draw_button()

    def _draw_difficulty_select_screen(self):
        self._draw_title()
        self.easy_button.draw_button()
        self.medium_button.draw_button()
        self.hard_button.draw_button()
        self.back_to_home_button.draw_button()

    def _draw_settings_screen(self):
        self._draw_title()

        # Define settings rows with their properties (label text, current value, decrease/increase buttons)
        settings_rows = [
            ("Ship Speed", self.settings.ship_speed, self.ship_speed_decrease, self.ship_speed_increase),
            ("Bullet Speed", self.settings.bullet_speed, self.bullet_speed_decrease, self.bullet_speed_increase),
            ("Alien Speed", self.settings.alien_speed, self.alien_speed_decrease, self.alien_speed_increase),
            ("Speedup Scale", self.settings.speedup_scale, self.speedup_scale_decrease, self.speedup_scale_increase),
        ]

        label_font = pygame.font.SysFont(None, 48)
        value_font = pygame.font.SysFont(None, 36)
        value_color = (200, 200, 200) # Off-white / light grey for value text

        for i, (label_text, current_value, decrease_button, increase_button) in enumerate(settings_rows):
            y_pos = self.screen.get_rect().centery - 150 + (i * 60) # Centralize rows vertically

            # --- Label Panel and Text ---
            label_surface = label_font.render(label_text, True, (255, 255, 255))
            label_rect = label_surface.get_rect()

            # Semi-transparent dark panel for label
            panel_width = label_rect.width + 40
            panel_height = 60 # Fixed height for consistency
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel_surface.fill((0, 0, 0, 128)) # Dark with 50% opacity

            panel_rect = panel_surface.get_rect()
            panel_rect.left = self.screen.get_rect().centerx - 250 # Left-align panel
            panel_rect.centery = y_pos

            self.screen.blit(panel_surface, panel_rect)

            label_rect.left = panel_rect.left + 20 # Text slightly indented
            label_rect.centery = panel_rect.centery
            self.screen.blit(label_surface, label_rect)

            # --- +/- Buttons ---
            decrease_button.rect.centery = y_pos
            decrease_button.draw_button()

            increase_button.rect.centery = y_pos
            increase_button.draw_button()

            # --- Value Text ---
            value_str = f"{current_value:.1f}"
            value_surface = value_font.render(value_str, True, value_color)
            value_rect = value_surface.get_rect()

            # Center value text between +/- buttons
            value_rect.centerx = decrease_button.rect.centerx + (increase_button.rect.centerx - decrease_button.rect.centerx) / 2
            value_rect.centery = y_pos
            self.screen.blit(value_surface, value_rect)

        self.back_to_home_button.draw_button()


    def _draw_text(self, text, x, y, size=48, color=(255, 255, 255), panel=False):
        font = pygame.font.SysFont(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)

        if panel:
            panel_rect = text_rect.inflate(40, 20)
            panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            panel_surface.fill((0, 0, 0, 128))
            self.screen.blit(panel_surface, panel_rect)

        self.screen.blit(text_surface, text_rect)


    def _draw_game_over_screen(self):
        self._draw_title()
        game_over_image = self.settings.game_over_font.render(
            self.settings.game_over_text, True, self.settings.game_over_color, (0,0,0,0))
        game_over_rect = game_over_image.get_rect()
        game_over_rect.centerx = self.screen.get_rect().centerx
        game_over_rect.centery = self.screen.get_rect().centery - 100
        self.screen.blit(game_over_image, game_over_rect)

        score_str = f"Final Score: {self.stats.score:,}"
        high_score_str = f"High Score: {self.stats.high_score:,}"
        self._draw_text(score_str, self.screen.get_rect().centerx, self.screen.get_rect().centery, size=48)
        self._draw_text(high_score_str, self.screen.get_rect().centerx, self.screen.get_rect().centery + 50, size=36)

        self.back_to_home_button.draw_button()

    def _draw_title(self):
        title_image = self.settings.title_font.render(
            self.settings.title_text, True, self.settings.title_color, None)
        title_rect = title_image.get_rect()
        title_rect.centerx = self.screen.get_rect().centerx
        title_rect.y = 50
        self.screen.blit(title_image, title_rect)

    def _ship_hit(self):
        if self.stats.ships_left > 0:
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            self.bullets.empty()
            self.super_bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()
            self._create_fleet()
            self.ship.center_ship()
            db.save_gamestate(self.stats.level, self.stats.score, self.stats.ships_left)
            sleep(0.5)
        else:
            self.state = 'game_over'
            self.sb.check_high_score()
            db.update_highscore(self.stats.score)
            db.delete_gamestate()
            pygame.mouse.set_visible(True)
            self.resume_button.is_disabled = True
            self.resume_button._prep_msg("Resume")


    def _check_aliens_bottom(self):
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break

if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()