import imgui
from imgui.integrations.pygame import PygameRenderer
import pygame
import time
from typing import Tuple


class PongGame:
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        
        # Game state
        self.paddle_x = 50
        self.paddle_y = height // 2 - 40
        self.paddle_width = 10
        self.paddle_height = 80
        self.paddle_speed = 20
        self.paddle_direction = 1  # 1 for up, -1 for down
        
        self.ball_x = width // 2
        self.ball_y = height // 2
        self.ball_size = 10
        self.ball_dx = 3
        self.ball_dy = 2
        
        # Game setup
        pygame.init()
        self.screen = pygame.display.set_mode((width, height), 
                                              pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        pygame.display.set_caption("Muse-Pong")
        
        imgui.create_context()
        self.renderer = PygameRenderer()
        
        self.running = True
        self.clock = pygame.time.Clock()
        
    def handle_blink(self):
        """Handle blink input - alternates paddle direction."""
        self.paddle_y += self.paddle_direction * self.paddle_speed
        self.paddle_direction *= -1  # Alternate direction
        
        # Keep paddle in bounds
        self.paddle_y = max(0, min(self.paddle_y, self.height - self.paddle_height))
    
    def handle_spacebar(self):
        """Handle spacebar input (simulation mode) - same as blink."""
        self.handle_blink()
    
    def update_ball(self):
        """Update ball position and handle collisions."""
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ball collision with top/bottom walls
        if self.ball_y <= 0 or self.ball_y >= self.height - self.ball_size:
            self.ball_dy *= -1
        
        # Ball collision with left paddle
        if (self.ball_x <= self.paddle_x + self.paddle_width and 
            self.ball_y >= self.paddle_y and 
            self.ball_y <= self.paddle_y + self.paddle_height):
            self.ball_dx *= -1
            self.ball_x = self.paddle_x + self.paddle_width
        
        # Ball goes off left edge - reset
        if self.ball_x < 0:
            self.reset_ball()
        
        # Ball goes off right edge - reset
        if self.ball_x > self.width:
            self.reset_ball()
    
    def reset_ball(self):
        """Reset ball to center."""
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_dx *= -1  # Change direction
    
    def process_events(self) -> bool:
        """Process pygame events. Returns False if should quit."""
        spacebar_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    spacebar_pressed = True
            
            self.renderer.process_event(event)
        
        return True, spacebar_pressed
    
    def render(self):
        """Render the game using imgui."""
        self.renderer.process_inputs()
        imgui.new_frame()
        
        # Create fullscreen window
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(self.width, self.height)
        
        imgui.begin("Pong", flags=imgui.WINDOW_NO_TITLE_BAR | 
                                 imgui.WINDOW_NO_RESIZE | 
                                 imgui.WINDOW_NO_MOVE | 
                                 imgui.WINDOW_NO_SCROLLBAR)
        
        draw_list = imgui.get_window_draw_list()
        
        # Draw paddle
        draw_list.add_rect_filled(
            self.paddle_x, self.paddle_y,
            self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height,
            imgui.get_color_u32_rgba(1, 1, 1, 1)
        )
        
        # Draw ball
        draw_list.add_rect_filled(
            self.ball_x, self.ball_y,
            self.ball_x + self.ball_size, self.ball_y + self.ball_size,
            imgui.get_color_u32_rgba(1, 1, 1, 1)
        )
        
        # Draw center line
        for y in range(0, self.height, 20):
            draw_list.add_rect_filled(
                self.width // 2 - 2, y,
                self.width // 2 + 2, y + 10,
                imgui.get_color_u32_rgba(0.5, 0.5, 0.5, 1)
            )
        
        imgui.end()
        
        imgui.render()
        self.renderer.render(imgui.get_draw_data())
        pygame.display.flip()
    
    def run_frame(self, blink_detected: bool = False, simulation_mode: bool = False):
        """Run one frame of the game."""
        continue_running, spacebar_pressed = self.process_events()
        
        if not continue_running:
            self.running = False
            return False
        
        # Handle input
        if blink_detected or (simulation_mode and spacebar_pressed):
            self.handle_blink()
        
        # Update game state
        self.update_ball()
        
        # Render
        self.render()
        self.clock.tick(60)  # 60 FPS
        
        return True
    
    def cleanup(self):
        """Clean up resources."""
        self.renderer.shutdown()
        pygame.quit()