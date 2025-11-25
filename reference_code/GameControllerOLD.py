"""
PLO8 Poker Game - Bovada-style Game Screen
Full-screen game with settings screen and poker table

To run: python graphic.py
"""

import pygame
import sys
import os
import math
import random

class PLO8:
    def __init__(self, settings):
        pygame.init()
        
        # Settings values
        self.starting_players = settings[0] # Number of players at the table
        self.starting_stack = settings[1] # Starting stack in big blinds (bb)
        self.human_in_loop = settings[2] # Include a human player
        
        # Try to launch on second monitor if available
        try:
            import ctypes
            user32 = ctypes.windll.user32
            monitor_count = user32.GetSystemMetrics(80)  # SM_CMONITORS
            
            if monitor_count > 1:
                primary_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
                os.environ['SDL_VIDEO_WINDOW_POS'] = '%d,%d' % (primary_width + 100, 100)
            else:
                os.environ['SDL_VIDEO_WINDOW_POS'] = '100,100'
        except:
            pass

        # Get display info
        display_info = pygame.display.Info()
        self.WIDTH = display_info.current_w
        self.HEIGHT = display_info.current_h - 50
        
        # Create window
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("PLO8 Training Sandbox")

        try:
            import ctypes
            hwnd = pygame.display.get_wm_info()['window']
            ctypes.windll.user32.ShowWindow(hwnd, 3)  # 3 = SW_MAXIMIZE
        except:
            pass
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Colors - Bovada style
        self.BG_COLOR = (68, 68, 68)  # Dark gray background
        self.PANEL_COLOR = (105, 105, 105)
        self.WHITE = (255, 255, 255)
        self.GRAY = (20, 20, 20)
        self.LIGHT_GRAY = (200, 200, 200)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.DARK_RED = (180, 80, 80)
        self.DARK_GRAY = (15, 15, 15)
        
        # Player seat colors (Bovada style - different colors per seat)
        self.SEAT_COLORS = [
            (100, 180, 100),  # Green
            (240, 160, 60),   # Orange  
            (255, 136, 151),  # Pink
            (80, 180, 180),   # Teal/Cyan
            (180, 100, 180),  # Purple
            (240, 200, 80),   # Yellow
            (100, 140, 200),  # Blue
            (200, 120, 100),  # Salmon
            (39, 60, 245),  # Navy Blue
        ]
        
        # Fonts
        self.title_font = pygame.font.SysFont('arial', 72, bold=True)
        self.heading_font = pygame.font.SysFont('arial', 48, bold=True)
        self.large_font = pygame.font.SysFont('arial', 36)
        self.medium_font = pygame.font.SysFont('arial', 28)
        self.small_font = pygame.font.SysFont('arial', 20)
        self.tiny_font = pygame.font.SysFont('arial', 16)
        self.stack_font = pygame.font.SysFont('arial', 24, bold=True)
        self.pot_font = pygame.font.SysFont('arial', 22, bold=True)
        
        # Hover state
        self.mouse_pos = (0, 0)
        self.hovered_slider = None
        self.hovered_toggle = None
        
        # Game data (sample data for display)
        self.players = []
        self.pot = 0
        self.community_cards = []
        self.dealer_position = 0
        self.current_player = 0
        self.init_game_data(self.starting_players, self.starting_stack)
    
    def init_game_data(self, starting_players, starting_stack):
        """Initialize sample game data for display"""
        # Sample player data - will be dynamic later
        sample_stacks = [starting_stack] * starting_players
        sample_status = ['vacant', 'vacant', 'vacant', 'vacant', 'vacant', 'vacant', 'vacant', 'vacant', 'vacant']
        for i in range(starting_players):
            sample_status[i] = 'active'

        self.players = []
        for i in range(starting_players):
            player = {
                'seat': i+1,
                'stack': sample_stacks[i],
                'bet': 0,
                'status': sample_status[i],
                'cards': [None, None, None, None],  # 4 hole cards for PLO8
                'timer': 0.7 if i == 4 else 0,  # Timer progress (0-1)
                'is_turn': i == 4,
            }
            self.players.append(player)
        
        self.pot = 0
        self.main_pot = 0
        self.dealer_position = random.randint(1, starting_players)
        print(self.dealer_position)
    
    def get_seat_positions(self):
        """
        Calculate seat positions around the rounded rectangle table.
        Returns list of positions for each seat
        """
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2 - 120  # Shifted up for bottom panel
        
        # Table dimensions
        table_width = min(self.WIDTH * 0.7, 1100)
        table_height = min(self.HEIGHT * 0.45, 380)
        
        # Define fixed positions around the table (not using angles for rectangle)
        # Positions are: [top-left, top-center-left, top-center-right, top-right, 
        #                 right, bottom-right, bottom-center, bottom-left, left]
        
        positions = []
        
        # Calculate offsets from center
        half_w = table_width // 2 + 140  # Distance from center to sides
        half_h = table_height // 2 + 120  # Distance from center to top/bottom
        
        # 9 seat positions arranged around rectangle
        seat_coords = [
            (center_x, center_y + half_h + 35, 'bottom'),                           # Seat 1
            (center_x - half_w * 0.3, center_y - half_h * 0.8, 'top'),              # Seat 2
            (center_x + half_w - 35 , center_y + half_h * 0.3, 'right-bottom'),     # Seat 3
            (center_x - half_w + 35 , center_y + half_h * 0.3, 'left-bottom'),      # Seat 4
            (center_x + half_w * 0.3, center_y - half_h * 0.8, 'top'),              # Seat 5
            (center_x - half_w * 0.6, center_y + half_h + 25, 'bottom-left'),       # Seat 6
            (center_x + half_w - 65 , center_y - half_h * 0.5, 'right-top'),        # Seat 7
            (center_x - half_w + 65, center_y - half_h * 0.5, 'left-top'),          # Seat 8
            (center_x + half_w * 0.6, center_y + half_h + 25, 'bottom-right'),      # Seat 9
        ]
        
        for i, (x, y, side) in enumerate(seat_coords[:9]):
            # Bet offset depends on which side of table
            if side == 'top':
                bet_offset = (0, 100)
            elif side == 'bottom':
                bet_offset = (0, -195)
            elif side == 'bottom-left':
                bet_offset = (70, -190)
            elif side == 'bottom-right':
                bet_offset = (-70, -190)
            elif side == 'left-top':
                bet_offset = (190, 55)
            elif side == 'left-bottom':
                bet_offset = (195, -35)
            elif side == 'right-top':
                bet_offset = (-190, 55)
            else:  # right-bottom
                bet_offset = (-195, -35)
            
            positions.append({
                'x': x,
                'y': y,
                'side': side,
                'bet_offset': bet_offset,
            })
        
        return positions
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(30)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Handle all pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_mouse_down(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_slider = None
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
    
    def handle_mouse_down(self, pos):
        """Handle mouse button down"""
        x, y = pos
    
    def render(self):
        """Main render function"""
        self.screen.fill(self.BG_COLOR)
                # Draw the rounded rectangle table
        self.draw_poker_table()
        
        # Draw pot information in center
        self.draw_pot_info()
        
        # Draw all players
        self.draw_players()
        
        # Draw community cards (if any)
        self.draw_community_cards()
        
        # Draw bottom control panel
        self.draw_control_panel()

        pygame.display.flip()
    
    def draw_control_panel(self):
        """Draw the bottom control panel for user actions"""
        panel_height = 230
        panel_y = self.HEIGHT - panel_height
        
        # Panel background
        pygame.draw.rect(self.screen, (50, 50, 50),
                        (0, panel_y, self.WIDTH, panel_height))
        pygame.draw.line(self.screen, (80, 80, 80),
                        (0, panel_y), (self.WIDTH, panel_y), 3)
        
        # Action buttons
        button_y = panel_y + 40
        button_height = 70
        button_spacing = 20
        
        # Calculate button positions (centered)
        buttons = [
            ("FOLD", (180, 60, 60), (220, 80, 80)),
            ("CHECK", (100, 100, 100), (130, 130, 130)),
            ("CALL", (60, 140, 60), (80, 180, 80)),
            ("RAISE", (60, 120, 180), (80, 150, 220)),
            ("ALL IN", (180, 140, 60), (220, 180, 80)),
        ]
        
        total_width = len(buttons) * 160 + (len(buttons) - 1) * button_spacing
        start_x = (self.WIDTH - total_width) // 2
        
        for i, (text, color, hover_color) in enumerate(buttons):
            btn_x = start_x + i * (160 + button_spacing)
            #self.draw_button(btn_x, button_y, 160, button_height, text, color, hover_color, button_id=f"action_{text.lower()}")
        
        # Info text
        info_font = pygame.font.SysFont('arial', 24)
        info_text = info_font.render("Your turn to act", True, self.LIGHT_GRAY)
        info_rect = info_text.get_rect(center=(self.WIDTH // 2, panel_y + 140))
        self.screen.blit(info_text, info_rect)
    
    def draw_poker_table(self):
        """Draw the rounded rectangle poker table"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2 - 120  # Shifted up for bottom panel
        
        # Table dimensions
        table_width = min(self.WIDTH * 0.65, 1000)
        table_height = min(self.HEIGHT * 0.4, 340)
        
        # Corner radius for rounded rectangle (very rounded)
        corner_radius = table_height // 2  # Makes ends fully rounded
        
        # Draw table border (outer edge)
        outer_rect = pygame.Rect(
            center_x - table_width//2 - 10, 
            center_y - table_height//2 - 10,
            table_width + 20, 
            table_height + 20
        )
        pygame.draw.rect(self.screen, self.PANEL_COLOR, outer_rect, border_radius=corner_radius + 8)
        
        # Draw table felt (inner)
        inner_rect = pygame.Rect(
            center_x - table_width//2, 
            center_y - table_height//2,
            table_width, 
            table_height
        )
        pygame.draw.rect(self.screen, self.BG_COLOR, inner_rect, border_radius=corner_radius)
    
    def draw_pot_info(self):
        """Draw pot information in center of table"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2 - 120 - 30  # Shifted up for bottom panel
        
        # Total pot
        pot_text = f"Total pot: {self.pot:,} bb"
        pot_surface = self.pot_font.render(pot_text, True, self.WHITE)
        pot_rect = pot_surface.get_rect(center=(center_x, center_y))
        
        # Background for pot info
        bg_rect = pot_rect.inflate(30, 10)
        pygame.draw.rect(self.screen, (60, 60, 60), bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, (90, 90, 90), bg_rect, 1, border_radius=5)
        self.screen.blit(pot_surface, pot_rect)
        
        # Main pot (if different)
        if self.main_pot and self.main_pot != self.pot:
            main_text = f"Main pot: {self.main_pot:,} bb"
            main_surface = self.small_font.render(main_text, True, self.WHITE)
            main_rect = main_surface.get_rect(center=(center_x, center_y + 35))
            
            bg_rect = main_rect.inflate(20, 6)
            pygame.draw.rect(self.screen, (60, 60, 60), bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, (90, 90, 90), bg_rect, 1, border_radius=5)
            self.screen.blit(main_surface, main_rect)
    
    def draw_players(self):
        """Draw all player seats"""
        positions = self.get_seat_positions()
        
        for i, pos in enumerate(positions):
            if i < len(self.players):
                player = self.players[i]
                self.draw_player_seat(pos, player, i)
            else:
                player = {
                    'status': 'vacant',
                }
                self.draw_vacant_seat(pos['x'], pos['y'])
            
    
    def draw_player_seat(self, pos, player, seat_index):
        """Draw a single player seat with cards, stack, and bet"""
        x, y = pos['x'], pos['y']
        side = pos['side']
        
        # Determine if cards should be above or below the info box
        cards_above = side
        
        if player['status'] == 'vacant':
            self.draw_vacant_seat(x, y)
            return
        
        # Draw cards first (so they appear behind the info box)
        card_x = x - 134  # Adjusted for larger cards
        if cards_above:
            card_y = y - 130  # More space for larger cards
        else:
            card_y = y + 64
        self.draw_hole_cards(card_x, card_y, player)
        
        # Draw player info box (stack + seat number)
        self.draw_player_info_box(x, y, player, seat_index)
        
        # Draw bet amount if player has bet
        if player['bet'] > 0:
            bet_x = x + pos['bet_offset'][0]
            bet_y = y + pos['bet_offset'][1]
            self.draw_bet_chip(bet_x, bet_y, player['bet'])
        
    
    def draw_vacant_seat(self, x, y):
        """Draw a vacant seat indicator"""
        # Draw circle with person icon - doubled size
        radius = 50
        pygame.draw.circle(self.screen, (60, 60, 60), (int(x), int(y)), radius)
        
        # Draw simple person icon - doubled size
        # Head
        pygame.draw.circle(self.screen, (140, 140, 140), (int(x), int(y) - 16), 20)
        # Body
        pygame.draw.ellipse(self.screen, (140, 140, 140), 
                           (int(x) - 36, int(y) + 8, 72, 40))
        pygame.draw.circle(self.screen, (100, 100, 100), (int(x), int(y)), radius, 3)
    
    def draw_hole_cards(self, x, y, player):
        card_width = 70
        card_height = 100
        card_spacing = -4
        
        # Draw 2 face-down cards
        for i in range(4):
            card_x = x + i * (card_width + card_spacing)
            
            # Card background (dark)
            pygame.draw.rect(self.screen, (30, 30, 30),
                           (card_x, y, card_width, card_height),
                           border_radius=8)
            
            # Card border
            pygame.draw.rect(self.screen, self.DARK_RED,
                           (card_x, y, card_width, card_height),
                           3, border_radius=8)
            
            # Card back design (simple "B" logo like Bovada) - larger font
            logo_font = pygame.font.SysFont('arial', 56, bold=False)
            logo = logo_font.render("?", True, self.DARK_RED)
            logo_rect = logo.get_rect(center=(card_x + card_width//2, y + card_height//2))
            self.screen.blit(logo, logo_rect)
    
    def draw_player_info_box(self, x, y, player, seat_index):
        """Draw the player info box with seat number and stack - doubled size"""
        # Box dimensions - doubled
        box_width = 260
        box_height = 84
        
        # Seat color
        seat_color = self.SEAT_COLORS[seat_index % len(self.SEAT_COLORS)]
        bg_color = (240, 240, 235)  # Light cream background like Bovada
        
        # Draw main box background
        box_x = x - box_width // 2
        box_y = y - box_height // 2
        
        pygame.draw.rect(self.screen, bg_color,
                        (box_x, box_y, box_width, box_height),
                        border_radius=box_height // 2)
        
        # Draw seat number circle on left - doubled size
        circle_radius = 36
        circle_x = box_x + circle_radius + 10
        circle_y = y
        
        pygame.draw.circle(self.screen, seat_color, (int(circle_x), int(circle_y)), circle_radius)
        
        # Seat number text - simple 1-9 numbering
        seat_num = str(seat_index + 1)
        
        num_font = pygame.font.SysFont('arial', 28, bold=True)
        num_text = num_font.render(seat_num, True, self.WHITE)
        num_rect = num_text.get_rect(center=(circle_x, circle_y))
        self.screen.blit(num_text, num_rect)
        
        # Stack amount text - larger font
        stack_str = f"{player['stack']:,}"
        text_color = self.DARK_GRAY if player['status'] != 'sitting_out' else self.WHITE
        stack_font = pygame.font.SysFont('arial', 40, bold=True)
        stack_text = stack_font.render(stack_str, True, text_color)
        stack_rect = stack_text.get_rect(midleft=(circle_x + circle_radius + 15, y))
        self.screen.blit(stack_text, stack_rect)
    
    def draw_bet_chip(self, x, y, amount):
        # text setup
        bb_font = pygame.font.SysFont('arial', 32, bold=True)
        bb_text = bb_font.render(f"{amount} bb", True, self.WHITE)
        bb_rect = bb_text.get_rect(center=(x, y))

        padding_x = 8
        padding_y = 4
        box_rect = pygame.Rect(
            bb_rect.x - padding_x,
            bb_rect.y - padding_y,
            bb_rect.width + padding_x*2,
            bb_rect.height + padding_y*2
        )
        box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(
            box_surf,
            (0, 0, 0, 120),
            (0, 0, box_rect.width, box_rect.height),
            border_radius=box_rect.height // 2  # pill shape
        )

        # Blit box + text
        self.screen.blit(box_surf, (box_rect.x, box_rect.y))
        self.screen.blit(bb_text, bb_rect)
    
    def draw_community_cards(self):
        """Draw community cards in center of table"""
        # For now, no community cards - can be added later
        pass

game = PLO8([9,20,True])
game.run()