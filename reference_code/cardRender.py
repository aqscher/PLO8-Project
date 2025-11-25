"""
PLO8 Poker Engine - Card Renderer
Renders playing cards with pygame
"""

import pygame
from typing import Tuple, Optional
import math


class CardRenderer:
    """Renders playing cards using pygame"""
    
    # Suit symbols
    SUIT_SYMBOLS = {
        0: '♣',  # Clubs
        1: '♦',  # Diamonds
        2: '♥',  # Hearts
        3: '♠'   # Spades
    }
    
    RANK_CHARS = {
        2: '2', 3: '3', 4: '4', 5: '5', 6: '6',
        7: '7', 8: '8', 9: '9', 10: '10',
        11: 'J', 12: 'Q', 13: 'K', 14: 'A'
    }
    
    def __init__(self, card_width: int = 80, card_height: int = 112):
        """Initialize card renderer"""
        self.card_width = card_width
        self.card_height = card_height
        self.card_radius = 8
        
        # Initialize fonts
        pygame.font.init()
        self.rank_font = pygame.font.SysFont('arial', 28, bold=True)
        self.suit_font = pygame.font.SysFont('arial', 36)
        self.mini_font = pygame.font.SysFont('arial', 16, bold=True)
        
        # Colors
        self.WHITE = (240, 240, 240)
        self.BLACK = (0, 0, 0)
        self.RED = (220, 20, 60)
        self.CARD_BACK_COLOR = (50, 80, 180)
        self.CARD_BACK_PATTERN = (70, 100, 200)
    
    def render_card(self, card, x: int, y: int, face_up: bool = True) -> pygame.Surface:
        """
        Render a card at the given position
        
        Args:
            card: Card object to render
            x: X position
            y: Y position
            face_up: Whether to show the face or back
        
        Returns:
            pygame.Surface of the rendered card
        """
        # Create card surface
        card_surface = pygame.Surface((self.card_width, self.card_height))
        card_surface.fill(self.WHITE)
        
        if not face_up:
            # Draw card back
            self._draw_card_back(card_surface)
        else:
            # Draw card face
            self._draw_card_face(card_surface, card)
        
        # Draw border
        pygame.draw.rect(card_surface, self.BLACK, 
                        (0, 0, self.card_width, self.card_height), 2)
        
        # Add rounded corners effect (draw over corners)
        corner_size = self.card_radius
        card_surface.set_colorkey((255, 0, 255))  # Magenta = transparent
        
        return card_surface
    
    def _draw_card_face(self, surface: pygame.Surface, card):
        """Draw the face of a card"""
        # Determine color (red for hearts/diamonds, black for clubs/spades)
        is_red = card.suit in [1, 2]  # Diamonds or Hearts
        color = self.RED if is_red else self.BLACK
        
        # Get symbols
        rank_str = self.RANK_CHARS[card.rank]
        suit_symbol = self.SUIT_SYMBOLS[card.suit]
        
        # Draw rank in top-left
        rank_text = self.rank_font.render(rank_str, True, color)
        surface.blit(rank_text, (8, 5))
        
        # Draw small suit symbol next to rank
        small_suit = self.mini_font.render(suit_symbol, True, color)
        rank_width = rank_text.get_width()
        surface.blit(small_suit, (8 + rank_width + 2, 10))
        
        # Draw large suit symbol in center
        large_suit = self.suit_font.render(suit_symbol, True, color)
        suit_x = (self.card_width - large_suit.get_width()) // 2
        suit_y = (self.card_height - large_suit.get_height()) // 2
        surface.blit(large_suit, (suit_x, suit_y))
        
        # Draw rank in bottom-right (upside down)
        rotated_rank = pygame.transform.rotate(rank_text, 180)
        surface.blit(rotated_rank, 
                    (self.card_width - rank_text.get_width() - 8,
                     self.card_height - rank_text.get_height() - 5))
        
        # Draw small suit in bottom-right (upside down)
        rotated_suit = pygame.transform.rotate(small_suit, 180)
        surface.blit(rotated_suit,
                    (self.card_width - rank_text.get_width() - small_suit.get_width() - 10,
                     self.card_height - rank_text.get_height()))
    
    def _draw_card_back(self, surface: pygame.Surface):
        """Draw the back of a card"""
        # Fill with base color
        surface.fill(self.CARD_BACK_COLOR)
        
        # Draw pattern
        pattern_margin = 8
        pattern_rect = pygame.Rect(
            pattern_margin,
            pattern_margin,
            self.card_width - 2 * pattern_margin,
            self.card_height - 2 * pattern_margin
        )
        
        # Draw diamond pattern
        pygame.draw.rect(surface, self.CARD_BACK_PATTERN, pattern_rect, 3)
        
        # Draw diagonal lines
        for i in range(0, self.card_width, 15):
            pygame.draw.line(surface, self.CARD_BACK_PATTERN,
                           (i, pattern_margin),
                           (i + self.card_height, self.card_height - pattern_margin), 2)
        
        for i in range(0, self.card_width, 15):
            pygame.draw.line(surface, self.CARD_BACK_PATTERN,
                           (i, self.card_height - pattern_margin),
                           (i + self.card_height, pattern_margin), 2)
    
    def render_card_at(self, screen: pygame.Surface, card, x: int, y: int, 
                      face_up: bool = True, scale: float = 1.0):
        """
        Render a card directly to screen at position
        
        Args:
            screen: Screen surface to draw on
            card: Card object
            x, y: Position (top-left corner)
            face_up: Show face or back
            scale: Scale factor (1.0 = normal size)
        """
        card_surface = self.render_card(card, x, y, face_up)
        
        if scale != 1.0:
            new_width = int(self.card_width * scale)
            new_height = int(self.card_height * scale)
            card_surface = pygame.transform.smoothscale(card_surface, (new_width, new_height))
        
        screen.blit(card_surface, (x, y))
    
    def render_multiple_cards(self, screen: pygame.Surface, cards: list,
                            start_x: int, start_y: int, spacing: int = 10,
                            face_up: bool = True):
        """
        Render multiple cards in a row
        
        Args:
            screen: Screen surface
            cards: List of Card objects
            start_x, start_y: Starting position
            spacing: Space between cards
            face_up: Show faces or backs
        """
        x = start_x
        for card in cards:
            self.render_card_at(screen, card, x, start_y, face_up)
            x += self.card_width + spacing


