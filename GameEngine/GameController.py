"""
GameController.py - Game logic and state management for PLO8 poker
Handles all game rules, betting, hand evaluation, and state transitions
"""

import random

class PLO8:
    def __init__(self, settings):
        """Initialize game controller with settings"""
        # Settings
        self.starting_players = settings[0]
        self.starting_stack = settings[1]
        self.human_in_loop = settings[2]
        
        # Game state
        self.players = []
        self.phase = ['Pre-flop', 'Flop', 'Turn', 'River', 'Showdown']
        self.order = list(range(1,self.starting_players+1))
        self.pot = 0
        self.main_pot = 0
        self.community_cards = []
        self.dealer_position = 0
        self.running = True
        
        self.init_deck()
        self.init_game()
    
    def init_game(self):
        """Initialize a new game"""
        # Create players
        self.players = []
        for i in range(1, self.starting_players + 1):
            player = {
                'seat': i,
                'stack': self.starting_stack,
                'bet': 0,
                'status': 'Active',     # Active, Vacant, Broke, Folded 
                'cards': [self.deal_card(), self.deal_card(), self.deal_card(), self.deal_card()],  # 4 hole cards for PLO8
                'is_turn': False
            }
            self.players.append(player)
        
        # Initialize pots
        self.pot = 0
        self.main_pot = 0
        
        # Random dealer position
        self.dealer_position = random.randint(1, self.starting_players)

        # 2 Player blinds set up
        if self.starting_players == 2:
            self.players[self.dealer_position % self.starting_players]['stack'] -= 0.5
            self.players[self.dealer_position % self.starting_players]['bet'] = 0.5
            self.players[(self.dealer_position+1) % self.starting_players]['stack'] -= 1
            self.players[(self.dealer_position+1) % self.starting_players]['bet'] = 1
            self.current_player = self.dealer_position
        # 3+ Player blinds set up
        else:
            self.players[(self.dealer_position+1) % self.starting_players]['stack'] -= 0.5
            self.players[(self.dealer_position+1) % self.starting_players]['bet'] = 0.5
            self.players[(self.dealer_position+2) % self.starting_players]['stack'] -= 1
            self.players[(self.dealer_position+2) % self.starting_players]['bet'] = 1
            self.current_player = (self.dealer_position + 3) % self.starting_players
        
        self.pot += 1.5
        print(f"Game initialized: {self.starting_players} players, dealer at seat {self.dealer_position + 1}")
    
    def get_game_state(self):
        """
        Return current game state for rendering
        Returns dict with all necessary display information
        """
        return {
            'players': self.players,
            'pot': self.pot,
            'main_pot': self.main_pot,
            'community_cards': self.community_cards,
            'dealer_position': self.dealer_position,
            'current_player': self.current_player,
            'phase': self.phase,
            #order is determined by incrementing the random starting position 1-9 by 1, and setting it to 1 if it was 9 and cycle through positions in a clockwise manner.
        }
    
    def process_action(self, action):
        """
        Process a player action
        
        Args:
            action: dict with keys:
                - 'type': action type (fold, check, call, raise, all_in)
                - 'amount': bet amount (for raise)
        """
        if not action:
            return
        
        action_type = action.get('action', '')
        
        print(f"Player {self.current_player + 1} action: {action_type}")
        
        if action_type == 'check/fold':
            self.handle_fold()
        elif action_type == 'call/minbet':
            self.handle_check()
        elif action_type == 'bet1/2pot':
            self.handle_call()
        elif action_type == 'bet3/4pot':
            self.handle_raise()
        elif action_type == 'betpot':
            self.handle_all_in()
        
        # Move to next player
        self.advance_action()
    
    def handle_fold(self):
        """Handle fold action"""
        self.players[self.current_player]['status'] = 'folded'
        print(f"Player {self.current_player + 1} folds")
    
    def handle_check(self):
        """Handle check action"""
        print(f"Player {self.current_player + 1} checks")
    
    def handle_call(self):
        """Handle call action"""
        # TODO: Implement proper betting logic
        call_amount = 10  # Placeholder
        self.players[self.current_player]['bet'] = call_amount
        self.players[self.current_player]['stack'] -= call_amount
        self.pot += call_amount
        print(f"Player {self.current_player + 1} calls {call_amount}")
    
    def handle_raise(self, amount=20):
        """Handle raise action"""
        # TODO: Implement proper betting logic
        self.players[self.current_player]['bet'] = amount
        self.players[self.current_player]['stack'] -= amount
        self.pot += amount
        print(f"Player {self.current_player + 1} raises to {amount}")
    
    def handle_all_in(self):
        """Handle all-in action"""
        stack = self.players[self.current_player]['stack']
        self.players[self.current_player]['bet'] = stack
        self.players[self.current_player]['stack'] = 0
        self.pot += stack
        print(f"Player {self.current_player + 1} goes all-in for {stack}")
    
    def advance_action(self):
        """Move to the next player in turn"""
        # Simple rotation for now
        self.players[self.current_player]['is_turn'] = False
        
        # Find next active player
        next_player = (self.current_player + 1) % len(self.players)
        attempts = 0
        
        while self.players[next_player]['status'] in ['folded'] and attempts < 9:
            next_player = (next_player + 1) % len(self.players)
            attempts += 1
        
        if attempts >= 9:
            print("No active players remaining")
            return
        
        self.current_player = next_player
        self.players[self.current_player]['is_turn'] = True
        print(f"Action to player {self.current_player + 1}")
    
    def deal_cards(self):
        """Deal hole cards to all active players"""
        # TODO: Implement proper deck and card dealing
        print("Dealing cards...")
        for player in self.players:
            if player['status'] == 'active':
                player['cards'] = ['?', '?', '?', '?']  # Placeholder
    
    def deal_flop(self):
        """Deal the flop (3 community cards)"""
        # TODO: Implement proper community card dealing
        print("Dealing flop...")
    
    def deal_turn(self):
        """Deal the turn (4th community card)"""
        # TODO: Implement proper community card dealing
        print("Dealing turn...")
    
    def deal_river(self):
        """Deal the river (5th community card)"""
        # TODO: Implement proper community card dealing
        print("Dealing river...")
    
    def determine_winners(self):
        """Evaluate hands and determine winners"""
        # TODO: Implement PLO8 hand evaluation
        print("Determining winners...")
    
    def start_new_hand(self):
        """Start a new hand"""
        # Reset player bets
        for player in self.players:
            if player['status'] == 'active':
                player['bet'] = 0
                player['is_turn'] = False
        
        # Reset pots
        self.pot = 0
        self.main_pot = 0
        
        # Move dealer button
        self.dealer_position = (self.dealer_position + 1) % self.starting_players
        
        # Deal new hand
        self.deal_cards()
        
        print("Starting new hand...")

    def init_deck(self):
        self.deck = [
            'C2', 'D2', 'S2', 'H2',
            'C3', 'D3', 'S3', 'H3',
            'C4', 'D4', 'S4', 'H4',
            'C5', 'D5', 'S5', 'H5',
            'C6', 'D6', 'S6', 'H6',
            'C7', 'D7', 'S7', 'H7',
            'C8', 'D8', 'S8', 'H8',
            'C9', 'D9', 'S9', 'H9',
            'C10','D10','S10','H10',
            'CJ', 'DJ', 'SJ', 'HJ',
            'CQ', 'DQ', 'SQ', 'HQ',
            'CK', 'DK', 'SK', 'HK',
            'CA', 'DA', 'SA', 'HA'
        ]
        random.shuffle(self.deck)
        random.shuffle(self.deck)   # shuffle twice for good measure
        self.deck.reverse()

    def deal_card(self):
        return self.deck.pop()
