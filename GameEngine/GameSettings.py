"""
PLO8 Poker Engine - Configuration Settings
Central configuration for colors, sizes, and game settings
"""

import pygame

# Window settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
FPS = 60
TITLE = "PLO8 Poker Trainer"

# Colors (RGB)
class Colors:
    # Table colors
    TABLE_GREEN = (53, 101, 77)
    TABLE_FELT = (35, 85, 60)
    TABLE_EDGE = (101, 67, 33)
    
    # UI colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (64, 64, 64)
    
    # Card colors
    CARD_WHITE = (240, 240, 240)
    CARD_BACK = (50, 80, 180)
    
    # Suit colors
    RED = (220, 20, 60)
    DARK_RED = (180, 0, 0)
    
    # Chip colors
    CHIP_WHITE = (255, 255, 255)
    CHIP_RED = (220, 20, 60)
    CHIP_GREEN = (34, 139, 34)
    CHIP_BLUE = (30, 144, 255)
    CHIP_BLACK = (32, 32, 32)
    
    # UI accent colors
    GOLD = (255, 215, 0)
    BUTTON_NORMAL = (70, 130, 180)
    BUTTON_HOVER = (100, 149, 237)
    BUTTON_ACTIVE = (65, 105, 225)
    BUTTON_DISABLED = (105, 105, 105)
    
    # Action colors
    ACTION_BET = (34, 139, 34)
    ACTION_RAISE = (255, 140, 0)
    ACTION_CALL = (70, 130, 180)
    ACTION_FOLD = (178, 34, 34)
    ACTION_CHECK = (128, 128, 128)
    
    # Alert colors
    SUCCESS = (46, 204, 113)
    WARNING = (241, 196, 15)
    ERROR = (231, 76, 60)
    INFO = (52, 152, 219)

# Card settings
CARD_WIDTH = 80
CARD_HEIGHT = 112
CARD_RADIUS = 8
CARD_SPACING = 10

# Player settings
MAX_PLAYERS = 9
PLAYER_BOX_WIDTH = 180
PLAYER_BOX_HEIGHT = 120
PLAYER_NAME_HEIGHT = 25

# Table settings
TABLE_CENTER_X = WINDOW_WIDTH // 2
TABLE_CENTER_Y = WINDOW_HEIGHT // 2
TABLE_RADIUS_X = 500
TABLE_RADIUS_Y = 280

# Player positions (angles in degrees for elliptical layout)
PLAYER_POSITIONS = {
    2: [270, 90],  # Heads up
    3: [270, 30, 150],
    4: [270, 0, 90, 180],
    5: [270, 340, 50, 130, 230],
    6: [270, 330, 30, 90, 150, 210],
    7: [270, 320, 20, 70, 110, 160, 200],
    8: [270, 315, 0, 45, 90, 135, 180, 225],
    9: [270, 310, 350, 30, 70, 110, 150, 190, 230]
}

# Font settings
FONT_NAME = 'arial'
FONT_SIZE_LARGE = 32
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 18
FONT_SIZE_TINY = 14

# Animation settings
CARD_DEAL_SPEED = 400  # pixels per second
CHIP_MOVE_SPEED = 300
FADE_SPEED = 5

# Game settings
DEFAULT_SMALL_BLIND = 5
DEFAULT_BIG_BLIND = 10
DEFAULT_STARTING_STACK = 1000
MIN_BUY_IN = 100
MAX_BUY_IN = 10000

# Button settings
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 50
BUTTON_RADIUS = 10
BUTTON_SPACING = 15

# Pot display
POT_DISPLAY_Y = 200
COMMUNITY_CARDS_Y = 350

# Action panel (bottom of screen)
ACTION_PANEL_HEIGHT = 150
ACTION_PANEL_Y = WINDOW_HEIGHT - ACTION_PANEL_HEIGHT

# Dealer button
DEALER_BUTTON_SIZE = 30

# Betting slider
SLIDER_WIDTH = 300
SLIDER_HEIGHT = 20
SLIDER_HANDLE_RADIUS = 12

# Timings (milliseconds)
PLAYER_THINK_TIME = 30000  # 30 seconds max
AI_THINK_TIME_MIN = 500  # Minimum time for AI to "think"
AI_THINK_TIME_MAX = 2000  # Maximum time for AI to "think"

# Z-ordering (drawing layers)
LAYER_TABLE = 0
LAYER_POTS = 1
LAYER_CARDS = 2
LAYER_PLAYERS = 3
LAYER_UI = 4
LAYER_POPUP = 5