"""
PLO8 Poker Engine - Player and Action Module
Handles player state, actions, and player types
"""

from enum import Enum
from typing import List, Optional
from dataclasses import dataclass


class PlayerType(Enum):
    """Type of player (human or AI)"""
    HUMAN = "human"
    AI_API = "ai_api"
    AI_LOCAL = "ai_local"  # For future local AI
    EMPTY = "empty"


class ActionType(Enum):
    """Poker actions a player can take"""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"
    ALL_IN = "all_in"


@dataclass
class Action:
    """Represents a player action"""
    action_type: ActionType
    amount: int = 0  # Bet/raise amount (0 for fold/check/call)
    
    def __str__(self) -> str:
        if self.amount > 0:
            return f"{self.action_type.value.upper()} ${self.amount}"
        return self.action_type.value.upper()


class Player:
    """Represents a player in the game"""
    
    def __init__(
        self,
        player_id: int,
        name: str,
        stack: int,
        player_type: PlayerType = PlayerType.HUMAN,
        seat_position: int = 0,
        api_endpoint: Optional[str] = None
    ):
        """
        Initialize a player
        
        Args:
            player_id: Unique player identifier
            name: Player's display name
            stack: Starting chip stack
            player_type: Type of player (human, AI, etc.)
            seat_position: Position at table (0-8)
            api_endpoint: API endpoint for AI players
        """
        self.player_id = player_id
        self.name = name
        self.stack = stack
        self.starting_stack = stack
        self.player_type = player_type
        self.seat_position = seat_position
        self.api_endpoint = api_endpoint
        
        # Hand state
        self.hole_cards: List = []  # Will hold Card objects
        self.is_active = True  # Still in the hand
        self.is_sitting_out = False  # Sitting out (not dealt in)
        self.is_all_in = False
        
        # Betting state
        self.current_bet = 0  # Amount bet in current betting round
        self.total_invested = 0  # Total invested in current hand
        self.acted_this_round = False  # Has acted in current betting round
        
        # Position info
        self.is_dealer = False
        self.is_small_blind = False
        self.is_big_blind = False
    
    def reset_for_new_hand(self):
        """Reset player state for a new hand"""
        self.hole_cards = []
        self.is_active = True
        self.is_all_in = False
        self.current_bet = 0
        self.total_invested = 0
        self.acted_this_round = False
        self.is_dealer = False
        self.is_small_blind = False
        self.is_big_blind = False
    
    def reset_for_new_round(self):
        """Reset player state for a new betting round"""
        self.current_bet = 0
        self.acted_this_round = False
    
    def deal_cards(self, cards: List):
        """Deal hole cards to player"""
        if len(cards) != 4:
            raise ValueError("PLO8 requires exactly 4 hole cards")
        self.hole_cards = cards
    
    def post_blind(self, amount: int) -> int:
        """
        Post blind bet
        
        Args:
            amount: Blind amount
        
        Returns:
            Actual amount posted (may be less if all-in)
        """
        actual_amount = min(amount, self.stack)
        self.stack -= actual_amount
        self.current_bet = actual_amount
        self.total_invested += actual_amount
        
        if self.stack == 0:
            self.is_all_in = True
        
        return actual_amount
    
    def fold(self):
        """Fold hand"""
        self.is_active = False
        self.hole_cards = []
    
    def bet(self, amount: int) -> int:
        """
        Make a bet
        
        Args:
            amount: Amount to bet
        
        Returns:
            Actual amount bet
        """
        actual_amount = min(amount, self.stack)
        self.stack -= actual_amount
        self.current_bet += actual_amount
        self.total_invested += actual_amount
        self.acted_this_round = True
        
        if self.stack == 0:
            self.is_all_in = True
        
        return actual_amount
    
    def add_chips(self, amount: int):
        """Add chips to stack (winning pot)"""
        self.stack += amount
    
    def can_act(self) -> bool:
        """Check if player can still act"""
        return self.is_active and not self.is_all_in and not self.is_sitting_out
    
    def has_cards(self) -> bool:
        """Check if player has hole cards"""
        return len(self.hole_cards) == 4
    
    def __str__(self) -> str:
        return f"{self.name} (${self.stack})"
    
    def __repr__(self) -> str:
        return f"Player({self.player_id}, {self.name}, ${self.stack}, {self.player_type.value})"
    
    def get_status_string(self) -> str:
        """Get player status for display"""
        status = []
        if not self.is_active:
            status.append("FOLDED")
        if self.is_all_in:
            status.append("ALL-IN")
        if self.is_dealer:
            status.append("D")
        if self.is_small_blind:
            status.append("SB")
        if self.is_big_blind:
            status.append("BB")
        
        return " ".join(status) if status else ""


# Testing code
if __name__ == "__main__":
    print("=== Testing Player Class ===")
    
    # Create players
    player1 = Player(1, "Alice", 1000, PlayerType.HUMAN, seat_position=0)
    player2 = Player(2, "Bob", 1000, PlayerType.AI_API, seat_position=1, 
                     api_endpoint="http://localhost:5000/api/action")
    
    print(f"Player 1: {player1}")
    print(f"Player 2: {player2}")
    print(f"Player 2 repr: {repr(player2)}")
    
    # Test blind posting
    print("\n=== Testing Blind Posting ===")
    player1.is_small_blind = True
    player2.is_big_blind = True
    
    sb_amount = player1.post_blind(5)
    bb_amount = player2.post_blind(10)
    
    print(f"{player1.name} posts SB: ${sb_amount}, stack now: ${player1.stack}")
    print(f"{player2.name} posts BB: ${bb_amount}, stack now: ${player2.stack}")
    print(f"Player 1 status: {player1.get_status_string()}")
    print(f"Player 2 status: {player2.get_status_string()}")
    
    # Test betting
    print("\n=== Testing Betting ===")
    bet_amount = player1.bet(30)
    print(f"{player1.name} bets ${bet_amount}, stack now: ${player1.stack}")
    print(f"Current bet: ${player1.current_bet}, Total invested: ${player1.total_invested}")
    
    # Test actions
    print("\n=== Testing Actions ===")
    action1 = Action(ActionType.RAISE, 50)
    action2 = Action(ActionType.FOLD)
    action3 = Action(ActionType.CALL, 30)
    
    print(f"Action 1: {action1}")
    print(f"Action 2: {action2}")
    print(f"Action 3: {action3}")
    
    # Test fold
    print("\n=== Testing Fold ===")
    player2.fold()
    print(f"{player2.name} folded. Active: {player2.is_active}, Can act: {player2.can_act()}")
    
    # Test all-in
    print("\n=== Testing All-In ===")
    player1.bet(965)  # Bet remaining stack
    print(f"{player1.name} stack: ${player1.stack}, All-in: {player1.is_all_in}")
    print(f"Status: {player1.get_status_string()}")