import pygame
import random
import sys
from typing import Tuple


class PongGame:
    def __init__(self, width: int = 600, height: int = 400):
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
        self.pause_time = 0
        self.pause_duration = 120  # 2 seconds at 60 FPS
        
        self.init_game()
    
    def ball_init(self, right):
        """Initialize ball position and velocity."""
        self.ball_pos = [self.WIDTH/2, self.HEIGHT/2]
        horz = random.randrange(2, 4)
        vert = random.randrange(1, 3)
        
        if not right:
            horz = -horz
            
        self.ball_vel = [horz, -vert]
    
    def init_game(self):
        """Initialize game state."""
        self.paddle1_pos = [self.HALF_PAD_WIDTH - 1, self.HEIGHT/2]
        self.paddle2_pos = [self.WIDTH + 1 - self.HALF_PAD_WIDTH, self.HEIGHT/2]
        self.paddle1_vel = self.paddle_direction * self.paddle_speed  # Start moving
        self.l_score = 0
        self.r_score = 0
        
        if random.randrange(0, 2) == 0:
            self.ball_init(True)
        else:
            self.ball_init(False)
    
    def reset_paddles(self):
        """Reset paddles to center position and start moving."""
        self.paddle1_pos = [self.HALF_PAD_WIDTH - 1, self.HEIGHT/2]
        self.paddle2_pos = [self.WIDTH + 1 - self.HALF_PAD_WIDTH, self.HEIGHT/2]
        self.paddle_direction = 1  # Reset to moving up
        self.paddle1_vel = self.paddle_direction * self.paddle_speed
    
    def handle_blink(self):
        """Handle blink input - changes paddle direction."""
        self.paddle_direction *= -1  # Alternate direction
        self.paddle1_vel = self.paddle_direction * self.paddle_speed
        print("Blink detected!")
    
    def draw(self):
        """Main draw function."""
        self.window.fill(self.BLACK)
        
        # Draw lines
        pygame.draw.line(self.window, self.WHITE, [self.WIDTH / 2, 0], [self.WIDTH / 2, self.HEIGHT], 1)
        pygame.draw.line(self.window, self.WHITE, [self.PAD_WIDTH, 0], [self.PAD_WIDTH, self.HEIGHT], 1)
        pygame.draw.line(self.window, self.WHITE, [self.WIDTH - self.PAD_WIDTH, 0], [self.WIDTH - self.PAD_WIDTH, self.HEIGHT], 1)
        pygame.draw.circle(self.window, self.WHITE, [self.WIDTH//2, self.HEIGHT//2], 70, 1)
        
        # Handle pause after scoring
        if self.pause_time > 0:
            self.pause_time -= 1
            # Don't update positions during pause
        else:
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
            self.reset_paddles()
            self.ball_init(True)
            self.pause_time = self.pause_duration
        
        if (int(self.ball_pos[0]) >= self.WIDTH + 1 - self.BALL_RADIUS - self.PAD_WIDTH and 
            int(self.ball_pos[1]) in range(int(self.paddle2_pos[1] - self.HALF_PAD_HEIGHT), 
                                         int(self.paddle2_pos[1] + self.HALF_PAD_HEIGHT), 1)):
            self.ball_vel[0] = -self.ball_vel[0]
            self.ball_vel[0] *= 1.1
            self.ball_vel[1] *= 1.1
        elif int(self.ball_pos[0]) >= self.WIDTH + 1 - self.BALL_RADIUS - self.PAD_WIDTH:
            self.l_score += 1
            self.reset_paddles()
            self.ball_init(False)
            self.pause_time = self.pause_duration
        
        # Draw scores
        font = pygame.font.SysFont("Comic Sans MS", 20)
        label1 = font.render("Score " + str(self.l_score), 1, self.YELLOW)
        self.window.blit(label1, (50, 20))
        
        label2 = font.render("Score " + str(self.r_score), 1, self.YELLOW)
        self.window.blit(label2, (470, 20))
    
    def process_events(self):
        """Process pygame events."""
        spacebar_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, spacebar_pressed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    spacebar_pressed = True
        
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