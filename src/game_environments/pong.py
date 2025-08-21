import pygame
import random
import sys
from typing import Tuple


class PongGame:
    def __init__(self, width: int = 600, height: int = 400, npc_mode: bool = False, ball_speed: float = 6.0):
        # Constants
        self.WIDTH = width
        self.HEIGHT = height
        self.BALL_RADIUS = 10
        self.PAD_WIDTH = 8
        self.PAD_HEIGHT = 80
        self.HALF_PAD_WIDTH = self.PAD_WIDTH / 2
        self.HALF_PAD_HEIGHT = self.PAD_HEIGHT / 2
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLACK = (0, 0, 0)
        self.YELLOW = (255, 255, 0)
        
        # Game setup
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT), 0, 32)
        pygame.display.set_caption("Muse-Pong")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.ball_pos = [0, 0]
        self.ball_vel = [0, 0]
        self.paddle1_pos = [0, 0]
        self.paddle2_pos = [0, 0]
        self.paddle1_vel = 0
        self.paddle2_vel = 0
        self.l_score = 0
        self.r_score = 0
        self.running = True
        self.paddle_direction = 1  # 1 for up, -1 for down
        self.paddle_speed = 4
        self.npc_mode = npc_mode
        self.ball_speed = ball_speed
        self.game_started = False  # New state for blink-to-start
        self.ball_start_right = True  # Default ball direction for start
        
        # Keyboard state for paddle2
        self.keys_pressed = set()
        
        self.init_game()
    
    def ball_init(self, right):
        """Initialize ball position and velocity."""
        self.ball_pos = [self.WIDTH/2, self.HEIGHT/2]
        
        if self.game_started:
            # Only set velocity if game has started
            horz = self.ball_speed * random.uniform(0.7, 1.3)  # Random variation
            vert = self.ball_speed * random.uniform(0.3, 0.8)
            
            if not right:
                horz = -horz
                
            self.ball_vel = [horz, -vert]
        else:
            # Ball starts stationary
            self.ball_vel = [0, 0]
            # Store intended direction for when game starts
            self.ball_start_right = right
    
    def init_game(self):
        """Initialize game state."""
        self.paddle1_pos = [self.HALF_PAD_WIDTH - 1, self.HEIGHT/2]
        self.paddle2_pos = [self.WIDTH + 1 - self.HALF_PAD_WIDTH, self.HEIGHT/2]
        self.paddle1_vel = 0  # Don't start moving until game starts
        self.l_score = 0
        self.r_score = 0
        
        if random.randrange(0, 2) == 0:
            self.ball_init(True)
        else:
            self.ball_init(False)
    
    def reset_paddles(self):
        """Reset paddles to center position and continue moving."""
        self.paddle1_pos = [self.HALF_PAD_WIDTH - 1, self.HEIGHT/2]
        self.paddle2_pos = [self.WIDTH + 1 - self.HALF_PAD_WIDTH, self.HEIGHT/2]
        self.paddle_direction = 1  # Reset to moving up
        if self.game_started:  # Only start moving if game has started
            self.paddle1_vel = self.paddle_direction * self.paddle_speed
    
    def handle_blink(self):
        """Handle blink input - starts game or changes paddle direction."""
        if not self.game_started:
            self.start_game()
        else:
            self.paddle_direction *= -1  # Alternate direction
            self.paddle1_vel = self.paddle_direction * self.paddle_speed
        print("Blink detected!")
    
    def start_game(self):
        """Start the game - begin paddle and ball movement."""
        self.game_started = True
        self.paddle1_vel = self.paddle_direction * self.paddle_speed
        
        # Start ball movement using stored direction
        horz = self.ball_speed * random.uniform(0.7, 1.3)
        vert = self.ball_speed * random.uniform(0.3, 0.8)
        
        if not self.ball_start_right:
            horz = -horz
            
        self.ball_vel = [horz, -vert]
    
    def reset_round(self, ball_direction_right):
        """Reset for next round - requires blink to start."""
        self.game_started = False
        self.paddle1_vel = 0
        self.reset_paddles()
        self.ball_init(ball_direction_right)
    
    def draw(self):
        """Main draw function."""
        self.window.fill(self.BLACK)
        
        # Draw lines
        pygame.draw.line(self.window, self.WHITE, [self.WIDTH / 2, 0], [self.WIDTH / 2, self.HEIGHT], 1)
        pygame.draw.line(self.window, self.WHITE, [self.PAD_WIDTH, 0], [self.PAD_WIDTH, self.HEIGHT], 1)
        pygame.draw.line(self.window, self.WHITE, [self.WIDTH - self.PAD_WIDTH, 0], [self.WIDTH - self.PAD_WIDTH, self.HEIGHT], 1)
        pygame.draw.circle(self.window, self.WHITE, [self.WIDTH//2, self.HEIGHT//2], 70, 1)
        
        # Only update positions if game has started
        if self.game_started:
            # Update paddle positions - paddle bounces off top/bottom walls
            if (self.paddle1_pos[1] > self.HALF_PAD_HEIGHT and 
                self.paddle1_pos[1] < self.HEIGHT - self.HALF_PAD_HEIGHT):
                self.paddle1_pos[1] += self.paddle1_vel
            elif self.paddle1_pos[1] <= self.HALF_PAD_HEIGHT and self.paddle1_vel < 0:
                # Hit top wall, reverse direction
                self.paddle1_vel = 0
            elif self.paddle1_pos[1] >= self.HEIGHT - self.HALF_PAD_HEIGHT and self.paddle1_vel > 0:
                # Hit bottom wall, reverse direction  
                self.paddle1_vel = 0
            else:
                self.paddle1_pos[1] += self.paddle1_vel
            
            # Update paddle2 position
            if self.npc_mode:
                # AI follows ball Y position
                ball_center_y = self.ball_pos[1]
                paddle2_center_y = self.paddle2_pos[1]
                
                if ball_center_y < paddle2_center_y - 5:
                    self.paddle2_pos[1] -= 3  # Move up
                elif ball_center_y > paddle2_center_y + 5:
                    self.paddle2_pos[1] += 3  # Move down
                
                # Keep paddle2 in bounds
                self.paddle2_pos[1] = max(self.HALF_PAD_HEIGHT, 
                                        min(self.paddle2_pos[1], self.HEIGHT - self.HALF_PAD_HEIGHT))
            else:
                # Human keyboard control
                if pygame.K_UP in self.keys_pressed:
                    self.paddle2_pos[1] -= 6
                if pygame.K_DOWN in self.keys_pressed:
                    self.paddle2_pos[1] += 6
                
                # Keep paddle2 in bounds
                self.paddle2_pos[1] = max(self.HALF_PAD_HEIGHT, 
                                        min(self.paddle2_pos[1], self.HEIGHT - self.HALF_PAD_HEIGHT))
            
            # Update ball position
            self.ball_pos[0] += int(self.ball_vel[0])
            self.ball_pos[1] += int(self.ball_vel[1])
        
        # Draw ball and paddles
        pygame.draw.circle(self.window, self.RED, [int(self.ball_pos[0]), int(self.ball_pos[1])], self.BALL_RADIUS, 0)
        
        # Draw paddle1 (left, controlled by blinks)
        pygame.draw.polygon(self.window, self.GREEN, [
            [self.paddle1_pos[0] - self.HALF_PAD_WIDTH, self.paddle1_pos[1] - self.HALF_PAD_HEIGHT],
            [self.paddle1_pos[0] - self.HALF_PAD_WIDTH, self.paddle1_pos[1] + self.HALF_PAD_HEIGHT],
            [self.paddle1_pos[0] + self.HALF_PAD_WIDTH, self.paddle1_pos[1] + self.HALF_PAD_HEIGHT],
            [self.paddle1_pos[0] + self.HALF_PAD_WIDTH, self.paddle1_pos[1] - self.HALF_PAD_HEIGHT]
        ], 0)
        
        # Draw paddle2 (right, stationary for now)
        pygame.draw.polygon(self.window, self.GREEN, [
            [self.paddle2_pos[0] - self.HALF_PAD_WIDTH, self.paddle2_pos[1] - self.HALF_PAD_HEIGHT],
            [self.paddle2_pos[0] - self.HALF_PAD_WIDTH, self.paddle2_pos[1] + self.HALF_PAD_HEIGHT],
            [self.paddle2_pos[0] + self.HALF_PAD_WIDTH, self.paddle2_pos[1] + self.HALF_PAD_HEIGHT],
            [self.paddle2_pos[0] + self.HALF_PAD_WIDTH, self.paddle2_pos[1] - self.HALF_PAD_HEIGHT]
        ], 0)
        
        # Ball collision with walls
        if int(self.ball_pos[1]) <= self.BALL_RADIUS:
            self.ball_vel[1] = -self.ball_vel[1]
        if int(self.ball_pos[1]) >= self.HEIGHT + 1 - self.BALL_RADIUS:
            self.ball_vel[1] = -self.ball_vel[1]
        
        # Ball collision with paddles
        if (int(self.ball_pos[0]) <= self.BALL_RADIUS + self.PAD_WIDTH and 
            int(self.ball_pos[1]) in range(int(self.paddle1_pos[1] - self.HALF_PAD_HEIGHT), 
                                         int(self.paddle1_pos[1] + self.HALF_PAD_HEIGHT), 1)):
            self.ball_vel[0] = -self.ball_vel[0]
            self.ball_vel[0] *= 1.1
            self.ball_vel[1] *= 1.1
        elif int(self.ball_pos[0]) <= self.BALL_RADIUS + self.PAD_WIDTH:
            self.r_score += 1
            self.reset_round(True)
        
        if (int(self.ball_pos[0]) >= self.WIDTH + 1 - self.BALL_RADIUS - self.PAD_WIDTH and 
            int(self.ball_pos[1]) in range(int(self.paddle2_pos[1] - self.HALF_PAD_HEIGHT), 
                                         int(self.paddle2_pos[1] + self.HALF_PAD_HEIGHT), 1)):
            self.ball_vel[0] = -self.ball_vel[0]
            self.ball_vel[0] *= 1.1
            self.ball_vel[1] *= 1.1
        elif int(self.ball_pos[0]) >= self.WIDTH + 1 - self.BALL_RADIUS - self.PAD_WIDTH:
            self.l_score += 1
            self.reset_round(False)
        
        # Draw scores
        font = pygame.font.SysFont("Comic Sans MS", 20)
        label1 = font.render("Score " + str(self.l_score), 1, self.YELLOW)
        self.window.blit(label1, (50, 20))
        
        label2 = font.render("Score " + str(self.r_score), 1, self.YELLOW)
        self.window.blit(label2, (470, 20))
        
        # Draw "Blink to start!" text if game hasn't started
        if not self.game_started:
            big_font = pygame.font.SysFont("Comic Sans MS", 36)
            start_text = big_font.render("Blink to start!", 1, self.WHITE)
            text_rect = start_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
            self.window.blit(start_text, text_rect)
    
    def process_events(self):
        """Process pygame events."""
        spacebar_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, spacebar_pressed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    spacebar_pressed = True
                elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                    self.keys_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_UP, pygame.K_DOWN]:
                    self.keys_pressed.discard(event.key)
        
        return True, spacebar_pressed
    
    def run_frame(self, blink_detected: bool = False, simulation_mode: bool = False):
        """Run one frame of the game."""
        continue_running, spacebar_pressed = self.process_events()
        
        if not continue_running:
            self.running = False
            return False
        
        # Handle input
        if blink_detected or (simulation_mode and spacebar_pressed):
            self.handle_blink()
        
        # Draw everything
        self.draw()
        
        pygame.display.update()
        self.clock.tick(60)
        
        return True
    
    def cleanup(self):
        """Clean up resources."""
        pygame.quit()