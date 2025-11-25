"""
PLO8 Poker Engine - Card and Deck Module
Handles card representation, deck management, and shuffling
"""

import random
from enum import IntEnum
from typing import List, Optional


class Suit(IntEnum):
    """Card suits"""
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3


class Rank(IntEnum):
    """Card ranks (2-14, where 14 is Ace)"""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Card:
    """Represents a single playing card"""
    
    RANK_CHARS = {
        2: '2', 3: '3', 4: '4', 5: '5', 6: '6',
        7: '7', 8: '8', 9: '9', 10: 'T',
        11: 'J', 12: 'Q', 13: 'K', 14: 'A'
    }
    
    SUIT_CHARS = {
        Suit.CLUBS: 'c',
        Suit.DIAMONDS: 'd',
        Suit.HEARTS: 'h',
        Suit.SPADES: 's'
    }
    
    SUIT_SYMBOLS = {
        Suit.CLUBS: '♣',
        Suit.DIAMONDS: '♦',
        Suit.HEARTS: '♥',
        Suit.SPADES: '♠'
    }
    
    def __init__(self, rank: int, suit: Suit):
        """
        Initialize a card
        
        Args:
            rank: Card rank (2-14, where 14 is Ace)
            suit: Card suit (Suit enum)
        """
        if rank < 2 or rank > 14:
            raise ValueError(f"Invalid rank: {rank}")
        if suit not in Suit:
            raise ValueError(f"Invalid suit: {suit}")
            
        self.rank = rank
        self.suit = suit
    
    def __str__(self) -> str:
        """Return string representation like 'Ah' or 'Tc'"""
        return f"{self.RANK_CHARS[self.rank]}{self.SUIT_CHARS[self.suit]}"
    
    def __repr__(self) -> str:
        return f"Card({self.rank}, {self.suit.name})"
    
    def display(self) -> str:
        """Return pretty display with suit symbols like 'A♥' or 'T♣'"""
        return f"{self.RANK_CHARS[self.rank]}{self.SUIT_SYMBOLS[self.suit]}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
    
    @classmethod
    def from_string(cls, card_str: str) -> 'Card':
        """
        Create a Card from string representation like 'Ah' or 'Tc'
        
        Args:
            card_str: String like 'Ah', 'Tc', 'Kd'
        
        Returns:
            Card object
        """
        if len(card_str) != 2:
            raise ValueError(f"Invalid card string: {card_str}")
        
        rank_char = card_str[0].upper()
        suit_char = card_str[1].lower()
        
        # Find rank
        rank = None
        for r, c in cls.RANK_CHARS.items():
            if c == rank_char:
                rank = r
                break
        
        if rank is None:
            raise ValueError(f"Invalid rank character: {rank_char}")
        
        # Find suit
        suit = None
        for s, c in cls.SUIT_CHARS.items():
            if c == suit_char:
                suit = s
                break
        
        if suit is None:
            raise ValueError(f"Invalid suit character: {suit_char}")
        
        return cls(rank, suit)


class Deck:
    """Represents a standard 52-card deck"""
    
    def __init__(self):
        """Initialize a full deck of 52 cards"""
        self.cards: List[Card] = []
        self.reset()
    
    def reset(self):
        """Reset deck to full 52 cards"""
        self.cards = [
            Card(rank, suit)
            for suit in Suit
            for rank in range(2, 15)
        ]
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def deal(self, num_cards: int = 1) -> List[Card]:
        """
        Deal cards from the top of the deck
        
        Args:
            num_cards: Number of cards to deal
        
        Returns:
            List of dealt cards
        
        Raises:
            ValueError: If not enough cards in deck
        """
        if num_cards > len(self.cards):
            raise ValueError(f"Not enough cards in deck. Requested {num_cards}, have {len(self.cards)}")
        
        dealt = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]
        return dealt
    
    def deal_one(self) -> Card:
        """Deal a single card"""
        return self.deal(1)[0]
    
    def cards_remaining(self) -> int:
        """Return number of cards remaining in deck"""
        return len(self.cards)
    
    def __len__(self) -> int:
        return len(self.cards)
    
    def __str__(self) -> str:
        return f"Deck({len(self.cards)} cards remaining)"


# Testing code
if __name__ == "__main__":
    # Test Card class
    print("=== Testing Card Class ===")
    card1 = Card(14, Suit.HEARTS)
    print(f"Card: {card1}")
    print(f"Display: {card1.display()}")
    print(f"Repr: {repr(card1)}")
    
    card2 = Card.from_string("Kd")
    print(f"From string 'Kd': {card2.display()}")
    
    # Test Deck class
    print("\n=== Testing Deck Class ===")
    deck = Deck()
    print(f"New deck: {deck}")
    print(f"Cards remaining: {deck.cards_remaining()}")
    
    deck.shuffle()
    print("Deck shuffled")
    
    # Deal some cards
    hand = deck.deal(4)
    print(f"Dealt 4 cards: {[c.display() for c in hand]}")
    print(f"Cards remaining: {deck.cards_remaining()}")
    
    # Deal flop
    flop = deck.deal(3)
    print(f"Flop: {[c.display() for c in flop]}")
    
    # Deal turn and river
    turn = deck.deal_one()
    river = deck.deal_one()
    print(f"Turn: {turn.display()}")
    print(f"River: {river.display()}")
    print(f"Cards remaining: {deck.cards_remaining()}")