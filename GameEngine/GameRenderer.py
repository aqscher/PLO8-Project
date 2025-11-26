"""
GameRenderer.py - Pygame rendering for PLO8 poker game
Handles all visual display and UI input collection
Includes card rendering functionality
"""

import pygame
import sys
import os
from typing import Optional


class CardRenderer:
    """Renders playing cards using pygame - supports string format like 'HA', 'D10', 'CK'"""
    SUIT_SYMBOLS = {
        'H': '♥',  # Hearts
        'D': '♦',  # Diamonds
        'C': '♣',  # Clubs
        'S': '♠'   # Spades
    }

    RED_SUITS = {'H'}
    GREEN_SUITS = {'C'}
    BLUE_SUITS = {'D'}

    # Rank display characters
    RANK_DISPLAY = {
        '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
        '7': '7', '8': '8', '9': '9', '10': '10',
        'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'
    }
    
    def __init__(self, card_width: int = 70, card_height: int = 100):
        """Initialize card renderer"""
        self.card_width = card_width
        self.card_height = card_height
        self.card_radius = 8
        
        # Initialize fonts
        pygame.font.init()
        self.rank_font = pygame.font.SysFont('arial', 42, bold=True)
        self.suit_font = pygame.font.SysFont('arial', 42)
        
        # Colors
        self.WHITE = (250, 250, 250)
        self.BLACK = (0, 0, 0)
        self.GREY = (58, 58, 58)
        self.RED = (220, 20, 60)
        self.BLUE = (0, 135, 202)
        self.GREEN = (50, 159, 40)
        self.CARD_BACK_COLOR = (30, 30, 30)
        self.CARD_BACK_BORDER = (180, 80, 80)
    
    def render_card(self, card, face_up: bool = True) -> pygame.Surface:
        """
        Render a card
        
        Args:
            card: Card string in format 'HA' (Hearts Ace), 'D10' (Diamonds 10), etc.
                  or None for card back
            face_up: Whether to show the face or back
        
        Returns:
            pygame.Surface of the rendered card
        """
        # Create card surface
        card_surface = pygame.Surface((self.card_width, self.card_height), pygame.SRCALPHA)
        
        if not face_up:
            # Draw card back
            self._draw_card_back(card_surface)
        else:
            self._draw_card_face(card_surface, card)
        
        # Draw border
        border_color = self.CARD_BACK_BORDER if not face_up else self.BLACK
        pygame.draw.rect(card_surface, border_color, 
                        (0, 0, self.card_width, self.card_height), 4, border_radius=self.card_radius)
        
        return card_surface
    
    def _parse_card(self, card_str: str) -> tuple:
        """
        Parse card string like 'HA', 'D10', 'CK' into suit and rank
        
        Args:
            card_str: Card string (e.g., 'HA', 'D10', 'S3')
        
        Returns:
            tuple: (suit_char, rank_str) e.g., ('H', 'A') or ('D', '10')
        """
        if not card_str or len(card_str) < 2:
            return None, None
        
        suit_char = card_str[0]  # First character is suit (H, D, C, S)
        rank_str = card_str[1:]  # Rest is rank (A, 2-10, J, Q, K)
        
        return suit_char, rank_str
    
    def _draw_card_face(self, surface: pygame.Surface, card_str: str):
        """Draw the face of a card from string format like 'HA', 'D10', 'CK'"""
        # Parse card string
        suit_char, rank_str = self._parse_card(card_str)
        
        # Determine color
        is_red = suit_char in self.RED_SUITS
        is_blue = suit_char in self.BLUE_SUITS
        is_green = suit_char in self.GREEN_SUITS
        color = self.GREY
        if is_red:
            color = self.RED
        elif is_blue:
            color = self.BLUE
        elif is_green:
            color = self.GREEN

        # Draw card face
        pygame.draw.rect(
            surface,
            color,
            surface.get_rect(),
            border_radius=self.card_radius
        )
        
        # Get symbols
        rank_display = self.RANK_DISPLAY.get(rank_str, rank_str)
        suit_symbol = self.SUIT_SYMBOLS.get(suit_char, '?')
        
        # Draw rank in top-left
        rank_text = self.rank_font.render(rank_display, True, self.WHITE)
        surface.blit(rank_text, (10, 4),)
        
        # Draw large suit symbol in center
        large_suit = self.suit_font.render(suit_symbol, True, self.WHITE)
        suit_x = (self.card_width - large_suit.get_width() + 26) // 2
        suit_y = (self.card_height - large_suit.get_height() + 30) // 2
        surface.blit(large_suit, (suit_x, suit_y))
    
    def _draw_card_back(self, surface: pygame.Surface):
        """Draw the back of a card"""
        pygame.draw.rect(
            surface,
            (*self.CARD_BACK_COLOR, 255),  # solid color
            surface.get_rect(),
            border_radius=self.card_radius
        )
        
        # Card back design (simple "?" like current design)
        logo_font = pygame.font.SysFont('arial', 56, bold=False)
        logo = logo_font.render("?", True, self.CARD_BACK_BORDER)
        logo_rect = logo.get_rect(center=(self.card_width//2, self.card_height//2))
        surface.blit(logo, logo_rect)


class Render:
    def __init__(self, settings):
        """Initialize pygame and rendering components"""
        pygame.init()
        
        self.settings = settings
        self.num_players = settings[0]
        self.starting_stack = settings[1]
        self.human_in_loop = settings[2]
        
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
        
        # Initialize card renderer
        self.card_renderer = CardRenderer(card_width=70, card_height=100)
        
        # Colors
        self.BG_COLOR = (68, 68, 68)
        self.PANEL_COLOR = (105, 105, 105)
        self.WHITE = (255, 255, 255)
        self.GRAY = (20, 20, 20)
        self.LIGHT_GRAY = (200, 200, 200)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.DARK_RED = (180, 80, 80)
        self.DARK_GRAY = (15, 15, 15)
        
        # Player seat colors
        self.SEAT_COLORS = [
            (100, 180, 100),  # Green
            (240, 160, 60),   # Orange  
            (255, 136, 151),  # Pink
            (80, 180, 180),   # Teal/Cyan
            (180, 100, 180),  # Purple
            (240, 200, 80),   # Yellow
            (100, 140, 200),  # Blue
            (200, 120, 100),  # Salmon
            (39, 60, 245),    # Navy Blue
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
        
        # Mouse state
        self.mouse_pos = (0, 0)
        
        # Button bounds for click detection
        self.button_bounds = {}

        self.perspective = 0  # 0 = all cards, 1-9 = that player's cards only
        self.perspective_slider_bounds = None
        self.dragging_perspective = False
    
    def get_user_input(self):
        """
        Handle pygame events and return user actions
        Returns: dict with action type or None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {'type': 'quit'}
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return {'type': 'quit'}
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check perspective slider first
                    if self._check_perspective_slider_click(event.pos):
                        self.dragging_perspective = True
                    else:
                        action = self._handle_mouse_click(event.pos)
                        if action:
                            return action
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging_perspective = False
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                if self.dragging_perspective:
                    self._handle_perspective_drag(event.pos)
        
        return None
    
    def _handle_mouse_click(self, pos):
        """Check if any button was clicked and return corresponding action"""
        x, y = pos
        
        for button_id, bounds in self.button_bounds.items():
            bx, by, bw, bh = bounds
            if bx <= x <= bx + bw and by <= y <= by + bh:
                # Button was clicked
                if button_id.startswith('action_'):
                    action_type = button_id.replace('action_', '')
                    return {'type': 'action', 'action': action_type}
                else:
                    return {'type': button_id}
        
        return None
    
    def _check_perspective_slider_click(self, pos):
        """Check if perspective slider was clicked"""
        if not self.perspective_slider_bounds:
            return False
        
        x, y = pos
        sx, sy, width, height = self.perspective_slider_bounds
        
        # Check if click is on slider track or handle
        return sx <= x <= sx + width and sy - 15 <= y <= sy + 15
    
    def _handle_perspective_drag(self, pos):
        """Update perspective value based on mouse position"""
        if not self.perspective_slider_bounds:
            return
        
        x, y = pos
        sx, sy, width, height = self.perspective_slider_bounds
        
        # Clamp mouse position to slider bounds
        x = max(sx, min(x, sx + width))
        
        # Calculate ratio
        ratio = (x - sx) / width
        
        # Calculate new value (0-9)
        new_val = int(ratio * 9)
        
        self.perspective = max(0, min(new_val, 9))
    
    def render(self, game_state):
        """
        Main render function - draws the entire game based on state
        
        Args:
            game_state: dict containing all game information to display
                {
                    'players': list of player dicts,
                    'pot': int,
                    'main_pot': int,
                    'community_cards': list,
                    'dealer_position': int,
                    'current_player': int,
                }
        """
        self.screen.fill(self.BG_COLOR)
        
        # Draw table
        self.draw_poker_table()
        
        # Draw pot info
        self.draw_pot_info(game_state['pot'], game_state.get('main_pot', 0))
        
        # Draw players
        self.draw_players(game_state)
        
        # Draw community cards
        self.draw_community_cards(game_state.get('community_cards', []))
        
        # Draw control panel
        self.draw_control_panel()
        
        # Update display
        pygame.display.flip()
        self.clock.tick(30)  # 30 FPS
    
    def get_seat_positions(self):
        """Calculate seat positions around the table"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2 - 120
        
        table_width = min(self.WIDTH * 0.7, 1100)
        table_height = min(self.HEIGHT * 0.45, 380)
        
        positions = []
        
        half_w = table_width // 2 + 140
        half_h = table_height // 2 + 120
        
        # 9 seat positions arranged around rectangle
        seat_coords = [
            (center_x, center_y + half_h + 35, 'bottom'),
            (center_x - half_w * 0.6, center_y + half_h + 25, 'bottom-left'),
            (center_x - half_w + 35, center_y + half_h * 0.3, 'left-bottom'),
            (center_x - half_w + 65, center_y - half_h * 0.5, 'left-top'),
            (center_x - half_w * 0.3, center_y - half_h * 0.8, 'top'),
            (center_x + half_w * 0.3, center_y - half_h * 0.8, 'top'),
            (center_x + half_w - 65, center_y - half_h * 0.5, 'right-top'),
            (center_x + half_w - 35, center_y + half_h * 0.3, 'right-bottom'),
            (center_x + half_w * 0.6, center_y + half_h + 25, 'bottom-right'),
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
    
    def draw_poker_table(self):
        """Draw the rounded rectangle poker table"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2 - 120
        
        table_width = min(self.WIDTH * 0.65, 1000)
        table_height = min(self.HEIGHT * 0.4, 340)
        
        corner_radius = table_height // 2
        
        # Outer border
        outer_rect = pygame.Rect(
            center_x - table_width//2 - 10, 
            center_y - table_height//2 - 10,
            table_width + 20, 
            table_height + 20
        )
        pygame.draw.rect(self.screen, self.PANEL_COLOR, outer_rect, border_radius=corner_radius + 8)
        
        # Inner felt
        inner_rect = pygame.Rect(
            center_x - table_width//2, 
            center_y - table_height//2,
            table_width, 
            table_height
        )
        pygame.draw.rect(self.screen, self.BG_COLOR, inner_rect, border_radius=corner_radius)
    
    def draw_pot_info(self, pot, main_pot):
        """Draw pot information in center of table"""
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2 - 120 - 30
        
        # Total pot
        pot_text = f"Total pot: {pot:,} bb"
        pot_surface = self.pot_font.render(pot_text, True, self.WHITE)
        pot_rect = pot_surface.get_rect(center=(center_x, center_y))
        
        # Background
        bg_rect = pot_rect.inflate(30, 10)
        pygame.draw.rect(self.screen, (60, 60, 60), bg_rect, border_radius=5)
        pygame.draw.rect(self.screen, (90, 90, 90), bg_rect, 1, border_radius=5)
        self.screen.blit(pot_surface, pot_rect)
        
        # Main pot (if different)
        if main_pot and main_pot != pot:
            main_text = f"Main pot: {main_pot:,} bb"
            main_surface = self.small_font.render(main_text, True, self.WHITE)
            main_rect = main_surface.get_rect(center=(center_x, center_y + 35))
            
            bg_rect = main_rect.inflate(20, 6)
            pygame.draw.rect(self.screen, (60, 60, 60), bg_rect, border_radius=5)
            pygame.draw.rect(self.screen, (90, 90, 90), bg_rect, 1, border_radius=5)
            self.screen.blit(main_surface, main_rect)
    
    def draw_players(self, game_state):
        players = game_state.get('players')
        positions = self.get_seat_positions()
        for i, pos in enumerate(positions):
            for player in players:
                if player['seat'] == i+1:
                    """Draw a single player seat with cards, stack, and bet"""
                    x, y = pos['x'], pos['y']
                    side = pos['side']
                    # Draw cards
                    card_x = x - 134
                    if side:
                        card_y = y - 130
                    else:
                        card_y = y + 64
                    self.draw_hole_cards(card_x, card_y, player)
                    
                    # Draw player info box
                    self.draw_player_info_box(x, y, player, i)

                    # Draw dealer coin
                    if game_state.get('dealer_position') == player['seat']-1:
                        self.draw_dealer_coin(x - 130, y - 30)
                    
                    # Draw bet
                    if player['bet'] > 0:
                        bet_x = x + pos['bet_offset'][0]
                        bet_y = y + pos['bet_offset'][1]
                        self.draw_bet_chip(bet_x, bet_y, player['bet'])

            if player['status'] == 'vacant':
                self.draw_vacant_seat(x, y)

    def draw_dealer_coin(self, x, y):
        """Draw the dealer button coin"""
        # Coin dimensions
        coin_radius = 30
        
        # Outer circle (border) - white
        pygame.draw.circle(self.screen, self.DARK_GRAY, (int(x), int(y)), coin_radius)
        
        # Inner circle - black background
        pygame.draw.circle(self.screen, self.WHITE, (int(x), int(y)), coin_radius - 3)
        
        # Draw "D" for dealer
        dealer_font = pygame.font.SysFont('arial', 32, bold=True)
        dealer_text = dealer_font.render("D", True, self.DARK_GRAY)
        dealer_rect = dealer_text.get_rect(center=(x, y))
        self.screen.blit(dealer_text, dealer_rect)
    
    def draw_vacant_seat(self, x, y):
        """Draw a vacant seat indicator"""
        radius = 50
        pygame.draw.circle(self.screen, (60, 60, 60), (int(x), int(y)), radius)
        
        # Person icon
        pygame.draw.circle(self.screen, (140, 140, 140), (int(x), int(y) - 16), 20)
        pygame.draw.ellipse(self.screen, (140, 140, 140), 
                           (int(x) - 36, int(y) + 8, 72, 40))
        pygame.draw.circle(self.screen, (100, 100, 100), (int(x), int(y)), radius, 3)
    
    def draw_hole_cards(self, x, y, player):
        """Draw player's hole cards - using CardRenderer for string format cards like 'HA', 'D10'"""
        card_width = 70
        card_height = 100
        card_spacing = -4
        
        cards = player.get('cards', [None, None, None, None])
        
        # Determine if cards should be face up based on perspective setting
        # 0 = all face up, 1-9 = only that player's cards face up
        should_show_face_up = (self.perspective == 0) or (self.perspective == player['seat'])
        
        for i in range(4):
            card_x = x + i * (card_width + card_spacing)
            
            # Check if we have a card string (e.g., 'HA', 'D10', 'CK')
            card = cards[i] if i < len(cards) else None
            has_card = card is not None and isinstance(card, str) and len(card) >= 2
            
            if has_card and should_show_face_up:
                # Use CardRenderer to draw actual card from string
                card_surface = self.card_renderer.render_card(card, face_up=True)
                self.screen.blit(card_surface, (card_x, y))
            else:
                # Draw card back (placeholder)
                card_surface = self.card_renderer.render_card(None, face_up=False)
                self.screen.blit(card_surface, (card_x, y))
    
    def draw_player_info_box(self, x, y, player, seat_index):
        """Draw player info box with seat number and stack"""
        box_width = 260
        box_height = 84
        
        seat_color = self.SEAT_COLORS[seat_index % len(self.SEAT_COLORS)]
        bg_color = (240, 240, 235)
        
        box_x = x - box_width // 2
        box_y = y - box_height // 2
        
        # Background
        pygame.draw.rect(self.screen, bg_color,
                        (box_x, box_y, box_width, box_height),
                        border_radius=box_height // 2)
        
        # Seat number circle
        circle_radius = 36
        circle_x = box_x + circle_radius + 10
        circle_y = y
        
        pygame.draw.circle(self.screen, seat_color, (int(circle_x), int(circle_y)), circle_radius)
        
        # Seat number
        seat_num = str(seat_index + 1)
        num_font = pygame.font.SysFont('arial', 28, bold=True)
        num_text = num_font.render(seat_num, True, self.WHITE)
        num_rect = num_text.get_rect(center=(circle_x, circle_y))
        self.screen.blit(num_text, num_rect)
        
        # Stack amount
        stack_str = f"{player['stack']:,}"
        text_color = self.DARK_GRAY if player['status'] != 'sitting_out' else self.WHITE
        stack_font = pygame.font.SysFont('arial', 40, bold=True)
        stack_text = stack_font.render(stack_str, True, text_color)
        stack_rect = stack_text.get_rect(midleft=(circle_x + circle_radius + 15, y))
        self.screen.blit(stack_text, stack_rect)
    
    def draw_bet_chip(self, x, y, amount):
        """Draw bet amount chip"""
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
            border_radius=box_rect.height // 2
        )

        self.screen.blit(box_surf, (box_rect.x, box_rect.y))
        self.screen.blit(bb_text, bb_rect)
    
    def draw_community_cards(self, community_cards):
        """Draw community cards in center of table - supports string format like 'HA', 'D10'"""
        if not community_cards:
            return
        
        # Calculate position for community cards (center of table, slightly below pot)
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 2 - 120 + 40
        
        card_width = 70
        card_spacing = 10
        
        # Calculate starting x to center the cards
        total_width = len(community_cards) * card_width + (len(community_cards) - 1) * card_spacing
        start_x = center_x - total_width // 2
        
        # Draw each community card
        for i, card in enumerate(community_cards):
            card_x = start_x + i * (card_width + card_spacing)
            
            # Check if we have a card string (e.g., 'HA', 'D10', 'CK')
            has_card = card is not None and isinstance(card, str) and len(card) >= 2
            
            if has_card:
                card_surface = self.card_renderer.render_card(card, face_up=True)
                self.screen.blit(card_surface, (card_x, center_y))
    
    def draw_control_panel(self):
        """Draw the bottom control panel with action buttons and perspective slider"""
        panel_height = 230
        panel_y = self.HEIGHT - panel_height
        
        # Panel background
        pygame.draw.rect(self.screen, (50, 50, 50),
                        (0, panel_y, self.WIDTH, panel_height))
        pygame.draw.line(self.screen, (80, 80, 80),
                        (0, panel_y), (self.WIDTH, panel_y), 3)
        
        # Draw perspective slider (bottom left)
        self.draw_perspective_slider(panel_y)
        
        # Action buttons
        button_y = panel_y + 40
        button_height = 70
        button_spacing = 20
        
        # 5 Allowed Actions at any decision point in PLO8
        buttons = [
            ("CHECK / FOLD", (108, 18, 18), (158, 68, 68), "check/fold"),
            ("CALL / BET MIN", (108, 59, 18), (158, 109, 68), "call/minbet"),
            ("BET 1/2 POT", (108, 108, 18), (158, 158, 68), "bet1/2pot"),
            ("BET 3/4 POT", (60, 108, 18), (110, 158, 68), "bet3/4pot"),
            ("BET POT", (14, 108, 18), (74, 158, 68), "betpot"),
        ]
        
        total_width = len(buttons) * 250 + (len(buttons) - 1) * button_spacing
        start_x = (self.WIDTH - total_width) // 2
        
        # Clear button bounds
        self.button_bounds = {}
        
        for i, (text, color, hover_color, action_id) in enumerate(buttons):
            btn_x = start_x + i * (250 + button_spacing)
            self.draw_button(btn_x, button_y, 250, button_height, 
                           text, color, hover_color, f"action_{action_id}")
        
        # Info text
        info_font = pygame.font.SysFont('arial', 24)
        info_text = info_font.render("Your turn to act", True, self.LIGHT_GRAY)
        info_rect = info_text.get_rect(center=(self.WIDTH // 2, panel_y + 140))
        self.screen.blit(info_text, info_rect)
    
    def draw_perspective_slider(self, panel_y):
        """Draw the perspective slider in bottom left corner"""
        # Slider position (bottom left corner)
        slider_x = 40
        slider_y = panel_y + 160
        slider_width = 250
        slider_height = 8
        
        # Store bounds for interaction
        self.perspective_slider_bounds = (slider_x, slider_y, slider_width, slider_height)
        
        # Label
        label_font = pygame.font.SysFont('arial', 20, bold=True)
        label_text = label_font.render("Perspective", True, self.WHITE)
        self.screen.blit(label_text, (slider_x + 80, slider_y - 30))
        
        # Draw track
        pygame.draw.rect(self.screen, (100, 100, 100),
                        (slider_x, slider_y, slider_width, slider_height),
                        border_radius=4)
        
        # Calculate handle position (0-9 values)
        ratio = self.perspective / 9
        handle_x = slider_x + int(ratio * slider_width)
        handle_y = slider_y + slider_height // 2
        handle_radius = 12
        
        # Draw handle
        handle_color = (150, 150, 150) if self.dragging_perspective else self.WHITE
        pygame.draw.circle(self.screen, handle_color, (handle_x, handle_y), handle_radius)
        pygame.draw.circle(self.screen, (80, 80, 80), (handle_x, handle_y), handle_radius, 2)
        
        # Value display
        value_font = pygame.font.SysFont('arial', 18)
        if self.perspective == 0:
            value_str = "All Cards"
        else:
            value_str = f"Player {self.perspective}"
        value_text = value_font.render(value_str, True, self.LIGHT_GRAY)
        self.screen.blit(value_text, (slider_x + slider_width + 16, slider_y - 8))
    
    def draw_button(self, x, y, w, h, text, color, hover_color, button_id):
        """Draw a button and track its bounds for click detection"""
        # Store bounds for click detection
        self.button_bounds[button_id] = (x, y, w, h)
        
        # Check hover
        mx, my = self.mouse_pos
        hovered = (x <= mx <= x + w and y <= my <= y + h)
        
        btn_color = hover_color if hovered else color
        
        # Draw button
        pygame.draw.rect(self.screen, btn_color, (x, y, w, h), border_radius=0)
        pygame.draw.rect(self.screen, self.WHITE, (x, y, w, h), 3, border_radius=0)
        
        # Draw text
        label = self.large_font.render(text, True, self.WHITE)
        label_rect = label.get_rect(center=(x + w//2, y + h//2))
        self.screen.blit(label, label_rect)
    
    def cleanup(self):
        """Cleanup pygame resources"""
        pygame.quit()