class Button:
    """Clickable button UI element"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: Tuple[int, int, int] = (70, 130, 180),
                 hover_color: Tuple[int, int, int] = (100, 149, 237),
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 disabled: bool = False):
        """Initialize button"""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.disabled = disabled
        self.hovered = False
        
        pygame.font.init()
        self.font = pygame.font.SysFont('arial', 20, bold=True)
    
    def draw(self, screen: pygame.Surface):
        """Draw the button"""
        # Choose color based on state
        if self.disabled:
            color = (105, 105, 105)
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.color
        
        # Draw rounded rectangle
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=10)
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event) -> bool:
        """
        Handle mouse events
        
        Returns:
            True if button was clicked
        """
        if self.disabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        
        return False
    
    def set_enabled(self, enabled: bool):
        """Enable or disable button"""
        self.disabled = not enabled


class Slider:
    """Slider UI element for bet sizing"""
    
    def __init__(self, x: int, y: int, width: int, min_val: int, max_val: int,
                 current_val: int, label: str = "Bet Amount"):
        """Initialize slider"""
        self.x = x
        self.y = y
        self.width = width
        self.height = 20
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.label = label
        self.dragging = False
        
        pygame.font.init()
        self.font = pygame.font.SysFont('arial', 16)
        
        self.handle_radius = 12
        self.track_color = (200, 200, 200)
        self.handle_color = (70, 130, 180)
        self.handle_hover_color = (100, 149, 237)
        self.hovered = False
    
    def draw(self, screen: pygame.Surface):
        """Draw the slider"""
        # Draw label
        label_surface = self.font.render(self.label, True, (255, 255, 255))
        screen.blit(label_surface, (self.x, self.y - 25))
        
        # Draw track
        track_rect = pygame.Rect(self.x, self.y + self.height // 2 - 2,
                                 self.width, 4)
        pygame.draw.rect(screen, self.track_color, track_rect)
        
        # Calculate handle position
        if self.max_val > self.min_val:
            ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        else:
            ratio = 0
        handle_x = self.x + int(ratio * self.width)
        handle_y = self.y + self.height // 2
        
        # Draw handle
        handle_color = self.handle_hover_color if self.hovered else self.handle_color
        pygame.draw.circle(screen, handle_color, (handle_x, handle_y), self.handle_radius)
        pygame.draw.circle(screen, (0, 0, 0), (handle_x, handle_y), self.handle_radius, 2)
        
        # Draw value
        value_text = f"${self.current_val}"
        value_surface = self.font.render(value_text, True, (255, 255, 255))
        value_rect = value_surface.get_rect(center=(handle_x, handle_y + 25))
        screen.blit(value_surface, value_rect)
    
    def handle_event(self, event) -> bool:
        """
        Handle mouse events
        
        Returns:
            True if value changed
        """
        if self.max_val <= self.min_val:
            return False
        
        # Calculate handle position for hit detection
        ratio = (self.current_val - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.x + int(ratio * self.width)
        handle_y = self.y + self.height // 2
        
        if event.type == pygame.MOUSEMOTION:
            # Check if hovering over handle
            mouse_x, mouse_y = event.pos
            distance = math.sqrt((mouse_x - handle_x)**2 + (mouse_y - handle_y)**2)
            self.hovered = distance <= self.handle_radius
            
            # Update value if dragging
            if self.dragging:
                self._update_value_from_mouse(event.pos[0])
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                distance = math.sqrt((mouse_x - handle_x)**2 + (mouse_y - handle_y)**2)
                if distance <= self.handle_radius:
                    self.dragging = True
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        
        return False
    
    def _update_value_from_mouse(self, mouse_x: int):
        """Update slider value based on mouse position"""
        # Clamp mouse position to slider bounds
        mouse_x = max(self.x, min(mouse_x, self.x + self.width))
        
        # Calculate ratio
        ratio = (mouse_x - self.x) / self.width
        
        # Calculate new value
        new_val = int(self.min_val + ratio * (self.max_val - self.min_val))
        
        # Round to nearest 5
        new_val = round(new_val / 5) * 5
        
        self.current_val = max(self.min_val, min(new_val, self.max_val))
    
    def get_value(self) -> int:
        """Get current slider value"""
        return self.current_val
    
    def set_value(self, value: int):
        """Set slider value"""
        self.current_val = max(self.min_val, min(value, self.max_val))
    
    def set_range(self, min_val: int, max_val: int):
        """Update slider range"""
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = max(min_val, min(self.current_val, max_val))