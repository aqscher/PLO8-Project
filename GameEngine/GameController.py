"""
GameController.py - Game logic and state management for PLO8 poker
Handles all game rules, betting, hand evaluation, and state transitions
"""

import random
import json
from decimal import Decimal, getcontext, ROUND_HALF_UP

# Decimal configuration
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP
CENTS = Decimal("0.01")

class PLO8:
    def __init__(self, settings):
        """Initialize game controller with settings"""
        # Settings
        self.starting_players = settings[0]
        self.starting_stack = settings[1]
        self.human_in_loop = settings[2]
        
        # Game state
        self.players = []
        self.street = 0     #Street int: 0: Preflop, 1:Flop, 2:Turn, 3:River, 4:Showdown
        self.pot = Decimal("0.00")    # total pot
        self.main_pot = Decimal("0.00")   # main pot
        self.side_pot = Decimal("0.00")   # side pot
        self.side_pot1 = Decimal("0.00")   # side pot +1
        self.side_pot2 = Decimal("0.00")   # side pot +2
        self.side_pot3 = Decimal("0.00")   # side pot +3
        self.side_pot4 = Decimal("0.00")   # side pot +4
        self.side_pot5 = Decimal("0.00")   # side pot +5
        self.side_pot6 = Decimal("0.00")   # side pot +6
        self.side_pot7 = Decimal("0.00")   # side pot +7
        self.community_cards = []
        self.dealer_position = 0
        self.current_player = 0

        self.running = True
        self.init_game()
        self.new_hand()
    
    def q(self, value):
        """Quantize a Decimal value to cents."""
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        return value.quantize(CENTS)

    def init_game(self):
        """Initialize a new game"""
        # Create players
        self.players = []
        for i in range(self.starting_players):
            player = {
                'seat': i,
                'stack': Decimal(str(self.starting_stack)),
                'bet': Decimal("0.00"),
                'status': 'active',     # active, folded 
                'cards': [None, None, None, None],  # 4 hole cards for PLO8
                'acted': False,
                'allin': (False, Decimal("0.00"))
            }
            self.players.append(player)
        
        # Random dealer position
        self.dealer_position = random.randint(0, self.starting_players-1)
        print(f"Game initialized: {self.starting_players} players, dealer at seat {self.dealer_position}")

    def new_hand(self):
        # Eject the brokies
        self.players = [p for p in self.players if p['stack'] != Decimal("0.00")]

        # Reset pot, street, update dealer position, deal new cards, reset player flags, community cards
        self.pot, self.main_pot, self.side_pot = Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.side_pot1, self.side_pot2, self.side_pot3 = Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.side_pot4, self.side_pot5, self.side_pot6, self.side_pot7 = Decimal("0.00"), Decimal("0.00"), Decimal("0.00"), Decimal("0.00")
        self.street = 0
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self.community_cards = []
        self.init_deck()
        for player in self.players:
            player['bet'] = Decimal("0.00")
            player['status'] = 'active'
            player['cards'] = [self.deal_card(), self.deal_card(), self.deal_card(), self.deal_card()]
            player['acted'] = False
            player['allin'] = False
        
        # 2 Player blinds set up
        if len(self.players) == 2:
            #small blind
            if self.players[self.dealer_position % self.starting_players]['stack'] > Decimal("0.50"):
                self.players[self.dealer_position % self.starting_players]['stack'] -= Decimal("0.50")
                self.players[self.dealer_position % self.starting_players]['bet'] = Decimal("0.50")
                self.pot += Decimal("0.50")
            else:
                self.players[self.dealer_position % self.starting_players]['allin'] = True, 
                self.players[self.dealer_position % self.starting_players]['bet'] = self.players[self.dealer_position % self.starting_players]['stack']
                self.players[self.dealer_position % self.starting_players]['stack'] = Decimal("0.00")
                self.pot += self.players[self.dealer_position % self.starting_players]['bet']
            #big blind    
            if self.players[(self.dealer_position+1) % self.starting_players]['stack'] > Decimal("1.00"):
                self.players[(self.dealer_position+1) % self.starting_players]['stack'] -= Decimal("1.00")
                self.players[(self.dealer_position+1) % self.starting_players]['bet'] = Decimal("1.00")
                self.pot += Decimal("1.00")
            else:
                self.players[(self.dealer_position+1) % self.starting_players]['allin'] = True
                self.players[(self.dealer_position+1) % self.starting_players]['bet'] = self.players[self.dealer_position % self.starting_players]['stack']
                self.players[(self.dealer_position+1) % self.starting_players]['stack'] = Decimal("0.00")
                self.pot += self.players[(self.dealer_position+1) % self.starting_players]['bet']
            self.current_player = self.dealer_position
            return
        
        # 3+ Player blinds set up
        #small blind
        if self.players[(self.dealer_position+1) % self.starting_players]['stack'] > Decimal("0.50"):
            self.players[(self.dealer_position+1) % self.starting_players]['stack'] -= Decimal("0.50")
            self.players[(self.dealer_position+1) % self.starting_players]['bet'] = Decimal("0.50")
            self.pot += Decimal("0.50")
        else:
            self.players[(self.dealer_position+1) % self.starting_players]['allin'] = True, 
            self.players[(self.dealer_position+1) % self.starting_players]['bet'] = self.players[self.dealer_position % self.starting_players]['stack']
            self.players[(self.dealer_position+1) % self.starting_players]['stack'] = Decimal("0.00")
            self.pot += self.players[(self.dealer_position+1) % self.starting_players]['bet']
        #big blind
        if self.players[(self.dealer_position+2) % self.starting_players]['stack'] > Decimal("1.00"):
            self.players[(self.dealer_position+2) % self.starting_players]['stack'] -= Decimal("1.00")
            self.players[(self.dealer_position+2) % self.starting_players]['bet'] = Decimal("1.00")
            self.pot += Decimal("1.00")
        else:
            self.players[(self.dealer_position+2) % self.starting_players]['allin'] = True, 
            self.players[(self.dealer_position+2) % self.starting_players]['bet'] = self.players[self.dealer_position % self.starting_players]['stack']
            self.players[(self.dealer_position+2) % self.starting_players]['stack'] = Decimal("0.00")
            self.pot += self.players[(self.dealer_position+2) % self.starting_players]['bet']
        self.current_player = (self.dealer_position + 3) % self.starting_players


    def get_game_state(self):
        """
        Return current game state for rendering
        Returns dict with all necessary display information
        """
        # Convert Decimals to floats for JSON serialization / display
        players_copy = []
        for p in self.players:
            p_copy = p.copy()
            # convert stack and bet to float for JSON
            if isinstance(p_copy.get('stack'), Decimal):
                p_copy['stack'] = float(self.q(p_copy['stack']))
            if isinstance(p_copy.get('bet'), Decimal):
                p_copy['bet'] = float(self.q(p_copy['bet']))
            players_copy.append(p_copy)

        return {
            'players': players_copy,
            'street': self.street,
            'pot': float(self.q(self.pot)),
            'main_pot': float(self.q(self.main_pot)),
            'side_pot': float(self.q(self.side_pot)),
            'side_pot1': float(self.q(self.side_pot1)),
            'side_pot2': float(self.q(self.side_pot2)),
            'side_pot3': float(self.q(self.side_pot3)),
            'side_pot4': float(self.q(self.side_pot4)),
            'side_pot5': float(self.q(self.side_pot5)),
            'side_pot6': float(self.q(self.side_pot6)),
            'community_cards': self.community_cards,
            'dealer_position': self.dealer_position,
            'current_player': self.current_player
        }

    # Main loop from here
    def advance_game(self, action):
        #get player action, check to see if game over
        self.process_action(action)
        if len(self.players) == 1:
            print("Game Over!")
            self.running = False
            return
        
        #handle end of hand where all but 1 player folds
        if sum(1 for player in self.players if player['status'] == 'active') == 1 and self.street < 4:
            winner = next((player for player in self.players if player['status'] == 'active'), None)
            if winner == None:
                raise Exception("Winner is none.")
            winner['stack'] += self.q(self.pot)
            print(f'Player {winner['seat']} wins the hand, starting new hand...')
            self.new_hand()
            return
        
        #update current_player
        next_player = (self.current_player + 1) % len(self.players)
        attempts = 0
        while ( self.players[next_player]['status'] != 'active' or self.players[next_player]['allin'] == True ) and attempts < 8:
            next_player = (next_player + 1) % len(self.players)
            attempts += 1
        if attempts == 8:
            print('oh shit')
            #self.new_street()  # crashes engine
            return

        #handle end of betting round with active players
        action_players = [p for p in self.players if p['status'] == 'active' and not p['allin']]
        if len(action_players) > 1:
            all_bets_equal = len({p['bet'] for p in action_players}) == 1   # bets must match
            all_have_acted = all(p['acted'] for p in action_players)
            if all_bets_equal and all_have_acted:
                self.new_street()
                return

        
        #otherwise, just move on to next player in round of betting, dump gamestate
        self.current_player = next_player
        with open("game_state.json", "w") as f:
            json.dump(self.get_game_state(), f, indent=4)

        #check for illegal gamestate
        stack_bb = [p['stack'] for p in self.players]
        pot_bb = [self.pot]
        all_bb = stack_bb + pot_bb
        if Decimal(str((self.starting_players * self.starting_stack))) != sum(all_bb):
            raise Exception(f'Invalid gamestate occurred: {Decimal(str((self.starting_players * self.starting_stack)))} != {sum(all_bb)}')


    def new_street(self):
        if self.street == 0:
            self.end_betting_round()
            self.deal_flop()
            self.street = 1
        elif self.street == 1:
            self.end_betting_round()
            self.deal_turn()
            self.street = 2
        elif self.street == 2:
            self.end_betting_round()
            self.deal_river()
            self.street = 3
        elif self.street == 4:
            self.end_betting_round()
            self.showdown()
            
    def end_betting_round(self):
        #no players are all in
        allin_players = [player for player in self.players if player['allin'] == True]
        if allin_players == []:
            # Clear betting round related player states, put bets in main pot
            for player in self.players:
                player['acted'] = False
                player['bet'] = Decimal("0.00")
            self.main_pot = self.q(self.pot)

        #create player
        # 1 player is all in
        if len(allin_players) < 2:
            #mainpot, sidepot logic
            pass
        # 2 players are all in
        elif len(allin_players) < 3:
            #mainpot, sidepot, sidepot+1 logic
            pass
        # 3 players are all in
        elif len(allin_players) < 4:
            #mainpot, sidepot, sidepot+1, sidepot+2 logic
            pass
        # 4 players are all in
        elif len(allin_players) < 5:
            #mainpot, sidepot, sidepot+1, sidepot+2, sidepot+3 logic
            pass
        # 5 players are all in
        elif len(allin_players) < 6:
            #mainpot, sidepot, sidepot+1, sidepot+2, sidepot+3, sidepot+4 logic
            pass
        # 6 players are all in
        elif len(allin_players) < 7:
            #mainpot, sidepot, sidepot+1, sidepot+2, sidepot+3, sidepot+4, sidepot+5 logic
            pass
        # 7 players are all in
        elif len(allin_players) < 8:
            #mainpot, sidepot, sidepot+1, sidepot+2, sidepot+3, sidepot+4, sidepot+5, sidepot+6 logic
            pass
        # 8+ players are all in
        else:
            #mainpot, sidepot, sidepot+1, sidepot+2, sidepot+3, sidepot+4, sidepot+5, sidepot+6, sidepot+7 logic
            pass
        

        #start with small blind position for next betting round
        next_player = (self.dealer_position + 1 ) % len(self.players)
        while self.players[next_player]['status'] != 'active' or self.players[next_player]['allin'] == True:
            next_player = (next_player + 1) % len(self.players)
        self.current_player = next_player
        print(f'Next betting round starts with player {self.current_player}')

    def process_action(self, action):
        """
        Process a player action
            action: str: 'quit', 'check/fold', 'call/minbet', 'bet1/2pot', 'bet3/4pot', 'betpot'
        """
        if action == 'check/fold':
            self.handle_checkfold()
        elif action == 'call/minbet':
            self.handle_callminbet()
        elif action == 'bet1/2pot':
            self.handle_bethalfpot()
        elif action == 'bet3/4pot':
            self.handle_betthreequarterspot()
        elif action == 'betpot':
            self.handle_betpot()
        
        self.players[self.current_player]['acted'] = True
    
    def deal_flop(self):
        """Deal the flop (3 community cards)"""
        self.community_cards.append(self.deal_card())
        self.community_cards.append(self.deal_card())
        self.community_cards.append(self.deal_card())
        print("Dealing flop...")
    
    def deal_turn(self):
        """Deal the turn (4th community card)"""
        self.community_cards.append(self.deal_card())
        print("Dealing turn...")
    
    def deal_river(self):
        """Deal the river (5th community card)"""
        self.community_cards.append(self.deal_card())
        print("Dealing river...")
    
    def showdown(self):
        """Evaluate hands and determine winners"""
        # TODO: Implement PLO8 hand evaluation
        print("SHOWDOWN")
        self.new_hand()
    
    def handle_checkfold(self):
        """Handle 0 bet (check or fold depending on gamestate)"""
        #find max bet
        min_to_play = max(player['bet'] for player in self.players)

        #determine if 0 bet is a check or fold
        if self.players[self.current_player]['bet'] == min_to_play:
            print(f"Player {self.current_player} checks")
        else:
            self.players[self.current_player]['status'] = 'folded'
            #self.players[self.current_player]['cards'] = []
            print(f"Player {self.current_player} folds")
    
    def handle_callminbet(self):
        """Handle minimum bet (call or min bet depending on gamestate)"""
        #find max bet
        min_to_play = max(player['bet'] for player in self.players)

        #min bet is 1bb
        if min_to_play == Decimal("0.00"):
            #not all in
            if self.players[self.current_player]['stack'] > Decimal("1.00"):
                self.players[self.current_player]['bet'] = Decimal("1.00")
                self.players[self.current_player]['stack'] -= Decimal("1.00")
                self.pot += Decimal("1.00")
                print(f"Player {self.current_player} bets 1bb")
            #all in
            else:
                self.players[self.current_player]['bet'] += self.players[self.current_player]['stack']
                self.players[self.current_player]['stack'] = Decimal("0.00")
                self.pot += self.players[self.current_player]['bet']
                self.players[self.current_player]['allin'] = True
                print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")
        #min bet is a call
        else:
            current_bet = self.players[self.current_player]['bet']
            to_call = self.q(min_to_play - current_bet)
            #not all in
            if self.players[self.current_player]['stack'] > to_call:
                self.players[self.current_player]['bet'] = self.q(min_to_play)
                self.players[self.current_player]['stack'] -= to_call
                self.pot += to_call
                print(f"Player {self.current_player} calls {min_to_play}bb")
            #all in
            else:
                self.players[self.current_player]['bet'] += self.players[self.current_player]['stack']
                self.pot += self.players[self.current_player]['stack']
                self.players[self.current_player]['stack'] = Decimal("0.00")
                self.players[self.current_player]['allin'] = True
                print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")
    
    def handle_bethalfpot(self):
        """Handle 1/2 pot bet"""
        #find max bet // amount to call
        min_to_play = max(player['bet'] for player in self.players)
        current_bet = self.players[self.current_player]['bet']
        pot = (self.pot - current_bet) + (Decimal("2.00") * min_to_play)
        pot12 = (Decimal("0.5") * pot).quantize(CENTS)
        if pot12 < Decimal("2.00"): pot12 = Decimal("2.00")     #min allowed bet preflop that's not a call

        #not all in
        if self.players[self.current_player]['stack'] > self.q(pot12 - current_bet):
            self.players[self.current_player]['bet'] = self.q(pot12)
            self.players[self.current_player]['stack'] -= self.q(pot12 - current_bet)
            self.pot += self.q(pot12 - current_bet)
            print(f"Player {self.current_player} bets 1/2 pot: {pot12}bb")
        #all in
        else:
            self.players[self.current_player]['bet'] += self.players[self.current_player]['stack']
            self.pot += self.players[self.current_player]['stack']
            self.players[self.current_player]['stack'] = Decimal("0.00")
            self.players[self.current_player]['allin'] = True
            print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")
    
    def handle_betthreequarterspot(self):
        """Handle 3/4 pot bet"""
        #find max bet // amount to call
        min_to_play = max(player['bet'] for player in self.players)
        current_bet = self.players[self.current_player]['bet']
        pot = (self.pot - current_bet) + (Decimal("2.00") * min_to_play)
        pot34 = (Decimal("0.75") * pot).quantize(CENTS)
        if pot34 < Decimal("2.00"): pot34 = Decimal("2.00")     #min allowed bet preflop that's not a call
        
        #not all in
        if self.players[self.current_player]['stack'] > self.q(pot34 - current_bet):
            self.players[self.current_player]['bet'] = self.q(pot34)
            self.players[self.current_player]['stack'] -= self.q(pot34 - current_bet)
            self.pot += self.q(pot34 - current_bet)
            print(f"Player {self.current_player} bets 3/4 pot: {pot34}bb")
        #all in
        else:
            self.players[self.current_player]['bet'] += self.players[self.current_player]['stack']
            self.pot += self.players[self.current_player]['stack']
            self.players[self.current_player]['stack'] = Decimal("0.00")
            self.players[self.current_player]['allin'] = True
            print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")
    
    def handle_betpot(self):
        """Handle pot bet"""
        #find max bet // amount to call
        min_to_play = max(player['bet'] for player in self.players)
        current_bet = self.players[self.current_player]['bet']
        pot = (self.pot - current_bet) + (Decimal("2.00") * min_to_play)
        pot = pot.quantize(CENTS)

        #not all in
        if self.players[self.current_player]['stack'] > self.q(pot - current_bet):
            self.players[self.current_player]['bet'] = self.q(pot)
            self.players[self.current_player]['stack'] -= self.q(pot - current_bet)
            self.pot += self.q(pot - current_bet)
            print(f"Player {self.current_player} bets pot: {pot}bb")
        #all in
        else:
            self.players[self.current_player]['bet'] += self.players[self.current_player]['stack']
            self.pot += self.players[self.current_player]['stack']
            self.players[self.current_player]['stack'] = Decimal("0.00")
            self.players[self.current_player]['allin'] = True
            print(f"Player {self.current_player} goes all in with {self.players[self.current_player]['bet']}bb")

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
