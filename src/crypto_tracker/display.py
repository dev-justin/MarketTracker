import pygame
import os
import platform
from pathlib import Path

class Display:
    def __init__(self):
        # Set up XDG_RUNTIME_DIR if running with sudo
        if os.geteuid() == 0:  # Check if running as root/sudo
            uid = int(os.environ.get('SUDO_UID', 1000))
            runtime_dir = f"/run/user/{uid}"
            os.environ['XDG_RUNTIME_DIR'] = runtime_dir
            
            # Create directory if it doesn't exist
            Path(runtime_dir).mkdir(parents=True, exist_ok=True)
            os.chmod(runtime_dir, 0o700)
            os.chown(runtime_dir, uid, uid)

        # Initialize pygame
        pygame.init()
        
        # Set up the display for Raspberry Pi
        os.putenv('SDL_VIDEODRIVER', 'fbcon')  # Tell SDL to use the framebuffer
        os.putenv('SDL_FBDEV', '/dev/fb0')     # Set the framebuffer device
        
        # Set up the display
        # Using your display's resolution
        self.width = 800
        self.height = 480
        
        # Initialize the display with no window manager
        if platform.machine() == 'armv7l':  # Check if we're on Raspberry Pi
            self.screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.FULLSCREEN | pygame.NOFRAME | pygame.HWSURFACE
            )
        else:
            self.screen = pygame.display.set_mode((self.width, self.height))
            
        pygame.display.set_caption("Crypto Tracker")
        
        # Set up fonts
        self.font = pygame.font.Font(None, 36)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)

    def update(self, prices):
        # Clear the screen
        self.screen.fill(self.BLACK)
        
        # Display each crypto price
        y_position = 50
        for symbol, price in prices.items():
            text = f"{symbol}: ${price:,.2f}"
            text_surface = self.font.render(text, True, self.WHITE)
            self.screen.blit(text_surface, (50, y_position))
            y_position += 60
        
        # Update the display
        pygame.display.flip()

    def cleanup(self):
        pygame.quit() 