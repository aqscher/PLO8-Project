# test_pygame.py
import os
os.environ['XDG_RUNTIME_DIR'] = '/tmp/runtime-' + os.environ.get('USER', 'user')

try:
    import pygame
    print("✓ Pygame imported")
    
    pygame.init()
    print("✓ Pygame initialized")
    
    screen = pygame.display.set_mode((800, 600))
    print("✓ Display created")
    
    pygame.quit()
    print("✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")